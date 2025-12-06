import pandas as pd
import os
import csv
from typing import List, Dict, Any

from models import Professor, Course, TimeSlot

def extract_data_from_excel_to_memory(file_path: str, data_store: Dict[str, Any]) -> bool:
    """
    Extracts professors and courses from the 'Matriz ITI' sheet directly into data_store.
    """
    print(f"Extracting data from {file_path}...")
    
    try:
        # Load the specific sheet
        df = pd.read_excel(file_path, sheet_name='Matriz ITI', header=None)
        
        professors = []
        prof_col_map = {} # Map column index to professor ID
        
        # Find the row with professor names
        prof_row_idx = -1
        for i in range(10):
            row_values = [str(x) for x in df.iloc[i].tolist()]
            if any("Recher" in x for x in row_values):
                prof_row_idx = i
                break
        
        if prof_row_idx == -1:
            print("Could not find professor row.")
            return False
            
        current_id = 1
        # Iterate through columns to find professors
        for col_idx in range(5, df.shape[1]):
            val = df.iloc[prof_row_idx, col_idx]
            if pd.notna(val) and isinstance(val, str) and val.strip() != "Horas Cubiertas":
                name = val.strip()
                # USER REQUEST: Full availability for all days (1-35)
                # Assuming 5 days * 7 slots = 35 slots
                full_availability = [i for i in range(1, 36)]
                
                prof = Professor(
                    id=current_id,
                    name=name,
                    email=f"professor{current_id}@university.edu",
                    available_timeslots=full_availability
                )
                professors.append(prof)
                prof_col_map[col_idx] = current_id
                current_id += 1
        
        # Ensure "Maestro Asignado" exists for unassigned courses
        maestro_asignado_id = None
        # Check if already exists
        for p in professors:
            if "Maestro Asignado" in p.name:
                maestro_asignado_id = p.id
                break
        
        if not maestro_asignado_id:
            maestro_asignado_id = current_id
            professors.append(Professor(
                id=maestro_asignado_id,
                name="Maestro Asignado",
                email="asignado@university.edu",
                available_timeslots=[i for i in range(1, 36)]
            ))
            current_id += 1

        # Extract Courses
        courses = []
        course_start_row = prof_row_idx + 5 # Approximation based on dump
        current_course_id = 1
        current_semester = 1 # Default to 1st semester
        
        semester_map = {
            "Primer Cuatrimestre": 1,
            "Segundo Cuatrimestre": 2,
            "Tercer Cuatrimestre": 3,
            "Cuarto Cuatrimestre": 4,
            "Quinto Cuatrimestre": 5,
            "Sexto Cuatrimestre": 6,
            "Séptimo Cuatrimestre": 7,
            "Octavo Cuatrimestre": 8,
            "Noveno Cuatrimestre": 9,
            "Décimo Cuatrimestre": 10
        }
        
        for row_idx in range(course_start_row, df.shape[0]):
            course_name_val = df.iloc[row_idx, 0]
            
            if pd.isna(course_name_val):
                continue
                
            course_name = str(course_name_val).strip()
            
            # Check if this row is a semester header
            if course_name in semester_map:
                current_semester = semester_map[course_name]
                print(f"Found semester header: {course_name} -> {current_semester}")
                continue
            
            if course_name in ["Horas Asignadas"]:
                continue
            
            hours_val = df.iloc[row_idx, 2]
            if pd.isna(hours_val):
                continue
                
            try:
                hours = int(hours_val)
            except:
                hours = 3
            
            assigned_prof_id = None
            for col_idx, prof_id in prof_col_map.items():
                assigned_hours = df.iloc[row_idx, col_idx]
                if pd.notna(assigned_hours) and assigned_hours > 0:
                    assigned_prof_id = prof_id
                    break
            
            # If no professor assigned, use "Maestro Asignado"
            if not assigned_prof_id:
                assigned_prof_id = maestro_asignado_id

            # Use semester as group_id for now (assuming 1 group per semester)
            group_id = current_semester
            
            course = Course(
                id=current_course_id,
                name=course_name,
                code=f"SUBJ{current_course_id:03d}",
                credits=hours,
                enrollment=30,
                prerequisites=[],
                professor_id=assigned_prof_id,
                semester=current_semester,
                group_id=group_id
            )
            courses.append(course)
            current_course_id += 1
            
        # Update data_store
        data_store['professors'] = professors
        data_store['courses'] = courses
        data_store['timeslots'] = [] # Clear timeslots or load default?
        
        # Load default timeslots if empty
        if not data_store['timeslots']:
             # 3. Generate TimeSlots
            days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
            ts_id = 1
            for day in days:
                for hour in range(7, 21, 2):
                    data_store['timeslots'].append(TimeSlot(
                        id=ts_id, 
                        day=day, 
                        start_hour=hour, 
                        start_minute=0, 
                        end_hour=hour + 2, 
                        end_minute=0
                    ))
                    ts_id += 1
        
        return True
        
    except Exception as e:
        print(f"Error extracting data: {e}")
        return False

if __name__ == "__main__":
    # This block would typically be in a main application file
    # For demonstration, we'll create a dummy data_store
    class Professor:
        def __init__(self, id, name, email, available_timeslots):
            self.id = id
            self.name = name
            self.email = email
            self.available_timeslots = available_timeslots
    
    class Course:
        def __init__(self, id, name, code, credits, enrollment, prerequisites, professor_id):
            self.id = id
            self.name = name
            self.code = code
            self.credits = credits
            self.enrollment = enrollment
            self.prerequisites = prerequisites
            self.professor_id = professor_id

    class TimeSlot:
        def __init__(self, id, day, start_hour, start_minute, end_hour, end_minute):
            self.id = id
            self.day = day
            self.start_hour = start_hour
            self.start_minute = start_minute
            self.end_hour = end_hour
            self.end_minute = end_minute

    # Create a dummy models.py for local testing if it doesn't exist
    if not os.path.exists('models.py'):
        with open('models.py', 'w') as f:
            f.write("""
from typing import List, Optional

class Professor:
    def __init__(self, id: int, name: str, email: str, available_timeslots: str):
        self.id = id
        self.name = name
        self.email = email
        self.available_timeslots = available_timeslots

class Course:
    def __init__(self, id: int, name: str, code: str, credits: int, enrollment: int, prerequisites: List[int], professor_id: Optional[int]):
        self.id = id
        self.name = name
        self.code = code
        self.credits = credits
        self.enrollment = enrollment
        self.prerequisites = prerequisites
        self.professor_id = professor_id

class TimeSlot:
    def __init__(self, id: int, day: str, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        self.id = id
        self.day = day
        self.start_hour = start_hour
        self.start_minute = start_minute
        self.end_hour = end_hour
        self.end_minute = end_minute
""")
    
    # Ensure sample_data directory and file exist for testing
    if not os.path.exists('sample_data'):
        os.makedirs('sample_data')
    # You would need to place 'Horarios EneAbr18(1).xlsx' in 'sample_data' for this to run
    # For a real test, you'd mock the pandas read_excel call or provide a dummy Excel file.
    
    # Example usage:
    data = {}
    success = extract_data_from_excel_to_memory('sample_data/Horarios EneAbr18(1).xlsx', data)
    
    if success:
        print("\nData extracted successfully into memory:")
        print(f"Professors found: {len(data.get('professors', []))}")
        print(f"Courses found: {len(data.get('courses', []))}")
        print(f"Timeslots generated: {len(data.get('timeslots', []))}")
        # print("First professor:", data['professors'][0].name if data['professors'] else "N/A")
        # print("First course:", data['courses'][0].name if data['courses'] else "N/A")
    else:
        print("\nData extraction failed.")
