"""
Data loader supporting multiple formats (CSV, JSON, Excel)
"""

import csv
import json
import pandas as pd
from typing import List, Dict, Any
from models import Course, Professor, TimeSlot


class DataLoader:
    """Handles loading data from various file formats"""
    
    @staticmethod
    def load_courses_from_csv(filepath: str) -> List[Course]:
        """Load courses from CSV file"""
        courses = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prerequisites = []
                if row.get('prerequisites'):
                    prerequisites = [int(x.strip()) for x in row['prerequisites'].split(',') if x.strip()]
                
                course = Course(
                    id=int(row['id']),
                    name=row['name'],
                    code=row.get('code', ''),
                    credits=int(row.get('credits', 3)),
                    enrollment=int(row['enrollment']),
                    prerequisites=prerequisites,
                    professor_id=int(row['professor_id']) if row.get('professor_id') else None
                )
                courses.append(course)
        return courses
    
    @staticmethod
    def load_courses_from_json(filepath: str) -> List[Course]:
        """Load courses from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        courses = []
        for item in data:
            course = Course(
                id=item['id'],
                name=item['name'],
                code=item.get('code', ''),
                credits=item.get('credits', 3),
                enrollment=item['enrollment'],
                prerequisites=item.get('prerequisites', [])
            )
            courses.append(course)
        return courses
    
    @staticmethod
    def load_courses_from_excel(filepath: str) -> List[Course]:
        """Load courses from Excel file"""
        df = pd.read_excel(filepath)
        courses = []
        
        for _, row in df.iterrows():
            prerequisites = []
            if pd.notna(row.get('prerequisites')):
                prerequisites = [int(x.strip()) for x in str(row['prerequisites']).split(',') if x.strip()]
            
            course = Course(
                id=int(row['id']),
                name=row['name'],
                code=row.get('code', ''),
                credits=int(row.get('credits', 3)),
                enrollment=int(row['enrollment']),
                prerequisites=prerequisites
            )
            courses.append(course)
        return courses
    
    @staticmethod
    def load_professors_from_csv(filepath: str) -> List[Professor]:
        """Load professors from CSV file"""
        professors = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timeslots = []
                if row.get('available_timeslots'):
                    timeslots = [int(x.strip()) for x in row['available_timeslots'].split(',') if x.strip()]
                
                professor = Professor(
                    id=int(row['id']),
                    name=row['name'],
                    email=row.get('email', ''),
                    available_timeslots=timeslots
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
                # Convert the compact format to TimeSlot objects
                # "time_slots": {"1": "07:00-07:55", ...}
                # "days": {"Lu": "Lunes", ...}
                
                days_map = data['days']
                slots_map = data['time_slots']
                
                # Create a grid of timeslots
                ts_id_counter = 1
                # We need to map the "Lu-1" format to integer IDs for the professors
                # And create the corresponding TimeSlot objects
                
                # But wait, the Professor model expects available_timeslots to be integers (IDs of TimeSlots).
                # In prueba.json, they are strings like "Lu-1".
                # We need to generate TimeSlot objects and map the strings to their new integer IDs.
                
                slot_string_to_id = {}
                
                for day_code, day_name in days_map.items():
                    for slot_idx, time_range in slots_map.items():
                        # Parse time range "07:00-07:55"
                        try:
                            start, end = time_range.split('-')
                            start_h, start_m = map(int, start.split(':'))
                            end_h, end_m = map(int, end.split(':'))
                            
                            # Create TimeSlot
                            # We can use a deterministic ID or a counter
                            # Let's use a deterministic ID based on day index and slot index to be safe?
                            # Or just a counter.
                            
                            # Construct the key used in available_slots, e.g. "Lu-1"
                            key = f"{day_code}-{slot_idx}"
                            
                            timeslot = TimeSlot(
                                id=ts_id_counter,
                                day=day_name,
                                start_hour=start_h,
                                start_minute=start_m,
                                end_hour=end_h,
                                end_minute=end_m
                            )
                            timeslots_data.append(timeslot)
                            slot_string_to_id[key] = ts_id_counter
                            ts_id_counter += 1
                        except ValueError:
                            continue

                # Now update professors' available_slots from strings to integers
                for p_data in professors_data:
                    if 'available_slots' in p_data: # Note: prueba.json uses available_slots, model uses available_timeslots
                        # Map strings to IDs
                        int_slots = []
                        for slot_str in p_data['available_slots']:
                            if slot_str in slot_string_to_id:
                                int_slots.append(slot_string_to_id[slot_str])
                        p_data['available_timeslots'] = int_slots
                    elif 'available_timeslots' in p_data:
                        # Already in some format, leave it if it's list of ints
                        pass

        elif isinstance(data, list):
            professors_data = data
        
        professors = []
        for item in professors_data:
            professor = Professor(
                id=item['id'],
                name=item['name'],
                email=item.get('email', ''),
                available_timeslots=item.get('available_timeslots', [])
            )
            professors.append(professor)
            
        return {
            'professors': professors,
            'timeslots': timeslots_data if timeslots_data else None
        }
    
    @staticmethod
    def load_timeslots_from_csv(filepath: str) -> List[TimeSlot]:
        """Load timeslots from CSV file"""
        timeslots = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timeslot = TimeSlot(
                    id=int(row['id']),
                    day=row['day'],
                    start_hour=int(row['start_hour']),
                    start_minute=int(row['start_minute']),
                    end_hour=int(row['end_hour']),
                    end_minute=int(row['end_minute'])
                )
                timeslots.append(timeslot)
        return timeslots
    
    @staticmethod
    def load_timeslots_from_json(filepath: str) -> List[TimeSlot]:
        """Load timeslots from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timeslots = []
        for item in data:
            timeslot = TimeSlot(
                id=item['id'],
                day=item['day'],
                start_hour=item['start_hour'],
                start_minute=item['start_minute'],
                end_hour=item['end_hour'],
                end_minute=item['end_minute']
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
