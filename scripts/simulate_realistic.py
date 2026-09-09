import sys
import io
import pathlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.patient_state.schemas import PatientState, SymptomDetail
from ai.questions.selector import QuestionSelector

def run_simulation():
    print("Initializing QuestionSelector (loading ranker model)...")
    selector = QuestionSelector()

    test_cases = [
        {
            "name": "English - Basic Cough (needs duration)",
            "lang": "en",
            "history": ["Patient: I have a bad cough."],
            "symptoms": {"cough": SymptomDetail(present=True, duration=None, severity=None)},
            "negated": [],
            "expected_question_id": "q_cough_duration"
        },
        {
            "name": "Hindi - Fever (needs duration)",
            "lang": "hi",
            "history": ["Patient: Mujhe bukhar hai."],
            "symptoms": {"fever": SymptomDetail(present=True, duration=None, severity=None)},
            "negated": [],
            "expected_question_id": "q_fever_duration"
        },
        {
            "name": "Marathi - Headache (needs duration)",
            "lang": "mr",
            "history": ["Patient: Majhe doke khup dukhat ahe."],
            "symptoms": {"headache": SymptomDetail(present=True, duration=None, severity=None)},
            "negated": [],
            "expected_question_id": "q_headache_duration"
        },
        {
            "name": "Hinglish - Chest pain (needs to check radiation)",
            "lang": "hinglish",
            "history": ["Patient: Chest mein dard ho raha hai."],
            "symptoms": {"chest_pain": SymptomDetail(present=True, duration=None, severity=None)},
            "negated": [],
            "expected_question_id": "q_chest_pain_radiate"
        },
        {
            "name": "English - Multiple symptoms (Cough and Fever)",
            "lang": "en",
            "history": ["Patient: I have a cough and some fever.", "Doctor: How long have you had the cough?", "Patient: For 3 days."],
            "symptoms": {
                "cough": SymptomDetail(present=True, duration="3 days", severity=None),
                "fever": SymptomDetail(present=True, duration=None, severity=None)
            },
            "answers": {"cough_duration": "3 days"},
            "negated": [],
            "expected_question_id": "q_fever_duration"
        }
    ]

    for tc in test_cases:
        print(f"\n--- Testing: {tc['name']} ---")
        state = PatientState(
            session_id="test_session",
            conversation_id="test_conv",
            language=tc["lang"],
            symptoms=tc["symptoms"],
            negated_symptoms=tc["negated"],
            original_input_history=tc["history"],
            answers=tc.get("answers", {})
        )

        result = selector.select_next_question(state)
        
        if result.is_ready_for_triage:
            print("Model output: READY FOR TRIAGE")
        else:
            q = result.selected_question
            print(f"Expected QID: {tc['expected_question_id']}")
            print(f"Selected QID: {q.question_id}")
            print(f"Wording: {result.wording}")
            print(f"Reasoning: {result.reasoning}")

if __name__ == "__main__":
    run_simulation()
