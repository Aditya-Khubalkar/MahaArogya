# -*- coding: utf-8 -*-
import wave
import numpy as np
import scipy.signal
import json
import os
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sys

sys.path.append("c:/MahaArogya")
from ai.nlp.extractor import MedicalExtractor
from ai.triage.safety_rules import SafetyRuleEngine
from ai.patient_state.schemas import PatientState
from ai.patient_state.state_manager import PatientStateManager

def load_wav(path):
    with wave.open(path, 'rb') as w:
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if sr != 16000 and len(audio) > 0:
            # Resample to 16000
            new_length = int(len(audio) * 16000 / sr)
            if new_length > 0:
                audio = scipy.signal.resample(audio, new_length)
            sr = 16000
        return audio, sr

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_wer(ref, hyp):
    r = ref.split()
    h = hyp.split()
    if len(r) == 0: return 0.0 if len(h) == 0 else 1.0
    return levenshtein(r, h) / len(r)

def calculate_cer(ref, hyp):
    if len(ref) == 0: return 0.0 if len(hyp) == 0 else 1.0
    return levenshtein(ref, hyp) / len(ref)

def evaluate_pipeline():
    model_dir = r"c:\MahaArogya\models\whisper_small_smoketest"
    processor = WhisperProcessor.from_pretrained("openai/whisper-small")
    model = WhisperForConditionalGeneration.from_pretrained(model_dir)
    model.eval()
    if torch.cuda.is_available():
        model.to("cuda")

    dataset_path = r"C:\MahaArogya\data\test\asr\synthetic_tts\asr_100_utterances.json"
    audio_dir = r"C:\MahaArogya\data\test\asr\synthetic_tts"

    with open(dataset_path, "r", encoding="utf-8") as f:
        utterances = json.load(f)

    extractor = MedicalExtractor()
    safety_engine = SafetyRuleEngine()

    total_wer = 0
    total_cer = 0
    total_samples = 0

    language_metrics = {}
    
    total_emergencies_expected = 0
    total_emergencies_predicted = 0
    
    print("Evaluating ASR and Pipeline...")
    for utt in utterances:
        filename = f"asr_{utt['id']}.wav"
        audio_path = os.path.join(audio_dir, filename)
        if not os.path.exists(audio_path):
            continue

        audio, sr = load_wav(audio_path)
        if len(audio) == 0:
            print(f"Skipping {audio_path} - Empty Audio")
            continue

        input_features = processor(audio, sampling_rate=sr, return_tensors="pt").input_features
        if torch.cuda.is_available():
            input_features = input_features.to("cuda")
        
        lang_code = utt["lang"]
        if lang_code == "mr": lang_code = "mr"
        elif lang_code == "hi": lang_code = "hi"
        else: lang_code = "en"
        
        forced_decoder_ids = processor.get_decoder_prompt_ids(language=lang_code, task="transcribe")
        
        with torch.no_grad():
            predicted_ids = model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
        
        print(f"[{utt['category']}] Ref: {utt['reference']}")
        print(f"[{utt['category']}] Hyp: {transcription}")

        ref = utt["reference"]
        wer = calculate_wer(ref, transcription)
        cer = calculate_cer(ref, transcription)

        total_wer += wer
        total_cer += cer
        total_samples += 1

        lang_cat = utt["category"]
        if lang_cat not in language_metrics:
            language_metrics[lang_cat] = {"wer": 0, "cer": 0, "count": 0}
        language_metrics[lang_cat]["wer"] += wer
        language_metrics[lang_cat]["cer"] += cer
        language_metrics[lang_cat]["count"] += 1

        manager = PatientStateManager(conversation_id="test")
        delta = extractor.extract("test", transcription)
        state = manager.update_with_delta(delta)
        safety_result = safety_engine.evaluate(state)
        severity = safety_result.escalation_level
        
        ref_manager = PatientStateManager(conversation_id="ref")
        ref_delta = extractor.extract("ref", ref)
        ref_state = ref_manager.update_with_delta(ref_delta)
        ref_safety_result = safety_engine.evaluate(ref_state)
        ref_severity = ref_safety_result.escalation_level
        
        # EMERGENCY_AMBULANCE is the level for emergency
        if "EMERGENCY" in ref_severity:
            total_emergencies_expected += 1
            if "EMERGENCY" in severity:
                total_emergencies_predicted += 1

    if total_samples > 0:
        avg_wer = total_wer / total_samples
        avg_cer = total_cer / total_samples
        print(f"Total Samples Evaluated: {total_samples}")
        print(f"Overall WER: {avg_wer:.4f}")
        print(f"Overall CER: {avg_cer:.4f}")
        print(f"Emergency Recall: {total_emergencies_predicted}/{total_emergencies_expected}")

        for lang, metrics in language_metrics.items():
            l_wer = metrics["wer"] / metrics["count"]
            l_cer = metrics["cer"] / metrics["count"]
            print(f"{lang} ({metrics['count']} samples) - WER: {l_wer:.4f}, CER: {l_cer:.4f}")

if __name__ == "__main__":
    evaluate_pipeline()
