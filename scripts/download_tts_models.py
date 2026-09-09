import os
from huggingface_hub import hf_hub_download

MODELS_DIR = r"C:\MahaArogya\models\tts"
os.makedirs(MODELS_DIR, exist_ok=True)

piper_files = [
    ("rhasspy/piper-voices", "en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx"),
    ("rhasspy/piper-voices", "en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx.json"),
    ("rhasspy/piper-voices", "hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx"),
    ("rhasspy/piper-voices", "hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx.json")
]

print("Downloading Piper models...")
for repo_id, filename in piper_files:
    try:
        path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=MODELS_DIR)
        print(f"Downloaded {filename} to {path}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print("Checking IndicF5 config download...")
try:
    path = hf_hub_download(repo_id="ai4bharat/IndicF5", filename="config.json", local_dir=MODELS_DIR)
    print(f"Downloaded IndicF5 config.json to {path}")
except Exception as e:
    print(f"Error downloading IndicF5 config: {e}")
