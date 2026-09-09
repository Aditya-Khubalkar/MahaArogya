from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

class AdminOverview(BaseModel):
    total_beds: int
    occupied_beds: int
    icu_total: int
    icu_occupied: int
    avg_triage_time_sec: float
    avg_wait_time_min: int

MOCK_ADMIN_OVERVIEW = {
    "total_beds": 500,
    "occupied_beds": 420,
    "icu_total": 50,
    "icu_occupied": 48,
    "avg_triage_time_sec": 4.5,
    "avg_wait_time_min": 25
}

@router.get("/overview", response_model=AdminOverview)
def get_admin_overview():
    return MOCK_ADMIN_OVERVIEW
