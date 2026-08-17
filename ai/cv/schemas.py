"""
MahaArogya — CCTV Bed Occupancy Estimation Schemas
Pydantic data models for non-authoritative CCTV bed occupancy estimation.
Constraint: CCTV is an estimate requiring human staff verification; no face recognition / PII.
"""

from pydantic import BaseModel, Field


class CCTVOccupancyResult(BaseModel):
    camera_id: str = Field(..., description="Camera ID (e.g. 'cam_ward_icu_01')")
    ward_id: str = Field(..., description="Ward identifier (e.g. 'ward_icu_A')")
    estimated_occupied_beds: int = Field(..., description="CV estimated occupied bed count")
    total_beds: int = Field(..., description="Total bed count in camera field of view")
    occupancy_percentage: float = Field(..., description="Calculated occupancy percentage")
    confidence_score: float = Field(..., description="Vision model confidence score (0.0 to 1.0)")
    
    db_authoritative_occupied: int = Field(..., description="Authoritative DB record count")
    discrepancy_detected: bool = Field(..., description="True if CV estimate disagrees with DB record")
    discrepancy_delta: int = Field(default=0, description="Difference between CV estimate and DB record")
    human_verification_required: bool = Field(..., description="True if staff must verify bed state")
    timestamp: str = Field(..., description="Frame estimation timestamp")
