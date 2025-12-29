
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
import os

odk_path = "/home/canequero/TULIAN/ODK/HFA + CARI (FES) + HHS + climate shocks and SEI checked.xlsx"
context_xlsx_path = "/home/canequero/TULIAN/context/public_emdat_custom_request_2025-12-04.xlsx"
docx_path = "/home/canequero/TULIAN/context/simulated scores.docx"

def read_xlsx_info(path, label):
    print(f"--- {label} ---")
    try:
        xls = pd.ExcelFile(path)
        print(f"Sheets: {xls.sheet_names}")
        for sheet in xls.sheet_names:
            if sheet in ['survey', 'choices', 'settings', 'EM-DAT Data']: # Relevant sheets
                df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
                print(f"\nSheet: {sheet}")
                print(f"Columns: {list(df.columns)}")
                print(f"First 2 rows:\n{df.head(2).to_string()}")
    except Exception as e:
        print(f"Error reading {path}: {e}")

def read_docx_text(path):
    print(f"\n--- DOCX Content: {os.path.basename(path)} ---")
    try:
        # manual unzip and xml parse to avoid deps if python-docx missing, 
        # but let's try direct first? No, let's use zipfile method to be safe/stock
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        # simplistic text extraction
        text = []
        NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        for node in tree.iter():
            if node.tag.endswith('}t'):
                if node.text:
                    text.append(node.text)
            elif node.tag.endswith('}p'):
               text.append('\n')
        print("".join(text)[:2000]) # Print first 2000 chars
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    read_xlsx_info(odk_path, "ODK FILE")
    read_xlsx_info(context_xlsx_path, "CONTEXT DATA")
    read_docx_text(docx_path)
