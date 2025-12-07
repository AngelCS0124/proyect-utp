"""
Módulo de modelos - Exporta todas las clases de modelos
"""
from .curso import Curso
from .profesor import Profesor
from .bloque_tiempo import BloqueTiempo
from .horario import Horario, Asignacion

# Exportar clases
__all__ = ['Curso', 'Profesor', 'BloqueTiempo', 'Horario', 'Asignacion']
