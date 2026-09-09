import pandas as pd
import json

csv_path = r"C:\MahaArogya\data\raw\triage\nhamcs\nhamcs_2021_raw.csv"
print("Loading dataset...")
df = pd.read_csv(csv_path)

results = {}
results["total_visits"] = len(df)
results["unique_visits"] = len(df) # NHAMCS has unique encounters per row implicitly (no patient tracking)

vitals_cols = [c for c in ['PULSE', 'TEMPF', 'RESPR', 'BPSYS', 'BPDIAS', 'SPO2', 'PAINSCALE'] if c in df.columns]
results["available_vitals"] = vitals_cols

complaint_cols = [c for c in df.columns if c.startswith('RFV')]
results["available_complaint_fields"] = complaint_cols

severity_cols = [c for c in ['IMMED', 'TRIAGE'] if c in df.columns]
results["severity_fields"] = severity_cols

# Missing values (just for vitals and severity)
missing = {}
for col in vitals_cols + severity_cols + complaint_cols[:3]: # check first 3 RFV
    missing[col] = int(df[col].isna().sum() + (df[col] < 0).sum()) # NHAMCS uses negative numbers like -9, -8 for missing/unknown

results["missing_values"] = missing

# Class balance for IMMED (Triage level)
if 'IMMED' in df.columns:
    # Filter out blank/unknown which are usually negative or > 5
    valid_immed = df[(df['IMMED'] >= 1) & (df['IMMED'] <= 5)]
    results["class_balance"] = valid_immed['IMMED'].value_counts(normalize=True).to_dict()
    results["class_counts"] = valid_immed['IMMED'].value_counts().to_dict()

results["duplicate_records"] = int(df.duplicated().sum())

with open("nhamcs_audit.json", "w") as f:
    json.dump(results, f, indent=4)
print("Audit complete.")
