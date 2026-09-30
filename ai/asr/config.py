"""
MahaArogya — ASR Configuration
Optimized for local inference on NVIDIA RTX 5060 (8GB VRAM).
"""

import os
from pydantic import BaseModel, Field, ConfigDict


class ASRConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Model size options: 'tiny', 'base', 'small', 'medium', 'large-v3'
    model_size: str = Field(default="large-v3", description="Whisper model size")
    device: str = Field(default="cuda", description="Inference device: 'cuda' or 'cpu'")
    compute_type: str = Field(default="int8_float16", description="Compute type: 'float16', 'int8_float16', or 'int8'")
    
    # Language options
    default_language: str | None = Field(default=None, description="Language code ('mr', 'hi', 'en') or None for auto-detection")
    beam_size: int = Field(default=5, description="Beam size for decoding")
    vad_filter: bool = Field(default=True, description="Enable Voice Activity Detection filter")
    
    # Paths
    download_root: str = Field(
        default="models/whisper",
        description="Directory to cache model weights"
    )
