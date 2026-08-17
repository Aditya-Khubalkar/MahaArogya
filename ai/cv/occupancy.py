"""
MahaArogya — CCTV Bed Occupancy Estimator Engine
Non-authoritative computer vision bed estimation.
Strictly non-PII, no facial recognition, enforces human verification workflows.
"""

from datetime import datetime
from ai.cv.schemas import CCTVOccupancyResult


class CCTVOccupancyEstimator:
    """Estimates ward bed occupancy from synthetic or frame metadata."""

    def estimate_ward_occupancy(
        self,
        camera_id: str,
        ward_id: str,
        detected_occupied_beds: int,
        total_beds: int,
        db_authoritative_occupied: int,
        confidence: float = 0.88
    ) -> CCTVOccupancyResult:
        """
        Calculates occupancy and compares with authoritative DB record.
        
        Args:
            camera_id: Camera identifier
            ward_id: Ward identifier
            detected_occupied_beds: CV detected occupied beds
            total_beds: Total beds in view
            db_authoritative_occupied: Known DB count
            confidence: Model confidence score

        Returns:
            CCTVOccupancyResult instance
        """
        if not camera_id or not str(camera_id).strip():
            raise ValueError("Camera ID cannot be empty")

        if not ward_id or not str(ward_id).strip():
            raise ValueError("Ward ID cannot be empty")

        if total_beds <= 0:
            raise ValueError("Total beds must be greater than zero")

        if detected_occupied_beds < 0:
            raise ValueError("Detected occupied beds cannot be negative")

        if db_authoritative_occupied < 0:
            raise ValueError("Authoritative DB occupancy cannot be negative")

        if not (0.0 <= confidence <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")

        occ_pct = round((detected_occupied_beds / total_beds) * 100.0, 1)
        discrepancy_delta = detected_occupied_beds - db_authoritative_occupied
        discrepancy_detected = abs(discrepancy_delta) > 0
        human_verification_required = discrepancy_detected or confidence < 0.80

        return CCTVOccupancyResult(
            camera_id=camera_id,
            ward_id=ward_id,
            estimated_occupied_beds=detected_occupied_beds,
            total_beds=total_beds,
            occupancy_percentage=occ_pct,
            confidence_score=round(confidence, 2),
            db_authoritative_occupied=db_authoritative_occupied,
            discrepancy_detected=discrepancy_detected,
            discrepancy_delta=discrepancy_delta,
            human_verification_required=human_verification_required,
            timestamp=datetime.now().isoformat()
        )
