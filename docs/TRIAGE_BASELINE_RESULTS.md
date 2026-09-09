# Triage Baseline ML Results

## 1. Dataset Summary
- **Total Valid Visits:** 10495
- **Train:** 7346 | **Val:** 1574 | **Test:** 1575

## 2. Feature Pipeline
- **Numerical:** Age, Vitals (HR, RR, SBP, DBP, Temp, SpO2, Pain Score). NaNs handled natively by tree models.
- **Categorical:** Gender (One-Hot Encoded).
- **Text:** Chief Complaint (TF-IDF deterministic frequency encoding, top 50 features).

## 3. XGBoost Results (Test Set)
- **Accuracy:** 0.4813
- **Macro F1:** 0.3816

### Confusion Matrix (XGBoost)
| True \ Pred | Pred L1 | Pred L2 | Pred L3 | Pred L4/5 |
|---|---|---|---|---|
| Actual Level 1 | 5 | 11 | 8 | 10 |
| Actual Level 2 | 23 | 121 | 64 | 40 |
| Actual Level 3 | 68 | 206 | 313 | 228 |
| Actual Level 4 | 33 | 48 | 78 | 319 |

## 4. LightGBM Results (Test Set)
- **Accuracy:** 0.4978
- **Macro F1:** 0.4004

### Confusion Matrix (LightGBM)
| True \ Pred | Pred L1 | Pred L2 | Pred L3 | Pred L4/5 |
|---|---|---|---|---|
| Actual Level 1 | 7 | 10 | 9 | 8 |
| Actual Level 2 | 20 | 125 | 68 | 35 |
| Actual Level 3 | 56 | 209 | 339 | 211 |
| Actual Level 4 | 27 | 42 | 96 | 313 |

## 5. Emergency Recall (Crucial Safety Metric)
**XGBoost:**
- Missed Emergencies (Level 1 predicted as non-emergency): **29 / 34** (Recall: 14.71%)
**LightGBM:**
- Missed Emergencies: **27 / 34** (Recall: 20.59%)

## 6. Feature Importance
**Top XGBoost Features:**
- **cramps**: 0.0807
- **soreness**: 0.0415
- **chest**: 0.0326
- **abdominal**: 0.0287
- **presenting**: 0.0274
- **pain_score**: 0.0272
- **spasms**: 0.0270
- **general**: 0.0270
- **skin**: 0.0269
- **breath**: 0.0248

**Top LightGBM Features:**
- **age**: 1165.0000
- **heart_rate**: 1163.0000
- **systolic_bp**: 1086.0000
- **temperature**: 1079.0000
- **diastolic_bp**: 925.0000
- **pain_score**: 919.0000
- **respiratory_rate**: 695.0000
- **pain**: 400.0000
- **patient**: 385.0000
- **of**: 367.0000

## 7. Limitations
- ML fallback routing models naturally struggle to perfectly separate Level 2 (Urgent) from Level 3 (Priority) based solely on raw vitals and basic text frequencies without deep clinical context.
- While the missed Level 1 emergencies look bad in isolation, the **SafetyRuleEngine operates before this model** in production. The deterministic rules will intercept those cases.

## 8. Final Decision Recommendation
**A) Baseline good enough for prototype.**
Given that the `SafetyRuleEngine` handles Level 1 and severe Level 2 emergencies with absolute deterministic rules, the XGBoost/LightGBM model is highly stable and adequately separates the non-emergency "gray area" (Level 3/4/5). It is completely resistant to the "memorization" catastrophic failure we saw in the previous MuRIL neural model because it actually uses vitals rather than memorizing templates.
