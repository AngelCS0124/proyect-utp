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
        errors = []
        warnings = []
        
        if not timeslots:
            errors.append("No timeslots provided")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for duplicate IDs
        ids = [t.id for t in timeslots]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate timeslot IDs found")
        
        # Check for valid times
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for timeslot in timeslots:
            if timeslot.day not in valid_days:
                errors.append(f"Invalid day: {timeslot.day}")
            
            if not (0 <= timeslot.start_hour < 24 and 0 <= timeslot.end_hour < 24):
                errors.append(f"Invalid hours for timeslot {timeslot.id}")
            
            if not (0 <= timeslot.start_minute < 60 and 0 <= timeslot.end_minute < 60):
                errors.append(f"Invalid minutes for timeslot {timeslot.id}")
            
            start_time = timeslot.start_hour * 60 + timeslot.start_minute
            end_time = timeslot.end_hour * 60 + timeslot.end_minute
            if start_time >= end_time:
                errors.append(f"Timeslot {timeslot.id} has invalid time range")
        
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
                errors.append(f"Course '{course.name}' has no professor assigned")
            elif course.professor_id not in professor_ids:
                errors.append(f"Course '{course.name}' assigned to non-existent professor ID: {course.professor_id}")
        
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
