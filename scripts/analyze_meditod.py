import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEDITOD_PATH = ROOT / "data" / "raw" / "meditod" / "data" / "dialogs.json"

def main():
    if not MEDITOD_PATH.exists():
        print(f"Error: MediTOD data not found at {MEDITOD_PATH}")
        return
        
    with open(MEDITOD_PATH, 'r', encoding='utf-8') as f:
        dialogs = json.load(f)
        
    total_dialogs = len(dialogs)
    total_turns = 0
    patient_turns = 0
    doctor_turns = 0
    doctor_actions = {}
    
    for d_id, d in dialogs.items():
        utts = d.get("utterances", [])
        total_turns += len(utts)
        for utt in utts:
            if utt.get("speaker") == "patient":
                patient_turns += 1
            elif utt.get("speaker") == "doctor":
                doctor_turns += 1
                for action_obj in utt.get("actions", []):
                    a = action_obj.get("action", "")
                    doctor_actions[a] = doctor_actions.get(a, 0) + 1
                    
    print("--- MediTOD Analysis ---")
    print(f"Total Dialogs: {total_dialogs}")
    print(f"Total Turns: {total_turns} (Avg {total_turns/total_dialogs:.1f} per dialog)")
    print(f"Patient Turns: {patient_turns}")
    print(f"Doctor Turns: {doctor_turns}")
    print("\nTop 10 Doctor Actions:")
    for a, c in sorted(doctor_actions.items(), key=lambda x: -x[1])[:10]:
        print(f"  {a}: {c}")

if __name__ == "__main__":
    main()
