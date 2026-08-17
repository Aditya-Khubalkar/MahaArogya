from datasets import load_dataset

targets = [
    ("Kathbath", "ai4bharat/Kathbath"),
    ("IndicVoices", "ai4bharat/IndicVoices"),
    ("Nirantar", "adjaysagar/nirantar"),
    ("FedMML-ED-Triage", "olaflaitinen/fedmml-ed-triage"),
]

for name, path in targets:
    print(f"\n=== Attempting {name} ({path}) ===")
    try:
        ds = load_dataset(path, streaming=True)
        sample = next(iter(ds[list(ds.keys())[0]]))
        print(f"SUCCESS: {name} loaded without auth. Sample keys: {list(sample.keys())}")
    except Exception as e:
        print(f"FAILED: {name} — {type(e).__name__}: {e}")
