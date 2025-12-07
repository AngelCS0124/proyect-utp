import csv
import os

def clean_csv():
    filepath = '/home/gina/Documentos/EstDatos/proyect-utp/python_backend/courses_full.csv'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
        
    # Columns to clear
    cols_to_clear = ['enrollment', 'prerequisites', 'professor_id']
    
    cleaned_rows = []
    for row in rows:
        for col in cols_to_clear:
            if col in row:
                row[col] = ''
        cleaned_rows.append(row)
        
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
        
    print(f"Cleaned {len(cleaned_rows)} rows in {filepath}")

if __name__ == "__main__":
    clean_csv()
