"""
MahaArogya — Unified Conversation Orchestrator
Target Architecture: Merges Voice (ASR + TTS) and Text modalities into ONE central medical engine.
Pipeline:
  Input -> ASR (if voice) -> Extractor -> PatientState -> Question Selector -> Triage -> Router -> TTS (if voice)
"""

import time
import uuid
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from ai.asr.service import get_asr_service
from ai.tts.service import get_tts_service
from ai.tts.schemas import TTSRequest
from ai.nlp.extractor import MedicalExtractor
from ai.patient_state.state_manager import PatientStateManager
from ai.patient_state.schemas import PatientState
from ai.questions.selector import QuestionSelector
from ai.triage.classifier import TriageClassifier
from ai.triage.schemas import TriageDecision
from ai.routing.router import HospitalRouter
from ai.routing.schemas import HospitalRecommendation

SYMPTOM_DEPARTMENT_MAP = {
    "abdominal_pain": "Gastroenterology",
    "chest_pain": "Cardiology",
    "breathlessness": "Pulmonology",
    "headache": "Neurology",
    "joint_pain": "Orthopedics",
    "burning_urination": "Urology",
    "sore_throat": "ENT",
    "fever": "General Medicine",
    "vomiting": "Gastroenterology",
    "diarrhea": "Gastroenterology",
    "dizziness": "Neurology",
    "numbness": "Neurology",
    "cough": "Pulmonology",
    "swelling": "General Medicine",
    "fatigue": "General Medicine",
    "nausea": "Gastroenterology",
}


class UnifiedTurnResponse(BaseModel):
    conversation_id: str
    modality: str  # 'voice' or 'text'
    language: str
    transcript_or_text: str
    ai_response_text: str
    audio_response_path: Optional[str] = None
    
    patient_state: PatientState
    triage_decision: TriageDecision
    is_ready_for_triage: bool
    
    hospital_recommendations: list[HospitalRecommendation] = Field(default_factory=list)
    latency_total_sec: float


class MahaArogyaOrchestrator:
    """Unified Orchestrator merging ASR, NLP, Memory, Questions, Triage, Routing, and TTS."""

    def __init__(self):
        self.extractor = MedicalExtractor()
        self.question_selector = QuestionSelector()
        self.triage_classifier = TriageClassifier()
        self.router = HospitalRouter()
        self.sessions: dict[str, PatientStateManager] = {}

    def get_or_create_session(
        self,
        conversation_id: Optional[str] = None,
        language: str = "mr",
        modality: str = "voice"
    ) -> PatientStateManager:
        cid = conversation_id or f"session_{uuid.uuid4().hex[:8]}"
        if cid not in self.sessions:
            self.sessions[cid] = PatientStateManager(
                conversation_id=cid,
                language=language,
                modality=modality
            )
        return self.sessions[cid]

    def process_turn(
        self,
        conversation_id: Optional[str] = None,
        text_input: Optional[str] = None,
        audio_path: Optional[str] = None,
        language: str = "mr",
        modality: str = "voice",
        patient_lat: float = 19.0100,
        patient_lon: float = 72.8500
    ) -> UnifiedTurnResponse:
        if modality not in ["voice", "text"]:
            raise ValueError("Modality must be 'voice' or 'text'")

        start_t = time.time()
        mgr = self.get_or_create_session(conversation_id, language=language, modality=modality)
        
        # Step 1: ASR if voice input
        if modality == "voice" and audio_path:
            asr_svc = get_asr_service()
            asr_res = asr_svc.transcribe(audio_path, language=language)
            raw_input = asr_res.transcript
        else:
            raw_input = text_input or "नमस्कार"

        # Step 2: Extract medical entities
        delta = self.extractor.extract(mgr.state.conversation_id, raw_input)
        state = mgr.update_with_delta(delta)

        # Step 3: Select next approved question or signal triage readiness
        q_res = self.question_selector.select_next_question(state)

        # Step 4: Run Triage & Safety Classifier
        triage_decision = self.triage_classifier.classify(state)

        # Step 5: Rank suitable hospitals if triage is ready or emergency
        hosp_recs = []
        if q_res.is_ready_for_triage or triage_decision.triage_category in ["EMERGENCY", "URGENT"]:
            target_dept = "General Medicine"
            for symptom_key in SYMPTOM_DEPARTMENT_MAP:
                if symptom_key in state.symptoms:
                    target_dept = SYMPTOM_DEPARTMENT_MAP[symptom_key]
                    break
            hosp_recs = self.router.rank_hospitals(
                triage_category=triage_decision.triage_category,
                target_department=target_dept,
                patient_lat=patient_lat,
                patient_lon=patient_lon
            )

        # Step 6: Determine AI text response
        if not q_res.is_ready_for_triage and q_res.wording and triage_decision.triage_category != "EMERGENCY":
            ai_response_text = q_res.wording
        else:
            ai_response_text = triage_decision.safe_response_text

        # Step 7: TTS if voice mode
        audio_out_path = None
        if modality == "voice":
            tts_svc = get_tts_service()
            tts_res = tts_svc.synthesize(TTSRequest(text=ai_response_text, language=language))
            audio_out_path = tts_res.audio_path

        total_latency = round(time.time() - start_t, 3)

        return UnifiedTurnResponse(
            conversation_id=mgr.state.conversation_id,
            modality=modality,
            language=language,
            transcript_or_text=raw_input,
            ai_response_text=ai_response_text,
            audio_response_path=audio_out_path,
            patient_state=state,
            triage_decision=triage_decision,
            is_ready_for_triage=q_res.is_ready_for_triage,
            hospital_recommendations=hosp_recs,
            latency_total_sec=total_latency
        )
