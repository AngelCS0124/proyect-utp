import sys
import os
import csv

# Add python_backend to path
sys.path.append(os.path.abspath('python_backend'))

from config.periods import PERIODOS, get_valid_groups
from modelos import Curso

def load_courses_mock():
    # Simulate loading from courses_full.csv
    courses = []
    filepath = 'python_backend/courses_full.csv'
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Note: In data_loader.py, IDs are converted to int. 
            # Let's verify if that happens correctly.
            try:
                c_id = int(float(row['id']))
                courses.append(Curso(id=c_id, nombre=row['name'], codigo=row['code'], creditos=int(float(row['credits'])), matricula=30, prerequisitos=[]))
            except ValueError:
                continue
    return courses

def reproduce():
    print("Reproducing Period Selection Logic...")
    
    # 1. Load Courses
    courses = load_courses_mock()
    print(f"Loaded {len(courses)} courses.")
    
    # 2. Select Period
    period = "sept-dec" # Default
    print(f"Selected Period: {period}")
    
    # 3. Get Valid IDs
    valid_ids = get_valid_groups(period)
    print(f"Valid IDs for {period}: {valid_ids[:10]}... ({len(valid_ids)} total)")
    
    # 4. Filter
    filtered_courses = []
    for c in courses:
        if c.id in valid_ids:
            filtered_courses.append(c)
            
    print(f"Filtered Courses: {len(filtered_courses)}")
    
    if len(filtered_courses) == 0:
        print("FAILURE: No courses found for period.")
        
        # Debugging
        print("\nDebugging:")
        print(f"Sample Course ID type: {type(courses[0].id)} value: {courses[0].id}")
        print(f"Sample Valid ID type: {type(valid_ids[0])} value: {valid_ids[0]}")
    else:
        print("SUCCESS: Courses found.")

if __name__ == "__main__":
    reproduce()
