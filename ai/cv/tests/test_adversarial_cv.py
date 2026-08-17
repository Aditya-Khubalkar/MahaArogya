"""
Hard Adversarial Test Suite for CCTV Bed Occupancy Estimator (ai/cv/)
Covers 15 adversarial cases: empty frames, zero/negative beds, low-light confidence drops,
occlusion under-counts, overexposure, false positive objects, and camera feed drops.
"""

import pytest
from ai.cv.occupancy import CCTVOccupancyEstimator
from ai.cv.schemas import CCTVOccupancyResult


# 1. TOTAL BEDS ZERO (DIVISION BY ZERO GUARD)
def test_adv_cv_01_total_beds_zero():
    estimator = CCTVOccupancyEstimator()
    with pytest.raises(ValueError, match="Total beds must be greater than zero"):
        estimator.estimate_ward_occupancy(
            camera_id="cam_icu_01",
            ward_id="ward_icu_A",
            detected_occupied_beds=0,
            total_beds=0,
            db_authoritative_occupied=0
        )


# 2. NEGATIVE DETECTED BEDS
def test_adv_cv_02_negative_detected_beds():
    estimator = CCTVOccupancyEstimator()
    with pytest.raises(ValueError, match="Detected occupied beds cannot be negative"):
        estimator.estimate_ward_occupancy(
            camera_id="cam_icu_01",
            ward_id="ward_icu_A",
            detected_occupied_beds=-3,
            total_beds=10,
            db_authoritative_occupied=5
        )


# 3. DETECTED EXCEEDS TOTAL BEDS (RAPID ENTRY / DOUBLE COUNTING)
def test_adv_cv_03_detected_exceeds_total_beds():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=15,
        total_beds=10,
        db_authoritative_occupied=10
    )
    assert res.occupancy_percentage == 150.0
    assert res.discrepancy_detected is True
    assert res.discrepancy_delta == 5
    assert res.human_verification_required is True


# 4. EMPTY CAMERA ID
def test_adv_cv_04_empty_camera_id():
    estimator = CCTVOccupancyEstimator()
    with pytest.raises(ValueError, match="Camera ID cannot be empty"):
        estimator.estimate_ward_occupancy(
            camera_id="",
            ward_id="ward_icu_A",
            detected_occupied_beds=5,
            total_beds=10,
            db_authoritative_occupied=5
        )


# 5. NONE WARD ID
def test_adv_cv_05_none_ward_id():
    estimator = CCTVOccupancyEstimator()
    with pytest.raises(ValueError, match="Ward ID cannot be empty"):
        estimator.estimate_ward_occupancy(
            camera_id="cam_icu_01",
            ward_id=None,
            detected_occupied_beds=5,
            total_beds=10,
            db_authoritative_occupied=5
        )


# 6. LOW LIGHTING / LOW CONFIDENCE FRAME (CONFIDENCE = 0.45)
def test_adv_cv_06_low_confidence_frame_low_light():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_night_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=5,
        total_beds=10,
        db_authoritative_occupied=5,
        confidence=0.45
    )
    assert res.confidence_score == 0.45
    assert res.human_verification_required is True  # Mandatory human verification due to low confidence


# 7. OVEREXPOSED FRAME CONFIDENCE DROP (CONFIDENCE = 0.60)
def test_adv_cv_07_overexposed_frame_confidence_drop():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_bright_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=5,
        total_beds=10,
        db_authoritative_occupied=5,
        confidence=0.60
    )
    assert res.confidence_score == 0.60
    assert res.human_verification_required is True


# 8. OCCLUSION UNDER-COUNT
def test_adv_cv_08_occlusion_under_count():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_curtain_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=3,  # Curtains blocking 5 beds
        total_beds=10,
        db_authoritative_occupied=8
    )
    assert res.discrepancy_detected is True
    assert res.discrepancy_delta == -5
    assert res.human_verification_required is True


# 9. FALSE DETECTION OF NON-PERSON OBJECTS (EQUIPMENT AS BED)
def test_adv_cv_09_false_detection_non_person_object():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=12,  # Equipment false positive
        total_beds=10,
        db_authoritative_occupied=6
    )
    assert res.discrepancy_detected is True
    assert res.discrepancy_delta == 6
    assert res.human_verification_required is True


# 10. INVALID CONFIDENCE SCORE (NEGATIVE)
def test_adv_cv_10_invalid_confidence_range_negative():
    estimator = CCTVOccupancyEstimator()
    with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
        estimator.estimate_ward_occupancy(
            camera_id="cam_icu_01",
            ward_id="ward_icu_A",
            detected_occupied_beds=5,
            total_beds=10,
            db_authoritative_occupied=5,
            confidence=-0.5
        )


# 11. INVALID CONFIDENCE SCORE (GREATER THAN 1.0)
def test_adv_cv_11_invalid_confidence_range_greater_than_one():
    estimator = CCTVOccupancyEstimator()
    with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
        estimator.estimate_ward_occupancy(
            camera_id="cam_icu_01",
            ward_id="ward_icu_A",
            detected_occupied_beds=5,
            total_beds=10,
            db_authoritative_occupied=5,
            confidence=1.5
        )


# 12. NEGATIVE DB AUTHORITATIVE COUNT
def test_adv_cv_12_negative_db_authoritative_count():
    estimator = CCTVOccupancyEstimator()
    with pytest.raises(ValueError, match="Authoritative DB occupancy cannot be negative"):
        estimator.estimate_ward_occupancy(
            camera_id="cam_icu_01",
            ward_id="ward_icu_A",
            detected_occupied_beds=5,
            total_beds=10,
            db_authoritative_occupied=-1
        )


# 13. CAMERA FEED DISCONNECT / STREAM DROP (CONFIDENCE 0.0)
def test_adv_cv_13_camera_disconnect_feed_drop():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_disconnected",
        ward_id="ward_icu_A",
        detected_occupied_beds=0,
        total_beds=10,
        db_authoritative_occupied=8,
        confidence=0.0
    )
    assert res.confidence_score == 0.0
    assert res.human_verification_required is True


# 14. OCCUPANCY PERCENTAGE PRECISION
def test_adv_cv_14_occupancy_percentage_precision():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=1,
        total_beds=3,
        db_authoritative_occupied=1,
        confidence=0.90
    )
    assert res.occupancy_percentage == 33.3


# 15. PERFECT MATCH HIGH CONFIDENCE
def test_adv_cv_15_perfect_match_high_confidence():
    estimator = CCTVOccupancyEstimator()
    res = estimator.estimate_ward_occupancy(
        camera_id="cam_icu_01",
        ward_id="ward_icu_A",
        detected_occupied_beds=6,
        total_beds=10,
        db_authoritative_occupied=6,
        confidence=0.95
    )
    assert res.occupancy_percentage == 60.0
    assert res.discrepancy_detected is False
    assert res.discrepancy_delta == 0
    assert res.human_verification_required is False
