"""
MahaArogya — Synthetic Hospital & OPD Database
Prototype hospital database for Maharashtra region with live queue and bed occupancy estimates.
"""

from ai.routing.schemas import Hospital, Department

SYNTHETIC_HOSPITALS: list[Hospital] = [
    Hospital(
        id="hosp_mumbai_01",
        name="KEM General Hospital & Medical Center",
        city="Mumbai",
        latitude=19.0024,
        longitude=72.8423,
        emergency_capable=True,
        current_load_percent=82.0,
        departments={
            "General Medicine": Department(
                id="dept_kem_gen", hospital_id="hosp_mumbai_01", name="General Medicine",
                open_now=True, queue_length=12, estimated_wait_min=35,
                available_slots=["10:00 AM", "11:30 AM", "02:00 PM", "03:30 PM"]
            ),
            "Gastroenterology": Department(
                id="dept_kem_gastro", hospital_id="hosp_mumbai_01", name="Gastroenterology",
                open_now=True, queue_length=6, estimated_wait_min=20,
                available_slots=["10:30 AM", "01:00 PM", "03:00 PM"]
            ),
            "Cardiology": Department(
                id="dept_kem_cardio", hospital_id="hosp_mumbai_01", name="Cardiology",
                open_now=True, queue_length=4, estimated_wait_min=15,
                available_slots=["11:00 AM", "02:30 PM"]
            )
        },
        resource_summary={"icu_beds_free": 4, "oxygen_available": True}
    ),
    Hospital(
        id="hosp_pune_01",
        name="Sassoon General Hospital",
        city="Pune",
        latitude=18.5284,
        longitude=73.8739,
        emergency_capable=True,
        current_load_percent=68.0,
        departments={
            "General Medicine": Department(
                id="dept_sassoon_gen", hospital_id="hosp_pune_01", name="General Medicine",
                open_now=True, queue_length=8, estimated_wait_min=25,
                available_slots=["10:00 AM", "11:00 AM", "02:00 PM"]
            ),
            "Gastroenterology": Department(
                id="dept_sassoon_gastro", hospital_id="hosp_pune_01", name="Gastroenterology",
                open_now=True, queue_length=3, estimated_wait_min=10,
                available_slots=["10:30 AM", "12:00 PM", "03:00 PM"]
            )
        },
        resource_summary={"icu_beds_free": 8, "oxygen_available": True}
    ),
    Hospital(
        id="hosp_nagpur_01",
        name="Government Medical College & Hospital (GMCH)",
        city="Nagpur",
        latitude=21.1350,
        longitude=79.0982,
        emergency_capable=True,
        current_load_percent=55.0,
        departments={
            "General Medicine": Department(
                id="dept_gmch_gen", hospital_id="hosp_nagpur_01", name="General Medicine",
                open_now=True, queue_length=4, estimated_wait_min=12,
                available_slots=["09:30 AM", "11:00 AM", "01:30 PM"]
            )
        },
        resource_summary={"icu_beds_free": 12, "oxygen_available": True}
    )
]


def get_all_hospitals() -> list[Hospital]:
    return SYNTHETIC_HOSPITALS
