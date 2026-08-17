"""
MahaArogya - Offline-First SQLite Local Persistence Engine
Complies with 'Local-Only, No Cloud' and Privacy-Preserving (Zero PII) Hard Constraints.
Features WAL mode, Foreign Key Enforcement, ACID Transactions, and Atomic State Transitions.
"""

import csv
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

DEFAULT_DB_PATH = Path("c:/MahaArogya/data/mahaarogya.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class LocalDatabase:
    _instance: Optional["LocalDatabase"] = None
    _lock = threading.Lock()

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self.init_schema()

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=30.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            self._local.conn = conn
        return self._local.conn

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

    def init_schema(self):
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()
        with self._lock:
            conn = self.get_connection()
            conn.executescript(ddl)
            conn.commit()

    def seed_registry_from_csv(self, csv_path: Path = Path("c:/MahaArogya/data/source_registry.csv")):
        if not csv_path.exists():
            return
        conn = self.get_connection()
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conn.execute("""
                    INSERT INTO dataset_registry (dataset_name, source_url, license, language, modality, date_acquired, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(dataset_name) DO UPDATE SET
                        source_url=excluded.source_url,
                        license=excluded.license,
                        language=excluded.language,
                        modality=excluded.modality,
                        date_acquired=excluded.date_acquired,
                        notes=excluded.notes
                """, (
                    row.get("dataset_name"),
                    row.get("source_url"),
                    row.get("license"),
                    row.get("language"),
                    row.get("modality"),
                    row.get("date_acquired"),
                    row.get("notes")
                ))
        conn.commit()

    def record_patient(self, patient_id: str, language: str = "mr", modality: str = "voice"):
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO patients (patient_id, created_at, language, modality)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(patient_id) DO NOTHING
        """, (patient_id, datetime.now().isoformat(), language, modality))
        conn.commit()

    def record_opd_token(self, token_id: str, patient_id: str, hospital_id: str,
                         department_name: str, queue_number: int,
                         estimated_wait_mins: int = 15, qr_payload: Optional[str] = None):
        self.record_patient(patient_id)
        now_str = datetime.now().isoformat()
        conn = self.get_connection()
        with conn:
            conn.execute("""
                INSERT INTO opd_tokens (token_id, patient_id, hospital_id, department_name, queue_number, estimated_wait_mins, issued_at, qr_payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(token_id) DO UPDATE SET
                    queue_number=excluded.queue_number,
                    estimated_wait_mins=excluded.estimated_wait_mins,
                    qr_payload=excluded.qr_payload
            """, (token_id, patient_id, hospital_id, department_name, queue_number, estimated_wait_mins, now_str, qr_payload))

            conn.execute("""
                INSERT INTO reception_checkins (token_id, patient_id, hospital_id, department_name, queue_number, arrival_status, updated_at)
                VALUES (?, ?, ?, ?, ?, 'ISSUED', ?)
                ON CONFLICT(token_id) DO NOTHING
            """, (token_id, patient_id, hospital_id, department_name, queue_number, now_str))

    def atomic_transition_reception_status(
        self,
        token_id: str,
        from_statuses: List[str],
        to_status: str,
        checked_in_at: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        conn = self.get_connection()
        now_str = datetime.now().isoformat()
        with conn:
            cur = conn.execute("SELECT * FROM reception_checkins WHERE token_id = ?", (token_id,))
            row = cur.fetchone()
            if not row:
                raise KeyError(f"Token '{token_id}' not found in database.")

            current_status = row["arrival_status"]
            if current_status not in from_statuses:
                if current_status == to_status:
                    raise ValueError(f"Invalid state transition: Token '{token_id}' is already in state '{current_status}'.")
                raise ValueError(f"Invalid state transition: Cannot transition '{token_id}' from '{current_status}' to '{to_status}'.")

            res = conn.execute("""
                UPDATE reception_checkins
                SET arrival_status = ?,
                    checked_in_at = COALESCE(?, checked_in_at),
                    notes = COALESCE(?, notes),
                    version = version + 1,
                    updated_at = ?
                WHERE token_id = ? AND arrival_status = ?
            """, (to_status, checked_in_at, notes, now_str, token_id, current_status))

            if res.rowcount != 1:
                raise RuntimeError(f"Concurrent modification detected during transition for token '{token_id}'.")

            event_map = {
                "CHECKED_IN": "PATIENT_CHECKED_IN",
                "NO_SHOW": "PATIENT_MARKED_NO_SHOW",
                "IN_CONSULTATION": "PATIENT_START_CONSULTATION",
                "COMPLETED": "PATIENT_COMPLETE_CONSULTATION"
            }
            event_name = event_map.get(to_status, f"TRANSITION_TO_{to_status}")
            conn.execute("""
                INSERT INTO reception_audit_log (token_id, event, timestamp, details)
                VALUES (?, ?, ?, ?)
            """, (token_id, event_name, now_str, notes))

            cur = conn.execute("SELECT * FROM reception_checkins WHERE token_id = ?", (token_id,))
            return dict(cur.fetchone())

    def get_queue_entry(self, token_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.execute("SELECT * FROM reception_checkins WHERE token_id = ?", (token_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def list_active_queue(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.execute("SELECT * FROM reception_checkins ORDER BY queue_number ASC")
        return [dict(r) for r in cur.fetchall()]

    def record_occupancy_snapshot(self, ward_name: str, total_beds: int, occupied_beds: int,
                                  occupancy_rate: float, head_count: int):
        conn = self.get_connection()
        now_str = datetime.now().isoformat()
        with conn:
            conn.execute("""
                INSERT INTO bed_occupancy_snapshots (ward_name, total_beds, occupied_beds, occupancy_rate, head_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ward_name, total_beds, occupied_beds, occupancy_rate, head_count, now_str))


def get_db(db_path: Path = DEFAULT_DB_PATH) -> LocalDatabase:
    if LocalDatabase._instance is None:
        with LocalDatabase._lock:
            if LocalDatabase._instance is None:
                LocalDatabase._instance = LocalDatabase(db_path)
    return LocalDatabase._instance
