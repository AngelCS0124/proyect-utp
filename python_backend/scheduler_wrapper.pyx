# distutils: language = c++
# cython: language_level = 3

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool

# C++ declarations
cdef extern from "scheduler_core.hpp" namespace "scheduler":
    cdef cppclass Assignment:
        int courseId
        int timeslotId
        int professorId
        
        Assignment() except +
        Assignment(int, int, int) except +
    
    cdef cppclass ScheduleResult:
        bool success
        vector[Assignment] assignments
        string errorMessage
        int backtrackCount
        double computationTime
        
        ScheduleResult() except +
    
    cdef cppclass SchedulerCore:
        SchedulerCore() except +
        
        void loadCourse(int id, const string& name, int enrollment,
                       const vector[int]& prerequisites) except +
        void loadProfessor(int id, const string& name,
                          const vector[int]& availableTimeslots) except +
        void loadTimeSlot(int id, const string& day, int startHour, int startMinute,
                         int endHour, int endMinute) except +
        
        void assignProfessorToCourse(int courseId, int professorId) except +
        
        ScheduleResult generateSchedule() except +
        void stopGeneration() except +
        void reset() except +
        
        bool hasData() const
        string validateData() const


# Python wrapper class
cdef class PyScheduler:
    cdef SchedulerCore* scheduler
    
    def __cinit__(self):
        self.scheduler = new SchedulerCore()
    
    def __dealloc__(self):
        if self.scheduler != NULL:
            del self.scheduler
    
    def load_course(self, int course_id, str name, int enrollment, list prerequisites=None):
        """Load a course into the scheduler"""
        cdef vector[int] prereq_vec
        if prerequisites:
            for p in prerequisites:
                prereq_vec.push_back(p)
        
        self.scheduler.loadCourse(course_id, name.encode('utf-8'), enrollment, prereq_vec)
    
    def load_professor(self, int prof_id, str name, list available_timeslots):
        """Load a professor with their available timeslots"""
        cdef vector[int] timeslot_vec
        for ts in available_timeslots:
            timeslot_vec.push_back(ts)
        
        self.scheduler.loadProfessor(prof_id, name.encode('utf-8'), timeslot_vec)
    
    def load_timeslot(self, int slot_id, str day, int start_hour, int start_minute,
                     int end_hour, int end_minute):
        """Load a timeslot"""
        self.scheduler.loadTimeSlot(slot_id, day.encode('utf-8'), 
                                    start_hour, start_minute, end_hour, end_minute)
    
    def assign_professor_to_course(self, int course_id, int professor_id):
        """Assign a professor to teach a course"""
        self.scheduler.assignProfessorToCourse(course_id, professor_id)
    
    def generate_schedule(self):
        """Generate the schedule using backtracking algorithm"""
        cdef ScheduleResult result = self.scheduler.generateSchedule()
        
        # Convert to Python dict
        py_result = {
            'success': result.success,
            'error_message': result.errorMessage.decode('utf-8'),
            'backtrack_count': result.backtrackCount,
            'computation_time': result.computationTime,
            'assignments': []
        }
        
        # Convert assignments
        for assignment in result.assignments:
            py_result['assignments'].append({
                'course_id': assignment.courseId,
                'timeslot_id': assignment.timeslotId,
                'professor_id': assignment.professorId
            })
        
        return py_result
    
    def stop_generation(self):
        """Stop the schedule generation process"""
        self.scheduler.stopGeneration()
    
    def reset(self):
        """Reset the scheduler (clear all data)"""
        self.scheduler.reset()
    
    def has_data(self):
        """Check if scheduler has any data loaded"""
        return self.scheduler.hasData()
    
    def validate_data(self):
        """Validate the loaded data"""
        return self.scheduler.validateData().decode('utf-8')
