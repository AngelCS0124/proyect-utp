#!/usr/bin/env python3
"""
Script simplificado para probar horario sin dependencias externas
"""

import json
import csv
import sys
import os

# Agregar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend'))

from modelos import Curso, Profesor, BloqueTiempo

# Importar CSPScheduler directamente para evitar dependencias de servicios.__init__
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend', 'servicios'))
from csp_scheduler import CSPScheduler

def cargar_cursos_simple(ruta):
    """Cargar cursos sin pandas"""
    cursos = []
    with open(ruta, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            curso = Curso(
                id=int(row['id']),
                nombre=row['nombre'],
                codigo=row['codigo'],
                creditos=int(row['creditos']),
                matricula=int(row['matricula']),
                prerequisitos=[int(x.strip()) for x in row['prerrequisitos'].split(',') if x.strip()],
                id_profesor=int(row['id_profesor']) if row['id_profesor'] else None,
                cuatrimestre=int(row['cuatrimestre']),
                id_grupo=int(row['id_grupo']),
                sesiones_por_semana=int(row['sesiones_por_semana'])
            )
            cursos.append(curso)
    return cursos

def cargar_profesores_simple(ruta):
    """Cargar profesores del JSON"""
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    profesores = []
    for item in data:
        prof = Profesor(
            id=item['id'],
            nombre=item['nombre'],
            email=item['email'],
            bloques_disponibles=item['bloques_disponibles'],
            materias_capaces=item['materias_capaces']
        )
        profesores.append(prof)
    return profesores

def cargar_bloques_simple(ruta):
    """Cargar bloques de tiempo del JSON"""
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bloques = []
    for item in data:
        bloque = BloqueTiempo(
            id=item['id'],
            dia=item['dia'],
            hora_inicio=item['hora_inicio'],
            minuto_inicio=item['minuto_inicio'],
            hora_fin=item['hora_fin'],
            minuto_fin=item['minuto_fin']
        )
        bloques.append(bloque)
    return bloques

def main():
    print("="*60)
    print("PRUEBA DE GENERACIÓN DE HORARIO")
    print("="*60)
    
    # Cargar datos
    print("\n📁 Cargando datos...")
    base_dir = os.path.dirname(__file__)
    datos_dir = os.path.join(base_dir, 'datos_muestra')
    
    try:
        cursos = cargar_cursos_simple(os.path.join(datos_dir, 'cursos.csv'))
        profesores = cargar_profesores_simple(os.path.join(datos_dir, 'profesores.json'))
        bloques = cargar_bloques_simple(os.path.join(datos_dir, 'bloques_tiempo.json'))
        
        print(f"✓ Cursos: {len(cursos)}")
        print(f"✓ Profesores: {len(profesores)}")
        print(f"✓ Bloques de tiempo: {len(bloques)}")
        
        # Mostrar sesiones por semana
        print("\n📊 Sesiones por semana por curso:")
        total_sesiones = 0
        for curso in cursos:
            print(f"   {curso.nombre:40} - {curso.sesiones_por_semana} sesiones/semana")
            total_sesiones += curso.sesiones_por_semana
        
        print(f"\n   TOTAL: {total_sesiones} sesiones a agendar")
        print(f"   Capacidad del calendario: {len(bloques)} bloques de tiempo")
        
        # Generar horario
        print("\n🔄 Generando horario con CSP Scheduler...")
        scheduler = CSPScheduler(cursos, profesores, bloques, max_intentos=100000)
        
        exito, horario = scheduler.resolver(max_reintentos=5)
        stats = scheduler.obtener_estadisticas()
        
        print(f"\n{'='*60}")
        if exito:
            print("✅ HORARIO GENERADO EXITOSAMENTE")
            print(f"{'='*60}")
            print(f"Asignaciones totales: {len(horario.asignaciones)}")
            print(f"Intentos: {stats['intentos']}")
            print(f"Backtracks: {stats['backtracks']}")
            
            # Análisis de distribución por día
            print("\n📅 Distribución por día:")
            por_dia = {}
            for asig in horario.asignaciones:
                # asig puede ser objeto o dict
                bloque_id = asig.id_bloque_tiempo if hasattr(asig, 'id_bloque_tiempo') else asig.get('id_bloque_tiempo')
                for bloque in bloques:
                    if bloque.id == bloque_id:
                        if bloque.dia not in por_dia:
                            por_dia[bloque.dia] = 0
                        por_dia[bloque.dia] += 1
                        break
            
            for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
                count = por_dia.get(dia, 0)
                barra = '█' * count
                print(f"   {dia:12} [{count:2}]: {barra}")
            
            # Guardar resultado
            resultado_path = os.path.join(base_dir, 'horario_generado.json')
            with open(resultado_path, 'w', encoding='utf-8') as f:
                json.dump(horario.a_diccionario(), f, indent=2, ensure_ascii=False)
            print(f"\n💾 Horario guardado en: {resultado_path}")
            
        else:
            print("❌ NO SE PUDO GENERAR HORARIO COMPLETO")
            print(f"{'='*60}")
            print(f"Variables creadas: {stats['variables']}")
            print(f"Asignaciones parciales: {stats['asignaciones']}")
            print(f"Intentos: {stats['intentos']}")
            print(f"Backtracks: {stats['backtracks']}")
            
            print("\n⚠️  Posibles problemas:")
            print("   - Restricciones de disponibilidad de profesores")
            print("   - Conflictos en asignación de profesores")
            print("   - Límite de intentos alcanzado")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
