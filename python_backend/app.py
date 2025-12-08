"""
Flask REST API for UTP Scheduling System
Modular architecture with separated concerns
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename

# Importar desde estructura modular
from modelos import Curso, Profesor, BloqueTiempo, Horario
from data import get_all_courses, get_courses_for_cycle, get_available_cycles
from data_loader import DataLoader
from validadores import Validador
from config.periods import PERIODOS, get_valid_semesters, get_valid_groups

# Try to import the C++ scheduler (will fail if not built yet)
try:
    from scheduler_wrapper import PyScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("WARNING: C++ scheduler not available. Please build the Cython extension first.")

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global data storage
data_store = {
    'courses': [],  # Will be populated based on selected cycle
    'professors': [],
    'timeslots': [],
    'schedule': None,
    'current_cycle': None,  # Track currently selected cycle
    'config': {
        'period': 'sept-dec', # Default period
        'time_limit': 30,    # Default time limit in seconds
        'strategy': 'time_limit' # Default strategy
    }
}

# Initialize predefined timeslots
def initialize_timeslots():
    """Initialize valid predefined timeslots for the schedule"""
    from configuracion.bloques_tiempo import obtener_bloques_semanales
    timeslot_dicts = obtener_bloques_semanales(language='es')
    data_store['timeslots'] = [
        BloqueTiempo(
            id=ts['id'],
            dia=ts['day'],
            hora_inicio=ts['start_hour'],
            minuto_inicio=ts['start_minute'],
            hora_fin=ts['end_hour'],
            minuto_fin=ts['end_minute']
        ) for ts in timeslot_dicts
    ]

# Load default timeslots on app startup
initialize_timeslots()

def load_initial_data():
    """Load default data on startup"""
    print("Loading default data...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    
    # Load courses
    courses_path = os.path.join(base_dir, 'courses_full.csv')
    if os.path.exists(courses_path):
        try:
            courses = DataLoader.load_courses_from_csv(courses_path)
            data_store['courses'] = courses
            print(f"Loaded {len(courses)} courses from {courses_path}")
        except Exception as e:
            print(f"Error loading courses: {e}")
            
    # Load professors
    professors_path = os.path.join(root_dir, 'sample_data', 'professors.json')
    if os.path.exists(professors_path):
        try:
            result = DataLoader.load_professors_from_json(professors_path)
            if isinstance(result, dict):
                data_store['professors'] = result['professors']
                if result.get('timeslots'):
                     # Merge or overwrite timeslots? Let's overwrite if we have them
                     data_store['timeslots'] = result['timeslots']
            else:
                data_store['professors'] = result
            print(f"Loaded {len(data_store['professors'])} professors from {professors_path}")
        except Exception as e:
            print(f"Error loading professors: {e}")

    # Load timeslots if not loaded from professors file
    if not data_store['timeslots']:
        timeslots_path = os.path.join(root_dir, 'sample_data', 'timeslots.json')
        if os.path.exists(timeslots_path):
            try:
                data_store['timeslots'] = DataLoader.load_timeslots_from_json(timeslots_path)
                print(f"Loaded {len(data_store['timeslots'])} timeslots from {timeslots_path}")
            except Exception as e:
                print(f"Error loading timeslots: {e}")

# Load data on startup
load_initial_data()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'scheduler_available': SCHEDULER_AVAILABLE,
        'data_loaded': {
            'courses': len(data_store['courses']),
            'professors': len(data_store['professors']),
            'timeslots': len(data_store['timeslots'])
        },
        'schedule_generated': data_store['schedule'] is not None,
        'current_cycle': data_store['current_cycle'],
        'config': data_store['config']
    })


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update system configuration"""
    data = request.json
    
    if 'period' in data:
        if data['period'] not in PERIODOS:
            return jsonify({'error': 'Invalid period'}), 400
        data_store['config']['period'] = data['period']
        
        # If courses are loaded, we might need to reload/filter them
        # For now, we'll just update the config. The filtering happens at generation time
        # or when loading courses.
        
    if 'time_limit' in data:
        try:
            limit = int(data['time_limit'])
            # If limit is 0 or negative, treat as "No Limit" (set to 1 hour)
            if limit <= 0:
                limit = 3600
            data_store['config']['time_limit'] = limit
        except ValueError:
            return jsonify({'error': 'Invalid time limit'}), 400
            
    if 'strategy' in data:
        if data['strategy'] not in ['complete', 'time_limit']:
            return jsonify({'error': 'Invalid strategy'}), 400
        data_store['config']['strategy'] = data['strategy']
        
    return jsonify({
        'success': True,
        'config': data_store['config'],
        'message': 'Configuration updated'
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process data files (professors and timeslots only)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    data_type = request.form.get('data_type')
    
    # Allow professors, timeslots, and courses
    if not data_type or data_type not in ['professors', 'timeslots', 'courses']:
        return jsonify({'error': 'Invalid data_type. Must be: professors, timeslots, or courses'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Allowed: CSV, JSON, Excel'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load data
        loaded_result = DataLoader.load_data(filepath, data_type)
        
        loaded_data = []
        warnings = []
        
        # Handle combined result (dict) or simple list
        if isinstance(loaded_result, dict) and 'professors' in loaded_result:
            loaded_data = loaded_result['professors']
            
            # If timeslots were also loaded, update them
            if loaded_result.get('timeslots'):
                data_store['timeslots'] = loaded_result['timeslots']
                warnings.append(f"Also loaded {len(loaded_result['timeslots'])} timeslots from the file.")
        else:
            loaded_data = loaded_result
        
        # Validate data
        if data_type == 'professors':
            print(f"DEBUG: Validating professors: {len(loaded_data)}")
            validation = Validador.validar_profesores(loaded_data)
        elif data_type == 'timeslots':
            print(f"DEBUG: Validating timeslots: {len(loaded_data)}")
            validation = Validador.validar_bloques_tiempo(loaded_data)
        elif data_type == 'courses':
            print(f"DEBUG: Validating courses: {len(loaded_data)}")
            validation = Validador.validar_cursos(loaded_data)
        
        if not validation['valid']:
            print(f"DEBUG: Validation failed: {validation['errors']}")
            return jsonify({
                'error': 'Validation failed',
                'details': validation['errors']
            }), 400
        
        # Store data
        data_store[data_type] = loaded_data
        
        # Clean up temp file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Loaded {len(loaded_data)} {data_type}. ' + ' '.join(warnings),
            'count': len(loaded_data),
            'warnings': validation.get('warnings', []) + warnings
        })
    
    except Exception as e:
        print(f"DEBUG: Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload_excel', methods=['POST'])
def upload_excel():
    """Upload and process the specific Excel format (Matriz ITI)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Invalid file format. Must be Excel'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract data using the service
        from services.excel_extractor import extract_data_from_excel_to_memory
        
        # We need to modify the extractor to return data instead of writing to files
        # Or we can let it write to a temp dir and load from there
        # For now, let's assume we modify the extractor or use a temp dir
        
        temp_output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_data')
        success = extract_data_from_excel_to_memory(filepath, data_store)
        
        # Clean up
        os.remove(filepath)
        
        if success:
            return jsonify({
                'success': True,
                'message': f"Loaded {len(data_store['professors'])} professors and {len(data_store['courses'])} courses",
                'counts': {
                    'professors': len(data_store['professors']),
                    'courses': len(data_store['courses'])
                }
            })
        else:
            return jsonify({'error': 'Failed to extract data from Excel'}), 500
            
    except Exception as e:
        print(f"DEBUG: Excel upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/load_defaults', methods=['POST'])
def load_defaults():
    """Load default data from sample Excel file"""
    try:
        sample_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'Horarios EneAbr18(1).xlsx')
        
        if not os.path.exists(sample_file):
            return jsonify({'error': 'Default file not found'}), 404
            
        from services.excel_extractor import extract_data_from_excel_to_memory
        
        success = extract_data_from_excel_to_memory(sample_file, data_store)
        
        if success:
            return jsonify({
                'success': True,
                'message': f"Loaded default data: {len(data_store['professors'])} professors and {len(data_store['courses'])} courses"
            })
        else:
            return jsonify({'error': 'Failed to extract default data'}), 500
            
    except Exception as e:
        print(f"DEBUG: Load defaults error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cycles', methods=['GET'])
def get_cycles():
    """Get available cycles"""
    return jsonify({
        'cycles': get_available_cycles()
    })


@app.route('/api/courses/<cycle>', methods=['GET'])
def get_courses_by_cycle(cycle):
    """Get courses for a specific cycle"""
    try:
        # Only load from curriculum if courses are empty or user explicitly requested (we assume explicit request for now)
        # But wait, the user might want to switch cycles.
        # Let's just load it. If they want to use uploaded courses, they should upload them AFTER selecting cycle?
        # Or we can add a flag.
        # For now, let's just load it, but if they uploaded courses, they probably didn't select a cycle yet.
        # The issue is if they select a cycle, it wipes their upload.
        # Let's check if we have courses and if they look like "custom" courses (e.g. from CSV).
        # But we don't track source.
        
        courses = get_courses_for_cycle(cycle)
        data_store['courses'] = courses
        data_store['current_cycle'] = cycle
        
        # CRITICAL FIX: Sync the config period with the selected cycle
        # This ensures generate_schedule uses the correct period for filtering
        
        # Normalize cycle key for config
        mapping_es_en = {
            "Ene-Abr": "jan-apr",
            "May-Ago": "may-aug",
            "Sep-Dic": "sept-dec",
            "Sept-Dic": "sept-dec",
            "jan-apr": "jan-apr",
            "may-aug": "may-aug",
            "sept-dec": "sept-dec",
            "sep_dic": "sept-dec", # Handle old key just in case
            "ene_abr": "jan-apr",
            "may_ago": "may-aug"
        }
        
        normalized_cycle = mapping_es_en.get(cycle.split(' ')[0], cycle)
        
        if normalized_cycle in PERIODOS:
            data_store['config']['period'] = normalized_cycle
            print(f"DEBUG: Switched period to {normalized_cycle} (from {cycle})")
        else:
            print(f"WARNING: Cycle {cycle} (normalized: {normalized_cycle}) not found in PERIODOS keys: {list(PERIODOS.keys())}")
            
        return jsonify({
            'data': [course.to_dict() for course in courses],
            'count': len(courses),
            'cycle': cycle
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/data/<data_type>', methods=['GET'])
def get_data(data_type):
    """Get loaded data"""
    if data_type not in data_store:
        return jsonify({'error': 'Invalid data type'}), 400
    
    data = data_store[data_type]
    return jsonify({
        'data': [item.to_dict() for item in data] if data else [],
        'count': len(data)
    })


@app.route('/api/assign-professor', methods=['POST'])
def assign_professor():
    """Assign a professor to a course"""
    data = request.json
    course_id = data.get('course_id')
    professor_id = data.get('professor_id')
    
    if course_id is None or professor_id is None:
        return jsonify({'error': 'Missing course_id or professor_id'}), 400
    
    # Find course and update
    course = next((c for c in data_store['courses'] if c.id == course_id), None)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    professor = next((p for p in data_store['professors'] if p.id == professor_id), None)
    if not professor:
        return jsonify({'error': 'Professor not found'}), 404
    
    course.id_profesor = professor_id
    
    return jsonify({
        'success': True,
        'message': f'Assigned {professor.nombre} to {course.nombre}'
    })


@app.route('/api/validate', methods=['GET'])
def validate_data():
    """Validate all loaded data"""
    validation = Validador.validar_todos_datos(
        data_store['courses'],
        data_store['professors'],
        data_store['timeslots']
    )
    
    return jsonify(validation)


@app.route('/api/visualization', methods=['GET'])
def get_visualization_data():
    """Get visualization data for scheduling algorithm structures"""
    from services.visualizacion import generar_datos_visualizacion
    
    if not data_store['schedule']:
        return jsonify({'error': 'No schedule generated yet'}), 404
    
    try:
        datos_viz = generar_datos_visualizacion(
            data_store['courses'],
            data_store['professors'],
            data_store['timeslots'],
            data_store['schedule']['assignments']
        )
        
        return jsonify(datos_viz)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import threading
import time

# Global generation state
generation_state = {
    'is_running': False,
    'thread': None,
    'stop_requested': False,
    'result': None,
    'error': None,
    'current_level': 1,
    'metrics': {}
}

def run_generation_task(courses, professors, timeslots, config):
    """Background task for schedule generation with cascading fallback"""
    global generation_state
    
    try:
        generation_state['is_running'] = True
        generation_state['result'] = None
        generation_state['error'] = None
        generation_state['stop_requested'] = False
        
        # Create scheduler instance (new instance per run to avoid state issues)
        scheduler = PyScheduler()
        
        # Load data
        for course in courses:
            group_id = getattr(course, 'cuatrimestre', 1) or 1
            credits = getattr(course, 'creditos', 0)
            weekly_hours = credits / 15.0 if credits > 0 else 4.0
            import math
            duration = math.ceil(weekly_hours)
            if duration < 1: duration = 1
            
            # Pass prerequisites if available
            prereqs = getattr(course, 'prerequisitos', [])
            
            scheduler.load_course(course.id, course.nombre, course.matricula, prereqs, group_id, duration)
            
        for timeslot in timeslots:
            scheduler.load_timeslot(timeslot.id, timeslot.dia, 
                                   timeslot.hora_inicio, timeslot.minuto_inicio,
                                   timeslot.hora_fin, timeslot.minuto_fin)

        for professor in professors:
            scheduler.load_professor(professor.id, professor.nombre, professor.bloques_disponibles)
        
        # Assign professors
        for course in courses:
            if course.id_profesor is not None:
                scheduler.assign_professor_to_course(course.id, course.id_profesor)
            else:
                # Auto-assign logic (simplified)
                candidate = None
                for p in professors:
                    if hasattr(p, 'materias_capaces') and course.codigo in p.materias_capaces:
                        candidate = p
                        break
                if candidate:
                    scheduler.assign_professor_to_course(course.id, candidate.id)
                    course.id_profesor = candidate.id

        # Cascading Fallback Strategy
        time_limit = config.get('time_limit', 30)
        levels = [1, 2, 3, 4] # STRICT, RELAXED, GREEDY, EMERGENCY
        
        final_result = None
        
        for level in levels:
            if generation_state['stop_requested']:
                break
                
            generation_state['current_level'] = level
            print(f"DEBUG: Starting generation Level {level}")
            
            # Run generation
            # We need to poll for stop request? The C++ code checks stop flag, but we need to set it.
            # We can't easily set C++ flag from here while it's running in blocking call.
            # Wait, PyScheduler.generate_schedule_with_config is blocking.
            # But we added `detenerGeneracion` in C++.
            # If `stop_requested` is set via API, we call scheduler.stop_generation() from the API thread?
            # Yes, we need to store the scheduler instance globally or pass it.
            generation_state['scheduler_instance'] = scheduler
            
            result = scheduler.generate_schedule_with_config(time_limit, level)
            
            # Update metrics
            metrics = scheduler.get_metrics()
            generation_state['metrics'] = metrics
            
            if result['success']:
                final_result = result
                print(f"DEBUG: Success at Level {level}")
                break
            elif len(result['assignments']) > 0:
                # Partial success - keep it but try next level if we want better?
                # Actually, lower levels (higher number) are easier.
                # If Level 1 fails, we try Level 2.
                # If Level 1 gives partial, is that "failure"?
                # Usually we want COMPLETE schedule.
                # If result['success'] is False, it's partial.
                # So we continue to next level to try to get full schedule (by relaxing constraints).
                # But we should keep the best partial result so far.
                if final_result is None or len(result['assignments']) > len(final_result['assignments']):
                    final_result = result
            
        if final_result:
            # Enrich assignments
            enriched_assignments = []
            for assignment in final_result['assignments']:
                course = next((c for c in courses if c.id == assignment['course_id']), None)
                professor = next((p for p in professors if p.id == assignment['professor_id']), None)
                timeslot = next((t for t in timeslots if t.id == assignment['timeslot_id']), None)
                
                enriched_assignments.append({
                    **assignment,
                    'course_name': course.nombre if course else 'Unknown',
                    'course_code': course.codigo if course else '',
                    'professor_name': professor.nombre if professor else 'Unknown',
                    'timeslot_display': timeslot.to_dict()['display'] if timeslot else 'Unknown',
                    'semester': max(1, getattr(course, 'cuatrimestre', 1) or 1),
                    'group_id': max(1, getattr(course, 'group_id', 1) or 1)
                })
            
            generation_state['result'] = {
                'assignments': enriched_assignments,
                'metadata': {
                    'backtrack_count': final_result['backtrack_count'],
                    'computation_time': final_result['computation_time'],
                    'status': 'success' if final_result['success'] else 'partial',
                    'level_reached': generation_state['current_level']
                }
            }
            data_store['schedule'] = generation_state['result']
        else:
            generation_state['error'] = "No se pudo generar ningún horario válido en ningún nivel."

    except Exception as e:
        print(f"Error in generation task: {e}")
        generation_state['error'] = str(e)
        import traceback
        traceback.print_exc()
    finally:
        generation_state['is_running'] = False
        generation_state['scheduler_instance'] = None

@app.route('/api/generate', methods=['POST'])
def generate_schedule():
    """Start schedule generation in background"""
    if not SCHEDULER_AVAILABLE:
        return jsonify({'error': 'Scheduler not available'}), 503
    
    if generation_state['is_running']:
        return jsonify({'error': 'Generation already in progress'}), 409
        
    # Check data... (same as before)
    if not data_store['current_cycle'] and not data_store['courses']:
        return jsonify({'error': 'Please select a cycle or upload courses first'}), 400
    
    current_period = data_store['config']['period']
    valid_course_ids = get_valid_groups(current_period)
    
    courses_to_schedule = []
    if data_store['courses']:
        for course in data_store['courses']:
            if course.id in valid_course_ids:
                courses_to_schedule.append(course)
    
    if not courses_to_schedule:
        return jsonify({'error': f'No courses found for period {current_period}'}), 400

    # Start thread
    thread = threading.Thread(target=run_generation_task, args=(
        courses_to_schedule,
        data_store['professors'],
        data_store['timeslots'],
        data_store['config']
    ))
    thread.start()
    
    return jsonify({'success': True, 'message': 'Generation started'})

@app.route('/api/generate/stop', methods=['POST'])
def stop_generation():
    """Stop current generation"""
    if not generation_state['is_running']:
        return jsonify({'error': 'No generation running'}), 400
        
    generation_state['stop_requested'] = True
    if generation_state.get('scheduler_instance'):
        generation_state['scheduler_instance'].stop_generation()
        
    return jsonify({'success': True, 'message': 'Stop requested'})

@app.route('/api/generate/status', methods=['GET'])
def get_generation_status():
    """Get status of background generation"""
    status = {
        'is_running': generation_state['is_running'],
        'current_level': generation_state['current_level'],
        'metrics': generation_state.get('metrics', {}),
        'error': generation_state['error'],
        'has_result': generation_state['result'] is not None
    }
    
    # If running, try to get fresh metrics from instance
    if generation_state['is_running'] and generation_state.get('scheduler_instance'):
        try:
            status['metrics'] = generation_state['scheduler_instance'].get_metrics()
        except:
            pass
            
    return jsonify(status)


@app.route('/api/analyze-constraints', methods=['GET'])
def analyze_constraints():
    """Analyze data to find potential issues before generation."""
    try:
        issues = []
        
        # Check for courses without professors
        courses_without_professors = []
        for course in data_store['courses']:
            # Check if any professor can teach this course
            has_professor = False
            for prof in data_store['professors']:
                # Check by ID or Name if needed, but usually we rely on ID linkage
                # If course.professor_id is set (CSV)
                if hasattr(course, 'professor_id') and course.professor_id == prof.id:
                    has_professor = True
                    break
                # Or if professor has available_courses list (JSON)
                if hasattr(prof, 'available_courses') and course.id in prof.available_courses:
                    has_professor = True
                    break
            
            if not has_professor:
                courses_without_professors.append(f"{course.nombre} (ID: {course.id})")
        
        if courses_without_professors:
            issues.append({
                'type': 'warning',
                'title': 'Cursos sin Profesor',
                'message': f"Hay {len(courses_without_professors)} cursos que no tienen ningún profesor asignado o disponible. Estos cursos NO se programarán.",
                'details': courses_without_professors[:10] + (['...'] if len(courses_without_professors) > 10 else [])
            })

        # Check for professors with no availability
        profs_no_availability = []
        for prof in data_store['professors']:
            if not prof.available_timeslots:
                profs_no_availability.append(prof.nombre)
        
        if profs_no_availability:
            issues.append({
                'type': 'warning',
                'title': 'Profesores sin Disponibilidad',
                'message': f"Hay {len(profs_no_availability)} profesores sin horas disponibles definidas.",
                'details': profs_no_availability[:10]
            })

        return jsonify({'issues': issues})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get the generated schedule"""
    if data_store['schedule'] is None:
        return jsonify({'error': 'No schedule generated yet'}), 404
    
    return jsonify(data_store['schedule'])


@app.route('/api/professors', methods=['POST'])
def add_professor():
    """Add a new professor"""
    data = request.json
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    # Generate ID
    new_id = 1
    if data_store['professors']:
        new_id = max(p.id for p in data_store['professors']) + 1
    
    professor = Professor(
        id=new_id,
        name=data['name'],
        email=data.get('email', ''),
        available_timeslots=data.get('available_timeslots', [])
    )
    
    data_store['professors'].append(professor)
    return jsonify({'success': True, 'professor': professor.to_dict()})

@app.route('/api/professors/<int:id>', methods=['PUT'])
def update_professor(id):
    """Update a professor"""
    data = request.json
    professor = next((p for p in data_store['professors'] if p.id == id), None)
    
    if not professor:
        return jsonify({'error': 'Professor not found'}), 404
    
    if 'name' in data:
        professor.name = data['name']
    if 'email' in data:
        professor.email = data['email']
    if 'available_timeslots' in data:
        professor.available_timeslots = data['available_timeslots']
        
    return jsonify({'success': True, 'professor': professor.to_dict()})

@app.route('/api/professors/<int:id>', methods=['DELETE'])
def delete_professor(id):
    """Delete a professor"""
    professor = next((p for p in data_store['professors'] if p.id == id), None)
    
    if not professor:
        return jsonify({'error': 'Professor not found'}), 404
    
    data_store['professors'].remove(professor)
    return jsonify({'success': True, 'message': 'Professor deleted'})

@app.route('/api/professors/<int:id>/availability', methods=['POST'])
def update_availability(id):
    """Update professor availability"""
    data = request.json
    professor = next((p for p in data_store['professors'] if p.id == id), None)
    
    if not professor:
        return jsonify({'error': 'Professor not found'}), 404
        
    if 'available_timeslots' not in data:
        return jsonify({'error': 'available_timeslots required'}), 400
        
    professor.available_timeslots = data['available_timeslots']
    return jsonify({'success': True, 'message': 'Availability updated'})

@app.route('/api/professors/save', methods=['POST'])
def save_professors():
    """Save current professors data to JSON file"""
    try:
        # Define path to save - using prueba.json as default target
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'prueba.json')
        
        # Convert professors to dictionary format
        professors_data = [p.to_dict() for p in data_store['professors']]
        
        # We need to preserve the original structure (professors, time_slots, days)
        # Load existing file to keep other keys if possible, or reconstruct
        output_data = {
            "professors": professors_data,
            # Add default time_slots and days if not present in data_store (they are partially there)
            # For now, let's try to read the existing file to get the auxiliary data
        }
        
        if os.path.exists(save_path):
            with open(save_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                output_data["time_slots"] = existing_data.get("time_slots", {})
                output_data["days"] = existing_data.get("days", {})
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        return jsonify({'success': True, 'message': 'Professors data saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_data():
    """Reset all data"""
    data_store['courses'] = []
    data_store['professors'] = []
    data_store['timeslots'] = []
    data_store['schedule'] = None
    data_store['current_cycle'] = None
    
    return jsonify({'success': True, 'message': 'All data cleared'})


if __name__ == '__main__':
    print("=" * 60)
    print("UTP Scheduling System - Flask Server")
    print("=" * 60)
    print(f"Scheduler Available: {SCHEDULER_AVAILABLE}")
    if not SCHEDULER_AVAILABLE:
        print("\nWARNING: C++ scheduler not built!")
        print("Run: cd python_backend && python setup.py build_ext --inplace")
    print("\nStarting server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
