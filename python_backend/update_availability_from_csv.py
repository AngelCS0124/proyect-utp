import pandas as pd
import json
import os

def parse_availability_csv(csv_path, output_path):
    # Read the CSV without header to handle the irregular structure
    df = pd.read_csv(csv_path, header=None)
    
    professors = []
    
    # Define time slot mapping based on timeslots.json
    # Format: "HH:MM-HH:MM" -> {day_index: base_id}
    # day_index: 0=L, 1=M, 2=Mi, 3=J, 4=V
    # base_id: 0=L, 100=M, 200=Mi, 300=J, 400=V
    
    time_map = {
        "7:00-7:55": 1,
        "7:55-8:50": 2,
        "8:50-9:45": 3,
        "9:45-10:40": 4,
        "11:10-12:05": 5,
        "12:05-13:00": 6,
        "13:00-13:55": 7,
        "14:00-14:55": 8,
        "14:55-15:50": 9,
        "15:50-16:45": 10,
        "16:45-17:40": 11,
        "18:00-18:55": 12,
        "18:55-19:50": 13,
        "19:50 – 20:45": 14,
        "19:50 - 20:45": 14
    }
    
    day_offsets = {
        0: 0,   # Lunes
        1: 100, # Martes
        2: 200, # Miércoles
        3: 300, # Jueves
        4: 400  # Viernes
    }
    
    # Function to process a block of professors
    def process_block(start_row, end_row, name_row_idx):
        # Iterate through columns to find professors
        # Professor names are in name_row_idx
        # Availability starts 2 rows below name
        
        num_cols = df.shape[1]
        col = 1 # Start from column 1 (column 0 is time)
        
        while col < num_cols:
            name = df.iloc[name_row_idx, col]
            
            if pd.isna(name) or str(name).strip() == "":
                col += 1
                continue
                
            # Found a professor
            prof_name = str(name).strip()
            print(f"Processing {prof_name}...")
            
            available_slots = []
            
            # Check 5 days (L, M, Mi, J, V)
            # Columns: col, col+1, col+2, col+3, col+4
            for day_idx in range(5):
                day_col = col + day_idx
                if day_col >= num_cols:
                    break
                    
                # Iterate through time rows
                for row_idx in range(start_row, end_row + 1):
                    time_str_raw = df.iloc[row_idx, 0]
                    if pd.isna(time_str_raw):
                        continue
                        
                    time_str = str(time_str_raw).strip()
                    # Handle potential encoding issues or variations
                    time_str = time_str.replace(" – ", "-").replace(" - ", "-")
                    
                    if time_str in time_map:
                        slot_num = time_map[time_str]
                        base_id = day_offsets[day_idx]
                        final_id = base_id + slot_num
                        
                        # Check availability marker "D"
                        marker = df.iloc[row_idx, day_col]
                        if str(marker).strip().upper() == 'D':
                            available_slots.append(final_id)
            
            professors.append({
                "id": len(professors) + 1,
                "name": prof_name,
                "email": "",
                "available_timeslots": available_slots
            })
            
            # Move to next professor (skip the 5 day columns + 1 empty column usually)
            col += 6 

    # Process first block
    # Names at row 0, Data from row 2 to 19 (approx)
    # Actually, let's look at the file content again.
    # Row 0 (index): Names
    # Row 2 (index): Start of data "7:00-7:55"
    # Row 19 (index): End of data "19:50 – 20:45" (we only care up to 15:50 for now, but let's scan all)
    process_block(2, 19, 0)
    
    # Process second block
    # Names at row 20 (index)
    # Data from row 22 (index) to end
    process_block(22, 38, 20)
    
    # Add placeholder professors
    all_slots = []
    for day_offset in day_offsets.values():
        for slot_num in range(1, 15):
            all_slots.append(day_offset + slot_num)
            
    placeholders = ["Maestro Ingles", "Maestro Valores"]
    for ph_name in placeholders:
        professors.append({
            "id": len(professors) + 1,
            "name": ph_name,
            "email": "",
            "available_timeslots": all_slots
        })
        print(f"Added {ph_name} with full availability.")

    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(professors, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully generated {output_path} with {len(professors)} professors.")

if __name__ == "__main__":
    csv_file = '../sample_data/Disponibilidad - Disponibilidad(1).csv'
    json_file = '../sample_data/professors.json'
    
    # Adjust paths if running from python_backend directory
    if not os.path.exists(csv_file):
        csv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'Disponibilidad - Disponibilidad(1).csv')
        json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'professors.json')
        
    parse_availability_csv(csv_file, json_file)
