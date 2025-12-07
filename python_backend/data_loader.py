"""
Data loader supporting multiple formats (CSV, JSON, Excel)
"""

import csv
import json
import pandas as pd
from typing import List, Dict, Any
from modelos import Curso, Profesor, BloqueTiempo


class DataLoader:
    """Handles loading data from various file formats"""
    
    @staticmethod
    def load_courses_from_csv(filepath: str) -> List[Curso]:
        """Load courses from CSV file"""
        courses = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prerequisites = []
                if row.get('prerequisites'):
                    prerequisites = [int(x.strip()) for x in row['prerequisites'].split(',') if x.strip()]
                
                course = Curso(
                    id=int(float(row['id'])),
                    nombre=row['name'],
                    codigo=row.get('code', ''),
                    creditos=int(float(row.get('credits', 3))),
                    matricula=int(float(row['enrollment'])),
                    prerequisitos=prerequisites,
                    id_profesor=int(float(row['professor_id'])) if row.get('professor_id') and row.get('professor_id').strip() else None
                )
                courses.append(course)
        return courses
    
    @staticmethod
    def load_courses_from_json(filepath: str) -> List[Curso]:
        """Load courses from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        courses = []
        for item in data:
            course = Curso(
                id=item['id'],
                nombre=item['name'],
                codigo=item.get('code', ''),
                creditos=item.get('credits', 3),
                matricula=item['enrollment'],
                prerequisitos=item.get('prerequisites', [])
            )
            courses.append(course)
        return courses
    
    @staticmethod
    def load_courses_from_excel(filepath: str) -> List[Curso]:
        """Load courses from Excel file"""
        df = pd.read_excel(filepath)
        courses = []
        
        for _, row in df.iterrows():
            prerequisites = []
            if pd.notna(row.get('prerequisites')):
                prerequisites = [int(x.strip()) for x in str(row['prerequisites']).split(',') if x.strip()]
            
            course = Curso(
                id=int(row['id']),
                nombre=row['name'],
                codigo=row.get('code', ''),
                creditos=int(row.get('credits', 3)),
                matricula=int(row['enrollment']),
                prerequisitos=prerequisites
            )
            courses.append(course)
        return courses
    
    @staticmethod
    def load_professors_from_csv(filepath: str) -> List[Profesor]:
        """Load professors from CSV file"""
        professors = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timeslots = []
                if row.get('available_timeslots'):
                    timeslots = [int(x.strip()) for x in row['available_timeslots'].split(',') if x.strip()]
                
                professor = Profesor(
                    id=int(float(row['id'])),
                    nombre=row['name'],
                    email=row.get('email', ''),
                    bloques_disponibles=timeslots
                )
                professors.append(professor)
        return professors
    
    @staticmethod
    def load_professors_from_json(filepath: str) -> Dict[str, Any]:
        """
        Load professors from JSON file.
        Supports both list of professors and combined format (professors + timeslots).
        Returns a dictionary with 'professors' and optionally 'timeslots'.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        professors_data = []
        timeslots_data = []
        
        # Check if it's the combined format
        if isinstance(data, dict) and 'professors' in data:
            professors_data = data['professors']
            
            # Handle timeslots if present
            if 'time_slots' in data and 'days' in data:
                days_map = data['days']
                slots_map = data['time_slots']
                
                ts_id_counter = 1
                slot_string_to_id = {}
                
                for day_code, day_name in days_map.items():
                    for slot_idx, time_range in slots_map.items():
                        try:
                            start, end = time_range.split('-')
                            start_h, start_m = map(int, start.split(':'))
                            end_h, end_m = map(int, end.split(':'))
                            
                            key = f"{day_code}-{slot_idx}"
                            
                            timeslot = BloqueTiempo(
                                id=ts_id_counter,
                                dia=day_name,
                                hora_inicio=start_h,
                                minuto_inicio=start_m,
                                hora_fin=end_h,
                                minuto_fin=end_m
                            )
                            timeslots_data.append(timeslot)
                            slot_string_to_id[key] = ts_id_counter
                            ts_id_counter += 1
                        except ValueError:
                            continue

                for p_data in professors_data:
                    new_slots = []
                    for slot_str in p_data.get('available_timeslots', []):
                        if slot_str in slot_string_to_id:
                            new_slots.append(slot_string_to_id[slot_str])
                    p_data['available_timeslots'] = new_slots
                    
        elif isinstance(data, list):
            professors_data = data
            
        professors = []
        for item in professors_data:
            professor = Profesor(
                id=item['id'],
                nombre=item['name'],
                email=item.get('email', ''),
                bloques_disponibles=item.get('available_timeslots', []),
                materias_capaces=item.get('available_courses', [])
            )
            professors.append(professor)
            
        return {
            'professors': professors,
            'timeslots': timeslots_data if timeslots_data else None
        }
    
    @staticmethod
    def load_timeslots_from_csv(filepath: str) -> List[BloqueTiempo]:
        """Load timeslots from CSV file"""
        timeslots = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timeslot = BloqueTiempo(
                    id=int(row['id']),
                    dia=row['day'],
                    hora_inicio=int(row['start_hour']),
                    minuto_inicio=int(row['start_minute']),
                    hora_fin=int(row['end_hour']),
                    minuto_fin=int(row['end_minute'])
                )
                timeslots.append(timeslot)
        return timeslots
    
    @staticmethod
    def load_timeslots_from_json(filepath: str) -> List[BloqueTiempo]:
        """Load timeslots from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timeslots = []
        for item in data:
            timeslot = BloqueTiempo(
                id=item['id'],
                dia=item['day'],
                hora_inicio=item['start_hour'],
                minuto_inicio=item['start_minute'],
                hora_fin=item['end_hour'],
                minuto_fin=item['end_minute']
            )
            timeslots.append(timeslot)
        return timeslots
    
    @staticmethod
    def detect_format(filepath: str) -> str:
        """Detect file format from extension"""
        if filepath.endswith('.csv'):
            return 'csv'
        elif filepath.endswith('.json'):
            return 'json'
        elif filepath.endswith(('.xlsx', '.xls')):
            return 'excel'
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
    
    @staticmethod
    def load_data(filepath: str, data_type: str):
        """Generic data loader that detects format and loads appropriate data type"""
        format_type = DataLoader.detect_format(filepath)
        
        loaders = {
            ('courses', 'csv'): DataLoader.load_courses_from_csv,
            ('courses', 'json'): DataLoader.load_courses_from_json,
            ('courses', 'excel'): DataLoader.load_courses_from_excel,
            ('professors', 'csv'): DataLoader.load_professors_from_csv,
            ('professors', 'json'): DataLoader.load_professors_from_json,
            ('timeslots', 'csv'): DataLoader.load_timeslots_from_csv,
            ('timeslots', 'json'): DataLoader.load_timeslots_from_json,
        }
        
        loader_key = (data_type, format_type)
        if loader_key in loaders:
            return loaders[loader_key](filepath)
        else:
            raise ValueError(f"No loader for {data_type} in {format_type} format")
