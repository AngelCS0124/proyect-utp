"""
Course model - Represents a course in the curriculum
"""
from typing import List


class Course:
    def __init__(self, id: int, name: str, code: str, credits: int, enrollment: int, 
                 prerequisites: List[int], professor_id: int = None, cuatrimestre: int = None,
                 sessions_per_week: int = 1):
        self.id = id
        self.name = name
        self.code = code
        self.credits = credits
        self.enrollment = enrollment
        self.prerequisites = prerequisites
        self.professor_id = professor_id
        self.cuatrimestre = cuatrimestre  # Cuatrimestre number (1-10) for cycle-based filtering
        self.sessions_per_week = sessions_per_week  # Number of sessions needed per week (1-10)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'credits': self.credits,
            'enrollment': self.enrollment,
            'prerequisites': self.prerequisites,
            'professor_id': self.professor_id,
            'cuatrimestre': self.cuatrimestre,
            'sessions_per_week': self.sessions_per_week
        }
