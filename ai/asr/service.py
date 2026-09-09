"""
MahaArogya — Local ASR Service
Powered by faster-whisper on NVIDIA RTX 5060 (8GB VRAM).
Supports Marathi, Hindi, English, Hinglish, and Code-Switching.
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Optional

from ai.asr.config import ASRConfig
from ai.asr.schemas import ASRResult, ASRSegment

_asr_lock = threading.Lock()


class ASRService:
    _instance: Optional["ASRService"] = None

    def __init__(self, config: Optional[ASRConfig] = None):
        self.config = config or ASRConfig()
        self.model = None
        self._model_lock = threading.Lock()

    def _load_model(self):
        """Lazy loader for faster-whisper model on GPU/CPU."""
        if self.model is not None:
            return

        with self._model_lock:
            if self.model is not None:
                return

            from faster_whisper import WhisperModel

            os.makedirs(self.config.download_root, exist_ok=True)

            logging.info(f"[ASRService] Loading Whisper '{self.config.model_size}' model...")
            logging.info(f"             Device: {self.config.device} | Precision: {self.config.compute_type}")

            start_t = time.time()
            self.model = WhisperModel(
                self.config.model_size,
                device=self.config.device,
                compute_type=self.config.compute_type,
                download_root=self.config.download_root
            )
            elapsed = time.time() - start_t
            logging.info(f"[ASRService] Model loaded successfully in {elapsed:.2f}s")

    def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        beam_size: Optional[int] = None
    ) -> ASRResult:
        """
        Transcribe an audio file into text with timing & language metadata.
        
        Args:
            audio_path: Path to input audio file (.wav, .mp3, .flac, .m4a)
            language: Forced language code ('mr', 'hi', 'en') or None for auto-detect
            beam_size: Beam search size (defaults to config beam_size)

        Returns:
            ASRResult containing transcript, segments, latency, and confidence
        """
        if self.model is None:
            self._load_model()

        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        lang = language or self.config.default_language
        beam = beam_size or self.config.beam_size

        start_t = time.time()

        segments_raw, info = self.model.transcribe(
            str(audio_path),
            language=lang,
            beam_size=beam,
            vad_filter=self.config.vad_filter
        )

        segments_list = []
        full_text_parts = []
        logprobs = []

        for seg in segments_raw:
            full_text_parts.append(seg.text.strip())
            logprobs.append(seg.avg_logprob)
            segments_list.append(
                ASRSegment(
                    id=seg.id,
                    seek=seg.seek,
                    start=round(seg.start, 2),
                    end=round(seg.end, 2),
                    text=seg.text.strip(),
                    temperature=seg.temperature,
                    avg_logprob=round(seg.avg_logprob, 4),
                    compression_ratio=round(seg.compression_ratio, 2),
                    no_speech_prob=round(seg.no_speech_prob, 4)
                )
            )

        latency = round(time.time() - start_t, 3)
        full_transcript = " ".join(full_text_parts).strip()
        avg_confidence = round(sum(logprobs) / len(logprobs), 4) if logprobs else 0.0

        return ASRResult(
            transcript=full_transcript,
            language=info.language,
            language_probability=round(info.language_probability, 4),
            duration_sec=round(info.duration, 2),
            latency_sec=latency,
            confidence=avg_confidence,
            model_name=self.config.model_size,
            compute_type=self.config.compute_type,
            device=self.config.device,
            segments=segments_list
        )


def get_asr_service(config: Optional[ASRConfig] = None) -> ASRService:
    """Singleton accessor for ASRService."""
    if ASRService._instance is None:
        with _asr_lock:
            if ASRService._instance is None:
                ASRService._instance = ASRService(config)
    return ASRService._instance
