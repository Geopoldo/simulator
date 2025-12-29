
import pandas as pd
import zipfile
import re
import xml.etree.ElementTree as ET
import os

EXCEL_PATH = "context/public_emdat_custom_request_2025-12-04.xlsx"
DOCX_PATH = "context/simulated scores.docx"

def analyze_excel():
    print(f"--- Analyzing {EXCEL_PATH} ---")
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='EM-DAT Data')
        print(f"Columns: {list(df.columns)}")
        print("\nSample Data (First record):")
        first_rec = df.iloc[0].to_dict()
        for k, v in first_rec.items():
            if pd.notna(v):
                print(f"  {k}: {v}")
        
        # Check for valuable numeric columns
        useful_metrics = ['Total Deaths', 'No Injured', 'No Affected', 'No Homeless', 'Total Affected', 'Total Damages (\'000 US$)']
        print("\nData Availability for Impact Metrics (Non-null counts):")
        for col in useful_metrics:
            if col in df.columns:
                print(f"  {col}: {df[col].count()} / {len(df)}")
                
    except Exception as e:
        print(f"Error reading Excel: {e}")

def extract_docx_text(path):
    print(f"\n--- Analyzing {path} ---")
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/document.xml')
        
        tree = ET.fromstring(xml_content)
        # Namespace for Word
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        text = []
        for p in tree.findall('.//w:p', ns):
            texts = [node.text for node in p.findall('.//w:t', ns) if node.text]
            if texts:
                text.append(''.join(texts))
        
        full_text = '\n'.join(text)
        print("Extracted Text Content (First 2000 chars):")
        print(full_text[:2000])
        return full_text
    except Exception as e:
        print(f"Error reading Docx: {e}")
        return ""

if __name__ == "__main__":
    analyze_excel()
    extract_docx_text(DOCX_PATH)
