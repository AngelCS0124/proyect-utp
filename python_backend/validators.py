"""
Input validation for the scheduling system
"""

from typing import List, Dict, Any
from models import Course, Professor, TimeSlot


class Validator:
    """Validates input data and system state"""
    
    @staticmethod
    def validate_courses(courses: List[Course]) -> Dict[str, Any]:
        """Validate course data"""
        errors = []
        warnings = []
        
        if not courses:
            errors.append("No courses provided")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for duplicate IDs
        ids = [c.id for c in courses]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate course IDs found")
        
        # Check for valid enrollment numbers
        for course in courses:
            if course.enrollment <= 0:
                errors.append(f"Course '{course.name}' has invalid enrollment: {course.enrollment}")
            
            # Check prerequisites exist
            for prereq_id in course.prerequisites:
                if prereq_id not in ids:
                    warnings.append(f"Course '{course.name}' has non-existent prerequisite ID: {prereq_id}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_professors(professors: List[Professor]) -> Dict[str, Any]:
        """Validate professor data"""
        errors = []
        warnings = []
        
        if not professors:
            errors.append("No professors provided")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for duplicate IDs
        ids = [p.id for p in professors]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate professor IDs found")
        
        # Check for availability
        for professor in professors:
            if not professor.available_timeslots:
                warnings.append(f"Professor '{professor.name}' has no available timeslots")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_timeslots(timeslots: List[TimeSlot]) -> Dict[str, Any]:
        """Validate timeslot data"""
        from config import VALID_DAYS, validate_timeslot_constraints
        
        errors = []
        warnings = []
        
        if not timeslots:
            errors.append("No timeslots provided")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for duplicate IDs
        ids = [t.id for t in timeslots]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate timeslot IDs found")
        
        # Get all valid days (Spanish and English)
        valid_days = VALID_DAYS['es'] + VALID_DAYS['en']
        
        # Check each timeslot
        for timeslot in timeslots:
            # Validate day (weekdays only)
            if timeslot.day not in valid_days:
                errors.append(f"Día inválido: {timeslot.day}. Solo se permiten días entre semana (Lunes-Viernes)")
            
            # Validate hours
            if not (0 <= timeslot.start_hour < 24 and 0 <= timeslot.end_hour < 24):
                errors.append(f"Invalid hours for timeslot {timeslot.id}")
            
            # Validate minutes
            if not (0 <= timeslot.start_minute < 60 and 0 <= timeslot.end_minute < 60):
                errors.append(f"Invalid minutes for timeslot {timeslot.id}")
            
            # Validate time range
            start_time = timeslot.start_hour * 60 + timeslot.start_minute
            end_time = timeslot.end_hour * 60 + timeslot.end_minute
            if start_time >= end_time:
                errors.append(f"Timeslot {timeslot.id} has invalid time range")
            
            # Validate against UTP time block constraints
            is_valid, error_msg = validate_timeslot_constraints(
                timeslot.start_hour,
                timeslot.start_minute,
                timeslot.end_hour,
                timeslot.end_minute
            )
            
            if not is_valid:
                errors.append(f"Timeslot {timeslot.id}: {error_msg}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_course_assignments(courses: List[Course], professors: List[Professor]) -> Dict[str, Any]:
        """Validate that all courses have professors assigned"""
        errors = []
        warnings = []
        
        professor_ids = {p.id for p in professors}
        
        for course in courses:
            if course.professor_id is None:
                print(f"DEBUG: Warning - Course {course.name} has no professor")
                warnings.append(f"Course '{course.name}' has no professor assigned")
            elif course.professor_id not in professor_ids:
                print(f"DEBUG: Error - Course {course.name} has invalid professor {course.professor_id}")
                errors.append(f"Course '{course.name}' assigned to non-existent professor ID: {course.professor_id}")
        
        print(f"DEBUG: Validation result - Errors: {len(errors)}, Warnings: {len(warnings)}")
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_all_data(courses: List[Course], professors: List[Professor],
                         timeslots: List[TimeSlot]) -> Dict[str, Any]:
        """Validate all data together"""
        all_errors = []
        all_warnings = []
        
        # Validate each data type
        course_validation = Validator.validate_courses(courses)
        all_errors.extend(course_validation['errors'])
        all_warnings.extend(course_validation['warnings'])
        
        prof_validation = Validator.validate_professors(professors)
        all_errors.extend(prof_validation['errors'])
        all_warnings.extend(prof_validation['warnings'])
        
        timeslot_validation = Validator.validate_timeslots(timeslots)
        all_errors.extend(timeslot_validation['errors'])
        all_warnings.extend(timeslot_validation['warnings'])
        
        # Validate assignments
        assignment_validation = Validator.validate_course_assignments(courses, professors)
        all_errors.extend(assignment_validation['errors'])
        all_warnings.extend(assignment_validation['warnings'])
        
        return {
            'valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': all_warnings
        }
