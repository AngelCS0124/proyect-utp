import sys
import os
import json
import csv

# Add python_backend to path
sys.path.append(os.path.abspath('python_backend'))

from data_loader import DataLoader
from scheduler_wrapper import PyScheduler

def reproduce():
    print("Initializing Scheduler...")
    scheduler = PyScheduler()

    # Load Timeslots
    print("Loading Timeslots...")
    timeslots = DataLoader.load_timeslots_from_json('sample_data/timeslots.json')
    for ts in timeslots:
        scheduler.load_timeslot(ts.id, ts.dia, ts.hora_inicio, ts.minuto_inicio, ts.hora_fin, ts.minuto_fin)

    # Load Professors
    print("Loading Professors...")
    professors_data = DataLoader.load_professors_from_json('sample_data/professors.json')
    professors = professors_data['professors']
    for p in professors:
        scheduler.load_professor(p.id, p.nombre, p.bloques_disponibles)

    # Load Courses
    print("Loading Courses...")
    courses = DataLoader.load_courses_from_csv('python_backend/courses_full.csv')
    
    # Assign Professors to Courses (Naive assignment based on availability)
    # In the real app, this might be done differently. 
    # We need to simulate how the app does it. 
    # Based on previous conversations, there might be a logic to assign professors.
    # For now, let's try to assign based on 'professor_id' in CSV if present, 
    # or find a capable professor.
    
    courses_to_schedule = []
    
    for c in courses:
        # Filter for a specific period if needed, but let's try to load all for now
        # or just a subset to test.
        # The user mentioned "courses_full.csv" has the data.
        
        # Infer group/semester from ID (e.g. 101 -> 1, 601 -> 6, 1001 -> 10)
        # Assuming last 2 digits are course number within semester
        try:
            group_id = int(str(c.id)[:-2])
        except:
            group_id = 1

        scheduler.load_course(c.id, c.nombre, c.matricula, c.prerequisitos, 
                              group_id=group_id, 
                              duration=int(c.creditos/15) if c.creditos else 4)
        
        if c.id_profesor:
             scheduler.assign_professor_to_course(c.id, c.id_profesor)
        else:
            # Try to find a professor who can teach this
            assigned = False
            for p in professors:
                # Check if p can teach c
                # The JSON has 'available_courses' which are course codes/names?
                # Let's check the data structure of professors.json again if needed.
                if str(c.id) in p.materias_capaces or c.nombre in p.materias_capaces:
                     scheduler.assign_professor_to_course(c.id, p.id)
                     assigned = True
                     break
            
            if not assigned:
                print(f"Warning: No professor found for course {c.nombre} ({c.id})")

    print("Generating Schedule (Optimization Mode)...")
    # Use 'complete' strategy to trigger the optimization loop
    result = scheduler.generate_schedule_with_config(time_limit_seconds=5, strategy="complete")
    
    print(f"Success: {result['success']}")
    print(f"Error: {result['error_message']}")
    print(f"Assignments: {len(result['assignments'])}")
    
    if len(result['assignments']) == 0:
        print("FAILURE: No assignments generated.")
    else:
        print("Partial or Full Schedule generated.")
        
        # Check for special courses
        special_ids = [601, 1001]
        assigned_ids = set(a['course_id'] for a in result['assignments'])
        
        for sid in special_ids:
            if sid in assigned_ids:
                print(f"SUCCESS: Special course {sid} was assigned.")
            else:
                print(f"WARNING: Special course {sid} was NOT assigned.")

if __name__ == "__main__":
    reproduce()
