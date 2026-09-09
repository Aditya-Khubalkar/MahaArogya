"""
CONTRACT TEST — RTX 5060 to RTX 3050 Network Client
====================================================
PURPOSE: Validates the Remote3050InferenceClient network boundary behaviors
using a local dummy HTTP server.

This is NOT a real 3050 inference test.
The real 3050 system is on a separate laptop and cannot be tested here.
This validates: request structure, timeout handling, malformed response
handling, and offline fallback behavior.
"""

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

import pytest

from ai.patient_state.schemas import PatientState, SymptomDetail, Vitals
from ai.triage.remote_3050_client import Remote3050InferenceClient


# ---------------------------------------------------------------------------
# Helpers: tiny inline HTTP server for contract boundary testing
# ---------------------------------------------------------------------------

class _HandlerFactory:
    def __init__(self, status: int, body: dict, delay: float = 0.0):
        self.status = status
        self.body = body
        self.delay = delay
        self.requests_received = []

    def __call__(self, *args, **kwargs):
        factory = self

        class _H(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                try:
                    factory.requests_received.append(json.loads(raw))
                except Exception:
                    factory.requests_received.append(raw)
                if factory.delay > 0:
                    time.sleep(factory.delay)
                body = json.dumps(factory.body).encode()
                self.send_response(factory.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                body = json.dumps({"status": "ok", "model_loaded": True, "device": "cuda:0"}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass  # suppress noisy HTTP log

        return _H(*args, **kwargs)


def _start_server(handler_factory, port: int):
    srv = HTTPServer(("127.0.0.1", port), handler_factory)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, t


def _make_client(port: int, timeout: float = 2.0) -> Remote3050InferenceClient:
    os.environ["MAHAAROGYA_3050_HOST"] = "127.0.0.1"
    os.environ["MAHAAROGYA_3050_PORT"] = str(port)
    os.environ["MAHAAROGYA_3050_TIMEOUT"] = str(timeout)
    client = Remote3050InferenceClient()
    return client


def _sample_state() -> PatientState:
    return PatientState(
        conversation_id="contract_test_01",
        symptoms={"cough": SymptomDetail(present=True)},
    )


# ---------------------------------------------------------------------------
# CONTRACT TEST 1: Successful remote inference response
# ---------------------------------------------------------------------------

def test_contract_successful_inference():
    """CONTRACT TEST: 5060 client correctly parses a well-formed 3050 response."""
    port = 18201
    valid_response = {
        "severity": "ROUTINE",
        "confidence": 0.82,
        "source": "xgboost_baseline",
        "features_used": ["age", "spo2"],
        "explanation": ["Based on general clinical presentation"]
    }
    handler = _HandlerFactory(200, valid_response)
    srv, _ = _start_server(handler, port)

    try:
        client = _make_client(port)
        result = client.predict(_sample_state())
        assert result["severity"] == "ROUTINE"
        assert result["confidence"] == pytest.approx(0.82)
        assert result["source"] == "xgboost_baseline"
        assert len(handler.requests_received) == 1
        # Verify conversation_id was sent in payload
        payload = handler.requests_received[0]
        assert payload["conversation_id"] == "contract_test_01"
    finally:
        srv.shutdown()
        for key in ["MAHAAROGYA_3050_HOST", "MAHAAROGYA_3050_PORT", "MAHAAROGYA_3050_TIMEOUT"]:
            os.environ.pop(key, None)


# ---------------------------------------------------------------------------
# CONTRACT TEST 2: Remote returns malformed response (missing required fields)
# ---------------------------------------------------------------------------

def test_contract_malformed_response():
    """CONTRACT TEST: 5060 client returns controlled fallback on malformed response."""
    port = 18202
    malformed = {"unexpected_field": "garbage"}
    handler = _HandlerFactory(200, malformed)
    srv, _ = _start_server(handler, port)

    try:
        client = _make_client(port)
        result = client.predict(_sample_state())
        assert result["source"] == "remote_inference_unavailable"
        assert result["confidence"] == 0.0
    finally:
        srv.shutdown()
        for key in ["MAHAAROGYA_3050_HOST", "MAHAAROGYA_3050_PORT", "MAHAAROGYA_3050_TIMEOUT"]:
            os.environ.pop(key, None)


# ---------------------------------------------------------------------------
# CONTRACT TEST 3: Remote returns HTTP 500 error
# ---------------------------------------------------------------------------

def test_contract_remote_server_error():
    """CONTRACT TEST: 5060 client returns controlled fallback on remote 500 error."""
    port = 18203
    handler = _HandlerFactory(500, {"detail": "Internal server error", "error_code": "INFERENCE_FAILED"})
    srv, _ = _start_server(handler, port)

    try:
        client = _make_client(port)
        result = client.predict(_sample_state())
        assert result["source"] == "remote_inference_unavailable"
        assert result["confidence"] == 0.0
    finally:
        srv.shutdown()
        for key in ["MAHAAROGYA_3050_HOST", "MAHAAROGYA_3050_PORT", "MAHAAROGYA_3050_TIMEOUT"]:
            os.environ.pop(key, None)


# ---------------------------------------------------------------------------
# CONTRACT TEST 4: Timeout handling
# ---------------------------------------------------------------------------

def test_contract_timeout():
    """CONTRACT TEST: 5060 client returns controlled fallback when 3050 times out."""
    port = 18204
    # Server responds after 3s; client timeout is 1s
    handler = _HandlerFactory(200, {"severity": "ROUTINE", "confidence": 0.9, "source": "x", "features_used": [], "explanation": []}, delay=3.0)
    srv, _ = _start_server(handler, port)

    try:
        client = _make_client(port, timeout=0.5)
        result = client.predict(_sample_state())
        assert result["source"] == "remote_inference_unavailable"
        assert result["confidence"] == 0.0
    finally:
        srv.shutdown()
        for key in ["MAHAAROGYA_3050_HOST", "MAHAAROGYA_3050_PORT", "MAHAAROGYA_3050_TIMEOUT"]:
            os.environ.pop(key, None)


# ---------------------------------------------------------------------------
# CONTRACT TEST 5: Completely offline — no host configured
# ---------------------------------------------------------------------------

def test_contract_no_host_configured():
    """CONTRACT TEST: When MAHAAROGYA_3050_HOST is unset, client returns fallback immediately."""
    for key in ["MAHAAROGYA_3050_HOST", "MAHAAROGYA_3050_PORT", "MAHAAROGYA_3050_TIMEOUT"]:
        os.environ.pop(key, None)
    client = Remote3050InferenceClient()
    result = client.predict(_sample_state())
    assert result["source"] == "remote_inference_unavailable"
    assert client.host is None


# ---------------------------------------------------------------------------
# CONTRACT TEST 6: Health check endpoint
# ---------------------------------------------------------------------------

def test_contract_health_check():
    """CONTRACT TEST: Health-check endpoint correctly parsed from 3050."""
    port = 18205
    handler = _HandlerFactory(200, {"status": "ok", "model_loaded": True, "device": "cuda:0"})
    srv, _ = _start_server(handler, port)

    try:
        client = _make_client(port)
        is_healthy = client.health_check()
        assert is_healthy is True
    finally:
        srv.shutdown()
        for key in ["MAHAAROGYA_3050_HOST", "MAHAAROGYA_3050_PORT", "MAHAAROGYA_3050_TIMEOUT"]:
            os.environ.pop(key, None)


# ---------------------------------------------------------------------------
# CONTRACT TEST 7: Health check returns False when 3050 is completely offline
# ---------------------------------------------------------------------------

def test_contract_health_check_offline():
    """CONTRACT TEST: Health-check returns False when no server is running at host:port."""
    for key in ["MAHAAROGYA_3050_HOST", "MAHAAROGYA_3050_PORT", "MAHAAROGYA_3050_TIMEOUT"]:
        os.environ.pop(key, None)
    client = Remote3050InferenceClient()
    assert client.health_check() is False
