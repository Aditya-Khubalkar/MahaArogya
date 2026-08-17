"""
MahaArogya — TTS Data Schemas
Pydantic data models for speech synthesis requests and responses.
"""

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    language: str = Field(default="mr", description="Language code ('mr', 'hi', 'en')")
    speed: float = Field(default=1.0, description="Speed multiplier (0.5 to 2.0)")


class TTSResponse(BaseModel):
    audio_path: str = Field(..., description="Path to generated WAV file")
    text: str = Field(..., description="Original text synthesized")
    language: str = Field(..., description="Language used")
    duration_sec: float = Field(..., description="Estimated audio duration in seconds")
    latency_sec: float = Field(..., description="Synthesis latency in seconds")
