from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/hospitals", tags=["Hospitals"])

class Hospital(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    beds_available: int
    total_beds: int
    icu_available: int
    type: str

MOCK_HOSPITALS = [
    {"id": "h1", "name": "Civil Hospital, Thane", "lat": 19.1943, "lng": 72.9759, "beds_available": 12, "total_beds": 150, "icu_available": 2, "type": "Government"},
    {"id": "h2", "name": "KEM Hospital, Mumbai", "lat": 19.0033, "lng": 72.8412, "beds_available": 0, "total_beds": 500, "icu_available": 0, "type": "Government"},
    {"id": "h3", "name": "Jupiter Hospital", "lat": 19.2131, "lng": 72.9733, "beds_available": 45, "total_beds": 200, "icu_available": 10, "type": "Private"},
]

@router.get("/", response_model=List[Hospital])
def get_hospitals():
    return MOCK_HOSPITALS

@router.get("/{hospital_id}", response_model=Hospital)
def get_hospital(hospital_id: str):
    for h in MOCK_HOSPITALS:
        if h["id"] == hospital_id:
            return h
    return {"error": "not found"}
