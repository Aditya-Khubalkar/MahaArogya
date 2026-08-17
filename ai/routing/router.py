"""
MahaArogya — Deterministic Hospital Routing Engine
Ranks suitable nearby hospitals based on care level, distance, queue wait, and department availability.
Calculates exact Haversine distance and transparent scoring components.
"""

import math
from typing import List, Optional
from ai.routing.schemas import Hospital, HospitalRecommendation
from ai.routing.hospitals import get_all_hospitals


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    if not (-90.0 <= lat1 <= 90.0) or not (-90.0 <= lat2 <= 90.0):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180.0 <= lon1 <= 180.0) or not (-180.0 <= lon2 <= 180.0):
        raise ValueError("Longitude must be between -180 and 180 degrees")

    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


class HospitalRouter:
    """Deterministic hospital ranking engine."""

    def __init__(self, hospitals: Optional[List[Hospital]] = None):
        self.hospitals = hospitals if hospitals is not None else get_all_hospitals()

    def rank_hospitals(
        self,
        triage_category: str,
        target_department: str = "General Medicine",
        patient_lat: float = 19.0100,  # Default Mumbai central
        patient_lon: float = 72.8500
    ) -> List[HospitalRecommendation]:
        """
        Ranks suitable hospitals for a patient.
        
        Args:
            triage_category: ['EMERGENCY', 'URGENT', 'PRIORITY', 'ROUTINE']
            target_department: Preferred specialty
            patient_lat: Patient latitude
            patient_lon: Patient longitude

        Returns:
            List of HospitalRecommendation ordered by suitability score (descending).
        """
        recommendations = []

        for hosp in self.hospitals:
            # Check emergency capability constraint
            if triage_category == "EMERGENCY" and not hosp.emergency_capable:
                continue  # Skip non-emergency capable for emergency cases

            dist_km = haversine_distance(patient_lat, patient_lon, hosp.latitude, hosp.longitude)

            # Match department or fallback to General Medicine
            dept = hosp.departments.get(target_department) or hosp.departments.get("General Medicine")
            if not dept or not dept.open_now:
                continue

            # Composite Score Calculation (higher is better)
            # Distance penalty: -2.0 points per km
            # Wait time penalty: -1.5 points per min
            # Load penalty: -1.0 points per % load over 50%
            
            distance_score = max(0.0, 100.0 - (dist_km * 2.0))
            wait_score = max(0.0, 100.0 - (dept.estimated_wait_min * 1.5))
            load_score = max(0.0, 100.0 - ((hosp.current_load_percent - 50.0) * 1.0))

            if triage_category == "EMERGENCY":
                # For emergency: distance is 70% weight, wait is 30% weight
                composite_score = (distance_score * 0.70) + (wait_score * 0.30)
                explanation = f"Emergency Priority: {dist_km}km distance ({distance_score:.1f}pts), {dept.estimated_wait_min}m wait ({wait_score:.1f}pts)."
            else:
                # For routine/urgent: balanced weight (distance 40%, wait 40%, load 20%)
                composite_score = (distance_score * 0.40) + (wait_score * 0.40) + (load_score * 0.20)
                explanation = f"Routine Score: {dist_km}km dist ({distance_score:.1f}pts), {dept.estimated_wait_min}m wait ({wait_score:.1f}pts), load {hosp.current_load_percent}% ({load_score:.1f}pts)."

            recommendations.append(
                HospitalRecommendation(
                    hospital=hosp,
                    department_name=dept.name,
                    score=round(composite_score, 2),
                    distance_km=dist_km,
                    estimated_wait_min=dept.estimated_wait_min,
                    explanation=explanation
                )
            )

        # Sort by composite score descending
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations
