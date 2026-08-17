"""
Unit tests for RBAC Security & Authorization System.
Tests exact role restriction scenarios from Spec Prompt 14A.
"""

import pytest
from fastapi import HTTPException
from src.rbac.models import AuthUser, UserRole, Permission
from src.rbac.middleware import enforce_permission, enforce_hospital_scope


def test_doctor_clinical_access_allowed():
    doc = AuthUser(user_id="doc_01", name="Dr. Patil", role=UserRole.DOCTOR, hospital_id="hosp_mumbai_01")
    # Should not raise exception
    enforce_permission(doc, Permission.VIEW_CLINICAL_SUMMARY)


def test_doctor_govt_analytics_forbidden():
    doc = AuthUser(user_id="doc_01", name="Dr. Patil", role=UserRole.DOCTOR, hospital_id="hosp_mumbai_01")
    with pytest.raises(HTTPException) as exc_info:
        enforce_permission(doc, Permission.VIEW_GOVT_ANALYTICS)
    assert exc_info.value.status_code == 403


def test_reception_checkin_allowed():
    rec = AuthUser(user_id="rec_01", name="Staff Kulkarni", role=UserRole.RECEPTION, hospital_id="hosp_mumbai_01")
    enforce_permission(rec, Permission.CHECKIN_PATIENT)


def test_nurse_staff_management_forbidden():
    nurse = AuthUser(user_id="nurse_01", name="Nurse Shinde", role=UserRole.NURSE, hospital_id="hosp_mumbai_01")
    with pytest.raises(HTTPException) as exc_info:
        enforce_permission(nurse, Permission.MANAGE_STAFF)
    assert exc_info.value.status_code == 403


def test_hospital_scope_restriction():
    doc = AuthUser(user_id="doc_01", name="Dr. Patil", role=UserRole.DOCTOR, hospital_id="hosp_mumbai_01")
    # Same hospital -> OK
    enforce_hospital_scope(doc, "hosp_mumbai_01")
    
    # Different hospital -> 403
    with pytest.raises(HTTPException) as exc_info:
        enforce_hospital_scope(doc, "hosp_pune_01")
    assert exc_info.value.status_code == 403
