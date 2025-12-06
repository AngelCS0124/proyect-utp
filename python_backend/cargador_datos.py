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
    def cargar_cursos_csv(ruta_archivo: str) -> List[Curso]:
        """Cargar cursos desde archivo CSV"""
        cursos = []
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                prerrequisitos = []
                if fila.get('prerrequisitos'):
                    prerrequisitos = [int(x.strip()) for x in str(fila['prerrequisitos']).split(',') if x.strip()]
                
                # Manejo de campos opcionales y tipos
                id_profesor_val = fila.get('id_profesor')
                id_profesor = int(id_profesor_val) if id_profesor_val and str(id_profesor_val).strip() else None
                
                curso = Curso(
                    id=int(fila['id']),
                    nombre=fila['nombre'],
                    codigo=fila.get('codigo', ''),
                    creditos=int(fila.get('creditos', 3)),
                    matricula=int(fila['matricula']),
                    prerequisitos=prerrequisitos,
                    id_profesor=id_profesor
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
            curso = Curso(
                id=item['id'],
                nombre=item['nombre'],
                codigo=item.get('codigo', ''),
                creditos=item.get('creditos', 3), # JSON sample uses 'credits' sometimes, checking...
                matricula=item['matricula'],
                prerequisitos=item.get('prerrequisitos', []),
                id_profesor=item.get('id_profesor')
            )
            cursos.append(curso)
        return cursos
    
    @staticmethod
    def cargar_cursos_excel(ruta_archivo: str) -> List[Curso]:
        """Cargar cursos desde archivo Excel"""
        df = pd.read_excel(ruta_archivo)
        cursos = []
        
        for _, fila in df.iterrows():
            prerrequisitos = []
            if pd.notna(fila.get('prerrequisitos')):
                prerrequisitos = [int(x.strip()) for x in str(fila['prerrequisitos']).split(',') if x.strip()]
            
            id_profesor = None
            if pd.notna(fila.get('id_profesor')):
                try:
                    id_profesor = int(fila['id_profesor'])
                except (ValueError, TypeError):
                    pass
            
            curso = Curso(
                id=int(fila['id']),
                nombre=fila['nombre'],
                codigo=fila.get('codigo', ''),
                creditos=int(fila.get('creditos', 3)),
                matricula=int(fila['matricula']),
                prerequisitos=prerrequisitos,
                id_profesor=id_profesor
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
                bloques = []
                if fila.get('bloques_disponibles'):
                    bloques = [int(x.strip()) for x in str(fila['bloques_disponibles']).split(',') if x.strip()]
                
                profesor = Profesor(
                    id=int(fila['id']),
                    nombre=fila['nombre'],
                    email=fila.get('email', ''),
                    bloques_disponibles=bloques
                )
                profesores.append(profesor)
        return profesores
    
    @staticmethod
    def cargar_profesores_json(ruta_archivo: str) -> List[Profesor]:
        """Cargar profesores desde archivo JSON"""
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        profesores = []
        for item in datos:
            profesor = Profesor(
                id=item['id'],
                nombre=item['nombre'],
                email=item.get('email', ''),
                bloques_disponibles=item.get('bloques_disponibles', [])
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
                bloque = BloqueTiempo(
                    id=int(fila['id']),
                    dia=fila['dia'],
                    hora_inicio=int(fila['hora_inicio']),
                    minuto_inicio=int(fila['minuto_inicio']),
                    hora_fin=int(fila['hora_fin']),
                    minuto_fin=int(fila['minuto_fin'])
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
                id=item['id'],
                dia=item['dia'],
                hora_inicio=item['hora_inicio'],
                minuto_inicio=item['minuto_inicio'],
                hora_fin=item['hora_fin'],
                minuto_fin=item['minuto_fin']
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
