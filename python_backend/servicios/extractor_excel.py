"""
Extractor de datos desde archivos Excel (Matriz ITI)
"""

import pandas as pd
from modelos import Curso, Profesor
import re

def extraer_datos_excel_a_memoria(ruta_archivo, ciclo_seleccionado=None):
    """
    Extraer cursos y profesores de un archivo Excel de horarios.
    
    Args:
        ruta_archivo: Ruta al archivo Excel
        ciclo_seleccionado: Nombre de la hoja/ciclo a procesar
        
    Returns:
        dict: {
            'courses': [Curso],
            'professors': [Profesor],
            'warnings': [str]
        }
    """
    warnings = []
    
    try:
        # Cargar archivo Excel
        xls = pd.ExcelFile(ruta_archivo)
        
        # Determinar hoja a usar
        hoja_uso = ciclo_seleccionado
        if not hoja_uso or hoja_uso not in xls.sheet_names:
            hoja_uso = xls.sheet_names[0]
            if ciclo_seleccionado:
                warnings.append(f"Ciclo '{ciclo_seleccionado}' no encontrado. Usando '{hoja_uso}'")
        
        df = pd.read_excel(xls, sheet_name=hoja_uso)
        
        # Procesamiento básico (simplificado para esta migración)
        # En una implementación completa, aquí iría toda la lógica de parsing de excel_extractor.py
        # traducida al español. Por ahora, creamos una estructura dummy funcional
        # para que la aplicación arranque.
        
        cursos = []
        profesores = []
        
        # TODO: Implementar lógica completa de extracción en español
        # Esta es una implementación placeholder para permitir que el servidor inicie
        
        return {
            'courses': cursos,
            'professors': profesores,
            'warnings': warnings
        }
            
    except Exception as e:
        return {'error': str(e)}
