import os
from huggingface_hub import snapshot_download, hf_hub_download

MODELS_DIR = r"C:\MahaArogya\models\tts"
os.makedirs(MODELS_DIR, exist_ok=True)

piper_dir = os.path.join(MODELS_DIR, "piper")
os.makedirs(piper_dir, exist_ok=True)

indic_dir = os.path.join(MODELS_DIR, "IndicF5")
os.makedirs(indic_dir, exist_ok=True)

print("Downloading Piper English voice...")
hf_hub_download(repo_id="rhasspy/piper-voices", filename="en/en_US/libritts/high/en_US-libritts-high.onnx", local_dir=piper_dir)
hf_hub_download(repo_id="rhasspy/piper-voices", filename="en/en_US/libritts/high/en_US-libritts-high.onnx.json", local_dir=piper_dir)

print("Downloading Piper Hindi voice...")
hf_hub_download(repo_id="rhasspy/piper-voices", filename="hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx", local_dir=piper_dir)
hf_hub_download(repo_id="rhasspy/piper-voices", filename="hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx.json", local_dir=piper_dir)

print("Downloading IndicF5...")
snapshot_download(repo_id="ai4bharat/IndicF5", local_dir=indic_dir, ignore_patterns=["*.git*"])

print("All models downloaded successfully.")
