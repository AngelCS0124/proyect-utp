"""
Data package initialization
"""
from .curriculum import (
    get_all_courses,
    get_courses_for_cycle,
    get_available_cycles,
    get_cuatrimestre_name,
    CURRICULUM,
    CYCLE_MAPPING,
    CYCLE_NAMES
)

__all__ = [
    'get_all_courses',
    'get_courses_for_cycle',
    'get_available_cycles',
    'get_cuatrimestre_name',
    'CURRICULUM',
    'CYCLE_MAPPING',
    'CYCLE_NAMES'
]
