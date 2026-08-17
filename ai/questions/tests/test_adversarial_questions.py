"""
Hard Adversarial Test Suite for Approved Question Selector Engine (ai/questions/)
Covers 20 adversarial edge cases: ambiguous/conflicting answers, null fields, off-topic inputs,
repeated questions, multi-symptom overlap, and language boundaries.
"""

import pytest
from ai.patient_state.schemas import PatientState, PatientStateDelta, SymptomDetail, Vitals
from ai.patient_state.state_manager import PatientStateManager
from ai.questions.schemas import ApprovedQuestion, QuestionSelectionResult
from ai.questions.selector import QuestionSelector
from ai.questions.question_bank import APPROVED_QUESTION_BANK


# 1. EMPTY PATIENT STATE
def test_adv_01_empty_patient_state():
    state = PatientState(conversation_id="adv_01")
    selector = QuestionSelector()
    res = selector.select_next_question(state)
    assert res.is_ready_for_triage is True
    assert res.selected_question is None


# 2. UNKNOWN LANGUAGE FALLBACK
def test_adv_02_unknown_language_fallback():
    mgr = PatientStateManager("adv_02", language="fr")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_02",
        new_input="Douleur abdominale.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True)}
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.wording == res.selected_question.wording_en  # Fallback to English


# 3. CONFLICTING DURATION IN ANSWERS VS SYMPTOMS
def test_adv_03_conflicting_duration_answers():
    mgr = PatientStateManager("adv_03", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_03",
        new_input="Abdominal pain.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, duration="2 days")},
        new_answers={"abdominal_pain_duration": "3 hours"}
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    # Since duration is present in symptoms AND answers, duration question must not be re-asked
    assert res.selected_question is None or res.selected_question.question_id != "q_abdo_duration"


# 4. NEGATED PRIMARY SYMPTOM (EXPLICIT NEGATION)
def test_adv_04_negated_primary_symptom():
    mgr = PatientStateManager("adv_04", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_04",
        new_input="No chest pain, but stomach hurts.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True)},
        new_negations=["chest_pain"]
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.selected_question.topic != "chest_pain"
    assert res.selected_question.question_id != "q_chest_pain_radiate"


# 5. ALL SYMPTOMS NEGATED
def test_adv_05_all_symptoms_negated():
    mgr = PatientStateManager("adv_05", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_05",
        new_input="No chest pain, no fever, no vomiting.",
        new_negations=["chest_pain", "fever", "vomiting", "abdominal_pain"]
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.is_ready_for_triage is True
    assert res.selected_question is None


# 6. REPEATED QUESTION FILTERING
def test_adv_06_repeated_question_filtering():
    mgr = PatientStateManager("adv_06", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_06",
        new_input="Abdominal pain.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, duration="2 days")},
        new_answers={"abdominal_pain_duration": "2 days", "vomiting_status": "none", "fever_status": "none"}
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is None
    assert res.is_ready_for_triage is True


# 7. MULTI-SYMPTOM OVERLAP PRIORITY (CHEST PAIN VS ABDOMINAL PAIN)
def test_adv_07_multi_symptom_overlap_priority():
    mgr = PatientStateManager("adv_07", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_07",
        new_input="I have chest pain and stomach pain.",
        new_symptoms={
            "chest_pain": SymptomDetail(present=True, severity="severe"),
            "abdominal_pain": SymptomDetail(present=True, severity="mild")
        }
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.selected_question.question_id == "q_chest_pain_radiate"
    assert res.selected_question.priority == 1


# 8. OFF-TOPIC UTTERANCE WITH ACTIVE SYMPTOM
def test_adv_08_off_topic_utterance_state():
    mgr = PatientStateManager("adv_08", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_08",
        new_input="I love drinking green tea in the morning.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True)}
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.selected_question.question_id == "q_abdo_duration"


# 9. NULL SYMPTOM ATTRIBUTES
def test_adv_09_null_symptom_attributes():
    state = PatientState(conversation_id="adv_09")
    state.symptoms["fever"] = SymptomDetail(present=True, duration=None, severity=None, location=None)
    res = QuestionSelector().select_next_question(state)
    assert res.selected_question is not None
    assert res.selected_question.question_id == "q_fever_duration"


# 10. NONE LANGUAGE FIELD
def test_adv_10_none_language_field():
    state = PatientState(conversation_id="adv_10", language=None)
    state.symptoms["abdominal_pain"] = SymptomDetail(present=True)
    res = QuestionSelector().select_next_question(state)
    assert res.selected_question is not None
    assert res.wording == res.selected_question.wording_mr  # Defaults to Marathi 'mr'


# 11. MULTIPLE PRIORITY 1 EMERGENCY QUESTIONS (CHEST PAIN & BREATHLESSNESS)
def test_adv_11_multiple_priority_1_questions():
    mgr = PatientStateManager("adv_11", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_11",
        new_input="Chest pain and severe shortness of breath.",
        new_symptoms={
            "chest_pain": SymptomDetail(present=True, severity="severe"),
            "breathlessness": SymptomDetail(present=True, severity="severe")
        }
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.selected_question.priority == 1
    assert res.selected_question.question_id in ["q_chest_pain_radiate", "q_breathless_severity"]


# 12. FEVER AND VOMITING OVERLAP (PRIORITY 1 EMERGENCY VS PRIORITY 2 ROUTINE)
def test_adv_12_fever_and_vomiting_overlap():
    mgr = PatientStateManager("adv_12", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_12",
        new_input="Fever and vomiting.",
        new_symptoms={
            "fever": SymptomDetail(present=True),
            "vomiting": SymptomDetail(present=True)
        }
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.selected_question.question_id == "q_vomit_blood"
    assert res.selected_question.priority == 1  # Emergency GI bleeding screening wins over fever duration


# 13. DUPLICATE AND NULL ANSWERS IN HISTORY
def test_adv_13_duplicate_answers_in_history():
    state = PatientState(conversation_id="adv_13")
    state.symptoms["abdominal_pain"] = SymptomDetail(present=True)
    state.answers = {"abdominal_pain_duration": None, "vomiting_status": False}
    res = QuestionSelector().select_next_question(state)
    # Null answer should not count as answered duration
    assert res.selected_question is not None


# 14. ROMAN MARATHI LANGUAGE LOCALIZATION
def test_adv_14_roman_mr_language_localization():
    mgr = PatientStateManager("adv_14", language="roman-mr")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_14",
        new_input="Pot dukhtay.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True)}
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.wording == "Kadhipasun pot dukhat ahe?"


# 15. HINGLISH LANGUAGE LOCALIZATION
def test_adv_15_hinglish_language_localization():
    mgr = PatientStateManager("adv_15", language="hinglish")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_15",
        new_input="Stomach pain ho raha hai.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True)}
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is not None
    assert res.wording == "Kab se stomach pain ho raha hai?"


# 16. ISOLATED CUSTOM QUESTION BANK
def test_adv_16_question_bank_isolation():
    custom_q = ApprovedQuestion(
        question_id="q_custom_01",
        topic="custom_sym",
        purpose="Custom purpose",
        wording_mr="कस्टम प्रश्न?",
        wording_hi="कस्टम प्रश्न?",
        wording_en="Custom question?",
        wording_roman_mr="Custom prashna?",
        wording_hinglish="Custom question?",
        information_collected="custom_info",
        priority=1,
        emergency_relevance=True,
        required_before_triage=True
    )
    selector = QuestionSelector(question_bank=[custom_q])
    state = PatientState(conversation_id="adv_16")
    state.symptoms["custom_sym"] = SymptomDetail(present=True)
    res = selector.select_next_question(state)
    assert res.selected_question.question_id == "q_custom_01"


# 17. NO MISSING INFO READY FOR TRIAGE
def test_adv_17_missing_info_recalculation():
    state = PatientState(conversation_id="adv_17")
    state.missing_information = []
    res = QuestionSelector().select_next_question(state)
    assert res.is_ready_for_triage is True
    assert res.selected_question is None


# 18. PARTIAL VITALS NO SYMPTOMS
def test_adv_18_partial_vitals_no_symptoms():
    state = PatientState(conversation_id="adv_18")
    state.vitals = Vitals(bp_systolic=80, pulse_rate=130)
    res = QuestionSelector().select_next_question(state)
    assert res.is_ready_for_triage is True
    assert res.selected_question is None


# 19. NONSENSICAL SYMPTOM KEY
def test_adv_19_nonsensical_symptom_key():
    state = PatientState(conversation_id="adv_19")
    state.symptoms["alien_headache"] = SymptomDetail(present=True)
    res = QuestionSelector().select_next_question(state)
    # Alien symptom has no question bank match, should complete triage readiness safely
    assert res.is_ready_for_triage is True
    assert res.selected_question is None


# 20. ALREADY ASKED EMERGENCY QUESTION
def test_adv_20_already_asked_emergency_question():
    mgr = PatientStateManager("adv_20", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="adv_20",
        new_input="Chest pain radiating to left arm.",
        new_symptoms={"chest_pain": SymptomDetail(present=True, severity="severe")},
        new_answers={"chest_pain_radiation": True}
    ))
    res = QuestionSelector().select_next_question(mgr.get_state())
    assert res.selected_question is None or res.selected_question.question_id != "q_chest_pain_radiate"
