from huggingface_hub import HfApi, hf_hub_download
import sys

api = HfApi()
try:
    info = api.model_info('ai4bharat/IndicF5')
    print('ACCESS_GRANTED')
    sys.exit(0)
except Exception as e:
    print('ACCESS_DENIED:', e)
    sys.exit(1)
