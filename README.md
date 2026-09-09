# MahaArogya (Sanjeevani Grid)

> **Statewide AI-Driven Healthcare Routing, Triage, and Hospital Management Infrastructure for Maharashtra**

MahaArogya is a privacy-first, GPU-accelerated medical triage, hospital routing, OPD appointment, and bed occupancy management subsystem built to integrate with Maharashtra's public health network.

---

## ⚡ Key Features

- **Multilingual Voice & Text Intake (ASR + TTS):** GPU-accelerated speech-to-text and offline TTS supporting Marathi, Hindi, English, and Romanized Marathi (Hinglish/Marathi-English).
- **Deterministic PatientState Memory:** Non-lossy, state-machine tracking symptoms, vitals, medical history, duration, and severity across turns.
- **Safety-First Triage Engine:** 4-class classification (`ROUTINE`, `PRIORITY`, `URGENT`, `EMERGENCY`) with deterministic safety red-flag overrides.
- **Hospital Router & Smart OPD Tokens:** Haversine distance-weighted facility routing paired with QR code-enabled digital OPD tokens.
- **Offline Hospital Reception Workflow:** Patient check-in, queue status transitions, and tamper-evident audit logging.
- **CCTV Bed Occupancy Estimator:** Computer Vision bed estimation enforcing human verification flags, zero face recognition, and zero patient PII tracking.
- **Role-Based Access Control (RBAC):** Secure scoping for Government, Doctor, Nurse, and Reception personas.
- **Modern Dashboard:** Next.js 16 Glassmorphism UI featuring live patient state visualization, interactive maps, chat interface, token issuing, and reception desk queue.

---

## 🏗 System Architecture

The repository is organized into cleanly separated sub-systems:

- **`src/`**: FastAPI backend API servers, database schema, and RBAC middleware.
- **`frontend/`**: Next.js 16 React frontend for various personas (Admin, Doctor, Nurse, Patient, Government).
- **`ai/`**: AI/ML pipelines (ASR, NLP Extraction, Triage).
- **`tests/` & `evaluation/`**: Integration tests and adversarial benchmarking suites.
- **`scripts/`**: Development, training, and database management scripts.
- **`docs/`**: Comprehensive system design and audit documentation.

---

## 🚀 Quick Start

### Prerequisites

- **Python:** 3.11+
- **Node.js:** v20+
- **GPU:** NVIDIA GPU (CUDA 12.8 support recommended)

### 1. Start Backend API Server

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Start FastAPI server on port 8000
python -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```

Swagger API Documentation: **http://127.0.0.1:8000/docs**

### 2. Start Frontend Dashboard

```bash
cd frontend
npm install
npm run dev -- -p 3001
```

Dashboard available at: **http://localhost:3001**

### 3. Run Test Suite

```bash
python -m pytest ai/ src/ tests/
python evaluation/run_evaluations.py
```

---

## 🔒 Safety & Privacy Principles

1. **Zero Face Recognition / Zero Patient PII:** CCTV bed monitoring operates on bed grid occupancy estimations only. No face detection or video streams are retained.
2. **Deterministic Safety Rules:** Generative ML or classifiers MUST NOT override safety red-flag rules (e.g. chest pain, severe dyspnea, infant high fever).
3. **Non-Authoritative CCTV:** CCTV outputs are treated as estimates; discrepancies with database records mandate human physical verification.
4. **Scope Authorization:** Hospital reception cannot modify clinical triage classifications.

---

## 📄 Data Provenance

Data sources cataloged in `data/source_registry.csv` include `symptom_to_diagnosis`, `meditod`, `medquad`, `bc5cdr`, and `ncbi_disease`. All data acquisition follows licensing and regional compliance guidelines.
