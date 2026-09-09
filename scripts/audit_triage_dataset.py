import pandas as pd
import numpy as np
import json
from collections import Counter

csv_path = r"C:\MahaArogya\data\raw\fedmml_ed_triage\fedmml_ed_triage_dataset.csv"
print(f"Loading dataset: {csv_path}")

try:
    df = pd.read_csv(csv_path)
    
    total_rows = len(df)
    unique_patients = df['patient_id'].nunique() if 'patient_id' in df.columns else 0
    unique_encounters = df['encounter_id'].nunique() if 'encounter_id' in df.columns else 0
    
    label_dist = df['triage_idx'].value_counts(normalize=True).to_dict() if 'triage_idx' in df.columns else {}
    label_counts = df['triage_idx'].value_counts().to_dict() if 'triage_idx' in df.columns else {}
    
    # Duplicates
    exact_duplicates = df.duplicated().sum()
    
    # Near duplicates (based on text)
    if 'chief_complaint' in df.columns:
        unique_texts = df['chief_complaint'].nunique()
        text_dups = total_rows - unique_texts
    else:
        text_dups = 0
        unique_texts = 0
        
    print(f"Total rows: {total_rows}")
    print(f"Unique patients: {unique_patients}")
    print(f"Unique encounters: {unique_encounters}")
    print(f"Label distribution: {label_dist}")
    print(f"Label counts: {label_counts}")
    print(f"Exact duplicates: {exact_duplicates}")
    print(f"Text duplicates (CC): {text_dups} (Unique texts: {unique_texts})")
    
    if unique_patients > 0:
        rows_per_patient = total_rows / unique_patients
        print(f"Average rows per patient: {rows_per_patient:.2f}")

    # Output to a JSON file for the agent to easily read
    results = {
        "total_rows": total_rows,
        "unique_patients": unique_patients,
        "unique_encounters": unique_encounters,
        "label_counts": label_counts,
        "exact_duplicates": int(exact_duplicates),
        "text_duplicates": int(text_dups),
        "unique_texts": int(unique_texts)
    }
    with open("dataset_audit_results.json", "w") as f:
        json.dump(results, f)
        
except Exception as e:
    print(f"Error: {e}")
