"""
MahaArogya — Role-Based Access Control (RBAC) System
Defines UserRoles, Permissions, and Scopes for the admin ecosystem.
Enforces strict security boundaries on API endpoints.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException, status


class UserRole(str, Enum):
    GOVERNMENT = "GOVERNMENT"
    HOSPITAL_HEAD = "HOSPITAL_HEAD"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    RECEPTION = "RECEPTION"
    EMERGENCY_CONTROL = "EMERGENCY_CONTROL"
    BLOOD_BANK = "BLOOD_BANK"
    PHARMACY = "PHARMACY"


class Permission(str, Enum):
    # Public & Citizen
    ASSESS_SYMPTOMS = "ASSESS_SYMPTOMS"
    BOOK_OPD_SLOT = "BOOK_OPD_SLOT"
    VIEW_MY_TOKEN = "VIEW_MY_TOKEN"

    # Reception
    LOOKUP_TOKEN = "LOOKUP_TOKEN"
    CHECKIN_PATIENT = "CHECKIN_PATIENT"
    MARK_NO_SHOW = "MARK_NO_SHOW"

    # Nurse
    VIEW_WARD_PATIENTS = "VIEW_WARD_PATIENTS"
    UPDATE_BED_STATUS = "UPDATE_BED_STATUS"
    RECORD_VITALS = "RECORD_VITALS"

    # Doctor
    VIEW_CLINICAL_SUMMARY = "VIEW_CLINICAL_SUMMARY"
    WRITE_PRESCRIPTION = "WRITE_PRESCRIPTION"
    REFER_PATIENT = "REFER_PATIENT"

    # Emergency Control
    VIEW_EMERGENCY_ALERTS = "VIEW_EMERGENCY_ALERTS"
    DISPATCH_AMBULANCE = "DISPATCH_AMBULANCE"

    # Hospital Head
    MANAGE_HOSPITAL_RESOURCES = "MANAGE_HOSPITAL_RESOURCES"
    MANAGE_STAFF = "MANAGE_STAFF"

    # Government
    VIEW_GOVT_ANALYTICS = "VIEW_GOVT_ANALYTICS"
    VIEW_NETWORK_FORECASTS = "VIEW_NETWORK_FORECASTS"


ROLE_PERMISSIONS: dict[UserRole, list[Permission]] = {
    UserRole.RECEPTION: [
        Permission.LOOKUP_TOKEN,
        Permission.CHECKIN_PATIENT,
        Permission.MARK_NO_SHOW
    ],
    UserRole.NURSE: [
        Permission.VIEW_WARD_PATIENTS,
        Permission.UPDATE_BED_STATUS,
        Permission.RECORD_VITALS
    ],
    UserRole.DOCTOR: [
        Permission.VIEW_CLINICAL_SUMMARY,
        Permission.WRITE_PRESCRIPTION,
        Permission.REFER_PATIENT,
        Permission.RECORD_VITALS
    ],
    UserRole.EMERGENCY_CONTROL: [
        Permission.VIEW_EMERGENCY_ALERTS,
        Permission.DISPATCH_AMBULANCE
    ],
    UserRole.HOSPITAL_HEAD: [
        Permission.MANAGE_HOSPITAL_RESOURCES,
        Permission.MANAGE_STAFF,
        Permission.VIEW_CLINICAL_SUMMARY,
        Permission.LOOKUP_TOKEN,
        Permission.VIEW_EMERGENCY_ALERTS,
        Permission.UPDATE_BED_STATUS
    ],
    UserRole.GOVERNMENT: [
        Permission.VIEW_GOVT_ANALYTICS,
        Permission.VIEW_NETWORK_FORECASTS
    ]
}


class AuthUser(BaseModel):
    user_id: str
    name: str
    role: UserRole
    hospital_id: Optional[str] = None
    ward_id: Optional[str] = None
    assigned_patient_ids: List[str] = Field(default_factory=list)

    def has_permission(self, perm: Permission) -> bool:
        """Checks if user role has the required permission."""
        allowed = ROLE_PERMISSIONS.get(self.role, [])
        return perm in allowed


# Authentic User Registry Directory for User Lookup
MOCK_USER_REGISTRY: dict[str, AuthUser] = {
    "reception_staff_01": AuthUser(user_id="reception_staff_01", name="Staff Kulkarni", role=UserRole.RECEPTION, hospital_id="hosp_mumbai_01"),
    "doctor_user_01": AuthUser(user_id="doctor_user_01", name="Dr. Patil", role=UserRole.DOCTOR, hospital_id="hosp_mumbai_01"),
    "nurse_user_01": AuthUser(user_id="nurse_user_01", name="Nurse Shinde", role=UserRole.NURSE, hospital_id="hosp_mumbai_01"),
    "govt_official_01": AuthUser(user_id="govt_official_01", name="Officer Deshmukh", role=UserRole.GOVERNMENT),
    "hospital_head_01": AuthUser(user_id="hospital_head_01", name="Dr. Mehta", role=UserRole.HOSPITAL_HEAD, hospital_id="hosp_mumbai_01"),
}


def get_authenticated_user(user_id: Optional[str]) -> AuthUser:
    """Resolves AuthUser from registry; raises HTTP 401 if missing or invalid."""
    if not user_id or not str(user_id).strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Required: Missing staff_user_id."
        )

    user = MOCK_USER_REGISTRY.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication Failed: Unrecognized user_id '{user_id}'."
        )

    return user
