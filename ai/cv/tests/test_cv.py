"""
Unit tests for CCTV Bed Occupancy Estimator.
"""

import pytest
from ai.cv.occupancy import CCTVOccupancyEstimator


def test_cctv_no_discrepancy():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=8,
        total_beds=10,
        db_authoritative_occupied=8,
        confidence=0.92
    )
    
    assert res.occupancy_percentage == 80.0
    assert res.discrepancy_detected is False
    assert res.human_verification_required is False


def test_cctv_discrepancy_triggers_human_verification():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_02",
        ward_id="ward_icu_B",
        detected_occupied_beds=9,
        total_beds=10,
        db_authoritative_occupied=7,
        confidence=0.85
    )
    
    assert res.discrepancy_detected is True
    assert res.discrepancy_delta == 2
    assert res.human_verification_required is True
