"""
MahaArogya — ASR Data Schemas
Pydantic data models for ASR inputs, segments, and outputs.
"""

from pydantic import BaseModel, Field


class ASRSegment(BaseModel):
    id: int
    seek: int
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Segment text")
    tokens: list[int] = Field(default_factory=list)
    temperature: float = 0.0
    avg_logprob: float = 0.0
    compression_ratio: float = 0.0
    no_speech_prob: float = 0.0


class ASRResult(BaseModel):
    transcript: str = Field(..., description="Full transcribed text")
    language: str = Field(..., description="Detected or specified language code ('mr', 'hi', 'en', etc.)")
    language_probability: float = Field(default=1.0, description="Confidence in language detection")
    duration_sec: float = Field(..., description="Audio duration in seconds")
    latency_sec: float = Field(..., description="ASR processing latency in seconds")
    confidence: float = Field(..., description="Average segment log probability score")
    model_name: str = Field(..., description="Whisper model size used")
    compute_type: str = Field(..., description="Compute precision used ('float16', 'int8', etc.)")
    device: str = Field(..., description="Device used ('cuda' or 'cpu')")
    segments: list[ASRSegment] = Field(default_factory=list, description="Detailed timestamped segments")
