"""
Modelo Profesor - Representa un profesor en el sistema
"""
from typing import List


class Profesor:
    """
    Clase que representa un profesor
    
    Atributos:
        id: Identificador único del profesor
        nombre: Nombre completo del profesor
        email: Correo electrónico del profesor
        bloques_disponibles: Lista de IDs de bloques de tiempo disponibles
    """
    
    def __init__(self, id: int, nombre: str, email: str = "", bloques_disponibles: List[int] = None, materias_capaces: List[str] = None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.bloques_disponibles = bloques_disponibles if bloques_disponibles is not None else []
        self.materias_capaces = materias_capaces if materias_capaces is not None else []
    
    def a_diccionario(self):
        """
        Convierte el objeto Profesor a un diccionario
        
        Returns:
            dict: Representación del profesor como diccionario
        """
        return {
            'id': self.id,
            'name': self.nombre,  # Mantener 'name' para compatibilidad con API
            'email': self.email,
            'available_timeslots': self.bloques_disponibles,  # Mantener nombre API
            'available_courses': self.materias_capaces # Lista de códigos de materia
        }
    
    # Alias para compatibilidad con código existente
    to_dict = a_diccionario
    
    def __repr__(self):
        """Representación en string del profesor"""
        return f"Profesor(id={self.id}, nombre='{self.nombre}', email='{self.email}')"
