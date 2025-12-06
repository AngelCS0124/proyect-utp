"""
Restricciones y helpers de scheduling para bloques consecutivos
"""

from configuracion import BLOQUES_TIEMPO


def obtener_bloques_consecutivos(id_bloque):
    """
    Obtener el ID del siguiente bloque consecutivo
    Retorna None si no hay bloque consecutivo (ej: antes del receso)
    
    Args:
        id_bloque: Número de bloque actual (1-9)
    
    Returns:
        ID del siguiente bloque o None
    """
    # Bloque 4 (9:45-10:39) no puede tener bloque consecutivo por el receso
    if id_bloque == 4:
        return None
    
    # Bloque 9 es el último bloque del día
    if id_bloque == 9:
        return None
    
    # De lo contrario, el siguiente bloque es consecutivo
    return id_bloque + 1


def puede_tener_bloques_consecutivos(id_bloque):
    """
    Verificar si un bloque puede tener un bloque consecutivo después
    
    Args:
        id_bloque: Número de bloque (1-9)
    
    Returns:
        True si es posible un bloque consecutivo
    """
    return id_bloque not in [4, 9]


def obtener_bloques_dobles(dia, id_bloque_inicio):
    """
    Obtener IDs de timeslots para un bloque doble (2 bloques consecutivos)
    
    Args:
        dia: Nombre del día (ej: 'Lunes')
        id_bloque_inicio: Bloque de inicio (1-9)
    
    Returns:
        Lista de 2 IDs de timeslot o lista vacía si no es posible
    """
    if not puede_tener_bloques_consecutivos(id_bloque_inicio):
        return []
    
    # Mapear día a ID base
    mapeo_dias = {
        'Lunes': 0, 'Monday': 0,
        'Martes': 100, 'Tuesday': 100,
        'Miércoles': 200, 'Wednesday': 200,
        'Jueves': 300, 'Thursday': 300,
        'Viernes': 400, 'Friday': 400,
    }
    
    id_base = mapeo_dias.get(dia, 0)
    siguiente_bloque = obtener_bloques_consecutivos(id_bloque_inicio)
    
    if siguiente_bloque is None:
        return []
    
    return [id_base + id_bloque_inicio, id_base + siguiente_bloque]


def obtener_opciones_bloques_dobles(dia):
    """
    Obtener todas las combinaciones posibles de bloques dobles para un día
    
    Args:
        dia: Nombre del día
    
    Returns:
        Lista de diccionarios con opciones de bloques dobles
    """
    mapeo_dias = {
        'Lunes': 0, 'Monday': 0,
        'Martes': 100, 'Tuesday': 100,
        'Miércoles': 200, 'Wednesday': 200,
        'Jueves': 300, 'Thursday': 300,
        'Viernes': 400, 'Friday': 400,
    }
    
    id_base = mapeo_dias.get(dia, 0)
    opciones = []
    
    # Bloques dobles posibles:
    # Bloques 1-2 (7:00-8:49)
    # Bloques 2-3 (7:55-9:44)
    # Bloques 3-4 (8:50-10:39)
    # --- RECESO ---
    # Bloques 5-6 (11:10-12:59)
    # Bloques 6-7 (12:05-13:54)
    # Bloques 7-8 (13:00-14:49)
    # Bloques 8-9 (14:00-15:49)
    
    for bloque in [1, 2, 3, 5, 6, 7, 8]:
        siguiente_bloque = bloque + 1
        opciones.append({
            'start_block': bloque,
            'end_block': siguiente_bloque,
            'timeslot_ids': [id_base + bloque, id_base + siguiente_bloque],
            'start_time': BLOQUES_TIEMPO[bloque],
            'end_time': BLOQUES_TIEMPO[siguiente_bloque]
        })
    
    return opciones


def calcular_sesiones_necesarias(creditos):
    """
    Calcular cuántas sesiones por semana necesita un curso basado en créditos
    
    Args:
        creditos: Créditos del curso (horas)
    
    Returns:
        Número de sesiones por semana (1-10)
    """
    # Cada sesión es de 54 minutos (0.9 horas)
    # creditos / 0.9 = sesiones necesarias
    # Dividido por semanas en un cuatrimestre (aproximadamente 16 semanas)
    
    # Simplificado: 
    # 60 créditos = 1 sesión/semana
    # 75 créditos = 1-2 sesiones/semana
    # 90 créditos = 2 sesiones/semana
    # 105 créditos = 2 sesiones/semana
    
    if creditos <= 60:
        return 1
    elif creditos <= 75:
        return 2
    elif creditos <= 90:
        return 2
    else:
        return 2  # Máximo 2 sesiones por semana (puede ser bloque doble)


def obtener_info_bloque(id_bloque):
    """
    Obtener información sobre un bloque específico
    
    Args:
        id_bloque: Número de bloque (1-9)
    
    Returns:
        Diccionario con información del bloque
    """
    if id_bloque not in BLOQUES_TIEMPO:
        return None
    
    bloque = BLOQUES_TIEMPO[id_bloque]
    return {
        'id': id_bloque,
        'name': bloque['name'],
        'start': f"{bloque['start_hour']:02d}:{bloque['start_minute']:02d}",
        'end': f"{bloque['end_hour']:02d}:{bloque['end_minute']:02d}",
        'can_be_double': puede_tener_bloques_consecutivos(id_bloque)
    }


# Alias para compatibilidad con código existente
get_consecutive_blocks = obtener_bloques_consecutivos
can_have_consecutive_blocks = puede_tener_bloques_consecutivos
get_double_block_timeslots = obtener_bloques_dobles
get_all_double_block_options = obtener_opciones_bloques_dobles
calculate_sessions_needed = calcular_sesiones_necesarias
get_block_info = obtener_info_bloque
