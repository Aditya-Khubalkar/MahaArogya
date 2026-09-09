import pandas as pd
import os

raw_dir = r"C:\MahaArogya\data\raw\triage\nhamcs"
meta_dir = r"C:\MahaArogya\data\metadata"
os.makedirs(meta_dir, exist_ok=True)

dta_file = os.path.join(raw_dir, "ed2021-stata.dta")
dict_file = os.path.join(meta_dir, "nhamcs_rfv_dictionary.csv")

print(f"Reading value labels from {dta_file}...")
with pd.io.stata.StataReader(dta_file) as reader:
    value_labels = reader.value_labels()

# RFV codes are usually under 'rfv1' or 'RFV1' or similar in the value labels.
# Let's inspect the keys of value_labels to find the one that corresponds to RFV
rfv_key = None
for k in value_labels.keys():
    if 'rfv' in k.lower():
        rfv_key = k
        break

if rfv_key:
    print(f"Found RFV labels under key: {rfv_key}")
    rfv_mapping = value_labels[rfv_key]
    
    # Create the dataframe
    df_rfv = pd.DataFrame(list(rfv_mapping.items()), columns=['rfv_code', 'description'])
    df_rfv['body_system/category'] = "Unknown"  # Stata labels typically don't have hierarchy
    df_rfv['source'] = "ed2021-stata.dta"
    df_rfv['year'] = 2021
    
    df_rfv.to_csv(dict_file, index=False)
    print(f"Saved RFV dictionary to {dict_file} ({len(df_rfv)} codes)")
else:
    print("Could not find RFV key in Stata value labels.")
    print("Available keys:")
    print(list(value_labels.keys()))
