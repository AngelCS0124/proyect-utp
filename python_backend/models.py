"""
Data models for the UTP Scheduling System
"""

from typing import List

class Course:
    def __init__(self, id: int, name: str, code: str, credits: int, enrollment: int, prerequisites: List[int], professor_id: int = None, semester: int = None):
        self.id = id
        self.name = name
        self.code = code
        self.credits = credits
        self.enrollment = enrollment
        self.prerequisites = prerequisites
        self.professor_id = professor_id
        self.semester = semester  # Semester number (1-10) for cycle-based filtering
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'credits': self.credits,
            'enrollment': self.enrollment,
            'prerequisites': self.prerequisites,
            'professor_id': self.professor_id,
            'semester': self.semester
        }


class Professor:
    def __init__(self, id, name, email, available_timeslots=None):
        self.id = id
        self.name = name
        self.email = email
        self.available_timeslots = available_timeslots or []
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'available_timeslots': self.available_timeslots
        }


class TimeSlot:
    def __init__(self, id, day, start_hour, start_minute, end_hour, end_minute):
        self.id = id
        self.day = day
        self.start_hour = start_hour
        self.start_minute = start_minute
        self.end_hour = end_hour
        self.end_minute = end_minute
    
    def to_dict(self):
        return {
            'id': self.id,
            'day': self.day,
            'start_hour': self.start_hour,
            'start_minute': self.start_minute,
            'end_hour': self.end_hour,
            'end_minute': self.end_minute,
            'display': f"{self.day} {self.start_hour:02d}:{self.start_minute:02d}-{self.end_hour:02d}:{self.end_minute:02d}"
        }


class Schedule:
    def __init__(self, assignments, metadata=None):
        self.assignments = assignments
        self.metadata = metadata or {}
    
    def to_dict(self):
        return {
            'assignments': self.assignments,
            'metadata': self.metadata
        }
