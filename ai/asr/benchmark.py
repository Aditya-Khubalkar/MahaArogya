"""
MahaArogya — ASR Benchmark Suite & CLI
Evaluates faster-whisper on Marathi, Hindi, English, Hinglish, and Code-Switching test sets.
Calculates Word Error Rate (WER), Character Error Rate (CER), latency, and VRAM footprint.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Adjust import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.asr.service import ASRService
from ai.asr.config import ASRConfig


def levenshtein_distance(ref: List[str], hyp: List[str]) -> int:
    """Computes Levenshtein edit distance between reference and hypothesis tokens."""
    m, n = len(ref), len(hyp)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n]


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate (WER)."""
    ref_words = reference.strip().lower().split()
    hyp_words = hypothesis.strip().lower().split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    dist = levenshtein_distance(ref_words, hyp_words)
    return round(dist / len(ref_words), 4)


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Calculate Character Error Rate (CER)."""
    ref_chars = list(reference.strip().lower())
    hyp_chars = list(hypothesis.strip().lower())

    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0

    dist = levenshtein_distance(ref_chars, hyp_chars)
    return round(dist / len(ref_chars), 4)


def run_single_benchmark(audio_path: str, model_size: str = "small", language: str = None):
    """Run ASR on a single audio file and print detailed timing and transcript."""
    config = ASRConfig(model_size=model_size)
    service = ASRService(config)

    print(f"\n{'='*60}")
    print(f"ASR Benchmark — Single Audio File")
    print(f"File: {audio_path}")
    print(f"Model: {model_size} | Language: {language or 'auto'}")
    print(f"{'='*60}\n")

    result = service.transcribe(audio_path, language=language)

    print(f"Transcript:           {result.transcript}")
    print(f"Detected Language:    {result.language} (prob: {result.language_probability:.2f})")
    print(f"Duration:             {result.duration_sec}s")
    print(f"Latency:              {result.latency_sec}s")
    print(f"Confidence (logprob): {result.confidence}")
    print(f"Segments Count:       {len(result.segments)}")

    out_file = PROJECT_ROOT / "evaluation" / f"asr_single_{Path(audio_path).stem}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    print(f"\nSaved evaluation log to: {out_file}")


def create_sample_audio_if_needed(target_wav: Path):
    """Generates a synthetic 3-second test WAV file using wave module if no audio file exists."""
    target_wav.parent.mkdir(parents=True, exist_ok=True)
    if target_wav.exists():
        return target_wav

    import math
    import struct
    import wave

    sample_rate = 16000
    duration = 3.0  # seconds
    frequency = 440.0  # A4 tone

    with wave.open(str(target_wav), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(sample_rate)

        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            # Sine wave sample
            sample = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            wav_file.writeframesraw(struct.pack("<h", sample))

    print(f"[SampleAudio] Generated synthetic test audio: {target_wav}")
    return target_wav


def main():
    parser = argparse.ArgumentParser(description="MahaArogya ASR Benchmark Tool")
    parser.add_argument("--audio", type=str, help="Path to audio file for single transcription")
    parser.add_argument("--model-size", type=str, default="small", choices=["tiny", "base", "small", "medium", "large-v3"], help="Whisper model size")
    parser.add_argument("--language", type=str, default=None, help="Language code (e.g. 'mr', 'hi', 'en')")
    parser.add_argument("--test-synthetic", action="store_true", help="Generate and test on synthetic tone audio file")

    args = parser.parse_args()

    if args.audio:
        run_single_benchmark(args.audio, model_size=args.model_size, language=args.language)
    elif args.test_synthetic:
        test_wav = PROJECT_ROOT / "data" / "test" / "synthetic_test.wav"
        create_sample_audio_if_needed(test_wav)
        run_single_benchmark(str(test_wav), model_size=args.model_size, language=args.language)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
