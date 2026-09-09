"""
MahaArogya — FastAPI Local API Server
Exposes clean local API interfaces for integration per technical spec deliverables.
Enforces strict Pydantic input validation, RBAC security, in-memory IP rate limiting, and global exception handling.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Optional, List, Dict, Tuple
import logging
import redis
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("maha_api")


from ai.orchestrator import MahaArogyaOrchestrator, UnifiedTurnResponse
from ai.asr.service import get_asr_service
from ai.tts.service import get_tts_service
from ai.tts.schemas import TTSRequest
from ai.cv.occupancy import CCTVOccupancyEstimator
from ai.cv.schemas import CCTVOccupancyResult
from ai.routing.opd_token import OPDTokenGenerator
from ai.routing.schemas import OPDToken

from src.rbac.models import AuthUser, UserRole, Permission, get_authenticated_user, get_current_user
from src.rbac.middleware import enforce_permission
from src.reception.workflow import ReceptionWorkflowManager, PatientQueueEntry

from src.routers import hospitals, queue, roles, dashboard, ward, doctor, admin, govt

app = FastAPI(
    title="MahaArogya (Sanjeevani Grid) AI Subsystem API",
    description="Healthcare-routing AI/ML subsystem local API server",
    version="1.0.0"
)

app.include_router(hospitals.router)
app.include_router(queue.router)
app.include_router(roles.router)
app.include_router(dashboard.router)
app.include_router(ward.router)
app.include_router(doctor.router)
app.include_router(admin.router)
app.include_router(govt.router)


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
                logger.warning(f"Rate limit exceeded (InMemory) for IP {client_ip} on {endpoint_key}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too Many Requests: Maximum {limit} requests allowed per {effective_window}s on endpoint '{endpoint_key}'."
                )

            self._history[key].append(now)


class RedisRateLimiter:
    """Redis-backed sliding-window IP rate limiter."""
    def __init__(self, redis_url="redis://localhost:6379", fallback_to_memory=True):
        self.redis_url = redis_url
        self.fallback = fallback_to_memory
        self.test_window_override: Optional[int] = None
        self._memory_fallback = InMemoryRateLimiter()
        try:
            self.r = redis.Redis.from_url(redis_url, decode_responses=True)
            self.r.ping()
            self.use_redis = True
            logger.info("Connected to Redis for rate limiting.")
        except redis.ConnectionError:
            if self.fallback:
                logger.warning(f"Failed to connect to Redis at {redis_url}. Falling back to InMemoryRateLimiter.")
                self.use_redis = False
            else:
                raise

    def reset(self):
        """Clears rate limit history (useful for test isolation)."""
        if self.use_redis:
            self.r.flushdb()
        else:
            self._memory_fallback.reset()

    def enforce_rate_limit(self, request: Request, endpoint_key: str, limit: int, window_seconds: int):
        effective_window = self.test_window_override if self.test_window_override is not None else window_seconds
        if not self.use_redis:
            return self._memory_fallback.enforce_rate_limit(request, endpoint_key, limit, effective_window)

        client_ip = request.client.host if request.client else "127.0.0.1"
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

        key = f"rate_limit:{client_ip}:{endpoint_key}"
        now = time.time()
        cutoff = now - effective_window

        # Use a Redis pipeline for atomicity
        pipeline = self.r.pipeline()
        pipeline.zremrangebyscore(key, 0, cutoff)
        pipeline.zcard(key)
        pipeline.zadd(key, {str(now): now})
        pipeline.expire(key, effective_window)
        results = pipeline.execute()

        current_requests = results[1]

        if current_requests >= limit:
            logger.warning(f"Rate limit exceeded (Redis) for IP {client_ip} on {endpoint_key}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too Many Requests: Maximum {limit} requests allowed per {effective_window}s on endpoint '{endpoint_key}'."
            )

rate_limiter = RedisRateLimiter()


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

# CORS — allow Next.js frontend (dev on port 3000 or 3001, Docker on 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
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
        import torch
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

class DemoLoginRequest(BaseModel):
    user_id: str

@app.post("/api/v1/auth/demo-login")
def demo_login(req: DemoLoginRequest):
    """Demo mode login that returns a JWT token for the selected role."""
    from src.rbac.models import get_authenticated_user, create_access_token
    from datetime import timedelta
    
    # Verify user exists
    user = get_authenticated_user(req.user_id)
    
    # Create token
    access_token_expires = timedelta(minutes=24 * 60)
    access_token = create_access_token(
        data={"sub": user.user_id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user.model_dump()}


class TextTurnRequest(BaseModel):
    conversation_id: Optional[str] = None
    text_input: str = Field(..., min_length=1, max_length=5000, description="Patient text statement")
    language: str = Field(default="mr", min_length=2)
    patient_lat: float = Field(default=19.0100, ge=-90.0, le=90.0)
    patient_lon: float = Field(default=72.8500, ge=-180.0, le=180.0)


@app.post("/api/v1/conversation/turn", response_model=UnifiedTurnResponse)
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


@app.post("/api/v1/cctv/estimate", response_model=CCTVOccupancyResult)
def estimate_cctv_occupancy(req: CCTVRequest, user: AuthUser = Depends(get_current_user)):
    """Estimates ward bed occupancy from CCTV input (Staff route, not rate-limited)."""
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


@app.post("/api/v1/opd/issue_token", response_model=OPDToken)
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

@app.post("/api/v1/reception/checkin", response_model=PatientQueueEntry)
def reception_checkin(req: CheckinRequest, user: AuthUser = Depends(get_current_user)):
    """Reception endpoint: Marks patient token as CHECKED_IN (Staff route, not rate-limited)."""
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

