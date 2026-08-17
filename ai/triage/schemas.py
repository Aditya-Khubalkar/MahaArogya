"""
MahaArogya — Triage & Safety Layer Data Schemas
Structured triage classification result and safety rule audit models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SafetyRuleResult(BaseModel):
    is_emergency: bool = Field(default=False, description="True if any red-flag safety rule was triggered")
    triggered_rule_ids: List[str] = Field(default_factory=list, description="IDs of triggered safety rules")
    risk_signals: List[str] = Field(default_factory=list, description="Clinical risk descriptors")
    escalation_level: str = Field(default="NONE", description="['NONE', 'OPD_ROUTINE', 'URGENT_EVALUATION', 'EMERGENCY_AMBULANCE']")
    explanation: str = Field(default="", description="Audit explanation for triggered safety rules")


class TriageDecision(BaseModel):
    triage_category: str = Field(..., description="['ROUTINE', 'PRIORITY', 'URGENT', 'EMERGENCY']")
    triage_confidence: float = Field(..., description="Model/Rule confidence score (0.0 to 1.0)")
    triggered_rule_ids: List[str] = Field(default_factory=list, description="List of triggered red flag rules")
    risk_signals: List[str] = Field(default_factory=list, description="Clinical risk descriptors")
    escalation_level: str = Field(..., description="Recommended care escalation level")
    explanation: str = Field(..., description="Clinical audit rationale")
    safe_response_text: str = Field(..., description="User-facing safe response template")
    model_version: str = Field(default="v1.0-safety-engine", description="Model & Rule engine version")
