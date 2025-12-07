import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'python_backend'))

from python_backend.scheduler_wrapper import PyScheduler
from python_backend.data_loader import DataLoader
from python_backend.config.periods import get_valid_groups

def test_scheduler():
    print("Testing robust scheduler...")
    
    # Load data
    base_dir = os.path.join(os.getcwd(), 'python_backend')
    courses_path = os.path.join(base_dir, 'courses_full.csv')
    professors_path = os.path.join(os.getcwd(), 'sample_data', 'professors.json')
    timeslots_path = os.path.join(os.getcwd(), 'sample_data', 'timeslots.json')
    
    courses = DataLoader.load_courses_from_csv(courses_path)
    professors_data = DataLoader.load_professors_from_json(professors_path)
    if isinstance(professors_data, dict):
        professors = professors_data['professors']
        timeslots = professors_data.get('timeslots')
    else:
        professors = professors_data
        timeslots = None
        
    if not timeslots:
        timeslots = DataLoader.load_timeslots_from_json(timeslots_path)
        
    print(f"Loaded {len(courses)} courses, {len(professors)} professors, {len(timeslots)} timeslots")
    
    # Filter for sep_dic
    valid_ids = get_valid_groups('sep_dic')
    courses_to_schedule = [c for c in courses if c.id in valid_ids]
    print(f"Courses for sep_dic: {len(courses_to_schedule)}")
    
    # Initialize scheduler
    scheduler = PyScheduler()
    
    # Load into scheduler
    # IMPORTANT: Load timeslots first so professors can reference them
    for t in timeslots:
        scheduler.load_timeslot(t.id, t.dia, t.hora_inicio, t.minuto_inicio, t.hora_fin, t.minuto_fin)

    for c in courses_to_schedule:
        duration = 4 # simplified
        scheduler.load_course(c.id, c.nombre, c.matricula, c.prerequisitos, getattr(c, 'group_id', 0), duration)
        
    for p in professors:
        scheduler.load_professor(p.id, p.nombre, p.bloques_disponibles)
        
    # Assign professors (naive assignment for testing if not already assigned)
    # courses_full.csv has professor_id but it might be empty
    # We match using course.codigo and professor.materias_capaces (which comes from available_courses)
    
    assigned_count = 0
    for c in courses_to_schedule:
        if c.id_profesor:
            scheduler.assign_professor_to_course(c.id, c.id_profesor)
            assigned_count += 1
        else:
            # Find a professor who can teach this course
            # c.codigo is the code (e.g. "ING1")
            # p.materias_capaces is list of codes
            
            # We need to access the raw professor object or dictionary
            # DataLoader returns Profesor objects which have materias_capaces
            
            candidate = None
            for p in professors:
                if c.codigo in p.materias_capaces:
                    candidate = p
                    break
            
            if candidate:
                scheduler.assign_professor_to_course(c.id, candidate.id)
                assigned_count += 1
                # print(f"Assigned {candidate.nombre} to {c.nombre} ({c.codigo})")
            else:
                print(f"Warning: No professor found for {c.nombre} ({c.codigo})")
            
    print(f"Assigned professors to {assigned_count} courses")
    
    # Generate
    print("Generating schedule...")
    result = scheduler.generate_schedule()
    
    print(f"Result success: {result['success']}")
    print(f"Assignments: {len(result['assignments'])}")
    print(f"Error message: {result['error_message']}")
    
    if len(result['assignments']) > 0:
        print("SUCCESS: Partial schedule generated!")
    else:
        print("FAILURE: No assignments generated.")

if __name__ == "__main__":
    test_scheduler()
