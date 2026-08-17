"""
Unit tests for Reception & Offline Hospital Arrival Workflow.
"""

import pytest
from ai.routing.opd_token import OPDTokenGenerator
from src.reception.workflow import ReceptionWorkflowManager


def test_reception_checkin_flow():
    token = OPDTokenGenerator.generate_token(
        patient_id="p_101",
        hospital_name="KEM General Hospital",
        department_name="General Medicine",
        slot_time="10:00 AM",
        current_queue_length=4
    )
    
    mgr = ReceptionWorkflowManager()
    entry = mgr.register_token(token)
    assert entry.arrival_status == "ISSUED"

    # Reception performs check-in
    checked_entry = mgr.checkin_patient(token.token_id)
    assert checked_entry.arrival_status == "CHECKED_IN"
    assert checked_entry.checked_in_at is not None
    assert len(mgr.audit_log) == 1
    assert mgr.audit_log[0]["event"] == "PATIENT_CHECKED_IN"


def test_reception_mark_no_show():
    token = OPDTokenGenerator.generate_token(
        patient_id="p_102",
        hospital_name="Sassoon Hospital",
        department_name="Gastroenterology",
        slot_time="11:00 AM"
    )
    
    mgr = ReceptionWorkflowManager()
    mgr.register_token(token)
    
    no_show_entry = mgr.mark_no_show(token.token_id)
    assert no_show_entry.arrival_status == "NO_SHOW"
