"""
Services package initialization
"""
from .scheduling_helpers import (
    get_consecutive_blocks,
    can_have_consecutive_blocks,
    get_double_block_timeslots,
    get_all_double_block_options,
    calculate_sessions_needed,
    get_block_info
)

__all__ = [
    'get_consecutive_blocks',
    'can_have_consecutive_blocks',
    'get_double_block_timeslots',
    'get_all_double_block_options',
    'calculate_sessions_needed',
    'get_block_info'
]
