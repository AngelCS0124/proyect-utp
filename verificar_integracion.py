import sys
import os
import unittest
import json
from io import BytesIO

# Añadir python_backend al path
sys.path.append(os.path.join(os.getcwd(), 'python_backend'))

# Importar app traducida
from aplicacion import app, almacen_datos

class TestIntegracion(unittest.TestCase):
    def setUp(self):
        # Asegurar que estamos en el directorio raíz del proyecto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_dir)
        self.app = app.test_client()
        self.app.testing = True
        # Reiniciar almacén de datos
        almacen_datos['cursos'] = []
        almacen_datos['profesores'] = []
        almacen_datos['bloques_tiempo'] = []
        
    def test_cargar_defecto(self):
        print("\nProbando /api/load-defaults (Carga por defecto)...")
        response = self.app.post('/api/load-defaults')
        data = json.loads(response.data)
        
        if response.status_code != 200:
            print(f"Error detallado: {data}")
            
        self.assertEqual(response.status_code, 200)
        # Verificar que se cargaron datos
        self.assertGreater(len(almacen_datos['profesores']), 0, f"No se cargaron profesores. Response: {data}")
        self.assertGreater(len(almacen_datos['cursos']), 0, f"No se cargaron cursos. Response: {data}")
        
        print(f"¡Éxito! Cargados {len(almacen_datos['profesores'])} profesores y {len(almacen_datos['cursos'])} cursos.")
        
    def test_status(self):
        print("\nProbando /api/status...")
        response = self.app.get('/api/status')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('scheduler_available', data)
        print("¡Éxito! Status OK.")

if __name__ == '__main__':
    print("="*60)
    print("VERIFICACIÓN DE INTEGRACIÓN (Sistema Traducido)")
    print("="*60)
    unittest.main()
