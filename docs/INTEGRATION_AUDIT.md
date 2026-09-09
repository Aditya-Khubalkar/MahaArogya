# MAHAAROGYA — FULL INTEGRATION AUDIT
**Date:** 2026-08-18  
**Audit Type:** Read-Only — Phase 1 of Integration  
**Auditor:** Antigravity AI Integration Agent  

---

## EXECUTIVE SUMMARY

Two independent MahaArogya systems exist:

| System | Location | Stack | Status |
|--------|----------|-------|--------|
| **RTX 5060** | `C:\MahaArogya\` | Python/FastAPI + Next.js | ✅ Validated, 18/18 tests pass |
| **RTX 3050 (Python)** | `C:\MahaArogya\integration\rtx3050\Projects\Projects\mahaarogya\` | Python/FastAPI + Next.js | ✅ 87 tests pass, production-complete |
| **RTX 3050 (NestJS)** | `C:\MahaArogya\integration\rtx3050\Projects\Projects\mahaaarogya backend\` | NestJS/TypeScript + Prisma | ⚠️ MOCK AI mode — real AI NOT connected |

**Integration Goal:** Merge into ONE working application where:
- 5060 provides the validated Medical AI pipeline (ASR/NLP/Triage/TTS/Safety)
- 3050 provides the validated hospital workflow backend (RBAC, OPD, Reception, Nurse, Doctor, CCTV, DB persistence, NestJS)

---

## ARCHITECTURE ANALYSIS

### RTX 5060 System Architecture
```
C:\MahaArogya\
├── api/                    FastAPI (port 8000) — text/voice endpoints
│   ├── routers/
│   │   ├── text.py         POST /api/v1/text/turn
│   │   └── voice.py        POST /api/v1/voice/turn
├── ai/
│   ├── orchestrator.py     MahaArogyaOrchestrator (unified pipeline)
│   ├── asr/service.py      faster-whisper (fine-tuned multilingual)
│   ├── nlp/extractor.py    MedicalExtractor (17,841 bytes — comprehensive)
│   ├── nlp/language_detector.py
│   ├── patient_state/      PatientStateManager + PatientState schemas
│   ├── questions/selector.py  QuestionSelector (v2 ranker model)
│   ├── triage/
│   │   ├── classifier.py   TriageClassifier (safety + ML + remote 3050)
│   │   ├── safety_rules.py SafetyRuleEngine (13,098 bytes — 15+ rules)
│   │   ├── ml_classifier.py MLTriageClassifier (XGBoost/LightGBM)
│   │   └── remote_3050_client.py Remote3050InferenceClient
│   ├── routing/router.py   HospitalRouter
│   ├── tts/service.py      TTS (Piper ONNX — EN/HI/MR)
│   └── cv/occupancy.py     CCTV occupancy (stub)
├── models/
│   ├── triage_classifier/  XGBoost model artifacts
│   ├── triage_xgboost_baseline/
│   ├── triage_lightgbm_baseline/
│   ├── whisper_finetuned_v2_full/   Fine-tuned Whisper (multilingual)
│   ├── question_ranker_v2/
│   ├── extraction_classifier/
│   └── tts/                Piper ONNX models (EN/HI/MR)
├── frontend/               Next.js (port 3000)
│   └── app/                conversation, cctv, dashboard, doctor, nurse, reception, opd
└── tests/                  18 tests (all passing)
```

### RTX 3050 Python Backend Architecture
```
C:\MahaArogya\integration\rtx3050\Projects\Projects\mahaarogya\
├── backend/
│   ├── main.py             FastAPI (port 8001) — comprehensive hospital API
│   │   ├── /auth/login     JWT-based auth
│   │   ├── /hospitals      Hospital listing + recommendations
│   │   ├── /reception/     Queue, check-in, no-show
│   │   ├── /nurse/         Ward patients
│   │   ├── /doctor/        Consultation start/complete
│   │   ├── /admin/         Overview, performance, resources, analytics
│   │   ├── /district/      District aggregate
│   │   ├── /gov/           State aggregate
│   │   ├── /cctv/          Cameras, snapshot, confirm, discrepancies
│   │   ├── /asr/transcribe ASR endpoint
│   │   ├── /tts/speak      TTS endpoint
│   │   └── /conversation/  Conversation start/turn (voice)
│   └── auth.py             DB-backed JWT, RBAC with DB permission check
├── ai/
│   ├── orchestrator.py     ConversationOrchestrator (PostgreSQL persistence)
│   ├── asr/asr_engine.py   ASREngine (faster-whisper small CUDA)
│   ├── tts/tts_engine.py   TTSEngine (Piper ONNX EN/HI)
│   ├── nlp/extractor.py    Basic keyword extractor (smaller than 5060)
│   ├── patient_state/      PatientState dataclass (list-based symptoms)
│   ├── triage/
│   │   ├── safety_rules.py 5 rules (simpler than 5060's 15+ rules)
│   │   └── triage_engine.py compute_triage function
│   ├── routing/
│   │   ├── hospitals.py    HOSPITALS list (4 Nagpur hospitals)
│   │   ├── router.py       rank_hospitals function
│   │   └── token_generator.py issue_token (PostgreSQL)
│   ├── questions/          question_bank + selector
│   ├── cv/occupancy_engine.py  YOLOv8n CCTV (REAL — camera or synthetic fallback)
│   └── forecasting/        OPD analytics
├── migrations/
│   ├── 001_full_persistence_schema.sql  15+ tables in PostgreSQL
│   └── 002_cctv_and_resources.sql       CCTV + resource tables
├── frontend/               Next.js (port 3000) — 11 pages
│   └── app/  admin, analytics, cctv, district, doctor, find-hospital, gov, 
│             login, nurse, reception, resources
└── tests/                  87 tests (all passing)
    ├── test_api.py          API + RBAC tests
    ├── test_nlp_extractor.py
    ├── test_routing.py
    ├── test_safety_rules.py
    └── test_triage_engine.py
```

### RTX 3050 NestJS Backend Architecture
```
C:\MahaArogya\integration\rtx3050\Projects\Projects\mahaaarogya backend\
├── src/
│   ├── main.ts             NestJS (port 4000)
│   ├── ai/                 AI module — MockAIService (MOCK mode, no real AI)
│   │   ├── ai.interface.ts  AIServiceInterface (transcribe, triage, synthesizeSpeech)
│   │   ├── ai-conversation.service.ts
│   │   └── mock-ai.service.ts  ← MOCK — keyword-based, not real ML
│   ├── auth/               JWT auth with guards
│   ├── cctv/               CCTV service (MOCK mode)
│   ├── realtime/           Socket.IO gateway
│   ├── hospitals/          Hospital management
│   ├── appointments/       OPD appointments
│   ├── beds/               Bed management
│   ├── emergency/          Emergency routing
│   ├── analytics/          Dashboard analytics
│   ├── notifications/      In-app notifications
│   └── audit/              Audit logs
└── prisma/schema.prisma    Comprehensive Prisma schema (1064 lines)
                            DB: mahaarogya_nest (SEPARATE from mahaarogya)
```

---

## COMPONENT CLASSIFICATION

### AI Pipeline Components

| Component | 5060 | 3050 Python | 3050 NestJS | Classification | Integration Role |
|-----------|------|-------------|-------------|----------------|-----------------|
| **ASR (Speech-to-Text)** | ✅ fine-tuned Whisper multilingual v2 | ✅ faster-whisper small | ⚠️ MOCK | **5060 WINS** — use 5060's fine-tuned model |
| **Language Detection** | ✅ dedicated language_detector.py | Implicit via Whisper | None | **5060 WINS** |
| **NLP/Medical Extractor** | ✅ 17KB comprehensive (SpO2, vitals, multi-lang) | ⚠️ 2KB basic keyword | MOCK | **5060 WINS** — 10x more capability |
| **PatientState** | ✅ Pydantic schemas (vitals, answers, age) | ✅ Dataclass (simpler) | ✅ Prisma model | **5060 WINS** — richer, compatible |
| **SafetyRuleEngine** | ✅ 15+ rules, deterministic | ✅ 5 rules, deterministic | MOCK | **5060 WINS** — more comprehensive |
| **Triage Classifier** | ✅ Safety + XGBoost/LightGBM + Remote3050 | ✅ Safety + heuristic | MOCK | **5060 WINS** |
| **TTS** | ✅ Piper EN/HI/MR (8356 bytes service) | ✅ Piper EN (831 bytes) | MOCK | **5060 WINS** — Marathi support |
| **Question Selector** | ✅ ML ranker v2 | ✅ Rule-based | None | **5060 WINS** |
| **Hospital Routing** | ✅ HospitalRouter with lat/lon | ✅ rank_hospitals functional | MOCK | **COMPATIBLE** — same hospital data |
| **CCTV/CV** | ✅ occupancy.py (basic stub) | ✅ YOLOv8n REAL camera | MOCK | **3050 WINS** — real YOLO implementation |
| **Forecasting** | None | ✅ OPD analytics | ✅ Analytics module | **3050 WINS** |

### Backend/API Components

| Component | 5060 FastAPI | 3050 FastAPI | 3050 NestJS | Classification | Integration Role |
|-----------|-------------|--------------|-------------|----------------|-----------------|
| **Auth/RBAC** | None | ✅ JWT + DB RBAC (7 roles) | ✅ JWT + Guards (9 roles) | **3050 FastAPI WINS** (simpler, validated) |
| **Reception** | None | ✅ Queue, check-in, no-show | ✅ Full module | **3050 FastAPI WINS** — tested |
| **Nurse** | None | ✅ Ward patients | ✅ Full module | **3050 FastAPI WINS** |
| **Doctor** | None | ✅ Consultation start/complete | ✅ Full module | **3050 FastAPI WINS** |
| **Admin Dashboard** | None | ✅ Overview + performance | ✅ Analytics | **3050 FastAPI WINS** |
| **CCTV API** | Basic stub | ✅ Complete (cameras, snapshot, confirm, discrepancies) | MOCK | **3050 FastAPI WINS** |
| **OPD Token** | None | ✅ PostgreSQL sequential | ✅ Prisma model | **3050 FastAPI WINS** |
| **Hospital Visits** | None | ✅ Full lifecycle | ✅ Appointments | **3050 FastAPI WINS** |
| **Gov/District** | None | ✅ Aggregate endpoints | ✅ Analytics | **3050 FastAPI WINS** |
| **WebSocket/Realtime** | None | ✅ WebSocket per hospital | ✅ Socket.IO gateway | **3050 FastAPI WINS** — Redis-backed |
| **Database Persistence** | SQLite (.db file) | ✅ PostgreSQL (15+ tables) | ✅ PostgreSQL Prisma | **3050 FastAPI WINS** |

### Frontend Components

| Page | 5060 Frontend | 3050 Python Frontend | 3050 NestJS Frontend | Integration Role |
|------|--------------|---------------------|---------------------|-----------------|
| Patient Conversation | ✅ /conversation | ✅ / (root page) | Via NestJS frontend | **3050 Python WINS** — more complete |
| Hospital Map | ✅ /conversation result | ✅ /find-hospital (Leaflet) | ✅ /find-hospital | **3050 Python WINS** |
| Reception | ✅ /reception | ✅ /reception | ✅ via NestJS | **3050 Python WINS** — complete |
| Nurse | ✅ /nurse | ✅ /nurse | ✅ via NestJS | **3050 Python WINS** |
| Doctor | ✅ /doctor | ✅ /doctor | ✅ via NestJS | **3050 Python WINS** |
| Admin | None | ✅ /admin + /resources + /analytics | ✅ via NestJS | **3050 Python WINS** |
| CCTV | ✅ /cctv | ✅ /cctv (full discrepancy UI) | MOCK | **3050 Python WINS** |
| Dashboard | ✅ /dashboard | ✅ /analytics + /district + /gov | ✅ Analytics | **3050 Python WINS** |

---

## CONFLICTS AND GAPS IDENTIFIED

### CRITICAL CONFLICTS

| # | Conflict | Description | Resolution |
|---|----------|-------------|------------|
| C1 | **Duplicate ASR** | 5060 has fine-tuned multilingual Whisper; 3050 has base Whisper small | Use 5060 ASR; 3050 backend calls 5060 API |
| C2 | **Duplicate NLP** | 5060 has comprehensive extractor; 3050 has basic extractor | Use 5060 NLP only |
| C3 | **Duplicate Safety Engine** | 5060 has 15+ rules; 3050 has 5 rules | Use 5060 engine only (safety must not be split) |
| C4 | **Duplicate PatientState** | 5060 Pydantic schema (rich); 3050 dataclass (simple) | Use 5060 as canonical; 3050 backend reads via API |
| C5 | **Duplicate TTS** | 5060 has EN/HI/MR; 3050 has EN/HI only | Use 5060 TTS |
| C6 | **Port conflict** | 5060 FastAPI on 8000; 3050 FastAPI on 8001; NestJS on 4000; frontends on 3000 | Separate ports, unified frontend |
| C7 | **Separate databases** | 3050 uses `mahaarogya` (psycopg2); NestJS uses `mahaarogya_nest` (Prisma) | Use `mahaarogya` for hospital workflow; 5060 adds session tables |
| C8 | **NestJS AI is MOCK** | NestJS MockAIService has no real ML | Replace with HTTP adapter calling 5060 FastAPI |
| C9 | **Frontend duplication** | Two Next.js frontends with overlapping pages | Use 3050 Python frontend (more complete) as primary |

### MISSING IN 5060 (provided by 3050)
- Full RBAC + JWT auth
- Reception/Nurse/Doctor endpoints
- CCTV full API (snapshot, confirm, discrepancies)
- OPD token persistence
- Hospital visit lifecycle
- Gov/District aggregate endpoints
- PostgreSQL persistence for all hospital workflow
- WebSocket/Realtime for queue updates
- OPD analytics + forecasting
- Map/Leaflet integration
- Admin resource management

### MISSING IN 3050 PYTHON (provided by 5060)
- Advanced multilingual NLP (comprehensive extractor)
- Comprehensive SafetyRuleEngine (15+ rules vs 5)
- ML-based triage (XGBoost/LightGBM trained models)
- Fine-tuned Whisper (multilingual v2)
- TTS for Marathi
- Multi-turn PatientState memory with vitals
- Question ranker v2 ML model
- Remote3050InferenceClient (already present — awaiting real 3050 endpoint)

### MISSING IN BOTH (gaps to fill)
- No actual NestJS-to-5060-FastAPI bridge (NestJS AI is MOCK, needs real connector)
- Voice endpoint schema mismatch in 5060 (`conversation_id` vs `session_id`) — known bug
- No QR code generation for tokens (referenced in spec but not implemented)
- No nurse vitals input endpoint (vitals mentioned but not as API endpoint)

---

## INTEGRATION ARCHITECTURE DECISION

### Chosen Integration Strategy: **3050 FastAPI Backend as Primary + 5060 AI Service**

```
UNIFIED MAHAAROGYA APPLICATION
================================

Patient Browser (port 3000) — Next.js
    |
    ├── AI Conversation ──────► 5060 AI FastAPI (port 8000)
    │   /api/v1/text/turn            Medical AI Pipeline
    │   /api/v1/voice/turn           ASR → NLP → PatientState
    │                                SafetyRuleEngine → Triage
    │                                Hospital Routing → TTS
    │
    └── Hospital Workflow ────► 3050 FastAPI Backend (port 8001)
        /auth/login                  JWT/RBAC
        /hospitals                   Hospital listing
        /reception/*                 Reception workflow
        /nurse/*                     Nurse workflow
        /doctor/*                    Doctor workflow
        /admin/*                     Admin dashboard
        /district/ + /gov/           Gov aggregate
        /cctv/*                      CCTV + YOLOv8n (REAL camera)
        /conversation/turn           Voice conversation (calls 5060 ASR)
        WebSocket /ws/queue          Realtime updates

3050 FastAPI Backend ─────────► 5060 AI FastAPI (port 8000)
    /conversation/turn              [calls 5060 ASR]
    /asr/transcribe                 [proxies to 5060]
    /tts/speak                      [proxies to 5060]

5060 TriageClassifier ────────► 3050 Backend (CCTV inference service)
    Remote3050InferenceClient        POST /api/v1/triage/predict
    (env: MAHAAROGYA_3050_HOST)      (needs adapter endpoint on 3050)

NestJS Backend (port 4000) — SECONDARY (Prisma schema reference only)
    Can be kept running for Swagger docs / future use
    Not primary integration target — too many MOCK dependencies
```

---

## COMPONENT STATUS MATRIX

| Component | Status | System | Notes |
|-----------|--------|--------|-------|
| Medical AI pipeline (ASR/NLP/Triage/TTS) | **WORKING** | 5060 | Fine-tuned, tested |
| SafetyRuleEngine (emergency) | **WORKING** | 5060 | 15+ rules, deterministic |
| PatientState memory | **WORKING** | 5060 | Multi-turn, vitals |
| CCTV YOLOv8n detection | **WORKING** | 3050 | Real camera + synthetic fallback |
| Hospital RBAC auth | **WORKING** | 3050 | DB-backed, 7 roles, 87 tests |
| Reception workflow | **WORKING** | 3050 | Queue, check-in, no-show |
| Doctor consultation | **WORKING** | 3050 | Start/complete lifecycle |
| OPD token persistence | **WORKING** | 3050 | PostgreSQL sequential |
| WebSocket/Realtime | **WORKING** | 3050 | Redis-backed |
| Hospital frontend | **WORKING** | 3050 | 11 pages Next.js |
| 5060→3050 remote client | **COMPATIBLE** | 5060 | Awaits 3050 adapter endpoint |
| NestJS AI service | **NEEDS ADAPTER** | NestJS | MOCK — replace with HTTP adapter |
| Voice endpoint schema | **CONFLICT** | 5060 | `conversation_id` vs `session_id` |
| PostgreSQL schema | **COMPATIBLE** | 3050 | Migrations ready |
| QR code generation | **MISSING** | Both | To be created as new adapter |
| Nurse vitals input | **MISSING** | Both | No dedicated vitals API endpoint |
| Triage predict endpoint on 3050 | **MISSING** | 3050 | Needed for remote client |

---

## FILES THAT MUST NOT BE MODIFIED (Validated)

### 5060 (DO NOT OVERWRITE):
- `ai/triage/safety_rules.py` — Emergency safety engine
- `ai/triage/classifier.py` — Triage classifier
- `ai/nlp/extractor.py` — Comprehensive NLP extractor
- `ai/patient_state/schemas.py` — PatientState schemas
- `ai/asr/service.py` — Fine-tuned Whisper service
- `ai/tts/service.py` — Multilingual TTS service
- `models/` — All trained model artifacts
- `tests/` — All 18 validated tests

### 3050 (DO NOT OVERWRITE):
- `backend/main.py` — Complete FastAPI backend (1046 lines)
- `backend/auth.py` — RBAC auth
- `ai/cv/occupancy_engine.py` — YOLOv8n CCTV
- `migrations/*.sql` — Database schemas
- `tests/` — All 87 validated tests
- `yolov8n.pt` — YOLO model artifact

---

## INTEGRATION WORK PLAN

### Phase 3: Integration Architecture
1. Create `C:\MahaArogya\integration\bridge\` directory
2. Create `5060_api_adapter.py` — adds `/api/v1/triage/predict` endpoint to expose 5060 as remote inference node
3. Create environment configuration linking both systems

### Phase 4-6: Medical AI + Hospital Flow
4. Fix voice endpoint schema mismatch (minor — align `conversation_id`)
5. Verify 3050 backend calls 5060 for ASR/TTS
6. Connect AI triage output → hospital routing → OPD token (3050 already has this)

### Phase 7: Map/Routing
7. Frontend already uses Leaflet + OSM — verify connection to routing output

### Phase 8: RBAC
8. Verify all 3050 backend protected endpoints enforce RBAC

### Phase 9: Realtime
9. Verify WebSocket broadcasts on check-in, consultation events

### Phase 10: CCTV
10. Verify YOLOv8n loads from correct path (`yolov8n.pt`)
11. Add CCTV inference endpoint if needed for remote 3050 client

### Phase 12: Database
12. Run migrations on PostgreSQL `mahaarogya` database
13. Seed demo data

### Phase 13: Dependencies
14. Ensure 5060 venv has: fastapi, faster-whisper, piper-tts, sqlalchemy, psycopg2, redis
15. Ensure 3050 venv has: fastapi, faster-whisper, piper-tts, ultralytics, sqlalchemy, redis

### Phase 14: Testing
16. Run all 18 + 87 tests
17. Run integration tests

---

## PORT ALLOCATION

| Service | Port | System |
|---------|------|--------|
| 5060 AI FastAPI | 8000 | RTX 5060 |
| 3050 Hospital FastAPI | 8001 | RTX 3050 (currently on 8001) |
| NestJS Backend | 4000 | RTX 3050 (reference only) |
| 3050 Next.js Frontend | 3000 | RTX 3050 (primary frontend) |
| PostgreSQL | 5432 | Shared |
| Redis | 6379 | Shared (3050 backend) |

---

## KNOWN RISKS

| Risk | Severity | Mitigation |
|------|----------|------------|
| YOLOv8n model path (`yolov8n.pt`) relative to working directory | HIGH | Configure absolute path or copy to standard location |
| Piper TTS model paths in 3050 backend (relative to root) | HIGH | Verify paths match actual model locations |
| PostgreSQL connection string mismatch | HIGH | Standardize DATABASE_URL across both systems |
| Redis required for 3050 backend realtime | MEDIUM | Ensure Redis running on port 6379 |
| 3050 backend imports from `ai/` using `sys.path.append` | MEDIUM | Path must be correct relative to working directory |
| 5060 voice endpoint `conversation_id` vs `session_id` | LOW | Simple schema fix needed |
| NestJS Prisma schema (mahaarogya_nest DB) conflict | LOW | Keep as separate database, not merged |

---

## DEFINITION: WHAT "INTEGRATION" MEANS

The integrated application will:
1. Use **5060's AI pipeline** for all medical intelligence (ASR, NLP, safety, triage, TTS)
2. Use **3050's FastAPI backend** for all hospital workflow (RBAC, OPD, reception, nurse, doctor, CCTV, realtime)
3. Use **3050's PostgreSQL schema** (`mahaarogya` database) for all persistence
4. Use **3050's Next.js frontend** as the primary UI (11 pages, complete)
5. The 5060 exposes a `/api/v1/triage/predict` endpoint (adapter) so the 3050's existing `Remote3050InferenceClient` works correctly in reverse (3050 backend can also call it)
6. Add a new CCTV inference adapter endpoint on 3050 for the 5060 remote client

---

*Audit Complete — No files were modified during this phase.*
