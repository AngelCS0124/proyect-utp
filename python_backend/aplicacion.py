"""
API REST Flask para Sistema de Horarios UTP
Arquitectura modular con separación de responsabilidades
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename

# Importar desde estructura modular en español
from modelos import Curso, Profesor, BloqueTiempo, Horario
from data import get_all_courses, get_courses_for_cycle, get_available_cycles
from cargador_datos import CargadorDatos
from validadores import Validador
from configuracion.bloques_tiempo import obtener_bloques_semanales
from servicios import (
    obtener_bloques_dobles, 
    obtener_opciones_bloques_dobles, 
    generar_datos_visualizacion
)
from servicios.extractor_excel import extraer_datos_excel_a_memoria

# Intento de importar el scheduler C++ (fallará si no está construido)
try:
    from scheduler_wrapper import PyScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("ADVERTENCIA: Módulo C++ scheduler_wrapper no encontrado. Usando implementación Python (más lenta).")

# Inicialización de la aplicación
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de carga de archivos
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'utp_scheduler_uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16MB

# Almacenamiento de datos en memoria
almacen_datos = {
    'cursos': [],  # Se poblará basado en el ciclo seleccionado
    'profesores': [],
    'bloques_tiempo': [],
    'horario': None,
    'ciclo_actual': None
}

# Inicializar bloques de tiempo predefinidos
def inicializar_bloques_tiempo():
    """Inicializar bloques de tiempo válidos predefinidos para el horario"""
    dicts_bloques = obtener_bloques_semanales(language='es')
    almacen_datos['bloques_tiempo'] = [
        BloqueTiempo(
            id=ts['id'],
            dia=ts['day'],
            hora_inicio=ts['start_hour'],
            minuto_inicio=ts['start_minute'],
            hora_fin=ts['end_hour'],
            minuto_fin=ts['end_minute']
        ) for ts in dicts_bloques
    ]

# Cargar bloques por defecto al inicio
inicializar_bloques_tiempo()

def archivo_permitido(nombre_archivo):
    return '.' in nombre_archivo and \
           nombre_archivo.rsplit('.', 1)[1].lower() in {'csv', 'json', 'xlsx', 'xls'}


# ==========================================
# Rutas API (Endpoints en Inglés para Compatibilidad)
# ==========================================

@app.route('/')
def index():
    """Servir la página principal"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status', methods=['GET'])
def obtener_estado():
    """Obtener estado del sistema"""
    return jsonify({
        'scheduler_available': SCHEDULER_AVAILABLE,
        'data_loaded': {
            'courses': len(almacen_datos['cursos']) > 0,
            'professors': len(almacen_datos['profesores']) > 0,
            'timeslots': len(almacen_datos['bloques_tiempo']) > 0,
            'schedule': almacen_datos['horario'] is not None
        },
        'counts': {
            'courses': len(almacen_datos['cursos']),
            'professors': len(almacen_datos['profesores']),
            'timeslots': len(almacen_datos['bloques_tiempo'])
        },
        'current_cycle': almacen_datos['ciclo_actual']
    })

@app.route('/api/upload', methods=['POST'])
def subir_archivo():
    """Subir y procesar archivos de datos (profesores y bloques solamente)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    archivo = request.files['file']
    tipo_dato = request.form.get('type')  # 'professors', 'timeslots'
    
    if archivo.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if archivo and archivo_permitido(archivo.filename):
        nombre_archivo = secure_filename(archivo.filename)
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo.save(ruta_archivo)
        
        try:
            # Mapeo de tipos de datos (inglés -> español)
            mapa_tipos = {
                'professors': 'profesores',
                'timeslots': 'bloques',
                'courses': 'cursos',
                'profesores': 'profesores',
                'bloques': 'bloques',
                'cursos': 'cursos'
            }
            
            tipo_interno = mapa_tipos.get(tipo_dato)
            
            if not tipo_interno:
                return jsonify({'error': f'Invalid data type: {tipo_dato}'}), 400
            
            # Cargar datos usando el nuevo cargador en español
            datos = CargadorDatos.cargar_datos(ruta_archivo, tipo_interno)
            
            # Actualizar almacén de datos (mapa interno)
            if tipo_interno == 'cursos':
                almacen_datos['cursos'] = datos
            elif tipo_interno == 'profesores':
                almacen_datos['profesores'] = datos
            elif 'bloques' in tipo_interno:
                almacen_datos['bloques_tiempo'] = datos
            
            return jsonify({
                'message': f'Successfully loaded {len(datos)} {tipo_dato}',
                'count': len(datos)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/upload-excel', methods=['POST'])
def subir_excel():
    """Subir y procesar excel formato específico (Matriz ITI)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    archivo = request.files['file']
    ciclo = request.form.get('cycle', 'Ene-Abr 2025')
    
    if archivo.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if archivo and archivo.filename.endswith(('.xlsx', '.xls')):
        nombre_archivo = secure_filename(archivo.filename)
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo.save(ruta_archivo)
        
        try:
            # Usar servicio existente (actualizaré extract_data... en futuro paso si necesario)
            # Por ahora asume que returns modelos españoles
            resultado = extract_data_from_excel_to_memory(ruta_archivo, ciclo)
            
            if 'error' in resultado:
                return jsonify({'error': resultado['error']}), 400
                
            almacen_datos['cursos'] = resultado['courses']
            almacen_datos['profesores'] = resultado['professors']
            # Mantener bloques predefinidos, no sobreescribir con excel
            
            return jsonify({
                'message': f'Successfully processed Excel for cycle {ciclo}',
                'counts': {
                    'courses': len(resultado['courses']),
                    'professors': len(resultado['professors'])
                },
                'warnings': resultado.get('warnings', [])
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file format. Please upload an Excel file.'}), 400

@app.route('/api/load-defaults', methods=['POST'])
def cargar_datos_defecto():
    """Cargar datos por defecto desde carpeta datos_muestra"""
    try:
        # Rutas a archivos de muestra traducidos
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dir_datos = os.path.join(base_dir, 'datos_muestra')
        
        # Fallback para ejecución desde raíz
        if not os.path.exists(dir_datos):
             dir_datos = os.path.join(os.getcwd(), 'datos_muestra')
        
        # Verificar que el directorio existe antes de continuar
        if not os.path.exists(dir_datos):
            return jsonify({'error': f'Directory not found: {dir_datos}'}), 500

        # Cargar cursos
        ruta_cursos = os.path.join(dir_datos, 'cursos.csv')
        if os.path.exists(ruta_cursos):
            almacen_datos['cursos'] = CargadorDatos.cargar_cursos_csv(ruta_cursos)
        else:
             print(f"Warning: cursos.csv not found at {ruta_cursos}")
        
        # Cargar profesores
        ruta_profesores = os.path.join(dir_datos, 'profesores.json')
        if os.path.exists(ruta_profesores):
            almacen_datos['profesores'] = CargadorDatos.cargar_profesores_json(ruta_profesores)
            
        # Cargar bloques (opcional, ya tenemos inicialización)
        # ruta_bloques = os.path.join(dir_datos, 'bloques_tiempo.json')
        # if os.path.exists(ruta_bloques):
        #     almacen_datos['bloques_tiempo'] = CargadorDatos.cargar_bloques_tiempo_json(ruta_bloques)
            
        return jsonify({
            'message': 'Default data loaded successfully',
            'counts': {
                'courses': len(almacen_datos['cursos']),
                'professors': len(almacen_datos['profesores']),
                'timeslots': len(almacen_datos['bloques_tiempo'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cycles', methods=['GET'])
def obtener_ciclos():
    """Obtener ciclos disponibles"""
    """Obtener ciclos disponibles"""
    # Obtener ciclos desde curriculum (tiene metadata correcta cuatrimestres)
    ciclos = get_available_cycles()
    
    # Ordenar cronológicamente: Jan, May, Sept
    order = {"jan-apr": 1, "may-aug": 2, "sept-dec": 3}
    ciclos.sort(key=lambda x: order.get(x['id'], 99))
    
    return jsonify({'cycles': ciclos})

@app.route('/api/courses/<cycle>', methods=['GET'])
def obtener_cursos_por_ciclo(cycle):
    """Obtener cursos para un ciclo específico"""
    try:
        # En esta demo, usamos curriculum.py (que ya fue actualizado en F1)
        # O extraemos de excel si ya se cargó
        
        # Simular carga desde módulo data (actualizado a español)
        # Nota: get_courses_for_cycle debería devolver objetos Curso (español)
        cursos = get_courses_for_cycle(cycle)
        almacen_datos['cursos'] = cursos
        almacen_datos['ciclo_actual'] = cycle
        
        # Convertir a dicts para JSON
        cursos_dict = [c.a_diccionario() for c in cursos]
        
        return jsonify({
            'count': len(cursos),
            'data': cursos_dict,
            'courses': cursos_dict  # Mantener por si acaso
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<data_type>', methods=['GET'])
def obtener_datos(data_type):
    """Obtener datos cargados"""
    datos = []
    if data_type == 'courses':
        datos = almacen_datos['cursos']
    elif data_type == 'professors':
        datos = almacen_datos['profesores']
    elif data_type == 'timeslots':
        datos = almacen_datos['bloques_tiempo']
    else:
        return jsonify({'error': 'Invalid data type'}), 400
        
    return jsonify({'data': [d.a_diccionario() for d in datos]})

@app.route('/api/assign-professor', methods=['POST'])
def asignar_profesor():
    """Asignar profesor a un curso"""
    data = request.json
    id_curso = int(data.get('courseId'))
    id_profesor = int(data.get('professorId'))
    
    # Buscar curso
    curso = next((c for c in almacen_datos['cursos'] if c.id == id_curso), None)
    if not curso:
        return jsonify({'error': 'Course not found'}), 404
        
    if id_profesor == -1 or id_profesor == 0:  # Desasignar
        curso.id_profesor = None
        return jsonify({'message': 'Professor unassigned', 'course': curso.a_diccionario()})
        
    # Buscar profesor
    profesor = next((p for p in almacen_datos['profesores'] if p.id == id_profesor), None)
    if not profesor:
        return jsonify({'error': 'Professor not found'}), 404
        
    curso.id_profesor = id_profesor
    return jsonify({'message': 'Professor assigned', 'course': curso.a_diccionario()})

@app.route('/api/validate', methods=['GET'])
def validar_datos():
    """Validar todos los datos cargados"""
    resultado = Validador.validar_todos_datos(
        almacen_datos['cursos'],
        almacen_datos['profesores'],
        almacen_datos['bloques_tiempo']
    )
    return jsonify(resultado)

@app.route('/api/generate', methods=['POST'])
def generar_horario_api():
    """Generar horario usando algoritmo"""
    try:
        # Validar primero
        validacion = Validador.validar_todos_datos(
            almacen_datos['cursos'],
            almacen_datos['profesores'],
            almacen_datos['bloques_tiempo']
        )
        
        if not validacion['valid']:
            return jsonify({
                'error': 'Data validation failed',
                'details': validacion['errors']
            }), 400
            
        print("Iniciando generación de horario...")
        
        # Algoritmo de backtracking (Python o C++)
        import time
        tiempo_inicio = time.time()
        
        exito = False
        nuevo_horario = Horario()
        meta = {}
        
        if SCHEDULER_AVAILABLE:
            try:
                print("Usando Scheduler C++ Optimizado...")
                scheduler = PyScheduler()
                scheduler.reset()
                
                # 1. Cargar Bloques de Tiempo
                for b in almacen_datos['bloques_tiempo']:
                    scheduler.load_timeslot(
                        b.id, b.dia, b.hora_inicio, b.minuto_inicio, b.hora_fin, b.minuto_fin
                    )
                
                # 2. Cargar Profesores
                for p in almacen_datos['profesores']:
                    scheduler.load_professor(p.id, p.nombre, p.bloques_disponibles)
                
                # 3. Cargar Cursos y Asignaciones
                for c in almacen_datos['cursos']:
                    scheduler.load_course(
                        c.id, c.nombre, c.matricula, c.prerequisitos
                    )
                    # Asignar profesor si ya está definido
                    if c.id_profesor:
                        scheduler.assign_professor_to_course(c.id, c.id_profesor)
                
                # 4. Generar Horario
                resultado = scheduler.generate_schedule()
                exito = resultado['success']
                
                if exito:
                    # Convertir asignaciones a estructura Python Horario
                    from modelos import Asignacion
                    
                    for asig_data in resultado['assignments']:
                        # Buscar objetos completos para la asignación
                        curso_obj = next((c for c in almacen_datos['cursos'] if c.id == asig_data['course_id']), None)
                        bloque_obj = next((b for b in almacen_datos['bloques_tiempo'] if b.id == asig_data['timeslot_id']), None)
                        
                        if curso_obj and bloque_obj:
                            asignacion = Asignacion(
                                curso=curso_obj,
                                bloque=bloque_obj,
                                id_profesor=asig_data['professor_id']
                            )
                            nuevo_horario.agregar_asignacion(asignacion)
                    
                    print(f"Horario generado con éxito: {len(nuevo_horario.asignaciones)} asignaciones")
                else:
                    print(f"Fallo al generar horario: {resultado.get('error_message')}")
                
                tiempo_fin = time.time()
                meta = {
                    'computation_time': tiempo_fin - tiempo_inicio,
                    'backtrack_count': resultado['backtrack_count'],
                    'solutions_found': 1 if exito else 0
                }
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error crítico en C++ Scheduler: {e}")
                exito = False
        else:
            # Fallback Python (Simplificado para esta demo)
            print("C++ Scheduler no disponible. Usando Mock.")
            exito = False # Mock falla por defecto para obligar a usar C++
            meta = {'computation_time': 0, 'backtrack_count': 0}
        
        almacen_datos['horario'] = nuevo_horario if exito else None
        
        return jsonify({
            'success': exito,
            'schedule': nuevo_horario.a_diccionario() if exito else None,
            'metadata': meta,
            'error': resultado.get('error_message') if 'resultado' in locals() and not exito else 'Generación fallida'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/professors', methods=['POST'])
def agregar_profesor():
    data = request.json
    try:
        nuevo_id = max([p.id for p in almacen_datos['profesores']], default=0) + 1
        profesor = Profesor(
            id=nuevo_id,
            nombre=data['name'],
            email=data.get('email', ''),
            bloques_disponibles=data.get('available_timeslots', [])
        )
        almacen_datos['profesores'].append(profesor)
        return jsonify(profesor.a_diccionario())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/professors/<int:id>', methods=['PUT'])
def actualizar_profesor(id):
    data = request.json
    profesor = next((p for p in almacen_datos['profesores'] if p.id == id), None)
    if not profesor:
        return jsonify({'error': 'Professor not found'}), 404
    
    profesor.nombre = data.get('name', profesor.nombre)
    profesor.email = data.get('email', profesor.email)
    return jsonify(profesor.a_diccionario())

@app.route('/api/professors/<int:id>', methods=['DELETE'])
def eliminar_profesor(id):
    almacen_datos['profesores'] = [p for p in almacen_datos['profesores'] if p.id != id]
    # Desasignar cursos
    for curso in almacen_datos['cursos']:
        if curso.id_profesor == id:
            curso.id_profesor = None
    return jsonify({'success': True})

@app.route('/api/professors/<int:id>/availability', methods=['POST'])
def actualizar_disponibilidad(id):
    data = request.json
    profesor = next((p for p in almacen_datos['profesores'] if p.id == id), None)
    if not profesor:
        return jsonify({'error': 'Professor not found'}), 404
        
    profesor.bloques_disponibles = data.get('timeslots', [])
    return jsonify(profesor.a_diccionario())

if __name__ == '__main__':
    print("=" * 60)
    print("Sistema de Horarios UTP - Servidor Flask (ESPAÑOL)")
    print("=" * 60)
    print(f"Scheduler Disponible: {SCHEDULER_AVAILABLE}")
    print("\nIniciando servidor en http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
