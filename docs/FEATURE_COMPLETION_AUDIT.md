# Feature Completion Audit (RTX 5060)

This is a STRICT FUNCTIONAL AUDIT evaluating actual backend, frontend, and database integration.

## Classification Legend
- **A = genuinely functional end-to-end**
- **B = partially functional**
- **C = demo/simulation only**
- **D = missing**
- **E = broken**

## Summary Matrix

| Feature | Status | Backend | Frontend | DB | E2E Tested | Evidence | Remaining Work |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Geolocation** | A | Yes | Yes | N/A | Yes | `navigator.geolocation` sends actual coords to `/api/conversation/turn`, falls back to hardcoded Mumbai coords on deny. | None |
| **2. Map** | B | Yes | Yes | N/A | Yes | Renders OSM tiles and plots markers. Polyline is a straight line, not road routing. OSM tiles require internet. | Cache tiles offline, implement real road routing. |
| **3. Hospital Routing** | B | Yes | Yes | No | Yes | `HospitalRouter` uses haversine distance, queue length, and load. However, hospitals are hardcoded in `hospitals.py`, not in DB. | Move `hospitals.py` mock data to actual database tables. |
| **4. OPD** | B | Yes | Yes | No | Yes | Logic flows correctly, but `available_slots` are hardcoded arrays in `hospitals.py`. | Create database schema and endpoints for actual OPD slot management. |
| **5. Token + QR** | C | Yes | Yes | Yes | No | Token generation saves to DB, but QR scan on frontend is a button that sets a static ID (`OPD-SIM-1234`). | Implement real QR scanning logic using device camera/Zxing. |
| **6. Reception** | A | Yes | Yes | Yes | Yes | `/api/reception/checkin` enforces RBAC, modifies state to `CHECKED_IN`, and persists to `reception_checkins` in SQLite. | None |
| **7. Nurse** | D | No | Yes | No | No | `nurse/page.tsx` has a UI, but uses a `setTimeout` dummy function. No API endpoint exists in `api.py`. No DB table for vitals. | Build `/api/nurse/vitals` endpoint and DB schema. |
| **8. Doctor** | D | No | Yes | No | No | `doctor/page.tsx` uses a hardcoded `mockQueue`. No API endpoint to fetch PatientState or consults. | Build `/api/doctor/queue` and consultation DB schema. |
| **9. RBAC** | B | Yes | Partial | N/A | Yes | Backend `enforce_permission` works correctly for Reception/CCTV, but Nurse, Doctor, and Govt endpoints are missing entirely. | Apply RBAC to all remaining missing endpoints. |
| **10. Dashboard** | C | No | Yes | No | No | `/dashboard` renders `recharts`, but data is completely hardcoded (`forecastData`, `triageData`). | Build `/api/dashboard/stats` aggregating real SQLite data. |
| **11. Forecasting** | D | No | Yes | No | No | The frontend graph claims "XGBoost", but no forecasting model exists. The only XGBoost model is for Triage. | Train a forecasting model or relabel as a statistical anomaly baseline. |
| **12. Voice & TTS** | A | Yes | Yes | N/A | Yes | Piper (English/Hindi) and IndicF5 (Marathi) correctly handle audio. | None |
| **13. Database** | B | Yes | N/A | Yes | Yes | Persists `opd_tokens`, `reception_checkins`. Missing `PatientState`, `triage_results`, `hospitals`, `slots`. | Expand schema to cover all orchestrator outputs. |

---

## Detailed Findings & Discrepancies

### 1. Actually Complete
- **Geolocation:** Captures lat/lon and sends it to the backend engine.
- **Reception:** Full ACID transactional state changes (ISSUED -> CHECKED_IN) with RBAC enforcement.
- **Emergency E2E & Voice:** The ASR -> Extractor -> SafetyRuleEngine pipeline correctly identifies emergencies (e.g. low SpO2) and filters for `emergency_capable=True` hospitals. TTS routing works locally.

### 2. Partially Complete
- **Hospital Recommendation:** The ranking logic (distance, wait time, load penalty) is fully implemented in Python, but the dataset is loaded from an in-memory python array, not the database.
- **Map:** It visualizes coordinates accurately but depends on an active internet connection for OpenStreetMap tiles, violating the strict offline constraint. The polyline is a straight-line vector, not an actual road path.
- **RBAC & Database:** The backend framework for both is solid, but it is missing the necessary tables and endpoints to support the Nurse, Doctor, and Dashboard workflows.

### 3. Demo/Simulation Only
- **QR Scanning:** The frontend button purely simulates a successful scan payload without invoking any camera APIs.
- **Dashboard Data:** Completely hardcoded frontend arrays for both the triage distribution and patient influx charts.

### 4. Broken
- N/A

### 5. Missing
- **Nurse Backend:** No endpoints or database schemas exist for capturing and persisting pre-consultation vitals.
- **Doctor Backend:** No endpoints exist to fetch a waitlist or retrieve the AI's extracted `PatientState` for the doctor to review.
- **Forecasting Model:** The dashboard falsely claims to use an XGBoost forecasting model. No such model or checkpoint exists in the codebase for patient influx prediction.

### 6. Exact Remaining Implementation Work
1. **Offline Map Tiles:** Configure Leaflet to use local cached map tiles or offline SVGs.
2. **Database Expansion:** Create SQLite tables for `hospitals`, `departments`, `opd_slots`, `conversations`, `patient_states`, and `nurse_vitals`.
3. **API Implementation:** Create endpoints in `api.py` for `/api/nurse/vitals`, `/api/doctor/queue`, `/api/doctor/consult/complete`, and `/api/dashboard/metrics`.
4. **Frontend Integration:** Hook up `nurse/page.tsx`, `doctor/page.tsx`, and `dashboard/page.tsx` to actually fetch and post to the new backend endpoints.
5. **QR Code Scanner:** Implement a real Javascript QR scanner library (e.g., `html5-qrcode`) on the frontend.
6. **Forecasting/Anomaly Detection:** Either train a lightweight offline time-series model for forecasting or rewrite the dashboard to use statistical moving averages based on real DB data.

### 7. Exact Test Results
- **Emergency E2E:** PASSED. Low SpO2 immediately triggers an Emergency Triage and restricts the hospital list to emergency-capable facilities.
- **Routine E2E (Text to Reception):** PASSED. Generates a token, saves to DB, Reception can check it in.
- **Routine E2E (Nurse to Doctor):** FAILED. Blocked by missing backend APIs.
- **Voice TTS Validation:** PASSED. Correctly routes languages to Piper and IndicF5.
