# distutils: language = c++
# cython: language_level = 3

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool

# Declaraciones C++ (Traducidas)
cdef extern from "planificador.hpp" namespace "planificador":
    cdef cppclass Asignacion:
        int idCurso
        int idBloque
        int idProfesor
        
        Asignacion() except +
        Asignacion(int, int, int) except +
    
    cdef cppclass ResultadoHorario:
        bool exito
        vector[Asignacion] asignaciones
        string mensajeError
        int conteoBacktrack
        double tiempoComputo
        
        ResultadoHorario() except +
    
    cdef cppclass PlanificadorCore:
        PlanificadorCore() except +
        
        void cargarCurso(int id, const string& nombre, int matricula,
                       const vector[int]& prerrequisitos, int idGrupo, int duracion) except +
        void cargarProfesor(int id, const string& nombre,
                          const vector[int]& bloquesDisponibles) except +
        void cargarBloqueTiempo(int id, const string& dia, int horaInicio, int minutoInicio,
                         int horaFin, int minutoFin) except +
        
        void asignarProfesorACurso(int idCurso, int idProfesor) except +
        
        ResultadoHorario generarHorario(int limiteTiempoSegundos, bool modoCompleto) except +
        void detenerGeneracion() except +
        void reiniciar() except +
        
        bool tieneDatos() const
        string validarDatos() const


# Clase Wrapper en Python
# Mantenemos nombres de métodos de Python para compatibilidad con backend existente
cdef class PyScheduler:
    cdef PlanificadorCore* scheduler
    
    def __cinit__(self):
        self.scheduler = new PlanificadorCore()
    
    def __dealloc__(self):
        if self.scheduler != NULL:
            del self.scheduler
    
    def load_course(self, int course_id, str name, int enrollment, list prerequisites=None, int group_id=0, int duration=1):
        """Cargar curso en el planificador"""
        cdef vector[int] prereq_vec
        if prerequisites:
            for p in prerequisites:
                prereq_vec.push_back(p)
        
        self.scheduler.cargarCurso(course_id, name.encode('utf-8'), enrollment, prereq_vec, group_id, duration)
    
    def load_professor(self, int prof_id, str name, list available_timeslots):
        """Cargar profesor con horarios disponibles"""
        cdef vector[int] timeslot_vec
        for ts in available_timeslots:
            timeslot_vec.push_back(ts)
        
        self.scheduler.cargarProfesor(prof_id, name.encode('utf-8'), timeslot_vec)
    
    def load_timeslot(self, int slot_id, str day, int start_hour, int start_minute,
                     int end_hour, int end_minute):
        """Cargar bloque de tiempo"""
        self.scheduler.cargarBloqueTiempo(slot_id, day.encode('utf-8'), 
                                    start_hour, start_minute, end_hour, end_minute)
    
    def assign_professor_to_course(self, int course_id, int professor_id):
        """Asignar profesor a curso"""
        self.scheduler.asignarProfesorACurso(course_id, professor_id)
    
    def generate_schedule(self):
        """Generar horario usando algoritmo"""
        cdef ResultadoHorario resultado = self.scheduler.generarHorario(0, False)
        
        # Convertir a dict Python
        py_result = {
            'success': resultado.exito,
            'error_message': resultado.mensajeError.decode('utf-8'),
            'backtrack_count': resultado.conteoBacktrack,
            'computation_time': resultado.tiempoComputo,
            'assignments': []
        }
        
        # Convertir asignaciones
        for asignacion in resultado.asignaciones:
            py_result['assignments'].append({
                'course_id': asignacion.idCurso,
                'timeslot_id': asignacion.idBloque,
                'professor_id': asignacion.idProfesor
            })
        
        return py_result

    def generate_schedule_with_config(self, int time_limit_seconds=0, str strategy="time_limit"):
        """Generar horario con configuración"""
        cdef bool modo_completo = (strategy == "complete")
        cdef ResultadoHorario resultado = self.scheduler.generarHorario(time_limit_seconds, modo_completo)
        
        # Convertir a dict Python
        py_result = {
            'success': resultado.exito,
            'error_message': resultado.mensajeError.decode('utf-8'),
            'backtrack_count': resultado.conteoBacktrack,
            'computation_time': resultado.tiempoComputo,
            'assignments': []
        }
        
        # Convertir asignaciones
        for asignacion in resultado.asignaciones:
            py_result['assignments'].append({
                'course_id': asignacion.idCurso,
                'timeslot_id': asignacion.idBloque,
                'professor_id': asignacion.idProfesor
            })
            
        return py_result
    
    def stop_generation(self):
        """Detener generación"""
        self.scheduler.detenerGeneracion()
    
    def reset(self):
        """Reiniciar planificador"""
        self.scheduler.reiniciar()
    
    def has_data(self):
        """Verificar si hay datos cargados"""
        return self.scheduler.tieneDatos()
    
    def validate_data(self):
        """Validar datos cargados"""
        return self.scheduler.validarDatos().decode('utf-8')
