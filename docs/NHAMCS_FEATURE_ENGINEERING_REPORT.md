# NHAMCS Feature Engineering Report

## 1. Dataset Dimensions
- **Rows before processing:** 16207
- **Rows after processing:** 10495
- **Removed Rows:** 5712
- **Reason for removal:** Missing or invalid triage severity label (`IMMEDR` < 1 or > 5).

## 2. Duplicate Analysis
- **Exact duplicate rows:** 3 (Note: NHAMCS is cross-sectional; exact duplicates across demographic/vitals likely represent low-variance data entry collisions rather than actual same-patient leakage, but they should be monitored).

## 3. Class Distribution
- **EMERGENCY (Level 1):** 229
- **URGENT (Level 2):** 1651
- **PRIORITY (Level 3):** 5429
- **ROUTINE (Level 4 & 5):** 3186

## 4. Missing Values
{
  "age": 0,
  "gender": 0,
  "temperature": 383,
  "heart_rate": 203,
  "respiratory_rate": 243,
  "systolic_bp": 721,
  "diastolic_bp": 725,
  "spo2": 10495,
  "pain_score": 2771,
  "chief_complaint_text": 0,
  "triage_level": 0,
  "triage_level_idx": 0
}

## 5. Splits
- **Train:** 7346 rows
- **Validation:** 1574 rows
- **Test:** 1575 rows

*Random Seed: 42. Stratified by triage level.*
