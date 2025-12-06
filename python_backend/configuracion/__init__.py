"""
Módulo de configuración - Exporta configuraciones del sistema
"""
from .bloques_tiempo import (
    # Variables principales (español)
    BLOQUES_TIEMPO,
    DIAS_VALIDOS,
    PERIODO_RECESO,
    RESTRICCIONES_HORARIO,
    # Funciones principales (español)
    obtener_bloques_dia,
    obtener_bloques_semanales,
    es_bloque_valido,
    es_durante_receso,
    obtener_nombre_bloque,
    validar_restricciones_bloque,
    # Alias para compatibilidad (inglés)
    TIME_BLOCKS,
    VALID_DAYS,
    RECESS_PERIOD,
    SCHEDULE_CONSTRAINTS,
    get_all_timeslots_for_day,
    get_all_weekly_timeslots,
    is_valid_timeslot,
    is_during_recess,
    get_block_name,
    validate_timeslot_constraints
)

__all__ = [
    # Español
    'BLOQUES_TIEMPO', 'DIAS_VALIDOS', 'PERIODO_RECESO', 'RESTRICCIONES_HORARIO',
    'obtener_bloques_dia', 'obtener_bloques_semanales', 'es_bloque_valido',
    'es_durante_receso', 'obtener_nombre_bloque', 'validar_restricciones_bloque',
    # Inglés (compatibilidad)
    'TIME_BLOCKS', 'VALID_DAYS', 'RECESS_PERIOD', 'SCHEDULE_CONSTRAINTS',
    'get_all_timeslots_for_day', 'get_all_weekly_timeslots', 'is_valid_timeslot',
    'is_during_recess', 'get_block_name', 'validate_timeslot_constraints'
]
