"""
Modelo Curso - Representa un curso en el currículo
"""
from typing import List


class Curso:
    """
    Clase que representa un curso académico
    
    Atributos:
        id: Identificador único del curso
        nombre: Nombre completo del curso
        codigo: Código del curso (ej: MAT101)
        creditos: Número de créditos del curso
        matricula: Número de estudiantes matriculados
        prerequisitos: Lista de IDs de cursos prerequisitos
        id_profesor: ID del profesor asignado (opcional)
        cuatrimestre: Número de cuatrimestre (1-10) para filtrado por ciclo
        id_grupo: Identificador del grupo (default: 0)
        sesiones_por_semana: Número de sesiones semanales necesarias
    """
    
    def __init__(self, id: int, nombre: str, codigo: str, creditos: int, matricula: int, 
                 prerequisitos: List[int], id_profesor: int = None, cuatrimestre: int = None,
                 id_grupo: int = 0, sesiones_por_semana: int = 1):
        self.id = id
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = creditos
        self.matricula = matricula
        self.prerequisitos = prerequisitos
        self.id_profesor = id_profesor
        self.cuatrimestre = cuatrimestre  # Número de cuatrimestre (1-10)
        self.id_grupo = id_grupo
        self.sesiones_por_semana = sesiones_por_semana  # Para bloques dobles
    
    def a_diccionario(self):
        """
        Convierte el objeto Curso a un diccionario
        
        Returns:
            dict: Representación del curso como diccionario
        """
        return {
            'id': self.id,
            'name': self.nombre,  # Mantener 'name' para compatibilidad con API
            'code': self.codigo,
            'credits': self.creditos,
            'enrollment': self.matricula,
            'prerequisites': self.prerequisitos,
            'professor_id': self.id_profesor,
            'semester': self.cuatrimestre,  # Mantener 'semester' para API
            'group_id': self.id_grupo,
            'sessions_per_week': self.sesiones_por_semana
        }
    
    def __repr__(self):
        """Representación en string del curso"""
        return f"Curso(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')"
