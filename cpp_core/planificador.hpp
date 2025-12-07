#ifndef PLANIFICADOR_HPP
#define PLANIFICADOR_HPP

#include "grafo.hpp"
#include "restricciones.hpp"
#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace planificador {

// Resultado del horario
struct ResultadoHorario {
  bool exito;
  std::vector<Asignacion> asignaciones;
  std::string mensajeError;
  int conteoBacktrack;
  double tiempoComputo;

  ResultadoHorario();
};

// Callback de progreso para UI
using CallbackProgreso =
    std::function<void(int actual, int total, const std::string &mensaje)>;

// Motor principal del planificador
class PlanificadorCore {
public:
  PlanificadorCore();
  ~PlanificadorCore();

  // Carga de Datos
  void cargarCurso(int id, const std::string &nombre, int matricula,
                   const std::vector<int> &prerrequisitos, int idGrupo,
                   int duracion);
  void cargarProfesor(int id, const std::string &nombre,
                      const std::vector<int> &bloquesDisponibles);
  void cargarBloqueTiempo(int id, const std::string &dia, int horaInicio,
                          int minutoInicio, int horaFin, int minutoFin);

  // Asignación Curso-Profesor
  void asignarProfesorACurso(int idCurso, int idProfesor);

  // Generación de Horario
  ResultadoHorario generarHorario(int limiteTiempoSegundos = 0,
                                  bool modoCompleto = false);
  ResultadoHorario generarHorarioConCallback(CallbackProgreso callback,
                                             int limiteTiempoSegundos = 0,
                                             bool modoCompleto = false);

  // Control
  void detenerGeneracion();
  void reiniciar();

  // Análisis
  std::string analizarFallo() const;

  // Getters
  const Grafo &obtenerGrafo() const;
  std::vector<Asignacion> obtenerAsignacionesActuales() const;
  bool tieneDatos() const;
  std::string validarDatos() const;

private:
  // Algoritmo de Backtracking
  bool backtrack(std::vector<Asignacion> &asignaciones,
                 const std::vector<int> &cursos, size_t indiceCurso);

  bool backtrackCurso(std::vector<Asignacion> &asignaciones, int idCurso,
                      int idProfesor, int bloquesRestantes,
                      const std::vector<int> &cursos, size_t indiceCurso,
                      const std::vector<std::string> &diasUsados);

  // Métodos auxiliares
  std::vector<int> obtenerOrdenCursos() const;
  bool intentarAsignacion(const Asignacion &asignacion,
                          std::vector<Asignacion> &asignaciones);
  void actualizarProgreso(int actual, int total, const std::string &mensaje);
  void actualizarMejorSolucion(const std::vector<Asignacion> &asignaciones);

  // Estado interno
  Grafo grafo;
  std::unique_ptr<VerificadorRestricciones> verificadorRestricciones;
  CallbackProgreso callbackProgreso;
  int contadorBacktrack;
  bool debeDetenerse;

  // Control de tiempo y mejor esfuerzo
  std::chrono::time_point<std::chrono::high_resolution_clock> tiempoInicio;
  int limiteTiempoSegundos;
  bool modoCompleto;
  std::vector<Asignacion> mejorSolucion;
  int maxCursosAsignados;
};

} // namespace planificador

#endif // PLANIFICADOR_HPP
