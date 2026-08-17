"""
MahaArogya — Smart OPD Token Generator
Generates verifiable OPD token instances with queue numbers and QR code payloads.
"""

import json
import uuid
from datetime import datetime
from ai.routing.schemas import OPDToken


class OPDTokenGenerator:
    """Generates verifiable OPD tokens upon patient slot confirmation."""

    @staticmethod
    def generate_token(
        patient_id: str,
        hospital_name: str,
        department_name: str,
        slot_time: str,
        current_queue_length: int = 5,
        is_emergency: bool = False
    ) -> OPDToken:
        """
        Generates a verifiable OPD token with QR payload.
        
        Args:
            patient_id: Patient ID
            hospital_name: Selected hospital name
            department_name: Department specialty
            slot_time: Selected slot timestamp
            current_queue_length: Current department queue length
            is_emergency: True if emergency priority queue preemption applies

        Returns:
            OPDToken instance
        """
        if not patient_id or not str(patient_id).strip():
            raise ValueError("Patient ID cannot be empty")

        if current_queue_length < 0:
            raise ValueError("Queue length cannot be negative")

        city_code = "".join(c for c in hospital_name if c.isalnum())[:3].upper() or "HSP"
        unique_suffix = uuid.uuid4().hex[:6].upper()

        if is_emergency:
            token_num = 1
            token_id = f"EMG-{city_code}-{unique_suffix}"
            status = "EMERGENCY_PRIORITY"
        else:
            token_num = current_queue_length + 1
            token_id = f"OPD-{city_code}-{unique_suffix}"
            status = "ISSUED"

        now_str = datetime.now().isoformat()

        qr_dict = {
            "token_id": token_id,
            "patient_id": patient_id,
            "hospital": hospital_name,
            "dept": department_name,
            "slot": slot_time,
            "queue_no": token_num,
            "issued_at": now_str
        }

        return OPDToken(
            token_id=token_id,
            patient_id=patient_id,
            hospital_name=hospital_name,
            department_name=department_name,
            slot_time=slot_time,
            queue_number=token_num,
            status=status,
            qr_payload=json.dumps(qr_dict),
            created_at=now_str
        )
