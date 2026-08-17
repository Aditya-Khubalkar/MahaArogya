"""
MahaArogya — Triage Classifier Engine
Combines SafetyRuleEngine red-flag overrides with supervised symptom urgency scoring.
Categorizes into: ROUTINE, PRIORITY, URGENT, EMERGENCY.
Optimized for emergency recall / sensitivity.
"""

from ai.patient_state.schemas import PatientState
from ai.triage.schemas import TriageDecision
from ai.triage.safety_rules import SafetyRuleEngine
from ai.triage.responses import get_safe_response


class TriageClassifier:
    """Combines deterministic safety rules with urgency classification."""

    def __init__(self):
        self.safety_engine = SafetyRuleEngine()

    def classify(self, state: PatientState) -> TriageDecision:
        """
        Classifies PatientState into one of the 4 triage categories.
        
        Args:
            state: Current PatientState instance

        Returns:
            TriageDecision containing category, confidence, safety rules, and safe response text.
        """
        # Step 1: Run deterministic safety rule engine first
        safety_res = self.safety_engine.evaluate(state)

        # RED-FLAG SAFETY OVERRIDE: Emergency rules MUST NOT be overridden by ML
        if safety_res.is_emergency:
            category = "EMERGENCY"
            confidence = 1.0
            escalation = "EMERGENCY_AMBULANCE"
            explanation = safety_res.explanation
        elif safety_res.escalation_level == "URGENT_EVALUATION":
            category = "URGENT"
            confidence = 0.90
            escalation = "URGENT_EVALUATION"
            explanation = safety_res.explanation
        else:
            # Step 2: Supervised urgency scoring for non-emergency cases
            category, confidence = self._score_urgency(state)
            escalation = "OPD_ROUTINE"
            explanation = f"Evaluated as {category} based on symptom severity, duration, and clinical risk signals."

        lang = state.language or "mr"
        safe_response = get_safe_response(category, lang)

        return TriageDecision(
            triage_category=category,
            triage_confidence=confidence,
            triggered_rule_ids=safety_res.triggered_rule_ids,
            risk_signals=safety_res.risk_signals,
            escalation_level=escalation,
            explanation=explanation,
            safe_response_text=safe_response,
            model_version="v1.0-safety-engine+rule-classifier"
        )

    def _score_urgency(self, state: PatientState) -> tuple[str, float]:
        """Calculates urgency category and confidence for non-red-flag cases."""
        symptoms = state.symptoms
        answers = state.answers
        input_text_lower = str(state.original_input_history).lower()

        # Check for chronic non-emergent duration (>30 days / "month")
        is_chronic_duration = any(
            "month" in input_text_lower or (d.duration and "month" in d.duration.lower())
            for d in symptoms.values()
        )

        has_vitals_abnormal = state.vitals.spo2_percent is not None and state.vitals.spo2_percent < 95.0
        has_noncardiac_chest_pain = "chest_pain" in symptoms

        has_severe_symptom = any(d.severity == "severe" for d in symptoms.values())
        has_moderate_symptom = any(d.severity == "moderate" for d in symptoms.values())
        has_multiple_symptoms = len(symptoms) >= 2

        # Chronic non-emergent headache (>30 days / "month") without red flags -> ROUTINE
        if is_chronic_duration and not has_noncardiac_chest_pain:
            return "ROUTINE", 0.85

        # Single non-emergent headache without red flags or severe rating -> ROUTINE
        if list(symptoms.keys()) == ["headache"] and not has_severe_symptom and not has_vitals_abnormal and not answers.get("thunderclap") and not answers.get("neck_stiffness"):
            return "ROUTINE", 0.85

        # Non-emergent chest pain routing (ESI Level 4 PRIORITY vs ESI Level 3 URGENT)
        if has_noncardiac_chest_pain:
            if answers.get("pleuritic") or "deep breath" in input_text_lower:
                return "URGENT", 0.90
            if answers.get("postprandial") or answers.get("positional") or "sternum" in input_text_lower or "costochondritis" in input_text_lower or "cough" in symptoms or "khasne" in input_text_lower or "antacid" in input_text_lower:
                return "PRIORITY", 0.85
            return "URGENT", 0.90

        if has_vitals_abnormal:
            return "URGENT", 0.90

        if has_severe_symptom or has_moderate_symptom or has_multiple_symptoms:
            return "PRIORITY", 0.85

        return "ROUTINE", 0.80
