/**
 * UTP Scheduler - Frontend Application
 * Handles file uploads, API communication, and schedule visualization
 */

const API_BASE = 'http://localhost:5000/api';

// State management
const state = {
    courses: [],
    professors: [],
    timeslots: [],
    schedule: null,
    dataLoaded: {
        courses: false,
        professors: false,
        timeslots: false
    }
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeDropzones();
    initializeButtons();
    checkSystemStatus();
    updateUI();
});

// ===== Dropzone Handling =====
function initializeDropzones() {
    const dropzones = document.querySelectorAll('.dropzone');
    
    dropzones.forEach(dropzone => {
        const input = dropzone.querySelector('.file-input');
        const dataType = dropzone.dataset.type;
        
        // Click to upload
        dropzone.addEventListener('click', () => input.click());
        
        // File selection
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0], dataType, dropzone);
            }
        });
        
        // Drag and drop
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });
        
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                handleFileUpload(e.dataTransfer.files[0], dataType, dropzone);
            }
        });
    });
}

// ===== File Upload =====
async function handleFileUpload(file, dataType, dropzone) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_type', dataType);
    
    try {
        showNotification('Cargando...', `Subiendo ${dataType}...`, 'info');
        
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            dropzone.classList.add('uploaded');
            state.dataLoaded[dataType] = true;
            
            showNotification('¡Éxito!', result.message, 'success');
            
            if (result.warnings && result.warnings.length > 0) {
                result.warnings.forEach(warning => {
                    showNotification('Advertencia', warning, 'warning');
                });
            }
            
            await loadData(dataType);
            updateUI();
        } else {
            showNotification('Error', result.error || 'Error al cargar archivo', 'error');
            if (result.details) {
                result.details.forEach(detail => {
                    showNotification('Error de validación', detail, 'error');
                });
            }
        }
    } catch (error) {
        showNotification('Error', `Error al subir archivo: ${error.message}`, 'error');
    }
}

// ===== Data Loading =====
async function loadData(dataType) {
    try {
        const response = await fetch(`${API_BASE}/data/${dataType}`);
        const result = await response.json();
        
        if (response.ok) {
            state[dataType] = result.data;
        }
    } catch (error) {
        console.error(`Error loading ${dataType}:`, error);
    }
}

// ===== Button Handlers =====
function initializeButtons() {
    const generateBtn = document.getElementById('generateBtn');
    const resetBtn = document.getElementById('resetBtn');
    
    generateBtn.addEventListener('click', generateSchedule);
    resetBtn.addEventListener('click', resetData);
}

async function generateSchedule() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('active');
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            state.schedule = result.schedule;
            displaySchedule(result.schedule);
            
            showNotification(
                '¡Horario Generado!',
                `Generado en ${result.schedule.metadata.computation_time.toFixed(3)}s con ${result.schedule.metadata.backtrack_count} retrocesos`,
                'success'
            );
        } else {
            showNotification('Error', result.error || 'No se pudo generar el horario', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error al generar horario: ${error.message}`, 'error');
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

async function resetData() {
    if (!confirm('¿Estás seguro de que quieres reiniciar todos los datos?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Reset state
            state.courses = [];
            state.professors = [];
            state.timeslots = [];
            state.schedule = null;
            state.dataLoaded = {
                courses: false,
                professors: false,
                timeslots: false
            };
            
            // Reset UI
            document.querySelectorAll('.dropzone').forEach(dz => {
                dz.classList.remove('uploaded');
            });
            
            document.getElementById('scheduleSection').style.display = 'none';
            
            updateUI();
            showNotification('Reiniciado', 'Todos los datos han sido eliminados', 'success');
        }
    } catch (error) {
        showNotification('Error', `Error al reiniciar: ${error.message}`, 'error');
    }
}

// ===== UI Updates =====
function updateUI() {
    // Update counts
    document.getElementById('coursesCount').textContent = state.courses.length;
    document.getElementById('professorsCount').textContent = state.professors.length;
    document.getElementById('timeslotsCount').textContent = state.timeslots.length;
    
    // Update status cards
    updateStatusCard('coursesCard', state.dataLoaded.courses);
    updateStatusCard('professorsCard', state.dataLoaded.professors);
    updateStatusCard('timeslotsCard', state.dataLoaded.timeslots);
    
    // Update generate button
    const allDataLoaded = Object.values(state.dataLoaded).every(v => v);
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = !allDataLoaded;
    
    // Update validation status
    updateValidationStatus(allDataLoaded);
}

function updateStatusCard(cardId, loaded) {
    const card = document.getElementById(cardId);
    if (loaded) {
        card.classList.add('loaded');
    } else {
        card.classList.remove('loaded');
    }
}

function updateValidationStatus(allDataLoaded) {
    const validationStatus = document.getElementById('validationStatus');
    
    if (allDataLoaded) {
        validationStatus.className = 'validation-status success';
        validationStatus.textContent = '✓ Todos los datos cargados. Listo para generar horario.';
    } else {
        validationStatus.className = 'validation-status error';
        const missing = [];
        if (!state.dataLoaded.courses) missing.push('cursos');
        if (!state.dataLoaded.professors) missing.push('profesores');
        if (!state.dataLoaded.timeslots) missing.push('horarios');
        validationStatus.textContent = `⚠ Faltan datos: ${missing.join(', ')}`;
    }
}

// ===== Schedule Display =====
function displaySchedule(schedule) {
    const scheduleSection = document.getElementById('scheduleSection');
    const scheduleStats = document.getElementById('scheduleStats');
    const scheduleList = document.getElementById('scheduleList');
    
    scheduleSection.style.display = 'block';
    
    // Display stats
    scheduleStats.innerHTML = `
        <div>📊 ${schedule.assignments.length} clases asignadas</div>
        <div>⚡ ${schedule.metadata.computation_time.toFixed(3)}s</div>
        <div>🔄 ${schedule.metadata.backtrack_count} retrocesos</div>
    `;
    
    // Display schedule grid
    displayScheduleGrid(schedule.assignments);
    
    // Display schedule list
    displayScheduleList(schedule.assignments);
    
    // Scroll to schedule
    scheduleSection.scrollIntoView({ behavior: 'smooth' });
}

function displayScheduleGrid(assignments) {
    const scheduleGrid = document.getElementById('scheduleGrid');
    
    // Group assignments by day and time
    const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    const timeSlots = [...new Set(assignments.map(a => a.timeslot_display))].sort();
    
    // Create grid
    let gridHTML = '<div class="schedule-cell header"></div>';
    days.forEach(day => {
        gridHTML += `<div class="schedule-cell header">${day}</div>`;
    });
    
    timeSlots.forEach(timeSlot => {
        gridHTML += `<div class="schedule-cell time">${timeSlot.split(' ')[1]}</div>`;
        
        days.forEach(day => {
            const dayAssignments = assignments.filter(a => 
                a.timeslot_display.startsWith(day) && a.timeslot_display.includes(timeSlot.split(' ')[1])
            );
            
            gridHTML += '<div class="schedule-cell">';
            dayAssignments.forEach(assignment => {
                gridHTML += `
                    <div class="schedule-item" title="${assignment.course_name}">
                        <div class="schedule-item-course">${assignment.course_code || assignment.course_name}</div>
                        <div class="schedule-item-details">${assignment.professor_name}</div>
                    </div>
                `;
            });
            gridHTML += '</div>';
        });
    });
    
    scheduleGrid.innerHTML = gridHTML;
}

function displayScheduleList(assignments) {
    const scheduleList = document.getElementById('scheduleList');
    
    let listHTML = '';
    assignments.forEach(assignment => {
        listHTML += `
            <div class="schedule-list-item">
                <div class="schedule-list-header">
                    <div>
                        <div class="schedule-list-course">${assignment.course_name}</div>
                        <div class="schedule-list-code">${assignment.course_code || ''}</div>
                    </div>
                </div>
                <div class="schedule-list-details">
                    <div class="schedule-list-detail">
                        <span>👨‍🏫</span>
                        <span>${assignment.professor_name}</span>
                    </div>
                    <div class="schedule-list-detail">
                        <span>⏰</span>
                        <span>${assignment.timeslot_display}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    scheduleList.innerHTML = listHTML;
}

// ===== Notifications =====
function showNotification(title, message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-title">${title}</div>
        <div class="notification-message">${message}</div>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 250ms reverse';
        setTimeout(() => notification.remove(), 250);
    }, 5000);
}

// ===== System Status =====
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const status = await response.json();
        
        if (!status.scheduler_available) {
            showNotification(
                'Advertencia',
                'El motor de C++ no está disponible. Por favor, compila la extensión de Cython.',
                'warning'
            );
        }
    } catch (error) {
        showNotification(
            'Error de Conexión',
            'No se puede conectar con el servidor. Asegúrate de que Flask esté ejecutándose.',
            'error'
        );
    }
}
