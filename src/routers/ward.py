from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/ward", tags=["Ward"])

class PatientVitals(BaseModel):
    bed_id: str
    patient_name: str
    heart_rate: int
    blood_pressure: str
    oxygen_saturation: int
    temperature: float
    status: str
    last_updated: str

MOCK_WARD_PATIENTS = [
    {
        "bed_id": "W-A-01",
        "patient_name": "Ramesh P.",
        "heart_rate": 82,
        "blood_pressure": "120/80",
        "oxygen_saturation": 98,
        "temperature": 98.6,
        "status": "STABLE",
        "last_updated": "2 mins ago"
    },
    {
        "bed_id": "W-A-02",
        "patient_name": "Sunita K.",
        "heart_rate": 110,
        "blood_pressure": "140/90",
        "oxygen_saturation": 92,
        "temperature": 101.2,
        "status": "ATTENTION",
        "last_updated": "Just now"
    },
    {
        "bed_id": "W-A-03",
        "patient_name": "Ashok M.",
        "heart_rate": 70,
        "blood_pressure": "118/75",
        "oxygen_saturation": 99,
        "temperature": 98.2,
        "status": "STABLE",
        "last_updated": "5 mins ago"
    }
]

@router.get("/patients", response_model=List[PatientVitals])
def get_ward_patients():
    return MOCK_WARD_PATIENTS
