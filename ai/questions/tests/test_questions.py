"""
Unit tests for Approved Question Selector Engine.
Verifies priority ranking, red flag escalation, and language localization.
"""

import pytest
from ai.patient_state.schemas import PatientStateDelta, SymptomDetail
from ai.patient_state.state_manager import PatientStateManager
from ai.questions.selector import QuestionSelector


def test_abdo_duration_question_selection():
    mgr = PatientStateManager("conv_q1", language="mr")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_q1",
        new_input="Majha pot dukhtay.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True)}
    ))
    
    selector = QuestionSelector()
    res = selector.select_next_question(mgr.get_state())
    
    assert res.selected_question is not None
    assert res.selected_question.question_id == "q_abdo_duration"
    assert res.wording == "कधीपासून पोट दुखत आहे?"
    assert res.is_ready_for_triage is False


def test_chest_pain_emergency_question_priority():
    mgr = PatientStateManager("conv_q2", language="hi")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_q2",
        new_input="छाती में बहुत तेज दर्द हो रहा है।",
        new_symptoms={"chest_pain": SymptomDetail(present=True, severity="severe")}
    ))
    
    selector = QuestionSelector()
    res = selector.select_next_question(mgr.get_state())
    
    assert res.selected_question is not None
    assert res.selected_question.question_id == "q_chest_pain_radiate"
    assert res.selected_question.priority == 1
    assert "बाएं हाथ" in res.wording


def test_ready_for_triage_when_info_complete():
    mgr = PatientStateManager("conv_q3", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_q3",
        new_input="I have abdominal pain for 2 days. No fever, no vomiting.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, duration="2 days")},
        new_negations=["fever", "vomiting", "chest_pain"]
    ))
    
    selector = QuestionSelector()
    res = selector.select_next_question(mgr.get_state())
    
    assert res.is_ready_for_triage is True
    assert res.selected_question is None
