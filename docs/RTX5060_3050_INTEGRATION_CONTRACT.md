# RTX 5060 to RTX 3050 Integration Contract

## A. What the 5060 sends to the 3050
The RTX 5060 (Orchestrator/Safety Node) sends the fully extracted, structured `PatientState` object after local safety rules have been evaluated and have determined that the case is NOT an immediate emergency. 

## B. What the 3050 returns
The RTX 3050 (ML Inference Node) returns a structured classification decision containing the predicted severity, confidence score, source model identifier, features utilized, and a list of explanatory strings.

## C. Request Schema
The request will be an HTTP POST with a JSON body representing the `PatientState`.
```json
{
  "conversation_id": "string",
  "language": "string",
  "modality": "string",
  "age_years": "float (optional)",
  "gender": "string (optional)",
  "symptoms": {
     "symptom_key": {
         "present": "boolean",
         "severity": "string",
         "duration_days": "integer"
     }
  },
  "vitals": {
     "temperature_f": "float",
     "pulse_rate": "float",
     "bp_systolic": "float",
     "bp_diastolic": "float",
     "spo2_percent": "float"
  },
  "medical_history": ["string"],
  "original_input_history": ["string"]
}
```

## D. Response Schema
The 3050 responds with HTTP 200 OK and a JSON object matching this schema:
```json
{
  "severity": "string (one of: ROUTINE, PRIORITY, URGENT, EMERGENCY)",
  "confidence": "float (0.0 to 1.0)",
  "source": "string (e.g., 'xgboost_baseline')",
  "features_used": ["string"],
  "explanation": ["string"]
}
```

## E. Error Schema
If the 3050 encounters a validation or processing error, it responds with HTTP 400 or 500:
```json
{
  "detail": "string (Error description)",
  "error_code": "string (e.g., 'INVALID_STATE', 'INFERENCE_FAILED')"
}
```

## F. Timeout Behavior
The 5060 will enforce a strict timeout (configurable, default 5.0 seconds). If the 3050 does not respond within this window, the 5060 will abandon the request and fallback to local routing.

## G. Health-Check Behavior
The 5060 may periodically query an HTTP GET `/health` endpoint on the 3050.
Response: `{"status": "ok", "model_loaded": true, "device": "cuda:0"}`.

## H. Model / Service Identifier
The 3050 response includes a `"source"` field (e.g., `xgboost_baseline` or `neural_net_v2`) to track which model version served the inference.

## I. Version Compatibility
The 5060 includes an `X-Client-Version` header. The schemas are bound to `MahaArogya v1.0` `PatientState` definitions.

## J. Session / Request ID Handling
The `conversation_id` serves as the tracing identifier. The 3050 should include it in logs. The 5060 will also inject a unique `X-Request-ID` header.

## K. How the 5060 knows whether the 3050 is available
The 5060 determines availability via configuration flags (`MAHAAROGYA_3050_HOST` being set) and catching network exceptions/timeouts during connection attempts.

## L. What happens when the 3050 is unavailable
The 5060 gracefully catches the `ConnectionError` or `Timeout`, avoids crashing, and returns a controlled fallback state:
`{"severity": "ROUTINE", "confidence": 0.0, "source": "remote_inference_unavailable", "explanation": ["3050 integration unavailable"]}`.
Safety is never compromised because emergencies are handled prior to ML inference.
