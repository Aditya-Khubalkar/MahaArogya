"""
MahaArogya — Versioned Safety Rule Engine
Independent, deterministic clinical red-flag rules.
Consumes PatientState and forces emergency escalation when high-risk signals exist.
Generative models CANNOT override this safety layer.
"""

from ai.patient_state.schemas import PatientState
from ai.triage.schemas import SafetyRuleResult


class SafetyRuleEngine:
    """Evaluates PatientState against explicit clinical safety rules."""

    def evaluate(self, state: PatientState) -> SafetyRuleResult:
        """
        Evaluates PatientState against deterministic red-flag rules.
        
        Args:
            state: Current PatientState memory instance

        Returns:
            SafetyRuleResult containing triggered rules, risk signals, and escalation level.
        """
        triggered_rules = []
        risk_signals = []
        is_emergency = False
        escalation_level = "NONE"

        symptoms = state.symptoms
        answers = state.answers
        vitals = state.vitals
        age = state.age_years

        # --- 1. CARDIAC RED FLAG ---
        if "chest_pain" in symptoms:
            detail = symptoms["chest_pain"]
            postprandial = answers.get("postprandial", False)
            positional = answers.get("positional", False)
            radiating = answers.get("chest_pain_radiation", False) or "radiat" in str(state.original_input_history).lower()
            diaphoresis = answers.get("diaphoresis", False)
            
            # Cardiac red flags: radiation, diaphoresis, dyspnea, or severe crushing pressure
            if radiating or diaphoresis or "breathlessness" in symptoms or detail.severity == "severe":
                triggered_rules.append("RULE_CARDIAC_01")
                risk_signals.append("Acute chest pain with cardiac radiation / diaphoresis / dyspnea red flag")
                is_emergency = True

        # --- 2. RESPIRATORY DISTRESS ---
        if "breathlessness" in symptoms:
            b_detail = symptoms["breathlessness"]
            exertional_resolved = answers.get("exertional_resolved", False)
            if not exertional_resolved:
                if b_detail.severity == "severe" or answers.get("breathless_severity") == True:
                    triggered_rules.append("RULE_RESP_01")
                    risk_signals.append("Severe acute respiratory distress")
                    is_emergency = True

        # --- 3. GI HEMORRHAGE / HEMOPTYSIS ---
        if "hematemesis" in symptoms or answers.get("vomit_blood") or "hematemesis" in state.risk_signals:
            triggered_rules.append("RULE_HEMORRHAGE_01")
            risk_signals.append("Hematemesis / active GI bleeding detected")
            is_emergency = True

        # --- 4. STROKE SIGNALS (FAST Criteria) ---
        has_slurred = answers.get("slurred_speech", False) or answers.get("dysarthria", False)
        has_facial_droop = answers.get("facial_droop", False)
        has_arm_weakness = answers.get("arm_weakness", False)
        has_stroke_numbness = "stroke_numbness" in symptoms or answers.get("unilateral_numbness", False)
        
        if has_slurred or has_facial_droop or has_arm_weakness or has_stroke_numbness:
            triggered_rules.append("RULE_STROKE_FAST")
            risk_signals.append("Acute neurological focal deficit / FAST stroke criteria met")
            is_emergency = True

        # --- 5. PREGNANCY + ABDOMINAL PAIN / BLEEDING ---
        if answers.get("pregnant", False):
            if "abdominal_pain" in symptoms or answers.get("first_trimester_bleeding") or answers.get("cramping"):
                triggered_rules.append("RULE_PREGNANCY_ABDO")
                risk_signals.append("Pregnancy with abdominal pain / bleeding (Ectopic / Miscarriage risk)")
                is_emergency = True

        # --- 6. ATYPICAL / SILENT MI PRESENTATION ---
        has_nausea = "nausea" in symptoms or "indigestion" in symptoms
        has_diaphoresis = answers.get("diaphoresis", False)
        is_high_risk_patient = answers.get("diabetic", False) or (age is not None and age > 50)
        
        if has_nausea and has_diaphoresis and is_high_risk_patient:
            triggered_rules.append("RULE_SILENT_MI")
            risk_signals.append("Atypical silent MI presentation in high-risk patient")
            is_emergency = True

        # --- 7. PEDIATRIC FEVER THRESHOLDS ---
        if age is not None:
            if age < 0.25 and ("fever" in symptoms or (vitals.temperature_f and vitals.temperature_f >= 100.4)):
                triggered_rules.append("RULE_NEONATAL_FEVER")
                risk_signals.append("Neonatal fever (age < 3 months) sepsis risk")
                is_emergency = True
            elif age <= 2.0 and vitals.temperature_f and vitals.temperature_f >= 104.0:
                triggered_rules.append("RULE_PEDIATRIC_HIGH_FEVER")
                risk_signals.append("Pediatric hyperpyrexia >= 104F")
                is_emergency = True

        # --- 8. VITAL SIGN EMERGENCY OVERRIDES ---
        if vitals.bp_systolic is not None and vitals.bp_systolic < 90:
            triggered_rules.append("RULE_SHOCK_BP")
            risk_signals.append("Severe hypotension (SBP < 90 mmHg) / shock state")
            is_emergency = True
            
        if vitals.pulse_rate is not None and vitals.pulse_rate > 120:
            triggered_rules.append("RULE_TACHYCARDIAC_HR")
            risk_signals.append("Sustained severe tachycardia (HR > 120 bpm)")
            is_emergency = True

        if vitals.spo2_percent is not None and vitals.spo2_percent < 92.0:
            triggered_rules.append("RULE_HYPOXIA_SPO2")
            risk_signals.append("Severe hypoxemia (SpO2 < 92%)")
            is_emergency = True

        # --- 9. MENINGITIS TRIAD ---
        if "headache" in symptoms:
            meningeal_count = sum([
                1 if answers.get("neck_stiffness", False) else 0,
                1 if answers.get("photophobia", False) else 0,
                1 if ("fever" in symptoms or (vitals.temperature_f is not None and vitals.temperature_f > 100.0)) else 0
            ])
            if meningeal_count >= 2:
                triggered_rules.append("RULE_MENINGITIS_TRIAD")
                risk_signals.append("Meningeal irritation triad (headache + nuchal rigidity / photophobia / fever)")
                is_emergency = True

        # --- 10. THUNDERCLAP HEADACHE ---
        if "headache" in symptoms and answers.get("thunderclap", False):
            triggered_rules.append("RULE_THUNDERCLAP_HEADACHE")
            risk_signals.append("Thunderclap onset headache (Subarachnoid Hemorrhage risk)")
            is_emergency = True

        # --- 11. OTHER CLINICAL RED FLAGS ---
        if answers.get("anaphylaxis", False) or "anaphylaxis_allergy" in symptoms:
            triggered_rules.append("RULE_ANAPHYLAXIS")
            risk_signals.append("Severe acute anaphylactic reaction / airway edema risk")
            is_emergency = True

        if answers.get("dka", False) or (answers.get("diabetic", False) and (answers.get("fruity_breath", False) or answers.get("kussmaul", False))):
            triggered_rules.append("RULE_DKA")
            risk_signals.append("Diabetic Ketoacidosis (DKA) / metabolic crisis risk")
            is_emergency = True

        if answers.get("testicular_torsion", False) or answers.get("testicular_pain", False):
            triggered_rules.append("RULE_TESTICULAR_TORSION")
            risk_signals.append("Acute testicular torsion risk (surgical emergency)")
            is_emergency = True

        if answers.get("compartment_syndrome", False) or answers.get("limb_ischemia", False):
            triggered_rules.append("RULE_COMPARTMENT_SYNDROME")
            risk_signals.append("Acute limb compartment syndrome / ischemia risk")
            is_emergency = True

        if answers.get("suicidal_ideation", False) or answers.get("self_harm", False):
            triggered_rules.append("RULE_SUICIDAL_IDEATION")
            risk_signals.append("Acute suicidal ideation / psychiatric crisis with intent")
            is_emergency = True

        emergency_standalone = [
            ("pediatric_high_fever", "RULE_PEDIATRIC_01", "Pediatric high fever red flag"),
            ("trauma_bleeding", "RULE_TRAUMA_01", "Severe active bleeding / acute trauma"),
            ("unconscious", "RULE_NEURO_01", "Loss of consciousness / unresponsiveness"),
            ("seizure", "RULE_NEURO_02", "Active seizure / postictal state"),
            ("cyanosis_spo2", "RULE_RESP_02", "Severe hypoxemia / cyanosis"),
        ]
        for key, rule_id, desc in emergency_standalone:
            if key in symptoms:
                triggered_rules.append(rule_id)
                risk_signals.append(desc)
                is_emergency = True

        # --- 12. URGENT CLINICAL SIGNALS (Non-Emergency Escalate to Urgent) ---
        if answers.get("petechial_rash", False) and "fever" in symptoms:
            triggered_rules.append("RULE_PETECHIAL_FEVER")
            risk_signals.append("Fever with petechial rash (Dengue / Meningococcemia risk)")

        if answers.get("recent_long_flight", False) and ("leg_pain" in symptoms or "unilateral_swelling" in answers):
            triggered_rules.append("RULE_DVT_RISK")
            risk_signals.append("Deep Vein Thrombosis (DVT) risk after long flight")

        if "abdominal_pain" in symptoms and "vomiting" in symptoms:
            abdo = symptoms["abdominal_pain"]
            vomit = symptoms["vomiting"]
            if abdo.severity == "severe" or (vomit.frequency and "2" in str(vomit.frequency)):
                triggered_rules.append("RULE_SEVERE_ABDO_01")
                risk_signals.append("Severe abdominal pain with persistent vomiting")

        if is_emergency:
            escalation_level = "EMERGENCY_AMBULANCE"
            explanation = f"CRITICAL SAFETY RED FLAG TRIGGERED: {'; '.join(risk_signals)}. Immediate emergency medical assessment required."
        elif triggered_rules:
            escalation_level = "URGENT_EVALUATION"
            explanation = f"URGENT CLINICAL SIGNALS DETECTED: {'; '.join(risk_signals)}. Prompt medical evaluation recommended."
        else:
            escalation_level = "OPD_ROUTINE"
            explanation = "No acute red-flag safety rules triggered."

        return SafetyRuleResult(
            is_emergency=is_emergency,
            triggered_rule_ids=triggered_rules,
            risk_signals=risk_signals,
            escalation_level=escalation_level,
            explanation=explanation
        )
