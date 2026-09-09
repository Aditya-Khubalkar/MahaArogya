from huggingface_hub import HfApi

api = HfApi()

models_to_check = [
    "facebook/mms-tts-hin",
    "facebook/mms-tts-mar"
]

print("--- Checking MMS Models ---")
for m in models_to_check:
    info = api.model_info(m)
    license_val = info.cardData.get("license", "Unknown") if info.cardData else "Unknown"
    print(f"{m}: License = {license_val}")

print("--- Searching for IndicF5 ---")
search_results = api.list_models(search="IndicF5", limit=5)
for m in search_results:
    info = api.model_info(m.id)
    license_val = info.cardData.get("license", "Unknown") if info.cardData else "Unknown"
    print(f"{m.id}: License = {license_val}")
