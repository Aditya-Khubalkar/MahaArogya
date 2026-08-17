import os
import huggingface_hub
from datasets import load_dataset

hf_token = huggingface_hub.get_token()
print(f"DEBUG: Retrieved HF Token present: {bool(hf_token)}")

targets = [
    ("Kathbath", "ai4bharat/Kathbath"),
    ("IndicVoices", "ai4bharat/IndicVoices"),
    ("FedMML-ED-Triage", "olaflaitinen/fedmml-ed-triage"),
]

for name, path in targets:
    print(f"\n=== Attempting Accepted Dataset: {name} ({path}) ===")
    try:
        # Pass token explicitly
        ds = load_dataset(path, streaming=True, token=hf_token)
        split = list(ds.keys())[0]
        sample = next(iter(ds[split]))
        print(f"SUCCESS: {name} loaded! Split: '{split}', Sample keys: {list(sample.keys())}")
    except Exception as e:
        print(f"FAILED: {name} — {type(e).__name__}: {e}")
