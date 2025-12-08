"""
Motor CSP para Generación de Horarios Escolares

Implementa un sistema de Constraint Satisfaction Problem con:
- Backtracking con forward checking
- Heurísticas MRV (Minimum Remaining Values) y LCV (Least Constraining Value)
- Jerarquía de restricciones: Hard → Estructurales → Soft

Autor: Sistema UTP
Fecha: 2025-12-07
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import copy
import random

from modelos import Curso, Profesor, BloqueTiempo, Horario, Asignacion


class Variable:
    """Representa una variable CSP: una sesión específica de un curso"""
    
    def __init__(self, curso: Curso, numero_sesion: int):
        """
        Args:
            curso: El curso al que pertenece esta sesión
            numero_sesion: Número de sesión (1, 2, 3...) para este curso
        """
        self.curso = curso
        self.numero_sesion = numero_sesion
        self.id = f"{curso.id}_s{numero_sesion}"
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Variable) and self.id == other.id
    
    def __repr__(self):
        return f"Variable({self.curso.nombre}, sesión {self.numero_sesion})"


class Dominio:
    """Dominio de valores posibles para una variable"""
    
    def __init__(self, bloques: Set[BloqueTiempo]):
        self.bloques = bloques.copy()
    
    def __len__(self):
        return len(self.bloques)
    
    def remover(self, bloque: BloqueTiempo):
        self.bloques.discard(bloque)
    
    def copiar(self) -> 'Dominio':
        return Dominio(self.bloques)


class CSPScheduler:
    """
    Motor CSP para generación de horarios
    
    Implementa backtracking con forward checking y heurísticas MRV/LCV
    """
    
    def __init__(self, cursos: List[Curso], profesores: List[Profesor], 
                 bloques_tiempo: List[BloqueTiempo], max_intentos: int = 100000):
        self.cursos = cursos
        self.profesores = profesores
        self.bloques_tiempo = bloques_tiempo
        self.max_intentos = max_intentos  # Aumentado de 10k a 100k
        
        # Mapeo rápido
        self.map_profesores = {p.id: p for p in profesores}
        self.map_bloques = {b.id: b for b in bloques_tiempo}
        
        # Capacidad de profesores (para validar carga)
        self.prof_capacity: Dict[int, int] = {}  # id_profesor -> num_bloques_disponibles
        self.prof_load: Dict[int, int] = {}      # id_profesor -> sesiones_asignadas
        
        # Estado del CSP
        self.variables: List[Variable] = []
        self.dominios: Dict[Variable, Dominio] = {}
        self.dominios_iniciales: Dict[Variable, Dominio] = {}  # Para reintentos
        self.asignaciones: List[Asignacion] = []
        
        # Estadísticas
        self.intentos = 0
        self.backtracks = 0
    
    def resolver(self, max_reintentos: int = 3) -> Tuple[bool, Optional[Horario]]:
        """
        Resuelve el CSP y retorna horario completo con reintentos
        
        Args:
            max_reintentos: Número de intentos con orden aleatorio diferente
        
        Returns:
            (exito, horario): Tupla con éxito bool y objeto Horario si exitoso
        """
        # 1. Aplicar restricciones estructurales
        self._aplicar_restricciones_estructurales()
        
        # 2. Inicializar variables y dominios
        self._inicializar_csp()
        
        # 3. Pre-validación de factibilidad
        es_factible, mensaje = self._validar_factibilidad()
        if not es_factible:
            print(f"⚠️  Problema no factible: {mensaje}", flush=True)
            return False, None
        
        # 4. Intentar resolver con reintentos random
        for intento in range(max_reintentos):
            if intento > 0:
                print(f"🔄 Reintento {intento+1}/{max_reintentos} con orden aleatorio...", flush=True)
                random.shuffle(self.variables)
                self._reiniciar_dominios()
            
            self.intentos = 0
            self.backtracks = 0
            self.asignaciones = []
            
            exito = self._backtrack()
            
            if exito:
                # Construir horario
                horario = Horario()
                for asig in self.asignaciones:
                    # Obtener bloque de tiempo para incluir display
                    bloque = self.map_bloques.get(asig.id_bloque_tiempo)
                    timeslot_display = ""
                    if bloque:
                        timeslot_display = f"{bloque.dia} {bloque.hora_inicio:02d}:{bloque.minuto_inicio:02d}-{bloque.hora_fin:02d}:{bloque.minuto_fin:02d}"
                    
                    horario.agregar_asignacion(
                        asig.id_curso,
                        asig.id_profesor,
                        asig.id_bloque_tiempo,
                        course_name=asig.nombre_curso,
                        professor_name=asig.nombre_profesor,
                        semester=asig.cuatrimestre,
                        group=asig.id_grupo,
                        timeslot_display=timeslot_display
                    )
                print(f"✅ Solución encontrada en intento {intento+1} con {self.intentos} intentos", flush=True)
                return True, horario
        
        print(f"❌ No se encontró solución después de {max_reintentos} reintentos", flush=True)
        return False, None
    
    def _aplicar_restricciones_estructurales(self):
        """
        EC1: Asignar un profesor a cada curso si no tiene
        EC2: Los profesores ya vienen con disponibilidad filtrada
        
        Usa fuzzy matching para detectar coincidencias parciales
        """
        # Calcular carga inicial
        carga = {p.id: 0 for p in self.profesores}
        for c in self.cursos:
            if c.id_profesor:
                carga[c.id_profesor] = carga.get(c.id_profesor, 0) + 1
        
        for curso in self.cursos:
            if curso.id_profesor is None:
                candidatos = []
                curso_code = str(curso.codigo).strip().upper() if curso.codigo else ""
                curso_name = str(curso.nombre).strip().upper()
                
                # Buscar profesores capaces con matching mejorado
                for p in self.profesores:
                    matched = False
                    
                    for materia_capaz in p.materias_capaces:
                        mat_upper = str(materia_capaz).strip().upper()
                        
                        # 1. Match exacto de código
                        if curso_code and mat_upper == curso_code:
                            candidatos.append(p)
                            matched = True
                            break
                        
                        # 2. Match exacto de nombre
                        if mat_upper == curso_name:
                            candidatos.append(p)
                            matched = True
                            break
                        
                        # 3. Match parcial (fuzzy) - buscar palabras clave
                        # Ej: "INGLÉS" matchea con "INGLÉS II", "INGLÉS V", etc.
                        mat_words = set(mat_upper.split())
                        curso_words = set(curso_name.split())
                        
                        # Si comparten palabras significativas (no artículos)
                        common = mat_words & curso_words
                        if common and len(common) >= 1:
                            # Filtrar palabras muy cortas que causan false positives
                            significant = [w for w in common if len(w) > 2]
                            if significant:
                                candidatos.append(p)
                                matched = True
                                break
                    
                    if matched:
                        continue
                
                if candidatos:
                    # Seleccionar el con menos carga actual
                    mejor = min(candidatos, key=lambda p: carga[p.id])
                    curso.id_profesor = mejor.id
                    carga[mejor.id] += 1
                    print(f"   Auto-asignado: {curso.nombre} → {mejor.nombre}", flush=True)
    
    def _inicializar_csp(self):
        """Inicializa variables y dominios para el CSP con validación de capacidad"""
        self.variables = []
        self.dominios = {}
        
        # 1. Calcular capacidad de cada profesor
        for profesor in self.profesores:
            # Capacidad = bloques que realmente existen en el sistema
            bloques_validos = [
                bid for bid in profesor.bloques_disponibles
                if bid in self.map_bloques
            ]
            self.prof_capacity[profesor.id] = len(bloques_validos)
            self.prof_load[profesor.id] = 0
        
        # 2. Contar sesiones ya asignadas
        for curso in self.cursos:
            if curso.id_profesor and curso.id_profesor in self.prof_load:
                # Cada curso cuenta por sus sesiones por semana
                self.prof_load[curso.id_profesor] += curso.sesiones_por_semana
        
        print("📊 Capacidad de Profesores:", flush=True)
        for pid, cap in self.prof_capacity.items():
            prof = self.map_profesores.get(pid)
            carga = self.prof_load.get(pid, 0)
            print(f"   {prof.nombre}: {carga}/{cap} sesiones", flush=True)
        
        # 3. Crear variables solo si hay capacidad
        for curso in self.cursos:
            if curso.id_profesor is None:
                continue  # Skip cursos sin profesor
            
            profesor = self.map_profesores.get(curso.id_profesor)
            if not profesor:
                print(f"⚠️  Profesor ID {curso.id_profesor} no encontrado para {curso.nombre}", flush=True)
                continue
            
            # Validar capacidad disponible
            carga_actual = self.prof_load.get(profesor.id, 0)
            sesiones = curso.sesiones_por_semana
            capacidad = self.prof_capacity.get(profesor.id, 0)
            
            if carga_actual + sesiones > capacidad:
                print(f"⚠️  {profesor.nombre} sin capacidad para {curso.nombre} ({carga_actual + sesiones} > {capacidad})", flush=True)
                continue  # Saltar este curso - NO crear variables
            
            # Crear una variable por cada sesión necesaria
            for num_sesion in range(1, sesiones + 1):
                variable = Variable(curso, num_sesion)
                self.variables.append(variable)
                
                # Dominio: bloques disponibles del profesor
                bloques_disponibles = {
                    self.map_bloques[bid]
                    for bid in profesor.bloques_disponibles
                    if bid in self.map_bloques
                }
                self.dominios[variable] = Dominio(bloques_disponibles)
        
        print(f"✓ Variables creadas: {len(self.variables)}", flush=True)
        
        # Guardar copia de dominios iniciales para reintentos
        self.dominios_iniciales = {v: self.dominios[v].copiar() for v in self.variables}
    def _backtrack(self, asignadas: Set[str] = None) -> bool:
        """
        Backtracking con forward checking y heurísticas MRV/LCV
        
        Args:
            asignadas: Conjunto de IDs de variables ya asignadas
            
        Returns:
            True si encuentra solución, False si no
        """
        if asignadas is None:
            asignadas = set()
        
        # ¿Todas las variables asignadas?
        if len(asignadas) == len(self.variables):
            return True
        
        # Seleccionar variable con MRV
        variable = self._seleccionar_variable_mrv(asignadas)
        if not variable:
            return True  # Todas asignadas
        
        # Marcar como asignada
        asignadas.add(variable.id)
        
        # Ordenar dominio con LCV
        bloques_ordenados = self._ordenar_dominio_lcv(variable, asignadas)
        
        for bloque in bloques_ordenados:
            self.intentos += 1
            
            # Límite de seguridad para evitar loops infinitos
            if self.intentos > self.max_intentos:
                return False
            
            # Crear asignación temporal
            asignacion = self._crear_asignacion(variable.curso, bloque)
            asignacion.variable_id = variable.id  # Añadir ID de variable
            
            # Verificar hard constraints
            if not self._es_consistente(asignacion):
                continue
            
            # Asignar
            self.asignaciones.append(asignacion)
            
            # Forward checking
            eliminados = self._forward_check(asignacion)
            
            # Verificar dominios vacíos
            if not self._tiene_dominio_vacio(asignadas):
                # Recursión
                if self._backtrack(asignadas):
                    return True
            
            # Backtrack
            self.backtracks += 1
            asignadas.discard(variable.id)  # Quitar de asignadas
            self.asignaciones.pop()
            self._restaurar_dominios(eliminados)
        
        return False

    
    def _seleccionar_variable_mrv(self, asignadas: Set[str]) -> Optional[Variable]:
        """
        Heurística MRV: Selecciona variable con menor dominio
        
        Args:
            asignadas: Conjunto de IDs de variables ya asignadas
            
        Returns:
            Variable con menor número de valores disponibles
        """
        no_asignadas = [v for v in self.variables if v.id not in asignadas]
        
        if not no_asignadas:
            return None
        
        return min(no_asignadas, key=lambda v: len(self.dominios[v]))
    
    def _ordenar_dominio_lcv(self, variable: Variable, asignadas: set) -> List[BloqueTiempo]:
        """
        Least Constraining Value: ordena bloques por menor restricción
        y favorece FUERTEMENTE distribución en múltiples días
        """
        bloques = list(self.dominios[variable].bloques)
        if not bloques:
            return []
        
        # Contar días ya usados por TODOS los cursos (no solo este)
        dias_usados_global = set()
        for asig in self.asignaciones:
            bloque = self.map_bloques.get(asig.id_bloque_tiempo)
            if bloque:
                dias_usados_global.add(bloque.dia)
        
        # También contar días usados por este curso específico
        dias_usados_curso = set()
        for asig in self.asignaciones:
            if asig.id_curso == variable.curso.id:
                bloque = self.map_bloques.get(asig.id_bloque_tiempo)
                if bloque:
                    dias_usados_curso.add(bloque.dia)
        
        # Calcular score para cada bloque
        scores = []
        for bloque in bloques:
            conflictos = 0
            
            # Contar conflictos con otras variables no asignadas
            for otra_var in self.variables:
                if otra_var.id in asignadas:
                    continue
                if otra_var.id == variable.id:
                    continue
                
                # Mismo profesor o mismo grupo (si != 0)
                if otra_var.curso.id_profesor == variable.curso.id_profesor:
                    if bloque in self.dominios[otra_var].bloques:
                        conflictos += 1
                elif (variable.curso.id_grupo != 0 and 
                      otra_var.curso.id_grupo == variable.curso.id_grupo):
                    if bloque in self.dominios[otra_var].bloques:
                        conflictos += 1
            
            # BONUS MUY FUERTE: Favorecer días diferentes
            dia_bonus = 0
            
            # Prioridad 1: Días NO usados por este curso
            if bloque.dia not in dias_usados_curso:
                dia_bonus -= 1000  # MUY alta prioridad
            
            # Prioridad 2: Días con menos clases globalmente
            count_dia = sum(1 for a in self.asignaciones 
                           if self.map_bloques.get(a.id_bloque_tiempo, None) and 
                           self.map_bloques[a.id_bloque_tiempo].dia == bloque.dia)
            dia_bonus += count_dia * 10  # Penalizar días sobrecargados
            
            scores.append((bloque, conflictos + dia_bonus))
        
        # Ordenar por score (menor primero)
        scores.sort(key=lambda x: x[1])
        return [b for b, _ in scores]
    
    def _crear_asignacion(self, curso: Curso, bloque: BloqueTiempo):
        """Crea un objeto Asignacion compatible con el sistema existente"""
        # Usar constructor existente: Asignacion(curso, bloque, id_profesor)
        asignacion = Asignacion(curso, bloque, curso.id_profesor)
        
        # Agregar atributos adicionales para compatibilidad con CSP
        asignacion.id_curso = curso.id
        asignacion.id_profesor = curso.id_profesor
        asignacion.id_bloque_tiempo = bloque.id
        
        profesor = self.map_profesores.get(curso.id_profesor)
        asignacion.nombre_curso = curso.nombre
        asignacion.nombre_profesor = profesor.nombre if profesor else "Sin Profesor"
        asignacion.cuatrimestre = curso.cuatrimestre or 1
        asignacion.id_grupo = curso.id_grupo or 0
        
        return asignacion

    
    def _es_consistente(self, asignacion: Asignacion) -> bool:
        """
        Verifica hard constraints
        
        HC1: Profesor no puede estar en 2 lugares al mismo tiempo
        HC2: Grupo no puede tener 2 clases al mismo tiempo (solo si grupo != 0)
        HC3: Bloque debe existir (ya verificado en dominio)
        
        Nota: id_grupo == 0 significa "sin grupo asignado", no se aplica restricción
        """
        for asig_existente in self.asignaciones:
            # Mismo timeslot
            if asig_existente.id_bloque_tiempo == asignacion.id_bloque_tiempo:
                # HC1: Mismo profesor
                if asig_existente.id_profesor == asignacion.id_profesor:
                    return False
                
                # HC2: Mismo grupo (solo si ambos tienen grupo != 0)
                if (asignacion.id_grupo != 0 and 
                    asig_existente.id_grupo == asignacion.id_grupo):
                    return False
        
        return True
    
    def _forward_check(self, asignacion: Asignacion) -> Dict[Variable, Set[BloqueTiempo]]:
        """
        Forward checking: Elimina valores inconsistentes de dominios futuros
        
        Returns:
            Dict con valores eliminados para restaurar en backtrack
        """
        eliminados = defaultdict(set)
        bloque = self.map_bloques[asignacion.id_bloque_tiempo]
        asignadas = {asig.variable_id for asig in self.asignaciones}
        
        for variable in self.variables:
            if variable.id in asignadas:
                continue
            
            # ¿Este bloque conflictuaría con esta variable?
            debe_eliminar = False
            
            # Mismo profesor
            if variable.curso.id_profesor == asignacion.id_profesor:
                debe_eliminar = True
            
            # Mismo grupo (solo si ambos tienen grupo != 0)
            if (asignacion.id_grupo != 0 and 
                variable.curso.id_grupo == asignacion.id_grupo):
                debe_eliminar = True
            
            if debe_eliminar and bloque in self.dominios[variable].bloques:
                self.dominios[variable].remover(bloque)
                eliminados[variable].add(bloque)
        
        return eliminados
    
    def _restaurar_dominios(self, eliminados: Dict[Variable, Set[BloqueTiempo]]):
        """Restaura dominios después de backtrack"""
        for variable, bloques in eliminados.items():
            self.dominios[variable].bloques.update(bloques)
    
    def _tiene_dominio_vacio(self, asignadas: Set[str]) -> bool:
        """Verifica si alguna variable no asignada tiene dominio vacío"""
        for variable in self.variables:
            if variable.id not in asignadas and len(self.dominios[variable]) == 0:
                return True
        return False
    
    def _validar_factibilidad(self) -> Tuple[bool, Optional[str]]:
        """
        Verifica si el problema es potencialmente resoluble antes de empezar
        
        Returns:
            (es_factible, mensaje_error): Tupla con bool y mensaje si no factible
        """
        for variable in self.variables:
            dominio_size = len(self.dominios[variable])
            
            if dominio_size == 0:
                return False, f"Variable {variable} no tiene bloques disponibles"
        
        # Verificar que hay suficientes bloques únicos por profesor
        for profesor in self.profesores:
            vars_profesor = [v for v in self.variables if v.curso.id_profesor == profesor.id]
            if len(vars_profesor) > len(profesor.bloques_disponibles):
                return False, f"Profesor {profesor.nombre} necesita {len(vars_profesor)} bloques pero solo tiene {len(profesor.bloques_disponibles)} disponibles"
        
        return True, None
    
    def _reiniciar_dominios(self):
        """Reinicia dominios a su estado inicial para reintentos"""
        for variable in self.variables:
            self.dominios[variable] = self.dominios_iniciales[variable].copiar()
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de la ejecución"""
        return {
            'intentos': self.intentos,
            'backtracks': self.backtracks,
            'asignaciones': len(self.asignaciones),
            'variables': len(self.variables)
        }
