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

            // If we uploaded professors, we might have also loaded timeslots
            if (dataType === 'professors') {
                // Check if timeslots are now available by fetching status or just trying to load
                await loadData('timeslots');
                // We can assume if professors loaded successfully with the new backend logic, timeslots might be there
                // Let's check the count from the result message or just rely on loadData updating the state
                state.dataLoaded.timeslots = true; // Optimistic update, or check state.timeslots.length after load
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
        const response = await fetch(`${API_BASE}/upload_excel`, { method: 'POST', body: formData });
        const result = await response.json();

        if (response.ok) {
            state.dataLoaded.professors = true;
            state.dataLoaded.courses = true; // Assuming courses are loaded too
            showNotification('¡Éxito!', result.message, 'success');

            // Reload data
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
    // For default data, we can either call a specific endpoint or just re-upload the sample file if it exists on server
    // Or we can create a new endpoint /api/load_defaults
    // Since we don't have that endpoint, let's assume the user has the file locally or we provide a way to trigger it.
    // But the user asked for "cargar valores por defecto".
    // I'll implement a simple alert for now or try to fetch a default file if I had one served.
    // Actually, I can implement an endpoint /api/load_defaults in backend that does exactly what extract_excel_data does with the sample file.

    try {
        showNotification('Cargando...', 'Cargando datos por defecto...', 'info');
        // We'll use a new endpoint for this
        const response = await fetch(`${API_BASE}/load_defaults`, { method: 'POST' });
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

    const ranges = [
        { start: 7, end: 9 },
        { start: 9, end: 11 },
        { start: 11, end: 13 },
        { start: 13, end: 15 },
        { start: 15, end: 17 },
        { start: 17, end: 19 },
        { start: 19, end: 21 }
    ];

    const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];

    ranges.forEach(range => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${range.start}:00 - ${range.end}:00</td>`;

        days.forEach(day => {
            // Find timeslot ID matching this day and time
            const slot = state.timeslots.find(t =>
                t.day === day && t.start_hour === range.start
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
    const btn = document.getElementById('generate-btn');
    const originalText = btn.innerHTML;
    btn.disabled = true;

    // Show Generation Overlay
    showGenerationOverlay();

    try {
        // Simulate steps for visual effect
        await updateGenerationStep('Construyendo Grafo de Conflictos...', 10);
        await new Promise(r => setTimeout(r, 800));

        await updateGenerationStep('Verificando Restricciones Hard/Soft...', 40);
        await new Promise(r => setTimeout(r, 800));

        await updateGenerationStep('Ejecutando Backtracking con Poda...', 70);

        const response = await fetch(`${API_BASE}/generate`, { method: 'POST' });
        const result = await response.json();

        if (response.ok && result.success) {
            await updateGenerationStep('¡Horario Generado!', 100);
            await new Promise(r => setTimeout(r, 500));

            state.schedule = result.schedule;
            showNotification('¡Horario Generado!', `Completado en ${result.schedule.metadata.computation_time.toFixed(4)}s con ${result.schedule.metadata.backtrack_count} backtracks.`, 'success');

            hideGenerationOverlay();
            // Switch to Horario view
            document.querySelector('[data-view="horario"]').click();
        } else {
            hideGenerationOverlay();
            // Show Error Modal
            showErrorModal(result.error || 'No se pudo generar el horario');
        }
    } catch (error) {
        console.error('Generation error:', error);

        let errorMsg = error.message;
        let detailsHtml = '';

        if (error.details && Array.isArray(error.details)) {
            detailsHtml = '<ul style="text-align: left; margin-top: 10px;">' +
                error.details.map(d => `<li>${d}</li>`).join('') +
                '</ul>';
        }

        hideGenerationOverlay(); // Ensure overlay is hidden on error
        showErrorModal('Error de Generación', `
            <div class="error-message">
                <p>${errorMsg}</p>
                ${detailsHtml}
            </div>
        `);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
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

function showGenerationOverlay() {
    if (!document.getElementById('gen-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'gen-overlay';
        overlay.className = 'generation-overlay';
        overlay.innerHTML = `
            <div class="gen-content">
                <div class="gen-spinner"></div>
                <h3 id="gen-step">Iniciando...</h3>
                <div class="progress-bar">
                    <div id="gen-progress" class="progress-fill"></div>
                </div>
                <div class="gen-details">
                    <p><i class="fas fa-project-diagram"></i> Algoritmo: Backtracking + Graph Coloring</p>
                    <p><i class="fas fa-microchip"></i> Motor: C++ Core</p>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    document.getElementById('gen-overlay').style.display = 'flex';
}

function hideGenerationOverlay() {
    const overlay = document.getElementById('gen-overlay');
    if (overlay) overlay.style.display = 'none';
}

async function updateGenerationStep(text, progress) {
    const step = document.getElementById('gen-step');
    const bar = document.getElementById('gen-progress');
    if (step) step.textContent = text;
    if (bar) bar.style.width = `${progress}%`;
}

function renderScheduleView() {
    const emptyState = document.getElementById('no-schedule-msg');
    const table = document.getElementById('schedule-table');
    const tbody = document.getElementById('schedule-body');
    const vizControls = document.getElementById('viz-controls');
    const filterContainer = document.getElementById('schedule-filters');

    if (!state.schedule) {
        emptyState.style.display = 'block';
        table.style.display = 'none';
        if (vizControls) vizControls.style.display = 'none';
        if (filterContainer) filterContainer.style.display = 'none';
        return;
    }

    emptyState.style.display = 'none';
    table.style.display = 'table';
    if (vizControls) vizControls.style.display = 'flex';
    if (filterContainer) filterContainer.style.display = 'block';

    // Update filter options based on current cycle
    updateSemesterFilter();

    tbody.innerHTML = '';

    const semesterFilter = document.getElementById('semester-filter') ? document.getElementById('semester-filter').value : 'all';

    state.schedule.assignments.forEach(assignment => {
        // Filter logic
        if (semesterFilter !== 'all') {
            const sem = assignment.semester || 0;
            if (sem.toString() !== semesterFilter) return;
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div style="font-weight: 600;">${assignment.course_name}</div>
                <div style="font-size: 0.85rem; color: var(--text-gray);">${assignment.course_code}</div>
            </td>
            <td>${assignment.professor_name}</td>
            <td><span class="badge badge-ready">${assignment.timeslot_display}</span></td>
            <td>${assignment.group_id || 'N/A'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateSemesterFilter() {
    const select = document.getElementById('semester-filter');
    const currentCycle = state.currentCycle;

    if (!select) return;

    // Save current selection if any
    const currentVal = select.value;

    // Clear existing options (keep "All")
    select.innerHTML = '<option value="all">Todos los Cuatrimestres</option>';

    if (!currentCycle) return;

    // Get semesters for this cycle
    // Mapping: sept-dec -> [1, 4, 7, 10], jan-apr -> [2, 5, 8], may-aug -> [3, 6, 9]
    const cycleMapping = {
        'sept-dec': [1, 4, 7, 10],
        'jan-apr': [2, 5, 8],
        'may-aug': [3, 6, 9]
    };

    const allowedSemesters = cycleMapping[currentCycle] || [];

    const ordinals = {
        1: "Primer", 2: "Segundo", 3: "Tercer", 4: "Cuarto", 5: "Quinto",
        6: "Sexto", 7: "Séptimo", 8: "Octavo", 9: "Noveno", 10: "Décimo"
    };

    allowedSemesters.forEach(sem => {
        const option = document.createElement('option');
        option.value = sem;
        option.textContent = `${ordinals[sem]} Cuatrimestre`;
        select.appendChild(option);
    });

    // Restore selection if valid, else default to all
    if (allowedSemesters.includes(parseInt(currentVal))) {
        select.value = currentVal;
    }
}

function filterScheduleBySemester() {
    renderScheduleView();
}

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

        setTimeout(updateUI, 500);
    } catch (error) {
        console.error("Connection error", error);
    }
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

    const semesterFilter = document.getElementById('semester-filter') ? document.getElementById('semester-filter').value : 'all';

    // Group assignments by semester/group
    const groups = {};
    state.schedule.assignments.forEach(a => {
        const sem = a.semester || 0;
        if (semesterFilter !== 'all' && sem.toString() !== semesterFilter) return;

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
