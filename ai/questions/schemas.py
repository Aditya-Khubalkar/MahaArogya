"""
MahaArogya — Question Engine Schemas
Versioned, approved question bank item representation.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ApprovedQuestion(BaseModel):
    question_id: str = Field(..., description="Unique question ID (e.g. 'q_abdo_duration')")
    topic: str = Field(..., description="Symptom module (e.g. 'abdominal_pain', 'fever', 'chest_pain')")
    purpose: str = Field(..., description="Clinical rationale for question")
    
    # Multilingual patient-friendly wording
    wording_mr: str = Field(..., description="Marathi wording")
    wording_hi: str = Field(..., description="Hindi wording")
    wording_en: str = Field(..., description="English wording")
    wording_roman_mr: str = Field(..., description="Roman Marathi wording")
    wording_hinglish: str = Field(..., description="Hinglish wording")

    information_collected: str = Field(..., description="Field updated by answer (e.g. 'duration', 'vomiting_status')")
    priority: int = Field(default=5, description="Priority rank (1=mandatory red flag, 10=routine detail)")
    emergency_relevance: bool = Field(default=False, description="True if evaluating acute red flag")
    required_before_triage: bool = Field(default=False, description="True if mandatory prior to triage decision")
    safety_notes: Optional[str] = Field(default=None)


class QuestionSelectionResult(BaseModel):
    selected_question: Optional[ApprovedQuestion] = Field(default=None, description="Chosen question from approved bank")
    wording: str = Field(default="", description="Localized question text")
    is_ready_for_triage: bool = Field(default=False, description="True if sufficient info exists for triage decision")
    reasoning: str = Field(default="", description="Selection audit rationale")
