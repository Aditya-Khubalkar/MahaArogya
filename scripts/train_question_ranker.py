"""
MahaArogya - Question Ranker Training Script
Trains MuRIL-based question ranker using BCEWithLogitsLoss.
"""

import json
import pathlib
import sys
import os
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from tqdm import tqdm
from sklearn.metrics import accuracy_score

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.questions.ranker import QuestionRanker
from ai.questions.question_bank import get_all_questions

MODEL_NAME = "google/muril-base-cased"
BATCH_SIZE = 8
GRAD_ACCUM_STEPS = 4
EPOCHS = 3
LR = 2e-5
MAX_SEQ_LEN = 256

# Ensure checkpoints dir exists
CHECKPOINT_DIR = ROOT / "models" / "checkpoints" / "question_ranker"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

QUESTION_BANK = {q.question_id: q for q in get_all_questions()}

class RankingDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_len=MAX_SEQ_LEN):
        self.samples = []
        self.tokenizer = tokenizer
        self.max_len = max_len
        
        print(f"Loading {jsonl_path}...")
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                
                # Format state
                state = data["extracted_state"]
                state_str = ", ".join(f"{k}: {v}" for k, v in state.items() if v)
                
                # Format history
                history_str = " | ".join(data["conversation_history"][-4:]) # Last 4 turns
                
                context = f"[STATE] {state_str} [HISTORY] {history_str}"
                
                pos_qid = data["positive_question_id"]
                candidates = data.get("candidate_question_ids", [])
                
                for qid in set(candidates):
                    if qid not in QUESTION_BANK:
                        continue
                    q_text = QUESTION_BANK[qid].wording_en
                    label = 1.0 if qid == pos_qid else 0.0
                    self.samples.append({
                        "context": context,
                        "question": q_text,
                        "label": label
                    })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        
        encoding = self.tokenizer(
            item["context"],
            item["question"],
            truncation=True,
            max_length=self.max_len,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": torch.tensor(item["label"], dtype=torch.float)
        }

def evaluate(model, dataloader, device):
    model.eval()
    total_loss = 0
    criterion = torch.nn.BCEWithLogitsLoss()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            total_loss += loss.item()
            
            preds = (torch.sigmoid(logits) > 0.5).float()
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    acc = accuracy_score(all_labels, all_preds)
    return total_loss / len(dataloader), acc

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    train_ds = RankingDataset(ROOT / "data" / "processed" / "question_ranking" / "train.jsonl", tokenizer)
    val_ds = RankingDataset(ROOT / "data" / "processed" / "question_ranking" / "val.jsonl", tokenizer)
    
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, pin_memory=True)
    val_dl = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=4, pin_memory=True)
    
    print(f"Train pairs: {len(train_ds)}, Val pairs: {len(val_ds)}")
    
    model = QuestionRanker(MODEL_NAME)
    model.to(device)
    
    if hasattr(model.encoder, "gradient_checkpointing_enable"):
        model.encoder.gradient_checkpointing_enable()
        print("Gradient checkpointing enabled.")
        
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    criterion = torch.nn.BCEWithLogitsLoss()
    scaler = torch.amp.GradScaler('cuda')
    
    best_val_acc = 0.0
    
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        optimizer.zero_grad()
        
        pbar = tqdm(train_dl, desc=f"Epoch {epoch+1}/{EPOCHS}")
        for step, batch in enumerate(pbar):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            
            with torch.amp.autocast('cuda'):
                logits = model(input_ids, attention_mask)
                loss = criterion(logits, labels)
                loss = loss / GRAD_ACCUM_STEPS
            
            scaler.scale(loss).backward()
            
            if (step + 1) % GRAD_ACCUM_STEPS == 0:
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
                
            total_loss += loss.item() * GRAD_ACCUM_STEPS
            pbar.set_postfix({"loss": f"{loss.item() * GRAD_ACCUM_STEPS:.4f}"})
            
        avg_train_loss = total_loss / len(train_dl)
        val_loss, val_acc = evaluate(model, val_dl, device)
        
        print(f"Epoch {epoch+1} | Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_path = CHECKPOINT_DIR / "best_model.pt"
            torch.save(model.state_dict(), save_path)
            print(f"Saved new best model to {save_path}")

if __name__ == "__main__":
    main()
