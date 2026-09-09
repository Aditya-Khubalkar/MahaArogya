# NHAMCS 2021 Triage Data Audit & Pipeline Design

## 1. Dataset Audit Statistics
- **Total Visits:** 16,207
- **Unique Visit Records:** 16,207
- **Duplicate Records:** 0
- **Available Vitals:** 
  - `PULSE` (Heart Rate)
  - `TEMPF` (Temperature in F)
  - `RESPR` (Respiratory Rate)
  - `BPSYS` (Systolic BP)
  - `BPDIAS` (Diastolic BP)
  - `PAINSCALE` (Pain 0-10)
  - `SPO2` (Oxygen Saturation)
- **Available Complaint Fields:** `RFV1`, `RFV2`, `RFV3`, `RFV4`, `RFV5` (Reason for Visit codes)
- **Severity-related Fields:** `IMMEDR` (Immediacy rating 1-5, matching ESI logic).
- **Missing Values:**
  - `PULSE`: 869 missing
  - `TEMPF`: 1,045 missing
  - `RESPR`: 881 missing
  - `BPSYS`: 1,577 missing
  - `BPDIAS`: 1,589 missing
  - `PAINSCALE`: 6,747 missing
  - `IMMEDR` (Triage): 5,712 missing/unknown (coded as -8, -9, 0, 7)
- **Class Balance (IMMEDR 1-5):**
  - Level 1 (Emergency): 229 (2.1%)
  - Level 2 (Urgent): 1,651 (15.7%)
  - Level 3 (Priority): 5,429 (51.7%)
  - Level 4 (Routine): 2,767 (26.3%)
  - Level 5 (Routine): 419 (4.0%)

---

## 2. Feature Conversion Pipeline

| Feature Name | Source Column | Transformation | Reason |
|---|---|---|---|
| **Age** | `AGE` | Keep as continuous float. Replace negative values with NaN. | Vital triage metric, esp for pediatric/geriatric rules. |
| **Heart Rate** | `PULSE` | Float. Replace negative values with NaN. | Cardiac triage and shock detection. |
| **Systolic BP** | `BPSYS` | Float. Replace negative values with NaN. | Hypotension / Hypertensive crisis detection. |
| **Diastolic BP** | `BPDIAS` | Float. Replace negative values with NaN. | Shock / Hypertension detection. |
| **Resp Rate** | `RESPR` | Float. Replace negative values with NaN. | Respiratory distress marker. |
| **Temperature** | `TEMPF` | Float. Convert to F. Replace negative values. | Fever, sepsis, infection risk. |
| **O2 Sat** | `SPO2` | Float. Replace negative values with NaN. | Hypoxia / Respiratory failure marker. |
| **Pain Score** | `PAINSCALE` | Float. Handle -8/-9 as NaN. | Important for urgent vs priority routing. |
| **Chief Complaint** | `RFV1` - `RFV5` | Look up categorical `RFV` codes using the NHAMCS dictionary to reconstruct synthetic natural language strings (e.g., "Patient reports {symptom_text}."). | NHAMCS stores complaints as codes. We need conversational strings to match the MahaArogya `PatientState`. |
| **Target Label** | `IMMEDR` | Filter out < 1 and > 5. Map 1=EMERGENCY, 2=URGENT, 3=PRIORITY, 4/5=ROUTINE. | Maps directly to the 4-tier MahaArogya triage schema. |

---

## 3. Model & Evaluation Strategy (XGBoost/LightGBM)

**Model Selection:**
Do NOT use neural networks initially. We will use **XGBoost** or **LightGBM** because:
1. They naturally handle the missing tabular data (NaNs) extremely well without aggressive imputation.
2. They are highly resistant to overfitting on imbalanced tabular data.
3. They provide robust feature importance (explainability), which is critical for clinical triage.

**Evaluation Framework:**
- Filter dataset to the ~10,495 rows with valid `IMMEDR` labels.
- Apply a strict 80/20 train/test split. (NHAMCS rows are independent visits, so random split is safe).
- **Target Metrics:**
  - Class-wise Recall (Crucial metric: ensuring Urgent cases are not misclassified as Routine).
  - Accuracy, Precision, F1-score.
  - Confusion Matrix to visualize misclassification severity.
  
**Safety Reminder:**
This ML model will exclusively route the non-emergency "gray area" (Urgent vs Priority vs Routine). All Emergency (Level 1) red flags will continue to be rigidly intercepted by the `SafetyRuleEngine` prior to ML inference.
