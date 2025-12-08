/**
 * UTP Scheduler - Frontend Application
 */

const API_BASE = 'http://localhost:5000/api';

// State management
const state = {
    courses: [],
    professors: [],
    timeslots: [],
    schedule: null,
    currentCycle: null,
    availableCycles: [],
    dataLoaded: {
        courses: false,
        professors: false,
        timeslots: false
    }
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    loadAvailableCycles();
    checkSystemStatus();
    updateUI();
});

// ===== Navigation =====
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view-section');
    const pageTitle = document.getElementById('page-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update Nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Update View
            const viewId = item.dataset.view;
            views.forEach(view => view.style.display = 'none');
            document.getElementById(`view-${viewId}`).style.display = 'block';

            // Update Title
            pageTitle.textContent = item.querySelector('span').textContent;

            // View Specific Actions
            if (viewId === 'maestros') renderProfessorsTable();
            if (viewId === 'disponibilidad') initializeAvailabilityView();
            if (viewId === 'horario') renderScheduleView();
        });
    });
}

// ===== Upload Handling =====
function uploadFile(input, dataType) {
    if (input.files.length > 0) {
        handleFileUpload(input.files[0], dataType);
    }
}

async function handleFileUpload(file, dataType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_type', dataType);

    try {
        showNotification('Cargando...', `Subiendo ${dataType}...`, 'info');
        const response = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
        const result = await response.json();

        if (response.ok) {
            state.dataLoaded[dataType] = true;
            showNotification('¡Éxito!', result.message, 'success');
            await loadData(dataType);

            if (dataType === 'professors') {
                await loadData('timeslots');
                state.dataLoaded.timeslots = true;
            }

            updateUI();
        } else {
            showNotification('Error', result.error || 'Error al cargar archivo', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error al subir archivo: ${error.message}`, 'error');
    }
}

async function uploadExcel(input) {
    if (input.files.length === 0) return;

    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        showNotification('Cargando...', 'Procesando Excel...', 'info');
        const response = await fetch(`${API_BASE}/upload-excel`, { method: 'POST', body: formData });
        const result = await response.json();

        if (response.ok) {
            state.dataLoaded.professors = true;
            state.dataLoaded.courses = true;
            showNotification('¡Éxito!', result.message, 'success');

            await loadData('professors');
            await loadData('courses');
            updateUI();
        } else {
            showNotification('Error', result.error || 'Error al procesar Excel', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error al subir Excel: ${error.message}`, 'error');
    }
}

async function loadDefaultData() {
    try {
        showNotification('Cargando...', 'Cargando datos por defecto...', 'info');
        const response = await fetch(`${API_BASE}/load-defaults`, { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            state.dataLoaded.professors = true;
            state.dataLoaded.courses = true;
            showNotification('¡Éxito!', result.message, 'success');
            await loadData('professors');
            await loadData('courses');
            updateUI();
        } else {
            showNotification('Error', result.error || 'Error al cargar datos por defecto', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error: ${error.message}`, 'error');
    }
}

async function loadData(dataType) {
    try {
        const response = await fetch(`${API_BASE}/data/${dataType}`);
        const result = await response.json();
        if (response.ok) {
            state[dataType] = result.data;
            if (dataType === 'courses') {
                state.dataLoaded.courses = true;
            }
        }
    } catch (error) {
        console.error(`Error loading ${dataType}:`, error);
    }
}

// ===== Cycle Management =====
async function loadAvailableCycles() {
    try {
        const response = await fetch(`${API_BASE}/cycles`);
        const result = await response.json();
        if (response.ok) {
            state.availableCycles = result.cycles;
            renderCycleSelector();
        }
    } catch (error) {
        console.error('Error loading cycles:', error);
    }
}

function renderCycleSelector() {
    const select = document.getElementById('cycle-select');
    select.innerHTML = '<option value="">Seleccionar ciclo...</option>';

    state.availableCycles.forEach(cycle => {
        const option = document.createElement('option');
        option.value = cycle.id;
        option.textContent = cycle.name;
        select.appendChild(option);
    });
}

async function loadCycleData() {
    const select = document.getElementById('cycle-select');
    const cycleId = select.value;

    if (!cycleId) {
        state.currentCycle = null;
        state.courses = [];
        state.dataLoaded.courses = false;
        updateUI();
        return;
    }

    try {
        showNotification('Cargando...', `Cargando cursos para ${select.options[select.selectedIndex].text}...`, 'info');
        const response = await fetch(`${API_BASE}/courses/${cycleId}`);
        const result = await response.json();

        if (response.ok) {
            state.courses = result.data;
            state.currentCycle = state.availableCycles.find(c => c.id === cycleId);
            state.dataLoaded.courses = true;

            // Update cycle info display
            document.getElementById('cycle-info').style.display = 'block';
            document.getElementById('cycle-months').textContent = state.currentCycle.months;

            // Render semester badges
            const badgesContainer = document.getElementById('cycle-semesters-badges');
            badgesContainer.innerHTML = '';
            state.currentCycle.cuatrimestres.forEach(sem => {
                const badge = document.createElement('span');
                badge.className = 'semester-badge';
                badge.textContent = `${sem}°`;
                badgesContainer.appendChild(badge);
            });

            showNotification('¡Éxito!', `Cargados ${result.count} cursos`, 'success');
            updateUI();
        } else {
            showNotification('Error', result.error || 'Error al cargar cursos', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error al cargar ciclo: ${error.message}`, 'error');
    }
}

// ===== Maestros View =====
function renderProfessorsTable() {
    const tbody = document.getElementById('professors-list');
    tbody.innerHTML = '';

    if (state.professors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No hay profesores cargados</td></tr>';
        return;
    }

    state.professors.forEach(prof => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${prof.id}</td>
            <td>
                <div style="font-weight: 600;">${prof.name}</div>
            </td>
            <td>${prof.email || 'N/A'}</td>
            <td>
                <button class="action-btn edit" onclick="openProfessorModal(${prof.id})"><i class="fas fa-pen"></i></button>
                <button class="action-btn delete" onclick="deleteProfessor(${prof.id})"><i class="fas fa-trash"></i></button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filterProfessors() {
    const query = document.getElementById('search-professor').value.toLowerCase();
    const rows = document.querySelectorAll('#professors-list tr');

    rows.forEach(row => {
        const name = row.children[1].textContent.toLowerCase();
        row.style.display = name.includes(query) ? '' : 'none';
    });
}

// Modal Logic
function openProfessorModal(id = null) {
    const modal = document.getElementById('professor-modal');
    const title = document.getElementById('modal-title');
    const idInput = document.getElementById('prof-id');
    const nameInput = document.getElementById('prof-name');
    const emailInput = document.getElementById('prof-email');

    if (id) {
        const prof = state.professors.find(p => p.id === id);
        title.textContent = 'Editar Maestro';
        idInput.value = prof.id;
        nameInput.value = prof.name;
        emailInput.value = prof.email;
    } else {
        title.textContent = 'Añadir Maestro';
        idInput.value = '';
        nameInput.value = '';
        emailInput.value = '';
    }

    modal.style.display = 'flex';
}

function closeProfessorModal() {
    document.getElementById('professor-modal').style.display = 'none';
}

async function saveProfessor() {
    const id = document.getElementById('prof-id').value;
    const name = document.getElementById('prof-name').value;
    const email = document.getElementById('prof-email').value;

    if (!name) {
        showNotification('Error', 'El nombre es obligatorio', 'error');
        return;
    }

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_BASE}/professors/${id}` : `${API_BASE}/professors`;

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });

        if (response.ok) {
            showNotification('Éxito', 'Profesor guardado', 'success');
            closeProfessorModal();
            await loadData('professors');
            renderProfessorsTable();
            updateUI();
        }
        if (!response.ok) {
            const errorData = await response.json();
            const error = new Error(errorData.error || 'Error al generar horario');
            if (errorData.details) {
                error.details = errorData.details;
            }
            throw error;
        }
    } catch (error) {
        showNotification('Error', error.message, 'error');
    }
}

async function deleteProfessor(id) {
    if (!confirm("¿Eliminar profesor?")) return;

    try {
        const response = await fetch(`${API_BASE}/professors/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showNotification('Éxito', 'Profesor eliminado', 'success');
            await loadData('professors');
            renderProfessorsTable();
            updateUI();
        }
    } catch (error) {
        showNotification('Error', error.message, 'error');
    }
}

// ===== Disponibilidad View =====
function initializeAvailabilityView() {
    const select = document.getElementById('availability-professor-select');
    select.innerHTML = '<option value="">Seleccionar Maestro</option>';

    state.professors.forEach(prof => {
        const option = document.createElement('option');
        option.value = prof.id;
        option.textContent = prof.name;
        select.appendChild(option);
    });

    // Reset overlay
    document.getElementById('calendar-overlay').style.display = 'flex';
    renderAvailabilityGrid([]);
}

function filterProfessorsBySubject() {
    const query = document.getElementById('availability-filter-subject').value.toLowerCase();
    const select = document.getElementById('availability-professor-select');

    // Clear current options
    select.innerHTML = '<option value="">Seleccionar Maestro</option>';

    // Filter professors based on courses they teach (if we had that data linked)
    // Since we don't have explicit subject linking in Professor model, 
    // we'll filter by name for now as a fallback, or check courses list

    const matchedProfIds = new Set();
    if (query) {
        state.courses.forEach(c => {
            if (c.name.toLowerCase().includes(query) && c.professor_id) {
                matchedProfIds.add(c.professor_id);
            }
        });
    }

    state.professors.forEach(prof => {
        // If query is empty, show all. If query exists, show only matched.
        if (!query || matchedProfIds.has(prof.id)) {
            const option = document.createElement('option');
            option.value = prof.id;
            option.textContent = prof.name;
            select.appendChild(option);
        }
    });
}

function loadProfessorAvailability() {
    const select = document.getElementById('availability-professor-select');
    const profId = parseInt(select.value);
    const overlay = document.getElementById('calendar-overlay');

    if (!profId) {
        overlay.style.display = 'flex';
        renderAvailabilityGrid([]);
        return;
    }

    overlay.style.display = 'none';
    const professor = state.professors.find(p => p.id === profId);

    if (professor) {
        renderAvailabilityGrid(professor.available_timeslots);
    } else {
        renderAvailabilityGrid([]);
    }
}

function renderAvailabilityGrid(availableSlots) {
    const tbody = document.getElementById('availability-grid');
    tbody.innerHTML = '';

    // Define the predefined time blocks (54 minutes each)
    const timeBlocks = [
        { name: 'Bloque 1', start_hour: 7, start_minute: 0, end_hour: 7, end_minute: 54 },
        { name: 'Bloque 2', start_hour: 7, start_minute: 55, end_hour: 8, end_minute: 49 },
        { name: 'Bloque 3', start_hour: 8, start_minute: 50, end_hour: 9, end_minute: 44 },
        { name: 'Bloque 4', start_hour: 9, start_minute: 45, end_hour: 10, end_minute: 39 },
        // RECESS: 10:40 - 11:09
        { name: 'Bloque 5', start_hour: 11, start_minute: 10, end_hour: 12, end_minute: 4 },
        { name: 'Bloque 6', start_hour: 12, start_minute: 5, end_hour: 12, end_minute: 59 },
        { name: 'Bloque 7', start_hour: 13, start_minute: 0, end_hour: 13, end_minute: 54 },
        { name: 'Bloque 8', start_hour: 14, start_minute: 0, end_hour: 14, end_minute: 54 },
        { name: 'Bloque 9', start_hour: 14, start_minute: 55, end_hour: 15, end_minute: 49 }
    ];

    const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];

    timeBlocks.forEach((block, index) => {
        // Add separator before Bloque 5 (after recess)
        if (index === 4) {
            const separatorTr = document.createElement('tr');
            separatorTr.innerHTML = '<td colspan="6" style="height: 20px; background-color: #f0f0f0; border-top: 2px solid #ccc; border-bottom: 2px solid #ccc;"><em style="color: #999;">Receso: 10:40 - 11:09</em></td>';
            separatorTr.style.pointerEvents = 'none';
            tbody.appendChild(separatorTr);
        }

        const tr = document.createElement('tr');
        const startTime = `${String(block.start_hour).padStart(2, '0')}:${String(block.start_minute).padStart(2, '0')}`;
        const endTime = `${String(block.end_hour).padStart(2, '0')}:${String(block.end_minute).padStart(2, '0')}`;
        tr.innerHTML = `<td>${startTime}-${endTime}</td>`;

        days.forEach(day => {
            // Find timeslot ID matching this day and time block
            const slot = state.timeslots.find(t =>
                t.day === day &&
                t.start_hour === block.start_hour &&
                t.start_minute === block.start_minute
            );

            let slotId = slot ? slot.id : null;
            let isAvailable = slotId && availableSlots.includes(slotId);

            const statusClass = isAvailable ? 'on' : 'off';
            const statusText = isAvailable ? 'On' : 'Off';

            tr.innerHTML += `
                <td>
                    <button class="toggle-btn ${statusClass}" 
                            data-slot-id="${slotId}"
                            onclick="toggleAvailability(this)">
                        ${statusText}
                    </button>
                </td>
            `;
        });
        tbody.appendChild(tr);
    });
}

function toggleAvailability(btn) {
    if (!btn.dataset.slotId || btn.dataset.slotId === "null") {
        showNotification('Info', 'No hay horario definido para este bloque', 'warning');
        return;
    }

    if (btn.classList.contains('on')) {
        btn.classList.remove('on');
        btn.classList.add('off');
        btn.textContent = 'Off';
    } else {
        btn.classList.remove('off');
        btn.classList.add('on');
        btn.textContent = 'On';
    }
}

async function saveAvailability() {
    const select = document.getElementById('availability-professor-select');
    const profId = parseInt(select.value);

    if (!profId) {
        showNotification('Error', 'Selecciona un profesor primero', 'error');
        return;
    }

    // Collect all 'on' slots
    const onButtons = document.querySelectorAll('.toggle-btn.on');
    const availableTimeslots = Array.from(onButtons)
        .map(btn => parseInt(btn.dataset.slotId))
        .filter(id => !isNaN(id));

    try {
        const response = await fetch(`${API_BASE}/professors/${profId}/availability`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ available_timeslots: availableTimeslots })
        });

        if (response.ok) {
            // After updating memory, save to file
            await saveAllProfessors(false); // false = silent mode (no extra notification if success)
            showNotification('Éxito', 'Disponibilidad guardada en archivo', 'success');
            await loadData('professors'); // Reload to update state
        }
    } catch (error) {
        showNotification('Error', error.message, 'error');
    }
}

async function saveAllProfessors(showSuccess = true) {
    try {
        const response = await fetch(`${API_BASE}/professors/save`, { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            if (showSuccess) showNotification('Éxito', 'Todos los cambios han sido guardados en el archivo', 'success');
        } else {
            showNotification('Error', result.error || 'Error al guardar en archivo', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error de conexión: ${error.message}`, 'error');
    }
}

// ===== Schedule Generation =====
async function generateSchedule() {
    // 1. Pre-check constraints
    try {
        const checkResponse = await fetch(`${API_BASE}/analyze-constraints`);
        const checkResult = await checkResponse.json();

        if (checkResult.issues && checkResult.issues.length > 0) {
            const proceed = await showPrecheckModal(checkResult.issues);
            if (!proceed) return;
        }
    } catch (e) {
        console.error("Pre-check failed", e);
    }

    const btn = document.getElementById('generate-btn');
    const originalText = btn.innerHTML;
    btn.disabled = true;

    // Show Generation Overlay
    showGenerationOverlay();

    try {
        // Read config values
        let timeLimit = parseInt(document.getElementById('time-limit').value);
        if (isNaN(timeLimit)) timeLimit = 0;

        const strategy = document.getElementById('strategy').value;
        const currentPeriod = state.currentCycle ? state.currentCycle.id : null;

        if (!currentPeriod) {
            showNotification('Error', 'Por favor selecciona un ciclo académico primero', 'error');
            hideGenerationOverlay();
            btn.disabled = false;
            btn.innerHTML = originalText;
            return;
        }

        // Update config on backend
        await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                time_limit: timeLimit,
                strategy: strategy,
                period: currentPeriod
            })
        });

        // Start Generation
        const response = await fetch(`${API_BASE}/generate`, { method: 'POST' });
        const result = await response.json();

        hideGenerationOverlay();

        if (response.ok && result.success) {
            // Backend returns schedule directly (synchronous generation)
            state.schedule = result.schedule;
            const meta = result.metadata || {};

            showNotification('¡Horario Generado!', `Generado con éxito en ${(meta.computation_time || 0).toFixed(2)}s`, 'success');
            document.querySelector('[data-view="horario"]').click();
        } else {
            showErrorModal(result.error || 'No se pudo generar el horario');
        }
    } catch (error) {
        console.error('Generation error:', error);
        hideGenerationOverlay();
        showErrorModal('Error de Generación', error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

function stopGeneration() {
    fetch(`${API_BASE}/generate/stop`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            const btn = document.getElementById('stop-gen-btn');
            if (btn) btn.textContent = "Deteniendo...";
        });
}

function updateGenerationStatus(status, timeLimit, startTime) {
    const elapsed = (Date.now() - startTime) / 1000;
    const metrics = status.metrics || {};

    // Update Text
    document.getElementById('gen-step').textContent = `Nivel ${status.current_level}: Explorando...`;

    // Update Progress Bar
    if (timeLimit > 0) {
        const percent = Math.min(100, (elapsed / timeLimit) * 100);
        document.getElementById('gen-progress').style.width = `${percent}%`;
        document.getElementById('gen-time').textContent = `${elapsed.toFixed(1)}s / ${timeLimit}s`;
    } else {
        document.getElementById('gen-progress').style.width = '100%';
        document.getElementById('gen-progress').classList.add('indeterminate');
        document.getElementById('gen-time').textContent = `${elapsed.toFixed(1)}s`;
    }

    // Update Metrics
    document.getElementById('metric-backtracks').textContent = metrics.backtrack_count || 0;
    document.getElementById('metric-score').textContent = (metrics.best_score || -1e9).toFixed(0);
    document.getElementById('metric-assigned').textContent = `${metrics.assigned_courses || 0} / ${metrics.total_courses || '?'}`;

    // Update Level Badge
    const levels = { 1: "ESTRICTO", 2: "RELAJADO", 3: "GREEDY", 4: "EMERGENCIA" };
    document.getElementById('metric-level').textContent = levels[status.current_level] || status.current_level;
}

function showGenerationOverlay() {
    if (!document.getElementById('gen-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'gen-overlay';
        overlay.className = 'generation-overlay';
        overlay.innerHTML = `
            <div class="gen-content" style="width: 500px;">
                <div class="gen-header">
                    <div class="gen-spinner"></div>
                    <h3 id="gen-step">Iniciando...</h3>
                </div>
                
                <div class="progress-container">
                    <div class="progress-bar">
                        <div id="gen-progress" class="progress-fill"></div>
                    </div>
                    <div id="gen-time" style="text-align: right; font-size: 0.9em; color: #666; margin-top: 5px;">0s</div>
                </div>
                
                <div class="metrics-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 20px 0; background: #f8fafc; padding: 15px; border-radius: 8px;">
                    <div class="metric-item">
                        <small>Nivel</small>
                        <strong id="metric-level">-</strong>
                    </div>
                    <div class="metric-item">
                        <small>Explorados</small>
                        <strong id="metric-backtracks">0</strong>
                    </div>
                    <div class="metric-item">
                        <small>Mejor Score</small>
                        <strong id="metric-score">0</strong>
                    </div>
                    <div class="metric-item">
                        <small>Asignados</small>
                        <strong id="metric-assigned">0/0</strong>
                    </div>
                </div>

                <div class="gen-checklist" style="text-align: left; font-size: 0.9em; color: #555; margin-bottom: 20px;">
                    <div><i class="fas fa-check-circle" style="color: green;"></i> Profesores sin conflictos</div>
                    <div><i class="fas fa-check-circle" style="color: green;"></i> Grupos sin choques</div>
                    <div><i class="fas fa-check-circle" style="color: green;"></i> Horarios válidos</div>
                </div>
                
                <button id="stop-gen-btn" class="btn-secondary" onclick="stopGeneration()" style="width: 100%; border-color: #ef4444; color: #ef4444;">
                    <i class="fas fa-stop"></i> DETENER BÚSQUEDA
                </button>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    document.getElementById('gen-overlay').style.display = 'flex';

    // Reset values
    document.getElementById('gen-progress').style.width = '0%';
    document.getElementById('stop-gen-btn').textContent = "DETENER BÚSQUEDA";
}

function showPrecheckModal(issues) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';

        let issuesHtml = issues.map(issue => `
            <div class="issue-item" style="margin-bottom: 15px; border-left: 4px solid #f59e0b; padding-left: 10px;">
                <h4 style="color: #d97706; margin: 0 0 5px 0;">${issue.title}</h4>
                <p style="margin: 0 0 5px 0;">${issue.message}</p>
                ${issue.details ? `<ul style="font-size: 0.9em; color: #666; max-height: 100px; overflow-y: auto;">${issue.details.map(d => `<li>${d}</li>`).join('')}</ul>` : ''}
            </div>
        `).join('');

        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header" style="background-color: #fffbeb; border-bottom: 1px solid #fcd34d;">
                    <h3 style="color: #b45309;"><i class="fas fa-exclamation-triangle"></i> Advertencia de Datos</h3>
                </div>
                <div class="modal-body">
                    <p>Se detectaron problemas en los datos que afectarán el horario:</p>
                    <div style="background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; max-height: 300px; overflow-y: auto;">
                        ${issuesHtml}
                    </div>
                    <p style="margin-top: 15px; font-weight: bold;">¿Deseas continuar de todos modos?</p>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" id="btn-cancel-gen">Cancelar</button>
                    <button class="btn-primary" id="btn-confirm-gen">Continuar</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        document.getElementById('btn-cancel-gen').onclick = () => {
            modal.remove();
            resolve(false);
        };
        document.getElementById('btn-confirm-gen').onclick = () => {
            modal.remove();
            resolve(true);
        };
    });
}

function showErrorModal(message) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'flex';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header" style="background-color: #fee2e2; border-bottom: 1px solid #fecaca;">
                <h3 style="color: #ef4444;"><i class="fas fa-exclamation-circle"></i> Error de Generación</h3>
                <span class="close-modal" onclick="this.closest('.modal').remove()">&times;</span>
            </div>
            <div class="modal-body">
                <p style="white-space: pre-wrap; font-family: monospace; background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0;">${message}</p>
            </div>
            <div class="modal-footer">
                <button class="btn-primary" onclick="this.closest('.modal').remove()">Entendido</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function hideGenerationOverlay() {
    const overlay = document.getElementById('gen-overlay');
    if (overlay) overlay.style.display = 'none';
}

function renderScheduleView() {
    const emptyState = document.getElementById('no-schedule-msg');
    const vizControls = document.getElementById('viz-controls');
    const filterContainer = document.getElementById('schedule-filters');
    const calendarContainer = document.getElementById('schedule-calendar-container');

    if (!state.schedule) {
        emptyState.style.display = 'block';
        if (vizControls) vizControls.style.display = 'none';
        if (filterContainer) filterContainer.style.display = 'none';
        if (calendarContainer) calendarContainer.style.display = 'none';
        return;
    }

    emptyState.style.display = 'none';
    if (vizControls) vizControls.style.display = 'flex';
    if (filterContainer) filterContainer.style.display = 'block';
    if (calendarContainer) calendarContainer.style.display = 'block';

    // Update filter options based on current cycle
    // updateSemesterFilter(); // Removed

    // Render Calendar View directly
    renderCalendarView();
}

function renderCalendarView() {
    const container = document.getElementById('schedule-calendar-container');
    container.innerHTML = '';

    // Group assignments by semester/group
    const groups = {};
    state.schedule.assignments.forEach(a => {
        const sem = a.semester || 1;
        const key = `Cuatrimestre ${sem}`;
        if (!groups[key]) groups[key] = [];
        groups[key].push(a);
    });

    // Render a calendar for each group
    Object.keys(groups).sort().forEach(groupName => {
        const groupAssignments = groups[groupName];

        const groupSection = document.createElement('div');
        groupSection.className = 'calendar-group';
        groupSection.innerHTML = `<h3>📅 ${groupName}</h3>`;

        const table = document.createElement('table');
        table.className = 'calendar-table';

        // Header con diseño profesional
        table.innerHTML = `
            <thead>
                <tr>
                    <th class="time-header">Horario</th>
                    <th>Lunes</th>
                    <th>Martes</th>
                    <th>Miércoles</th>
                    <th>Jueves</th>
                    <th>Viernes</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;

        const tbody = table.querySelector('tbody');

        // Time blocks
        const timeBlocks = [
            { label: '7:00-7:54', start: 7, min: 0 },
            { label: '7:55-8:49', start: 7, min: 55 },
            { label: '8:50-9:44', start: 8, min: 50 },
            { label: '9:45-10:39', start: 9, min: 45 },
            { label: '11:10-12:04', start: 11, min: 10 },
            { label: '12:05-12:59', start: 12, min: 5 },
            { label: '13:00-13:54', start: 13, min: 0 },
            { label: '14:00-14:54', start: 14, min: 0 },
            { label: '14:55-15:49', start: 14, min: 55 }
        ];

        timeBlocks.forEach(block => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td class="time-cell">${block.label}</td>`;

            ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'].forEach(day => {
                const td = document.createElement('td');
                td.className = 'calendar-cell';

                // Find assignment for this day and time
                const assignment = groupAssignments.find(a => {
                    if (!a.timeslot_display) return false;
                    return a.timeslot_display.includes(day) &&
                        a.timeslot_display.includes(block.label.split('-')[0]);
                });

                if (assignment) {
                    // Crear tarjeta de curso con diseño profesional
                    const courseCard = document.createElement('div');
                    courseCard.className = 'cell-content';
                    courseCard.innerHTML = `
                        <div class="cell-course">${assignment.course_name}</div>
                        <div class="cell-prof">${assignment.professor_name}</div>
                    `;

                    // Tooltip opcional
                    courseCard.title = `${assignment.course_name}\n${assignment.professor_name}\n${assignment.timeslot_display}`;

                    td.appendChild(courseCard);
                }

                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        groupSection.appendChild(table);
        container.appendChild(groupSection);
    });
}

// Filter functions removed as requested

// ===== System Status =====
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const status = await response.json();

        if (status.data_loaded.courses > 0) {
            state.dataLoaded.courses = true;
            loadData('courses');
        }
        if (status.data_loaded.professors > 0) {
            state.dataLoaded.professors = true;
            loadData('professors');
        }
        if (status.data_loaded.timeslots > 0) {
            state.dataLoaded.timeslots = true;
            loadData('timeslots');
        }

        // Update current cycle if set
        if (status.current_cycle) {
            state.currentCycle = state.availableCycles.find(c => c.id === status.current_cycle);
            if (state.currentCycle) {
                document.getElementById('cycle-select').value = status.current_cycle;
                document.getElementById('cycle-info').style.display = 'block';
                document.getElementById('cycle-months').textContent = state.currentCycle.months;

                // Render semester badges
                const badgesContainer = document.getElementById('cycle-semesters-badges');
                badgesContainer.innerHTML = '';
                state.currentCycle.cuatrimestres.forEach(sem => {
                    const badge = document.createElement('span');
                    badge.className = 'semester-badge';
                    badge.textContent = `${sem}°`;
                    badgesContainer.appendChild(badge);
                });
            }
        }
    } catch (error) {
        console.error('Error checking system status:', error);
        showNotification('Error', 'No se pudo conectar con el servidor para obtener el estado.', 'error');
    }
}

function exportarHorario() {
    if (!state.schedule || !state.schedule.assignments) {
        showNotification('Error', 'No hay horario para exportar', 'error');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text('Horario Generado - Universidad', 14, 20);
    doc.setFontSize(11);
    doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 28);

    let yPos = 35;

    // Group by semester
    const groups = {};
    state.schedule.assignments.forEach(a => {
        const sem = a.semester || 1;
        const key = `Cuatrimestre ${sem}`;
        if (!groups[key]) groups[key] = [];
        groups[key].push(a);
    });

    Object.keys(groups).sort().forEach((groupName, index) => {
        if (index > 0) {
            doc.addPage();
            yPos = 20;
        }

        doc.setFontSize(14);
        doc.text(groupName, 14, yPos);
        yPos += 10;

        const groupAssignments = groups[groupName];

        // Prepare table data
        const timeBlocks = [
            { label: '7:00-7:54', start: 7, min: 0 },
            { label: '7:55-8:49', start: 7, min: 55 },
            { label: '8:50-9:44', start: 8, min: 50 },
            { label: '9:45-10:39', start: 9, min: 45 },
            { label: '11:10-12:04', start: 11, min: 10 },
            { label: '12:05-12:59', start: 12, min: 5 },
            { label: '13:00-13:54', start: 13, min: 0 },
            { label: '14:00-14:54', start: 14, min: 0 },
            { label: '14:55-15:49', start: 14, min: 55 }
        ];

        const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
        const body = [];

        timeBlocks.forEach(block => {
            const row = [block.label];
            days.forEach(day => {
                const assignment = groupAssignments.find(a =>
                    a.timeslot_display.includes(day) && a.timeslot_display.includes(block.label.split('-')[0])
                );
                if (assignment) {
                    row.push(`${assignment.course_name}\n${assignment.professor_name}`);
                } else {
                    row.push('');
                }
            });
            body.push(row);
        });

        doc.autoTable({
            startY: yPos,
            head: [['Horario', ...days]],
            body: body,
            theme: 'grid',
            styles: { fontSize: 8, cellPadding: 2 },
            headStyles: { fillColor: [66, 133, 244] },
            columnStyles: {
                0: { cellWidth: 25 }, // Time column
                1: { cellWidth: 32 },
                2: { cellWidth: 32 },
                3: { cellWidth: 32 },
                4: { cellWidth: 32 },
                5: { cellWidth: 32 }
            }
        });

        yPos = doc.lastAutoTable.finalY + 20;
    });

    doc.save('horario_universidad.pdf');
    showNotification('Éxito', 'Horario exportado a PDF', 'success');
}
function updateUI() {
    // Update cycle name
    const cycleName = document.getElementById('cycle-name');
    if (state.currentCycle) {
        cycleName.textContent = state.currentCycle.name;
        cycleName.style.fontSize = '0.9rem';
    } else {
        cycleName.textContent = 'No seleccionado';
        cycleName.style.fontSize = '';
    }

    document.getElementById('course-count').textContent = state.courses.length;
    document.getElementById('professor-count').textContent = state.professors.length;
    document.getElementById('timeslot-count').textContent = state.timeslots.length;

    // Update upload cards status
    updateCardState('card-professors', state.dataLoaded.professors);
    updateCardState('card-timeslots', state.dataLoaded.timeslots);
    updateCardState('card-courses', state.dataLoaded.courses);
}

function updateCardState(cardId, loaded) {
    const card = document.getElementById(cardId);
    if (!card) return;

    const icon = card.querySelector('.upload-status-icon');

    if (loaded) {
        card.style.borderColor = 'var(--success)';
        card.querySelector('.upload-icon').style.color = 'var(--success)';
        if (icon) icon.style.display = 'block';
    }
}

function showNotification(title, message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.className = `notification ${type}`;
    notification.innerHTML = `<strong>${title}</strong><br>${message}`;
    notification.style.display = 'block';
    setTimeout(() => notification.style.display = 'none', 5000);
}

// Expose functions for onclick handlers
window.openProfessorModal = openProfessorModal;
window.closeProfessorModal = closeProfessorModal;
window.saveProfessor = saveProfessor;
window.deleteProfessor = deleteProfessor;
window.saveAvailability = saveAvailability;
window.uploadFile = uploadFile;
window.generateSchedule = generateSchedule;
window.toggleAvailability = toggleAvailability;
window.loadProfessorAvailability = loadProfessorAvailability;
window.filterProfessors = filterProfessors;
window.filterProfessorsBySubject = filterProfessorsBySubject;
window.loadCycleData = loadCycleData;
window.loadDefaultData = loadDefaultData;
window.filterScheduleBySemester = filterScheduleBySemester;
window.saveAllProfessors = saveAllProfessors;

// ===== Calendar View Logic =====

state.currentScheduleView = 'list';

function switchScheduleView(view) {
    state.currentScheduleView = view;

    // Update buttons
    document.getElementById('btn-view-list').classList.toggle('active', view === 'list');
    document.getElementById('btn-view-calendar').classList.toggle('active', view === 'calendar');

    // Update visibility
    document.getElementById('schedule-list-container').style.display = view === 'list' ? 'block' : 'none';
    document.getElementById('schedule-calendar-container').style.display = view === 'calendar' ? 'block' : 'none';

    if (view === 'calendar') {
        renderScheduleCalendarView();
    }
}

window.switchScheduleView = switchScheduleView;

function renderScheduleCalendarView() {
    const container = document.getElementById('schedule-calendar-container');
    container.innerHTML = '';

    if (!state.schedule) return;

    // const semesterFilter = document.getElementById('semester-filter') ? document.getElementById('semester-filter').value : 'all';

    // Group assignments by semester/group
    const groups = {};
    state.schedule.assignments.forEach(a => {
        const sem = a.semester || 0;
        // if (semesterFilter !== 'all' && sem.toString() !== semesterFilter) return;

        const groupKey = `Cuatrimestre ${sem}`; // Or use group_id if available
        if (!groups[groupKey]) groups[groupKey] = [];
        groups[groupKey].push(a);
    });

    // Get unique time ranges
    const uniqueTimes = [];
    const seenTimes = new Set();
    // Sort timeslots first
    const sortedSlots = [...state.timeslots].sort((a, b) =>
        (a.start_hour * 60 + a.start_minute) - (b.start_hour * 60 + b.start_minute)
    );

    sortedSlots.forEach(t => {
        const key = `${t.start_hour}:${t.start_minute}-${t.end_hour}:${t.end_minute}`;
        if (!seenTimes.has(key)) {
            seenTimes.add(key);
            uniqueTimes.push({
                start_h: t.start_hour,
                start_m: t.start_minute,
                end_h: t.end_hour,
                end_m: t.end_minute,
                label: `${t.start_hour}:${t.start_minute.toString().padStart(2, '0')}-${t.end_hour}:${t.end_minute.toString().padStart(2, '0')}`
            });
        }
    });

    const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];

    // Render a calendar for each group
    Object.keys(groups).sort().forEach(groupName => {
        const groupAssignments = groups[groupName];

        const groupDiv = document.createElement('div');
        groupDiv.className = 'calendar-group';
        groupDiv.innerHTML = `<h3 class="calendar-group-title">${groupName}</h3>`;

        const table = document.createElement('table');
        table.className = 'calendar-table';

        // Header
        let theadHtml = '<thead><tr><th>Horario</th>';
        days.forEach(d => theadHtml += `<th>${d}</th>`);
        theadHtml += '</tr></thead>';
        table.innerHTML = theadHtml;

        const tbody = document.createElement('tbody');

        uniqueTimes.forEach(time => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td class="time-cell">${time.label}</td>`;

            days.forEach(day => {
                // Find assignment
                const assignment = groupAssignments.find(a => {
                    // Find timeslot for this assignment
                    const ts = state.timeslots.find(t => t.id === a.timeslot_id);
                    if (!ts) return false;

                    return ts.day === day &&
                        ts.start_hour === time.start_h &&
                        ts.start_minute === time.start_m;
                });

                if (assignment) {
                    const color = getColorForString(assignment.course_name);

                    tr.innerHTML += `
                        <td class="calendar-cell" style="background-color: ${color}20; border-left: 3px solid ${color};">
                            <div class="cell-content">
                                <div class="cell-course">${assignment.course_name}</div>
                                <div class="cell-prof">${assignment.professor_name}</div>
                            </div>
                        </td>
                    `;
                } else {
                    tr.innerHTML += '<td></td>';
                }
            });

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        groupDiv.appendChild(table);
        container.appendChild(groupDiv);
    });
}

function getColorForString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
    return '#' + '00000'.substring(0, 6 - c.length) + c;
}

// Override renderScheduleView to handle initial view state
const originalRenderScheduleView = renderScheduleView;
renderScheduleView = function () {
    originalRenderScheduleView();

    // Also update calendar view if active
    if (state.currentScheduleView === 'calendar') {
        renderScheduleCalendarView();
    }

    // Ensure correct container visibility
    switchScheduleView(state.currentScheduleView);
}
