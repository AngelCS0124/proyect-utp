#!/usr/bin/env python3
"""
Test con cursos del curriculum para verificar auto-asignación
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend'))

from data.curriculum import get_courses_for_cycle
from cargador_datos import CargadorDatos
from servicios.csp_scheduler import CSPScheduler

print("=" * 60)
print("Test con Curriculum (Ene-Abr)")
print("=" * 60)

# Cargar cursos de curriculum (como hace el frontend)
cursos = get_courses_for_cycle("jan-apr")
print(f"\n✓ Cargados {len(cursos)} cursos del curriculum")
print(f"   Cuatrimestres: 2, 5, 8")

# Cargar profesores y bloques
datos_dir = 'datos_muestra'
profesores = CargadorDatos.cargar_profesores_json(os.path.join(datos_dir, 'profesores.json'))
bloques = CargadorDatos.cargar_bloques_tiempo_json(os.path.join(datos_dir, 'bloques_tiempo.json'))

print(f"✓ Cargados {len(profesores)} profesores")
print(f"✓ Cargados {len(bloques)} bloques")

# Verificar cursos sin profesor
sin_prof = [c for c in cursos if not c.id_profesor]
print(f"\n📊 Cursos sin profesor: {len(sin_prof)} de {len(cursos)}")

# Crear scheduler
solver = CSPScheduler(cursos, profesores, bloques[:9])  # Solo 9 bloques para test rápido

# Resolver
print("\n🔧 Resolviendo...")
exito, horario = solver.resolver(max_reintentos=1)

stats = solver.obtener_estadisticas()

print(f"\n{'✅ ÉXITO' if exito else '❌ FALLO'}")
print(f"   Variables: {stats['variables']}")
print(f"   Asignaciones: {stats['asignaciones']}")
print(f"   Intentos: {stats['intentos']}")
print(f"   Backtracks: {stats['backtracks']}")

if exito:
    print("\n📋 Asignaciones generadas:")
    for i, asig in enumerate(horario.asignaciones[:10]):
        if isinstance(asig, dict):
            print(f"   {i+1}. {asig.get('course_name', 'N/A')} → {asig.get('professor_name', 'N/A')}")

print("\n" + "=" * 60)
