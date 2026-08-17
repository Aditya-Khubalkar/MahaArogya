"""
Hard Adversarial Test Suite for Hospital Routing & Smart OPD Token System (ai/routing/)
Covers 20 adversarial cases: token collisions, concurrent multi-threaded issuance, invalid patient IDs,
priority queue preemption, capacity overflow, bounds checking, and malformed inputs.
"""

import json
import re
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from ai.routing.schemas import Hospital, Department, OPDToken, HospitalRecommendation
from ai.routing.hospitals import get_all_hospitals
from ai.routing.router import HospitalRouter, haversine_distance
from ai.routing.opd_token import OPDTokenGenerator


# 1. TOKEN UNIQUENESS (1,000 SEQUENTIAL TOKENS)
def test_adv_01_token_uniqueness_1000():
    tokens = [
        OPDTokenGenerator.generate_token(
            patient_id=f"p_{i}",
            hospital_name="KEM General Hospital",
            department_name="General Medicine",
            slot_time="10:00 AM",
            current_queue_length=i
        )
        for i in range(1000)
    ]
    token_ids = [t.token_id for t in tokens]
    assert len(token_ids) == 1000
    assert len(set(token_ids)) == 1000, f"Token collisions detected! Unique: {len(set(token_ids))}/1000"


# 2. CONCURRENT / SIMULTANEOUS MULTI-THREADED TOKEN REQUESTS
def test_adv_02_concurrent_token_generation():
    def issue_token(pid):
        return OPDTokenGenerator.generate_token(
            patient_id=f"concurrent_patient_{pid}",
            hospital_name="Sassoon Hospital",
            department_name="Cardiology",
            slot_time="11:00 AM",
            current_queue_length=pid
        )

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(issue_token, i) for i in range(100)]
        results = [f.result() for f in as_completed(futures)]

    assert len(results) == 100
    token_ids = {t.token_id for t in results}
    assert len(token_ids) == 100, f"Concurrent race condition collision detected! Unique: {len(token_ids)}/100"


# 3. INVALID / EMPTY PATIENT ID
def test_adv_03_empty_patient_id():
    with pytest.raises(ValueError, match="Patient ID cannot be empty"):
        OPDTokenGenerator.generate_token(
            patient_id="",
            hospital_name="KEM Hospital",
            department_name="General Medicine",
            slot_time="10:00 AM"
        )


# 4. NONE PATIENT ID
def test_adv_04_none_patient_id():
    with pytest.raises((ValueError, TypeError)):
        OPDTokenGenerator.generate_token(
            patient_id=None,
            hospital_name="KEM Hospital",
            department_name="General Medicine",
            slot_time="10:00 AM"
        )


# 5. PRIORITY QUEUE PREEMPTION (EMERGENCY OVERRIDE FOR OPD TOKEN)
def test_adv_05_priority_queue_emergency_bypassing():
    # Emergency token should be assigned priority status and queue number 1 (or emergency flag)
    token = OPDTokenGenerator.generate_token(
        patient_id="emg_patient_01",
        hospital_name="KEM Hospital",
        department_name="Emergency / ICU",
        slot_time="IMMEDIATE",
        current_queue_length=15,
        is_emergency=True
    )
    assert token.queue_number == 1 or "EMG" in token.token_id
    assert token.status in ["ISSUED", "EMERGENCY_PRIORITY"]


# 6. CAPACITY OVERFLOW (0 AVAILABLE SLOTS / DEPARTMENT FULL)
def test_adv_06_department_capacity_overflow():
    hosp = Hospital(
        id="hosp_full_01",
        name="Full Capacity Hospital",
        city="Mumbai",
        latitude=19.00,
        longitude=72.84,
        departments={
            "General Medicine": Department(
                id="dept_full", hospital_id="hosp_full_01", name="General Medicine",
                open_now=True, queue_length=50, estimated_wait_min=180,
                available_slots=[]  # 0 available slots
            )
        }
    )
    router = HospitalRouter(hospitals=[hosp])
    recs = router.rank_hospitals("ROUTINE", target_department="General Medicine")
    # Capacity overflow (0 slots) should either lower rank or reflect 0 available slots
    assert len(recs) == 0 or recs[0].estimated_wait_min == 180


# 7. CLOSED DEPARTMENT FILTER
def test_adv_07_closed_department_filter():
    hosp = Hospital(
        id="hosp_closed_01",
        name="Night Closed Clinic",
        city="Mumbai",
        latitude=19.00,
        longitude=72.84,
        departments={
            "General Medicine": Department(
                id="dept_closed", hospital_id="hosp_closed_01", name="General Medicine",
                open_now=False, queue_length=0, estimated_wait_min=0, available_slots=[]
            )
        }
    )
    router = HospitalRouter(hospitals=[hosp])
    recs = router.rank_hospitals("ROUTINE", target_department="General Medicine")
    assert len(recs) == 0, "Closed department must be excluded from routing recommendations"


# 8. NON-EMERGENCY HOSPITAL EXCLUSION FOR EMERGENCY TRIAGE
def test_adv_08_non_emergency_hospital_exclusion():
    non_emg_hosp = Hospital(
        id="hosp_day_care",
        name="Day Care Polyclinic",
        city="Mumbai",
        latitude=19.01,
        longitude=72.85,
        emergency_capable=False,
        departments={
            "General Medicine": Department(
                id="dept_day", hospital_id="hosp_day_care", name="General Medicine",
                open_now=True, queue_length=2, estimated_wait_min=5, available_slots=["10:00 AM"]
            )
        }
    )
    router = HospitalRouter(hospitals=[non_emg_hosp])
    recs = router.rank_hospitals("EMERGENCY", target_department="General Medicine")
    assert len(recs) == 0, "Non-emergency capable facility MUST be excluded for EMERGENCY triage"


# 9. INVALID LATITUDE AND LONGITUDE BOUNDS
def test_adv_09_invalid_latitude_longitude_bounds():
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        haversine_distance(999.0, 72.85, 19.01, 72.85)


# 10. NEGATIVE QUEUE LENGTH HANDLING
def test_adv_10_negative_queue_length():
    with pytest.raises(ValueError, match="Queue length cannot be negative"):
        OPDTokenGenerator.generate_token(
            patient_id="p_neg",
            hospital_name="KEM Hospital",
            department_name="General Medicine",
            slot_time="10:00 AM",
            current_queue_length=-5
        )


# 11. EMPTY HOSPITAL DATABASE
def test_adv_11_empty_hospital_database():
    router = HospitalRouter(hospitals=[])
    recs = router.rank_hospitals("ROUTINE")
    assert recs == []


# 12. HOSPITAL WITH NO MATCHING OR FALLBACK DEPARTMENT
def test_adv_12_hospital_with_no_matching_department():
    hosp = Hospital(
        id="hosp_ortho_only",
        name="Specialty Ortho Center",
        city="Mumbai",
        latitude=19.01,
        longitude=72.85,
        departments={
            "Orthopedics": Department(
                id="dept_ortho", hospital_id="hosp_ortho_only", name="Orthopedics",
                open_now=True, queue_length=1, estimated_wait_min=5, available_slots=["10:00 AM"]
            )
        }
    )
    router = HospitalRouter(hospitals=[hosp])
    recs = router.rank_hospitals("ROUTINE", target_department="Cardiology")
    assert len(recs) == 0, "Hospital without requested department or General Medicine fallback must be skipped"


# 13. EXTREME DISTANCE SCORE CLAMPING
def test_adv_13_extreme_distance_penalty():
    # Tokyo coordinates (13,000+ km away)
    router = HospitalRouter()
    recs = router.rank_hospitals("ROUTINE", patient_lat=35.6762, patient_lon=139.6503)
    assert len(recs) > 0
    for r in recs:
        assert r.score >= 0.0, "Composite score must not become negative"


# 14. MAXIMUM HOSPITAL LOAD (100% LOAD)
def test_adv_14_max_hospital_load_100_percent():
    hosp = Hospital(
        id="hosp_overloaded",
        name="Overloaded Hospital",
        city="Mumbai",
        latitude=19.01,
        longitude=72.85,
        current_load_percent=100.0,
        departments={
            "General Medicine": Department(
                id="dept_ovr", hospital_id="hosp_overloaded", name="General Medicine",
                open_now=True, queue_length=20, estimated_wait_min=60, available_slots=["04:00 PM"]
            )
        }
    )
    router = HospitalRouter(hospitals=[hosp])
    recs = router.rank_hospitals("ROUTINE")
    assert len(recs) == 1
    assert recs[0].score >= 0.0


# 15. QR PAYLOAD JSON VALIDITY & MANDATORY KEYS
def test_adv_15_qr_payload_json_validity():
    token = OPDTokenGenerator.generate_token(
        patient_id="patient_qr_test",
        hospital_name="Sassoon General Hospital",
        department_name="Gastroenterology",
        slot_time="02:00 PM",
        current_queue_length=3
    )
    qr_dict = json.loads(token.qr_payload)
    required_keys = ["token_id", "patient_id", "hospital", "dept", "slot", "queue_no", "issued_at"]
    for k in required_keys:
        assert k in qr_dict
        assert qr_dict[k] is not None


# 16. SPECIAL CHARACTERS IN PATIENT ID
def test_adv_16_special_characters_patient_id():
    token = OPDTokenGenerator.generate_token(
        patient_id="PATIENT#99/MARATHI-मराठी<script>",
        hospital_name="KEM Hospital",
        department_name="General Medicine",
        slot_time="10:00 AM"
    )
    assert token.patient_id == "PATIENT#99/MARATHI-मराठी<script>"
    qr_dict = json.loads(token.qr_payload)
    assert qr_dict["patient_id"] == "PATIENT#99/MARATHI-मराठी<script>"


# 17. TOKEN ID FORMAT CONTRACT
def test_adv_17_token_id_format_contract():
    token = OPDTokenGenerator.generate_token(
        patient_id="p_contract",
        hospital_name="KEM Hospital",
        department_name="Cardiology",
        slot_time="11:00 AM"
    )
    assert re.match(r"^OPD-[A-Z0-9]{3,4}-[A-Z0-9]{4,8}$", token.token_id) is not None


# 18. SAME LOCATION ZERO DISTANCE SCORE
def test_adv_18_same_location_zero_distance():
    # KEM hospital coordinates (19.0024, 72.8423)
    router = HospitalRouter()
    recs = router.rank_hospitals("ROUTINE", target_department="General Medicine", patient_lat=19.0024, patient_lon=72.8423)
    assert len(recs) > 0
    kem_rec = [r for r in recs if r.hospital.id == "hosp_mumbai_01"][0]
    assert kem_rec.distance_km == 0.0


# 19. EMERGENCY VS ROUTINE WEIGHTING DIFFERENCE
def test_adv_19_emergency_priority_weighting():
    router = HospitalRouter()
    recs_emg = router.rank_hospitals("EMERGENCY", target_department="General Medicine", patient_lat=19.01, patient_lon=72.85)
    recs_rtn = router.rank_hospitals("ROUTINE", target_department="General Medicine", patient_lat=19.01, patient_lon=72.85)
    
    assert recs_emg[0].explanation.startswith("Emergency Priority:")
    assert recs_rtn[0].explanation.startswith("Routine Score:")


# 20. TOKEN STATUS VALID TRANSITIONS
def test_adv_20_token_status_transitions():
    token = OPDTokenGenerator.generate_token(
        patient_id="p_status_test",
        hospital_name="GMCH Nagpur",
        department_name="General Medicine",
        slot_time="09:30 AM"
    )
    assert token.status == "ISSUED"
    token.status = "CHECKED_IN"
    assert token.status == "CHECKED_IN"
    token.status = "COMPLETED"
    assert token.status == "COMPLETED"
