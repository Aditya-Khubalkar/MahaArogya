"""
MahaArogya — PatientState Data Models & Schemas
Structured, deterministic conversation memory representation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Vitals(BaseModel):
    temperature_f: Optional[float] = Field(default=None, description="Body temperature in Fahrenheit")
    bp_systolic: Optional[int] = Field(default=None, description="Systolic blood pressure")
    bp_diastolic: Optional[int] = Field(default=None, description="Diastolic blood pressure")
    pulse_rate: Optional[int] = Field(default=None, description="Heart rate / pulse in bpm")
    spo2_percent: Optional[float] = Field(default=None, description="Oxygen saturation SpO2 %")


class SymptomDetail(BaseModel):
    present: bool = Field(default=True, description="True if symptom is confirmed present")
    location: Optional[str] = Field(default=None, description="Body location (e.g. 'abdomen', 'chest')")
    duration: Optional[str] = Field(default=None, description="Duration (e.g. '2 days', '3 hours')")
    onset: Optional[str] = Field(default=None, description="Onset timing (e.g. 'sudden', 'gradual', 'yesterday')")
    severity: Optional[str] = Field(default=None, description="Severity rating ('mild', 'moderate', 'severe')")
    frequency: Optional[str] = Field(default=None, description="Frequency (e.g. '2 times', 'constant')")
    progression: Optional[str] = Field(default=None, description="Progression ('worsening', 'stable', 'improving')")


class PatientState(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation session UUID")
    # Demographics & Session
    patient_id: str = Field(default="demo_patient_001", description="Patient / anonymous demo ID")
    age_years: Optional[float] = Field(default=None, description="Patient age in years")
    gender: Optional[str] = Field(default=None, description="Patient gender")
    language: Optional[str] = Field(default="mr", description="Current language ('mr', 'hi', 'en', 'roman-mr', 'hinglish')")
    modality: str = Field(default="voice", description="Interaction modality ('voice' or 'text')")
    
    # Text records
    original_input_history: List[str] = Field(default_factory=list, description="Raw input history")
    latest_input: str = Field(default="", description="Most recent raw statement")
    normalized_text: str = Field(default="", description="Normalized medical text representation")

    # Structured medical facts
    symptoms: Dict[str, SymptomDetail] = Field(default_factory=dict, description="Extracted symptom entities and details")
    body_locations: List[str] = Field(default_factory=list, description="Target body locations")
    negated_symptoms: List[str] = Field(default_factory=list, description="Explicitly negated symptoms")
    uncertain_symptoms: List[str] = Field(default_factory=list, description="Symptoms expressed with uncertainty")
    
    # Clinical history & vitals
    vitals: Vitals = Field(default_factory=Vitals, description="Patient vitals")
    history: List[str] = Field(default_factory=list, description="Relevant medical history (e.g. 'diabetes', 'hypertension')")
    medications: List[str] = Field(default_factory=list, description="Current medications")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")

    # Conversation & question state
    answers: Dict[str, Any] = Field(default_factory=dict, description="Answers provided to system questions")
    missing_information: List[str] = Field(default_factory=list, description="Fields still required before triage")
    risk_signals: List[str] = Field(default_factory=list, description="Triggered clinical red flags / risk signals")
    
    # Triage decision support
    triage_category: str = Field(default="PENDING", description="['PENDING', 'ROUTINE', 'PRIORITY', 'URGENT', 'EMERGENCY']")
    triage_confidence: float = Field(default=0.0, description="Triage category confidence score")
    
    # Provenance metadata
    model_versions: Dict[str, str] = Field(default_factory=dict, description="Subsystem model versions used")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class PatientStateDelta(BaseModel):
    conversation_id: str
    new_input: str
    new_symptoms: Dict[str, SymptomDetail] = Field(default_factory=dict)
    new_negations: List[str] = Field(default_factory=list)
    new_vitals: Optional[Vitals] = None
    new_answers: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
