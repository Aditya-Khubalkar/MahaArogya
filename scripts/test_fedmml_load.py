import huggingface_hub
from datasets import load_dataset

hf_token = huggingface_hub.get_token()

print("=== DIAGNOSING FedMML-ED-Triage LOAD ===")

# Test 1: Non-streaming load
print("\n--- Test 1: Non-streaming load (load_dataset('olaflaitinen/fedmml-ed-triage')) ---")
try:
    ds = load_dataset("olaflaitinen/fedmml-ed-triage", token=hf_token)
    print("SUCCESS Non-Streaming!")
    print(ds)
except Exception as e:
    print(f"FAILED Non-Streaming — {type(e).__name__}: {e}")

# Test 2: With trust_remote_code=True
print("\n--- Test 2: trust_remote_code=True ---")
try:
    ds = load_dataset("olaflaitinen/fedmml-ed-triage", trust_remote_code=True, token=hf_token)
    print("SUCCESS with trust_remote_code!")
    print(ds)
except Exception as e:
    print(f"FAILED trust_remote_code — {type(e).__name__}: {e}")

# Test 3: Direct parquet/csv file download via hf_hub_download
print("\n--- Test 3: List files via HfApi ---")
try:
    api = huggingface_hub.HfApi()
    files = api.list_repo_files("olaflaitinen/fedmml-ed-triage", repo_type="dataset")
    print(f"SUCCESS Listing Files: {files}")
except Exception as e:
    print(f"FAILED Listing Files — {type(e).__name__}: {e}")
