"""
MahaArogya — Adaptive Question Selector Engine
Consumes PatientState memory, filters out asked & negated questions, enforces safety priority,
and selects EXACTLY ONE approved question from the versioned bank.
"""

from typing import Optional
from ai.patient_state.schemas import PatientState
from ai.questions.schemas import ApprovedQuestion, QuestionSelectionResult
from ai.questions.question_bank import get_all_questions


class QuestionSelector:
    """Intelligent Question Selector engine for task-oriented medical dialogue."""

    def __init__(self, question_bank: Optional[list[ApprovedQuestion]] = None):
        self.question_bank = question_bank or get_all_questions()

    def select_next_question(self, state: PatientState) -> QuestionSelectionResult:
        """
        Selects the next best approved question for the current patient state.
        
        Args:
            state: Current PatientState memory instance

        Returns:
            QuestionSelectionResult with selected_question, localized wording, and triage readiness.
        """
        lang = state.language or "mr"
        
        # Collect already gathered information keys (only non-None values)
        collected_info = {k for k, v in state.answers.items() if v is not None}
        for sym, detail in state.symptoms.items():
            collected_info.add(f"{sym}_status")
            if detail.duration:
                collected_info.add(f"{sym}_duration")

        for neg in state.negated_symptoms:
            collected_info.add(f"{neg}_status")

        # Step 1: Check emergency red-flag questions (Priority 1)
        for q in self.question_bank:
            if q.priority == 1 and q.information_collected not in collected_info:
                # Do not ask if symptom topic is explicitly negated
                if q.topic in state.negated_symptoms:
                    continue
                if q.topic in state.symptoms:
                    return self._build_result(q, lang, f"Mandatory emergency red flag question for topic '{q.topic}'")

        # Step 2: Check questions matching active symptoms
        eligible_questions = []
        for q in self.question_bank:
            if q.information_collected in collected_info:
                continue  # Already answered
            if q.topic in state.negated_symptoms:
                continue  # Explicitly negated topic
            
            # Check topic match with active symptoms
            if q.topic in state.symptoms:
                eligible_questions.append(q)

        if not eligible_questions:
            return QuestionSelectionResult(
                selected_question=None,
                wording="",
                is_ready_for_triage=True,
                reasoning="Sufficient information collected for safety triage decision."
            )

        # Sort eligible by priority (ascending, 1 is highest priority)
        eligible_questions.sort(key=lambda item: item.priority)
        best_question = eligible_questions[0]

        return self._build_result(
            best_question,
            lang,
            f"Selected question '{best_question.question_id}' based on missing info '{best_question.information_collected}'"
        )

    def _build_result(self, q: ApprovedQuestion, lang: str, reasoning: str) -> QuestionSelectionResult:
        """Pick localized wording for language."""
        if lang == "mr":
            text = q.wording_mr
        elif lang == "hi":
            text = q.wording_hi
        elif lang == "roman-mr":
            text = q.wording_roman_mr
        elif lang == "hinglish":
            text = q.wording_hinglish
        else:
            text = q.wording_en

        return QuestionSelectionResult(
            selected_question=q,
            wording=text,
            is_ready_for_triage=False,
            reasoning=reasoning
        )
