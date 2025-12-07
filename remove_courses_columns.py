import csv
import os

def remove_columns():
    filepath = '/home/gina/Documentos/EstDatos/proyect-utp/python_backend/courses_full.csv'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    # New fieldnames
    fieldnames = ['id', 'name', 'code', 'credits']
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            new_row = {k: row[k] for k in fieldnames if k in row}
            writer.writerow(new_row)
        
    print(f"Updated {filepath} with columns: {fieldnames}")

if __name__ == "__main__":
    remove_columns()
