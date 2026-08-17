"""
Unit tests for Hospital Routing & Smart OPD Token Generator.
"""

import json
import pytest
from ai.routing.router import HospitalRouter, haversine_distance
from ai.routing.opd_token import OPDTokenGenerator


def test_haversine_distance_accuracy():
    # Distance between Mumbai Central (19.01, 72.85) and Pune (18.52, 73.87) is ~120-130 km
    dist = haversine_distance(19.0100, 72.8500, 18.5284, 73.8739)
    assert 110.0 <= dist <= 140.0


def test_emergency_hospital_ranking():
    router = HospitalRouter()
    recs = router.rank_hospitals("EMERGENCY", target_department="Cardiology", patient_lat=19.01, patient_lon=72.85)
    
    assert len(recs) > 0
    top_recommendation = recs[0]
    assert top_recommendation.hospital.emergency_capable is True
    assert top_recommendation.score > 0.0


def test_routine_opd_ranking():
    router = HospitalRouter()
    recs = router.rank_hospitals("ROUTINE", target_department="General Medicine", patient_lat=19.01, patient_lon=72.85)
    
    assert len(recs) > 0
    top = recs[0]
    assert top.hospital.name is not None
    assert top.estimated_wait_min >= 0


def test_opd_token_generation():
    token = OPDTokenGenerator.generate_token(
        patient_id="p_9901",
        hospital_name="KEM General Hospital & Medical Center",
        department_name="Gastroenterology",
        slot_time="10:30 AM",
        current_queue_length=6
    )
    
    assert token.token_id.startswith("OPD-")
    assert token.queue_number == 7
    assert token.status == "ISSUED"
    
    qr_data = json.loads(token.qr_payload)
    assert qr_data["patient_id"] == "p_9901"
    assert qr_data["queue_no"] == 7
