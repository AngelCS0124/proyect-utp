"""
TimeSlot model - Represents a time slot in the schedule
"""


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
