# NHAMCS Triage Feature Schema

This document details the feature engineering pipeline mapping the raw NHAMCS ED dataset into the clean `nhamcs_triage_features.csv` used for the Machine Learning Triage Fallback Model.

## Demographics
| Feature Name | Source Column | Transformation | Reason |
|---|---|---|---|
| `age` | `AGE` | Replace negative codes (e.g. -9) with NaN. | Age is a critical determinant in many triage and safety guidelines (e.g., pediatric fevers vs adult fevers). |
| `gender` | `SEX` | Map 1 -> 'Female', 2 -> 'Male', -9/-8 -> 'Unknown'. | Useful for demographic risk baseline. |

## Vitals
| Feature Name | Source Column | Transformation | Reason |
|---|---|---|---|
| `temperature` | `TEMPF` | Extract float. Replace negatives with NaN. | Essential for detecting fever, infection, or sepsis risks. |
| `heart_rate` | `PULSE` | Extract float. Replace negatives with NaN. | Tachycardia / Bradycardia markers for shock or cardiac events. |
| `respiratory_rate`| `RESPR` | Extract float. Replace negatives with NaN. | High RR is a strong predictor of respiratory distress and acuity. |
| `systolic_bp` | `BPSYS` | Extract float. Replace negatives with NaN. | Hypertension crisis or hypotensive shock. |
| `diastolic_bp` | `BPDIAS` | Extract float. Replace negatives with NaN. | Cardiovascular health and shock detection. |
| `spo2` | `POX` | Extract float. Replace negatives with NaN. | Direct indicator of hypoxemia. |
| `pain_score` | `PAINSCALE` | Extract float (0-10). Handle blanks as NaN. | Pain severity heavily influences Priority vs Urgent routing. |

## Presentation / Text Representation
| Feature Name | Source Column | Transformation | Reason |
|---|---|---|---|
| `chief_complaint_text` | `RFV1` - `RFV5` | Mapped categorical Reason for Visit (RFV) codes using the official NHAMCS Stata `value_labels` dictionary. Converted to a continuous natural language string: "Patient presenting with {symptom_1}, {symptom_2}". | The target model needs to comprehend natural language symptomatic inputs that match MahaArogya's production `PatientState` representations. No LLMs were used; this is a strict 1:1 lookup translation. |

## Target (Labels)
| Feature Name | Source Column | Transformation | Reason |
|---|---|---|---|
| `triage_level` | `IMMEDR` | Filtered rows outside the 1-5 range. Mapped integers to MahaArogya schema: 1 -> EMERGENCY, 2 -> URGENT, 3 -> PRIORITY, 4/5 -> ROUTINE. | Aligns the NHAMCS ESI-style scale to the exact 4-tier output expected by the `TriageClassifier`. |
| `triage_level_idx` | `IMMEDR` | Mapped to (0, 1, 2, 3) | Integer encoding for XGBoost/LightGBM training. |
