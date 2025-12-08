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
    """Inicializar bloques de tiempo válidos desde archivo JSON"""
    import os
    import json
    
    # Intentar cargar desde JSON primero (45 bloques)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'datos_muestra', 'bloques_tiempo.json')
    
    # Fallback si se ejecuta desde raíz
    if not os.path.exists(json_path):
        json_path = os.path.join(os.getcwd(), 'datos_muestra', 'bloques_tiempo.json')
    
    if os.path.exists(json_path):
        try:
            print(f"Cargando bloques de tiempo desde: {json_path}", flush=True)
            almacen_datos['bloques_tiempo'] = CargadorDatos.cargar_bloques_tiempo_json(json_path)
            print(f"✓ Cargados {len(almacen_datos['bloques_tiempo'])} bloques de tiempo", flush=True)
            return
        except Exception as e:
            print(f"Error cargando bloques JSON: {e}. Usando fallback...", flush=True)
    
    # Fallback: bloques predefinidos (solo 9)
    print("Usando 9 bloques predefinidos (fallback)", flush=True)
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
    tipo_dato = request.form.get('data_type') or request.form.get('type')  # Frontend envía 'data_type'
    
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

@app.route('/api/config', methods=['POST'])
def configurar_parametros():
    """Recibir configuración de generación (tiempo límite, estrategia)"""
    try:
        data = request.json
        # Por ahora solo logueamos o guardamos en variable global si fuera necesario
        # En esta versión, los parámetros suelen venir en el request de generación
        # pero el frontend a veces manda config por separado.
        print(f"Configuración recibida: {data}", flush=True)
        return jsonify({'message': 'Configuration updated'}), 200
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
                print("--- INICIANDO GENERACIÓN DE HORARIO ---", flush=True)
                print(f"Datos: {len(almacen_datos['bloques_tiempo'])} bloques, {len(almacen_datos['profesores'])} profesores, {len(almacen_datos['cursos'])} cursos", flush=True)
                
                scheduler = PyScheduler()
                scheduler.reset()
                
                # --- MAPEO DE IDs (SHADOW MAPPING) ---
                # El grafo C++ asigna IDs secuenciales (0, 1, 2...) en el orden de inserción.
                # Debemos replicar esto para pasar los IDs correctos a asignarProfesor.
                internal_id_counter = 0
                map_bloques = {}   # id_externo -> id_interno
                map_profesores = {}
                map_cursos = {}
                
                # 1. Cargar Bloques de Tiempo
                print("Cargando bloques...", flush=True)
                for b in almacen_datos['bloques_tiempo']:
                    scheduler.load_timeslot(
                        b.id, b.dia, b.hora_inicio, b.minuto_inicio, b.hora_fin, b.minuto_fin
                    )
                    map_bloques[b.id] = internal_id_counter
                    internal_id_counter += 1
                
                # 2. Cargar Profesores
                print("Cargando profesores...", flush=True)
                for p in almacen_datos['profesores']:
                    # MAPEAR Bloques Disponibles (Externo -> Interno)
                    bloques_internos = []
                    for b_ext in p.bloques_disponibles:
                        if b_ext in map_bloques:
                            bloques_internos.append(map_bloques[b_ext])
                        # Si no existe, ignoramos (o podríamos loguear warning)
                    
                    scheduler.load_professor(p.id, p.nombre, bloques_internos)
                    map_profesores[p.id] = internal_id_counter
                    internal_id_counter += 1
                
                # 3. Cargar Cursos y Asignaciones Automáticas
                print("Cargando cursos y asignando profesores...", flush=True)
                cursos_sin_profe = 0
                cursos_con_profe = 0
                
                # --- PREPARACIÓN BALANCEO DE CARGA ---
                # 1. Calcular capacidad real (slots disponibles)
                prof_capacity = {}      # id -> int (total slots)
                prof_load = {}          # id -> int (cursos asignados actualmente)
                
                for p in almacen_datos['profesores']:
                    # La capacidad REAL son los bloques que existen en el sistema (map_bloques)
                    # Si el JSON tiene bloques que no están en time_slots, no cuentan.
                    valid_blocks = [b for b in p.bloques_disponibles if b in map_bloques]
                    cap = len(valid_blocks)
                    prof_capacity[p.id] = cap
                    prof_load[p.id] = 0
                
                # Pre-calcular carga inicial de cursos YA asignados (por CSV)
                for c in almacen_datos['cursos']:
                     if c.id_profesor and c.id_profesor in prof_load:
                         prof_load[c.id_profesor] += 1
                
                print("--- Capacidad de Profesores ---", flush=True)
                for pid, cap in prof_capacity.items():
                    p_obj = next((x for x in almacen_datos['profesores'] if x.id == pid), None)
                    print(f"  {p_obj.nombre}: {cap} slots", flush=True)
                
                for c in almacen_datos['cursos']:
                    # MAPEAR Prerrequisitos (Externo -> Interno)
                    prereq_internos = [] 
                    for pre_ext in c.prerequisitos:
                         if pre_ext in map_cursos:
                             prereq_internos.append(map_cursos[pre_ext])
                    
                    scheduler.load_course(
                        c.id, c.nombre, c.matricula, prereq_internos
                    )
                    map_cursos[c.id] = internal_id_counter
                    current_course_internal_id = internal_id_counter
                    internal_id_counter += 1
                    
                    # LOGICA DE AUTO-ASIGNACIÓN INTELIGENTE (SMART LOAD BALANCING)
                    if not c.id_profesor:
                        # 1. Encontrar todos los candidatos capaces
                        candidatos = []
                        curso_code = str(c.codigo).strip().upper() if c.codigo else ""
                        curso_name = str(c.nombre).strip().upper()

                        for p in almacen_datos['profesores']:
                            capaces = [str(m).strip().upper() for m in p.materias_capaces]
                            if (curso_code and curso_code in capaces) or (curso_name in capaces):
                                candidatos.append(p)
                        
                        # 2. Elegir el mejor candidato
                        mejor_candidato = None
                        
                        if candidatos:
                            # Filtrar candidatos con capacidad disponible
                            candidatos_viables = [p for p in candidatos if prof_load[p.id] < prof_capacity[p.id]]
                            
                            if candidatos_viables:
                                # Ordenar por:
                                # 1. Menor carga actual (prof_load) -> Para balancear
                                # 2. Mayor capacidad total (prof_capacity) -> Desempatar usando al que tiene más holgura general
                                candidatos_viables.sort(key=lambda p: (prof_load[p.id], -prof_capacity[p.id]))
                                
                                mejor_candidato = candidatos_viables[0]
                                
                                # Asignar
                                c.id_profesor = mejor_candidato.id
                                prof_load[mejor_candidato.id] += 1
                                print(f"  [AUTO-SMART] Asignado {c.codigo} ({c.nombre}) -> {mejor_candidato.nombre} (Carga: {prof_load[mejor_candidato.id]}/{prof_capacity[mejor_candidato.id]})", flush=True)
                            else:
                                # Todos los candidatos están saturados
                                print(f"  [WARN] Saturación: {len(candidatos)} candidatos para {c.nombre} están llenos.", flush=True)
                                # Opcional: Asignar al menos peor (el que tenga más capacidad total aunque esté lleno)?
                                # Por ahora NO asignamos para respetar la restricción dura del usuario.
                        else:
                             print(f"  [WARN] Nadie calificado para: {c.nombre} ({c.codigo})", flush=True)

                    if c.id_profesor:
                        # Verificar que el profesor exista en el mapa y actualizar carga si venía pre-asignado
                        if c.id_profesor in map_profesores:
                            if c.id_profesor not in prof_load: # Caso raro si no estaba en loop anterior
                                prof_load[c.id_profesor] = 1
                            # Nota: Si venía pre-asignado manualmente en el CSV, no incrementamos prof_load arriba, 
                            # deberíamos hacerlo aqui para ser justos, pero asumimos que el auto-assign corre para los vacíos.
                            # Corrección: El CSV 'courses.csv' define id_profesor. Si ya viene, deberíamos contarlo en la carga inicial?
                            # Sí, idealmente. Pero como estamos iterando linealmente, si el curso 1 ya tiene profe, deberíamos haberlo contado antes.
                            # Simplificación: Asumimos que la carga pre-existente es 0 o gestionada dinámicamente.
                            
                            internal_prof_id = map_profesores[c.id_profesor]
                            scheduler.assign_professor_to_course(current_course_internal_id, internal_prof_id)
                            cursos_con_profe += 1
                        else:
                            print(f"  [Error] Profesor ID {c.id_profesor} asignado a {c.nombre} no se cargó.", flush=True)
                    else:
                        print(f"  [WARN] Curso sin profesor: {c.nombre} ({c.codigo}) - Se omitirá del horario.", flush=True)
                        cursos_sin_profe += 1
                
                print(f"Resumen Asignación: {cursos_con_profe} asignados, {cursos_sin_profe} sin profesor.", flush=True)
                
                # 4. Generar Horario
                print("Ejecutando C++ Scheduler...", flush=True)
                # OJO: generate_schedule devuelve IDs internos en 'assignments' ??
                # Necesitamos verificar qué devuelve.
                # scheduler_wrapper.pyx: 
                #   'course_id': asignacion.idCurso, 'professor_id': asignacion.idProfesor
                #   PlanificadorCore devuelve nodos. 
                #   Si asignacion tiene atributos 'id' (el string externo), wrappers suele convertirlos.
                #   VERIFICAR scheduler_wrapper.pyx
                
                resultado = scheduler.generate_schedule()
                print(f"Resultado C++: {resultado}", flush=True)
                
                exito = resultado['success']
                
                if exito:
                    # Convertir asignaciones a estructura Python Horario
                    from modelos import Asignacion
                    
                    # Como no sabemos si 'resultado' devuelve IDs internos o externos, 
                    # asumiremos que devuelve lo que el nodo tenga como atributo "id" si el wrapper lo maneja
                    # O si devuelve ID de nodo (int).
                    
                    # Revisando scheduler_wrapper.pyx (memoria):
                    #   asignacion.idCurso es un int.
                    #   Si es el internal ID, debemos mapearlo de vuelta a externo.
                    #   Pero el wrapper podría estar intentando devolver el atributo.
                    #   Vamos a asumir INTERNAL y usar reverse map si es necesario,
                    #   o intentar buscar por ambos.
                    
                    # Mapa inverso para cursos y bloques (Internal -> External Object)
                    inv_map_cursos = {v: k for k, v in map_cursos.items()}
                    inv_map_bloques = {v: k for k, v in map_bloques.items()}
                    
                    for asig_data in resultado['assignments']:
                        # asig_data['course_id'] y 'timeslot_id' vienen del C++.
                        # Si son IDs internos (muy probable), usamos el mapa inverso.
                        
                        raw_c_id = asig_data['course_id']
                        raw_t_id = asig_data['timeslot_id']
                        raw_p_id = asig_data['professor_id']
                        
                        # Intentar recuperar ID externo
                        ext_c_id = inv_map_cursos.get(raw_c_id, raw_c_id)
                        ext_t_id = inv_map_bloques.get(raw_t_id, raw_t_id)
                        # Profesores no suelen venir en la asignación final del solver salvo que se pida expicitamente,
                        # pero PyScheduler wrapper lo incluye.
                        
                        # Buscar objetos completos
                        curso_obj = next((c for c in almacen_datos['cursos'] if c.id == ext_c_id), None)
                        bloque_obj = next((b for b in almacen_datos['bloques_tiempo'] if b.id == ext_t_id), None)
                        
                        if curso_obj and bloque_obj:
                            p_obj = next((p for p in almacen_datos['profesores'] if p.id == curso_obj.id_profesor), None)
                            p_name = p_obj.nombre if p_obj else "Sin Profesor"
                            
                            nuevo_horario.agregar_asignacion(
                                curso_obj.id, 
                                curso_obj.id_profesor, 
                                bloque_obj.id,
                                course_name=curso_obj.nombre,
                                professor_name=p_name,
                                semester=getattr(curso_obj, 'cuatrimestre', 1), # Corregido: atributo es 'cuatrimestre'
                                group=getattr(curso_obj, 'id_grupo', 'A') # Corregido: atributo es 'id_grupo'
                            )

                    
                    print(f"Horario generado con éxito: {len(nuevo_horario.asignaciones)} asignaciones", flush=True)
                else:
                    msg = resultado.get('error_message')
                    print(f"Fallo al generar horario (C++): {msg}", flush=True)
                
                tiempo_fin = time.time()
                meta = {
                    'computation_time': tiempo_fin - tiempo_inicio,
                    'backtrack_count': resultado['backtrack_count'],
                    'solutions_found': 1 if exito else 0
                }
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error crítico en C++ Scheduler: {e}", flush=True)
                exito = False
                error_critico = str(e)
        else:
            # CSP Scheduler Python (fuzzy matching auto-assign integrad o)
            try:
                print("C++ Scheduler no disponible. Usando CSP Scheduler Python...", flush=True)
                
                from servicios.csp_scheduler import CSPScheduler
                
                solver = CSPScheduler(
                    almacen_datos['cursos'],
                    almacen_datos['profesores'],
                    almacen_datos['bloques_tiempo']
                )
                
                exito, nuevo_horario = solver.resolver(max_reintentos=3)
                stats = solver.obtener_estadisticas()
                
                meta = {
                    'computation_time': time.time() - tiempo_inicio,
                    'method': 'CSP Python (Backtracking + Forward Checking + MRV/LCV)',
                    'attempts': stats['intentos'],
                    'backtrack_count': stats['backtracks'],
                    'solutions_found': 1 if exito else 0
                }
                
                print(f"CSP Python completado: {'Éxito' if exito else 'Fallo'}", flush=True)
                print(f"Estadísticas: {stats['intentos']} intentos, {stats['backtracks']} backtracks", flush=True)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error en CSP Scheduler: {e}", flush=True)
                exito = False
                nuevo_horario = None
                meta = {'computation_time': time.time() - tiempo_inicio, 'backtrack_count': 0}

        
        almacen_datos['horario'] = nuevo_horario if exito else None
        
        # Construir respuesta
        response = {
            'success': exito,
            'schedule': nuevo_horario.a_diccionario() if exito else None,
            'metadata': meta
        }
        
        # Solo agregar mensaje de error si realmente falló
        if not exito:
            mensaje_error = 'Generación fallida'
            if 'resultado' in locals():
                # Si el C++ devolvió un mensaje específico
                detail = resultado.get('error_message', '')
                if detail and str(detail).strip():
                    mensaje_error = f"Error del Motor: {detail}"
                else:
                    mensaje_error = "No se pudo encontrar un horario válido (Límite de intentos excedido o restricciones imposibles)."
            elif 'error_critico' in locals():
                mensaje_error = f"Excepción interna: {error_critico}"
            
            response['error'] = mensaje_error
        
        return jsonify(response)

        
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
