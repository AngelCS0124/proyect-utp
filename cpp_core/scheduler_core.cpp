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

void SchedulerCore::loadCourse(int id, const std::string &name, int enrollment,
                               const std::vector<int> &prerequisites,
                               int groupId, int duration) {
  int nodeId = graph.addNode(NodeType::COURSE, name);
  auto node = graph.getNode(nodeId);
  node->setAttribute("id", std::to_string(id));
  node->setAttribute("groupId", std::to_string(groupId));
  node->setAttribute("duration", std::to_string(duration));

  for (int prereqId : prerequisites) {
    constraintChecker->addCoursePrerequisite(nodeId, prereqId);
  }
  constraintChecker->addCourseGroup(id, groupId);
}

void SchedulerCore::loadProfessor(int id, const std::string &name,
                                  const std::vector<int> &availableTimeslots) {
  int nodeId = graph.addNode(NodeType::PROFESSOR, name);
  auto node = graph.getNode(nodeId);
  node->setAttribute("id", std::to_string(id));

  for (int timeslotId : availableTimeslots) {
    constraintChecker->addProfessorAvailability(nodeId, timeslotId);
  }
}

void SchedulerCore::loadTimeSlot(int id, const std::string &day, int startHour,
                                 int startMinute, int endHour, int endMinute) {
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

ScheduleResult
SchedulerCore::generateScheduleWithCallback(ProgressCallback callback) {
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
    updateProgress(courseOrder.size(), courseOrder.size(),
                   "Schedule generated successfully!");
  } else {
    result.errorMessage = "No se pudo encontrar un horario válido con las "
                          "restricciones dadas.\n\n" +
                          analyzeFailure();
  }

  result.backtrackCount = backtrackCounter;

  auto endTime = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> elapsed = endTime - startTime;
  result.computationTime = elapsed.count();

  return result;
}

bool SchedulerCore::backtrack(std::vector<Assignment> &assignments,
                              const std::vector<int> &courses,
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

  // Determine needed slots
  int duration = 1;
  if (courseNode->hasAttribute("duration")) {
    try {
      duration = std::stoi(courseNode->getAttribute("duration"));
    } catch (...) {
      duration = 1;
    }
  }
  // Assume 1 slot = 2 hours. If duration <= 2, 1 slot. If 3 or 4, 2 slots.
  int neededSlots = (duration + 1) / 2;
  if (neededSlots < 1)
    neededSlots = 1;

  // Try all available timeslots
  auto availableTimeslots = constraintChecker->getAvailableTimeslots(
      courseId, professorId, assignments);

  for (int startSlotId : availableTimeslots) {
    std::vector<int> sequence;
    sequence.push_back(startSlotId);

    int currentSlot = startSlotId;
    bool possible = true;

    // Find consecutive slots
    for (int i = 1; i < neededSlots; ++i) {
      int nextSlot = constraintChecker->getNextConsecutiveSlot(currentSlot);
      if (nextSlot == -1) {
        possible = false;
        break;
      }

      // Verify nextSlot is valid
      Assignment checkAssign(courseId, nextSlot, professorId);
      if (!constraintChecker->isValidAssignment(checkAssign, assignments)) {
        possible = false;
        break;
      }

      currentSlot = nextSlot;
      sequence.push_back(currentSlot);
    }

    if (possible) {
      // Try to assign ALL slots
      std::vector<Assignment> newAssignments;
      bool allValid = true;

      for (int slotId : sequence) {
        Assignment a(courseId, slotId, professorId);
        if (!constraintChecker->isValidAssignment(a, assignments)) {
          allValid = false;
          break;
        }
        newAssignments.push_back(a);
      }

      if (allValid) {
        // Commit
        for (const auto &a : newAssignments)
          assignments.push_back(a);

        if (backtrack(assignments, courses, courseIndex + 1))
          return true;

        // Backtrack
        for (size_t i = 0; i < newAssignments.size(); ++i)
          assignments.pop_back();
      }
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

void SchedulerCore::updateProgress(int current, int total,
                                   const std::string &message) {
  if (progressCallback) {
    progressCallback(current, total, message);
  }
}

void SchedulerCore::stopGeneration() { shouldStop = true; }

void SchedulerCore::reset() {
  graph.clear();
  constraintChecker = std::make_unique<ConstraintChecker>(graph);
  backtrackCounter = 0;
  shouldStop = false;
}

const Graph &SchedulerCore::getGraph() const { return graph; }

std::vector<Assignment> SchedulerCore::getCurrentAssignments() const {
  return std::vector<Assignment>();
}

bool SchedulerCore::hasData() const { return graph.size() > 0; }

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
  // for (int courseId : courses) {
  //     auto professorEdges = graph.getNeighbors(courseId);
  //     if (professorEdges.empty()) {
  //         auto node = graph.getNode(courseId);
  //         // errors << "Course '" << node->name << "' has no professor
  //         assigned. ";
  //     }
  // }

  return errors.str();
}

std::string SchedulerCore::analyzeFailure() const {
  std::ostringstream analysis;
  analysis << "Análisis de Fallo:\n\n";

  auto courses = graph.getNodesByType(NodeType::COURSE);
  auto professors = graph.getNodesByType(NodeType::PROFESSOR);

  // 1. Check Professor Capacity
  for (int professorId : professors) {
    auto profNode = graph.getNode(professorId);

    // Count courses assigned to this professor
    int assignedCourses = 0;
    int totalHoursNeeded = 0;

    // Find all courses pointing to this professor
    for (int courseId : courses) {
      auto neighbors = graph.getNeighbors(courseId);
      if (!neighbors.empty() && neighbors[0] == professorId) {
        assignedCourses++;
        // Assuming 1 course = 1 timeslot for now (simplification)
        // Ideally we should read credits from course node attributes
        totalHoursNeeded++;
      }
    }

    // Count available timeslots
    int availableSlots = 0;
    // In our graph model, professor availability is stored in ConstraintChecker
    // We need to access it. Since we can't easily access private members of
    // ConstraintChecker from here without changing its API, we'll try a
    // different approach or expose it. For now, let's assume we can check the
    // constraints directly if we expose a helper.

    // Alternative: Check the graph edges? No, availability is in
    // ConstraintChecker. Let's rely on a heuristic or modify ConstraintChecker.
    // For this quick fix, let's just say "Check availability for Professor X"

    if (assignedCourses > 0) {
      analysis << "- Profesor " << profNode->name << " tiene "
               << assignedCourses
               << " cursos asignados. Verifique que tenga al menos "
               << totalHoursNeeded << " horarios disponibles.\n";
    }
  }

  analysis << "\nSugerencia: Intente agregar más horarios disponibles a los "
              "profesores mencionados o asigne menos cursos.";

  return analysis.str();
}

} // namespace scheduler
