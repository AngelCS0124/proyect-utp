"""
Configuración de bloques de tiempo predefinidos para UTP
Sistema de 9 bloques de 54 minutos, Lunes a Viernes, 7:00 AM - 3:49 PM
"""

# Bloques de tiempo predefinidos (54 minutos cada uno)
BLOQUES_TIEMPO = {
    1: {
        'id': 1,
        'name': 'Bloque 1',
        'start_hour': 7,
        'start_minute': 0,
        'end_hour': 7,
        'end_minute': 54
    },
    2: {
        'id': 2,
        'name': 'Bloque 2',
        'start_hour': 7,
        'start_minute': 55,
        'end_hour': 8,
        'end_minute': 49
    },
    3: {
        'id': 3,
        'name': 'Bloque 3',
        'start_hour': 8,
        'start_minute': 50,
        'end_hour': 9,
        'end_minute': 44
    },
    4: {
        'id': 4,
        'name': 'Bloque 4',
        'start_hour': 9,
        'start_minute': 45,
        'end_hour': 10,
        'end_minute': 39
    },
    # RECESO: 10:40 - 11:09 (29 minutos)
    5: {
        'id': 5,
        'name': 'Bloque 5',
        'start_hour': 11,
        'start_minute': 10,
        'end_hour': 12,
        'end_minute': 4
    },
    6: {
        'id': 6,
        'name': 'Bloque 6',
        'start_hour': 12,
        'start_minute': 5,
        'end_hour': 12,
        'end_minute': 59
    },
    7: {
        'id': 7,
        'name': 'Bloque 7',
        'start_hour': 13,
        'start_minute': 0,
        'end_hour': 13,
        'end_minute': 54
    },
    8: {
        'id': 8,
        'name': 'Bloque 8',
        'start_hour': 14,  # 2:00 PM
        'start_minute': 0,
        'end_hour': 14,
        'end_minute': 54
    },
    9: {
        'id': 9,
        'name': 'Bloque 9',
        'start_hour': 14,  # 2:55 PM
        'start_minute': 55,
        'end_hour': 15,  # 3:49 PM
        'end_minute': 49
    }
}

# Días válidos (solo entre semana)
DIAS_VALIDOS = {
    'es': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
}

# Periodo de receso (no se permiten clases)
PERIODO_RECESO = {
    "start_hour": 10,
    "start_minute": 40,
    "end_hour": 11,
    "end_minute": 9,
    "duration_minutes": 29
}

# Restricciones del horario
RESTRICCIONES_HORARIO = {
    "earliest_start_hour": 7,
    "earliest_start_minute": 0,
    "latest_end_hour": 15,  # 3:49 PM = 15:49
    "latest_end_minute": 49,
    "class_duration_minutes": 54,
    "min_break_minutes": 1,  # Pausa mínima entre clases
    "max_break_minutes": 1,  # Pausa máxima para evitar huecos
}


def obtener_bloques_dia(dia):
    """
    Generar todos los bloques de tiempo para un día dado
    
    Args:
        dia: Nombre del día (ej: 'Lunes', 'Monday')
        
    Returns:
        Lista de diccionarios de bloques de tiempo
    """
    bloques = []
    id_base = 0
    
    # Mapear día a ID base (Lunes=0, Martes=100, etc.)
    mapeo_dias = {
        'Lunes': 0, 'Monday': 0,
        'Martes': 100, 'Tuesday': 100,
        'Miércoles': 200, 'Wednesday': 200,
        'Jueves': 300, 'Thursday': 300,
        'Viernes': 400, 'Friday': 400,
    }
    
    id_base = mapeo_dias.get(dia, 0)
    
    for num_bloque, bloque in BLOQUES_TIEMPO.items():
        bloques.append({
            'id': id_base + num_bloque,
            'day': dia,
            'start_hour': bloque['start_hour'],
            'start_minute': bloque['start_minute'],
            'end_hour': bloque['end_hour'],
            'end_minute': bloque['end_minute'],
            'block_name': bloque['name']
        })
    
    return bloques


def obtener_bloques_semanales(language='es'):
    """
    Generar horario semanal completo (todos los bloques para todos los días)
    
    Args:
        language: Idioma para nombres de días ('es' o 'en')
        
    Returns:
        Lista de todos los bloques de tiempo de la semana
    """
    dias = DIAS_VALIDOS[language]
    todos_bloques = []
    
    for dia in dias:
        todos_bloques.extend(obtener_bloques_dia(dia))
    
    return todos_bloques


def es_bloque_valido(hora_inicio, minuto_inicio, hora_fin, minuto_fin):
    """
    Validar si un bloque de tiempo coincide con uno de los bloques predefinidos
    
    Args:
        hora_inicio: Hora de inicio (0-23)
        minuto_inicio: Minuto de inicio (0-59)
        hora_fin: Hora de fin (0-23)
        minuto_fin: Minuto de fin (0-59)
        
    Returns:
        bool: True si coincide con un bloque predefinido
    """
    for bloque in BLOQUES_TIEMPO.values():
        if (bloque['start_hour'] == hora_inicio and 
            bloque['start_minute'] == minuto_inicio and
            bloque['end_hour'] == hora_fin and 
            bloque['end_minute'] == minuto_fin):
            return True
    return False


def es_durante_receso(hora_inicio, minuto_inicio, hora_fin, minuto_fin):
    """
    Verificar si un bloque de tiempo solapa con el periodo de receso obligatorio
    
    Args:
        hora_inicio: Hora de inicio
        minuto_inicio: Minuto de inicio
        hora_fin: Hora de fin
        minuto_fin: Minuto de fin
        
    Returns:
        bool: True si solapa con el receso
    """
    # Convertir a minutos para comparación más fácil
    inicio_bloque = hora_inicio * 60 + minuto_inicio
    fin_bloque = hora_fin * 60 + minuto_fin
    inicio_receso = PERIODO_RECESO['start_hour'] * 60 + PERIODO_RECESO['start_minute']
    fin_receso = PERIODO_RECESO['end_hour'] * 60 + PERIODO_RECESO['end_minute']
    
    # Verificar solapamiento
    return not (fin_bloque <= inicio_receso or inicio_bloque >= fin_receso)


def obtener_nombre_bloque(hora_inicio, minuto_inicio):
    """
    Obtener el nombre del bloque para una hora de inicio dada
    
    Args:
        hora_inicio: Hora de inicio
        minuto_inicio: Minuto de inicio
        
    Returns:
        str: Nombre del bloque o "Bloque Desconocido"
    """
    for bloque in BLOQUES_TIEMPO.values():
        if bloque['start_hour'] == hora_inicio and bloque['start_minute'] == minuto_inicio:
            return bloque['name']
    return "Bloque Desconocido"


def validar_restricciones_bloque(hora_inicio, minuto_inicio, hora_fin, minuto_fin):
    """
    Validar que un bloque de tiempo cumple con todas las restricciones UTP
    
    Args:
        hora_inicio: Hora de inicio
        minuto_inicio: Minuto de inicio
        hora_fin: Hora de fin
        minuto_fin: Minuto de fin
        
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    # Verificar si está dentro de las horas permitidas
    mas_temprano = RESTRICCIONES_HORARIO['earliest_start_hour'] * 60 + RESTRICCIONES_HORARIO['earliest_start_minute']
    mas_tarde = RESTRICCIONES_HORARIO['latest_end_hour'] * 60 + RESTRICCIONES_HORARIO['latest_end_minute']
    inicio_bloque = hora_inicio * 60 + minuto_inicio
    fin_bloque = hora_fin * 60 + minuto_fin
    
    if inicio_bloque < mas_temprano:
        return False, "Las clases no pueden iniciar antes de las 7:00 AM"
    
    if fin_bloque > mas_tarde:
        return False, "Las clases no pueden terminar después de las 3:49 PM"
    
    # Verificar si está durante el receso
    if es_durante_receso(hora_inicio, minuto_inicio, hora_fin, minuto_fin):
        return False, "No se pueden programar clases durante el receso (10:40-11:09)"
    
    # Verificar si coincide con un bloque predefinido
    if not es_bloque_valido(hora_inicio, minuto_inicio, hora_fin, minuto_fin):
        return False, "El horario debe coincidir con uno de los bloques predefinidos de 54 minutos"
    
    return True, ""


# Mantener alias para compatibilidad con código existente
TIME_BLOCKS = BLOQUES_TIEMPO
VALID_DAYS = DIAS_VALIDOS
RECESS_PERIOD = PERIODO_RECESO
SCHEDULE_CONSTRAINTS = RESTRICCIONES_HORARIO

# Alias de funciones para compatibilidad
get_all_timeslots_for_day = obtener_bloques_dia
get_all_weekly_timeslots = obtener_bloques_semanales
is_valid_timeslot = es_bloque_valido
is_during_recess = es_durante_receso
get_block_name = obtener_nombre_bloque
validate_timeslot_constraints = validar_restricciones_bloque
