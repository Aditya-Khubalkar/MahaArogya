"""
MahaArogya — PatientState Memory Manager
Manages deterministic state updates, state deltas, and missing information tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional
from ai.patient_state.schemas import PatientState, PatientStateDelta, SymptomDetail, Vitals


class PatientStateManager:
    """Manages creation, state deltas, and updates for a PatientState session."""

    def __init__(self, conversation_id: str, patient_id: str = "demo_patient_001", language: str = "mr", modality: str = "voice"):
        self.state = PatientState(
            conversation_id=conversation_id,
            patient_id=patient_id,
            language=language,
            modality=modality
        )
        self.history_deltas: List[PatientStateDelta] = []
        self._recalculate_missing_info()

    def update_with_delta(self, delta: PatientStateDelta) -> PatientState:
        """Applies a state delta update without losing prior state history."""
        self.state.original_input_history.append(delta.new_input)
        self.state.latest_input = delta.new_input
        self.state.updated_at = datetime.now().isoformat()

        # Update symptoms
        for sym_name, detail in delta.new_symptoms.items():
            if sym_name in self.state.symptoms:
                # Merge existing details with new info
                existing = self.state.symptoms[sym_name]
                merged_detail = SymptomDetail(
                    present=detail.present if detail.present is not None else existing.present,
                    location=detail.location or existing.location,
                    duration=detail.duration or existing.duration,
                    onset=detail.onset or existing.onset,
                    severity=detail.severity or existing.severity,
                    frequency=detail.frequency or existing.frequency,
                    progression=detail.progression or existing.progression
                )
                self.state.symptoms[sym_name] = merged_detail
            else:
                self.state.symptoms[sym_name] = detail

        # Update negations
        for neg in delta.new_negations:
            if neg not in self.state.negated_symptoms:
                self.state.negated_symptoms.append(neg)

        # Update vitals
        if delta.new_vitals:
            v_dict = delta.new_vitals.model_dump(exclude_unset=True)
            current_v = self.state.vitals.model_dump()
            current_v.update(v_dict)
            self.state.vitals = Vitals(**current_v)

        # Update answers
        self.state.answers.update(delta.new_answers)

        # Record delta
        self.history_deltas.append(delta)

        # Recalculate missing information
        self._recalculate_missing_info()

        return self.state

    def _recalculate_missing_info(self):
        """Identifies what key medical facts are still unknown."""
        missing = []
        
        # Check if any symptom is present without duration
        for sym, detail in self.state.symptoms.items():
            if detail.present and not detail.duration:
                missing.append(f"{sym}_duration")
            if detail.present and not detail.severity:
                missing.append(f"{sym}_severity")

        # Check key red flag screening questions
        if "vomiting" not in self.state.symptoms and "vomiting" not in self.state.negated_symptoms:
            missing.append("vomiting_status")
        if "fever" not in self.state.symptoms and "fever" not in self.state.negated_symptoms:
            missing.append("fever_status")
        if "chest_pain" not in self.state.symptoms and "chest_pain" not in self.state.negated_symptoms:
            missing.append("chest_pain_status")

        self.state.missing_information = missing

    def get_state(self) -> PatientState:
        return self.state
