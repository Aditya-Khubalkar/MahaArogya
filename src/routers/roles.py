from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])

class RoleInfo(BaseModel):
    id: str
    title: str
    description: str
    permissions: List[str]

MOCK_ROLES = [
    {"id": "public", "title": "Public App", "description": "Patient facing app", "permissions": []},
    {"id": "reception", "title": "Receptionist", "description": "Manage check-ins", "permissions": ["checkin"]},
    {"id": "nurse", "title": "Nurse", "description": "Ward and vitals", "permissions": ["vitals", "ward"]},
    {"id": "doctor", "title": "Doctor", "description": "Consultation", "permissions": ["consult"]},
    {"id": "hospital_admin", "title": "Hospital Admin", "description": "Hospital metrics", "permissions": ["metrics"]},
    {"id": "hospital_head", "title": "Hospital Head", "description": "Hospital overview", "permissions": ["metrics"]},
    {"id": "district_officer", "title": "District Officer", "description": "District overview", "permissions": ["metrics_district"]},
    {"id": "government", "title": "State Government", "description": "State overview", "permissions": ["metrics_state"]},
]

@router.get("/", response_model=List[RoleInfo])
def get_roles():
    return MOCK_ROLES
