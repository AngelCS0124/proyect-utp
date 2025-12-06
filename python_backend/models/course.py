"""
Course model - Represents a course in the curriculum
"""
from typing import List


class Course:
    def __init__(self, id: int, name: str, code: str, credits: int, enrollment: int, 
                 prerequisites: List[int], professor_id: int = None, semester: int = None,
                 group_id: int = 0):
        self.id = id
        self.name = name
        self.code = code
        self.credits = credits
        self.enrollment = enrollment
        self.prerequisites = prerequisites
        self.professor_id = professor_id
        self.semester = semester  # Semester number (1-10) for cycle-based filtering
        self.group_id = group_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'credits': self.credits,
            'enrollment': self.enrollment,
            'prerequisites': self.prerequisites,
            'professor_id': self.professor_id,
            'semester': self.semester,
            'group_id': self.group_id
        }
