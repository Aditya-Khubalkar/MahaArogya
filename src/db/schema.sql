-- MahaArogya Local SQLite Schema (Zero-Config, Offline-First, Privacy-Preserving)

CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    language TEXT DEFAULT 'mr',
    modality TEXT DEFAULT 'voice'
);

CREATE TABLE IF NOT EXISTS opd_tokens (
    token_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    hospital_id TEXT NOT NULL,
    department_name TEXT NOT NULL,
    queue_number INTEGER NOT NULL,
    estimated_wait_mins INTEGER DEFAULT 15,
    issued_at TEXT NOT NULL,
    qr_payload TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE IF NOT EXISTS reception_checkins (
    token_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    hospital_id TEXT NOT NULL,
    department_name TEXT NOT NULL,
    queue_number INTEGER NOT NULL,
    arrival_status TEXT NOT NULL CHECK(arrival_status IN ('ISSUED', 'CHECKED_IN', 'IN_CONSULTATION', 'COMPLETED', 'NO_SHOW')),
    checked_in_at TEXT,
    notes TEXT,
    version INTEGER DEFAULT 1,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(token_id) REFERENCES opd_tokens(token_id)
);

CREATE TABLE IF NOT EXISTS reception_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id TEXT NOT NULL,
    event TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT
);

CREATE TABLE IF NOT EXISTS bed_occupancy_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ward_name TEXT NOT NULL,
    total_beds INTEGER NOT NULL,
    occupied_beds INTEGER NOT NULL,
    occupancy_rate REAL NOT NULL,
    head_count INTEGER NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dataset_registry (
    dataset_name TEXT PRIMARY KEY,
    source_url TEXT,
    license TEXT,
    language TEXT,
    modality TEXT,
    date_acquired TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_reception_status ON reception_checkins(arrival_status);
CREATE INDEX IF NOT EXISTS idx_tokens_patient ON opd_tokens(patient_id);
