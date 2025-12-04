#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <memory>

namespace scheduler {

// Forward declarations
class Graph;
class Node;

// Node types for the scheduling graph
enum class NodeType {
    COURSE,
    PROFESSOR,
    CLASSROOM,
    TIMESLOT
};

// Represents a node in the graph
class Node {
public:
    int id;
    NodeType type;
    std::string name;
    std::unordered_map<std::string, std::string> attributes;
    
    Node(int id, NodeType type, const std::string& name);
    void setAttribute(const std::string& key, const std::string& value);
    std::string getAttribute(const std::string& key) const;
};

// Graph structure using adjacency list
class Graph {
private:
    std::unordered_map<int, std::shared_ptr<Node>> nodes;
    std::unordered_map<int, std::vector<int>> adjacencyList;
    std::unordered_map<int, std::unordered_set<int>> reverseAdjacencyList;
    int nextNodeId;

public:
    Graph();
    
    // Node management
    int addNode(NodeType type, const std::string& name);
    std::shared_ptr<Node> getNode(int nodeId) const;
    void removeNode(int nodeId);
    
    // Edge management (directed edges for constraints)
    void addEdge(int fromId, int toId);
    void removeEdge(int fromId, int toId);
    bool hasEdge(int fromId, int toId) const;
    
    // Graph queries
    std::vector<int> getNeighbors(int nodeId) const;
    std::vector<int> getReverseNeighbors(int nodeId) const;
    std::vector<int> getAllNodes() const;
    std::vector<int> getNodesByType(NodeType type) const;
    
    // Graph algorithms
    bool hasCycle() const;
    std::vector<int> topologicalSort() const;
    std::vector<int> bfs(int startId) const;
    std::vector<int> dfs(int startId) const;
    
    // Utility
    int size() const;
    void clear();

private:
    bool hasCycleDFS(int nodeId, std::unordered_set<int>& visited, 
                     std::unordered_set<int>& recursionStack) const;
    void topologicalSortUtil(int nodeId, std::unordered_set<int>& visited,
                            std::vector<int>& stack) const;
};

} // namespace scheduler

#endif // GRAPH_HPP
