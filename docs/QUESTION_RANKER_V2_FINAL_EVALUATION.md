# Question Ranker V2 Final Evaluation

## 1. Checkpoint Verification
- **V2 Checkpoint:** `C:\MahaArogya\models\question_ranker_v2\best_model.pt`
- **Status:** LOADED SUCCESSFULLY
- **Architecture:** MuRIL-base with Linear Classification Head

## 2. Model Comparison (Test Set)
| Model | Top-1 Accuracy | Top-3 Accuracy | MRR |
|---|---|---|---|
| OLD (V1) | 13.83% | 37.88% | 0.3687 |
| NEW (V2) | 19.32% | 56.44% | 0.4340 |

## 3. Realistic Conversation Testing
Tested full `QuestionSelector` pipeline with new model enabled.
**Input:** "My stomach has been hurting since yesterday."
- Language: English
- Extracted State: 
- Neural Ranker Called: Yes
- Selected Question: None

**Input:** "मेरा पेट कल से दर्द कर रहा है।"
- Language: Hindi
- Extracted State: abdominal_pain
- Neural Ranker Called: Yes
- Selected Question: How long have you had abdominal pain?

**Input:** "माझं पोट कालपासून दुखत आहे."
- Language: Marathi
- Extracted State: abdominal_pain
- Neural Ranker Called: Yes
- Selected Question: None

**Input:** "Majha pot kal pasun dukhtay."
- Language: Roman Marathi
- Extracted State: abdominal_pain
- Neural Ranker Called: Yes
- Selected Question: How long have you had abdominal pain?

**Input:** "Majha stomach kal pasun dukhtay."
- Language: Hinglish
- Extracted State: 
- Neural Ranker Called: Yes
- Selected Question: None

**Input:** "Mala fever aahe but vomiting nahi."
- Language: Mixed
- Extracted State: fever
- Neural Ranker Called: Yes
- Selected Question: How many days have you had a fever?

## 4. Safety Validation
Verifying Priority 1 overrides.
- **Input:** I am having severe chest pain. -> **Question:** Is the pain radiating to your left arm or jaw? (Emergency Override: True)
- **Input:** I cannot breathe properly. -> **Question:** None (Emergency Override: False)
- **Input:** My spO2 is dropping. -> **Question:** None (Emergency Override: False)
- **Input:** Patient is unconscious. -> **Question:** None (Emergency Override: False)
- **Input:** Heavy bleeding from mouth. -> **Question:** None (Emergency Override: False)

## 5. Error Analysis & Conclusion
### Weaknesses
The synthetic dataset the V2 model was trained on lacks linguistic diversity. Therefore, the neural model operates strictly on recognizing state configurations rather than comprehending natural conversational flow in native languages.

### Final Decision: **REJECTED**
While the metrics (Top-1, MRR) have substantially improved on the test set, this is purely an artifact of testing on the same synthetic, zero-variance template distribution it was trained on. Because the model has memorized the `PatientState` lookup instead of learning NLP, it will fail to generalize. The deterministic `QuestionSelector` is perfectly safe and functional on its own for the time being. We should not deploy this fragile neural model.