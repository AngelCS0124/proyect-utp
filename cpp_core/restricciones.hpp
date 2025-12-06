#ifndef RESTRICCIONES_HPP
#define RESTRICCIONES_HPP

#include "grafo.hpp"
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace planificador {

// Representación de bloque de tiempo
struct BloqueTiempo {
  int id;
  std::string dia;
  int horaInicio;
  int minutoInicio;
  int horaFin;
  int minutoFin;

  BloqueTiempo();
  BloqueTiempo(int id, const std::string &dia, int horaInicio, int minutoInicio,
           int horaFin, int minutoFin);

  bool seSolapa(const BloqueTiempo &otro) const;
  std::string aString() const;
};

// Asignación de curso (curso -> bloque, profesor)
struct Asignacion {
  int idCurso;
  int idBloque;
  int idProfesor;

  Asignacion(int idCurso = -1, int idBloque = -1, int idProfesor = -1);
};

// Verificador de restricciones
class VerificadorRestricciones {
private:
  const Grafo &grafo;
  std::unordered_map<int, BloqueTiempo> bloquesTiempo;
  std::unordered_map<int, std::unordered_set<int>>
      disponibilidadProfesor; // idProfesor -> set(idBloque)
  std::unordered_map<int, std::unordered_set<int>>
      prerrequisitosCurso; // idCurso -> set(idPrerrequisito)
  std::unordered_map<int, int> gruposCurso; // idCurso -> idGrupo

public:
  VerificadorRestricciones(const Grafo &grafo);

  // Configuración de datos
  void agregarBloqueTiempo(const BloqueTiempo &bloque);
  void agregarDisponibilidadProfesor(int idProfesor, int idBloque);
  void agregarPrerrequisitoCurso(int idCurso, int idPrerrequisito);
  void agregarGrupoCurso(int idCurso, int idGrupo);

  // Validación de restricciones
  bool
  esAsignacionValida(const Asignacion &asignacion,
                    const std::vector<Asignacion> &asignacionesExistentes) const;

  bool verificarConflictoTiempo(int idProfesor, int idBloque,
                         const std::vector<Asignacion> &asignaciones) const;

  bool verificarConflictoGrupo(int idCurso, int idBloque,
                          const std::vector<Asignacion> &asignaciones) const;

  bool verificarDisponibilidadProfesor(int idProfesor, int idBloque) const;

  bool verificarPrerrequisitos(int idCurso,
                          const std::vector<Asignacion> &asignaciones) const;

  // Obtener opciones disponibles
  std::vector<int>
  obtenerBloquesDisponibles(int idCurso, int idProfesor,
                        const std::vector<Asignacion> &asignaciones) const;

  int obtenerSiguienteBloqueConsecutivo(int idBloque) const;

  // Mensajes de validación
  std::string
  obtenerMensajeViolacion(const Asignacion &asignacion,
                      const std::vector<Asignacion> &asignaciones) const;
};

} // namespace planificador

#endif // RESTRICCIONES_HPP
