#include "grafo.hpp"
#include <algorithm>
#include <queue>
#include <stack>
#include <stdexcept>

namespace planificador {

// Implementación de Nodo
Nodo::Nodo(int id, TipoNodo tipo, const std::string &nombre)
    : id(id), tipo(tipo), nombre(nombre) {}

void Nodo::setAtributo(const std::string &clave, const std::string &valor) {
  atributos[clave] = valor;
}

std::string Nodo::getAtributo(const std::string &clave) const {
  auto it = atributos.find(clave);
  return (it != atributos.end()) ? it->second : "";
}

bool Nodo::tieneAtributo(const std::string &clave) const {
  return atributos.find(clave) != atributos.end();
}

// Implementación de Grafo
Grafo::Grafo() : siguienteIdNodo(0) {}

int Grafo::agregarNodo(TipoNodo tipo, const std::string &nombre) {
  int idNodo = siguienteIdNodo++;
  nodos[idNodo] = std::make_shared<Nodo>(idNodo, tipo, nombre);
  listaAdyacencia[idNodo] = std::vector<int>();
  listaAdyacenciaInversa[idNodo] = std::unordered_set<int>();
  return idNodo;
}

std::shared_ptr<Nodo> Grafo::obtenerNodo(int idNodo) const {
  auto it = nodos.find(idNodo);
  if (it != nodos.end()) {
    return it->second;
  }
  return nullptr;
}

void Grafo::eliminarNodo(int idNodo) {
  // Eliminar todas las aristas que involucran a este nodo
  if (listaAdyacencia.find(idNodo) != listaAdyacencia.end()) {
    for (int vecino : listaAdyacencia[idNodo]) {
      listaAdyacenciaInversa[vecino].erase(idNodo);
    }
  }

  if (listaAdyacenciaInversa.find(idNodo) != listaAdyacenciaInversa.end()) {
    for (int predecesor : listaAdyacenciaInversa[idNodo]) {
      auto &vecinos = listaAdyacencia[predecesor];
      vecinos.erase(std::remove(vecinos.begin(), vecinos.end(), idNodo),
                      vecinos.end());
    }
  }

  nodos.erase(idNodo);
  listaAdyacencia.erase(idNodo);
  listaAdyacenciaInversa.erase(idNodo);
}

void Grafo::agregarArista(int desdeId, int hastaId) {
  if (nodos.find(desdeId) == nodos.end() || nodos.find(hastaId) == nodos.end()) {
    throw std::invalid_argument("IDs de nodo deben existir en el grafo");
  }

  listaAdyacencia[desdeId].push_back(hastaId);
  listaAdyacenciaInversa[hastaId].insert(desdeId);
}

void Grafo::eliminarArista(int desdeId, int hastaId) {
  auto &vecinos = listaAdyacencia[desdeId];
  vecinos.erase(std::remove(vecinos.begin(), vecinos.end(), hastaId),
                  vecinos.end());
  listaAdyacenciaInversa[hastaId].erase(desdeId);
}

bool Grafo::tieneArista(int desdeId, int hastaId) const {
  auto it = listaAdyacencia.find(desdeId);
  if (it != listaAdyacencia.end()) {
    const auto &vecinos = it->second;
    return std::find(vecinos.begin(), vecinos.end(), hastaId) !=
           vecinos.end();
  }
  return false;
}

std::vector<int> Grafo::obtenerVecinos(int idNodo) const {
  auto it = listaAdyacencia.find(idNodo);
  return (it != listaAdyacencia.end()) ? it->second : std::vector<int>();
}

std::vector<int> Grafo::obtenerVecinosInversos(int idNodo) const {
  auto it = listaAdyacenciaInversa.find(idNodo);
  if (it != listaAdyacenciaInversa.end()) {
    return std::vector<int>(it->second.begin(), it->second.end());
  }
  return std::vector<int>();
}

std::vector<int> Grafo::obtenerTodosNodos() const {
  std::vector<int> resultado;
  resultado.reserve(nodos.size());
  for (const auto &par : nodos) {
    resultado.push_back(par.first);
  }
  return resultado;
}

std::vector<int> Grafo::obtenerNodosPorTipo(TipoNodo tipo) const {
  std::vector<int> resultado;
  for (const auto &par : nodos) {
    if (par.second->tipo == tipo) {
      resultado.push_back(par.first);
    }
  }
  return resultado;
}

bool Grafo::tieneCiclo() const {
  std::unordered_set<int> visitados;
  std::unordered_set<int> pilaRecursion;

  for (const auto &par : nodos) {
    if (visitados.find(par.first) == visitados.end()) {
      if (tieneCicloDFS(par.first, visitados, pilaRecursion)) {
        return true;
      }
    }
  }
  return false;
}

bool Grafo::tieneCicloDFS(int idNodo, std::unordered_set<int> &visitados,
                        std::unordered_set<int> &pilaRecursion) const {
  visitados.insert(idNodo);
  pilaRecursion.insert(idNodo);

  for (int vecino : obtenerVecinos(idNodo)) {
    if (visitados.find(vecino) == visitados.end()) {
      if (tieneCicloDFS(vecino, visitados, pilaRecursion)) {
        return true;
      }
    } else if (pilaRecursion.find(vecino) != pilaRecursion.end()) {
      return true;
    }
  }

  pilaRecursion.erase(idNodo);
  return false;
}

std::vector<int> Grafo::ordenamientoTopologico() const {
  if (tieneCiclo()) {
    throw std::runtime_error(
        "No se puede realizar ordenamiento topologico en grafo con ciclos");
  }

  std::unordered_set<int> visitados;
  std::vector<int> pila;

  for (const auto &par : nodos) {
    if (visitados.find(par.first) == visitados.end()) {
      ordenamientoTopologicoUtil(par.first, visitados, pila);
    }
  }

  std::reverse(pila.begin(), pila.end());
  return pila;
}

void Grafo::ordenamientoTopologicoUtil(int idNodo, std::unordered_set<int> &visitados,
                                std::vector<int> &pila) const {
  visitados.insert(idNodo);

  for (int vecino : obtenerVecinos(idNodo)) {
    if (visitados.find(vecino) == visitados.end()) {
      ordenamientoTopologicoUtil(vecino, visitados, pila);
    }
  }

  pila.push_back(idNodo);
}

std::vector<int> Grafo::bfs(int idInicio) const {
  std::vector<int> resultado;
  std::unordered_set<int> visitados;
  std::queue<int> cola;

  cola.push(idInicio);
  visitados.insert(idInicio);

  while (!cola.empty()) {
    int actual = cola.front();
    cola.pop();
    resultado.push_back(actual);

    for (int vecino : obtenerVecinos(actual)) {
      if (visitados.find(vecino) == visitados.end()) {
        visitados.insert(vecino);
        cola.push(vecino);
      }
    }
  }

  return resultado;
}

std::vector<int> Grafo::dfs(int idInicio) const {
  std::vector<int> resultado;
  std::unordered_set<int> visitados;
  std::stack<int> pila;

  pila.push(idInicio);

  while (!pila.empty()) {
    int actual = pila.top();
    pila.pop();

    if (visitados.find(actual) == visitados.end()) {
      visitados.insert(actual);
      resultado.push_back(actual);

      for (int vecino : obtenerVecinos(actual)) {
        if (visitados.find(vecino) == visitados.end()) {
          pila.push(vecino);
        }
      }
    }
  }

  return resultado;
}

int Grafo::tamano() const { return nodos.size(); }

void Grafo::limpiar() {
  nodos.clear();
  listaAdyacencia.clear();
  listaAdyacenciaInversa.clear();
  siguienteIdNodo = 0;
}

} // namespace planificador
