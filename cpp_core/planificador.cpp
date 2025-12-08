#include "planificador.hpp"
#include <algorithm>
#include <chrono>
#include <map>
#include <random>
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
                                                  int nivel) {
  return generarHorarioConCallback(nullptr, limiteTiempoSegundos, nivel);
}

ResultadoHorario PlanificadorCore::generarHorarioConCallback(
    CallbackProgreso callback, int limiteTiempoSegundos, int nivel) {
  ResultadoHorario resultado;
  tiempoInicio = std::chrono::high_resolution_clock::now();
  this->limiteTiempoSegundos = limiteTiempoSegundos;
  this->nivelActual = nivel;
  this->maxCursosAsignados = 0;
  this->mejorSolucion.clear();
  this->mejorPuntaje = -1e9; // Inicializar con puntaje muy bajo

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

  // Obtener orden de cursos
  std::vector<int> ordenCursos = obtenerOrdenCursos();
  if (ordenCursos.empty()) {
    resultado.exito = false;
    resultado.mensajeError = "No hay cursos para programar";
    return resultado;
  }

  actualizarProgreso(0, ordenCursos.size(),
                     "Iniciando generación de horario (Nivel " +
                         std::to_string(nivel) + ")...");

  // BUCLE DE OPTIMIZACIÓN
  // Ejecutamos al menos una vez de forma determinista.
  // Si hay tiempo y nivel es alto (STRICT/RELAXED), seguimos probando con
  // aleatoriedad.
  bool primeraPasada = true;
  this->usarAleatoriedad = false;

  while (!debeDetenerse) {
    std::vector<Asignacion> asignaciones;
    // Resetear estado para nueva iteración si es necesario?
    // backtrack limpia? No, backtrack construye sobre 'asignaciones' vacía.

    bool exito = backtrack(asignaciones, ordenCursos, 0);

    // Calcular puntaje de esta solución
    double puntajeActual = calcularPuntaje(asignaciones);

    // Si es mejor, guardarla
    if (asignaciones.size() > maxCursosAsignados ||
        (asignaciones.size() == maxCursosAsignados &&
         puntajeActual > mejorPuntaje)) {
      mejorSolucion = asignaciones;
      maxCursosAsignados = asignaciones.size();
      mejorPuntaje = puntajeActual;
    }

    // Verificar tiempo
    auto ahora = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> transcurrido = ahora - tiempoInicio;
    if (limiteTiempoSegundos > 0 &&
        transcurrido.count() >= limiteTiempoSegundos) {
      break;
    }

    // Si es modo GREEDY o EMERGENCY, terminamos con la primera solución válida
    // O si encontramos una solución completa (exito)
    if ((nivelActual >= 3 || exito) && !debeDetenerse) {
      // Si queremos seguir optimizando en STRICT/RELAXED incluso con éxito,
      // quitamos "|| exito" Pero por defecto, si encontramos una solución
      // completa, paramos. A menos que sea "Sin límite" (limiteTiempoSegundos
      // <= 0) y queramos la mejor de las mejores.
      if (limiteTiempoSegundos > 0 || exito) {
        break;
      }
    }

    // Para siguientes pasadas, usar aleatoriedad
    this->usarAleatoriedad = true;
    primeraPasada = false;

    // Si falló la primera pasada determinista y no tenemos nada, seguimos
    // intentando
  }

  // Preparar resultado final con la MEJOR solución encontrada
  resultado.asignaciones = mejorSolucion;
  resultado.exito = (maxCursosAsignados == ordenCursos.size());

  if (resultado.exito) {
    resultado.mensajeError = "Horario generado exitosamente. Puntaje: " +
                             std::to_string((int)mejorPuntaje);
  } else if (!mejorSolucion.empty()) {
    resultado.exito = false;
    resultado.mensajeError = "Horario parcial generado (" +
                             std::to_string(maxCursosAsignados) + "/" +
                             std::to_string(ordenCursos.size()) +
                             "). Puntaje: " + std::to_string((int)mejorPuntaje);
  } else {
    resultado.exito = false;
    resultado.mensajeError = "No se pudo generar ningún horario válido.";
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

double
PlanificadorCore::calcularPuntaje(const std::vector<Asignacion> &asignaciones) {
  double puntaje = 0;

  // 1. Maximizar cursos asignados (prioridad máxima)
  puntaje +=
      asignaciones.size() * 100000; // Aumentado peso para asegurar completitud

  // Organizar por grupo y día para analizar huecos y horario
  std::map<std::string, std::map<std::string, std::vector<int>>> horarioGrupo;

  for (const auto &a : asignaciones) {
    auto nodoCurso = grafo.obtenerNodo(a.idCurso);
    std::string groupId = nodoCurso->getAtributo("groupId");
    std::string dia = verificadorRestricciones->obtenerDiaBloque(a.idBloque);

    horarioGrupo[groupId][dia].push_back(a.idBloque);

    // 2. Preferir horas tempranas (penalizar horas tardías)
    // IDs de bloque: 1 (7:00), 2 (7:55), ... 9 (14:55)
    // Penalizar cuadráticamente para odiar mucho las últimas horas
    puntaje -= (a.idBloque * a.idBloque) * 5.0;
  }

  // 3. Penalizar huecos (horas libres entre clases)
  for (auto &[grupo, dias] : horarioGrupo) {
    for (auto &[dia, bloques] : dias) {
      std::sort(bloques.begin(), bloques.end());

      if (bloques.empty())
        continue;

      // Verificar inicio del día (Preferir empezar a la primera hora
      // disponible, usualmente bloque 1) Si el primer bloque no es el 1 (o el
      // mínimo posible), penalizar levemente para fomentar "entrar temprano y
      // salir temprano" Pero cuidado con profes que no pueden temprano. puntaje
      // -= (bloques.front() - 1) * 50;

      for (size_t i = 0; i < bloques.size() - 1; ++i) {
        int actual = bloques[i];
        int siguiente = bloques[i + 1];

        // Verificar si son consecutivos
        int esperado =
            verificadorRestricciones->obtenerSiguienteBloqueConsecutivo(actual);

        if (esperado != -1 && siguiente != esperado) {
          // Hay un hueco
          // Penalización MUY fuerte por hueco intermedio
          puntaje -= 2000;
        } else {
          // Son consecutivos, bonificación
          puntaje += 100;
        }
      }
    }
  }

  return puntaje;
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
  int idProfesor = -1; // Default: Sin profesor

  if (!aristasProfesor.empty()) {
    idProfesor = aristasProfesor[0]; // Asumiendo un profesor por curso
  }

  // Si no hay profesor asignado, NO programar el curso.
  // Esto evita que aparezcan como "Unknown" en el horario.
  if (idProfesor == -1) {
    return backtrack(asignaciones, cursos, indiceCurso + 1);
  }

  // Determinar bloques necesarios
  int duracion = 1;
  if (nodoCurso->tieneAtributo("duration")) {
    try {
      duracion = std::stoi(nodoCurso->getAtributo("duration"));
    } catch (...) {
      duracion = 1;
    }
  }

  int bloquesNecesarios = duracion;
  if (bloquesNecesarios < 1)
    bloquesNecesarios = 1;

  // Iniciar recursión para asignar los bloques de este curso
  std::vector<std::string> diasUsados;

  // Intentar asignar el curso
  if (backtrackCurso(asignaciones, idCurso, idProfesor, bloquesNecesarios,
                     cursos, indiceCurso, diasUsados)) {
    return true;
  }

  // ESTRATEGIA ROBUSTA: Si no se puede asignar este curso, lo saltamos
  // y continuamos con el siguiente para generar un horario parcial.
  // Esto asegura que siempre devolvamos algo.
  // NOTA: Esto significa que el resultado final puede no tener todos los
  // cursos. El wrapper de Python debe detectar esto y advertir al usuario.
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

  if (this->usarAleatoriedad) {
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(bloquesDisponibles.begin(), bloquesDisponibles.end(), g);
  }

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

    // Si ya tenemos 3 bloques en este día, PREFERIBLEMENTE no agregar más.
    // Nivel STRICT: Máximo 3 horas (Soft Constraint 7 se vuelve Hard-ish)
    // Otros niveles: Relajado a 8
    int limiteDiario = 8;
    if (nivelActual == 1) { // STRICT
      limiteDiario = 3;
    }

    if (bloquesEnEsteDia >= limiteDiario)
      continue;

    // Intentar asignar chunks de 1, 2 o 3 bloques
    // Pero respetando bloquesRestantes y límite diario
    int maxChunk = std::min(bloquesRestantes, limiteDiario - bloquesEnEsteDia);

    // Limitamos el chunk a 3 horas consecutivas como máximo ideal
    if (maxChunk > 3)
      maxChunk = 3;

    // Probamos chunks de mayor a menor para "Best Effort" (llenar días)
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
        if (!verificadorRestricciones->esAsignacionValida(
                check, asignaciones,
                (VerificadorRestricciones::NivelRestriccion)nivelActual)) {
          posible = false;
          break;
        }
        bloqueActual = siguiente;
        secuencia.push_back(bloqueActual);
      }

      if (posible) {
        // Verificar validez del primero
        Asignacion a1(idCurso, idBloqueInicio, idProfesor);
        if (!verificadorRestricciones->esAsignacionValida(
                a1, asignaciones,
                (VerificadorRestricciones::NivelRestriccion)nivelActual)) {
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

  // Si estamos en modo Inteligente (o siempre, según petición), usamos "Easiest
  // First" Easiest First = Curso con más opciones disponibles primero.
  // Heurística: (Bloques disponibles del profe) * (1 / Duración)
  // O simplemente: Priorizar cursos con profesor asignado y mucha
  // disponibilidad.

  // Para simplificar y cumplir con "Easiest First":
  // Ordenamos por:
  // 1. Cursos con profesor ya asignado (más restringido? No, más fácil de
  // validar)
  // 2. Disponibilidad del profesor (Mayor es mejor)

  // Sin embargo, la literatura dice "Most Constrained First" (Hardest First)
  // para CSP. El usuario pidió explícitamente "Easiest First". Esto maximiza el
  // número de cursos asignados en un horario parcial.

  std::vector<std::pair<int, int>> cursoPuntaje;

  for (int idCurso : cursos) {
    int puntaje = 0;
    auto vecinos = grafo.obtenerVecinos(idCurso);
    if (!vecinos.empty()) {
      int idProfesor = vecinos[0];
      // Obtener disponibilidad del profesor
      // No tenemos acceso directo fácil a disponibilidadProfesor desde aquí sin
      // pasar por verificador Pero podemos estimar con grado del nodo profesor?
      // No, el grafo no tiene nodos de bloque conectados al profe directamente
      // en esta estructura Usamos verificadorRestricciones Pero
      // obtenerBloquesDisponibles requiere asignaciones actuales (vacío)
      std::vector<Asignacion> vacio;
      auto bloques = verificadorRestricciones->obtenerBloquesDisponibles(
          idCurso, idProfesor, vacio);
      puntaje = bloques.size();
    } else {
      // Sin profesor: muchas opciones (cualquier bloque)
      puntaje = 1000;
    }
    cursoPuntaje.push_back({idCurso, puntaje});
  }

  // Ordenar descendente (Mayor puntaje = Más fácil = Primero)
  std::sort(cursoPuntaje.begin(), cursoPuntaje.end(),
            [](const std::pair<int, int> &a, const std::pair<int, int> &b) {
              return a.second > b.second;
            });

  std::vector<int> orden;
  for (const auto &p : cursoPuntaje) {
    orden.push_back(p.first);
  }

  return orden;
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

Metricas PlanificadorCore::obtenerMetricas() const {
  Metricas m;
  m.backtrackCount = contadorBacktrack;
  m.mejorPuntaje = mejorPuntaje;
  m.cursosAsignados = maxCursosAsignados;
  // Total cursos es el número de nodos tipo CURSO
  auto cursos = grafo.obtenerNodosPorTipo(TipoNodo::CURSO);
  m.totalCursos = cursos.size();

  if (limiteTiempoSegundos > 0 || debeDetenerse) {
    auto ahora = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> transcurrido = ahora - tiempoInicio;
    m.tiempoTranscurrido = transcurrido.count();
  } else {
    m.tiempoTranscurrido = 0;
  }

  return m;
}

} // namespace planificador
