# MahaArogya Phase 4 — Local TTS Audit

## 1. Current Environment
- **Python & Virtual Environment**: Python 3.12.0 is installed and active in `C:\MahaArogya\venv`.
- **PyTorch/CUDA Status**: PyTorch 2.11.0+cu128 is installed. CUDA is fully available.
- **GPU**: NVIDIA GeForce RTX 5060 Laptop GPU.

## 2. Existing TTS Implementation
- **Codebase**: The core TTS synthesis logic is located in `C:\MahaArogya\ai\tts\service.py` and configuration in `schemas.py` and `config.py`. 
- **Packages**: The current engine is powered by the `pyttsx3` package (version 2.99), which hooks into Windows SAPI5 offline voice synthesis.
- **Frontend**: Both `frontend` and `frontend maha` already have robust UI wiring for voice interactions. They record user audio, send it to the backend (via endpoints like `/api/conversation/voice_turn` and `/api/v1/tts/synthesize`), and then play back the returned generated WAV files using standard Web Audio/HTML5 Audio players.

## 3. Existing Models
- **ASR**: Whisper-small and several fine-tuned variations are successfully stored in `C:\MahaArogya\models\`.
- **NLP/Triage**: XGBoost, LightGBM, and other classifiers are present.
- **TTS Models**: **None.** There are currently no neural acoustic or TTS model weights (e.g., Bark, VITS, XTTS) stored in the `models\` directory.

## 4. Existing Dependencies
- The only explicitly TTS-related package in `requirements.txt` is `pyttsx3==2.99`.
- Other generic ML/audio libraries exist (e.g., `transformers`, `torchaudio`, `librosa`, `soundfile`), which will be useful for a neural TTS upgrade.

## 5. Language Support
- **Current Support**: Because `pyttsx3` relies on native OS voices, English (US/UK) works well locally. However, high-quality, native-sounding Hindi and Marathi are completely unsupported out-of-the-box unless the specific Windows language packs have been manually installed and configured by the user, and even then, they sound highly robotic. 

## 6. Local/Cloud Status
- **Current Status**: 100% Local. No cloud or paid APIs (like OpenAI, Google TTS) are being used. 

## 7. Missing Components for Phase 4
- We lack a neural text-to-speech (TTS) engine capable of natural, multilingual synthesis (English, Hindi, Marathi).
- We lack the corresponding open-source model weights.
- `ai\tts\service.py` needs to be rewritten/updated to drop `pyttsx3` and load a neural PyTorch/Transformers-based TTS pipeline instead.
- We might need a dedicated Marathi/Indic TTS model or a multilingual model that handles code-switching well.

## 8. Expected VRAM/Resource Requirements (RTX 5060 8GB)
- **Constraint**: The RTX 5060 has 8GB of VRAM. 
- Whisper-small for ASR already consumes around 1.5 - 2GB of VRAM. 
- XGBoost and other NLP models take minimal GPU memory (mostly CPU/RAM).
- **Available VRAM for TTS**: ~5GB to 6GB maximum.
- **Consideration**: We cannot use massive models like Bark out-of-the-box without aggressive quantization. We must select VRAM-friendly neural TTS models.

## 9. Recommended Local TTS Candidates
1. **Coqui XTTS v2**: Excellent multilingual support (including Hindi/English). Marathi support might require transliteration to Hindi or fine-tuning. Fits in ~2.5 - 3GB VRAM.
2. **VITS (MMS / Facebook Massively Multilingual Speech)**: Has dedicated language models for Hindi and Marathi. Very fast, very lightweight (~1GB VRAM). Sound quality is good but slightly less expressive than XTTS.
3. **Silero TTS**: Extremely lightweight and fast, but Indic language coverage is limited (has Hindi, no native Marathi).
4. **Parler-TTS**: Requires testing for Hindi/Marathi capabilities, but highly expressive.

## 10. Exact Next Step
- Determine which neural TTS model architecture (XTTSv2, VITS/MMS, etc.) we will adopt to ensure English, Hindi, and Marathi support while keeping total VRAM usage under the 8GB limit alongside Whisper.
- Download the agreed-upon model weights to `C:\MahaArogya\models\`.
- Update `requirements.txt` with any new dependencies (e.g., `TTS` or `piper-tts`).
