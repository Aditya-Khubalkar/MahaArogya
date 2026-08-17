"""
Unit tests for Triage Classifier and Safety Rule Engine.
Evaluates emergency recall, red-flag safety overrides, and regression coverage for all 10 safety rules.
"""

import pytest
from ai.patient_state.schemas import PatientStateDelta, SymptomDetail, Vitals
from ai.patient_state.state_manager import PatientStateManager
from ai.triage.classifier import TriageClassifier
from ai.triage.safety_rules import SafetyRuleEngine


# --- EXISTING CORE TESTS ---

def test_chest_pain_emergency_override():
    mgr = PatientStateManager("conv_tr1", language="mr")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_tr1",
        new_input="Majhya chhatit khup severe pain ahe ani dava hat dukhatahe.",
        new_symptoms={"chest_pain": SymptomDetail(present=True, severity="severe")},
        new_answers={"chest_pain_radiation": True}
    ))
    
    classifier = TriageClassifier()
    decision = classifier.classify(mgr.get_state())
    
    assert decision.triage_category == "EMERGENCY"
    assert decision.triage_confidence == 1.0
    assert "RULE_CARDIAC_01" in decision.triggered_rule_ids
    assert decision.escalation_level == "EMERGENCY_AMBULANCE"
    assert "🚨" in decision.safe_response_text


def test_hematemesis_emergency_override():
    mgr = PatientStateManager("conv_tr2", language="hi")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_tr2",
        new_input="Khoon ki ulti hui hai.",
        new_symptoms={"vomiting": SymptomDetail(present=True)},
        new_answers={"vomit_blood": True}
    ))
    
    classifier = TriageClassifier()
    decision = classifier.classify(mgr.get_state())
    
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_HEMORRHAGE_01" in decision.triggered_rule_ids


def test_severe_abdominal_pain_urgent():
    mgr = PatientStateManager("conv_tr3", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_tr3",
        new_input="Severe abdominal pain and vomited twice.",
        new_symptoms={
            "abdominal_pain": SymptomDetail(present=True, severity="severe"),
            "vomiting": SymptomDetail(present=True, frequency="2 times")
        }
    ))
    
    classifier = TriageClassifier()
    decision = classifier.classify(mgr.get_state())
    
    assert decision.triage_category in ["URGENT", "EMERGENCY"]
    assert "RULE_SEVERE_ABDO_01" in decision.triggered_rule_ids


def test_routine_triage_classification():
    mgr = PatientStateManager("conv_tr4", language="mr")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_tr4",
        new_input="Majha pot 2 divas pasun thoda dukhtay.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, duration="2 days", severity="mild")},
        new_negations=["fever", "vomiting", "chest_pain"]
    ))
    
    classifier = TriageClassifier()
    decision = classifier.classify(mgr.get_state())
    
    assert decision.triage_category == "ROUTINE"
    assert decision.escalation_level == "OPD_ROUTINE"
    assert "✅" in decision.safe_response_text


# --- NEW PERMANENT REGRESSION TESTS FOR 10 SAFETY RULES ---

# 1. STROKE FAST CRITERIA
def test_stroke_fast_slurred_speech_positive():
    mgr = PatientStateManager("conv_st1", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_st1",
        new_input="Mild headache and slurred speech.",
        new_symptoms={"headache": SymptomDetail(present=True, severity="mild")},
        new_answers={"slurred_speech": True}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_STROKE_FAST" in decision.triggered_rule_ids


def test_stroke_fast_negative():
    mgr = PatientStateManager("conv_st2", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_st2",
        new_input="Mild headache without speech problems.",
        new_symptoms={"headache": SymptomDetail(present=True, severity="mild")},
        new_answers={"slurred_speech": False}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category in ["ROUTINE", "PRIORITY"]
    assert "RULE_STROKE_FAST" not in decision.triggered_rule_ids


# 2. PREGNANCY + ABDOMINAL PAIN
def test_pregnancy_abdominal_pain_positive():
    mgr = PatientStateManager("conv_pr1", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_pr1",
        new_input="Mild abdominal cramps in 8 weeks pregnant patient.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, severity="mild")},
        new_answers={"pregnant": True, "cramping": True}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_PREGNANCY_ABDO" in decision.triggered_rule_ids


def test_pregnancy_no_abdominal_pain_negative():
    mgr = PatientStateManager("conv_pr2", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_pr2",
        new_input="Morning nausea in pregnant patient.",
        new_symptoms={"nausea": SymptomDetail(present=True, severity="mild")},
        new_answers={"pregnant": True}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category in ["ROUTINE", "PRIORITY"]
    assert "RULE_PREGNANCY_ABDO" not in decision.triggered_rule_ids


# 3. SILENT / ATYPICAL MI
def test_atypical_silent_mi_positive():
    mgr = PatientStateManager("conv_mi1", language="en")
    state = mgr.get_state()
    state.age_years = 62
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_mi1",
        new_input="Indigestion, nausea, and cold sweating.",
        new_symptoms={"nausea": SymptomDetail(present=True, severity="mild")},
        new_answers={"diaphoresis": True, "diabetic": True}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_SILENT_MI" in decision.triggered_rule_ids


def test_atypical_silent_mi_negative():
    mgr = PatientStateManager("conv_mi2", language="en")
    state = mgr.get_state()
    state.age_years = 25
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_mi2",
        new_input="Nausea after eating spicy food.",
        new_symptoms={"nausea": SymptomDetail(present=True, severity="mild")},
        new_answers={"diaphoresis": False}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category in ["ROUTINE", "PRIORITY"]
    assert "RULE_SILENT_MI" not in decision.triggered_rule_ids


# 4. NEONATAL FEVER (< 3 MONTHS)
def test_neonatal_fever_positive():
    mgr = PatientStateManager("conv_neo1", language="en")
    state = mgr.get_state()
    state.age_years = 0.16  # 2 months
    state.vitals = Vitals(temperature_f=101.5)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_neo1",
        new_input="High fever in 2-month-old infant.",
        new_symptoms={"fever": SymptomDetail(present=True, severity="severe")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_NEONATAL_FEVER" in decision.triggered_rule_ids


def test_adult_fever_negative():
    mgr = PatientStateManager("conv_neo2", language="en")
    state = mgr.get_state()
    state.age_years = 25.0
    state.vitals = Vitals(temperature_f=101.5)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_neo2",
        new_input="Moderate fever in 25yo adult.",
        new_symptoms={"fever": SymptomDetail(present=True, severity="moderate")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "PRIORITY"
    assert "RULE_NEONATAL_FEVER" not in decision.triggered_rule_ids


# 5. PEDIATRIC HIGH FEVER (HYPERPYREXIA >= 104F)
def test_pediatric_high_fever_positive():
    mgr = PatientStateManager("conv_ped1", language="en")
    state = mgr.get_state()
    state.age_years = 1.5
    state.vitals = Vitals(temperature_f=104.5)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_ped1",
        new_input="Hyperpyrexia in 1.5 year old toddler.",
        new_symptoms={"fever": SymptomDetail(present=True, severity="severe")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_PEDIATRIC_HIGH_FEVER" in decision.triggered_rule_ids


# 6. VITAL SIGN OVERRIDES: HYPOTENSION SHOCK (SBP < 90)
def test_hypotension_shock_bp_positive():
    mgr = PatientStateManager("conv_bp1", language="en")
    state = mgr.get_state()
    state.vitals = Vitals(bp_systolic=85, bp_diastolic=55)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_bp1",
        new_input="Abdominal pain with blood pressure 85/55.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, severity="moderate")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_SHOCK_BP" in decision.triggered_rule_ids


def test_normal_bp_negative():
    mgr = PatientStateManager("conv_bp2", language="en")
    state = mgr.get_state()
    state.vitals = Vitals(bp_systolic=120, bp_diastolic=80)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_bp2",
        new_input="Abdominal pain with blood pressure 120/80.",
        new_symptoms={"abdominal_pain": SymptomDetail(present=True, severity="moderate")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "PRIORITY"
    assert "RULE_SHOCK_BP" not in decision.triggered_rule_ids


# 7. VITAL SIGN OVERRIDES: TACHYCARDIA (HR > 120)
def test_tachycardia_hr_positive():
    mgr = PatientStateManager("conv_hr1", language="en")
    state = mgr.get_state()
    state.vitals = Vitals(pulse_rate=130)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_hr1",
        new_input="Heart rate is 130 bpm.",
        new_symptoms={"palpitations": SymptomDetail(present=True, severity="moderate")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_TACHYCARDIAC_HR" in decision.triggered_rule_ids


# 8. VITAL SIGN OVERRIDES: SEVERE HYPOXIA (SPO2 < 92%)
def test_severe_hypoxia_spo2_positive():
    mgr = PatientStateManager("conv_spo2_1", language="en")
    state = mgr.get_state()
    state.vitals = Vitals(spo2_percent=90.0)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_spo2_1",
        new_input="SpO2 oxygen level is 90%.",
        new_symptoms={"breathlessness": SymptomDetail(present=True, severity="mild")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_HYPOXIA_SPO2" in decision.triggered_rule_ids


def test_normal_spo2_negative():
    mgr = PatientStateManager("conv_spo2_2", language="en")
    state = mgr.get_state()
    state.vitals = Vitals(spo2_percent=98.0)
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_spo2_2",
        new_input="SpO2 oxygen level is 98%.",
        new_symptoms={"cough": SymptomDetail(present=True, severity="mild")}
    ))
    decision = TriageClassifier().classify(state)
    assert decision.triage_category == "ROUTINE"
    assert "RULE_HYPOXIA_SPO2" not in decision.triggered_rule_ids


# 9. MENINGITIS TRIAD
def test_meningitis_triad_positive():
    mgr = PatientStateManager("conv_men1", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_men1",
        new_input="Headache with neck stiffness and photophobia.",
        new_symptoms={
            "headache": SymptomDetail(present=True, severity="moderate"),
            "fever": SymptomDetail(present=True, severity="moderate")
        },
        new_answers={"neck_stiffness": True, "photophobia": True}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_MENINGITIS_TRIAD" in decision.triggered_rule_ids


def test_headache_without_meningeal_signs_negative():
    mgr = PatientStateManager("conv_men2", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_men2",
        new_input="Tension headache without neck pain.",
        new_symptoms={"headache": SymptomDetail(present=True, severity="mild")},
        new_answers={"neck_stiffness": False, "photophobia": False}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category in ["ROUTINE", "PRIORITY"]
    assert "RULE_MENINGITIS_TRIAD" not in decision.triggered_rule_ids


# 10. THUNDERCLAP HEADACHE
def test_thunderclap_headache_positive():
    mgr = PatientStateManager("conv_th1", language="en")
    mgr.update_with_delta(PatientStateDelta(
        conversation_id="conv_th1",
        new_input="Sudden thunderclap headache.",
        new_symptoms={"headache": SymptomDetail(present=True, severity="severe")},
        new_answers={"thunderclap": True}
    ))
    decision = TriageClassifier().classify(mgr.get_state())
    assert decision.triage_category == "EMERGENCY"
    assert "RULE_THUNDERCLAP_HEADACHE" in decision.triggered_rule_ids
