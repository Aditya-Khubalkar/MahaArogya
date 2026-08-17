import huggingface_hub
from datasets import load_dataset

print("=== WHOAMI OUTPUT RIGHT BEFORE DOWNLOAD ===")
try:
    user_info = huggingface_hub.whoami()
    print(user_info)
    username = user_info.get("name") if isinstance(user_info, dict) else None
    token_role = user_info.get("auth", {}).get("accessToken", {}).get("role") if isinstance(user_info, dict) else None
    token_name = user_info.get("auth", {}).get("accessToken", {}).get("displayName") if isinstance(user_info, dict) else None
    print(f"\nExtracted Username: '{username}'")
    print(f"Token Display Name: '{token_name}'")
    print(f"Token Role: '{token_role}'")
except Exception as e:
    print(f"whoami() failed: {e}")
    username = None

print("\n=== DOWNLOAD RETRY ATTEMPT ===")
targets = [
    ("Kathbath", "ai4bharat/Kathbath"),
    ("IndicVoices", "ai4bharat/IndicVoices"),
    ("FedMML-ED-Triage", "olaflaitinen/fedmml-ed-triage"),
]

for name, path in targets:
    print(f"\n=== Attempting {name} ({path}) ===")
    try:
        ds = load_dataset(path, streaming=True, token=huggingface_hub.get_token())
        split = list(ds.keys())[0]
        sample = next(iter(ds[split]))
        print(f"SUCCESS: {name} loaded! Split: '{split}', Sample keys: {list(sample.keys())}")
    except Exception as e:
        print(f"FAILED: {name} — {type(e).__name__}: {e}")
