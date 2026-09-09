import sys
import os
from fastapi import APIRouter, HTTPException

# Add the 5060 root path to sys.path if not present so we can import its modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ai.patient_state.schemas import PatientState
from ai.triage.schemas import TriageDecision
from ai.triage.classifier import TriageClassifier

router = APIRouter()
triage_classifier = TriageClassifier()

@router.post("/predict", response_model=TriageDecision)
def predict_triage(state: PatientState):
    """
    Adapter endpoint that allows the 3050 system to call the 5060's medical triage 
    inference (which includes SafetyRuleEngine + ML inference) remotely.
    """
    try:
        decision = triage_classifier.classify(state)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
