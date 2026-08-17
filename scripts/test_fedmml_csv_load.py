import huggingface_hub
from datasets import load_dataset

hf_token = huggingface_hub.get_token()

print("=== TESTING DIRECT CSV LOAD FOR FedMML-ED-Triage ===")
try:
    csv_file = huggingface_hub.hf_hub_download(
        repo_id="olaflaitinen/fedmml-ed-triage",
        filename="fedmml_ed_triage_dataset.csv",
        repo_type="dataset",
        token=hf_token
    )
    print(f"Downloaded CSV to local cache: {csv_file}")
    
    ds = load_dataset("csv", data_files=csv_file)
    split = list(ds.keys())[0]
    sample = ds[split][0]
    print(f"SUCCESS: FedMML-ED-Triage loaded via CSV! Split: '{split}', Rows: {len(ds[split])}, Sample keys: {list(sample.keys())}")
except Exception as e:
    print(f"FAILED Direct CSV Load — {type(e).__name__}: {e}")
