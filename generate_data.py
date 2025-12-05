import csv
import os

# Ensure sample_data directory exists
os.makedirs('sample_data', exist_ok=True)

# 1. Generate Professors (5 Professors)
# Full availability for everyone to ensure solvability
full_availability = ",".join([str(i) for i in range(1, 36)])

professors = [
    {"id": 1, "name": "Dr. Said", "email": "said@university.edu", "available_timeslots": full_availability},
    {"id": 2, "name": "Dr. Alicia Romero", "email": "a.romero@university.edu", "available_timeslots": full_availability},
    {"id": 3, "name": "Prof. Marco Silva", "email": "m.silva@university.edu", "available_timeslots": full_availability},
    {"id": 4, "name": "Dr. Meera Patel", "email": "m.patel@university.edu", "available_timeslots": full_availability},
    {"id": 5, "name": "Mtro. Luis Roberto", "email": "l.roberto@university.edu", "available_timeslots": full_availability}
]

with open('sample_data/professors.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "email", "available_timeslots"])
    writer.writeheader()
    writer.writerows(professors)

print("Generated sample_data/professors.csv")

# 2. Generate Courses (5 Courses, 1 per Professor)
# This 1-to-1 mapping guarantees no conflicts if availability is full
courses = [
    [1, "Matemáticas Discretas", "MAT101", 3, 30, "", 1], # Assigned to Dr. Said
    [2, "Estructura de Datos", "CS102", 4, 25, "1", 2],   # Assigned to Dr. Alicia
    [3, "Inglés I", "LANG101", 2, 20, "", 3],             # Assigned to Prof. Marco
    [4, "Programación Web", "CS201", 3, 30, "2", 4],      # Assigned to Dr. Meera
    [5, "Base de Datos", "CS202", 3, 28, "2", 5]          # Assigned to Mtro. Luis
]

with open('sample_data/courses.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'code', 'credits', 'enrollment', 'prerequisites', 'professor_id'])
    writer.writerows(courses)

print("Generated sample_data/courses.csv")

# 3. Generate TimeSlots
days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
timeslots = []
ts_id = 1
for day in days:
    # 7 blocks per day
    for hour in range(7, 21, 2): # 7, 9, 11, 13, 15, 17, 19
        timeslots.append({
            "id": ts_id, 
            "day": day, 
            "start_hour": hour, 
            "start_minute": 0, 
            "end_hour": hour + 2, 
            "end_minute": 0
        })
        ts_id += 1

with open('sample_data/timeslots.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "day", "start_hour", "start_minute", "end_hour", "end_minute"])
    writer.writeheader()
    writer.writerows(timeslots)

print("Generated sample_data/timeslots.csv")
