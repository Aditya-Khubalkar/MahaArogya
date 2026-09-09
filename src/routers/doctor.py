from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])

class ConsultationItem(BaseModel):
    token_id: str
    patient_name: str
    age: int
    gender: str
    triage_category: str
    predicted_condition: str
    wait_time: int
    status: str

MOCK_DOCTOR_QUEUE = [
    {
        "token_id": "T-105",
        "patient_name": "Ramesh P.",
        "age": 45,
        "gender": "M",
        "triage_category": "PRIORITY",
        "predicted_condition": "Acute Gastroenteritis",
        "wait_time": 12,
        "status": "WAITING"
    },
    {
        "token_id": "T-106",
        "patient_name": "Sunita K.",
        "age": 32,
        "gender": "F",
        "triage_category": "ROUTINE",
        "predicted_condition": "Viral Fever",
        "wait_time": 25,
        "status": "WAITING"
    }
]

@router.get("/queue", response_model=List[ConsultationItem])
def get_doctor_queue():
    return MOCK_DOCTOR_QUEUE
