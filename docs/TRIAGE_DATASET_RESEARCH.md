# Triage Dataset Research Report

## Objective
Identify and evaluate free, open-source datasets suitable for training an Emergency Department (ED) triage routing model. The dataset must contain real patient diversity, chief complaints/symptoms, vital signs, and triage severity labels.

---

## 1. MIMIC-IV-ED (PhysioNet)
- **Source URL:** [PhysioNet MIMIC-IV-ED](https://physionet.org/content/mimic-iv-ed/)
- **License:** Restricted Health Data (Requires CITI training and Data Use Agreement)
- **Language:** English
- **Number of Cases:** ~425,000 ED stays
- **Number of Unique Patients:** Hundreds of thousands (highly diverse)
- **Features Available:** Chief complaints (free-text), vital signs (HR, SBP, DBP, RR, Temp, SpO2), pain scores, demographics.
- **Labels Available:** ESI (Emergency Severity Index) triage score (1-5), Hospital Admission outcome.
- **Real vs Synthetic:** 100% Real Clinical Data
- **Known Limitations:** The primary limitation is licensing/access. It is not "frictionless" open-source; researchers must be formally credentialed. It is also US-demographic centric.
- **Train/Test Split:** Standard splits are widely published in literature.
- **Suitability for MahaArogya:** **HIGH**. This is the gold standard dataset. If credentialing can be obtained, this is the most robust dataset for training a triage model.

---

## 2. Emergency Service - Triage Application (Kaggle)
- **Source URL:** [Kaggle - Emergency Service Triage](https://www.kaggle.com/datasets/kageyama/emergency-service-triage-application)
- **License:** Open (CC0: Public Domain)
- **Language:** English
- **Number of Cases:** 1,267 records
- **Number of Unique Patients:** 1,267
- **Features Available:** Age, sex, arrival mode, chief complaint, vital signs (SBP, DBP, HR, RR, BT), pain score.
- **Labels Available:** KTAS (Korean Triage and Acuity Scale) / Acuity scores.
- **Real vs Synthetic:** Real Clinical Data (Cross-sectional retrospective study from two EDs)
- **Known Limitations:** **Very small size**. 1,267 rows is generally insufficient to train a generalized multimodal neural network from scratch without severe overfitting.
- **Train/Test Split:** N/A (single CSV, must manually split).
- **Suitability for MahaArogya:** **LOW-MODERATE**. Good for testing and validation, but too small for primary model training.

---

## 3. NHAMCS (National Hospital Ambulatory Medical Care Survey)
- **Source URL:** [CDC NHAMCS](https://www.cdc.gov/nchs/ahcd/index.htm)
- **License:** Public Domain (US Government)
- **Language:** English
- **Number of Cases:** ~20,000 - 30,000 ED visits per annual release (multi-year datasets reach >500k).
- **Number of Unique Patients:** Highly diverse, nationally representative sample.
- **Features Available:** Vital signs, demographics, Reason for Visit (RFV).
- **Labels Available:** Immediacy with which patient should be seen (1-5 triage scale), hospitalization outcome.
- **Real vs Synthetic:** Real Clinical Data
- **Known Limitations:** The "Reason for Visit" (symptoms) are provided as structured categorical codes (RFV codes) rather than raw natural language text. A mapping dictionary is required to convert codes back into text strings for NLP training.
- **Train/Test Split:** Standard cross-validation applied by researchers.
- **Suitability for MahaArogya:** **MODERATE-HIGH**. Excellent scale and diversity, but requires heavy preprocessing to convert tabular RFV codes into natural language strings compatible with the MahaArogya `PatientState` input.

---

## 4. FedMML-ED-Triage (Hugging Face)
- **Source URL:** [Hugging Face - fedmml-ed-triage](https://huggingface.co/datasets/olaflaitinen/fedmml-ed-triage)
- **License:** Open
- **Number of Cases:** 87,234
- **Number of Unique Patients:** 96
- **Real vs Synthetic:** Highly Synthetic / Duplicated
- **Suitability for MahaArogya:** **REJECTED** (Previous audit proved catastrophic leakage and lack of diversity).

---

## Summary & Recommendation
To successfully train Option C (a lightweight ML fallback routing model), we need a dataset with both scale and raw text complaints.

1. **First Choice:** Acquire **MIMIC-IV-ED**. It has the exact feature schema required (raw text complaints + vitals -> ESI score) and massive scale.
2. **Alternative:** If MIMIC-IV-ED access is blocked due to credentialing, we can use **NHAMCS**, but we must build a translation pipeline to convert its categorical symptom codes into conversational text strings.
3. **Validation:** We can use the Kaggle 1.2k dataset as an independent out-of-distribution test set.
