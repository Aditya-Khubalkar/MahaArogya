from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/queue", tags=["Queue"])

class QueueItem(BaseModel):
    token_id: str
    patient_name: str
    status: str # "WAITING", "IN_CONSULTATION", "DONE"
    department: str
    estimated_wait_time: int

MOCK_QUEUE = [
    {"token_id": "T-100", "patient_name": "Ramesh P.", "status": "IN_CONSULTATION", "department": "General Medicine", "estimated_wait_time": 0},
    {"token_id": "T-101", "patient_name": "Sunita K.", "status": "WAITING", "department": "General Medicine", "estimated_wait_time": 15},
    {"token_id": "T-102", "patient_name": "Ashok M.", "status": "WAITING", "department": "Cardiology", "estimated_wait_time": 30},
]

@router.get("/", response_model=List[QueueItem])
def get_queue():
    return MOCK_QUEUE

@router.get("/live", response_model=List[QueueItem])
def get_live_queue():
    return MOCK_QUEUE
