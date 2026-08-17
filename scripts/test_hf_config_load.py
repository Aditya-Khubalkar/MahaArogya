import huggingface_hub
from datasets import load_dataset

hf_token = huggingface_hub.get_token()

print("\n=== LOADING GATED DATASETS WITH CONFIG SUBSPECIFICATION ===")

# 1. Kathbath ('marathi' config)
print("\n--- 1. Kathbath (ai4bharat/Kathbath, config='marathi') ---")
try:
    ds_kb = load_dataset("ai4bharat/Kathbath", "marathi", streaming=True, token=hf_token)
    split_kb = list(ds_kb.keys())[0]
    sample_kb = next(iter(ds_kb[split_kb]))
    print(f"SUCCESS: Kathbath loaded! Split: '{split_kb}', Sample keys: {list(sample_kb.keys())}")
except Exception as e:
    print(f"FAILED: Kathbath — {type(e).__name__}: {e}")

# 2. IndicVoices ('marathi' config)
print("\n--- 2. IndicVoices (ai4bharat/IndicVoices, config='marathi') ---")
try:
    ds_iv = load_dataset("ai4bharat/IndicVoices", "marathi", streaming=True, token=hf_token)
    split_iv = list(ds_iv.keys())[0]
    sample_iv = next(iter(ds_iv[split_iv]))
    print(f"SUCCESS: IndicVoices loaded! Split: '{split_iv}', Sample keys: {list(sample_iv.keys())}")
except Exception as e:
    print(f"FAILED: IndicVoices — {type(e).__name__}: {e}")

# 3. FedMML-ED-Triage
print("\n--- 3. FedMML-ED-Triage (olaflaitinen/fedmml-ed-triage) ---")
try:
    ds_fed = load_dataset("olaflaitinen/fedmml-ed-triage", streaming=True, token=hf_token)
    split_fed = list(ds_fed.keys())[0]
    sample_fed = next(iter(ds_fed[split_fed]))
    print(f"SUCCESS: FedMML-ED-Triage loaded! Split: '{split_fed}', Sample keys: {list(sample_fed.keys())}")
except Exception as e:
    print(f"FAILED: FedMML-ED-Triage — {type(e).__name__}: {e}")
