"""
Cargador de datos con soporte para múltiples formatos (CSV, JSON, Excel)
Adaptado para leer datos con claves en español
"""

import csv
import json
import pandas as pd
from typing import List, Dict, Any, Union
from modelos import Curso, Profesor, BloqueTiempo


class CargadorDatos:
    """Maneja la carga de datos desde varios formatos de archivo (español)"""
    
    @staticmethod
    def safe_int(valor, default=None):
        """Convierte valor a int de forma segura, manejando strings de floats ('32.0')"""
        if valor is None:
            return default
        try:
            # Primero intentar conversión directa
            return int(valor)
        except (ValueError, TypeError):
            try:
                # Intentar convertir float a int (ej: '32.0' -> 32.0 -> 32)
                return int(float(valor))
            except (ValueError, TypeError):
                return default

    @staticmethod
    def cargar_cursos_csv(ruta_archivo: str) -> List[Curso]:
        """Cargar cursos desde archivo CSV"""
        cursos = []
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                # Normalizar claves
                keys = fila.keys()
                
                # Helper para obtener valor con claves ES o EN
                def get_val(es, en, default=None):
                    v = fila.get(es)
                    if v is None and en in keys:
                        v = fila[en]
                    return v if v is not None else default

                # Extraer valores básicos
                id_curso = CargadorDatos.safe_int(fila.get('id', fila.get('id')))
                nombre = get_val('nombre', 'name', 'Sin Nombre')
                
                # Prerrequisitos
                prerrequisitos = []
                prereq_raw = get_val('prerrequisitos', 'prerequisites')
                if prereq_raw:
                    parts = str(prereq_raw).replace('"', '').split(',')
                    for p in parts:
                        val = CargadorDatos.safe_int(p.strip())
                        if val is not None:
                            prerrequisitos.append(val)
                
                id_profesor = CargadorDatos.safe_int(get_val('id_profesor', 'professor_id'))
                
                # Inferir cuatrimestre si no existe columna
                cuatri = CargadorDatos.safe_int(get_val('cuatrimestre', 'semester'))
                if cuatri is None and id_curso:
                    # Heurística UTP: 101 -> 1, 901 -> 9, 1001 -> 10
                    try:
                        numeric_id = int(float(id_curso)) # Manejar '101.0'
                        cuatri = numeric_id // 100
                        if cuatri == 0: cuatri = 1 # Fallback
                    except Exception:
                        cuatri = 1
                
                # Sesiones por semana (nuevo campo opcional)
                sesiones = CargadorDatos.safe_int(get_val('sesiones_por_semana', 'sessions_per_week'), 1)
                
                curso = Curso(
                    id=id_curso,
                    nombre=nombre,
                    codigo=get_val('codigo', 'code', ''),
                    creditos=CargadorDatos.safe_int(get_val('creditos', 'credits'), 3),
                    matricula=CargadorDatos.safe_int(get_val('matricula', 'enrollment'), 0),
                    prerequisitos=prerrequisitos,
                    id_profesor=id_profesor,
                    cuatrimestre=cuatri if cuatri else 1,
                    id_grupo=CargadorDatos.safe_int(get_val('id_grupo', 'group_id'), 0),
                    sesiones_por_semana=sesiones
                )
                cursos.append(curso)

        return cursos
    
    @staticmethod
    def cargar_cursos_json(ruta_archivo: str) -> List[Curso]:
        """Cargar cursos desde archivo JSON"""
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        cursos = []
        for item in datos:
            # Helper local
            def get_val(k_es, k_en, default=None):
                return item.get(k_es, item.get(k_en, default))

            # Prerrequisitos
            prereq_raw = get_val('prerrequisitos', 'prerequisites', [])
            prerrequisitos = []
            if isinstance(prereq_raw, list):
                prerrequisitos = [CargadorDatos.safe_int(p) for p in prereq_raw if CargadorDatos.safe_int(p) is not None]
            
            curso = Curso(
                id=CargadorDatos.safe_int(item.get('id')),
                nombre=get_val('nombre', 'name'),
                codigo=get_val('codigo', 'code', ''),
                creditos=CargadorDatos.safe_int(get_val('creditos', 'credits'), 3),
                matricula=CargadorDatos.safe_int(get_val('matricula', 'enrollment'), 0),
                prerequisitos=prerrequisitos,
                id_profesor=CargadorDatos.safe_int(get_val('id_profesor', 'professor_id')),
                cuatrimestre=CargadorDatos.safe_int(get_val('cuatrimestre', 'semester'), 1),
                id_grupo=get_val('grupo', 'group_id', 'A')
            )
            cursos.append(curso)
        return cursos
    
    @staticmethod
    def cargar_cursos_excel(ruta_archivo: str) -> List[Curso]:
        """Cargar cursos desde archivo Excel"""
        df = pd.read_excel(ruta_archivo)
        cursos = []
        
        # Mapeo de columnas si no existen las españolas
        cols_map = {
            'name': 'nombre', 'code': 'codigo', 'credits': 'creditos',
            'enrollment': 'matricula', 'prerequisites': 'prerrequisitos',
            'professor_id': 'id_profesor', 'semester': 'cuatrimestre', 'group': 'grupo'
        }
        df.rename(columns=cols_map, inplace=True)
        
        for _, fila in df.iterrows():
            if 'nombre' not in fila and 'name' in fila: fila['nombre'] = fila['name']
            
            prerrequisitos = []
            if pd.notna(fila.get('prerrequisitos')):
                parts = str(fila['prerrequisitos']).replace('"', '').split(',')
                for p in parts:
                    val = CargadorDatos.safe_int(p.strip())
                    if val is not None:
                        prerrequisitos.append(val)
            
            id_profesor = CargadorDatos.safe_int(fila.get('id_profesor'))
            
            curso = Curso(
                id=CargadorDatos.safe_int(fila.get('id')),
                nombre=fila.get('nombre', 'Sin Nombre'),
                codigo=fila.get('codigo', ''),
                creditos=CargadorDatos.safe_int(fila.get('creditos'), 3),
                matricula=CargadorDatos.safe_int(fila.get('matricula'), 0),
                prerequisitos=prerrequisitos,
                id_profesor=id_profesor,
                cuatrimestre=CargadorDatos.safe_int(fila.get('cuatrimestre'), 1),
                id_grupo=fila.get('grupo', 'A')
            )
            cursos.append(curso)
        return cursos
    
    @staticmethod
    def cargar_profesores_csv(ruta_archivo: str) -> List[Profesor]:
        """Cargar profesores desde archivo CSV"""
        profesores = []
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                keys = fila.keys()
                def get_val(es, en):
                    v = fila.get(es)
                    if v is None and en in keys: return fila[en]
                    return v

                bloques = []
                bloques_raw = get_val('bloques_disponibles', 'available_timeslots')
                if bloques_raw:
                    parts = str(bloques_raw).replace('"', '').split(',')
                    for p in parts:
                        val = CargadorDatos.safe_int(p.strip())
                        if val is not None:
                            bloques.append(val)
                
                materias = []
                materias_raw = get_val('materias_capaces', 'available_courses')
                if materias_raw:
                    # Si viene como lista stringificada "['A', 'B']" o separada por comas
                    parts = str(materias_raw).replace('"', '').replace("'", "").replace('[', '').replace(']', '').split(',')
                    for p in parts:
                        if p.strip():
                            materias.append(p.strip())

                profesor = Profesor(
                    id=CargadorDatos.safe_int(fila.get('id', fila.get('id'))),
                    nombre=get_val('nombre', 'name'),
                    email=get_val('email', 'email') or '',
                    bloques_disponibles=bloques,
                    materias_capaces=materias
                )
                profesores.append(profesor)
        return profesores
    
    @staticmethod
    def cargar_profesores_json(ruta_archivo: str) -> List[Profesor]:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        profesores = []
        for item in datos:
            nombre = item.get('nombre', item.get('name'))
            email = item.get('email', '')
            bloques_raw = item.get('bloques_disponibles', item.get('available_timeslots', []))
            bloques = [CargadorDatos.safe_int(b) for b in bloques_raw if CargadorDatos.safe_int(b) is not None]
            
            materias = item.get('materias_capaces', item.get('available_courses', []))

            profesor = Profesor(
                id=CargadorDatos.safe_int(item.get('id')),
                nombre=nombre,
                email=email,
                bloques_disponibles=bloques,
                materias_capaces=materias
            )
            profesores.append(profesor)
        return profesores
    
    @staticmethod
    def cargar_bloques_tiempo_csv(ruta_archivo: str) -> List[BloqueTiempo]:
        """Cargar bloques de tiempo desde archivo CSV"""
        bloques = []
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                keys = fila.keys()
                def get_val(es, en): return fila.get(es) if fila.get(es) else fila.get(en)

                bloque = BloqueTiempo(
                    id=CargadorDatos.safe_int(fila.get('id', fila.get('id'))),
                    dia=get_val('dia', 'day'),
                    hora_inicio=CargadorDatos.safe_int(get_val('hora_inicio', 'start_hour'), 0),
                    minuto_inicio=CargadorDatos.safe_int(get_val('minuto_inicio', 'start_minute'), 0),
                    hora_fin=CargadorDatos.safe_int(get_val('hora_fin', 'end_hour'), 0),
                    minuto_fin=CargadorDatos.safe_int(get_val('minuto_fin', 'end_minute'), 0)
                )
                bloques.append(bloque)
        return bloques
    
    @staticmethod
    def cargar_bloques_tiempo_json(ruta_archivo: str) -> List[BloqueTiempo]:
        """Cargar bloques de tiempo desde archivo JSON"""
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        bloques = []
        for item in datos:
            bloque = BloqueTiempo(
                id=CargadorDatos.safe_int(item.get('id')),
                dia=item.get('dia', item.get('day')),
                hora_inicio=CargadorDatos.safe_int(item.get('hora_inicio', item.get('start_hour')), 0),
                minuto_inicio=CargadorDatos.safe_int(item.get('minuto_inicio', item.get('start_minute')), 0),
                hora_fin=CargadorDatos.safe_int(item.get('hora_fin', item.get('end_hour')), 0),
                minuto_fin=CargadorDatos.safe_int(item.get('minuto_fin', item.get('end_minute')), 0)
            )
            bloques.append(bloque)
        return bloques
    
    @staticmethod
    def detectar_formato(ruta_archivo: str) -> str:
        """Detectar formato de archivo por extensión"""
        if ruta_archivo.endswith('.csv'):
            return 'csv'
        elif ruta_archivo.endswith('.json'):
            return 'json'
        elif ruta_archivo.endswith(('.xlsx', '.xls')):
            return 'excel'
        else:
            raise ValueError(f"Formato de archivo no soportado: {ruta_archivo}")
    
    @staticmethod
    def cargar_datos(ruta_archivo: str, tipo_dato: str):
        """Cargador genérico que detecta formato y carga el tipo de dato apropiado"""
        formato = CargadorDatos.detectar_formato(ruta_archivo)
        
        cargadores = {
            ('cursos', 'csv'): CargadorDatos.cargar_cursos_csv,
            ('cursos', 'json'): CargadorDatos.cargar_cursos_json,
            ('cursos', 'excel'): CargadorDatos.cargar_cursos_excel,
            ('profesores', 'csv'): CargadorDatos.cargar_profesores_csv,
            ('profesores', 'json'): CargadorDatos.cargar_profesores_json,
            ('bloques', 'csv'): CargadorDatos.cargar_bloques_tiempo_csv,
            ('bloques', 'json'): CargadorDatos.cargar_bloques_tiempo_json,
            # Alias en inglés para compatibilidad
            ('courses', 'csv'): CargadorDatos.cargar_cursos_csv,
            ('courses', 'json'): CargadorDatos.cargar_cursos_json,
            ('courses', 'excel'): CargadorDatos.cargar_cursos_excel,
            ('professors', 'csv'): CargadorDatos.cargar_profesores_csv,
            ('professors', 'json'): CargadorDatos.cargar_profesores_json,
            ('timeslots', 'csv'): CargadorDatos.cargar_bloques_tiempo_csv,
            ('timeslots', 'json'): CargadorDatos.cargar_bloques_tiempo_json,
        }
        
        clave_cargador = (tipo_dato, formato)
        if clave_cargador in cargadores:
            return cargadores[clave_cargador](ruta_archivo)
        else:
            raise ValueError(f"No hay cargador para {tipo_dato} en formato {formato}")

