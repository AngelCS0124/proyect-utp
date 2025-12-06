import pandas as pd
import os

file_path = 'sample_data/Horarios EneAbr18(1).xlsx'

try:
    xls = pd.ExcelFile(file_path)
    with open('excel_dump.txt', 'w') as f:
        f.write(f"Sheet names: {xls.sheet_names}\n")
        
        for sheet_name in xls.sheet_names:
            f.write(f"\n--- Sheet: {sheet_name} ---\n")
            df = pd.read_excel(xls, sheet_name=sheet_name, nrows=20)
            f.write(df.to_string())
            f.write("\n" + "-" * 30 + "\n")
            
except Exception as e:
    with open('excel_dump.txt', 'w') as f:
        f.write(f"Error reading Excel file: {e}")
