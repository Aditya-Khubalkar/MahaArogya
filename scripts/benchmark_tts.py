import os
import time
import json
import psutil
import torch
from ai.tts.schemas import TTSRequest
from ai.tts.service import get_tts_service

OUTPUT_DIR = r"C:\MahaArogya\data\test\tts_benchmark"
os.makedirs(OUTPUT_DIR, exist_ok=True)

sentences = {
    "en": [
        "Please remain calm. I am checking your symptoms.",
        "Your oxygen level is 88 percent and your heart rate is 130.",
        "Blood pressure 120 over 80.",
        "Temperature is 98.6 degrees."
    ],
    "hi": [
        "कृपया शांत रहें। मैं आपके लक्षणों की जाँच कर रहा हूँ।",
        "आपका ऑक्सीजन स्तर 88 प्रतिशत है और आपकी हृदय गति 130 है।"
    ],
    "mr": [
        "कृपया शांत राहा. मी तुमच्या लक्षणांची तपासणी करत आहे.",
        "तुमची ऑक्सिजन पातळी 88 टक्के आहे आणि तुमची हृदय गती 130 आहे."
    ]
}

def get_ram_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 ** 2)

def get_vram_mb():
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        return torch.cuda.memory_allocated() / (1024 ** 2)
    return 0

def run_benchmark():
    service = get_tts_service()
    results = {}

    for lang, texts in sentences.items():
        print(f"Benchmarking language: {lang}")
        results[lang] = {"sentences": [], "success_rate": 0}
        successes = 0

        # Cold start
        ram_before = get_ram_mb()
        vram_before = get_vram_mb()

        # Warmup / First inference
        try:
            req = TTSRequest(text=texts[0], language=lang, speed=1.0)
            res = service.synthesize(req)
            successes += 1
            results[lang]["sentences"].append({
                "type": "cold",
                "latency": res.latency_sec,
                "duration": res.duration_sec,
                "rtf": round(res.latency_sec / res.duration_sec, 3) if res.duration_sec > 0 else 0,
                "ram_used_mb": get_ram_mb() - ram_before,
                "vram_used_mb": get_vram_mb() - vram_before
            })
        except Exception as e:
            print(f"Failed cold inference for {lang}: {e}")

        # Warm inferences
        for text in texts[1:]:
            try:
                ram_before = get_ram_mb()
                vram_before = get_vram_mb()
                req = TTSRequest(text=text, language=lang, speed=1.0)
                res = service.synthesize(req)
                successes += 1
                results[lang]["sentences"].append({
                    "type": "warm",
                    "latency": res.latency_sec,
                    "duration": res.duration_sec,
                    "rtf": round(res.latency_sec / res.duration_sec, 3) if res.duration_sec > 0 else 0,
                    "ram_used_mb": get_ram_mb() - ram_before,
                    "vram_used_mb": get_vram_mb() - vram_before
                })
            except Exception as e:
                print(f"Failed warm inference for {lang}: {e}")

        results[lang]["success_rate"] = successes / len(texts)

    with open(os.path.join(OUTPUT_DIR, "final_benchmark.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print("Benchmark complete!")

if __name__ == "__main__":
    run_benchmark()
