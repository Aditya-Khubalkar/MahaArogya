import torch
"""
MahaArogya — FastAPI Local API Server
Exposes clean local API interfaces for integration per technical spec deliverables.
Enforces strict Pydantic input validation, RBAC security, in-memory IP rate limiting, and global exception handling.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Optional, List, Dict, Tuple
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai.orchestrator import MahaArogyaOrchestrator, UnifiedTurnResponse
from ai.asr.service import get_asr_service
from ai.tts.service import get_tts_service
from ai.tts.schemas import TTSRequest
from ai.cv.occupancy import CCTVOccupancyEstimator
from ai.cv.schemas import CCTVOccupancyResult
from ai.routing.opd_token import OPDTokenGenerator
from ai.routing.schemas import OPDToken

from src.rbac.models import AuthUser, UserRole, Permission, get_authenticated_user
from src.rbac.middleware import enforce_permission
from src.reception.workflow import ReceptionWorkflowManager, PatientQueueEntry

app = FastAPI(
    title="MahaArogya (Sanjeevani Grid) AI Subsystem API",
    description="Healthcare-routing AI/ML subsystem local API server",
    version="1.0.0"
)


class InMemoryRateLimiter:
    """Thread-safe zero-dependency in-memory sliding-window IP rate limiter."""
    def __init__(self):
        self._history: Dict[Tuple[str, str], List[float]] = defaultdict(list)
        self._lock = Lock()
        self.test_window_override: Optional[int] = None

    def reset(self):
        """Clears rate limit history (useful for test isolation)."""
        with self._lock:
            self._history.clear()

    def enforce_rate_limit(self, request: Request, endpoint_key: str, limit: int, window_seconds: int):
        """Enforces sliding-window IP rate limit. Raises HTTP 429 if exceeded."""
        effective_window = self.test_window_override if self.test_window_override is not None else window_seconds
        client_ip = request.client.host if request.client else "127.0.0.1"
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

        key = (client_ip, endpoint_key)
        now = time.time()
        cutoff = now - effective_window

        with self._lock:
            self._history[key] = [t for t in self._history[key] if t > cutoff]

            if len(self._history[key]) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too Many Requests: Maximum {limit} requests allowed per {effective_window}s on endpoint '{endpoint_key}'."
                )

            self._history[key].append(now)


rate_limiter = InMemoryRateLimiter()


# Global ValueError exception handler returning HTTP 400 Bad Request
@app.exception_handler(ValueError)
def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

# Global KeyError exception handler returning HTTP 404 Not Found
@app.exception_handler(KeyError)
def key_error_exception_handler(request: Request, exc: KeyError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
orchestrator = MahaArogyaOrchestrator()
cv_estimator = CCTVOccupancyEstimator()
reception_mgr = ReceptionWorkflowManager()


def detect_gpu_device() -> str:
    """Dynamically detects available GPU device or returns CPU fallback descriptor."""
    try:
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            return name if "nvidia" in name.lower() else f"NVIDIA {name}"
        return "CPU (no GPU passthrough)"
    except Exception:
        return "CPU (fallback)"


@app.get("/health")
def health_check():
    """Health check endpoint (Not rate-limited)."""
    return {
        "status": "healthy",
        "subsystem": "MahaArogya AI/ML Subsystem",
        "gpu_detected": detect_gpu_device(),
        "version": "1.0.0"
    }


class TextTurnRequest(BaseModel):
    conversation_id: Optional[str] = None
    text_input: str = Field(..., min_length=1, description="Patient text statement")
    language: str = Field(default="mr", min_length=2)
    patient_lat: float = Field(default=19.0100, ge=-90.0, le=90.0)
    patient_lon: float = Field(default=72.8500, ge=-180.0, le=180.0)


@app.post("/api/conversation/turn", response_model=UnifiedTurnResponse)
def process_conversation_turn(req: TextTurnRequest, request: Request):
    """Handles a text conversation turn through the unified AI engine. Rate limited: max 30 per 10 mins per IP."""
    rate_limiter.enforce_rate_limit(request, endpoint_key="conversation_turn", limit=30, window_seconds=600)

    return orchestrator.process_turn(
        conversation_id=req.conversation_id,
        text_input=req.text_input,
        language=req.language,
        modality="text",
        patient_lat=req.patient_lat,
        patient_lon=req.patient_lon
    )


class CCTVRequest(BaseModel):
    camera_id: str = Field(..., min_length=1)
    ward_id: str = Field(..., min_length=1)
    detected_occupied_beds: int = Field(..., ge=0)
    total_beds: int = Field(..., gt=0)
    db_authoritative_occupied: int = Field(..., ge=0)
    confidence: float = Field(default=0.88, ge=0.0, le=1.0)
    staff_user_id: Optional[str] = None


@app.post("/api/cctv/estimate", response_model=CCTVOccupancyResult)
def estimate_cctv_occupancy(req: CCTVRequest):
    """Estimates ward bed occupancy from CCTV input (Staff route, not rate-limited)."""
    if req.staff_user_id:
        user = get_authenticated_user(req.staff_user_id)
        enforce_permission(user, Permission.UPDATE_BED_STATUS)

    return cv_estimator.estimate_ward_occupancy(
        camera_id=req.camera_id,
        ward_id=req.ward_id,
        detected_occupied_beds=req.detected_occupied_beds,
        total_beds=req.total_beds,
        db_authoritative_occupied=req.db_authoritative_occupied,
        confidence=req.confidence
    )


class IssueTokenRequest(BaseModel):
    patient_id: str = Field(..., min_length=1)
    hospital_name: str = Field(..., min_length=1)
    department_name: str = Field(..., min_length=1)
    slot_time: str = Field(..., min_length=1)
    current_queue_length: int = Field(default=5, ge=0)


@app.post("/api/opd/issue_token", response_model=OPDToken)
def issue_opd_token(req: IssueTokenRequest, request: Request):
    """Issues a smart OPD token. Rate limited: max 5 per 10 mins per IP."""
    rate_limiter.enforce_rate_limit(request, endpoint_key="issue_token", limit=5, window_seconds=600)

    token = OPDTokenGenerator.generate_token(
        patient_id=req.patient_id,
        hospital_name=req.hospital_name,
        department_name=req.department_name,
        slot_time=req.slot_time,
        current_queue_length=req.current_queue_length
    )
    reception_mgr.register_token(token)
    return token


class CheckinRequest(BaseModel):
    token_id: str = Field(..., min_length=1)
    staff_user_id: Optional[str] = Field(default=None, description="Authentic reception staff user ID")


@app.post("/api/reception/checkin", response_model=PatientQueueEntry)
def reception_checkin(req: CheckinRequest):
    """Reception endpoint: Marks patient token as CHECKED_IN (Staff route, not rate-limited)."""
    user = get_authenticated_user(req.staff_user_id)
    enforce_permission(user, Permission.CHECKIN_PATIENT)

    try:
        return reception_mgr.checkin_patient(req.token_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Token Not Found: {str(exc)}"
        )
    except ValueError as exc:
        err_msg = str(exc)
        if "format" in err_msg.lower() or "empty" in err_msg.lower() or "whitespace" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=err_msg
        )

