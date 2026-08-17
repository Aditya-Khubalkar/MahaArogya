"""
Unit and Integration Tests for In-Memory IP Rate Limiting (src/api.py)
Validates sliding-window per-IP rate limits on public endpoints (/api/opd/issue_token, /api/conversation/turn).
Uses test-only window overrides (1 second) to maintain fast, deterministic test execution.
"""

import time
import pytest
from fastapi.testclient import TestClient
from src.api import app, rate_limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Resets rate limiter state before every test."""
    rate_limiter.reset()
    rate_limiter.test_window_override = None


# 1. UNDER LIMIT SUCCEEDS
def test_rate_limit_under_limit_succeeds():
    for i in range(5):
        resp = client.post(
            "/api/opd/issue_token",
            json={
                "patient_id": f"p_{i}",
                "hospital_name": "KEM Hospital",
                "department_name": "Cardiology",
                "slot_time": "10:00 AM"
            },
            headers={"X-Forwarded-For": "192.168.1.100"}
        )
        assert resp.status_code == 200


# 2. EXCEEDING LIMIT RETURNS 429 TOO MANY REQUESTS
def test_rate_limit_exceeding_limit_returns_429():
    for i in range(5):
        client.post(
            "/api/opd/issue_token",
            json={
                "patient_id": f"p_{i}",
                "hospital_name": "KEM Hospital",
                "department_name": "Cardiology",
                "slot_time": "10:00 AM"
            },
            headers={"X-Forwarded-For": "192.168.1.101"}
        )

    # 6th request from same IP should get 429
    resp6 = client.post(
        "/api/opd/issue_token",
        json={
            "patient_id": "p_6",
            "hospital_name": "KEM Hospital",
            "department_name": "Cardiology",
            "slot_time": "10:00 AM"
        },
        headers={"X-Forwarded-For": "192.168.1.101"}
    )
    assert resp6.status_code == 429
    assert "Too Many Requests" in resp6.json()["detail"]


# 3. DIFFERENT IPS TRACKED INDEPENDENTLY
def test_rate_limit_independent_ips():
    # Exhaust IP A (192.168.1.10)
    for i in range(5):
        client.post(
            "/api/opd/issue_token",
            json={
                "patient_id": f"p_a_{i}",
                "hospital_name": "KEM Hospital",
                "department_name": "Cardiology",
                "slot_time": "10:00 AM"
            },
            headers={"X-Forwarded-For": "192.168.1.10"}
        )

    # IP A 6th request is blocked
    resp_a = client.post(
        "/api/opd/issue_token",
        json={"patient_id": "p_a_6", "hospital_name": "KEM", "department_name": "Cardio", "slot_time": "10:00 AM"},
        headers={"X-Forwarded-For": "192.168.1.10"}
    )
    assert resp_a.status_code == 429

    # IP B (192.168.1.20) should succeed unblocked
    resp_b = client.post(
        "/api/opd/issue_token",
        json={"patient_id": "p_b_1", "hospital_name": "KEM", "department_name": "Cardio", "slot_time": "10:00 AM"},
        headers={"X-Forwarded-For": "192.168.1.20"}
    )
    assert resp_b.status_code == 200


# 4. LIMIT RESETS AFTER TIME WINDOW EXPIRES
def test_rate_limit_resets_after_window_expires():
    # Set short 1-second window override for test speed
    rate_limiter.test_window_override = 1

    # Exhaust limit (5 requests)
    for i in range(5):
        client.post(
            "/api/opd/issue_token",
            json={
                "patient_id": f"p_expire_{i}",
                "hospital_name": "KEM Hospital",
                "department_name": "Cardiology",
                "slot_time": "10:00 AM"
            },
            headers={"X-Forwarded-For": "192.168.1.200"}
        )

    # 6th request immediately is blocked (429)
    blocked_resp = client.post(
        "/api/opd/issue_token",
        json={"patient_id": "p_blocked", "hospital_name": "KEM", "department_name": "Cardio", "slot_time": "10:00 AM"},
        headers={"X-Forwarded-For": "192.168.1.200"}
    )
    assert blocked_resp.status_code == 429

    # Sleep 1.1s for window to expire
    time.sleep(1.1)

    # Request after window expiration succeeds (200 OK)
    success_resp = client.post(
        "/api/opd/issue_token",
        json={"patient_id": "p_after_expire", "hospital_name": "KEM", "department_name": "Cardio", "slot_time": "10:00 AM"},
        headers={"X-Forwarded-For": "192.168.1.200"}
    )
    assert success_resp.status_code == 200


# 5. CONVERSATION TURN ENDPOINT HIGHER LIMIT (30 REQUESTS)
def test_rate_limit_conversation_turn_limit():
    for i in range(30):
        resp = client.post(
            "/api/conversation/turn",
            json={"text_input": f"Turn {i} pot dukhate."},
            headers={"X-Forwarded-For": "192.168.1.150"}
        )
        assert resp.status_code == 200

    # 31st request from same IP should get 429
    resp31 = client.post(
        "/api/conversation/turn",
        json={"text_input": "Turn 31 pot dukhate."},
        headers={"X-Forwarded-For": "192.168.1.150"}
    )
    assert resp31.status_code == 429
