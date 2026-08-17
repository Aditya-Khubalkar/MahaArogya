"""
MahaArogya - Reception & Offline Hospital Arrival Workflow
Manages patient arrival check-in, token lookup, queue state updates, audit trails,
and strict state-machine enforcement with thread safety and SQLite ACID persistence.
"""

import re
from datetime import datetime
from threading import Lock
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from ai.routing.schemas import OPDToken
from src.db.database import LocalDatabase, get_db


TOKEN_ID_REGEX = re.compile(r"^(OPD|EMG)-[A-Z0-9]{2,}-[A-Z0-9]+$")

LEGAL_STATE_TRANSITIONS: Dict[str, List[str]] = {
    "ISSUED": ["CHECKED_IN", "NO_SHOW"],
    "CHECKED_IN": ["IN_CONSULTATION"],
    "IN_CONSULTATION": ["COMPLETED"],
    "COMPLETED": [],
    "NO_SHOW": []
}


def validate_token_format(token_id: str) -> str:
    if not token_id or not isinstance(token_id, str) or not token_id.strip():
        raise ValueError("Token ID cannot be empty or whitespace.")
    clean_id = token_id.strip()
    if not TOKEN_ID_REGEX.match(clean_id):
        raise ValueError(f"Invalid token format: '{clean_id}'. Expected format 'OPD-<HOSP>-<CODE>' or 'EMG-<HOSP>-<CODE>'.")
    return clean_id


class PatientQueueEntry(BaseModel):
    token_id: str
    patient_id: str
    hospital_id: str
    department_name: str
    queue_number: int
    arrival_status: str = Field(default="ISSUED", description="['ISSUED', 'CHECKED_IN', 'IN_CONSULTATION', 'COMPLETED', 'NO_SHOW']")
    checked_in_at: Optional[str] = None
    notes: Optional[str] = None


class ReceptionWorkflowManager:
    def __init__(self, db: Optional[LocalDatabase] = None):
        self.active_queue: Dict[str, PatientQueueEntry] = {}
        self.audit_log: List[dict] = []
        self._lock = Lock()
        self.db = db

    def register_token(self, token: OPDToken, hospital_id: str = "hosp_mumbai_01", estimated_wait_mins: Optional[int] = None) -> PatientQueueEntry:
        clean_token_id = validate_token_format(token.token_id)
        with self._lock:
            entry = PatientQueueEntry(
                token_id=clean_token_id,
                patient_id=token.patient_id,
                hospital_id=hospital_id,
                department_name=token.department_name,
                queue_number=token.queue_number,
                arrival_status="ISSUED"
            )
            self.active_queue[clean_token_id] = entry
            if self.db is not None:
                if estimated_wait_mins is None:
                    wait_mins = 0 if clean_token_id.startswith("EMG") else max(0, token.queue_number * 15)
                else:
                    wait_mins = estimated_wait_mins
                self.db.record_opd_token(
                    token_id=clean_token_id,
                    patient_id=token.patient_id,
                    hospital_id=hospital_id,
                    department_name=token.department_name,
                    queue_number=token.queue_number,
                    estimated_wait_mins=wait_mins,
                    qr_payload=getattr(token, "qr_payload", None)
                )
            return entry

    def _transition_status(self, token_id: str, target_status: str, checked_in_at: Optional[str] = None, notes: Optional[str] = None) -> PatientQueueEntry:
        if token_id not in self.active_queue:
            raise KeyError(f"Token '{token_id}' not found in active queue: unregistered or never issued.")

        entry = self.active_queue[token_id]
        current_status = entry.arrival_status

        if target_status not in LEGAL_STATE_TRANSITIONS.get(current_status, []):
            if current_status == target_status:
                raise ValueError(
                    f"Invalid state transition: Token '{token_id}' is already in state '{current_status}' (duplicate transition to '{target_status}' rejected)."
                )
            raise ValueError(
                f"Invalid state transition: Cannot transition token '{token_id}' from current state '{current_status}' to '{target_status}'."
            )

        if self.db is not None:
            allowed_from = [k for k, v in LEGAL_STATE_TRANSITIONS.items() if target_status in v]
            self.db.atomic_transition_reception_status(
                token_id=token_id,
                from_statuses=allowed_from,
                to_status=target_status,
                checked_in_at=checked_in_at,
                notes=notes
            )

        entry.arrival_status = target_status
        if checked_in_at:
            entry.checked_in_at = checked_in_at
        if notes:
            entry.notes = notes
        return entry

    def checkin_patient(self, token_id: str, notes: Optional[str] = None) -> PatientQueueEntry:
        clean_token_id = validate_token_format(token_id)
        with self._lock:
            now_str = datetime.now().isoformat()
            entry = self._transition_status(clean_token_id, "CHECKED_IN", checked_in_at=now_str, notes=notes)
            self.audit_log.append({
                "event": "PATIENT_CHECKED_IN",
                "token_id": clean_token_id,
                "timestamp": now_str
            })
            return entry

    def mark_no_show(self, token_id: str) -> PatientQueueEntry:
        clean_token_id = validate_token_format(token_id)
        with self._lock:
            entry = self._transition_status(clean_token_id, "NO_SHOW")
            self.audit_log.append({
                "event": "PATIENT_MARKED_NO_SHOW",
                "token_id": clean_token_id,
                "timestamp": datetime.now().isoformat()
            })
            return entry

    def start_consultation(self, token_id: str) -> PatientQueueEntry:
        clean_token_id = validate_token_format(token_id)
        with self._lock:
            entry = self._transition_status(clean_token_id, "IN_CONSULTATION")
            self.audit_log.append({
                "event": "PATIENT_START_CONSULTATION",
                "token_id": clean_token_id,
                "timestamp": datetime.now().isoformat()
            })
            return entry

    def complete_consultation(self, token_id: str) -> PatientQueueEntry:
        clean_token_id = validate_token_format(token_id)
        with self._lock:
            entry = self._transition_status(clean_token_id, "COMPLETED")
            self.audit_log.append({
                "event": "PATIENT_COMPLETE_CONSULTATION",
                "token_id": clean_token_id,
                "timestamp": datetime.now().isoformat()
            })
            return entry
