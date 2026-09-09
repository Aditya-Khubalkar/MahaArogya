import pytest
from fastapi.testclient import TestClient
from src.api import app, rate_limiter
from src.rbac.models import AuthUser, UserRole

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Force in-memory limiter and specific window for testing
    rate_limiter.use_redis = False
    rate_limiter.test_window_override = 1
    rate_limiter.reset()
    yield
    rate_limiter.reset()
    rate_limiter.test_window_override = None

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()

def test_demo_login():
    response = client.post("/api/v1/auth/demo-login", json={"user_id": "reception_staff_01"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["user_id"] == "reception_staff_01"
    assert data["user"]["role"] == "RECEPTION"

def test_protected_route_without_token():
    # checkin requires reception role
    response = client.post("/api/v1/reception/checkin", json={"token_id": "T-100"})
    assert response.status_code == 401

def test_protected_route_with_wrong_role():
    # Login as doctor, try to access reception checkin
    login_res = client.post("/api/v1/auth/demo-login", json={"user_id": "doctor_user_01"})
    token = login_res.json()["access_token"]
    
    response = client.post(
        "/api/v1/reception/checkin",
        json={"token_id": "T-100"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403 # Forbidden

def test_rate_limiting():
    # issue_token is limited to 5 requests per window
    payload = {
        "patient_id": "P-123",
        "hospital_name": "Sion Hospital",
        "department_name": "Cardiology",
        "slot_time": "10:30 AM"
    }
    
    # First 5 should succeed
    for _ in range(5):
        res = client.post("/api/v1/opd/issue_token", json=payload)
        assert res.status_code == 200
        
    # 6th should fail with 429
    res = client.post("/api/v1/opd/issue_token", json=payload)
    assert res.status_code == 429

    # Wait for the rate limit window to expire (1 second override)
    import time
    time.sleep(1.1)
    
    # 7th should succeed again
    res = client.post("/api/v1/opd/issue_token", json=payload)
    assert res.status_code == 200

def test_get_dashboard_stats():
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Online"
    assert "triage_breakdown" in data
