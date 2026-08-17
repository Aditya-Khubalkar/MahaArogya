"""
Unit tests for ASR module schemas and configuration.
"""

import pytest
from ai.asr.config import ASRConfig
from ai.asr.schemas import ASRResult, ASRSegment


def test_asr_config_defaults():
    config = ASRConfig()
    assert config.model_size == "small"
    assert config.device == "cuda"
    assert config.compute_type == "float16"


def test_asr_result_schema():
    segment = ASRSegment(
        id=0,
        seek=0,
        start=0.0,
        end=2.5,
        text="Majha pot dukhtay",
        avg_logprob=-0.25
    )
    result = ASRResult(
        transcript="Majha pot dukhtay",
        language="mr",
        language_probability=0.98,
        duration_sec=2.5,
        latency_sec=0.15,
        confidence=-0.25,
        model_name="small",
        compute_type="float16",
        device="cuda",
        segments=[segment]
    )
    assert result.language == "mr"
    assert len(result.segments) == 1
    assert result.segments[0].text == "Majha pot dukhtay"
