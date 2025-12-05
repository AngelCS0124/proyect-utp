"""
Configuration package initialization
"""
from .time_blocks import (
    TIME_BLOCKS,
    VALID_DAYS,
    RECESS_PERIOD,
    SCHEDULE_CONSTRAINTS,
    get_all_timeslots_for_day,
    get_all_weekly_timeslots,
    is_valid_timeslot,
    is_during_recess,
    get_block_name,
    validate_timeslot_constraints
)

__all__ = [
    'TIME_BLOCKS',
    'VALID_DAYS',
    'RECESS_PERIOD',
    'SCHEDULE_CONSTRAINTS',
    'get_all_timeslots_for_day',
    'get_all_weekly_timeslots',
    'is_valid_timeslot',
    'is_during_recess',
    'get_block_name',
    'validate_timeslot_constraints'
]
