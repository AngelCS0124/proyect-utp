"""
Predefined time blocks for UTP scheduling
Based on 54-minute class periods with mandatory recess
"""

# Time block structure for UTP
# Each block is 54 minutes
# Mandatory recess: 10:40 - 11:09 (29 minutes)

TIME_BLOCKS = {
    # Morning blocks (before recess)
    1: {"id": 1, "start_hour": 7, "start_minute": 0, "end_hour": 7, "end_minute": 55, "name": "Bloque 1"},
    2: {"id": 2, "start_hour": 7, "start_minute": 55, "end_hour": 8, "end_minute": 50, "name": "Bloque 2"},
    3: {"id": 3, "start_hour": 8, "start_minute": 50, "end_hour": 9, "end_minute": 45, "name": "Bloque 3"},
    4: {"id": 4, "start_hour": 9, "start_minute": 45, "end_hour": 10, "end_minute": 40, "name": "Bloque 4"},
    
    # RECESS: 10:40 - 11:10 (30 minutes)
    
    # Afternoon blocks (after recess)
    5: {"id": 5, "start_hour": 11, "start_minute": 10, "end_hour": 12, "end_minute": 5, "name": "Bloque 5"},
    6: {"id": 6, "start_hour": 12, "start_minute": 5, "end_hour": 13, "end_minute": 0, "name": "Bloque 6"},
    7: {"id": 7, "start_hour": 13, "start_minute": 0, "end_hour": 13, "end_minute": 55, "name": "Bloque 7"},
    8: {"id": 8, "start_hour": 14, "start_minute": 0, "end_hour": 14, "end_minute": 55, "name": "Bloque 8"},
    9: {"id": 9, "start_hour": 14, "start_minute": 55, "end_hour": 15, "end_minute": 50, "name": "Bloque 9"},
    10: {"id": 10, "start_hour": 15, "start_minute": 50, "end_hour": 16, "end_minute": 45, "name": "Bloque 10"},
}

# Valid days (weekdays only)
VALID_DAYS = {
    'es': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
}

# Recess period (no classes allowed)
RECESS_PERIOD = {
    "start_hour": 10,
    "start_minute": 40,
    "end_hour": 11,
    "end_minute": 10,
    "duration_minutes": 30
}

# Schedule constraints
SCHEDULE_CONSTRAINTS = {
    "earliest_start_hour": 7,
    "earliest_start_minute": 0,
    "latest_end_hour": 17,  # 5:00 PM
    "latest_end_minute": 0,
    "class_duration_minutes": 55,
    "min_break_minutes": 0,  # Minimum break between classes
    "max_break_minutes": 5,  # Maximum break to avoid gaps
}


def get_all_timeslots_for_day(day):
    """
    Generate all time blocks for a given day
    Returns list of timeslot dictionaries
    """
    timeslots = []
    base_id = 0
    
    # Map day to base ID (Monday=0, Tuesday=100, etc.)
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
    Generate complete weekly schedule (all blocks for all weekdays)
    """
    days = VALID_DAYS[language]
    all_timeslots = []
    
    for day in days:
        all_timeslots.extend(get_all_timeslots_for_day(day))
    
    return all_timeslots


def is_valid_timeslot(start_hour, start_minute, end_hour, end_minute):
    """
    Validate if a timeslot matches one of the predefined blocks
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
    Check if a timeslot overlaps with the mandatory recess period
    """
    # Convert to minutes for easier comparison
    slot_start = start_hour * 60 + start_minute
    slot_end = end_hour * 60 + end_minute
    recess_start = RECESS_PERIOD['start_hour'] * 60 + RECESS_PERIOD['start_minute']
    recess_end = RECESS_PERIOD['end_hour'] * 60 + RECESS_PERIOD['end_minute']
    
    # Check for overlap
    return not (slot_end <= recess_start or slot_start >= recess_end)


def get_block_name(start_hour, start_minute):
    """
    Get the block name for a given start time
    """
    for block in TIME_BLOCKS.values():
        if block['start_hour'] == start_hour and block['start_minute'] == start_minute:
            return block['name']
    return "Unknown Block"


def validate_timeslot_constraints(start_hour, start_minute, end_hour, end_minute):
    """
    Validate that a timeslot meets all UTP constraints
    Returns (is_valid, error_message)
    """
    # Check if within allowed hours
    earliest = SCHEDULE_CONSTRAINTS['earliest_start_hour'] * 60 + SCHEDULE_CONSTRAINTS['earliest_start_minute']
    latest = SCHEDULE_CONSTRAINTS['latest_end_hour'] * 60 + SCHEDULE_CONSTRAINTS['latest_end_minute']
    slot_start = start_hour * 60 + start_minute
    slot_end = end_hour * 60 + end_minute
    
    if slot_start < earliest:
        return False, f"Las clases no pueden iniciar antes de las 7:00 AM"
    
    if slot_end > latest:
        return False, f"Las clases no pueden terminar después de las 2:49 PM"
    
    # Check if during recess
    if is_during_recess(start_hour, start_minute, end_hour, end_minute):
        return False, f"No se pueden programar clases durante el receso (10:40-11:09)"
    
    # Check if matches a predefined block
    if not is_valid_timeslot(start_hour, start_minute, end_hour, end_minute):
        return False, f"El horario debe coincidir con uno de los bloques predefinidos de 54 minutos"
    
    return True, ""
