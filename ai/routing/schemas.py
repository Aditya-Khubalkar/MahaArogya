"""
MahaArogya — Hospital Routing & Smart OPD Schemas
Data models for hospital facilities, departments, routing recommendations, and OPD tokens.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Department(BaseModel):
    id: str = Field(..., description="Department ID (e.g. 'dept_gastro_01')")
    hospital_id: str = Field(..., description="Parent hospital ID")
    name: str = Field(..., description="Department name (e.g. 'Gastroenterology', 'General Medicine', 'Cardiology')")
    open_now: bool = Field(default=True, description="True if department is open now")
    queue_length: int = Field(default=5, description="Current waiting patient queue length")
    estimated_wait_min: int = Field(default=20, description="Estimated wait time in minutes")
    available_slots: List[str] = Field(default_factory=list, description="Available OPD slot timestamps")


class Hospital(BaseModel):
    id: str = Field(..., description="Hospital ID (e.g. 'hosp_mumbai_01')")
    name: str = Field(..., description="Hospital name")
    city: str = Field(..., description="City (e.g. 'Mumbai', 'Pune', 'Nagpur')")
    latitude: float = Field(..., description="GPS latitude")
    longitude: float = Field(..., description="GPS longitude")
    departments: Dict[str, Department] = Field(default_factory=dict, description="Departments available")
    operating_hours: str = Field(default="24x7", description="Operating hours string")
    emergency_capable: bool = Field(default=True, description="True if has 24x7 Emergency/ICU")
    resource_summary: Dict[str, Any] = Field(default_factory=dict, description="Beds, ventilators, oxygen info")
    current_load_percent: float = Field(default=65.0, description="Current hospital load percentage")


class HospitalRecommendation(BaseModel):
    hospital: Hospital
    department_name: str
    score: float = Field(..., description="Composite suitability score (higher is better)")
    distance_km: float = Field(..., description="Calculated distance in km")
    estimated_wait_min: int = Field(..., description="Estimated total wait time")
    explanation: str = Field(..., description="Transparent scoring breakdown")


class OPDToken(BaseModel):
    token_id: str = Field(..., description="Unique OPD token ID (e.g. 'OPD-MUM-8921')")
    patient_id: str = Field(..., description="Patient ID")
    hospital_name: str = Field(..., description="Hospital name")
    department_name: str = Field(..., description="Department name")
    slot_time: str = Field(..., description="Booked slot timestamp")
    queue_number: int = Field(..., description="Assigned token queue number")
    status: str = Field(default="ISSUED", description="['ISSUED', 'CHECKED_IN', 'IN_CONSULTATION', 'COMPLETED']")
    qr_payload: str = Field(..., description="QR code payload string")
    created_at: str = Field(..., description="Issuance timestamp")
