import sys
import os
import json
import string
import torch
import scipy.io.wavfile as wav
from pathlib import Path
from transformers import WhisperForConditionalGeneration, WhisperProcessor

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def compute_wer_cer(ref: str, hyp: str) -> tuple[float, float]:
    translator = str.maketrans("", "", string.punctuation)
    
    ref_clean = ref.lower().translate(translator).strip()
    hyp_clean = hyp.lower().translate(translator).strip()
    
    ref_words = ref_clean.split()
    hyp_words = hyp_clean.split()
    
    if not ref_words:
        return (0.0 if not hyp_words else 1.0, 0.0 if not hyp_words else 1.0)
        
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1): d[i][0] = i
    for j in range(len(hyp_words) + 1): d[0][j] = j
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = 1 + min(d[i-1][j], d[i][j-1], d[i-1][j-1])
    wer = d[len(ref_words)][len(hyp_words)] / len(ref_words)
    
    ref_chars = list(ref_clean.replace(" ", ""))
    hyp_chars = list(hyp_clean.replace(" ", ""))
    if not ref_chars:
        return (wer, 0.0 if not hyp_chars else 1.0)
        
    dc = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
    for i in range(len(ref_chars) + 1): dc[i][0] = i
    for j in range(len(hyp_chars) + 1): dc[0][j] = j
    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                dc[i][j] = dc[i-1][j-1]
            else:
                dc[i][j] = 1 + min(dc[i-1][j], dc[i][j-1], dc[i-1][j-1])
    cer = dc[len(ref_chars)][len(hyp_chars)] / len(ref_chars)
    return round(wer, 4), round(cer, 4)

def run_indicwhisper_eval():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("=" * 115)
    print(f"FLEURS EVALUATION ON INDICWHISPER MODEL (Device: {device})")
    print("=" * 115)

    manifest_path = Path(r"C:\MahaArogya\data\test\asr_real_eval\manifest.json")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    print("Loading ai4bharat/indicwhisper from HuggingFace...")
    processor = WhisperProcessor.from_pretrained("openai/whisper-small")
    model = WhisperForConditionalGeneration.from_pretrained("ai4bharat/indicwhisper").to(device)
    model.eval()

    lang_map = {"hi": "hindi", "mr": "marathi"}
    results = []

    print(f"{'Idx':<4} | {'ID':<14} | {'Lang':<5} | {'WER':<8} | {'CER':<8} | {'Exact Audio File Path'}")
    print("-" * 115)

    for idx, s in enumerate(samples, 1):
        audio_path = Path(s["audio_path"])
        if not audio_path.exists():
            print(f"{idx:<4} | {s['id']:<14} | {s['lang']:<5} | ERROR    | ERROR    | FILE NOT FOUND: {audio_path}")
            continue

        sr, audio_data = wav.read(audio_path)
        inputs = processor(audio_data, sampling_rate=sr, return_tensors="pt").input_features.to(device)

        full_lang = lang_map.get(s["lang"], s["lang"])
        forced_decoder_ids = processor.get_decoder_prompt_ids(language=full_lang, task="transcribe")

        with torch.no_grad():
            predicted_ids = model.generate(inputs, forced_decoder_ids=forced_decoder_ids)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

        wer, cer = compute_wer_cer(s["reference"], transcription)

        res = {
            "clip_id": s["id"],
            "language": s["lang"],
            "reference": s["reference"],
            "hypothesis": transcription,
            "wer": wer,
            "cer": cer,
            "audio_path": str(audio_path.resolve())
        }
        results.append(res)

        print(f"{idx:<4} | {s['id']:<14} | {s['lang']:<5} | {wer*100:6.2f}% | {cer*100:6.2f}% | {str(audio_path.resolve())}")

    hi_results = [r for r in results if r["language"] == "hi"]
    mr_results = [r for r in results if r["language"] == "mr"]

    hi_wer = sum(r["wer"] for r in hi_results) / len(hi_results) if hi_results else 0.0
    hi_cer = sum(r["cer"] for r in hi_results) / len(hi_results) if hi_results else 0.0
    mr_wer = sum(r["wer"] for r in mr_results) / len(mr_results) if mr_results else 0.0
    mr_cer = sum(r["cer"] for r in mr_results) / len(mr_results) if mr_results else 0.0
    comb_wer = sum(r["wer"] for r in results) / len(results) if results else 0.0
    comb_cer = sum(r["cer"] for r in results) / len(results) if results else 0.0

    print("\n" + "=" * 115)
    print("INDICWHISPER EVALUATION FINAL SUMMARY")
    print("=" * 115)
    print(f"Hindi (25 clips)   | Mean WER: {hi_wer*100:6.2f}% | Mean CER: {hi_cer*100:6.2f}%")
    print(f"Marathi (25 clips) | Mean WER: {mr_wer*100:6.2f}% | Mean CER: {mr_cer*100:6.2f}%")
    print(f"Combined (50 clips)| Mean WER: {comb_wer*100:6.2f}% | Mean CER: {comb_cer*100:6.2f}%")
    print("=" * 115)

if __name__ == "__main__":
    run_indicwhisper_eval()
