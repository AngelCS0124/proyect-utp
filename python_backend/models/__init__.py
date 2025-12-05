"""
Package initialization for models
"""
from .course import Course
from .professor import Professor
from .timeslot import TimeSlot
from .schedule import Schedule

__all__ = ['Course', 'Professor', 'TimeSlot', 'Schedule']
