from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats() -> Dict[str, Any]:
    # Hardcoded/Mock implementation for now, returning metrics the frontend expects
    return {
        "status": "Online",
        "active_sessions": 12,
        "opd_tokens_issued": 81,
        "avg_latency": "0.34s",
        "triage_breakdown": [
            {"category": "ROUTINE", "count": 42, "pct": 52, "color": "var(--routine)"},
            {"category": "PRIORITY", "count": 24, "pct": 30, "color": "var(--priority)"},
            {"category": "URGENT", "count": 10, "pct": 12, "color": "var(--urgent)"},
            {"category": "EMERGENCY", "count": 5, "pct": 6, "color": "var(--emergency)"},
        ],
        "recent_activities": [
            { "id": "1", "type": "TRIAGE", "message": "Patient triaged as PRIORITY — Gastroenterology referral", "time": "2 min ago", "badge": "PRIORITY" },
            { "id": "2", "type": "OPD", "message": "OPD Token OPD-MUM-4521 issued for KEM Hospital", "time": "5 min ago", "badge": "ROUTINE" },
            { "id": "3", "type": "CHECKIN", "message": "Patient checked in at Sion Hospital reception", "time": "8 min ago", "badge": "ROUTINE" },
            { "id": "4", "type": "EMERGENCY", "message": "Red-flag detected: chest pain + breathlessness", "time": "12 min ago", "badge": "EMERGENCY" },
            { "id": "5", "type": "CCTV", "message": "Ward B2 occupancy discrepancy — human verification flagged", "time": "15 min ago", "badge": "URGENT" },
        ]
    }
