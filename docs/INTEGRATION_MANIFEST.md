# MAHAAROGYA — INTEGRATION MANIFEST
**Date:** 2026-08-18  
**Purpose:** Pre-integration file inventory with SHA256 hashes to verify no accidental changes

---

## CRITICAL 5060 FILES (DO NOT OVERWRITE)

| SHA256 | Size (bytes) | File | System | Role |
|--------|-------------|------|--------|------|
| 1B904AA6A69431735108929A16DABD1930D1D840AB8ECEE05DC7100399A2DA1C | 13098 | `ai/triage/safety_rules.py` | 5060 | Emergency safety engine (15+ rules) |
| 72CDFF42CECF2D25883632199ED7867895696181C89F4D31CF1BE42F19665901 | 4072 | `ai/triage/classifier.py` | 5060 | Triage classifier (safety + ML + remote) |
| E7F1A2D462D815EF4E5A4681171B441BFBC85E62D493E8B78EBFC171724C4893 | 17841 | `ai/nlp/extractor.py` | 5060 | Comprehensive medical NLP extractor |
| B2DD79197F3EE5FF32B6E37938CC85BD3F32D31CA6D79779B5EFC13937EB5C83 | 5117 | `ai/asr/service.py` | 5060 | Fine-tuned Whisper ASR service |
| E487BED22EB5C40695E1BFEF6A364380FC96416CB3C7764B9516764A888A85E5 | 8356 | `ai/tts/service.py` | 5060 | Multilingual TTS (EN/HI/MR) |
| 525C9D5C13BC25D023E7A5AED14C1D92D616266FDB0A0EB196441D4331222796 | 5306 | `ai/orchestrator.py` | 5060 | Unified orchestrator |
| 2FA6828AEE4CBB306F9841CDE7582B86ABB3D54F42605A0D135056C38479CDB6 | 1613 | `api/main.py` | 5060 | FastAPI main app |

---

## CRITICAL 3050 FILES (DO NOT OVERWRITE)

| SHA256 | Size (bytes) | File | System | Role |
|--------|-------------|------|--------|------|
| 7805E159EA92C129698197028B3C21ACE799D82BC3ADEE7BC27F6964610D7567 | 39135 | `backend/main.py` | 3050 Python | Complete hospital FastAPI backend |
| 6A88D2628FF051D29F6FEB6355BE5BCC99E2AB52F37B5F6CB5F59966B52A73E3 | 2561 | `backend/auth.py` | 3050 Python | JWT + RBAC auth |
| 705CE9BBB79ACA54EFFAAC5B08E5CA95E26F72F1B6B75BDE03EEB27A4E2E4982 | 2706 | `ai/cv/occupancy_engine.py` | 3050 Python | YOLOv8n CCTV occupancy detection |
| D7E61A62BC2445CC68DF3568E3FBB912C1DBBEBE8D8DEBE53A15987C09063F10 | 3991 | `ai/triage/safety_rules.py` | 3050 Python | 5-rule safety engine (PRESERVED but not primary) |
| 925E1F7D3B21A867D27CC5CAC68774DB00F9B46938E1D8E00BD65E02C3DD9491 | 3123 | `ai/triage/triage_engine.py` | 3050 Python | Triage engine (PRESERVED but not primary) |

---

## INTEGRATION STRATEGY

**PRIMARY AI SYSTEM:** RTX 5060 (`C:\MahaArogya\`)
- All medical AI inference goes through 5060
- Safety rules, NLP, ASR, TTS, triage — all from 5060

**PRIMARY WORKFLOW BACKEND:** RTX 3050 Python FastAPI
- All hospital workflow: RBAC, OPD, reception, nurse, doctor, CCTV, admin
- PostgreSQL database: `mahaarogya`
- Redis: realtime WebSocket

**INTEGRATION LAYER:** New files in `C:\MahaArogya\integration\bridge\`
- No existing validated file will be overwritten

---

## ORIGINAL SYSTEMS PRESERVED AT:

- 5060: `C:\MahaArogya\` (Git repository — use `git diff` to verify no changes)
- 3050: `C:\MahaArogya\integration\rtx3050\` (original preserved here per specification)

---

## FILES TO BE CREATED (Integration Layer)

All new files will be created in:
- `C:\MahaArogya\integration\bridge\` — adapter/bridge scripts
- `C:\MahaArogya\docs\` — documentation

**NO EXISTING FILES WILL BE DELETED OR OVERWRITTEN.**
