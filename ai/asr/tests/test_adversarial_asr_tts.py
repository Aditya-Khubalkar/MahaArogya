"""
Hard Adversarial Integration Test Suite for ASR, TTS, and Unified Voice Orchestration.
Covers 15 adversarial cases: missing audio files, 0-byte corrupt WAVs, malformed TTS transcripts,
code-switching, HTML injection, speed multiplier bounds, and end-to-end pipeline error handling.
"""

import os
import wave
import struct
import pytest
from pathlib import Path

from ai.asr.service import ASRService, get_asr_service
from ai.tts.service import TTSService, get_tts_service
from ai.tts.schemas import TTSRequest, TTSResponse
from ai.orchestrator import MahaArogyaOrchestrator


# 1. NON-EXISTENT AUDIO FILE
def test_adv_asr_01_nonexistent_audio_file():
    asr = get_asr_service()
    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        asr.transcribe("non_existent_file_path_999.wav")


# 2. ZERO-BYTE CORRUPTED WAV FILE
def test_adv_asr_02_zero_byte_corrupted_wav(tmp_path):
    corrupt_file = tmp_path / "zero_byte.wav"
    corrupt_file.write_bytes(b"")
    
    asr = get_asr_service()
    with pytest.raises(Exception):  # Expect Exception from whisper / file reader
        asr.transcribe(corrupt_file)


# 3. CORRUPTED HEADER WAV FILE
def test_adv_asr_03_corrupted_header_wav(tmp_path):
    corrupt_file = tmp_path / "corrupt_header.wav"
    corrupt_file.write_bytes(b"RIFF1234WAVEfmt BADHEADERDATA1234567890")
    
    asr = get_asr_service()
    with pytest.raises(Exception):
        asr.transcribe(corrupt_file)


# 4. EMPTY TEXT INPUT FOR TTS
def test_adv_tts_01_empty_text_input():
    tts = get_tts_service()
    with pytest.raises(ValueError, match="Text for TTS synthesis cannot be empty"):
        tts.synthesize(TTSRequest(text="", language="mr"))


# 5. WHITESPACE ONLY TEXT INPUT FOR TTS
def test_adv_tts_02_whitespace_only_text():
    tts = get_tts_service()
    with pytest.raises(ValueError, match="Text for TTS synthesis cannot be empty"):
        tts.synthesize(TTSRequest(text="   \n\t  ", language="en"))


# 6. SPECIAL CHARACTERS & HTML INJECTION IN TTS
def test_adv_tts_03_special_characters_html_injection():
    tts = get_tts_service()
    res = tts.synthesize(TTSRequest(text="<script>alert('xss');</script> !@#$%^&*()", language="en"))
    assert res.audio_path is not None
    assert Path(res.audio_path).exists()


# 7. NUMBERS ONLY TRANSCRIPT IN TTS
def test_adv_tts_04_numbers_only_transcript():
    tts = get_tts_service()
    res = tts.synthesize(TTSRequest(text="1234567890 999 000", language="en"))
    assert res.audio_path is not None
    assert Path(res.audio_path).exists()


# 8. INVALID SPEED MULTIPLIER (ZERO OR NEGATIVE)
def test_adv_tts_05_extreme_speed_multiplier_zero():
    tts = get_tts_service()
    with pytest.raises(ValueError, match="TTS speed multiplier must be greater than zero"):
        tts.synthesize(TTSRequest(text="Test speed", speed=0.0))


# 9. UNSUPPORTED LANGUAGE FALLBACK IN TTS
def test_adv_tts_06_unsupported_language_fallback():
    tts = get_tts_service()
    res = tts.synthesize(TTSRequest(text="Bonjour comment allez vous", language="fr"))
    assert res.audio_path is not None
    assert Path(res.audio_path).exists()


# 10. END-TO-END VOICE ORCHESTRATOR PIPELINE (REAL CUDA FASTER-WHISPER)
def test_adv_pipeline_01_end_to_end_voice_orchestrator():
    test_audio = Path("data/test/synthetic_test.wav")
    if not test_audio.exists():
        pytest.skip("synthetic_test.wav not present")
        
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="voice_e2e_01",
        audio_path=str(test_audio),
        language="en",
        modality="voice"
    )
    assert res.transcript_or_text != ""
    assert res.ai_response_text != ""
    assert res.audio_response_path is not None
    assert Path(res.audio_response_path).exists()


# 11. MULTILINGUAL CODE-SWITCHING PIPELINE
def test_adv_pipeline_02_multilingual_code_switching_text():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="code_switch_01",
        text_input="Majha pot dukhtay and I am experiencing severe breathlessness.",
        language="mr",
        modality="text"
    )
    assert "abdominal_pain" in res.patient_state.symptoms
    assert "breathlessness" in res.patient_state.symptoms
    assert res.triage_decision.triage_category == "EMERGENCY"


# 5 NEW CODE-SWITCHED EMERGENCY TEST CASES (DIFFERENT LANGUAGE MIXES)
def test_adv_codeswitch_01_marathi_english_cardiac():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="cs_cardiac_01",
        text_input="Majhya chhatit sharp chest pain ahe and left arm dukhatahe.",
        language="mr",
        modality="text"
    )
    assert "chest_pain" in res.patient_state.symptoms
    assert res.triage_decision.triage_category == "EMERGENCY"


def test_adv_codeswitch_02_hindi_marathi_hemorrhage():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="cs_hem_02",
        text_input="Khoon ki ulti ho rahi hai along with severe pot dukhna.",
        language="hi",
        modality="text"
    )
    assert res.triage_decision.triage_category == "EMERGENCY"


def test_adv_codeswitch_03_hinglish_english_resp():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="cs_resp_03",
        text_input="Chhatit severe pain ahe ani shwas ghyayla severe trouble hotay.",
        language="hinglish",
        modality="text"
    )
    assert res.triage_decision.triage_category == "EMERGENCY"


def test_adv_codeswitch_04_hinglish_stroke():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="cs_stroke_04",
        text_input="Sudden slurred speech ho raha hai and face per numbness feel ho raha hai.",
        language="hinglish",
        modality="text"
    )
    assert res.triage_decision.triage_category == "EMERGENCY"


def test_adv_codeswitch_05_hindi_english_pregnancy():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="cs_preg_05",
        text_input="8 weeks pregnant hu and acute severe abdominal pain ho raha hai.",
        language="hi",
        modality="text"
    )
    assert res.triage_decision.triage_category == "EMERGENCY"


# 12. EXTREMELY LONG TRANSCRIPT FOR TTS
def test_adv_pipeline_03_extremely_long_transcript_tts():
    long_text = "Patient presents with severe acute abdominal pain. " * 20
    tts = get_tts_service()
    res = tts.synthesize(TTSRequest(text=long_text, language="en"))
    assert res.audio_path is not None
    assert Path(res.audio_path).exists()


# 13. ASR EMPTY TRANSCRIPT GRADUAL FALLBACK
def test_adv_pipeline_04_asr_result_empty_transcript_handling():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="empty_trans_01",
        text_input="",
        language="mr",
        modality="text"
    )
    assert res.ai_response_text != ""
    assert res.triage_decision is not None


# 14. INVALID MODALITY PASSED TO ORCHESTRATOR
def test_adv_pipeline_05_invalid_modality_passed():
    orch = MahaArogyaOrchestrator()
    with pytest.raises(ValueError, match="Modality must be 'voice' or 'text'"):
        orch.process_turn(
            conversation_id="inv_mod_01",
            text_input="Hello",
            modality="invalid_modality"
        )


# 15. NULL INPUT AND NULL AUDIO VOICE FALLBACK
def test_adv_pipeline_06_null_input_and_null_audio():
    orch = MahaArogyaOrchestrator()
    res = orch.process_turn(
        conversation_id="null_audio_01",
        text_input=None,
        audio_path=None,
        modality="voice"
    )
    assert res.transcript_or_text != ""
    assert res.ai_response_text != ""
