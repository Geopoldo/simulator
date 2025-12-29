import pandas as pd
import json

file_path = "context/public_emdat_custom_request_2025-12-04.xlsx"
print(f"Reading {file_path}...")

try:
    df = pd.read_excel(file_path, sheet_name='EM-DAT Data')
    print("\nCOLUMNS FOUND:")
    for col in df.columns:
        # Get data type and some non-null examples
        dtype = df[col].dtype
        examples = df[col].dropna().unique()[:3]
        print(f"- {col} ({dtype}): {list(examples)}")
        
except Exception as e:
    print(f"Error reading file: {e}")
