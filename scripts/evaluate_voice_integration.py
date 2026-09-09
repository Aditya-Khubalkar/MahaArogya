"""
MahaArogya — Voice Integration Evaluation
Tests the end-to-end Voice -> ASR -> Extractor -> PatientState -> Triage pipeline.
"""

import os
import time
import requests
import pyttsx3
import tempfile
import sys

API_URL = "http://127.0.0.1:8000/api/conversation/voice_turn"

def synthesize_test_audio(text: str, filename: str) -> str:
    print(f"Synthesizing test audio for: '{text}'")
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    filepath = os.path.join(tempfile.gettempdir(), filename)
    engine.save_to_file(text, filepath)
    engine.runAndWait()
    engine.stop()
    return filepath

def run_test_case(name: str, text: str, expected_symptoms: list, expected_triage: str):
    print(f"\n======================================")
    print(f"TEST CASE: {name}")
    print(f"======================================")
    
    audio_path = synthesize_test_audio(text, f"test_{name}.wav")
    
    print(f"Sending audio to {API_URL} ...")
    start_t = time.time()
    
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": (f"test_{name}.wav", f, "audio/wav")}
            data = {"language": "en"}
            response = requests.post(API_URL, files=files, data=data)
            
        latency = time.time() - start_t
        
        if response.status_code != 200:
            print(f"[FAIL] HTTP {response.status_code}: {response.text}")
            return False
            
        result = response.json()
        
        transcript = result.get("transcript_or_text", "")
        patient_state = result.get("patient_state", {})
        symptoms = patient_state.get("symptoms", {})
        triage = result.get("triage_decision", {})
        triage_category = triage.get("triage_category", "")
        
        print(f"ASR Transcript: '{transcript}'")
        print(f"Extracted Symptoms: {list(symptoms.keys())}")
        print(f"Triage Decision: {triage_category}")
        print(f"Latency: {latency:.2f}s")
        
        # Verify extraction
        missing_symptoms = [s for s in expected_symptoms if s not in symptoms]
        if missing_symptoms:
            print(f"[FAIL] Missing symptoms: {missing_symptoms}")
            return False
            
        if triage_category != expected_triage:
            print(f"[FAIL] Expected {expected_triage} but got {triage_category}")
            return False
            
        print("[PASS] Validation successful!")
        return True
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == "__main__":
    print("Starting Voice Integration Tests...")
    
    # Wait for API to be up
    try:
        requests.get("http://127.0.0.1:8000/health")
    except requests.exceptions.ConnectionError:
        print("API is not running. Please start the FastAPI backend on port 8000.")
        sys.exit(1)
        
    tests = [
        {
            "name": "emergency_oxygen",
            "text": "My oxygen is 88 and I cannot breathe. Please help me.",
            "expected_symptoms": ["breathing_difficulty"],
            "expected_triage": "EMERGENCY"
        },
        {
            "name": "urgent_chest",
            "text": "I have been having severe chest pain for the last hour.",
            "expected_symptoms": ["chest_pain"],
            "expected_triage": "EMERGENCY"
        }
    ]
    
    all_passed = True
    for t in tests:
        if not run_test_case(t["name"], t["text"], t["expected_symptoms"], t["expected_triage"]):
            all_passed = False
            
    if all_passed:
        print("\nAll integration tests PASSED! 100% Emergency Recall.")
        sys.exit(0)
    else:
        print("\nSome tests FAILED.")
        sys.exit(1)
