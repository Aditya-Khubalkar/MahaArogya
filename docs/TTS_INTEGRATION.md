# TTS Integration Architecture - Phase 4

## Architecture Overview
The TTS Service uses a unified local interface (`synthesize`) that dynamically routes requests to the optimal offline model based on the requested language. It prevents the need to keep large neural models constantly resident in VRAM by lazy-loading them upon first request.

- **English (`en`)**: Routed to Piper TTS (`en_US-libritts-high`)
- **Hindi (`hi`)**: Routed to Piper TTS (`hi_IN-pratham-medium`)
- **Marathi (`mr`)**: Routed to `ai4bharat/IndicF5`

No translation occurs within the TTS layer. The language detected and assigned by the upstream NLP/Routing modules is strictly enforced.

## Selected Models & Licenses
| Language | Model | Architecture | License | VRAM | Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **English** | `piper: en_US-libritts-high` | VITS (ONNX) | MIT | 0 MB (CPU) | `C:\MahaArogya\models\tts\piper\en\en_US\libritts\high\en_US-libritts-high.onnx` |
| **Hindi** | `piper: hi_IN-pratham-medium` | VITS (ONNX) | MIT | 0 MB (CPU) | `C:\MahaArogya\models\tts\piper\hi\hi_IN\pratham\medium\hi_IN-pratham-medium.onnx` |
| **Marathi** | `ai4bharat/IndicF5` | CFM + Vocos | MIT | 1.36 GB (GPU) | `C:\MahaArogya\models\tts\IndicF5\` |

## Performance Benchmark Results
- **English**: Warm Latency: **0.51s** (RTF: 0.12), Cold Start: 1.63s, Success Rate: 100%
- **Hindi**: Warm Latency: **0.16s** (RTF: 0.03), Cold Start: 2.10s, Success Rate: 100%
- **Marathi**: Warm Latency: **7.06s** (RTF: 0.44 for 16.1s audio), Cold Start: 19.04s, Success Rate: 100%, VRAM: 1.36 GB

## API Interface
```python
def synthesize(self, request: TTSRequest) -> TTSResponse:
    ...
```
- **Inputs**: `text` (str), `language` (str: en, hi, mr), `speed` (float).
- **Outputs**: `audio_path` (str, absolute path to `.wav`), `duration_sec` (float), `latency_sec` (float).
- **Format**: Standard WAV format (PCM 16-bit Mono), out-of-the-box compatible with frontend audio playback.

## Error Handling & Local Verification
- **100% Offline Execution**: All models are saved locally under `C:\MahaArogya\models\tts\`.
- **No Cloud Fallback**: If an unsupported language or invalid input is provided, a controlled local exception is raised. No external or paid APIs are invoked.
