#ifndef GRAFO_HPP
#define GRAFO_HPP

#include <memory>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace planificador {

// Forward declarations
class Grafo;
class Nodo;

// Tipos de nodo en el grafo
enum class TipoNodo { CURSO, PROFESOR, AULA, BLOQUE_TIEMPO };

// Representa un nodo en el grafo
class Nodo {
public:
  int id;
  TipoNodo tipo;
  std::string nombre;
  std::unordered_map<std::string, std::string> atributos;

  Nodo(int id, TipoNodo tipo, const std::string &nombre);
  void setAtributo(const std::string &clave, const std::string &valor);
  std::string getAtributo(const std::string &clave) const;
  bool tieneAtributo(const std::string &clave) const;
};

// Estructura de grafo usando lista de adyacencia
class Grafo {
private:
  std::unordered_map<int, std::shared_ptr<Nodo>> nodos;
  std::unordered_map<int, std::vector<int>> listaAdyacencia;
  std::unordered_map<int, std::unordered_set<int>> listaAdyacenciaInversa;
  int siguienteIdNodo;

public:
  Grafo();

  // Gestión de Nodos
  int agregarNodo(TipoNodo tipo, const std::string &nombre);
  std::shared_ptr<Nodo> obtenerNodo(int idNodo) const;
  void eliminarNodo(int idNodo);

  // Gestión de Aristas (dirigidas para restricciones)
  void agregarArista(int desdeId, int hastaId);
  void eliminarArista(int desdeId, int hastaId);
  bool tieneArista(int desdeId, int hastaId) const;

  // Consultas al Grafo
  std::vector<int> obtenerVecinos(int idNodo) const;
  std::vector<int> obtenerVecinosInversos(int idNodo) const;
  std::vector<int> obtenerTodosNodos() const;
  std::vector<int> obtenerNodosPorTipo(TipoNodo tipo) const;

  // Algoritmos de Grafo
  bool tieneCiclo() const;
  std::vector<int> ordenamientoTopologico() const;
  std::vector<int> bfs(int idInicio) const;
  std::vector<int> dfs(int idInicio) const;

  // Utilidad
  int tamano() const;
  void limpiar();

private:
  bool tieneCicloDFS(int idNodo, std::unordered_set<int> &visitados,
                   std::unordered_set<int> &pilaRecursion) const;
  void ordenamientoTopologicoUtil(int idNodo, std::unordered_set<int> &visitados,
                           std::vector<int> &pila) const;
};

} // namespace planificador

#endif // GRAFO_HPP
