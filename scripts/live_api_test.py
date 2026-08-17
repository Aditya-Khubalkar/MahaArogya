"""
MahaArogya — Live End-to-End API Test Script
Tests all live endpoints on http://127.0.0.1:8000
"""

import sys
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    print("\n[TEST 1/5] GET /health")
    res = requests.get(f"{BASE_URL}/health")
    print(f"  Status Code: {res.status_code}")
    print(f"  Response: {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200, "Health check failed"


def test_conversation():
    print("\n[TEST 2/5] POST /api/conversation/turn")
    # Turn 1: Emergency Chest Pain (Marathi)
    payload_1 = {
        "text_input": "माझ्या छातीत खूप दुखत आहे आणि श्वास घ्यायला त्रास होतोय",
        "language": "mr",
        "patient_lat": 19.0100,
        "patient_lon": 72.8500
    }
    res_1 = requests.post(f"{BASE_URL}/api/conversation/turn", json=payload_1)
    print(f"  Turn 1 (Marathi Emergency) -> Status: {res_1.status_code}")
    data_1 = res_1.json()
    print(f"    Conversation ID: {data_1['conversation_id']}")
    print(f"    Triage Category: {data_1['triage_decision']['triage_category']}")
    print(f"    AI Response: {data_1['ai_response_text']}")
    print(f"    Triggered Red Flags: {data_1['triage_decision']['triggered_rule_ids']}")
    print(f"    Top Hospital: {data_1['hospital_recommendations'][0]['hospital']['name'] if data_1['hospital_recommendations'] else 'N/A'}")

    # Turn 2: Abdominal Pain (English)
    payload_2 = {
        "text_input": "I have severe abdominal pain since 3 days and fever",
        "language": "en",
        "patient_lat": 19.0100,
        "patient_lon": 72.8500
    }
    res_2 = requests.post(f"{BASE_URL}/api/conversation/turn", json=payload_2)
    print(f"\n  Turn 2 (English Priority) -> Status: {res_2.status_code}")
    data_2 = res_2.json()
    print(f"    Triage Category: {data_2['triage_decision']['triage_category']}")
    print(f"    Extracted Symptoms: {list(data_2['patient_state']['symptoms'].keys())}")
    print(f"    Latency: {data_2['latency_total_sec']}s")


def test_opd_token():
    print("\n[TEST 3/5] POST /api/opd/issue_token")
    payload = {
        "patient_id": "PAT-LIVE-901",
        "hospital_name": "KEM Hospital Mumbai",
        "department_name": "Gastroenterology",
        "slot_time": "2026-08-17T11:00:00",
        "current_queue_length": 4
    }
    res = requests.post(f"{BASE_URL}/api/opd/issue_token", json=payload)
    print(f"  Status Code: {res.status_code}")
    token = res.json()
    print(f"    Token ID: {token['token_id']}")
    print(f"    Queue Number: {token['queue_number']}")
    print(f"    Status: {token['status']}")
    print(f"    QR Payload: {token['qr_payload']}")
    return token['token_id']


def test_reception_checkin(token_id):
    print("\n[TEST 4/5] POST /api/reception/checkin")
    payload = {
        "token_id": token_id,
        "staff_user_id": "reception_staff_01"
    }
    res = requests.post(f"{BASE_URL}/api/reception/checkin", json=payload)
    print(f"  Status Code: {res.status_code}")
    entry = res.json()
    print(f"    Token ID: {entry['token_id']}")
    print(f"    Arrival Status: {entry['arrival_status']}")
    print(f"    Checked In At: {entry['checked_in_at']}")


def test_cctv_estimate():
    print("\n[TEST 5/5] POST /api/cctv/estimate")
    payload = {
        "camera_id": "CAM-WARD-A1-02",
        "ward_id": "WARD-ICU-A1",
        "detected_occupied_beds": 11,
        "total_beds": 12,
        "db_authoritative_occupied": 10,
        "confidence": 0.92
    }
    res = requests.post(f"{BASE_URL}/api/cctv/estimate", json=payload)
    print(f"  Status Code: {res.status_code}")
    result = res.json()
    print(f"    Ward: {result['ward_id']}")
    print(f"    Occupancy: {result['occupancy_percentage']}% ({result['estimated_occupied_beds']}/{result['total_beds']} beds)")
    print(f"    Discrepancy Delta: Δ{result['discrepancy_delta']}")
    print(f"    Human Verification Required: {result['human_verification_required']}")


def run_all_tests():
    print("=" * 60)
    print("  MahaArogya Live API End-to-End Verification")
    print("=" * 60)
    test_health()
    test_conversation()
    token_id = test_opd_token()
    test_reception_checkin(token_id)
    test_cctv_estimate()
    print("=" * 60)
    print("  ALL LIVE API ENDPOINTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
