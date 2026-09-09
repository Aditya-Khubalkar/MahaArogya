from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/govt", tags=["Government"])

class StateOverview(BaseModel):
    total_hospitals: int
    active_emergencies: int
    total_patients_today: int
    avg_occupancy_rate: float
    critical_supplies_alerts: int

MOCK_STATE_OVERVIEW = {
    "total_hospitals": 245,
    "active_emergencies": 12,
    "total_patients_today": 15420,
    "avg_occupancy_rate": 82.5,
    "critical_supplies_alerts": 3
}

@router.get("/state-overview", response_model=StateOverview)
def get_state_overview():
    return MOCK_STATE_OVERVIEW
