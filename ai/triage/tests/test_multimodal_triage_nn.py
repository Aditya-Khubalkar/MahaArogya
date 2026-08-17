"""
Unit tests for the Fine-Tuned Multimodal Triage Acuity Model.
"""

import os
import json
import pytest
import torch
from ai.triage.train_multimodal_triage import MultimodalTriageClassifier, CLASS_NAMES


def test_triage_model_artifacts_exist():
    best_model_path = r"C:\MahaArogya\models\triage_classifier\best_model.pt"
    manifest_path = r"C:\MahaArogya\models\triage_classifier\run_manifest.json"
    split_path = r"C:\MahaArogya\data\splits\triage_split_seed42.json"

    assert os.path.exists(best_model_path), "best_model.pt missing"
    assert os.path.exists(manifest_path), "run_manifest.json missing"
    assert os.path.exists(split_path), "triage_split_seed42.json missing"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["total_epochs_trained"] >= 1
    assert manifest["best_emergency_recall"] == 1.0


def test_triage_model_forward_pass():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MultimodalTriageClassifier(model_name="sentence-transformers/all-MiniLM-L6-v2", num_classes=4, tabular_dim=8).to(device)
    model.eval()

    # Dummy inputs: batch size 2, seq len 16, 8 tabular vitals
    input_ids = torch.randint(0, 1000, (2, 16), dtype=torch.long).to(device)
    attention_mask = torch.ones((2, 16), dtype=torch.long).to(device)
    tabular = torch.randn((2, 8), dtype=torch.float32).to(device)

    with torch.no_grad():
        logits = model(input_ids, attention_mask, tabular)

    assert logits.shape == (2, 4), f"Expected shape (2, 4), got {logits.shape}"
