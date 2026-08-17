"""
Unit tests for Multilingual MedicalExtractor.
Verifies Marathi, Hindi, English, Roman Marathi, and Hinglish extraction & negations.
"""

import pytest
from ai.nlp.extractor import MedicalExtractor
from ai.patient_state.state_manager import PatientStateManager


def test_marathi_extraction_and_negation():
    extractor = MedicalExtractor()
    
    # Positive + Duration
    delta1 = extractor.extract("conv_01", "माझं पोट दोन दिवसांपासून खूप दुखत आहे.")
    assert "abdominal_pain" in delta1.new_symptoms
    assert delta1.new_symptoms["abdominal_pain"].present is True
    assert delta1.new_symptoms["abdominal_pain"].duration is not None

    # Positive + Negation
    delta2 = extractor.extract("conv_02", "छातीत कळ मारते आहे पण ताप नाही.")
    assert "chest_pain" in delta2.new_symptoms
    assert "fever" in delta2.new_negations


def test_hindi_extraction_and_negation():
    extractor = MedicalExtractor()
    
    delta = extractor.extract("conv_03", "कल से बुखार है पर उल्टी नहीं हुई है।")
    assert "fever" in delta.new_symptoms
    assert "vomiting" in delta.new_negations


def test_english_extraction():
    extractor = MedicalExtractor()
    
    delta = extractor.extract("conv_04", "I have severe abdominal pain for 2 days.")
    assert "abdominal_pain" in delta.new_symptoms
    assert delta.new_symptoms["abdominal_pain"].severity == "severe"


def test_hinglish_extraction():
    extractor = MedicalExtractor()
    
    delta = extractor.extract("conv_05", "Mera stomach 2 days se severe pain kar raha hai.")
    assert "abdominal_pain" in delta.new_symptoms


def test_end_to_end_extractor_with_patient_state():
    extractor = MedicalExtractor()
    mgr = PatientStateManager("conv_e2e_01", language="mr")
    
    # Turn 1
    delta1 = extractor.extract("conv_e2e_01", "माझं पोट दोन दिवसांपासून खूप दुखत आहे.")
    state1 = mgr.update_with_delta(delta1)
    assert state1.symptoms["abdominal_pain"].present is True
    assert state1.symptoms["abdominal_pain"].duration is not None

    # Turn 2
    delta2 = extractor.extract("conv_e2e_01", "ताप नाही पण २ वेळा उलटी झाली.")
    state2 = mgr.update_with_delta(delta2)
    assert "fever" in state2.negated_symptoms
    assert "vomiting" in state2.symptoms
    assert state2.symptoms["vomiting"].frequency == "२ वेळा"
