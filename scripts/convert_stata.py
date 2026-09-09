import pandas as pd
import os

raw_dir = r"C:\MahaArogya\data\raw\triage\nhamcs"
dta_file = os.path.join(raw_dir, "ed2021-stata.dta")
csv_path = os.path.join(raw_dir, "nhamcs_2021_raw.csv")

print(f"Reading {dta_file} without converting categoricals...")
try:
    df = pd.read_stata(dta_file, convert_categoricals=False)
    df.to_csv(csv_path, index=False)
    print(f"Successfully saved to {csv_path}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
except Exception as e:
    print(f"Error reading Stata file: {e}")
