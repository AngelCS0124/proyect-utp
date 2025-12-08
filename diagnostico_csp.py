#!/usr/bin/env python3
"""
Diagnóstico del CSP Scheduler
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend'))

from cargador_datos import CargadorDatos
from servicios.csp_scheduler import CSPScheduler

def diagnosticar():
    datos_dir = 'datos_muestra'
    
    print("=" * 60)
    print("Diagnóstico CSP Scheduler")
    print("=" * 60)
    
    # Cargar datos
    cursos = CargadorDatos.cargar_cursos_csv(os.path.join(datos_dir, 'cursos.csv'))
    profesores = CargadorDatos.cargar_profesores_json(os.path.join(datos_dir, 'profesores.json'))
    bloques = CargadorDatos.cargar_bloques_tiempo_json(os.path.join(datos_dir, 'bloques_tiempo.json'))
    
    print(f"\n📊 Datos Cargados:")
    print(f"   Cursos: {len(cursos)}")
    print(f"   Profesores: {len(profesores)}")
    print(f"   Bloques: {len(bloques)}")
    
    # Analizar cursos
    print(f"\n📚 Análisis de Cursos:")
    for curso in cursos:
        print(f"   • {curso.nombre} (ID: {curso.id})")
        print(f"     - Profesor ID: {curso.id_profesor}")
        print(f"     - Sesiones/semana: {curso.sesiones_por_semana}")
        print(f"     - Grupo: {curso.id_grupo}")
    
    # Analizar profesores
    print(f"\n👥 Análisis de Profesores:")
    for prof in profesores:
        print(f"   • {prof.nombre} (ID: {prof.id})")
        print(f"     - Bloques disponibles: {len(prof.bloques_disponibles)}")
        print(f"     - Materias capaces: {len(prof.materias_capaces)}")
    
    # Crear scheduler y ver inicialización
    print(f"\n🔧 Inicializando CSP...")
    solver = CSPScheduler(cursos, profesores, bloques)
    
    # Forzar inicialización
    solver._aplicar_restricciones_estructurales()
    solver._inicializar_csp()
    
    print(f"\n📊 Estado del CSP:")
    print(f"   Variables creadas: {len(solver.variables)}")
    print(f"   Dominios: {len(solver.dominios)}")
    
    print(f"\n🔍 Detalles de Variables:")
    for var in solver.variables:
        dom_size = len(solver.dominios[var])
        print(f"   • {var.id}: {var.curso.nombre} sesión {var.numero_sesion}")
        print(f"     - Dominio: {dom_size} bloques")
        print(f"     - Profesor: {var.curso.id_profesor}")
        print(f"     - Grupo: {var.curso.id_grupo}")
    
    # Pre-validación
    print(f"\n✅ Pre-validación:")
    es_factible, mensaje = solver._validar_factibilidad()
    if es_factible:
        print(f"   ✓ Problema es factible")
    else:
        print(f"   ✗ Problema NO factible: {mensaje}")

if __name__ == '__main__':
    diagnosticar()
