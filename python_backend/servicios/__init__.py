"""
Módulo de servicios - Exporta funciones de utilidad
"""
from .scheduling_helpers import (
    # Funciones principales (español)
    obtener_bloques_consecutivos,
    puede_tener_bloques_consecutivos,
    obtener_bloques_dobles,
    obtener_opciones_bloques_dobles,
    calcular_sesiones_necesarias,
    obtener_info_bloque,
    # Alias para compatibilidad (inglés)
    get_consecutive_blocks,
    can_have_consecutive_blocks,
    get_double_block_timeslots,
    get_all_double_block_options,
    calculate_sessions_needed,
    get_block_info
)

from .visualizacion import generar_datos_visualizacion

from .extractor_excel import extraer_datos_excel_a_memoria

from .csp_scheduler import CSPScheduler

__all__ = [
    # Español
    'obtener_bloques_consecutivos', 'puede_tener_bloques_consecutivos',
    'obtener_bloques_dobles', 'obtener_opciones_bloques_dobles',
    'calcular_sesiones_necesarias', 'obtener_info_bloque',
    # Inglés (compatibilidad)
    'get_consecutive_blocks', 'can_have_consecutive_blocks',
    'get_double_block_timeslots', 'get_all_double_block_options',
    'calculate_sessions_needed', 'get_block_info',
    # Visualización
    'generar_datos_visualizacion',
    # Excel
    'extraer_datos_excel_a_memoria',
    # CSP Scheduler
    'CSPScheduler'
]
