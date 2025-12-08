"""
Modelo BloqueTiempo - Representa un bloque de tiempo en el horario
"""


class BloqueTiempo:
    """
    Clase que representa un bloque de tiempo en el horario
    
    Atributos:
        id: Identificador único del bloque
        dia: Día de la semana (Lunes, Martes, etc.)
        hora_inicio: Hora de inicio (0-23)
        minuto_inicio: Minuto de inicio (0-59)
        hora_fin: Hora de fin (0-23)
        minuto_fin: Minuto de fin (0-59)
    """
    
    def __init__(self, id: int, dia: str, hora_inicio: int, minuto_inicio: int, 
                 hora_fin: int, minuto_fin: int):
        self.id = id
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.minuto_inicio = minuto_inicio
        self.hora_fin = hora_fin
        self.minuto_fin = minuto_fin
    
    def a_diccionario(self):
        """
        Convierte el objeto BloqueTiempo a un diccionario
        
        Returns:
            dict: Representación del bloque de tiempo como diccionario
        """
        # Defensive: ensure no None values
        hora_inicio = self.hora_inicio if self.hora_inicio is not None else 0
        minuto_inicio = self.minuto_inicio if self.minuto_inicio is not None else 0
        hora_fin = self.hora_fin if self.hora_fin is not None else 0
        minuto_fin = self.minuto_fin if self.minuto_fin is not None else 0
        
        return {
            'id': self.id,
            'day': self.dia,  # Mantener 'day' para compatibilidad con API
            'start_hour': hora_inicio,
            'start_minute': minuto_inicio,
            'end_hour': hora_fin,
            'end_minute': minuto_fin,
            'display': f"{self.dia} {hora_inicio:02d}:{minuto_inicio:02d}-{hora_fin:02d}:{minuto_fin:02d}"
        }
    
    # Alias para compatibilidad con código existente
    to_dict = a_diccionario
    
    def __repr__(self):
        """Representación en string del bloque de tiempo"""
        # Defensive: ensure no None values
        hora_inicio = self.hora_inicio if self.hora_inicio is not None else 0
        minuto_inicio = self.minuto_inicio if self.minuto_inicio is not None else 0
        hora_fin = self.hora_fin if self.hora_fin is not None else 0
        minuto_fin = self.minuto_fin if self.minuto_fin is not None else 0
        
        return f"BloqueTiempo(id={self.id}, dia='{self.dia}', {hora_inicio:02d}:{minuto_inicio:02d}-{hora_fin:02d}:{minuto_fin:02d})"

