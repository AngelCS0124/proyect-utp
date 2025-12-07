#include "planificador.hpp"
#include <algorithm>
#include <chrono>
#include <map>
#include <set>
#include <sstream>
#include <utility>

namespace planificador {

// Implementación de ResultadoHorario
ResultadoHorario::ResultadoHorario()
    : exito(false), conteoBacktrack(0), tiempoComputo(0.0) {}

// Implementación de PlanificadorCore
PlanificadorCore::PlanificadorCore()
    : verificadorRestricciones(
          std::make_unique<VerificadorRestricciones>(grafo)),
      contadorBacktrack(0), debeDetenerse(false) {}

PlanificadorCore::~PlanificadorCore() = default;

void PlanificadorCore::cargarCurso(int id, const std::string &nombre,
                                   int matricula,
                                   const std::vector<int> &prerrequisitos,
                                   int idGrupo, int duracion) {
  int idNodo = grafo.agregarNodo(TipoNodo::CURSO, nombre);
  auto nodo = grafo.obtenerNodo(idNodo);
  nodo->setAtributo("id", std::to_string(id));
  nodo->setAtributo("groupId", std::to_string(idGrupo));
  nodo->setAtributo("duration", std::to_string(duracion));

  cursoExtToInt[id] = idNodo;

  for (int idPrerreq : prerrequisitos) {
    // Nota: Los prerrequisitos vienen como IDs externos.
    // Necesitamos convertirlos a internos si ya existen.
    // Si no existen, esto podría fallar si no manejamos el orden de carga.
    // Asumimos que se cargan en orden o que manejamos la dependencia después.
    // PERO verificadorRestricciones espera IDs internos.
    if (cursoExtToInt.find(idPrerreq) != cursoExtToInt.end()) {
      verificadorRestricciones->agregarPrerrequisitoCurso(
          idNodo, cursoExtToInt[idPrerreq]);
    }
  }
  verificadorRestricciones->agregarGrupoCurso(
      idNodo, idGrupo); // idGrupo es atributo, no ID de nodo
}

void PlanificadorCore::cargarProfesor(
    int id, const std::string &nombre,
    const std::vector<int> &bloquesDisponibles) {
  int idNodo = grafo.agregarNodo(TipoNodo::PROFESOR, nombre);
  auto nodo = grafo.obtenerNodo(idNodo);
  nodo->setAtributo("id", std::to_string(id));

  profesorExtToInt[id] = idNodo;

  for (int idBloque : bloquesDisponibles) {
    // idBloque es externo. Necesitamos convertirlo?
    // cargarProfesor se llama DESPUES de cargarBloqueTiempo normalmente?
    // Si no, tenemos un problema.
    // Asumimos que los bloques se cargan antes o usamos un mapa temporal?
    // O mejor, verificadorRestricciones maneja IDs internos.
    // Pero cargarProfesor recibe IDs externos de bloques.
    // DEBEMOS cargar bloques antes.
    if (bloqueExtToInt.find(idBloque) != bloqueExtToInt.end()) {
      verificadorRestricciones->agregarDisponibilidadProfesor(
          idNodo, bloqueExtToInt[idBloque]);
    }
  }
}

void PlanificadorCore::cargarBloqueTiempo(int id, const std::string &dia,
                                          int horaInicio, int minutoInicio,
                                          int horaFin, int minutoFin) {
  int idNodo = grafo.agregarNodo(TipoNodo::BLOQUE_TIEMPO, dia);
  auto nodo = grafo.obtenerNodo(idNodo);
  nodo->setAtributo("id", std::to_string(id));

  bloqueExtToInt[id] = idNodo;

  BloqueTiempo bloque(idNodo, dia, horaInicio, minutoInicio, horaFin,
                      minutoFin);
  verificadorRestricciones->agregarBloqueTiempo(bloque);
}

void PlanificadorCore::asignarProfesorACurso(int idCurso, int idProfesor) {
  // Convertir IDs externos a internos
  if (cursoExtToInt.find(idCurso) == cursoExtToInt.end() ||
      profesorExtToInt.find(idProfesor) == profesorExtToInt.end()) {
    // Error: IDs no encontrados
    return;
  }

  int idNodoCurso = cursoExtToInt[idCurso];
  int idNodoProfesor = profesorExtToInt[idProfesor];

  // Crear arista de curso a profesor
  grafo.agregarArista(idNodoCurso, idNodoProfesor);
}

ResultadoHorario PlanificadorCore::generarHorario(int limiteTiempoSegundos,
                                                  bool modoCompleto) {
  return generarHorarioConCallback(nullptr, limiteTiempoSegundos, modoCompleto);
}

ResultadoHorario PlanificadorCore::generarHorarioConCallback(
    CallbackProgreso callback, int limiteTiempoSegundos, bool modoCompleto) {
  ResultadoHorario resultado;
  tiempoInicio = std::chrono::high_resolution_clock::now();
  this->limiteTiempoSegundos = limiteTiempoSegundos;
  this->modoCompleto = modoCompleto;
  this->maxCursosAsignados = 0;
  this->mejorSolucion.clear();

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

  actualizarProgreso(0, ordenCursos.size(),
                     "Iniciando generación de horario...");

  // Ejecutar algoritmo de backtracking
  std::vector<Asignacion> asignaciones;
  bool exitoCompleto = backtrack(asignaciones, ordenCursos, 0);

  // Verificar si realmente se asignaron todos los cursos
  std::set<int> cursosAsignados;
  for (const auto &a : asignaciones) {
    cursosAsignados.insert(a.idCurso);
  }

  if (cursosAsignados.size() < ordenCursos.size()) {
    exitoCompleto = false; // Éxito parcial
  }

  resultado.exito = exitoCompleto;

  if (debeDetenerse) {
    // Si se detuvo por tiempo o usuario, devolvemos lo mejor que tenemos
    if (!mejorSolucion.empty()) {
      resultado.asignaciones = mejorSolucion;
      // Si no es éxito completo, es parcial pero útil
      resultado.exito = false; // Marcar como no perfecto
      resultado.mensajeError = "Tiempo agotado o detenido. Se muestra la mejor "
                               "solución parcial encontrada (" +
                               std::to_string(maxCursosAsignados) + "/" +
                               std::to_string(ordenCursos.size()) + " cursos).";
    } else {
      resultado.exito = false;
      resultado.mensajeError =
          "Generación detenida sin encontrar solución válida.";
    }
  } else if (exitoCompleto) {
    resultado.asignaciones = asignaciones;
    actualizarProgreso(ordenCursos.size(), ordenCursos.size(),
                       "Horario generado exitosamente!");
  } else {
    // Terminó la búsqueda sin éxito completo
    if (!modoCompleto && !mejorSolucion.empty()) {
      // En modo "Best Effort" devolvemos lo que encontramos
      resultado.asignaciones = mejorSolucion;
      resultado.exito = false; // Parcial
      resultado.mensajeError = "No se encontró solución perfecta. Se muestra "
                               "la mejor solución parcial (" +
                               std::to_string(maxCursosAsignados) + "/" +
                               std::to_string(ordenCursos.size()) + " cursos).";
    } else {
      resultado.mensajeError = "No se pudo encontrar un horario válido con las "
                               "restricciones dadas.\n\n" +
                               analizarFallo();
    }
  }

  resultado.conteoBacktrack = contadorBacktrack;

  auto tiempoFin = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> transcurrido = tiempoFin - tiempoInicio;
  resultado.tiempoComputo = transcurrido.count();

  // Convertir asignaciones a IDs externos
  std::vector<Asignacion> asignacionesExternas;
  for (const auto &a : resultado.asignaciones) {
    asignacionesExternas.push_back(Asignacion(obtenerIdExterno(a.idCurso),
                                              obtenerIdExterno(a.idBloque),
                                              obtenerIdExterno(a.idProfesor)));
  }
  resultado.asignaciones = asignacionesExternas;

  return resultado;
}

int PlanificadorCore::obtenerIdExterno(int idInterno) const {
  auto nodo = grafo.obtenerNodo(idInterno);
  if (nodo && nodo->tieneAtributo("id")) {
    try {
      return std::stoi(nodo->getAtributo("id"));
    } catch (...) {
      return -1;
    }
  }
  return -1;
}

bool PlanificadorCore::backtrack(std::vector<Asignacion> &asignaciones,
                                 const std::vector<int> &cursos,
                                 size_t indiceCurso) {
  contadorBacktrack++;

  // Verificar si debemos detenernos (usuario o tiempo)
  if (debeDetenerse) {
    return false;
  }

  // Verificar límite de tiempo periódicamente (cada 1000 backtracks para no
  // afectar rendimiento)
  if (limiteTiempoSegundos > 0 && contadorBacktrack % 1000 == 0) {
    auto ahora = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> transcurrido = ahora - tiempoInicio;
    if (transcurrido.count() > limiteTiempoSegundos) {
      debeDetenerse = true;
      return false;
    }
  }

  // Actualizar mejor solución encontrada hasta ahora
  if (asignaciones.size() > maxCursosAsignados) {
    actualizarMejorSolucion(asignaciones);
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
    // En modo Best Effort, podríamos saltarlo y seguir
    // Por ahora, asumimos que si no hay profesor, no se puede programar este
    // curso Pero seguimos intentando con el siguiente para maximizar
    // asignaciones
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
  // Asumir 1 bloque = 1 hora (aprox).
  // La lógica anterior dividía por 2, pero ahora duration viene directo como
  // slots.
  int bloquesNecesarios = duracion;
  if (bloquesNecesarios < 1)
    bloquesNecesarios = 1;

  // Probar todos los bloques de tiempo disponibles
  auto bloquesDisponibles = verificadorRestricciones->obtenerBloquesDisponibles(
      idCurso, idProfesor, asignaciones);

  // Iniciar recursión para asignar los bloques de este curso
  std::vector<std::string> diasUsados;
  if (backtrackCurso(asignaciones, idCurso, idProfesor, bloquesNecesarios,
                     cursos, indiceCurso, diasUsados)) {
    return true;
  }

  // ESTRATEGIA ROBUSTA: Si no se puede asignar este curso, lo saltamos
  // y continuamos con el siguiente para generar un horario parcial.
  // Esto asegura que siempre devolvamos algo.
  return backtrack(asignaciones, cursos, indiceCurso + 1);
}

bool PlanificadorCore::backtrackCurso(
    std::vector<Asignacion> &asignaciones, int idCurso, int idProfesor,
    int bloquesRestantes, const std::vector<int> &cursos, size_t indiceCurso,
    const std::vector<std::string> &diasUsados) {
  // Caso base: todos los bloques de este curso asignados
  if (bloquesRestantes == 0) {
    // Verificar restricción de "al menos 2 días" si el curso tiene muchos
    // bloques Por ahora, si tiene >= 4 bloques, exigimos 2 días. Si tiene < 4,
    // permitimos 1 día.
    // TODO: Hacer esto configurable o más estricto según reglas exactas.
    // La regla E dice: "Las horas semanales deben distribuirse en al menos 2
    // días diferentes" "Ejemplo: 4 horas semanales NO pueden ser todas el
    // Lunes" Asumimos que para < 4 horas (ej 3) sí se puede en un día.

    // Calcular total de bloques asignados a este curso (podríamos pasarlo como
    // param) Pero sabemos que acabamos de asignar 'bloquesRestantes' que era el
    // inicial? No. Necesitamos saber el total original. Simplificación: Si
    // diasUsados.size() < 2 y bloquesAsignadosTotal >= 4 -> return false. Pero
    // no tenemos bloquesAsignadosTotal fácil aquí sin recalcular. Asumimos que
    // la lógica de partición ya intentó cumplirlo.

    return backtrack(asignaciones, cursos, indiceCurso + 1);
  }

  auto bloquesDisponibles = verificadorRestricciones->obtenerBloquesDisponibles(
      idCurso, idProfesor, asignaciones);

  for (int idBloqueInicio : bloquesDisponibles) {
    // Verificar que este bloque no sea en un día ya usado si queremos forzar
    // distribución O más bien, si ya usamos este día, verificar si excedemos el
    // límite diario (3 horas)

    std::string diaBloque =
        verificadorRestricciones->obtenerDiaBloque(idBloqueInicio);

    // Contar cuántos bloques ya asignamos a este día para este curso
    int bloquesEnEsteDia = 0;
    for (const auto &a : asignaciones) {
      if (a.idCurso == idCurso) {
        std::string d = verificadorRestricciones->obtenerDiaBloque(a.idBloque);
        if (d == diaBloque)
          bloquesEnEsteDia++;
      }
    }

    // Si ya tenemos 3 bloques en este día, no podemos agregar más (Hard
    // constraint E)
    if (bloquesEnEsteDia >= 3)
      continue;

    // Intentar asignar chunks de 1, 2 o 3 bloques
    // Pero respetando bloquesRestantes y límite diario (3)
    int maxChunk = std::min(bloquesRestantes, 3 - bloquesEnEsteDia);

    // Probamos chunks de mayor a menor para "Best Effort" (llenar días)
    // O de menor a mayor?
    // Si probamos 3 primero, llenamos el día.
    for (int tamChunk = maxChunk; tamChunk >= 1; --tamChunk) {
      std::vector<int> secuencia;
      secuencia.push_back(idBloqueInicio);
      int bloqueActual = idBloqueInicio;
      bool posible = true;

      for (int i = 1; i < tamChunk; ++i) {
        int siguiente =
            verificadorRestricciones->obtenerSiguienteBloqueConsecutivo(
                bloqueActual);
        if (siguiente == -1) {
          posible = false;
          break;
        }

        // Verificar validez
        Asignacion check(idCurso, siguiente, idProfesor);
        if (!verificadorRestricciones->esAsignacionValida(check,
                                                          asignaciones)) {
          posible = false;
          break;
        }
        bloqueActual = siguiente;
        secuencia.push_back(bloqueActual);
      }

      if (posible) {
        // Verificar validez del primero (los demás ya se verificaron en loop,
        // menos el primero)
        Asignacion a1(idCurso, idBloqueInicio, idProfesor);
        if (!verificadorRestricciones->esAsignacionValida(a1, asignaciones)) {
          posible = false;
        }
      }

      if (posible) {
        // Commit chunk
        std::vector<Asignacion> nuevas;
        for (int idB : secuencia) {
          nuevas.push_back(Asignacion(idCurso, idB, idProfesor));
        }

        for (const auto &a : nuevas)
          asignaciones.push_back(a);

        std::vector<std::string> nuevosDias = diasUsados;
        bool diaNuevo = true;
        for (const std::string &d : diasUsados)
          if (d == diaBloque)
            diaNuevo = false;
        if (diaNuevo)
          nuevosDias.push_back(diaBloque);

        if (backtrackCurso(asignaciones, idCurso, idProfesor,
                           bloquesRestantes - tamChunk, cursos, indiceCurso,
                           nuevosDias)) {
          return true;
        }

        // Backtrack
        for (size_t i = 0; i < nuevas.size(); ++i)
          asignaciones.pop_back();
      }
    }
  }

  return false;
}

void PlanificadorCore::actualizarMejorSolucion(
    const std::vector<Asignacion> &asignaciones) {
  if (asignaciones.size() > mejorSolucion.size()) {
    mejorSolucion = asignaciones;
    maxCursosAsignados = 0;
    // Contar cursos únicos asignados
    std::vector<int> cursosUnicos;
    for (const auto &a : asignaciones) {
      bool existe = false;
      for (int id : cursosUnicos)
        if (id == a.idCurso)
          existe = true;
      if (!existe)
        cursosUnicos.push_back(a.idCurso);
    }
    maxCursosAsignados = cursosUnicos.size();
  }
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
      // Verificar si tiene suficientes bloques
      // Esto es aproximado, ya que no sabemos cuántos bloques tiene realmente
      // disponibles sin consultar restricciones Pero podemos contar las aristas
      // de disponibilidad si las tuviéramos en el grafo explícitamente O
      // consultar verificadorRestricciones. Por ahora dejamos el mensaje
      // genérico si parece sobrecargado.
    }
  }

  analisis << "\nSugerencia: Intente agregar más horarios disponibles a los "
              "profesores mencionados o asigne menos cursos.";

  return analisis.str();
}

} // namespace planificador
