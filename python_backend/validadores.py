"""
Validación de entrada para el sistema de horarios
"""

from typing import List, Dict, Any
from modelos import Curso, Profesor, BloqueTiempo


class Validador:
    """Valida datos de entrada y estado del sistema"""
    
    @staticmethod
    def validar_cursos(cursos: List[Curso]) -> Dict[str, Any]:
        """
        Valida datos de cursos
        
        Args:
            cursos: Lista de objetos Curso
            
        Returns:
            dict: {'valid': bool, 'errors': list, 'warnings': list}
        """
        errores = []
        advertencias = []
        
        if not cursos:
            errores.append("No se proporcionaron cursos")
            return {'valid': False, 'errors': errores, 'warnings': advertencias}
        
        # Verificar IDs duplicados
        ids = [c.id for c in cursos]
        if len(ids) != len(set(ids)):
            errores.append("Se encontraron IDs de curso duplicados")
        
        # Verificar números de matrícula válidos
        for curso in cursos:
            if curso.matricula <= 0:
                errores.append(f"Curso '{curso.nombre}' tiene matrícula inválida: {curso.matricula}")
            
            # Verificar que los prerequisitos existan
            for id_prereq in curso.prerequisitos:
                if id_prereq not in ids:
                    advertencias.append(f"Curso '{curso.nombre}' tiene prerequisito inexistente ID: {id_prereq}")
        
        return {
            'valid': len(errores) == 0,
            'errors': errores,
            'warnings': advertencias
        }
    
    @staticmethod
    def validar_profesores(profesores: List[Profesor]) -> Dict[str, Any]:
        """
        Valida datos de profesores
        
        Args:
            profesores: Lista de objetos Profesor
            
        Returns:
            dict: {'valid': bool, 'errors': list, 'warnings': list}
        """
        errores = []
        advertencias = []
        
        if not profesores:
            errores.append("No se proporcionaron profesores")
            return {'valid': False, 'errors': errores, 'warnings': advertencias}
        
        # Verificar IDs duplicados
        ids = [p.id for p in profesores]
        if len(ids) != len(set(ids)):
            errores.append("Se encontraron IDs de profesor duplicados")
        
        # Verificar disponibilidad
        for profesor in profesores:
            if not profesor.bloques_disponibles:
                advertencias.append(f"Profesor '{profesor.nombre}' no tiene bloques de tiempo disponibles")
        
        return {
            'valid': len(errores) == 0,
            'errors': errores,
            'warnings': advertencias
        }
    
    @staticmethod
    def validar_bloques_tiempo(bloques: List[BloqueTiempo]) -> Dict[str, Any]:
        """
        Valida datos de bloques de tiempo
        
        Args:
            bloques: Lista de objetos BloqueTiempo
            
        Returns:
            dict: {'valid': bool, 'errors': list, 'warnings': list}
        """
        from configuracion import VALID_DAYS, validate_timeslot_constraints
        
        errores = []
        advertencias = []
        
        if not bloques:
            errores.append("No se proporcionaron bloques de tiempo")
            return {'valid': False, 'errors': errores, 'warnings': advertencias}
        
        # Verificar IDs duplicados
        ids = [b.id for b in bloques]
        if len(ids) != len(set(ids)):
            errores.append("Se encontraron IDs de bloque de tiempo duplicados")
        
        # Obtener todos los días válidos (español e inglés)
        dias_validos = VALID_DAYS['es'] + VALID_DAYS['en']
        
        # Verificar cada bloque de tiempo
        for bloque in bloques:
            # Validar día (solo días entre semana)
            if bloque.dia not in dias_validos:
                errores.append(f"Día inválido: {bloque.dia}. Solo se permiten días entre semana (Lunes-Viernes)")
            
            # Validar horas
            if not (0 <= bloque.hora_inicio < 24 and 0 <= bloque.hora_fin < 24):
                errores.append(f"Horas inválidas para bloque {bloque.id}")
            
            # Validar minutos
            if not (0 <= bloque.minuto_inicio < 60 and 0 <= bloque.minuto_fin < 60):
                errores.append(f"Minutos inválidos para bloque {bloque.id}")
            
            # Validar rango de tiempo
            tiempo_inicio = bloque.hora_inicio * 60 + bloque.minuto_inicio
            tiempo_fin = bloque.hora_fin * 60 + bloque.minuto_fin
            if tiempo_inicio >= tiempo_fin:
                errores.append(f"Bloque {bloque.id} tiene rango de tiempo inválido")
            
            # Validar contra restricciones de bloques de tiempo UTP
            es_valido, mensaje_error = validate_timeslot_constraints(
                bloque.hora_inicio,
                bloque.minuto_inicio,
                bloque.hora_fin,
                bloque.minuto_fin
            )
            
            if not es_valido:
                errores.append(f"Bloque {bloque.id}: {mensaje_error}")
        
        return {
            'valid': len(errores) == 0,
            'errors': errores,
            'warnings': advertencias
        }
    
    @staticmethod
    def validar_asignaciones_cursos(cursos: List[Curso], profesores: List[Profesor]) -> Dict[str, Any]:
        """
        Valida que todos los cursos tengan profesores asignados
        
        Args:
            cursos: Lista de objetos Curso
            profesores: Lista de objetos Profesor
            
        Returns:
            dict: {'valid': bool, 'errors': list, 'warnings': list}
        """
        errores = []
        advertencias = []
        
        ids_profesores = {p.id for p in profesores}
        
        for curso in cursos:
            if curso.id_profesor is None:
                print(f"DEBUG: Advertencia - Curso {curso.nombre} no tiene profesor")
                advertencias.append(f"Curso '{curso.nombre}' no tiene profesor asignado")
            elif curso.id_profesor not in ids_profesores:
                print(f"DEBUG: Error - Curso {curso.nombre} tiene profesor inválido {curso.id_profesor}")
                errores.append(f"Curso '{curso.nombre}' asignado a profesor inexistente ID: {curso.id_profesor}")
        
        print(f"DEBUG: Resultado de validación - Errores: {len(errores)}, Advertencias: {len(advertencias)}")
        return {
            'valid': len(errores) == 0,
            'errors': errores,
            'warnings': advertencias
        }
    
    @staticmethod
    def validar_todos_datos(cursos: List[Curso], profesores: List[Profesor],
                           bloques: List[BloqueTiempo]) -> Dict[str, Any]:
        """
        Valida todos los datos juntos
        
        Args:
            cursos: Lista de objetos Curso
            profesores: Lista de objetos Profesor
            bloques: Lista de objetos BloqueTiempo
            
        Returns:
            dict: {'valid': bool, 'errors': list, 'warnings': list}
        """
        todos_errores = []
        todas_advertencias = []
        
        # Validar cada tipo de dato
        validacion_cursos = Validador.validar_cursos(cursos)
        todos_errores.extend(validacion_cursos['errors'])
        todas_advertencias.extend(validacion_cursos['warnings'])
        
        validacion_profesores = Validador.validar_profesores(profesores)
        todos_errores.extend(validacion_profesores['errors'])
        todas_advertencias.extend(validacion_profesores['warnings'])
        
        validacion_bloques = Validador.validar_bloques_tiempo(bloques)
        todos_errores.extend(validacion_bloques['errors'])
        todas_advertencias.extend(validacion_bloques['warnings'])
        
        # Validar asignaciones
        validacion_asignaciones = Validador.validar_asignaciones_cursos(cursos, profesores)
        todos_errores.extend(validacion_asignaciones['errors'])
        todas_advertencias.extend(validacion_asignaciones['warnings'])
        
        return {
            'valid': len(todos_errores) == 0,
            'errors': todos_errores,
            'warnings': todas_advertencias
        }
