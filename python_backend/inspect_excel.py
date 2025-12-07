import pandas as pd
import os

def inspect_excel():
    file_path = '../sample_data/Horarios EneAbr18(1).xlsx'
    if not os.path.exists(file_path):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'Horarios EneAbr18(1).xlsx')
    
    print(f"Reading {file_path}...")
    
    # Read all sheets
    xls = pd.ExcelFile(file_path)
    print(f"Sheets: {xls.sheet_names}")
    
    df = pd.read_excel(file_path, sheet_name='Matriz ITI', header=None)
    
    target = "Marina"
    print(f"Searching for '{target}' in Matriz ITI...")
    
    # Inspect Row 7 (Algoritmos)
    row_idx = 7
    print(f"\nInspecting Row {row_idx} ({df.iloc[row_idx, 0]}):")
    for col in range(5, 40):
        val = df.iloc[row_idx, col]
        if pd.notna(val) and val != 0:
            prof_name = df.iloc[1, col]
            print(f"Col {col}: {val} (Assigned to: {prof_name})")

if __name__ == "__main__":
    inspect_excel()
