"""
Unit & Integration Tests for MahaArogya SQLite Local Persistence Layer.
Verifies schema creation, ACID transactions, atomic transitions, and state persistence across process restarts.
"""

from datetime import datetime
import pytest
from src.db.database import LocalDatabase
from src.reception.workflow import ReceptionWorkflowManager
from ai.routing.schemas import OPDToken


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_mahaarogya.db"
    db = LocalDatabase(db_file)
    db.seed_registry_from_csv()
    yield db
    db.close()


def test_schema_init_and_registry_seed(temp_db):
    conn = temp_db.get_connection()
    cur = conn.execute("SELECT count(*) as cnt FROM dataset_registry")
    cnt = cur.fetchone()["cnt"]
    assert cnt > 0, "dataset_registry should have seeded records"


def test_patient_and_token_persistence(temp_db):
    now_str = datetime.now().isoformat()
    token = OPDToken(
        token_id="OPD-KEM-101",
        patient_id="pat_anon_999",
        hospital_name="KEM Hospital",
        department_name="General Medicine",
        slot_time="10:30 AM",
        queue_number=4,
        status="ISSUED",
        qr_payload="dummy_qr",
        created_at=now_str
    )
    workflow = ReceptionWorkflowManager(db=temp_db)
    entry = workflow.register_token(token, hospital_id="hosp_kem_01")
    assert entry.arrival_status == "ISSUED"

    db_entry = temp_db.get_queue_entry("OPD-KEM-101")
    assert db_entry is not None
    assert db_entry["patient_id"] == "pat_anon_999"
    assert db_entry["arrival_status"] == "ISSUED"


def test_atomic_state_transitions_in_db(temp_db):
    now_str = datetime.now().isoformat()
    token = OPDToken(
        token_id="OPD-SION-202",
        patient_id="pat_anon_888",
        hospital_name="Sion Hospital",
        department_name="Cardiology",
        slot_time="11:00 AM",
        queue_number=1,
        status="ISSUED",
        qr_payload="dummy_qr_sion",
        created_at=now_str
    )
    workflow = ReceptionWorkflowManager(db=temp_db)
    workflow.register_token(token, hospital_id="hosp_sion_01")

    res = workflow.checkin_patient("OPD-SION-202")
    assert res.arrival_status == "CHECKED_IN"

    db_entry = temp_db.get_queue_entry("OPD-SION-202")
    assert db_entry["arrival_status"] == "CHECKED_IN"
    assert db_entry["version"] == 2

    workflow.start_consultation("OPD-SION-202")
    db_entry = temp_db.get_queue_entry("OPD-SION-202")
    assert db_entry["arrival_status"] == "IN_CONSULTATION"
    assert db_entry["version"] == 3

    workflow.complete_consultation("OPD-SION-202")
    db_entry = temp_db.get_queue_entry("OPD-SION-202")
    assert db_entry["arrival_status"] == "COMPLETED"
    assert db_entry["version"] == 4


def test_process_restart_persistence_simulation(temp_db, tmp_path):
    now_str = datetime.now().isoformat()
    token = OPDToken(
        token_id="OPD-JJH-303",
        patient_id="pat_anon_777",
        hospital_name="JJ Hospital",
        department_name="Pulmonology",
        slot_time="11:30 AM",
        queue_number=7,
        status="ISSUED",
        qr_payload="dummy_qr_jj",
        created_at=now_str
    )
    p1_workflow = ReceptionWorkflowManager(db=temp_db)
    p1_workflow.register_token(token, hospital_id="hosp_jj_01")
    p1_workflow.checkin_patient("OPD-JJH-303")
    temp_db.close()

    p2_db = LocalDatabase(temp_db.db_path)
    recovered = p2_db.get_queue_entry("OPD-JJH-303")
    assert recovered is not None
    assert recovered["arrival_status"] == "CHECKED_IN"
    assert recovered["department_name"] == "Pulmonology"
    p2_db.close()


def test_bed_occupancy_telemetry_persistence(temp_db):
    temp_db.record_occupancy_snapshot("ICU Ward A", total_beds=20, occupied_beds=18, occupancy_rate=0.90, head_count=19)
    conn = temp_db.get_connection()
    cur = conn.execute("SELECT * FROM bed_occupancy_snapshots WHERE ward_name = 'ICU Ward A'")
    row = cur.fetchone()
    assert row is not None
    assert row["occupied_beds"] == 18
    assert row["occupancy_rate"] == 0.90
