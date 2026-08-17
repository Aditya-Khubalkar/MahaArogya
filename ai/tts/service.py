"""
MahaArogya â€” Local TTS Service
Offline text-to-speech synthesis engine generating WAV responses for voice mode.
"""

import os
import re
import time
import uuid
from pathlib import Path
from typing import Optional

from ai.tts.config import TTSConfig
from ai.tts.schemas import TTSRequest, TTSResponse


class TTSService:
    _instance: Optional["TTSService"] = None

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        """
        Synthesizes text into a local WAV audio file.
        
        Args:
            request: TTSRequest containing text, language, speed

        Returns:
            TTSResponse containing generated audio_path, duration, and latency
        """
        if not request.text or not request.text.strip():
            raise ValueError("Text for TTS synthesis cannot be empty")

        if request.speed <= 0:
            raise ValueError("TTS speed multiplier must be greater than zero")

        # Sanitize HTML tags & control characters before engine synthesis
        clean_text = re.sub(r"<[^>]*>", "", request.text).strip()
        if not clean_text:
            clean_text = "Standard clinical notification."

        import pyttsx3

        start_t = time.time()
        output_filename = f"response_{uuid.uuid4().hex[:8]}.wav"
        output_path = Path(self.config.output_dir) / output_filename

        engine = pyttsx3.init()
        engine.setProperty("rate", int(self.config.speech_rate * request.speed))
        engine.setProperty("volume", self.config.volume)

        # Select matching voice if available
        try:
            voices = engine.getProperty("voices")
            selected_voice = None

            for voice in voices:
                v_name = getattr(voice, "name", "").lower()
                if request.language in ["hi", "mr"] and ("india" in v_name or "hindi" in v_name or "marathi" in v_name or "mr" in v_name or "hi" in v_name):
                    selected_voice = voice.id
                    break
                elif request.language == "en" and ("english" in v_name or "david" in v_name or "zira" in v_name or "en" in v_name):
                    selected_voice = voice.id
                    break

            if selected_voice:
                engine.setProperty("voice", selected_voice)
        except Exception:
            pass

        engine.save_to_file(clean_text, str(output_path))
        engine.runAndWait()
        engine.stop()

        latency = round(time.time() - start_t, 3)
        words = len(clean_text.split())
        est_duration = round(words / (self.config.speech_rate / 60.0), 2)

        return TTSResponse(
            audio_path=str(output_path),
            text=clean_text,
            language=request.language,
            duration_sec=max(1.0, est_duration),
            latency_sec=latency
        )


def get_tts_service(config: Optional[TTSConfig] = None) -> TTSService:
    """Singleton accessor for TTSService."""
    if TTSService._instance is None:
        TTSService._instance = TTSService(config)
    return TTSService._instance

