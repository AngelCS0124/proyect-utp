"""
Schedule model - Represents a generated schedule
"""


class Schedule:
    def __init__(self, assignments, metadata=None):
        self.assignments = assignments
        self.metadata = metadata or {}
    
    def to_dict(self):
        return {
            'assignments': self.assignments,
            'metadata': self.metadata
        }
