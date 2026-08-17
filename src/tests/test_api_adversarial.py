"""
Hard Adversarial Test Suite for FastAPI Local API Server (src/api.py)
Covers 25 adversarial cases: missing fields, malformed JSON, SQL injection payloads,
oversized strings, RBAC role resolution & authorization, concurrent race conditions, CORS origins, and HTTP 400/401/403/405/422 error handling.
"""

import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


# 1. MISSING REQUIRED FIELD (text_input)
def test_adv_api_01_missing_required_text_input():
    resp = client.post("/api/conversation/turn", json={})
    assert resp.status_code == 422


# 2. MALFORMED JSON BODY
def test_adv_api_02_invalid_json_body_conversation():
    resp = client.post(
        "/api/conversation/turn",
        content="{\"text_input\": \"hello\",}",
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 422


# 3. SQL INJECTION PAYLOAD IN CONVERSATION TURN
def test_adv_api_03_sql_injection_payload_in_turn():
    resp = client.post(
        "/api/conversation/turn",
        json={"text_input": "SELECT * FROM users; DROP TABLE patients;--"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "transcript_or_text" in data


# 4. OVERSIZED PAYLOAD STRING
def test_adv_api_04_oversized_payload_conversation():
    long_str = "Severe headache " * 50000  # ~800KB
    resp = client.post(
        "/api/conversation/turn",
        json={"text_input": long_str}
    )
    assert resp.status_code == 200


# 5. CCTV ESTIMATE MISSING REQUIRED FIELD (total_beds)
def test_adv_api_05_cctv_missing_total_beds():
    resp = client.post(
        "/api/cctv/estimate",
        json={"camera_id": "cam_01", "ward_id": "ward_A", "detected_occupied_beds": 5}
    )
    assert resp.status_code == 422


# 6. CCTV ESTIMATE NEGATIVE TOTAL BEDS
def test_adv_api_06_cctv_negative_total_beds():
    resp = client.post(
        "/api/cctv/estimate",
        json={
            "camera_id": "cam_01",
            "ward_id": "ward_A",
            "detected_occupied_beds": 5,
            "total_beds": -5,
            "db_authoritative_occupied": 5
        }
    )
    assert resp.status_code in [400, 422]


# 7. CCTV ESTIMATE INVALID CONFIDENCE RANGE (2.5)
def test_adv_api_07_cctv_invalid_confidence_range():
    resp = client.post(
        "/api/cctv/estimate",
        json={
            "camera_id": "cam_01",
            "ward_id": "ward_A",
            "detected_occupied_beds": 5,
            "total_beds": 10,
            "db_authoritative_occupied": 5,
            "confidence": 2.5
        }
    )
    assert resp.status_code in [400, 422]


# 8. CCTV SQL INJECTION IN CAMERA ID
def test_adv_api_08_cctv_sql_injection_camera_id():
    resp = client.post(
        "/api/cctv/estimate",
        json={
            "camera_id": "cam' OR 1=1;--",
            "ward_id": "ward_A",
            "detected_occupied_beds": 5,
            "total_beds": 10,
            "db_authoritative_occupied": 5
        }
    )
    assert resp.status_code == 200


# 9. OPD ISSUE TOKEN MISSING PATIENT ID
def test_adv_api_09_opd_issue_token_missing_patient_id():
    resp = client.post(
        "/api/opd/issue_token",
        json={"hospital_name": "KEM Hospital", "department_name": "Cardiology", "slot_time": "10:00 AM"}
    )
    assert resp.status_code == 422


# 10. OPD ISSUE TOKEN EMPTY PATIENT ID
def test_adv_api_10_opd_issue_token_empty_patient_id():
    resp = client.post(
        "/api/opd/issue_token",
        json={"patient_id": "", "hospital_name": "KEM Hospital", "department_name": "Cardiology", "slot_time": "10:00 AM"}
    )
    assert resp.status_code in [400, 422]


# 11. OPD ISSUE TOKEN NEGATIVE QUEUE LENGTH
def test_adv_api_11_opd_issue_token_negative_queue_length():
    resp = client.post(
        "/api/opd/issue_token",
        json={
            "patient_id": "p_123",
            "hospital_name": "KEM Hospital",
            "department_name": "Cardiology",
            "slot_time": "10:00 AM",
            "current_queue_length": -10
        }
    )
    assert resp.status_code in [400, 422]


# 12. RECEPTION CHECKIN MISSING TOKEN ID
def test_adv_api_12_reception_checkin_missing_token_id():
    resp = client.post(
        "/api/reception/checkin",
        json={"staff_user_id": "reception_staff_01"}
    )
    assert resp.status_code == 422


# 13. RECEPTION CHECKIN RBAC UNAUTHORIZED ROLE (DOCTOR ROLE)
def test_adv_api_13_reception_checkin_rbac_unauthorized_role():
    resp = client.post(
        "/api/reception/checkin",
        json={"token_id": "OPD-KEM-1234", "staff_user_id": "doctor_user_01"}
    )
    assert resp.status_code == 403


# 14. RECEPTION CHECKIN VALID ROLE (RECEPTION STAFF)
def test_adv_api_14_reception_checkin_valid_reception_role():
    issue_resp = client.post(
        "/api/opd/issue_token",
        json={
            "patient_id": "p_valid_role_user",
            "hospital_name": "KEM Hospital",
            "department_name": "General Medicine",
            "slot_time": "11:00 AM",
            "current_queue_length": 1
        }
    )
    assert issue_resp.status_code == 200
    token_id = issue_resp.json()["token_id"]

    resp = client.post(
        "/api/reception/checkin",
        json={"token_id": token_id, "staff_user_id": "reception_staff_01"}
    )
    assert resp.status_code == 200
    assert resp.json()["arrival_status"] == "CHECKED_IN"


# 15. CONCURRENT OPD TOKEN GENERATION (DISTINCT CLIENT IPS)
def test_adv_api_15_concurrent_opd_token_generation():
    def issue_token(i):
        return client.post(
            "/api/opd/issue_token",
            json={
                "patient_id": f"p_conc_{i}",
                "hospital_name": "Sion Hospital",
                "department_name": "General Medicine",
                "slot_time": "11:00 AM"
            },
            headers={"X-Forwarded-For": f"10.0.0.{i+1}"}
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(issue_token, i) for i in range(30)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert all(r.status_code == 200 for r in results)
    token_ids = [r.json()["token_id"] for r in results]
    assert len(set(token_ids)) == 30


# 16. CONCURRENT SESSION TURNS
def test_adv_api_16_concurrent_session_turns():
    def send_turn(i):
        return client.post(
            "/api/conversation/turn",
            json={"conversation_id": "conc_session_01", "text_input": f"Turn {i} pot dukhatahe."}
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_turn, i) for i in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert all(r.status_code == 200 for r in results)


# 17. CORS HEADER ALLOWED ORIGIN (localhost:3000)
def test_adv_api_17_cors_header_allowed_origin():
    resp = client.options(
        "/api/conversation/turn",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        }
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


# 18. CORS HEADER UNREGISTERED ORIGIN
def test_adv_api_18_cors_header_unregistered_origin():
    resp = client.options(
        "/api/conversation/turn",
        headers={
            "Origin": "http://malicious-attacker.com",
            "Access-Control-Request-Method": "POST"
        }
    )
    assert resp.headers.get("access-control-allow-origin") != "http://malicious-attacker.com"


# 19. HEALTH ENDPOINT RESPONSE SCHEMA
def test_adv_api_19_health_endpoint_response_schema():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "gpu_detected" in data


# 20. UNSUPPORTED HTTP METHOD (PUT /api/conversation/turn)
def test_adv_api_20_unsupported_http_method():
    resp = client.put("/api/conversation/turn", json={"text_input": "test"})
    assert resp.status_code == 405


# 21. RBAC: RECEPTION ROLE HITTING UNPERMITTED ROUTE (NURSE ROUTE WITH STAFF ID)
def test_adv_api_21_rbac_reception_role_hitting_unpermitted_route():
    resp = client.post(
        "/api/cctv/estimate",
        json={
            "camera_id": "cam_01",
            "ward_id": "ward_A",
            "detected_occupied_beds": 5,
            "total_beds": 10,
            "db_authoritative_occupied": 5,
            "staff_user_id": "reception_staff_01"  # Reception role lacks UPDATE_BED_STATUS
        }
    )
    assert resp.status_code == 403


# 22. RBAC: NURSE ROLE ALLOWED ON CCTV BED UPDATE
def test_adv_api_22_rbac_nurse_role_allowed_cctv_update():
    resp = client.post(
        "/api/cctv/estimate",
        json={
            "camera_id": "cam_01",
            "ward_id": "ward_A",
            "detected_occupied_beds": 5,
            "total_beds": 10,
            "db_authoritative_occupied": 5,
            "staff_user_id": "nurse_user_01"  # Nurse role possesses UPDATE_BED_STATUS
        }
    )
    assert resp.status_code == 200


# 23. RBAC: UNRECOGNIZED NON-EXISTENT STAFF USER ID
def test_adv_api_23_rbac_unrecognized_nonexistent_staff_user_id():
    resp = client.post(
        "/api/reception/checkin",
        json={"token_id": "OPD-KEM-1234", "staff_user_id": "ghost_user_999"}
    )
    assert resp.status_code == 401


# 24. RBAC: MISSING STAFF USER ID ON PROTECTED ROUTE
def test_adv_api_24_rbac_missing_staff_user_id_on_checkin():
    resp = client.post(
        "/api/reception/checkin",
        json={"token_id": "OPD-KEM-1234", "staff_user_id": None}
    )
    assert resp.status_code == 401


# 25. RBAC: DOCTOR ROLE UNPERMITTED ON RECEPTION ROUTE
def test_adv_api_25_rbac_doctor_role_unpermitted_on_reception():
    resp = client.post(
        "/api/reception/checkin",
        json={"token_id": "OPD-KEM-1234", "staff_user_id": "doctor_user_01"}
    )
    assert resp.status_code == 403

