"""
MahaArogya — Multimodal Emergency Triage Acuity Model
Fine-tunes a transformer text backbone + 2-layer tabular vital signs MLP
on the 87,234-row FedMML-ED-Triage dataset with class-weighted Cross-Entropy loss.
"""

import os
import sys
import time
import json
import subprocess
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, recall_score, confusion_matrix
from transformers import AutoTokenizer, AutoModel

# 4-class Triage Mapping
ESI_TO_TRIAGE = {1: 0, 2: 1, 3: 2, 4: 3, 5: 3}
CLASS_NAMES = ["EMERGENCY", "URGENT", "PRIORITY", "ROUTINE"]
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}

VITAL_COLS = [
    "systolic_bp", "diastolic_bp", "heart_rate", "respiratory_rate",
    "temperature", "spo2", "pain_score", "age"
]

DEFAULT_VITAL_MEANS = {
    "systolic_bp": 128.0, "diastolic_bp": 78.0, "heart_rate": 82.0,
    "respiratory_rate": 16.0, "temperature": 36.8, "spo2": 97.5,
    "pain_score": 3.0, "age": 48.0
}
DEFAULT_VITAL_STDS = {
    "systolic_bp": 22.0, "diastolic_bp": 14.0, "heart_rate": 18.0,
    "respiratory_rate": 4.0, "temperature": 0.8, "spo2": 3.0,
    "pain_score": 3.0, "age": 20.0
}


class FedMMLTriageDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer, max_len: int = 64, means=None, stds=None):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.means = means or DEFAULT_VITAL_MEANS
        self.stds = stds or DEFAULT_VITAL_STDS

        vitals_array = []
        for col in VITAL_COLS:
            val = self.df[col].fillna(self.means[col]).values
            norm = (val - self.means[col]) / (self.stds[col] + 1e-6)
            vitals_array.append(norm)
        self.tabular_features = np.stack(vitals_array, axis=1).astype(np.float32)

        texts = []
        for _, row in self.df.iterrows():
            cc = str(row["chief_complaint"]) if pd.notnull(row["chief_complaint"]) else "Unspecified symptoms"
            cn = str(row["clinical_notes"]) if pd.notnull(row["clinical_notes"]) and str(row["clinical_notes"]).strip() else ""
            if cn:
                full_text = f"{cc}. Notes: {cn[:120]}"
            else:
                full_text = cc
            texts.append(full_text)
        self.texts = texts

        if "triage_idx" in self.df.columns:
            self.labels = self.df["triage_idx"].values.astype(np.int64)
        else:
            self.labels = None

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        text = self.texts[idx]
        tokens = self.tokenizer(
            text,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        item = {
            "input_ids": tokens["input_ids"].squeeze(0),
            "attention_mask": tokens["attention_mask"].squeeze(0),
            "tabular": torch.tensor(self.tabular_features[idx], dtype=torch.float32)
        }

        if self.labels is not None:
            item["label"] = torch.tensor(self.labels[idx], dtype=torch.long)

        return item


class MultimodalTriageClassifier(nn.Module):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", num_classes: int = 4, tabular_dim: int = 8):
        super().__init__()
        self.transformer = AutoModel.from_pretrained(model_name)
        text_dim = self.transformer.config.hidden_size

        self.tabular_mlp = nn.Sequential(
            nn.Linear(tabular_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.BatchNorm1d(64),
            nn.ReLU()
        )

        self.fusion_head = nn.Sequential(
            nn.Linear(text_dim + 64, 128),
            nn.LayerNorm(128),
            nn.Dropout(0.2),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, input_ids, attention_mask, tabular):
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        token_embeddings = outputs[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        text_emb = sum_embeddings / sum_mask

        tab_emb = self.tabular_mlp(tabular)
        fused = torch.cat([text_emb, tab_emb], dim=1)
        logits = self.fusion_head(fused)
        return logits


def get_gpu_smi():
    try:
        res = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.stdout
    except Exception as e:
        return f"nvidia-smi error: {e}"


def train_epoch(model, dataloader, optimizer, criterion, device, log_interval=20, capture_smi_step=10):
    model.train()
    total_loss = 0.0
    smi_output_captured = None

    for step, batch in enumerate(dataloader, 1):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        tabular = batch["tabular"].to(device)
        labels = batch["label"].to(device)

        optimizer.zero_grad()
        logits = model(input_ids, attention_mask, tabular)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        if step % log_interval == 0 or step == 1:
            current_vram = torch.cuda.memory_allocated() / (1024 ** 2) if torch.cuda.is_available() else 0
            print(f"  Step [{step:4d}/{len(dataloader):4d}] - Loss: {loss.item():.4f} - VRAM: {current_vram:.1f} MiB")

        if step == capture_smi_step and smi_output_captured is None:
            smi_output_captured = get_gpu_smi()

    avg_loss = total_loss / len(dataloader)
    return avg_loss, smi_output_captured


def evaluate_model(model, dataloader, device):
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            tabular = batch["tabular"].to(device)
            labels = batch["label"].to(device)

            logits = model(input_ids, attention_mask, tabular)
            preds = torch.argmax(logits, dim=1).cpu().numpy()

            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    acc = accuracy_score(all_labels, all_preds)
    recalls = recall_score(all_labels, all_preds, average=None, labels=[0, 1, 2, 3], zero_division=0)
    rep = classification_report(all_labels, all_preds, target_names=CLASS_NAMES, zero_division=0, output_dict=True)
    cm = confusion_matrix(all_labels, all_preds, labels=[0, 1, 2, 3])

    return {
        "accuracy": acc,
        "emergency_recall": recalls[0],
        "urgent_recall": recalls[1],
        "priority_recall": recalls[2],
        "routine_recall": recalls[3],
        "classification_report": rep,
        "confusion_matrix": cm
    }
