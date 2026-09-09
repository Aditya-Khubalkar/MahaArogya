"""
MahaArogya — TTS Configuration
Offline speech synthesis configuration for voice responses.
"""

from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

# Derive project root portably (works in Docker, Linux, Windows)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_OUTPUT_DIR = str(_PROJECT_ROOT / "data" / "processed" / "audio_responses")


class TTSConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    speech_rate: int = Field(default=160, description="Speech rate in words per minute (WPM)")
    volume: float = Field(default=1.0, description="Audio output volume (0.0 to 1.0)")
    default_language: str = Field(default="mr", description="Default response language ('mr', 'hi', 'en')")
    output_dir: str = Field(
        default=_DEFAULT_OUTPUT_DIR,
        description="Directory to save synthesized audio files"
    )

