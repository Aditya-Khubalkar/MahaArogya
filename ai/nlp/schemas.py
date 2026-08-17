"""
MahaArogya — Medical NLP Extraction & Annotation Schemas
Spec Phase 6A: Structured multilingual medical entity & state representation.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MedicalAnnotationRecord(BaseModel):
    id: str = Field(..., description="Unique record identifier")
    text: str = Field(..., description="Raw text statement")
    language: str = Field(..., description="Language code ('mr', 'hi', 'en', 'roman-mr', 'hinglish')")
    normalized_text: str = Field(default="", description="Normalized medical sentence")
    
    symptoms: List[str] = Field(default_factory=list, description="Extracted symptom entities")
    body_locations: List[str] = Field(default_factory=list, description="Extracted body locations")
    duration: Optional[str] = Field(default=None, description="Duration string (e.g. '2 days')")
    onset: Optional[str] = Field(default=None, description="Onset string (e.g. 'yesterday')")
    severity: Optional[str] = Field(default=None, description="Severity rating ('mild', 'moderate', 'severe')")
    frequency: Optional[str] = Field(default=None, description="Frequency (e.g. '2 times')")
    
    associated_symptoms: List[str] = Field(default_factory=list, description="Co-occurring symptoms")
    negated_symptoms: List[str] = Field(default_factory=list, description="Explicitly negated symptoms")
    uncertain_symptoms: List[str] = Field(default_factory=list, description="Uncertain / ambiguous symptoms")
    
    vitals: Dict[str, Any] = Field(default_factory=dict, description="Extracted vitals")
    history: List[str] = Field(default_factory=list, description="Medical history")
    medications: List[str] = Field(default_factory=list, description="Medications mentioned")
    allergies: List[str] = Field(default_factory=list, description="Allergies mentioned")
    
    source_type: str = Field(default="synthetic", description="['manual', 'synthetic', 'public']")
    source_reference: str = Field(default="MahaArogya-Phase6-Engine")
    license: str = Field(default="Project-internal")
    review_status: str = Field(default="approved", description="['unreviewed', 'approved', 'rejected']")
