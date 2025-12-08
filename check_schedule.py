#!/usr/bin/env python3
"""
Script para ver exactamente qué se generó en el último horario
"""

import sys
import os
import requests

print("=" * 60)
print("Diagnóstico de Generación de Horario")
print("=" * 60)

# 1. Ver status
print("\n1. Status del sistema:")
response = requests.get('http://localhost:5000/api/status')
if response.ok:
    status = response.json()
    print(f"   Schedule generado: {status['data_loaded']['schedule']}")
    print(f"   Cursos cargados: {status['counts']['courses']}")
    print(f"   Profesores: {status['counts']['professors']}")
    print(f"   Timeslots: {status['counts']['timeslots']}")

# 2. Ver si hay schedule en el servidor (endpoint que necesitamos verificar existe)
print("\n2. Intentando obtener horario generado...")
# El horario debería estar en la memoria del servidor después de generarlo
# Necesitamos verificar cómo accederlo

# 3. Ver cursos con profesor asignado
print("\n3. Cursos cargados:")
response = requests.get('http://localhost:5000/api/data/courses')
if response.ok:
    data = response.json()
    cursos = data.get('data', [])
    print(f"   Total cursos: {len(cursos)}")
    
    con_prof = [c for c in cursos if c.get('professor_id')]
    sin_prof = [c for c in cursos if not c.get('professor_id')]
    
    print(f"   Con profesor: {len(con_prof)}")
    print(f"   Sin profesor: {len(sin_prof)}")
    
    if con_prof:
        print("\n   Cursos CON profesor:")
        for c in con_prof[:5]:
            print(f"     • {c['name']} - Profesor ID: {c['professor_id']}")

print("\n" + "=" * 60)
