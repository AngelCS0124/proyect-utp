import pandas as pd
import json
import os
from difflib import get_close_matches

def fix_assignments():
    # Paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    excel_path = os.path.join(base_dir, 'sample_data', 'Horarios EneAbr18(1).xlsx')
    json_path = os.path.join(base_dir, 'sample_data', 'professors.json')
    csv_path = os.path.join(base_dir, 'sample_data', 'courses.csv')
    
    # Load Professors
    with open(json_path, 'r', encoding='utf-8') as f:
        professors = json.load(f)
    
    # Create Name -> ID map
    prof_map = {p['name']: p['id'] for p in professors}
    prof_names = list(prof_map.keys())
    
    # Find placeholder IDs
    english_id = next((p['id'] for p in professors if "Maestro Ingles" in p['name']), None)
    values_id = next((p['id'] for p in professors if "Maestro Valores" in p['name']), None)
    
    print(f"Placeholder IDs - English: {english_id}, Values: {values_id}")
    
    # Load Excel
    print("Reading Excel...")
    df_excel = pd.read_excel(excel_path, sheet_name='Matriz ITI', header=None)
    
    # Extract Professor Names from Row 1 (Index 1)
    # Columns 5 to end
    excel_prof_names = {} # col_idx -> name
    for col in range(5, df_excel.shape[1]):
        val = df_excel.iloc[1, col]
        if pd.notna(val) and isinstance(val, str):
            excel_prof_names[col] = val.strip()
            
    # Load Courses CSV
    print("Reading Courses CSV...")
    df_courses = pd.read_csv(csv_path)
    
    # Iterate and Update
    updated_count = 0
    
    for idx, row in df_courses.iterrows():
        course_name = row['name']
        
        # Special cases
        if "Inglés" in course_name or "Ingles" in course_name:
            if english_id:
                df_courses.at[idx, 'professor_id'] = english_id
                print(f"Assigned {course_name} to Maestro Ingles ({english_id})")
                updated_count += 1
            continue
            
        if "Valores" in course_name:
            if values_id:
                df_courses.at[idx, 'professor_id'] = values_id
                print(f"Assigned {course_name} to Maestro Valores ({values_id})")
                updated_count += 1
            continue
            
        # Find course in Excel
        # Search in Column 0
        excel_row_idx = -1
        for r_idx, val in df_excel[0].items():
            if isinstance(val, str) and val.strip() == course_name.strip():
                excel_row_idx = r_idx
                break
        
        if excel_row_idx == -1:
            print(f"Warning: Course '{course_name}' not found in Excel")
            continue
            
        # Find assigned professor column
        assigned_prof_name = None
        for col, prof_name in excel_prof_names.items():
            val = df_excel.iloc[excel_row_idx, col]
            if pd.notna(val) and val != 0:
                assigned_prof_name = prof_name
                break
        
        if not assigned_prof_name:
            print(f"Warning: No professor assigned for '{course_name}' in Excel")
            continue
            
        # Match Excel Name to JSON Name
        matched_id = None
        
        # 1. Substring matching (Normalized)
        n_excel = assigned_prof_name.lower().replace('.', '').replace('  ', ' ')
        
        for json_name, pid in prof_map.items():
            n_json = json_name.lower().replace('.', '').replace('  ', ' ')
            
            # Check if one is contained in the other
            # e.g. "jose fidencio" in "msi jose fidencio lopez luna"
            if n_json in n_excel:
                matched_id = pid
                print(f"Substring Match '{assigned_prof_name}' -> '{json_name}' (ID: {matched_id})")
                break
        
        # 2. First + Last name matching
        if not matched_id:
            for json_name, pid in prof_map.items():
                # Clean names
                clean_json = json_name.replace('.', '').replace(',', '').split()
                clean_excel = assigned_prof_name.replace('.', '').replace(',', '').split()
                
                if len(clean_json) >= 2:
                    first = clean_json[0].lower()
                    last = clean_json[-1].lower()
                    
                    # Check if first and last appear in excel name
                    excel_lower = [p.lower() for p in clean_excel]
                    if first in excel_lower and last in excel_lower:
                        matched_id = pid
                        print(f"First/Last Match '{assigned_prof_name}' -> '{json_name}' (ID: {matched_id})")
                        break
        
        if matched_id:
             df_courses.at[idx, 'professor_id'] = matched_id
             updated_count += 1
             continue

        # Use difflib to find closest match
        # Increase cutoff to avoid bad matches (e.g. Hector Hugo -> Hugo Camargo)
        matches = get_close_matches(assigned_prof_name, prof_names, n=1, cutoff=0.6)
        
        if matches:
            matched_name = matches[0]
            matched_id = prof_map[matched_name]
            print(f"Matched '{assigned_prof_name}' -> '{matched_name}' (ID: {matched_id})")
            
            df_courses.at[idx, 'professor_id'] = matched_id
            updated_count += 1
        else:
            print(f"Warning: Could not match professor '{assigned_prof_name}' to any JSON professor")
            # Fallback to PA if exists
            pa_id = next((p['id'] for p in professors if p['name'] == "PA"), None)
            if pa_id:
                print(f"Fallback: Assigned '{assigned_prof_name}' courses to PA ({pa_id})")
                df_courses.at[idx, 'professor_id'] = pa_id
                updated_count += 1
            else:
                # Fallback to Maestro Valores as last resort
                if values_id:
                     df_courses.at[idx, 'professor_id'] = values_id
                     updated_count += 1

    # Save CSV
    df_courses.to_csv(csv_path, index=False)
    print(f"Updated {updated_count} assignments in {csv_path}")

if __name__ == "__main__":
    fix_assignments()
