#!/usr/bin/env python3
"""
Script de prueba para verificar la carga de bloques de tiempo
"""

import sys
import os

# Agregar el directorio python_backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend'))

from cargador_datos import CargadorDatos
from validadores import Validador

def test_load_timeslots():
    """Prueba de carga de bloques de tiempo desde JSON y CSV"""
    
    datos_dir = 'datos_muestra'
    
    print("=" * 60)
    print("Prueba de Carga de Bloques de Tiempo")
    print("=" * 60)
    
    # Test 1: Cargar desde JSON
    print("\n1. Cargando desde JSON...")
    try:
        json_path = os.path.join(datos_dir, 'bloques_tiempo.json')
        bloques_json = CargadorDatos.cargar_bloques_tiempo_json(json_path)
        print(f"   ✓ Cargados {len(bloques_json)} bloques desde JSON")
        
        # Mostrar primer bloque
        if bloques_json:
            b = bloques_json[0]
            print(f"   Ejemplo: {b}")
            dict_repr = b.a_diccionario()
            print(f"   Dict: {dict_repr}")
            
            # Verificar que no hay None
            assert b.hora_inicio is not None, "hora_inicio es None!"
            assert b.minuto_inicio is not None, "minuto_inicio es None!"
            assert b.hora_fin is not None, "hora_fin es None!"
            assert b.minuto_fin is not None, "minuto_fin es None!"
            print(f"   ✓ Todos los campos tienen valores válidos")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Cargar desde CSV
    print("\n2. Cargando desde CSV...")
    try:
        csv_path = os.path.join(datos_dir, 'bloques_tiempo.csv')
        bloques_csv = CargadorDatos.cargar_bloques_tiempo_csv(csv_path)
        print(f"   ✓ Cargados {len(bloques_csv)} bloques desde CSV")
        
        # Mostrar primer bloque
        if bloques_csv:
            b = bloques_csv[0]
            print(f"   Ejemplo: {b}")
            
            # Verificar que no hay None
            assert b.hora_inicio is not None, "hora_inicio es None!"
            assert b.minuto_inicio is not None, "minuto_inicio es None!"
            assert b.hora_fin is not None, "hora_fin es None!"
            assert b.minuto_fin is not None, "minuto_fin es None!"
            print(f"   ✓ Todos los campos tienen valores válidos")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Validación
    print("\n3. Validando bloques...")
    try:
        validacion = Validador.validar_bloques_tiempo(bloques_csv)
        print(f"   Válido: {validacion['valid']}")
        if validacion['errors']:
            print(f"   Errores: {validacion['errors']}")
        if validacion['warnings']:
            print(f"   Advertencias: {validacion['warnings']}")
        print(f"   ✓ Validación completada")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS PASARON ✓")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_load_timeslots()
    sys.exit(0 if success else 1)
