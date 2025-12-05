import csv
import os
import random

# Ensure sample_data directory exists
os.makedirs('sample_data', exist_ok=True)

# 1. Generate Courses
courses = [
    {"id": 1, "name": "Estructura de Datos", "code": "ITI-301", "credits": 5, "enrollment": 30, "prerequisites": ""},
    {"id": 2, "name": "Inglés I", "code": "ING-101", "credits": 3, "enrollment": 25, "prerequisites": ""},
    {"id": 3, "name": "Programación Web", "code": "ITI-302", "credits": 5, "enrollment": 28, "prerequisites": "1"},
    {"id": 4, "name": "Base de Datos", "code": "ITI-303", "credits": 5, "enrollment": 30, "prerequisites": ""},
    {"id": 5, "name": "Redes de Computadoras", "code": "ITI-401", "credits": 5, "enrollment": 25, "prerequisites": ""},
    {"id": 6, "name": "Sistemas Operativos", "code": "ITI-402", "credits": 5, "enrollment": 28, "prerequisites": ""},
    {"id": 7, "name": "Ingeniería de Software", "code": "ITI-501", "credits": 5, "enrollment": 30, "prerequisites": "3,4"},
    {"id": 8, "name": "Matemáticas Discretas", "code": "MAT-101", "credits": 4, "enrollment": 35, "prerequisites": ""},
]

with open('sample_data/courses.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "code", "credits", "enrollment", "prerequisites"])
    writer.writeheader()
    writer.writerows(courses)

print("Generated sample_data/courses.csv")

# 2. Generate Professors
# Based on screenshots/inferred
professors = [
    {"id": 1, "name": "Dr. Said", "email": "said@university.edu", "available_timeslots": "1,2,3,4,5,6,7,8,9,10"},
    {"id": 2, "name": "Dr. Alicia Romero", "email": "a.romero@university.edu", "available_timeslots": "1,2,3,4,5,11,12,13,14,15"},
    {"id": 3, "name": "Prof. Marco Silva", "email": "m.silva@university.edu", "available_timeslots": "6,7,8,9,10,16,17,18,19,20"},
    {"id": 4, "name": "Dr. Meera Patel", "email": "m.patel@university.edu", "available_timeslots": "1,3,5,7,9,11,13,15,17,19"},
    {"id": 5, "name": "Mtro. Luis Roberto", "email": "l.roberto@university.edu", "available_timeslots": "2,4,6,8,10,12,14,16,18,20"},
    {"id": 6, "name": "Mtra. Gloria", "email": "gloria@university.edu", "available_timeslots": "1,2,3,4,5,6,7,8,9,10"},
    {"id": 7, "name": "Mtro. Mario", "email": "mario@university.edu", "available_timeslots": "11,12,13,14,15,16,17,18,19,20"},
    {"id": 8, "name": "Mtra. Vanessa", "email": "vanessa@university.edu", "available_timeslots": "1,3,5,7,9,11,13,15,17,19"},
    {"id": 9, "name": "Mtro. Nuño", "email": "nuno@university.edu", "available_timeslots": "2,4,6,8,10,12,14,16,18,20"},
]

with open('sample_data/professors.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "email", "available_timeslots"])
    writer.writeheader()
    writer.writerows(professors)

print("Generated sample_data/professors.csv")

# 3. Generate TimeSlots
# Standard slots: Mon-Fri, 7am-9pm, 2 hour blocks roughly
days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
timeslots = []
ts_id = 1
for day in days:
    # 7:00 - 9:00
    timeslots.append({"id": ts_id, "day": day, "start_hour": 7, "start_minute": 0, "end_hour": 9, "end_minute": 0})
    ts_id += 1
    # 9:00 - 11:00
    timeslots.append({"id": ts_id, "day": day, "start_hour": 9, "start_minute": 0, "end_hour": 11, "end_minute": 0})
    ts_id += 1
    # 11:00 - 13:00
    timeslots.append({"id": ts_id, "day": day, "start_hour": 11, "start_minute": 0, "end_hour": 13, "end_minute": 0})
    ts_id += 1
    # 13:00 - 15:00
    timeslots.append({"id": ts_id, "day": day, "start_hour": 13, "start_minute": 0, "end_hour": 15, "end_minute": 0})
    ts_id += 1
    # 15:00 - 17:00
    timeslots.append({"id": ts_id, "day": day, "start_hour": 15, "start_minute": 0, "end_hour": 17, "end_minute": 0})
    ts_id += 1
    # 17:00 - 19:00
    timeslots.append({"id": ts_id, "day": day, "start_hour": 17, "start_minute": 0, "end_hour": 19, "end_minute": 0})
    ts_id += 1
    # 19:00 - 21:00
    timeslots.append({"id": ts_id, "day": day, "start_hour": 19, "start_minute": 0, "end_hour": 21, "end_minute": 0})
    ts_id += 1

with open('sample_data/timeslots.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "day", "start_hour", "start_minute", "end_hour", "end_minute"])
    writer.writeheader()
    writer.writerows(timeslots)

print("Generated sample_data/timeslots.csv")
