#ifndef PLANIFICADOR_HPP
#define PLANIFICADOR_HPP

#include "restricciones.hpp"
#include "grafo.hpp"
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
private:
  Grafo grafo;
  std::unique_ptr<VerificadorRestricciones> verificadorRestricciones;
  CallbackProgreso callbackProgreso;
  int contadorBacktrack;
  bool debeDetenerse;

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
  ResultadoHorario generarHorario();
  ResultadoHorario generarHorarioConCallback(CallbackProgreso callback);

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

  // Métodos auxiliares
  std::vector<int> obtenerOrdenCursos() const;
  bool intentarAsignacion(const Asignacion &asignacion,
                     std::vector<Asignacion> &asignaciones);
  void actualizarProgreso(int actual, int total, const std::string &mensaje);
};

} // namespace planificador

#endif // PLANIFICADOR_HPP
