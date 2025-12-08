#!/usr/bin/env python3
"""
Test básico del CSP Scheduler optimizado
"""

import sys
import os

# Agregar el directorio python_backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend'))

from cargador_datos import CargadorDatos
from servicios.csp_scheduler import CSPScheduler

def test_csp_scheduler():
    """Prueba el CSP scheduler con datos reales"""
    
    datos_dir = 'datos_muestra'
    
    print("=" * 60)
    print("Prueba de CSP Scheduler Optimizado")
    print("=" * 60)
    
    # 1. Cargar datos
    print("\n1. Cargando datos...")
    try:
        cursos_path = os.path.join(datos_dir, 'cursos.csv')
        profesores_path = os.path.join(datos_dir, 'profesores.json')
        bloques_path = os.path.join(datos_dir, 'bloques_tiempo.json')
        
        cursos = CargadorDatos.cargar_cursos_csv(cursos_path)
        profesores = CargadorDatos.cargar_profesores_json(profesores_path)
        bloques = CargadorDatos.cargar_bloques_tiempo_json(bloques_path)
        
        print(f"   ✓ Cargados {len(cursos)} cursos")
        print(f"   ✓ Cargados {len(profesores)} profesores")
        print(f"   ✓ Cargados {len(bloques)} bloques")
    except Exception as e:
        print(f"   ✗ Error cargando datos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. Crear solver CSP
    print("\n2. Creando CSP Scheduler...")
    try:
        solver = CSPScheduler(cursos, profesores, bloques, max_intentos=50000)
        print(f"   ✓ Scheduler creado")
    except Exception as e:
        print(f"   ✗ Error creando scheduler: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Resolver
    print("\n3. Resolviendo CSP...")
    try:
        exito, horario = solver.resolver(max_reintentos=3)
        
        stats = solver.obtener_estadisticas()
        
        print(f"\n   Resultado: {'✅ ÉXITO' if exito else '❌ FALLO'}")
        print(f"   Intentos: {stats['intentos']}")
        print(f"   Backtracks: {stats['backtracks']}")
        print(f"   Asignaciones: {stats['asignaciones']}")
        print(f"   Variables: {stats['variables']}")
        
        if exito and horario:
            print(f"\n   ✓ Horario generado con {len(horario.asignaciones)} asignaciones")
            
            # Mostrar algunas asignaciones
            print("\n   Primeras 5 asignaciones:")
            for i, asig in enumerate(horario.asignaciones[:5]):
                # asignaciones son dicts
                if isinstance(asig, dict):
                    print(f"     {i+1}. {asig.get('course_name', 'N/A')} - {asig.get('professor_name', 'N/A')}")
                else:
                    print(f"     {i+1}. {asig.nombre_curso} - {asig.nombre_profesor}")
            
            return True
        else:
            print(f"\n   ✗ No se pudo generar horario")
            return False
            
    except Exception as e:
        print(f"   ✗ Error resolviendo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n")
    success = test_csp_scheduler()
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST EXITOSO")
    else:
        print("❌ TEST FALLIDO")
    print("=" * 60 + "\n")
    sys.exit(0 if success else 1)
