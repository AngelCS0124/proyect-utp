#ifndef SCHEDULER_CORE_HPP
#define SCHEDULER_CORE_HPP

#include "constraints.hpp"
#include "graph.hpp"
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace scheduler {

// Schedule result
struct ScheduleResult {
  bool success;
  std::vector<Assignment> assignments;
  std::string errorMessage;
  int backtrackCount;
  double computationTime;

  ScheduleResult();
};

// Progress callback for UI updates
using ProgressCallback =
    std::function<void(int current, int total, const std::string &message)>;

// Main scheduler engine
class SchedulerCore {
private:
  Graph graph;
  std::unique_ptr<ConstraintChecker> constraintChecker;
  ProgressCallback progressCallback;
  int backtrackCounter;
  bool shouldStop;

public:
  SchedulerCore();
  ~SchedulerCore();

  // Data loading
  void loadCourse(int id, const std::string &name, int enrollment,
                  const std::vector<int> &prerequisites);
  void loadProfessor(int id, const std::string &name,
                     const std::vector<int> &availableTimeslots);
  void loadTimeSlot(int id, const std::string &day, int startHour,
                    int startMinute, int endHour, int endMinute);

  // Course-Professor assignment
  void assignProfessorToCourse(int courseId, int professorId);

  // Schedule generation
  ScheduleResult generateSchedule();
  ScheduleResult generateScheduleWithCallback(ProgressCallback callback);

  // Control
  void stopGeneration();
  void reset();

  // Analysis
  std::string analyzeFailure() const;

  // Getters
  const Graph &getGraph() const;
  std::vector<Assignment> getCurrentAssignments() const;
  bool hasData() const;
  std::string validateData() const;

private:
  // Backtracking algorithm
  bool backtrack(std::vector<Assignment> &assignments,
                 const std::vector<int> &courses, size_t courseIndex);

  // Helper methods
  std::vector<int> getCourseOrder() const;
  bool tryAssignment(const Assignment &assignment,
                     std::vector<Assignment> &assignments);
  void updateProgress(int current, int total, const std::string &message);
};

} // namespace scheduler

#endif // SCHEDULER_CORE_HPP
