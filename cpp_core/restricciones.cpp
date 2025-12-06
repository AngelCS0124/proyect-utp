#include "restricciones.hpp"
#include <algorithm>
#include <iomanip>
#include <sstream>

namespace planificador {

// Implementación de BloqueTiempo
BloqueTiempo::BloqueTiempo()
    : id(-1), dia(""), horaInicio(0), minutoInicio(0), horaFin(0), minutoFin(0) {}

BloqueTiempo::BloqueTiempo(int id, const std::string &dia, int horaInicio,
                   int minutoInicio, int horaFin, int minutoFin)
    : id(id), dia(dia), horaInicio(horaInicio), minutoInicio(minutoInicio),
      horaFin(horaFin), minutoFin(minutoFin) {}

bool BloqueTiempo::seSolapa(const BloqueTiempo &otro) const {
  if (dia != otro.dia) {
    return false;
  }

  int esteInicio = horaInicio * 60 + minutoInicio;
  int esteFin = horaFin * 60 + minutoFin;
  int otroInicio = otro.horaInicio * 60 + otro.minutoInicio;
  int otroFin = otro.horaFin * 60 + otro.minutoFin;

  return !(esteFin <= otroInicio || otroFin <= esteInicio);
}

std::string BloqueTiempo::aString() const {
  std::ostringstream oss;
  oss << dia << " " << std::setfill('0') << std::setw(2) << horaInicio << ":"
      << std::setfill('0') << std::setw(2) << minutoInicio << "-"
      << std::setfill('0') << std::setw(2) << horaFin << ":"
      << std::setfill('0') << std::setw(2) << minutoFin;
  return oss.str();
}

// Implementación de Asignacion
Asignacion::Asignacion(int idCurso, int idBloque, int idProfesor)
    : idCurso(idCurso), idBloque(idBloque), idProfesor(idProfesor) {}

// Implementación de VerificadorRestricciones
VerificadorRestricciones::VerificadorRestricciones(const Grafo &grafo) : grafo(grafo) {}

void VerificadorRestricciones::agregarBloqueTiempo(const BloqueTiempo &bloque) {
  bloquesTiempo[bloque.id] = bloque;
}

void VerificadorRestricciones::agregarDisponibilidadProfesor(int idProfesor,
                                                 int idBloque) {
  disponibilidadProfesor[idProfesor].insert(idBloque);
}

void VerificadorRestricciones::agregarPrerrequisitoCurso(int idCurso,
                                              int idPrerrequisito) {
  prerrequisitosCurso[idCurso].insert(idPrerrequisito);
}

void VerificadorRestricciones::agregarGrupoCurso(int idCurso, int idGrupo) {
  gruposCurso[idCurso] = idGrupo;
}

bool VerificadorRestricciones::esAsignacionValida(
    const Asignacion &asignacion,
    const std::vector<Asignacion> &asignacionesExistentes) const {
  // Verificar disponibilidad profesor
  if (!verificarDisponibilidadProfesor(asignacion.idProfesor,
                                  asignacion.idBloque)) {
    return false;
  }

  // Verificar conflictos de tiempo (Profesor)
  if (verificarConflictoTiempo(asignacion.idProfesor, asignacion.idBloque,
                        asignacionesExistentes)) {
    return false;
  }

  // Verificar conflictos de grupo (Estudiantes)
  if (verificarConflictoGrupo(asignacion.idCurso, asignacion.idBloque,
                         asignacionesExistentes)) {
    return false;
  }

  return true;
}

bool VerificadorRestricciones::verificarConflictoTiempo(
    int idProfesor, int idBloque,
    const std::vector<Asignacion> &asignaciones) const {
  auto it = bloquesTiempo.find(idBloque);
  if (it == bloquesTiempo.end()) {
    return true; // Bloque inválido
  }

  const BloqueTiempo &nuevoBloque = it->second;

  for (const auto &asignacion : asignaciones) {
    if (asignacion.idProfesor == idProfesor) {
      auto existenteIt = bloquesTiempo.find(asignacion.idBloque);
      if (existenteIt != bloquesTiempo.end()) {
        if (nuevoBloque.seSolapa(existenteIt->second)) {
          return true; // Conflicto encontrado
        }
      }
    }
  }

  return false;
}

bool VerificadorRestricciones::verificarConflictoGrupo(
    int idCurso, int idBloque,
    const std::vector<Asignacion> &asignaciones) const {

  auto grupoIt = gruposCurso.find(idCurso);
  if (grupoIt == gruposCurso.end()) {
    return false; // Sin grupo asignado, asumir sin conflicto
  }
  int idGrupo = grupoIt->second;

  auto it = bloquesTiempo.find(idBloque);
  if (it == bloquesTiempo.end()) {
    return true; // Bloque inválido
  }
  const BloqueTiempo &nuevoBloque = it->second;

  for (const auto &asignacion : asignaciones) {
    // Verificar si el otro curso pertenece al mismo grupo
    auto otroGrupoIt = gruposCurso.find(asignacion.idCurso);
    if (otroGrupoIt != gruposCurso.end() && otroGrupoIt->second == idGrupo) {
      // Mismo grupo, verificar solapamiento de tiempo
      auto existenteIt = bloquesTiempo.find(asignacion.idBloque);
      if (existenteIt != bloquesTiempo.end()) {
        if (nuevoBloque.seSolapa(existenteIt->second)) {
          return true; // Conflicto: Mismo grupo tiene dos clases al mismo tiempo
        }
      }
    }
  }

  return false;
}

bool VerificadorRestricciones::verificarDisponibilidadProfesor(int idProfesor,
                                                   int idBloque) const {
  auto it = disponibilidadProfesor.find(idProfesor);
  if (it == disponibilidadProfesor.end()) {
    return false; // Sin datos de disponibilidad
  }

  return it->second.find(idBloque) != it->second.end();
}

bool VerificadorRestricciones::verificarPrerrequisitos(
    int idCurso, const std::vector<Asignacion> &asignaciones) const {
  auto it = prerrequisitosCurso.find(idCurso);
  if (it == prerrequisitosCurso.end()) {
    return true; // Sin prerrequisitos
  }

  std::unordered_set<int> cursosAsignados;
  for (const auto &asignacion : asignaciones) {
    cursosAsignados.insert(asignacion.idCurso);
  }

  for (int idPrerreq : it->second) {
    if (cursosAsignados.find(idPrerreq) == cursosAsignados.end()) {
      return false;
    }
  }

  return true;
}

std::vector<int> VerificadorRestricciones::obtenerBloquesDisponibles(
    int idCurso, int idProfesor,
    const std::vector<Asignacion> &asignaciones) const {

  std::vector<int> disponibles;

  auto dispoIt = disponibilidadProfesor.find(idProfesor);
  if (dispoIt == disponibilidadProfesor.end()) {
    return disponibles;
  }

  for (int idBloque : dispoIt->second) {
    if (!verificarConflictoTiempo(idProfesor, idBloque, asignaciones)) {
      disponibles.push_back(idBloque);
    }
  }

  return disponibles;
}

std::string VerificadorRestricciones::obtenerMensajeViolacion(
    const Asignacion &asignacion,
    const std::vector<Asignacion> &asignaciones) const {

  std::ostringstream oss;

  if (!verificarDisponibilidadProfesor(asignacion.idProfesor,
                                  asignacion.idBloque)) {
    oss << "Profesor no disponible en este horario. ";
  }

  if (verificarConflictoTiempo(asignacion.idProfesor, asignacion.idBloque,
                        asignaciones)) {
    oss << "Conflicto de horario del profesor. ";
  }

  return oss.str();
}

int VerificadorRestricciones::obtenerSiguienteBloqueConsecutivo(int idBloque) const {
  auto it = bloquesTiempo.find(idBloque);
  if (it == bloquesTiempo.end()) {
    return -1;
  }
  const BloqueTiempo &actual = it->second;

  for (const auto &par : bloquesTiempo) {
    const BloqueTiempo &siguiente = par.second;
    if (siguiente.dia == actual.dia && siguiente.horaInicio == actual.horaFin &&
        siguiente.minutoInicio == actual.minutoFin) {
      return siguiente.id;
    }
  }
  return -1;
}

} // namespace planificador
