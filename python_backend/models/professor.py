"""
Professor model - Represents a professor
"""


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
