import json
import os

def validate_prueba():
    path = 'sample_data/prueba.json'
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    professors = data.get('professors', [])
    ids = [p['id'] for p in professors]
    
    print(f"Total professors: {len(professors)}")
    
    # Check duplicates
    if len(ids) != len(set(ids)):
        print("ERROR: Duplicate professor IDs found!")
        seen = set()
        dupes = set()
        for x in ids:
            if x in seen:
                dupes.add(x)
            seen.add(x)
        print(f"Duplicate IDs: {dupes}")
    else:
        print("No duplicate professor IDs.")

    # Check timeslots
    if 'time_slots' in data:
        print("Time slots found.")
        # Check for valid format
        for k, v in data['time_slots'].items():
            try:
                start, end = v.split('-')
                sh, sm = map(int, start.split(':'))
                eh, em = map(int, end.split(':'))
                if sh > eh or (sh == eh and sm >= em):
                    print(f"ERROR: Invalid time range for slot {k}: {v}")
            except ValueError:
                print(f"ERROR: Invalid format for slot {k}: {v}")

if __name__ == "__main__":
    validate_prueba()
