#include "scheduler_core.hpp"
#include <algorithm>
#include <chrono>
#include <sstream>

namespace scheduler {

// ScheduleResult implementation
ScheduleResult::ScheduleResult()
    : success(false), backtrackCount(0), computationTime(0.0) {}

// SchedulerCore implementation
SchedulerCore::SchedulerCore()
    : constraintChecker(std::make_unique<ConstraintChecker>(graph)),
      backtrackCounter(0), shouldStop(false) {}

SchedulerCore::~SchedulerCore() = default;

void SchedulerCore::loadCourse(int id, const std::string& name, int enrollment,
                               const std::vector<int>& prerequisites) {
    int nodeId = graph.addNode(NodeType::COURSE, name);
    auto node = graph.getNode(nodeId);
    node->setAttribute("id", std::to_string(id));
    
    for (int prereqId : prerequisites) {
        constraintChecker->addCoursePrerequisite(nodeId, prereqId);
    }
}

void SchedulerCore::loadProfessor(int id, const std::string& name,
                                  const std::vector<int>& availableTimeslots) {
    int nodeId = graph.addNode(NodeType::PROFESSOR, name);
    auto node = graph.getNode(nodeId);
    node->setAttribute("id", std::to_string(id));
    
    for (int timeslotId : availableTimeslots) {
        constraintChecker->addProfessorAvailability(nodeId, timeslotId);
    }
}

void SchedulerCore::loadTimeSlot(int id, const std::string& day, int startHour, int startMinute,
                                 int endHour, int endMinute) {
    int nodeId = graph.addNode(NodeType::TIMESLOT, day);
    auto node = graph.getNode(nodeId);
    node->setAttribute("id", std::to_string(id));
    
    TimeSlot slot(nodeId, day, startHour, startMinute, endHour, endMinute);
    constraintChecker->addTimeSlot(slot);
}

void SchedulerCore::assignProfessorToCourse(int courseId, int professorId) {
    // Create edge from course to professor
    graph.addEdge(courseId, professorId);
}

ScheduleResult SchedulerCore::generateSchedule() {
    return generateScheduleWithCallback(nullptr);
}

ScheduleResult SchedulerCore::generateScheduleWithCallback(ProgressCallback callback) {
    ScheduleResult result;
    auto startTime = std::chrono::high_resolution_clock::now();
    
    progressCallback = callback;
    backtrackCounter = 0;
    shouldStop = false;
    
    // Validate data first
    std::string validationError = validateData();
    if (!validationError.empty()) {
        result.success = false;
        result.errorMessage = validationError;
        return result;
    }
    
    // Get course order (topological sort if prerequisites exist)
    std::vector<int> courseOrder = getCourseOrder();
    
    if (courseOrder.empty()) {
        result.success = false;
        result.errorMessage = "No courses to schedule";
        return result;
    }
    
    updateProgress(0, courseOrder.size(), "Starting schedule generation...");
    
    // Run backtracking algorithm
    std::vector<Assignment> assignments;
    result.success = backtrack(assignments, courseOrder, 0);
    
    if (shouldStop) {
        result.success = false;
        result.errorMessage = "Schedule generation stopped by user";
    } else if (result.success) {
        result.assignments = assignments;
        updateProgress(courseOrder.size(), courseOrder.size(), "Schedule generated successfully!");
    } else {
        result.errorMessage = "Could not find valid schedule with given constraints";
    }
    
    result.backtrackCount = backtrackCounter;
    
    auto endTime = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = endTime - startTime;
    result.computationTime = elapsed.count();
    
    return result;
}

bool SchedulerCore::backtrack(std::vector<Assignment>& assignments,
                              const std::vector<int>& courses,
                              size_t courseIndex) {
    // Check if we should stop
    if (shouldStop) {
        return false;
    }
    
    // Base case: all courses assigned
    if (courseIndex >= courses.size()) {
        return true;
    }
    
    int courseId = courses[courseIndex];
    auto courseNode = graph.getNode(courseId);
    
    updateProgress(courseIndex, courses.size(), 
                  "Scheduling: " + courseNode->name);
    
    // Get assigned professor for this course
    auto professorEdges = graph.getNeighbors(courseId);
    if (professorEdges.empty()) {
        // No professor assigned, skip or fail
        return backtrack(assignments, courses, courseIndex + 1);
    }
    
    int professorId = professorEdges[0]; // Assuming one professor per course
    
    // Try all available timeslots
    auto availableTimeslots = constraintChecker->getAvailableTimeslots(
        courseId, professorId, assignments);
    
    for (int timeslotId : availableTimeslots) {
        Assignment assignment(courseId, timeslotId, professorId);
        
        // Check if assignment is valid
        if (constraintChecker->isValidAssignment(assignment, assignments)) {
            // Make assignment
            assignments.push_back(assignment);
            
            // Recurse
            if (backtrack(assignments, courses, courseIndex + 1)) {
                return true;
            }
            
            // Backtrack
            assignments.pop_back();
            backtrackCounter++;
        }
    }
    
    // No valid assignment found
    return false;
}

std::vector<int> SchedulerCore::getCourseOrder() const {
    auto courses = graph.getNodesByType(NodeType::COURSE);
    
    // Try topological sort if there are prerequisites
    try {
        return graph.topologicalSort();
    } catch (...) {
        // If topological sort fails (cycles), just return courses in order
        return courses;
    }
}

void SchedulerCore::updateProgress(int current, int total, const std::string& message) {
    if (progressCallback) {
        progressCallback(current, total, message);
    }
}

void SchedulerCore::stopGeneration() {
    shouldStop = true;
}

void SchedulerCore::reset() {
    graph.clear();
    constraintChecker = std::make_unique<ConstraintChecker>(graph);
    backtrackCounter = 0;
    shouldStop = false;
}

const Graph& SchedulerCore::getGraph() const {
    return graph;
}

std::vector<Assignment> SchedulerCore::getCurrentAssignments() const {
    return std::vector<Assignment>();
}

bool SchedulerCore::hasData() const {
    return graph.size() > 0;
}

std::string SchedulerCore::validateData() const {
    std::ostringstream errors;
    
    auto courses = graph.getNodesByType(NodeType::COURSE);
    auto professors = graph.getNodesByType(NodeType::PROFESSOR);
    auto timeslots = graph.getNodesByType(NodeType::TIMESLOT);
    
    if (courses.empty()) {
        errors << "No hay cursos cargados. ";
    }
    
    if (professors.empty()) {
        errors << "No hay profesores cargados. ";
    }
    
    if (timeslots.empty()) {
        errors << "No hay horarios cargados. ";
    }
    
    // Check if all courses have professors assigned
    for (int courseId : courses) {
        auto professorEdges = graph.getNeighbors(courseId);
        if (professorEdges.empty()) {
            auto node = graph.getNode(courseId);
            errors << "Course '" << node->name << "' has no professor assigned. ";
        }
    }
    
    return errors.str();
}

} // namespace scheduler
