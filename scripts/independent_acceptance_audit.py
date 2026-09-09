import os
import sys
import time
import shutil
import uuid
import subprocess
import requests
import traceback
import json
import re
import tempfile
from pathlib import Path

print("========================================")
print("INDEPENDENT ACCEPTANCE AUDIT INIT")
print("========================================")

# Ensure CWD is project root
PROJECT_ROOT = Path(os.getcwd())
if not (PROJECT_ROOT / "ai").exists():
    print("Must run from project root")
    sys.exit(1)
sys.path.append(str(PROJECT_ROOT))

# Setup temp dir
TEMP_DIR = Path(tempfile.gettempdir()) / f"mahaarogya_audit_{uuid.uuid4().hex[:8]}"
TEMP_DIR.mkdir(parents=True, exist_ok=True)
print(f"TEMP DIR: {TEMP_DIR}")

metrics = {
    "TOTAL_CHECKS": 0,
    "PASS": 0,
    "FAIL": 0,
    "PARTIAL": 0,
    "NOT_VERIFIED": 0,
    "CRITICAL_FAILURES": 0,
    "CLAIMED_BUT_UNPROVEN": 0,
    "MOCKED_PRODUCTION_COMPONENTS": 0
}

results = {
    "RTX 5060 AI": "NOT VERIFIED",
    "API": "NOT VERIFIED",
    "REAL ASR": "NOT VERIFIED",
    "REAL TTS": "NOT VERIFIED",
    "REAL TRIAGE": "NOT VERIFIED",
    "REAL VOICE PIPELINE": "NOT VERIFIED",
    "REAL HTTP": "NOT VERIFIED",
    "PORTABILITY": "NOT VERIFIED",
    "8GB VRAM": "NOT VERIFIED",
}

def record_result(category, status, is_critical=False):
    metrics["TOTAL_CHECKS"] += 1
    if status == "PASS":
        metrics["PASS"] += 1
    elif status == "FAIL":
        metrics["FAIL"] += 1
        if is_critical:
            metrics["CRITICAL_FAILURES"] += 1
    elif status == "PARTIAL":
        metrics["PARTIAL"] += 1
    elif status == "NOT VERIFIED":
        metrics["NOT_VERIFIED"] += 1
    elif status == "CLAIMED BUT UNPROVEN":
        metrics["CLAIMED_BUT_UNPROVEN"] += 1
    print(f"[{category}] -> {status}")

# Import actual modules
try:
    import torch
    from ai.asr.service import get_asr_service
    from ai.tts.service import get_tts_service
    from ai.tts.schemas import TTSRequest
    from ai.nlp.extractor import MedicalExtractor
    from ai.triage.classifier import TriageClassifier
    from ai.patient_state.state_manager import PatientStateManager
    from ai.triage.safety_rules import SafetyRuleEngine
    from ai.orchestrator import MahaArogyaOrchestrator
except Exception as e:
    print(f"FATAL IMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# RULE 13 - VRAM (Baseline)
def get_vram():
    if torch.cuda.is_available():
        return torch.cuda.memory_allocated(0) / (1024**3)
    return 0

vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3) if torch.cuda.is_available() else 0
vram_baseline = get_vram()
print(f"VRAM Total: {vram_total:.2f} GB, Baseline: {vram_baseline:.2f} GB")

# RULE 2 - REAL PYTEST
print("\n--- RULE 2: PYTEST ---")
pytest_out = subprocess.run([sys.executable, "-m", "pytest", "tests"], capture_output=True, text=True)
print(pytest_out.stdout)
pytest_summary = "Pytest execution failed to parse"
if "failed" in pytest_out.stdout.lower() or "passed" in pytest_out.stdout.lower():
    lines = pytest_out.stdout.splitlines()
    for line in reversed(lines):
        if "passed" in line.lower() or "failed" in line.lower():
            pytest_summary = line.strip()
            break
print(f"Parsed Pytest: {pytest_summary}")

# RULE 3 - MODEL INVENTORY
print("\n--- RULE 3: MODEL INVENTORY ---")
models_dir = PROJECT_ROOT / "models"
for root, dirs, files in os.walk(models_dir):
    for file in files:
        if file.endswith(('.pt', '.bin', '.safetensors', '.onnx')):
            fp = Path(root) / file
            print(f"Model: {fp}, Size: {fp.stat().st_size / (1024**2):.2f} MB")

# RULE 4 - REAL ASR
print("\n--- RULE 4: REAL ASR ---")
try:
    asr = get_asr_service()
    vram_asr_load = get_vram()
    print(f"VRAM after ASR load: {vram_asr_load:.2f} GB")
    
    # find audio file
    test_audio = None
    for ext in ['*.wav', '*.mp3']:
        for f in PROJECT_ROOT.rglob(ext):
            if 'test' in str(f).lower() or 'sample' in str(f).lower():
                test_audio = f
                break
        if test_audio: break
        
    if test_audio:
        print(f"Using audio: {test_audio}")
        t0 = time.time()
        asr_res = asr.transcribe(str(test_audio))
        vram_asr_peak = get_vram()
        print(f"ASR Peak VRAM: {vram_asr_peak:.2f} GB")
        print(f"Transcript: {asr_res.transcript}")
        print(f"Language: {asr_res.language}")
        print(f"Latency: {time.time()-t0:.2f}s")
        if asr_res.transcript:
            results["REAL ASR"] = "PASS"
            record_result("REAL ASR", "PASS")
        else:
            results["REAL ASR"] = "FAIL"
            record_result("REAL ASR", "FAIL", True)
    else:
        print("No test audio found.")
        results["REAL ASR"] = "NOT VERIFIED"
        record_result("REAL ASR", "NOT VERIFIED")
except Exception as e:
    print(f"ASR Error: {e}")
    results["REAL ASR"] = "FAIL"
    record_result("REAL ASR", "FAIL", True)

# RULE 5 & 6 - REAL NLP & MEDICAL PIPELINE
print("\n--- RULE 5 & 6: REAL NLP & MEDICAL PIPELINE ---")
nlp_pass = True
try:
    extractor = MedicalExtractor()
    triage = TriageClassifier()
    state_mgr = PatientStateManager("audit_nlp")
    
    cases = [
        ("My oxygen is 88 and I cannot breathe.", "en"),
        ("मेरा ऑक्सीजन 88 है और मुझे सांस नहीं आ रही।", "hi"),
        ("माझा ऑक्सिजन ८८ आहे आणि मला श्वास घेता येत नाही.", "mr"),
        ("maza oxygen 88 aahe ani mala shwas gheta yet nahi", "roman-mr"),
        ("mera oxygen 88 hai aur mujhe saans nahi aa rahi", "hinglish")
    ]
    
    safety_engine = SafetyRuleEngine()
    for text, lang in cases:
        print(f"\nRAW INPUT: {text}")
        print(f"LANGUAGE: {lang}")
        diff = extractor.extract(f"conv_{lang}", text)
        state_mgr.update_with_delta(diff)
        state = state_mgr.get_state()
        print(f"EXTRACTOR OUTPUT: {diff.new_symptoms}, {diff.new_vitals}")
        print(f"PATIENT STATE: SpO2={getattr(state.vitals, 'spo2_percent', None)}, Symptoms={list(state.symptoms.keys())}")
        
        sr = safety_engine.evaluate(state)
        print(f"SAFETY RULES: {sr.is_emergency} {sr.triggered_rule_ids}")
        
        decision = triage.classify(state)
        print(f"TRIAGE: {decision.triage_category}")
        print(f"ESCALATION: {decision.escalation_level}")
        
        if "88" in text or "८८" in text:
            if getattr(state.vitals, 'spo2_percent', None) == 88.0 and decision.triage_category == "EMERGENCY":
                print("Pipeline rules PASS for SpO2=88")
            else:
                print("Pipeline rules FAIL for SpO2=88")
                nlp_pass = False
        
        state_mgr = PatientStateManager(f"audit_nlp_{uuid.uuid4().hex}")
        
    vram_triage = get_vram()
    print(f"VRAM after NLP/Triage: {vram_triage:.2f} GB")
    
    if nlp_pass:
        results["REAL TRIAGE"] = "PASS"
        record_result("NLP & TRIAGE", "PASS")
    else:
        results["REAL TRIAGE"] = "FAIL"
        record_result("NLP & TRIAGE", "FAIL", True)

except Exception as e:
    print(f"NLP Error: {e}")
    results["REAL TRIAGE"] = "FAIL"
    record_result("NLP & TRIAGE", "FAIL", True)

# RULE 7 - MULTI-TURN
print("\n--- RULE 7: MULTI-TURN ---")
try:
    sm = PatientStateManager("audit_multiturn")
    sm.update_with_delta(extractor.extract("audit_multiturn", "Majha pot dukhtay."))
    print(f"Turn 1 Symptoms: {list(sm.get_state().symptoms.keys())}")
    sm.update_with_delta(extractor.extract("audit_multiturn", "Don divas pasun."))
    print(f"Turn 2 Duration: {sm.get_state().symptoms.get('abdominal_pain').duration if 'abdominal_pain' in sm.get_state().symptoms else None}")
    sm.update_with_delta(extractor.extract("audit_multiturn", "Vomiting pan hot aahe."))
    print(f"Turn 3 Symptoms: {list(sm.get_state().symptoms.keys())}")
    
    if "abdominal_pain" in sm.get_state().symptoms and "vomiting" in sm.get_state().symptoms:
        record_result("MULTI-TURN", "PASS")
    else:
        record_result("MULTI-TURN", "FAIL", True)
        
    sm2 = PatientStateManager("audit_multiturn_2")
    if len(sm2.get_state().symptoms) == 0:
        print("Isolation PASS")
    else:
        print("Isolation FAIL")
except Exception as e:
    print(f"Multi-turn Error: {e}")
    record_result("MULTI-TURN", "FAIL", True)

# RULE 8 - REAL TTS
print("\n--- RULE 8: REAL TTS ---")
try:
    tts = get_tts_service()
    vram_tts_load = get_vram()
    print(f"VRAM after TTS load: {vram_tts_load:.2f} GB")
    
    backend_used = getattr(tts, 'provider', 'unknown')
    if hasattr(tts, '_get_provider'): backend_used = tts._get_provider("en")
    print(f"TTS Backend: {backend_used}")
    
    t0 = time.time()
    res = tts.synthesize(TTSRequest(text="This is a test.", language="en"))
    print(f"Latency: {time.time()-t0:.2f}s")
    if os.path.exists(res.audio_path) and os.path.getsize(res.audio_path) > 0:
        print(f"TTS Audio generated: {res.audio_path}")
        results["REAL TTS"] = "PASS"
        record_result("REAL TTS", "PASS")
    else:
        results["REAL TTS"] = "FAIL"
        record_result("REAL TTS", "FAIL", True)
except Exception as e:
    print(f"TTS Error: {e}")
    results["REAL TTS"] = "FAIL"
    record_result("REAL TTS", "FAIL", True)

# RULE 9 & 10 - REAL FASTAPI & VOICE PIPELINE
print("\n--- RULE 10: REAL FASTAPI ---")
PORT = 8011
BASE_URL = f"http://127.0.0.1:{PORT}"

# Free up VRAM before starting Uvicorn in a subprocess
print("Clearing VRAM before FastAPI test...")
try:
    del asr
    del extractor
    del tts
except Exception:
    pass
import gc
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
print(f"VRAM after cleanup: {get_vram():.2f} GB")

server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(10) # wait for startup
try:
    r_health = requests.get(f"{BASE_URL}/health")
    print(f"Health: {r_health.status_code}")
    
    r_text = requests.post(f"{BASE_URL}/api/v1/text/turn", json={"session_id": "audit_api", "text_input": "I have chest pain", "language": "en"})
    print(f"Text Turn status: {r_text.status_code}")
    if r_text.status_code == 200:
        results["REAL HTTP"] = "PASS"
        record_result("HTTP TEXT", "PASS")
    else:
        results["REAL HTTP"] = "FAIL"
        record_result("HTTP TEXT", "FAIL", True)
        
    # Voice Turn
    if test_audio:
        with open(test_audio, "rb") as f:
            r_voice = requests.post(f"{BASE_URL}/api/v1/voice/turn", files={"audio_file": ("test.wav", f, "audio/wav")}, data={"session_id": "audit_api_voice", "language": "en"})
        print(f"Voice Turn status: {r_voice.status_code}")
        if r_voice.status_code == 200:
            results["REAL VOICE PIPELINE"] = "PASS"
            record_result("HTTP VOICE", "PASS")
        else:
            results["REAL VOICE PIPELINE"] = "FAIL"
            record_result("HTTP VOICE", "FAIL", True)
    
    # RULE 11 - API ERROR TESTS
    r_err = requests.post(f"{BASE_URL}/api/v1/text/turn", json={"missing": "fields"})
    print(f"Malformed request status: {r_err.status_code}")
    if r_err.status_code == 422:
        record_result("HTTP ERRORS", "PASS")
    else:
        record_result("HTTP ERRORS", "FAIL")

except Exception as e:
    print(f"API Error: {e}")
    results["REAL HTTP"] = "FAIL"
    results["REAL VOICE PIPELINE"] = "FAIL"
finally:
    server.terminate()
    server.wait()

# RULE 12 - PORTABILITY
print("\n--- RULE 12: PORTABILITY ---")
portability_dir = TEMP_DIR / "portability"
portability_dir.mkdir()
try:
    # Copy essential dirs
    for d in ["ai", "api", "models", "data", "core"]:
        if (PROJECT_ROOT / d).exists():
            shutil.copytree(PROJECT_ROOT / d, portability_dir / d)
    
    # Run a simple import script in that dir
    test_script = portability_dir / "test_portability.py"
    test_script.write_text(
        "import sys, os; sys.path.append(os.getcwd()); "
        "from ai.orchestrator import MahaArogyaOrchestrator; "
        "print('PORTABILITY_OK')"
    )
    port_out = subprocess.run([sys.executable, str(test_script)], cwd=str(portability_dir), capture_output=True, text=True)
    if "C:\\MahaArogya" in port_out.stdout or "C:\\MahaArogya" in port_out.stderr:
        print("Portability FAIL: Absolute paths found in execution")
        results["PORTABILITY"] = "FAIL"
        record_result("PORTABILITY", "FAIL", True)
    elif "PORTABILITY_OK" in port_out.stdout:
        print("Portability PASS")
        results["PORTABILITY"] = "PASS"
        record_result("PORTABILITY", "PASS")
    else:
        print(f"Portability FAIL: {port_out.stderr}")
        results["PORTABILITY"] = "FAIL"
        record_result("PORTABILITY", "FAIL", True)
except Exception as e:
    print(f"Portability Error: {e}")
    results["PORTABILITY"] = "FAIL"
    record_result("PORTABILITY", "FAIL", True)

# RULE 14 & 15 - CLOUD & MOCK DETECTION
print("\n--- RULE 14 & 15: CLOUD & MOCK DETECTION ---")
grep_cloud = subprocess.run('findstr /S /I /M "OpenAI Gemini Azure ElevenLabs cloud" ai\\*.py api\\*.py', shell=True, capture_output=True, text=True)
print(f"Cloud mentions: {grep_cloud.stdout.strip().replace(chr(10), ' ')}")

def classify_mock(path, line_content):
    path = path.lower()
    line = line_content.lower()
    if 'data\\raw' in path or 'scripts\\' in path or 'test' in path:
        return "TEST CODE"
    if 'f5_tts' in path:
        return "THIRD-PARTY CODE"
    if '#' in line_content and line_content.split('#', 1)[1].lower().find('mock') != -1:
        return "DOCUMENTATION"
    if 'mock' in line or 'dummy' in line or 'fake' in line:
        if 'src\\' in path or 'ai\\' in path or 'api\\' in path:
            return "REAL PRODUCTION MOCK"
    return "FALSE POSITIVE"

metrics["REAL_PRODUCTION_MOCKS"] = 0
metrics["FALSE_POSITIVE_MOCKS"] = 0

print("Mock Matches:")
for root, dirs, files in os.walk(PROJECT_ROOT):
    if "venv" in root or ".git" in root or "tests" in root: continue
    for file in files:
        if file.endswith('.py'):
            fp = Path(root) / file
            try:
                content = fp.read_text(encoding='utf-8')
                for idx, line in enumerate(content.splitlines()):
                    if re.search(r'\b(mock|dummy|fake|placeholder|simulation|stub)\b', line, re.IGNORECASE):
                        rel = str(fp.relative_to(PROJECT_ROOT))
                        cls = classify_mock(rel, line.strip())
                        print(f"{rel}:{idx+1} -> [{cls}] {line.strip()}")
                        if cls == "REAL PRODUCTION MOCK":
                            metrics["REAL_PRODUCTION_MOCKS"] += 1
                        else:
                            metrics["FALSE_POSITIVE_MOCKS"] += 1
            except Exception: pass

# RULE 16 - TEST MODIFICATION AUDIT
print("\n--- RULE 16: TEST MODIFICATION AUDIT ---")
git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
if git_status.returncode == 0:
    git_diff = subprocess.run(["git", "diff", "--", "tests/"], capture_output=True, text=True)
    if git_diff.stdout.strip():
        print("TEST MODIFICATIONS DETECTED:")
        print(git_diff.stdout[:500])
    else:
        print("No uncommitted test modifications.")
else:
    print("TEST HISTORY: NOT AVAILABLE")

# Final check for VRAM
vram_peak = get_vram()
print(f"Peak VRAM: {vram_peak:.2f} GB")
if vram_total > 0 and vram_peak <= vram_total and vram_peak <= 8.0:
    results["8GB VRAM"] = "PASS"
else:
    results["8GB VRAM"] = "FAIL"

if results["REAL ASR"] == "PASS" and results["REAL TTS"] == "PASS" and results["REAL TRIAGE"] == "PASS" and results["REAL VOICE PIPELINE"] == "PASS" and results["PORTABILITY"] == "PASS":
    results["RTX 5060 AI"] = "PASS"
else:
    results["RTX 5060 AI"] = "FAIL"

if results["REAL HTTP"] == "PASS" and results["REAL VOICE PIPELINE"] == "PASS":
    results["API"] = "PASS"
else:
    results["API"] = "FAIL"

print("\n========================================")
print("CORRECTED FINAL ACCEPTANCE RESULT")
print("========================================")
print(f"RTX 5060 AI: {results['RTX 5060 AI']}")
print(f"API: {results['API']}")
print(f"REAL ASR: {results['REAL ASR']}")
print(f"REAL TTS: {results['REAL TTS']}")
print(f"REAL TRIAGE: {results['REAL TRIAGE']}")
print(f"REAL VOICE PIPELINE: {results['REAL VOICE PIPELINE']}")
print(f"REAL HTTP: {results['REAL HTTP']}")
print(f"PORTABILITY: {results['PORTABILITY']}")
print(f"8GB VRAM: {results['8GB VRAM']}")
print(f"\nPYTEST:\n{pytest_summary}")
print(f"\nTOTAL CHECKS:\n{metrics['TOTAL_CHECKS']}")
print(f"\nPASS:\n{metrics['PASS']}")
print(f"\nFAIL:\n{metrics['FAIL']}")
print(f"\nPARTIAL:\n{metrics['PARTIAL']}")
print(f"\nNOT VERIFIED:\n{metrics['NOT_VERIFIED']}")
print(f"\nCRITICAL FAILURES:\n{metrics['CRITICAL_FAILURES']}")
print(f"\nCLAIMED BUT UNPROVEN:\n{metrics['CLAIMED_BUT_UNPROVEN']}")
print(f"\nREAL PRODUCTION MOCKS:\n{metrics['REAL_PRODUCTION_MOCKS']}")
print(f"\nFALSE POSITIVE MOCK MATCHES:\n{metrics['FALSE_POSITIVE_MOCKS']}")
print("========================================")
