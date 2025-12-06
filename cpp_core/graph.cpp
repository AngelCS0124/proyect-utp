#include "graph.hpp"
#include <algorithm>
#include <queue>
#include <stack>
#include <stdexcept>

namespace scheduler {

// Node implementation
Node::Node(int id, NodeType type, const std::string &name)
    : id(id), type(type), name(name) {}

void Node::setAttribute(const std::string &key, const std::string &value) {
  attributes[key] = value;
}

std::string Node::getAttribute(const std::string &key) const {
  auto it = attributes.find(key);
  return (it != attributes.end()) ? it->second : "";
}

bool Node::hasAttribute(const std::string &key) const {
  return attributes.find(key) != attributes.end();
}

// Graph implementation
Graph::Graph() : nextNodeId(0) {}

int Graph::addNode(NodeType type, const std::string &name) {
  int nodeId = nextNodeId++;
  nodes[nodeId] = std::make_shared<Node>(nodeId, type, name);
  adjacencyList[nodeId] = std::vector<int>();
  reverseAdjacencyList[nodeId] = std::unordered_set<int>();
  return nodeId;
}

std::shared_ptr<Node> Graph::getNode(int nodeId) const {
  auto it = nodes.find(nodeId);
  if (it != nodes.end()) {
    return it->second;
  }
  return nullptr;
}

void Graph::removeNode(int nodeId) {
  // Remove all edges involving this node
  if (adjacencyList.find(nodeId) != adjacencyList.end()) {
    for (int neighbor : adjacencyList[nodeId]) {
      reverseAdjacencyList[neighbor].erase(nodeId);
    }
  }

  if (reverseAdjacencyList.find(nodeId) != reverseAdjacencyList.end()) {
    for (int predecessor : reverseAdjacencyList[nodeId]) {
      auto &neighbors = adjacencyList[predecessor];
      neighbors.erase(std::remove(neighbors.begin(), neighbors.end(), nodeId),
                      neighbors.end());
    }
  }

  nodes.erase(nodeId);
  adjacencyList.erase(nodeId);
  reverseAdjacencyList.erase(nodeId);
}

void Graph::addEdge(int fromId, int toId) {
  if (nodes.find(fromId) == nodes.end() || nodes.find(toId) == nodes.end()) {
    throw std::invalid_argument("Node IDs must exist in graph");
  }

  adjacencyList[fromId].push_back(toId);
  reverseAdjacencyList[toId].insert(fromId);
}

void Graph::removeEdge(int fromId, int toId) {
  auto &neighbors = adjacencyList[fromId];
  neighbors.erase(std::remove(neighbors.begin(), neighbors.end(), toId),
                  neighbors.end());
  reverseAdjacencyList[toId].erase(fromId);
}

bool Graph::hasEdge(int fromId, int toId) const {
  auto it = adjacencyList.find(fromId);
  if (it != adjacencyList.end()) {
    const auto &neighbors = it->second;
    return std::find(neighbors.begin(), neighbors.end(), toId) !=
           neighbors.end();
  }
  return false;
}

std::vector<int> Graph::getNeighbors(int nodeId) const {
  auto it = adjacencyList.find(nodeId);
  return (it != adjacencyList.end()) ? it->second : std::vector<int>();
}

std::vector<int> Graph::getReverseNeighbors(int nodeId) const {
  auto it = reverseAdjacencyList.find(nodeId);
  if (it != reverseAdjacencyList.end()) {
    return std::vector<int>(it->second.begin(), it->second.end());
  }
  return std::vector<int>();
}

std::vector<int> Graph::getAllNodes() const {
  std::vector<int> result;
  result.reserve(nodes.size());
  for (const auto &pair : nodes) {
    result.push_back(pair.first);
  }
  return result;
}

std::vector<int> Graph::getNodesByType(NodeType type) const {
  std::vector<int> result;
  for (const auto &pair : nodes) {
    if (pair.second->type == type) {
      result.push_back(pair.first);
    }
  }
  return result;
}

bool Graph::hasCycle() const {
  std::unordered_set<int> visited;
  std::unordered_set<int> recursionStack;

  for (const auto &pair : nodes) {
    if (visited.find(pair.first) == visited.end()) {
      if (hasCycleDFS(pair.first, visited, recursionStack)) {
        return true;
      }
    }
  }
  return false;
}

bool Graph::hasCycleDFS(int nodeId, std::unordered_set<int> &visited,
                        std::unordered_set<int> &recursionStack) const {
  visited.insert(nodeId);
  recursionStack.insert(nodeId);

  for (int neighbor : getNeighbors(nodeId)) {
    if (visited.find(neighbor) == visited.end()) {
      if (hasCycleDFS(neighbor, visited, recursionStack)) {
        return true;
      }
    } else if (recursionStack.find(neighbor) != recursionStack.end()) {
      return true;
    }
  }

  recursionStack.erase(nodeId);
  return false;
}

std::vector<int> Graph::topologicalSort() const {
  if (hasCycle()) {
    throw std::runtime_error(
        "Cannot perform topological sort on graph with cycles");
  }

  std::unordered_set<int> visited;
  std::vector<int> stack;

  for (const auto &pair : nodes) {
    if (visited.find(pair.first) == visited.end()) {
      topologicalSortUtil(pair.first, visited, stack);
    }
  }

  std::reverse(stack.begin(), stack.end());
  return stack;
}

void Graph::topologicalSortUtil(int nodeId, std::unordered_set<int> &visited,
                                std::vector<int> &stack) const {
  visited.insert(nodeId);

  for (int neighbor : getNeighbors(nodeId)) {
    if (visited.find(neighbor) == visited.end()) {
      topologicalSortUtil(neighbor, visited, stack);
    }
  }

  stack.push_back(nodeId);
}

std::vector<int> Graph::bfs(int startId) const {
  std::vector<int> result;
  std::unordered_set<int> visited;
  std::queue<int> queue;

  queue.push(startId);
  visited.insert(startId);

  while (!queue.empty()) {
    int current = queue.front();
    queue.pop();
    result.push_back(current);

    for (int neighbor : getNeighbors(current)) {
      if (visited.find(neighbor) == visited.end()) {
        visited.insert(neighbor);
        queue.push(neighbor);
      }
    }
  }

  return result;
}

std::vector<int> Graph::dfs(int startId) const {
  std::vector<int> result;
  std::unordered_set<int> visited;
  std::stack<int> stack;

  stack.push(startId);

  while (!stack.empty()) {
    int current = stack.top();
    stack.pop();

    if (visited.find(current) == visited.end()) {
      visited.insert(current);
      result.push_back(current);

      for (int neighbor : getNeighbors(current)) {
        if (visited.find(neighbor) == visited.end()) {
          stack.push(neighbor);
        }
      }
    }
  }

  return result;
}

int Graph::size() const { return nodes.size(); }

void Graph::clear() {
  nodes.clear();
  adjacencyList.clear();
  reverseAdjacencyList.clear();
  nextNodeId = 0;
}

} // namespace scheduler
