"""
Modelo Horario - Representa un horario generado
"""
from typing import List, Dict, Any


class Horario:
    """
    Clase que representa un horario generado
    
    Atributos:
        asignaciones: Lista de asignaciones de cursos a bloques de tiempo
        metadatos: Información adicional sobre la generación del horario
    """
    
    def __init__(self, asignaciones: List[Dict[str, Any]] = None, metadatos: Dict[str, Any] = None):
        self.asignaciones = asignaciones if asignaciones is not None else []
        self.metadatos = metadatos if metadatos is not None else {}
    
    def a_diccionario(self):
        """
        Convierte el objeto Horario a un diccionario
        
        Returns:
            dict: Representación del horario como diccionario
        """
        return {
            'assignments': self.asignaciones,  # Mantener 'assignments' para API
            'metadata': self.metadatos
        }
    
    def agregar_asignacion(self, id_curso: int, id_profesor: int, id_bloque: int):
        """
        Agrega una asignación al horario
        
        Args:
            id_curso: ID del curso
            id_profesor: ID del profesor
            id_bloque: ID del bloque de tiempo
        """
        self.asignaciones.append({
            'course_id': id_curso,
            'professor_id': id_profesor,
            'timeslot_id': id_bloque
        })
    
    def __repr__(self):
        """Representación en string del horario"""
        return f"Horario(asignaciones={len(self.asignaciones)}, metadatos={self.metadatos})"
