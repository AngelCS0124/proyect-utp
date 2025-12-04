#include "constraints.hpp"
#include <sstream>
#include <iomanip>
#include <algorithm>

namespace scheduler {

// TimeSlot implementation
TimeSlot::TimeSlot(int id, const std::string& day, int startHour, int startMinute,
                   int endHour, int endMinute)
    : id(id), day(day), startHour(startHour), startMinute(startMinute),
      endHour(endHour), endMinute(endMinute) {}

bool TimeSlot::overlaps(const TimeSlot& other) const {
    if (day != other.day) {
        return false;
    }
    
    int thisStart = startHour * 60 + startMinute;
    int thisEnd = endHour * 60 + endMinute;
    int otherStart = other.startHour * 60 + other.startMinute;
    int otherEnd = other.endHour * 60 + other.endMinute;
    
    return !(thisEnd <= otherStart || otherEnd <= thisStart);
}

std::string TimeSlot::toString() const {
    std::ostringstream oss;
    oss << day << " " 
        << std::setfill('0') << std::setw(2) << startHour << ":"
        << std::setfill('0') << std::setw(2) << startMinute << "-"
        << std::setfill('0') << std::setw(2) << endHour << ":"
        << std::setfill('0') << std::setw(2) << endMinute;
    return oss.str();
}

// Assignment implementation
Assignment::Assignment(int courseId, int timeslotId, int professorId)
    : courseId(courseId), timeslotId(timeslotId), professorId(professorId) {}

// ConstraintChecker implementation
ConstraintChecker::ConstraintChecker(const Graph& graph) : graph(graph) {}

void ConstraintChecker::addTimeSlot(const TimeSlot& slot) {
    timeslots[slot.id] = slot;
}

void ConstraintChecker::addProfessorAvailability(int professorId, int timeslotId) {
    professorAvailability[professorId].insert(timeslotId);
}

void ConstraintChecker::addCoursePrerequisite(int courseId, int prerequisiteId) {
    coursePrerequisites[courseId].insert(prerequisiteId);
}

bool ConstraintChecker::isValidAssignment(const Assignment& assignment,
                                         const std::vector<Assignment>& existingAssignments) const {
    // Check professor availability
    if (!checkProfessorAvailability(assignment.professorId, assignment.timeslotId)) {
        return false;
    }
    
    // Check time conflicts
    if (checkTimeConflict(assignment.professorId, assignment.timeslotId, existingAssignments)) {
        return false;
    }
    
    return true;
}

bool ConstraintChecker::checkTimeConflict(int professorId, int timeslotId,
                                         const std::vector<Assignment>& assignments) const {
    auto it = timeslots.find(timeslotId);
    if (it == timeslots.end()) {
        return true; // Invalid timeslot
    }
    
    const TimeSlot& newSlot = it->second;
    
    for (const auto& assignment : assignments) {
        if (assignment.professorId == professorId) {
            auto existingIt = timeslots.find(assignment.timeslotId);
            if (existingIt != timeslots.end()) {
                if (newSlot.overlaps(existingIt->second)) {
                    return true; // Conflict found
                }
            }
        }
    }
    
    return false;
}

bool ConstraintChecker::checkProfessorAvailability(int professorId, int timeslotId) const {
    auto it = professorAvailability.find(professorId);
    if (it == professorAvailability.end()) {
        return false; // No availability data
    }
    
    return it->second.find(timeslotId) != it->second.end();
}

bool ConstraintChecker::checkPrerequisites(int courseId, 
                                          const std::vector<Assignment>& assignments) const {
    auto it = coursePrerequisites.find(courseId);
    if (it == coursePrerequisites.end()) {
        return true; // No prerequisites
    }
    
    // For now, just check if prerequisites exist in assignments
    // In a real system, you'd check semester ordering
    std::unordered_set<int> assignedCourses;
    for (const auto& assignment : assignments) {
        assignedCourses.insert(assignment.courseId);
    }
    
    for (int prereqId : it->second) {
        if (assignedCourses.find(prereqId) == assignedCourses.end()) {
            return false;
        }
    }
    
    return true;
}

std::vector<int> ConstraintChecker::getAvailableTimeslots(
    int courseId, int professorId, const std::vector<Assignment>& assignments) const {
    
    std::vector<int> available;
    
    auto availIt = professorAvailability.find(professorId);
    if (availIt == professorAvailability.end()) {
        return available;
    }
    
    for (int timeslotId : availIt->second) {
        if (!checkTimeConflict(professorId, timeslotId, assignments)) {
            available.push_back(timeslotId);
        }
    }
    
    return available;
}

std::string ConstraintChecker::getViolationMessage(
    const Assignment& assignment, const std::vector<Assignment>& assignments) const {
    
    std::ostringstream oss;
    
    if (!checkProfessorAvailability(assignment.professorId, assignment.timeslotId)) {
        oss << "Profesor no disponible en este horario. ";
    }
    
    if (checkTimeConflict(assignment.professorId, assignment.timeslotId, assignments)) {
        oss << "Conflicto de horario del profesor. ";
    }
    
    return oss.str();
}

} // namespace scheduler
