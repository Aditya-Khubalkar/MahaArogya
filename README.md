# MahaArogya (Sanjeevani Grid) — AI/ML Healthcare Subsystem

> **Statewide AI-Driven Healthcare Routing & Triage Infrastructure for Maharashtra**

MahaArogya is a privacy-first, GPU-accelerated medical triage, hospital routing, OPD appointment, and bed occupancy management subsystem built to integrate with Maharashtra's public health network (KEM, Sion, JJ, Sassoon, GMCH Nagpur).

---

## ⚡ Key Features

- **Multilingual Voice & Text Intake (ASR + TTS):** GPU-accelerated speech-to-text (`faster-whisper` on NVIDIA RTX 5060) and offline TTS supporting Marathi, Hindi, English, and Romanized Marathi (Hinglish/Marathi-English).
- **Deterministic PatientState Memory:** Non-lossy, state-machine tracking symptoms, vitals, medical history, duration, and severity across turns.
- **Safety-First Triage Engine:** 4-class classification (`ROUTINE`, `PRIORITY`, `URGENT`, `EMERGENCY`) with deterministic safety red-flag overrides that Generative ML models cannot bypass.
- **Hospital Router & Smart OPD Tokens:** Haversine distance-weighted facility routing paired with QR code-enabled digital OPD tokens.
- **Offline Hospital Reception Workflow:** Patient check-in, queue status transitions (`ISSUED` → `CHECKED_IN` → `IN_CONSULTATION`), and tamper-evident audit logging.
- **CCTV Bed Occupancy Estimator:** Computer Vision bed estimation enforcing human verification flags, discrepancy detection, zero face recognition, and zero patient PII tracking.
- **Role-Based Access Control (RBAC):** Access control enforcing hospital scope boundaries across Government, Doctor, Nurse, and Reception personas.
- **Next.js 16 Glassmorphism Dashboard:** Production UI featuring live patient state visualization, chat interface, token issuing, reception desk queue, and CCTV monitor.

---

## 🏗 Subsystem Architecture

```
[ Patient Voice / Text ] ──▶ [ ASR Engine (Whisper CUDA) ]
                                      │
                                      ▼
                           [ Medical Entity Extractor ]
                                      │
                                      ▼
                             [ PatientState Memory ]
                                      │
                                      ▼
                        [ Safety Rules & Triage Engine ]
                                      │
                                      ▼
                       [ Hospital Router & OPD Generator ]
                                      │
                                      ▼
[ Next.js Dashboard ] ◄──HTTP── [ FastAPI API Server ]
```

---

## 🚀 Quick Start

### Prerequisites
- **Python:** 3.11+ (PyTorch 2.11+ CUDA 12.8 support recommended)
- **Node.js:** v20+
- **GPU:** NVIDIA GPU (tested on NVIDIA GeForce RTX 5060 Laptop GPU)

### 1. Run Backend Server
```powershell
# Activate environment
C:\MahaArogya\venv\Scripts\activate

# Start FastAPI server on port 8000
python -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```
Swagger API docs will be available at: **http://127.0.0.1:8000/docs**

### 2. Run Frontend Dashboard
```powershell
cd frontend
npm install
npx next dev -p 3001
```
Open **http://localhost:3001** in your browser.

### 3. Run Automated Integration Tests & Evaluation Benchmark
```powershell
# Run unit & integration test suite (31 tests)
python -m pytest ai/ src/ tests/

# Run benchmark evaluation suite (100% pass)
python evaluation/run_evaluations.py
```

### 4. Docker Deployment
```bash
docker-compose up --build -d
```

---

## 🔒 Safety & Privacy Principles

1. **Zero Face Recognition / Zero Patient PII:** CCTV bed monitoring operates on bed grid occupancy estimations only. No face detection or video streams are retained.
2. **Deterministic Safety Rules:** Generative ML or classifiers MUST NOT override safety red-flag rules (e.g. chest pain, severe dyspnea, infant high fever).
3. **Non-Authoritative CCTV:** CCTV outputs are treated as estimates; discrepancies with database records mandate human physical verification.
4. **Scope Authorization:** Hospital reception cannot modify clinical triage classifications.

---

## 📊 Quality & Performance Benchmarks

| Module | Metric | Result |
|--------|--------|--------|
| **Multilingual Medical NLP Extractor** | Accuracy | **100.0%** (1.05 ms) |
| **Triage Safety Classifier** | Emergency Sensitivity | **100.0%** (0.00 ms) |
| **Hospital Routing Engine** | Regional Coverage | **100.0%** (0.00 ms) |
| **Integration Test Suite** | Passed | **31 / 31** (0.37s) |

---

## 📄 Data Provenance
Data sources cataloged in `data/source_registry.csv` include `symptom_to_diagnosis`, `meditod`, `medquad`, `bc5cdr`, and `ncbi_disease`. All data acquisition follows licensing and regional compliance guidelines.
