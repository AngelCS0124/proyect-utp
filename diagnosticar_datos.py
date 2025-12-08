#!/usr/bin/env python3
"""
Script de diagnóstico para verificar qué datos se están cargando
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend'))

from cargador_datos import CargadorDatos

def main():
    print("="*70)
    print("DIAGNÓSTICO DE DATOS")
    print("="*70)
    
    base_dir = os.path.dirname(__file__)
    datos_dir = os.path.join(base_dir, 'datos_muestra')
    
    # Verificar archivo existe
    ruta_cursos = os.path.join(datos_dir, 'cursos.csv')
    print(f"\n📁 Archivo: {ruta_cursos}")
    print(f"   Existe: {os.path.exists(ruta_cursos)}")
    
    if os.path.exists(ruta_cursos):
        # Leer número de líneas
        with open(ruta_cursos, 'r') as f:
            lines = f.readlines()
        print(f"   Líneas en archivo: {len(lines)} (incluyendo header)")
        print(f"   Cursos en archivo: {len(lines) - 1}")
        
        # Cargar con el cargador
        print("\n🔄 Cargando con CargadorDatos...")
        try:
            cursos = CargadorDatos.cargar_cursos_csv(ruta_cursos)
            print(f"   ✅ Cursos cargados: {len(cursos)}")
            
            # Análisis
            print("\n📊 Análisis de cursos:")
            cuatrimestres = {}
            total_sesiones = 0
            
            for curso in cursos:
                cuatri = curso.cuatrimestre
                if cuatri not in cuatrimestres:
                    cuatrimestres[cuatri] = 0
                cuatrimestres[cuatri] += 1
                total_sesiones += curso.sesiones_por_semana
            
            print(f"   Total sesiones: {total_sesiones}")
            print(f"\n   Distribución por cuatrimestre:")
            for cuatri in sorted(cuatrimestres.keys()):
                print(f"      Cuatrimestre {cuatri}: {cuatrimestres[cuatri]} cursos")
            
            # Mostrar primeros 5 cursos
            print(f"\n📚 Primeros 5 cursos:")
            for i, curso in enumerate(cursos[:5]):
                print(f"   {i+1}. {curso.nombre} - Cuatri: {curso.cuatrimestre}, Sesiones: {curso.sesiones_por_semana}, Grupo: {curso.id_grupo}")
            
            # Mostrar últimos 5 cursos
            if len(cursos) > 5:
                print(f"\n📚 Últimos 5 cursos:")
                for i, curso in enumerate(cursos[-5:]):
                    idx = len(cursos) - 5 + i + 1
                    print(f"   {idx}. {curso.nombre} - Cuatri: {curso.cuatrimestre}, Sesiones: {curso.sesiones_por_semana}, Grupo: {curso.id_grupo}")
            
        except Exception as e:
            print(f"   ❌ Error al cargar: {e}")
            import traceback
            traceback.print_exc()
    
    # Verificar profesores
    ruta_profesores = os.path.join(datos_dir, 'profesores.json')
    print(f"\n📁 Profesores: {ruta_profesores}")
    if os.path.exists(ruta_profesores):
        profesores = CargadorDatos.cargar_profesores_json(ruta_profesores)
        print(f"   ✅ Profesores cargados: {len(profesores)}")
    
    # Verificar bloques
    ruta_bloques = os.path.join(datos_dir, 'bloques_tiempo.json')
    print(f"\n📁 Bloques: {ruta_bloques}")
    if os.path.exists(ruta_bloques):
        bloques = CargadorDatos.cargar_bloques_tiempo_json(ruta_bloques)
        print(f"   ✅ Bloques cargados: {len(bloques)}")

if __name__ == '__main__':
    main()
