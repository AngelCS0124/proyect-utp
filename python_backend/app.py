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
    'current_cycle': None  # Track currently selected cycle
}

# Initialize predefined timeslots
def initialize_timeslots():
    """Initialize valid predefined timeslots for the schedule"""
    from config.time_blocks import get_all_weekly_timeslots
    timeslot_dicts = get_all_weekly_timeslots(language='es')
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
        'current_cycle': data_store['current_cycle']
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process data files (professors and timeslots only)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    data_type = request.form.get('data_type')
    
    # Courses are now predefined, only allow professors and timeslots
    if not data_type or data_type not in ['professors', 'timeslots']:
        return jsonify({'error': 'Invalid data_type. Must be: professors or timeslots (courses are predefined)'}), 400
    
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
        loaded_data = DataLoader.load_data(filepath, data_type)
        
        # Validate data
        if data_type == 'professors':
            validation = Validator.validate_professors(loaded_data)
        elif data_type == 'timeslots':
            validation = Validator.validate_timeslots(loaded_data)
        
        if not validation['valid']:
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
            'message': f'Loaded {len(loaded_data)} {data_type}',
            'count': len(loaded_data),
            'warnings': validation.get('warnings', [])
        })
    
    except Exception as e:
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
        courses = get_courses_for_cycle(cycle)
        data_store['courses'] = courses
        data_store['current_cycle'] = cycle
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
    
    course.professor_id = professor_id
    
    return jsonify({
        'success': True,
        'message': f'Assigned {professor.name} to {course.name}'
    })


@app.route('/api/validate', methods=['GET'])
def validate_data():
    """Validate all loaded data"""
    validation = Validator.validate_all_data(
        data_store['courses'],
        data_store['professors'],
        data_store['timeslots']
    )
    
    return jsonify(validation)


@app.route('/api/generate', methods=['POST'])
def generate_schedule():
    """Generate schedule using C++ backtracking algorithm"""
    if not SCHEDULER_AVAILABLE:
        return jsonify({'error': 'Scheduler not available. Please build the C++ extension.'}), 503
    
    # Check if a cycle is selected
    if not data_store['current_cycle']:
        return jsonify({'error': 'Please select a cycle first'}), 400
    
    # Validate data first
    validation = Validator.validate_all_data(
        data_store['courses'],
        data_store['professors'],
        data_store['timeslots']
    )
    
    print(f"DEBUG: Validation result - valid: {validation['valid']}, errors: {validation['errors']}, warnings: {validation['warnings']}")
    
    if not validation['valid']:
        return jsonify({
            'error': 'Data validation failed',
            'details': validation['errors']
        }), 400
    
    try:
        # Create scheduler instance
        scheduler = PyScheduler()
        
        # Load data into C++ scheduler
        for course in data_store['courses']:
            group_id = getattr(course, 'group_id', 0)
            duration = getattr(course, 'credits', 1)
            scheduler.load_course(course.id, course.name, course.enrollment, course.prerequisites, group_id, duration)
        
        for professor in data_store['professors']:
            scheduler.load_professor(professor.id, professor.name, professor.available_timeslots)
        
        for timeslot in data_store['timeslots']:
            scheduler.load_timeslot(timeslot.id, timeslot.day, 
                                   timeslot.start_hour, timeslot.start_minute,
                                   timeslot.end_hour, timeslot.end_minute)
        
        # Assign professors to courses
        for course in data_store['courses']:
            if course.professor_id is not None:
                scheduler.assign_professor_to_course(course.id, course.professor_id)
        
        # Generate schedule
        result = scheduler.generate_schedule()
        
        if result['success']:
            # Enrich assignments with names
            enriched_assignments = []
            for assignment in result['assignments']:
                course = next((c for c in data_store['courses'] if c.id == assignment['course_id']), None)
                professor = next((p for p in data_store['professors'] if p.id == assignment['professor_id']), None)
                timeslot = next((t for t in data_store['timeslots'] if t.id == assignment['timeslot_id']), None)
                
                enriched_assignments.append({
                    **assignment,
                    'course_name': course.name if course else 'Unknown',
                    'course_code': course.code if course else '',
                    'professor_name': professor.name if professor else 'Unknown',
                    'timeslot_display': timeslot.to_dict()['display'] if timeslot else 'Unknown',
                    'semester': getattr(course, 'semester', None),
                    'group_id': getattr(course, 'group_id', 0)
                })
            
            data_store['schedule'] = {
                'assignments': enriched_assignments,
                'metadata': {
                    'backtrack_count': result['backtrack_count'],
                    'computation_time': result['computation_time']
                }
            }
            
            return jsonify({
                'success': True,
                'schedule': data_store['schedule']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error_message']
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
