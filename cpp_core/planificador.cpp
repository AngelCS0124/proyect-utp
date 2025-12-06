#include "planificador.hpp"
#include <algorithm>
#include <chrono>
#include <sstream>

namespace planificador {

// Implementación de ResultadoHorario
ResultadoHorario::ResultadoHorario()
    : exito(false), conteoBacktrack(0), tiempoComputo(0.0) {}

// Implementación de PlanificadorCore
PlanificadorCore::PlanificadorCore()
    : verificadorRestricciones(std::make_unique<VerificadorRestricciones>(grafo)),
      contadorBacktrack(0), debeDetenerse(false) {}

PlanificadorCore::~PlanificadorCore() = default;

void PlanificadorCore::cargarCurso(int id, const std::string &nombre, int matricula,
                               const std::vector<int> &prerrequisitos,
                               int idGrupo, int duracion) {
  int idNodo = grafo.agregarNodo(TipoNodo::CURSO, nombre);
  auto nodo = grafo.obtenerNodo(idNodo);
  nodo->setAtributo("id", std::to_string(id));
  nodo->setAtributo("groupId", std::to_string(idGrupo));
  nodo->setAtributo("duration", std::to_string(duracion));

  for (int idPrerreq : prerrequisitos) {
    verificadorRestricciones->agregarPrerrequisitoCurso(idNodo, idPrerreq);
  }
  verificadorRestricciones->agregarGrupoCurso(id, idGrupo);
}

void PlanificadorCore::cargarProfesor(int id, const std::string &nombre,
                                  const std::vector<int> &bloquesDisponibles) {
  int idNodo = grafo.agregarNodo(TipoNodo::PROFESOR, nombre);
  auto nodo = grafo.obtenerNodo(idNodo);
  nodo->setAtributo("id", std::to_string(id));

  for (int idBloque : bloquesDisponibles) {
    verificadorRestricciones->agregarDisponibilidadProfesor(idNodo, idBloque);
  }
}

void PlanificadorCore::cargarBloqueTiempo(int id, const std::string &dia, int horaInicio,
                                 int minutoInicio, int horaFin, int minutoFin) {
  int idNodo = grafo.agregarNodo(TipoNodo::BLOQUE_TIEMPO, dia);
  auto nodo = grafo.obtenerNodo(idNodo);
  nodo->setAtributo("id", std::to_string(id));

  BloqueTiempo bloque(idNodo, dia, horaInicio, minutoInicio, horaFin, minutoFin);
  verificadorRestricciones->agregarBloqueTiempo(bloque);
}

void PlanificadorCore::asignarProfesorACurso(int idCurso, int idProfesor) {
  // Crear arista de curso a profesor
  grafo.agregarArista(idCurso, idProfesor);
}

ResultadoHorario PlanificadorCore::generarHorario() {
  return generarHorarioConCallback(nullptr);
}

ResultadoHorario
PlanificadorCore::generarHorarioConCallback(CallbackProgreso callback) {
  ResultadoHorario resultado;
  auto tiempoInicio = std::chrono::high_resolution_clock::now();

  callbackProgreso = callback;
  contadorBacktrack = 0;
  debeDetenerse = false;

  // Validar datos primero
  std::string errorValidacion = validarDatos();
  if (!errorValidacion.empty()) {
    resultado.exito = false;
    resultado.mensajeError = errorValidacion;
    return resultado;
  }

  // Obtener orden de cursos (sort topológico si hay prerrequisitos)
  std::vector<int> ordenCursos = obtenerOrdenCursos();

  if (ordenCursos.empty()) {
    resultado.exito = false;
    resultado.mensajeError = "No hay cursos para programar";
    return resultado;
  }

  actualizarProgreso(0, ordenCursos.size(), "Iniciando generación de horario...");

  // Ejecutar algoritmo de backtracking
  std::vector<Asignacion> asignaciones;
  resultado.exito = backtrack(asignaciones, ordenCursos, 0);

  if (debeDetenerse) {
    resultado.exito = false;
    resultado.mensajeError = "Generación de horario detenida por usuario";
  } else if (resultado.exito) {
    resultado.asignaciones = asignaciones;
    actualizarProgreso(ordenCursos.size(), ordenCursos.size(),
                   "Horario generado exitosamente!");
  } else {
    resultado.mensajeError = "No se pudo encontrar un horario válido con las "
                          "restricciones dadas.\n\n" +
                          analizarFallo();
  }

  resultado.conteoBacktrack = contadorBacktrack;

  auto tiempoFin = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> transcurrido = tiempoFin - tiempoInicio;
  resultado.tiempoComputo = transcurrido.count();

  return resultado;
}

bool PlanificadorCore::backtrack(std::vector<Asignacion> &asignaciones,
                               const std::vector<int> &cursos,
                               size_t indiceCurso) {
  // Verificar si debemos detenernos
  if (debeDetenerse) {
    return false;
  }

  // Caso base: todos los cursos asignados
  if (indiceCurso >= cursos.size()) {
    return true;
  }

  int idCurso = cursos[indiceCurso];
  auto nodoCurso = grafo.obtenerNodo(idCurso);

  actualizarProgreso(indiceCurso, cursos.size(),
                 "Programando: " + nodoCurso->nombre);

  // Obtener profesor asignado para este curso
  auto aristasProfesor = grafo.obtenerVecinos(idCurso);
  if (aristasProfesor.empty()) {
    // Sin profesor asignado, saltar o fallar
    return backtrack(asignaciones, cursos, indiceCurso + 1);
  }

  int idProfesor = aristasProfesor[0]; // Asumiendo un profesor por curso

  // Determinar bloques necesarios
  int duracion = 1;
  if (nodoCurso->tieneAtributo("duration")) {
    try {
      duracion = std::stoi(nodoCurso->getAtributo("duration"));
    } catch (...) {
      duracion = 1;
    }
  }
  // Asumir 1 bloque = 2 horas. Si duracion <= 2, 1 bloque. Si 3 o 4, 2 bloques.
  int bloquesNecesarios = (duracion + 1) / 2;
  if (bloquesNecesarios < 1)
    bloquesNecesarios = 1;

  // Probar todos los bloques de tiempo disponibles
  auto bloquesDisponibles = verificadorRestricciones->obtenerBloquesDisponibles(
      idCurso, idProfesor, asignaciones);

  for (int idBloqueInicio : bloquesDisponibles) {
    std::vector<int> secuencia;
    secuencia.push_back(idBloqueInicio);

    int bloqueActual = idBloqueInicio;
    bool posible = true;

    // Encontrar bloques consecutivos
    for (int i = 1; i < bloquesNecesarios; ++i) {
      int siguienteBloque = verificadorRestricciones->obtenerSiguienteBloqueConsecutivo(bloqueActual);
      if (siguienteBloque == -1) {
        posible = false;
        break;
      }

      // Verificar que siguienteBloque es válido
      Asignacion checkAsign(idCurso, siguienteBloque, idProfesor);
      if (!verificadorRestricciones->esAsignacionValida(checkAsign, asignaciones)) {
        posible = false;
        break;
      }

      bloqueActual = siguienteBloque;
      secuencia.push_back(bloqueActual);
    }

    if (posible) {
      // Intentar asignar TODOS los bloques
      std::vector<Asignacion> nuevasAsignaciones;
      bool todoValido = true;

      for (int idBloque : secuencia) {
        Asignacion a(idCurso, idBloque, idProfesor);
        if (!verificadorRestricciones->esAsignacionValida(a, asignaciones)) {
          todoValido = false;
          break;
        }
        nuevasAsignaciones.push_back(a);
      }

      if (todoValido) {
        // Commit
        for (const auto &a : nuevasAsignaciones)
          asignaciones.push_back(a);

        if (backtrack(asignaciones, cursos, indiceCurso + 1))
          return true;

        // Backtrack
        for (size_t i = 0; i < nuevasAsignaciones.size(); ++i)
          asignaciones.pop_back();
      }
    }
  }

  // Ninguna asignación válida encontrada
  return false;
}

std::vector<int> PlanificadorCore::obtenerOrdenCursos() const {
  auto cursos = grafo.obtenerNodosPorTipo(TipoNodo::CURSO);

  // Intentar sort topológico si hay prerrequisitos
  try {
    return grafo.ordenamientoTopologico();
  } catch (...) {
    // Si falla (ciclos), retornar cursos en orden por defecto
    return cursos;
  }
}

void PlanificadorCore::actualizarProgreso(int actual, int total,
                                   const std::string &mensaje) {
  if (callbackProgreso) {
    callbackProgreso(actual, total, mensaje);
  }
}

void PlanificadorCore::detenerGeneracion() { debeDetenerse = true; }

void PlanificadorCore::reiniciar() {
  grafo.limpiar();
  verificadorRestricciones = std::make_unique<VerificadorRestricciones>(grafo);
  contadorBacktrack = 0;
  debeDetenerse = false;
}

const Grafo &PlanificadorCore::obtenerGrafo() const { return grafo; }

std::vector<Asignacion> PlanificadorCore::obtenerAsignacionesActuales() const {
  return std::vector<Asignacion>();
}

bool PlanificadorCore::tieneDatos() const { return grafo.tamano() > 0; }

std::string PlanificadorCore::validarDatos() const {
  std::ostringstream errores;

  auto cursos = grafo.obtenerNodosPorTipo(TipoNodo::CURSO);
  auto profesores = grafo.obtenerNodosPorTipo(TipoNodo::PROFESOR);
  auto bloques = grafo.obtenerNodosPorTipo(TipoNodo::BLOQUE_TIEMPO);

  if (cursos.empty()) {
    errores << "No hay cursos cargados. ";
  }

  if (profesores.empty()) {
    errores << "No hay profesores cargados. ";
  }

  if (bloques.empty()) {
    errores << "No hay horarios cargados. ";
  }

  return errores.str();
}

std::string PlanificadorCore::analizarFallo() const {
  std::ostringstream analisis;
  analisis << "Análisis de Fallo:\n\n";

  auto cursos = grafo.obtenerNodosPorTipo(TipoNodo::CURSO);
  auto profesores = grafo.obtenerNodosPorTipo(TipoNodo::PROFESOR);

  // 1. Verificar Capacidad de Profesores
  for (int idProfesor : profesores) {
    auto nodoProf = grafo.obtenerNodo(idProfesor);

    // Contar cursos asignados a este profesor
    int cursosAsignados = 0;
    int totalHorasNecesarias = 0;

    // Encontrar todos los cursos que apuntan a este profesor
    for (int idCurso : cursos) {
      auto vecinos = grafo.obtenerVecinos(idCurso);
      if (!vecinos.empty() && vecinos[0] == idProfesor) {
        cursosAsignados++;
        // Asumiendo 1 curso = 1 bloque por ahora (simplificación)
        totalHorasNecesarias++;
      }
    }

    if (cursosAsignados > 0) {
      analisis << "- Profesor " << nodoProf->nombre << " tiene "
               << cursosAsignados
               << " cursos asignados. Verifique que tenga al menos "
               << totalHorasNecesarias << " horarios disponibles.\n";
    }
  }

  analisis << "\nSugerencia: Intente agregar más horarios disponibles a los "
              "profesores mencionados o asigne menos cursos.";

  return analisis.str();
}

} // namespace planificador
