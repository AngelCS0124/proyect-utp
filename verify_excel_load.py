import sys
import os

# Add python_backend to path
sys.path.append(os.path.join(os.getcwd(), 'python_backend'))

from services.excel_extractor import extract_data_from_excel_to_memory

data_store = {
    'courses': [],
    'professors': [],
    'timeslots': []
}

file_path = os.path.join(os.getcwd(), 'sample_data', 'Horarios EneAbr18(1).xlsx')

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

print(f"Testing extraction from: {file_path}")
success = extract_data_from_excel_to_memory(file_path, data_store)

if success:
    print("Extraction successful!")
    print(f"Professors: {len(data_store['professors'])}")
    print(f"Courses: {len(data_store['courses'])}")
    print(f"Timeslots: {len(data_store['timeslots'])}")
    
    # Check for group_id and duration
    if data_store['courses']:
        c = data_store['courses'][0]
        print(f"Sample Course: {c.name}")
        print(f"  Group ID: {getattr(c, 'group_id', 'MISSING')}")
        print(f"  Credits/Duration: {getattr(c, 'credits', 'MISSING')}")
else:
    print("Extraction failed.")
    sys.exit(1)
