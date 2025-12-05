#ifndef CONSTRAINTS_HPP
#define CONSTRAINTS_HPP

#include "graph.hpp"
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace scheduler {

// Time slot representation
struct TimeSlot {
  int id;
  std::string day; // Monday, Tuesday, etc.
  int startHour;   // 24-hour format
  int startMinute;
  int endHour;
  int endMinute;

  TimeSlot();
  TimeSlot(int id, const std::string &day, int startHour, int startMinute,
           int endHour, int endMinute);

  bool overlaps(const TimeSlot &other) const;
  std::string toString() const;
};

// Course assignment (course -> timeslot, professor)
struct Assignment {
  int courseId;
  int timeslotId;
  int professorId;

  Assignment(int courseId = -1, int timeslotId = -1, int professorId = -1);
};

// Constraint checker
class ConstraintChecker {
private:
  const Graph &graph;
  std::unordered_map<int, TimeSlot> timeslots;
  std::unordered_map<int, std::unordered_set<int>>
      professorAvailability; // professor -> timeslot IDs
  std::unordered_map<int, std::unordered_set<int>>
      coursePrerequisites; // course -> prerequisite course IDs

public:
  ConstraintChecker(const Graph &graph);

  // Data setup
  void addTimeSlot(const TimeSlot &slot);
  void addProfessorAvailability(int professorId, int timeslotId);
  void addCoursePrerequisite(int courseId, int prerequisiteId);

  // Constraint validation
  bool
  isValidAssignment(const Assignment &assignment,
                    const std::vector<Assignment> &existingAssignments) const;

  bool checkTimeConflict(int professorId, int timeslotId,
                         const std::vector<Assignment> &assignments) const;

  bool checkProfessorAvailability(int professorId, int timeslotId) const;

  bool checkPrerequisites(int courseId,
                          const std::vector<Assignment> &assignments) const;

  // Get available options for a course
  std::vector<int>
  getAvailableTimeslots(int courseId, int professorId,
                        const std::vector<Assignment> &assignments) const;

  // Validation messages
  std::string
  getViolationMessage(const Assignment &assignment,
                      const std::vector<Assignment> &assignments) const;
};

} // namespace scheduler

#endif // CONSTRAINTS_HPP
