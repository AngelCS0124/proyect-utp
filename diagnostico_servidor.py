#!/usr/bin/env python3
"""
Diagnóstico rápido del servidor
"""
import requests
import json

print("=" * 60)
print("Diagnóstico del Servidor")
print("=" * 60)

# 1. Ver estado
print("\n1. Estado del servidor:")
r = requests.get('http://localhost:5000/api/status')
if r.ok:
    data = r.json()
    print(f"   Cursos: {data['counts']['courses']}")
    print(f"   Profesores: {data['counts']['professors']}")
    print(f"   Timeslots: {data['counts']['timeslots']}")
    print(f"   Horario: {data['data_loaded']['schedule']}")
else:
    print(f"   ERROR: {r.status_code}")

# 2. Ver bloques de tiempo
print("\n2. Bloques de tiempo:")
r = requests.get('http://localhost:5000/api/data/timeslots')
if r.ok:
    data = r.json()['data']
    dias = {}
    for t in data:
        dias[t['day']] = dias.get(t['day'], 0) + 1
    print(f"   Total: {len(data)}")
    for dia, count in sorted(dias.items()):
        print(f"   {dia}: {count} bloques")
else:
    print(f"   ERROR: {r.status_code}")

# 3. Ver profesores
print("\n3. Profesores:")
r = requests.get('http://localhost:5000/api/data/professors')
if r.ok:
    profs = r.json()['data']
    print(f"   Total: {len(profs)}")
    for p in profs[:3]:
        bloques = len(p.get(' available_timeslots', []))
        print(f"   {p['name']}: {bloques} bloques disponibles")
else:
    print(f"   ERROR: {r.status_code}")

# 4. Intentar generar
print("\n4. Intentando generar horario...")
r = requests.post('http://localhost:5000/api/generate')
print(f"   Status code: {r.status_code}")

if r.ok:
    data = r.json()
    print(f"   Success: {data.get('success')}")
    if 'schedule' in data and data['schedule']:
        asigs = data['schedule'].get('assignments', [])
        print(f"   Asignaciones: {len(asigs)}")
        
        # Ver distribución
        if asigs:
            dias = {}
            for a in asigs:
                if 'timeslot_display' in a:
                    dia = a['timeslot_display'].split()[0]
                    dias[dia] = dias.get(dia, 0) + 1
            
            print("   Distribución:")
            for dia, count in sorted(dias.items()):
                print(f"     {dia}: {count} clases")
    elif 'error' in data:
        print(f"   ERROR: {data['error']}")
else:
    print(f"   ERROR HTTP: {r.text[:200]}")

print("\n" + "=" * 60)
