"""
Scheduling constraints and helpers for consecutive blocks
"""

from config import TIME_BLOCKS


def get_consecutive_blocks(block_id):
    """
    Get the next consecutive block ID
    Returns None if there's no consecutive block (e.g., before recess)
    
    Args:
        block_id: Current block number (1-8)
    
    Returns:
        Next block ID or None
    """
    # Block 4 (9:45-10:39) cannot have a consecutive block because of recess
    if block_id == 4:
        return None
    
    # Block 8 is the last block of the day
    if block_id == 8:
        return None
    
    # Otherwise, next block is consecutive
    return block_id + 1


def can_have_consecutive_blocks(block_id):
    """
    Check if a block can have a consecutive block after it
    
    Args:
        block_id: Block number (1-8)
    
    Returns:
        True if consecutive block is possible
    """
    return block_id not in [4, 8]


def get_double_block_timeslots(day, start_block_id):
    """
    Get timeslot IDs for a double block (2 consecutive blocks)
    
    Args:
        day: Day name (e.g., 'Lunes')
        start_block_id: Starting block (1-8)
    
    Returns:
        List of 2 timeslot IDs or empty list if not possible
    """
    if not can_have_consecutive_blocks(start_block_id):
        return []
    
    # Map day to base ID
    day_mapping = {
        'Lunes': 0, 'Monday': 0,
        'Martes': 100, 'Tuesday': 100,
        'Miércoles': 200, 'Wednesday': 200,
        'Jueves': 300, 'Thursday': 300,
        'Viernes': 400, 'Friday': 400,
    }
    
    base_id = day_mapping.get(day, 0)
    next_block = get_consecutive_blocks(start_block_id)
    
    if next_block is None:
        return []
    
    return [base_id + start_block_id, base_id + next_block]


def get_all_double_block_options(day):
    """
    Get all possible double block combinations for a day
    
    Args:
        day: Day name
    
    Returns:
        List of tuples (block1_id, block2_id, timeslot1_id, timeslot2_id)
    """
    day_mapping = {
        'Lunes': 0, 'Monday': 0,
        'Martes': 100, 'Tuesday': 100,
        'Miércoles': 200, 'Wednesday': 200,
        'Jueves': 300, 'Thursday': 300,
        'Viernes': 400, 'Friday': 400,
    }
    
    base_id = day_mapping.get(day, 0)
    options = []
    
    # Possible double blocks:
    # Blocks 1-2 (7:00-8:49)
    # Blocks 2-3 (7:55-9:44)
    # Blocks 3-4 (8:50-10:39)
    # --- RECESS ---
    # Blocks 5-6 (11:10-12:59)
    # Blocks 6-7 (12:05-13:54)
    # Blocks 7-8 (13:00-14:49)
    
    for block in [1, 2, 3, 5, 6, 7]:
        next_block = block + 1
        options.append({
            'start_block': block,
            'end_block': next_block,
            'timeslot_ids': [base_id + block, base_id + next_block],
            'start_time': TIME_BLOCKS[block],
            'end_time': TIME_BLOCKS[next_block]
        })
    
    return options


def calculate_sessions_needed(credits):
    """
    Calculate how many sessions per week a course needs based on credits
    
    Args:
        credits: Course credits (hours)
    
    Returns:
        Number of sessions per week (1-10)
    """
    # Each session is 54 minutes (0.9 hours)
    # credits / 0.9 = sessions needed
    # Divided by weeks in a cuatrimestre (approximately 16 weeks)
    
    # Simplified: 
    # 60 credits = 1 session/week
    # 75 credits = 1-2 sessions/week
    # 90 credits = 2 sessions/week
    # 105 credits = 2 sessions/week
    
    if credits <= 60:
        return 1
    elif credits <= 75:
        return 2
    elif credits <= 90:
        return 2
    else:
        return 2  # Maximum 2 sessions per week (can be double block)


def get_block_info(block_id):
    """
    Get information about a specific block
    
    Args:
        block_id: Block number (1-8)
    
    Returns:
        Dictionary with block information
    """
    if block_id not in TIME_BLOCKS:
        return None
    
    block = TIME_BLOCKS[block_id]
    return {
        'id': block_id,
        'name': block['name'],
        'start': f"{block['start_hour']:02d}:{block['start_minute']:02d}",
        'end': f"{block['end_hour']:02d}:{block['end_minute']:02d}",
        'can_be_double': can_have_consecutive_blocks(block_id)
    }
