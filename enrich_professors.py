import json
import csv
import random
import os

PROFESSORS_FILE = 'sample_data/professors.json'
COURSES_FILE = 'python_backend/courses_full.csv'

def load_courses():
    courses = []
    with open(COURSES_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            courses.append(row)
    return courses

def load_professors():
    with open(PROFESSORS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_professors(professors):
    with open(PROFESSORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(professors, f, indent=4, ensure_ascii=False)

def enrich_data():
    courses = load_courses()
    professors = load_professors()
    
    # Map course code to list of professors who can teach it
    course_professors = {}
    for c in courses:
        code = c['code']
        course_professors[code] = []
        for p in professors:
            if code in p.get('available_courses', []):
                course_professors[code].append(p['id'])
    
    print("Current coverage:")
    for code, profs in course_professors.items():
        print(f"{code}: {len(profs)} professors")
        
    # Enrich
    for c in courses:
        code = c['code']
        current_profs = course_professors[code]
        
        if len(current_profs) < 3:
            needed = 3 - len(current_profs)
            print(f"Enriching {code} (has {len(current_profs)}, adding {needed})")
            
            # Find professors who don't teach this course yet
            candidates = [p for p in professors if p['id'] not in current_profs]
            
            # Prefer professors with fewer courses assigned to balance load
            candidates.sort(key=lambda p: len(p.get('available_courses', [])))
            
            # Take top candidates
            chosen = candidates[:needed]
            
            for p in chosen:
                if 'available_courses' not in p:
                    p['available_courses'] = []
                p['available_courses'].append(code)
                print(f"  -> Assigned to {p['name']}")

    save_professors(professors)
    print("Done enriching professors.json")

if __name__ == '__main__':
    enrich_data()
