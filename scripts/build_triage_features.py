import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split

raw_csv = r"C:\MahaArogya\data\raw\triage\nhamcs\nhamcs_2021_raw.csv"
rfv_csv = r"C:\MahaArogya\data\metadata\nhamcs_rfv_dictionary.csv"
processed_dir = r"C:\MahaArogya\data\processed\triage\nhamcs"
splits_dir = r"C:\MahaArogya\data\splits\triage\nhamcs"
docs_dir = r"C:\MahaArogya\docs"

os.makedirs(processed_dir, exist_ok=True)
os.makedirs(splits_dir, exist_ok=True)

# Load data
df = pd.read_csv(raw_csv, low_memory=False)
rfv_df = pd.read_csv(rfv_csv)
rfv_dict = dict(zip(rfv_df['rfv_code'], rfv_df['description']))

initial_rows = len(df)

# Step 2: Target Filtering
# Drop missing triage levels or level <1, >5
df = df[(df['IMMEDR'] >= 1) & (df['IMMEDR'] <= 5)].copy()
# Triage Mapping: 1=EMERGENCY, 2=URGENT, 3=PRIORITY, 4/5=ROUTINE
triage_map = {1: 'EMERGENCY', 2: 'URGENT', 3: 'PRIORITY', 4: 'ROUTINE', 5: 'ROUTINE'}
df['triage_level'] = df['IMMEDR'].map(triage_map)

# Handle Vitals (Convert negative values to NaN)
vitals = ['PULSE', 'TEMPF', 'RESPR', 'BPSYS', 'BPDIAS', 'POX', 'PAINSCALE', 'AGE']
for v in vitals:
    if v in df.columns:
        df.loc[df[v] < 0, v] = np.nan

# Handle RFV mapping (Text Representation)
def map_rfv_to_text(row):
    complaints = []
    for col in ['RFV1', 'RFV2', 'RFV3', 'RFV4', 'RFV5']:
        if col in row and pd.notna(row[col]) and row[col] != 'Blank' and row[col] != -9:
            # Code might be float/string, NHAMCS codes are sometimes strings or floats
            # Let's try matching as float and int and str
            try:
                code_val = float(row[col])
                if code_val in rfv_dict:
                    complaints.append(str(rfv_dict[code_val]).strip())
            except:
                pass
    if complaints:
        joined = ", ".join(complaints).lower()
        return f"Patient presenting with {joined}"
    return "Patient presenting with unspecified symptoms"

df['chief_complaint_text'] = df.apply(map_rfv_to_text, axis=1)

# Rename features for clarity
df_feat = pd.DataFrame()
df_feat['age'] = df['AGE']
df_feat['gender'] = df['SEX'].map({1: 'Female', 2: 'Male', -9: 'Unknown', -8: 'Unknown'}).fillna('Unknown')
df_feat['temperature'] = df['TEMPF']
df_feat['heart_rate'] = df['PULSE']
df_feat['respiratory_rate'] = df['RESPR']
df_feat['systolic_bp'] = df['BPSYS']
df_feat['diastolic_bp'] = df['BPDIAS']
df_feat['spo2'] = df['POX'] if 'POX' in df.columns else np.nan
df_feat['pain_score'] = df['PAINSCALE']
df_feat['chief_complaint_text'] = df['chief_complaint_text']
df_feat['triage_level'] = df['triage_level']
df_feat['triage_level_idx'] = df['IMMEDR'].map({1: 0, 2: 1, 3: 2, 4: 3, 5: 3})

# Save features
processed_path = os.path.join(processed_dir, 'nhamcs_triage_features.csv')
df_feat.to_csv(processed_path, index=False)

# Splits (70 / 15 / 15)
train_df, temp_df = train_test_split(df_feat, test_size=0.30, random_state=42, stratify=df_feat['triage_level_idx'])
val_df, test_df = train_test_split(temp_df, test_size=0.50, random_state=42, stratify=temp_df['triage_level_idx'])

train_df.to_csv(os.path.join(splits_dir, "train.csv"), index=False)
val_df.to_csv(os.path.join(splits_dir, "val.csv"), index=False)
test_df.to_csv(os.path.join(splits_dir, "test.csv"), index=False)

# Report Generation
missing_stats = df_feat.isnull().sum().to_dict()
class_dist = df_feat['triage_level'].value_counts().to_dict()
duplicate_count = df_feat.duplicated().sum()

report = f"""# NHAMCS Feature Engineering Report

## 1. Dataset Dimensions
- **Rows before processing:** {initial_rows}
- **Rows after processing:** {len(df_feat)}
- **Removed Rows:** {initial_rows - len(df_feat)}
- **Reason for removal:** Missing or invalid triage severity label (`IMMEDR` < 1 or > 5).

## 2. Duplicate Analysis
- **Exact duplicate rows:** {duplicate_count} (Note: NHAMCS is cross-sectional; exact duplicates across demographic/vitals likely represent low-variance data entry collisions rather than actual same-patient leakage, but they should be monitored).

## 3. Class Distribution
- **EMERGENCY (Level 1):** {class_dist.get('EMERGENCY', 0)}
- **URGENT (Level 2):** {class_dist.get('URGENT', 0)}
- **PRIORITY (Level 3):** {class_dist.get('PRIORITY', 0)}
- **ROUTINE (Level 4 & 5):** {class_dist.get('ROUTINE', 0)}

## 4. Missing Values
{json.dumps(missing_stats, indent=2)}

## 5. Splits
- **Train:** {len(train_df)} rows
- **Validation:** {len(val_df)} rows
- **Test:** {len(test_df)} rows

*Random Seed: 42. Stratified by triage level.*
"""

with open(os.path.join(docs_dir, "NHAMCS_FEATURE_ENGINEERING_REPORT.md"), "w") as f:
    f.write(report)
    
print("Feature pipeline complete.")
print(f"Processed dataset size: {len(df_feat)}")
