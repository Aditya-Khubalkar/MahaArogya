# MahaArogya — Technical Implementation Specification

This document provides the structured specification for the development of the MahaArogya (Sanjeevani Grid) AI/ML subsystem on a local machine (RTX 5060, 8GB VRAM).

## 1. Project Overview
MahaArogya is a healthcare-routing prototype. The AI/ML subsystem handles:
- Multilingual voice (ASR) and text inputs.
- Medical information extraction.
- Patient state management.
- Safety/triage decision support.
- Routing and OPD slot selection.
- CCTV-based bed occupancy estimation.

## 2. Hard Constraints
- **Hardware**: RTX 5060 (8GB VRAM).
- **Setup**: Assume a completely clean machine. Operator is a beginner.
- **Data**: Only synthetic, consented, or clearly licensed open-source data. No PII.
- **Development**: Local development only. No paid APIs, SaaS, or cloud GPUs.
- **Safety**: Clinical decisions must have deterministic, auditable layers independent of generative models.

## 3. Data & Training Pipeline
A mandatory research phase is required before any training:
1. **Source Registry**: Maintain `data/source_registry.csv` with full provenance, license, and usage terms for every dataset.
2. **Data Engineering**: Acquire, clean, deduplicate, and curate datasets for:
    - ASR evaluation.
    - Medical information extraction.
    - Follow-up question selection.
    - Triage classification.
3. **Training Strategy**: Use established open-source foundations (e.g., AI4Bharat resources) and fine-tune project-specific models. Do not train foundation models from scratch.

## 4. Execution Phases
1. **Audit**: Inspect system hardware, drivers, and software.
2. **Environment**: Python, virtualenv, CUDA/PyTorch verification.
3. **Data Acquisition**: Search, verify, and document datasets.
4. **ASR/TTS**: Research, benchmark, and integrate.
5. **Extraction**: Train/validate multilingual medical extraction.
6. **PatientState**: Deterministic conversation memory implementation.
7. **Triage/Safety**: Rule-based safety engine + urgency classifier.
8. **Integration**: Expose clean local interfaces.

## 5. Required Deliverables
- Fully documented local implementation.
- `source_registry.csv`.
- Evaluation reports (WER/CER, F1-scores, emergency recall, latency, VRAM usage).
- Clean local API interfaces for integration.

---
*Reference: MahaArogya — Claude 5060 From-Zero Data & Training Specification (Project context and constraints).*
