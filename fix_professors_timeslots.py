import json
import os

def fix_professors():
    # Paths
    base_dir = '/home/gina/Documentos/EstDatos/proyect-utp'
    timeslots_path = os.path.join(base_dir, 'sample_data/timeslots.json')
    professors_path = os.path.join(base_dir, 'sample_data/professors.json')
    
    # 1. Load Timeslots and identify valid IDs and last hours
    with open(timeslots_path, 'r', encoding='utf-8') as f:
        timeslots = json.load(f)
        
    valid_ids = set(ts['id'] for ts in timeslots)
    
    # Group by day to find last hour
    day_slots = {}
    for ts in timeslots:
        day = ts['day']
        if day not in day_slots:
            day_slots[day] = []
        day_slots[day].append(ts)
        
    last_hour_ids = []
    for day, slots in day_slots.items():
        # Sort by start hour/minute to find the last one
        slots.sort(key=lambda x: (x['start_hour'], x['start_minute']))
        if slots:
            last_hour_ids.append(slots[-1]['id'])
            
    print(f"Valid Timeslot IDs count: {len(valid_ids)}")
    print(f"Last Hour IDs: {last_hour_ids}")
    
    # 2. Load Professors
    with open(professors_path, 'r', encoding='utf-8') as f:
        professors = json.load(f)
        
    # 3. Filter and Update
    modified_count = 0
    empty_count = 0
    
    for prof in professors:
        original_slots = prof.get('available_timeslots', [])
        # Filter
        new_slots = [sid for sid in original_slots if sid in valid_ids]
        
        if len(new_slots) != len(original_slots):
            modified_count += 1
            
        # Check if empty
        if not new_slots:
            new_slots = list(last_hour_ids)
            empty_count += 1
            print(f"Professor {prof['name']} (ID {prof['id']}) had no valid slots. Assigned last hours.")
            
        prof['available_timeslots'] = new_slots
        
    # 4. Save
    with open(professors_path, 'w', encoding='utf-8') as f:
        json.dump(professors, f, indent=4, ensure_ascii=False)
        
    print(f"Process complete.")
    print(f"Professors modified: {modified_count}")
    print(f"Professors assigned default slots: {empty_count}")

if __name__ == "__main__":
    fix_professors()
