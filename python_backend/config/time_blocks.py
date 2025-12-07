"""
Configuración de bloques de tiempo predefinidos para UTP
Sistema de 9 bloques de 54 minutos, Lunes a Viernes, 7:00 AM - 3:49 PM
"""

# Bloques de tiempo predefinidos (54 minutos cada uno)
TIME_BLOCKS = {
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
VALID_DAYS = {
    'es': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
}

# Periodo de receso (no se permiten clases)
RECESS_PERIOD = {
    "start_hour": 10,
    "start_minute": 40,
    "end_hour": 11,
    "end_minute": 10,
    "duration_minutes": 30
}

# Restricciones del horario
SCHEDULE_CONSTRAINTS = {
    "earliest_start_hour": 7,
    "earliest_start_minute": 0,
    "latest_end_hour": 15,  # 3:49 PM = 15:49
    "latest_end_minute": 49,
    "class_duration_minutes": 54,
    "min_break_minutes": 1,  # Pausa mínima entre clases
    "max_break_minutes": 1,  # Pausa máxima para evitar huecos
}


def get_all_timeslots_for_day(day):
    """
    Generar todos los bloques de tiempo para un día dado
    Retorna lista de diccionarios de timeslots
    """
    timeslots = []
    base_id = 0
    
    # Mapear día a ID base (Lunes=0, Martes=100, etc.)
    day_mapping = {
        'Lunes': 0, 'Monday': 0,
        'Martes': 100, 'Tuesday': 100,
        'Miércoles': 200, 'Wednesday': 200,
        'Jueves': 300, 'Thursday': 300,
        'Viernes': 400, 'Friday': 400,
    }
    
    base_id = day_mapping.get(day, 0)
    
    for block_num, block in TIME_BLOCKS.items():
        timeslots.append({
            'id': base_id + block_num,
            'day': day,
            'start_hour': block['start_hour'],
            'start_minute': block['start_minute'],
            'end_hour': block['end_hour'],
            'end_minute': block['end_minute'],
            'block_name': block['name']
        })
    
    return timeslots


def get_all_weekly_timeslots(language='es'):
    """
    Generar horario semanal completo (todos los bloques para todos los días)
    """
    days = VALID_DAYS[language]
    all_timeslots = []
    
    for day in days:
        all_timeslots.extend(get_all_timeslots_for_day(day))
    
    return all_timeslots


def is_valid_timeslot(start_hour, start_minute, end_hour, end_minute):
    """
    Validar si un timeslot coincide con uno de los bloques predefinidos
    """
    for block in TIME_BLOCKS.values():
        if (block['start_hour'] == start_hour and 
            block['start_minute'] == start_minute and
            block['end_hour'] == end_hour and 
            block['end_minute'] == end_minute):
            return True
    return False


def is_during_recess(start_hour, start_minute, end_hour, end_minute):
    """
    Verificar si un timeslot solapa con el periodo de receso obligatorio
    """
    # Convertir a minutos para comparación más fácil
    slot_start = start_hour * 60 + start_minute
    slot_end = end_hour * 60 + end_minute
    recess_start = RECESS_PERIOD['start_hour'] * 60 + RECESS_PERIOD['start_minute']
    recess_end = RECESS_PERIOD['end_hour'] * 60 + RECESS_PERIOD['end_minute']
    
    # Verificar solapamiento
    return not (slot_end <= recess_start or slot_start >= recess_end)


def get_block_name(start_hour, start_minute):
    """
    Obtener el nombre del bloque para una hora de inicio dada
    """
    for block in TIME_BLOCKS.values():
        if block['start_hour'] == start_hour and block['start_minute'] == start_minute:
            return block['name']
    return "Bloque Desconocido"


def validate_timeslot_constraints(start_hour, start_minute, end_hour, end_minute):
    """
    Validar que un timeslot cumple con todas las restricciones UTP
    Retorna (es_valido, mensaje_error)
    """
    # Verificar si está dentro de las horas permitidas
    earliest = SCHEDULE_CONSTRAINTS['earliest_start_hour'] * 60 + SCHEDULE_CONSTRAINTS['earliest_start_minute']
    latest = SCHEDULE_CONSTRAINTS['latest_end_hour'] * 60 + SCHEDULE_CONSTRAINTS['latest_end_minute']
    slot_start = start_hour * 60 + start_minute
    slot_end = end_hour * 60 + end_minute
    
    if slot_start < earliest:
        return False, f"Las clases no pueden iniciar antes de las 7:00 AM"
    
    if slot_end > latest:
        return False, f"Las clases no pueden terminar después de las 3:49 PM"
    
    # Verificar si está durante el receso
    if is_during_recess(start_hour, start_minute, end_hour, end_minute):
        return False, f"No se pueden programar clases durante el receso (10:40-11:09)"
    
    # Verificar si coincide con un bloque predefinido
    if not is_valid_timeslot(start_hour, start_minute, end_hour, end_minute):
        return False, f"El horario debe coincidir con uno de los bloques predefinidos de 54 minutos"
    
    return True, ""
