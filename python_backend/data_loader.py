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
                    prerequisites=prerequisites
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
    def load_professors_from_json(filepath: str) -> List[Professor]:
        """Load professors from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        professors = []
        for item in data:
            professor = Professor(
                id=item['id'],
                name=item['name'],
                email=item.get('email', ''),
                available_timeslots=item.get('available_timeslots', [])
            )
            professors.append(professor)
        return professors
    
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
