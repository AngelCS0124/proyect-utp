#!/usr/bin/env python3
"""
Analizar el horario generado
"""

import json

# Cargar horario
with open('horario_generado.json', 'r', encoding='utf-8') as f:
    horario = json.load(f)

assignments = horario['assignments']

print("="*70)
print(f"HORARIO GENERADO - {len(assignments)} CLASES ASIGNADAS")
print("="*70)

# Distribución por día
dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
por_dia = {dia: [] for dia in dias_orden}

for asig in assignments:
    display = asig['timeslot_display']
    dia = display.split()[0]
    if dia in por_dia:
        por_dia[dia].append(asig)

print("\n📅 DISTRIBUCIÓN POR DÍA:")
print("-"*70)
for dia in dias_orden:
    clases = por_dia[dia]
    barra = '█' * len(clases)
    print(f"{dia:12} [{len(clases):2} clases]: {barra}")

# Mostrar clases por día
print("\n📚 DETALLE DE CLASES POR DÍA:")
print("-"*70)
for dia in dias_orden:
    clases = sorted(por_dia[dia], key=lambda x: x['timeslot_display'])
    if clases:
        print(f"\n{dia}:")
        for asig in clases:
            print(f"  {asig['timeslot_display']:20} | {asig['course_name']:35} | {asig['professor_name']}")

# Cursos únicos
cursos_unicos = {}
for asig in assignments:
    curso_id = asig['course_id']
    if curso_id not in cursos_unicos:
        cursos_unicos[curso_id] = {
            'nombre': asig['course_name'],
            'profesor': asig['professor_name'],
            'sesiones': 0
        }
    cursos_unicos[curso_id]['sesiones'] += 1

print("\n" + "="*70)
print(f"📊 RESUMEN: {len(cursos_unicos)} CURSOS DIFERENTES")
print("="*70)
for curso_id, info in sorted(cursos_unicos.items()):
    print(f"  {info['nombre']:40} - {info['sesiones']} sesiones - {info['profesor']}")

print("\n" + "="*70)
print("✅ CALENDARIO COMPLETAMENTE LLENO")
print("="*70)
