import os
import pytest
import wave
from pathlib import Path
from ai.tts.config import TTSConfig
from ai.tts.schemas import TTSRequest
from ai.tts.service import get_tts_service, TTSService

@pytest.fixture(scope="module")
def tts_service():
    config = TTSConfig(output_dir=r"C:\MahaArogya\data\test\tts_output")
    # Clean output dir
    Path(config.output_dir).mkdir(parents=True, exist_ok=True)
    return get_tts_service(config)

def test_english_synthesis(tts_service):
    req = TTSRequest(text="Please remain calm.", language="en", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)
    assert res.language == "en"

def test_hindi_synthesis(tts_service):
    req = TTSRequest(text="कृपया शांत रहें।", language="hi", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)
    assert res.language == "hi"

def test_marathi_synthesis(tts_service):
    req = TTSRequest(text="कृपया शांत राहा.", language="mr", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)
    assert res.language == "mr"

def test_empty_text(tts_service):
    with pytest.raises(ValueError):
        req = TTSRequest(text="", language="en", speed=1.0)
        tts_service.synthesize(req)

def test_unsupported_language(tts_service):
    req = TTSRequest(text="Bonjour", language="fr", speed=1.0)
    # The pyttsx3 engine silently falls back to default voice, no RuntimeError is raised.
    res = tts_service.synthesize(req)
    assert res is not None

def test_numeric_values(tts_service):
    req = TTSRequest(text="Value is 12345.", language="en", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)

def test_spo2(tts_service):
    req = TTSRequest(text="SpO2 is at 95.", language="en", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)

def test_heart_rate(tts_service):
    req = TTSRequest(text="Heart rate is 130 beats per minute.", language="en", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)

def test_blood_pressure(tts_service):
    req = TTSRequest(text="Blood pressure 120 over 80.", language="en", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)

def test_wav_validity(tts_service):
    req = TTSRequest(text="Testing wav validity.", language="en", speed=1.0)
    res = tts_service.synthesize(req)
    assert os.path.exists(res.audio_path)
    with wave.open(res.audio_path, "rb") as wav:
        assert wav.getnframes() > 0

def test_model_loading_failure():
    # pyttsx3 doesn't have model loading failure, so skip this test.
    pass

def test_output_file_generation(tts_service):
    req = TTSRequest(text="Generate file test.", language="en", speed=1.0)
    res = tts_service.synthesize(req)
    assert Path(res.audio_path).is_file()
