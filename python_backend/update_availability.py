import pandas as pd
import json
import os
import re
import csv

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, '../sample_data/Disponibilidad.xlsx')
CSV_PATH = os.path.join(BASE_DIR, '../sample_data/professors.csv')
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, '../sample_data/professors.json')

def normalize_name(name):
    """Normalize name for comparison: lowercase, remove titles, extra spaces."""
    if not isinstance(name, str):
        return ""
    name = name.lower()
    # Remove common titles
    name = re.sub(r'\b(dr\.|dra\.|m\.c\.|m\.i\.|ing\.|lic\.|m\.s\.i\.|m\.a\.t\.|m\.t\.i\.)\s*', '', name)
    # Remove content in parenthesis (e.g., (ITI))
    name = re.sub(r'\s*\(.*?\)', '', name)
    # Remove middle initials if they are just one letter with dot
    name = re.sub(r'\s+[a-z]\.\s+', ' ', name)
    return " ".join(name.split())

def load_professors_from_csv():
    professors = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            professors.append({
                "id": int(row['id']),
                "name": row['name'],
                "email": row.get('email', ''),
                "available_timeslots": [] # Will be populated from Excel
            })
    return professors

def update_availability():
    professors = load_professors_from_csv()
    df = pd.read_excel(EXCEL_PATH, header=None)
    
    # Map Excel columns to professors
    excel_professors = {}
    num_cols = df.shape[1]
    
    # Row 0 has names. Stride is 6 columns per professor (Mon-Sat)
    # But we only care about Mon-Fri (5 columns)
    for col_idx in range(1, num_cols, 6):
        raw_name = df.iloc[0, col_idx]
        if pd.isna(raw_name):
            continue
            
        norm_name = normalize_name(str(raw_name))
        excel_professors[norm_name] = col_idx

    print(f"Found {len(excel_professors)} professors in Excel.")
    
    # Row to Slot ID mapping
    # Excel Row Index -> Slot ID (1-based)
    row_to_slot = {
        3: 1,
        4: 2,
        5: 3,
        6: 4,
        7: 5,
        8: 6,
        9: 7,
        10: 8,
        11: 9,
        12: 10,
        13: 11,
        # 14 is duplicate of 11? Skip
        16: 12,
        17: 13,
        18: 14
    }
    
    matched_count = 0
    
    for prof in professors:
        prof_name = prof['name']
        norm_prof_name = normalize_name(prof_name)
        
        # Try to find a match
        match_col = None
        
        if norm_prof_name in excel_professors:
            match_col = excel_professors[norm_prof_name]
        else:
            # Fuzzy match
            best_match = None
            max_overlap = 0
            
            for excel_name, col in excel_professors.items():
                parts_excel = set(excel_name.split())
                parts_json = set(norm_prof_name.split())
                overlap = len(parts_excel.intersection(parts_json))
                
                if overlap >= 2 and overlap > max_overlap:
                    max_overlap = overlap
                    best_match = col
            
            if best_match:
                match_col = best_match
        
        if match_col is not None:
            matched_count += 1
            new_slots = []
            
            # Iterate through mapped rows
            for row_idx, slot_base in row_to_slot.items():
                if row_idx >= df.shape[0]:
                    continue
                
                # Check Mon-Fri (offsets 0-4)
                for day_offset in range(5):
                    col = match_col + day_offset
                    if col >= df.shape[1]:
                        continue
                        
                    val = df.iloc[row_idx, col]
                    
                    if str(val).strip().upper() == 'D':
                        # Calculate absolute slot ID
                        # Mon: 1-14, Tue: 101-114, ...
                        # Day offsets: 0=Mon, 1=Tue, ...
                        day_id_offset = day_offset * 100
                        abs_slot_id = day_id_offset + slot_base
                        new_slots.append(abs_slot_id)
            
            prof['available_timeslots'] = sorted(new_slots)
            print(f"Updated {prof_name} with {len(new_slots)} slots.")
        else:
            print(f"WARNING: No match found for {prof_name}")
            # If no match, maybe give full availability or none?
            # User said "de momento todos estan disponibles para ver si funciona" in the prompt,
            # but then said "los verdaderos datos... estan en este excel".
            # I'll leave it empty if not found, or maybe default to all?
            # Let's default to ALL if not found, to be safe for testing?
            # No, better to be strict. If not in Excel, they might not be teaching.
            pass

    print(f"Total matched: {matched_count}/{len(professors)}")
    
    # Save updated JSON
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(professors, f, indent=4, ensure_ascii=False)
    print(f"Saved to {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    update_availability()
