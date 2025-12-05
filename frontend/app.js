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
    dataLoaded: {
        courses: false,
        professors: false,
        timeslots: false
    }
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
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
            updateUI();
        } else {
            showNotification('Error', result.error || 'Error al cargar archivo', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error al subir archivo: ${error.message}`, 'error');
    }
}

async function loadData(dataType) {
    try {
        const response = await fetch(`${API_BASE}/data/${dataType}`);
        const result = await response.json();
        if (response.ok) state[dataType] = result.data;
    } catch (error) {
        console.error(`Error loading ${dataType}:`, error);
    }
}

// ===== Maestros View =====
function renderProfessorsTable() {
    const tbody = document.getElementById('professors-list');
    tbody.innerHTML = '';

    if (state.professors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No hay profesores cargados</td></tr>';
        return;
    }

    state.professors.forEach(prof => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${prof.id}</td>
            <td>
                <div style="font-weight: 600;">${prof.name}</div>
                <div style="font-size: 0.8rem; color: var(--text-gray);">Senior Lecturer</div>
            </td>
            <td>${prof.email || 'N/A'}</td>
            <td>3/wk</td>
            <td><span class="badge badge-ready">Actualizado</span></td>
            <td>
                <button class="action-btn edit"><i class="fas fa-pen"></i></button>
                <button class="action-btn delete"><i class="fas fa-trash"></i></button>
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

    renderAvailabilityGrid([]);
}

function loadProfessorAvailability() {
    const select = document.getElementById('availability-professor-select');
    const profId = parseInt(select.value);
    const professor = state.professors.find(p => p.id === profId);

    if (professor) {
        document.getElementById('availability-email').value = professor.email;
        renderAvailabilityGrid(professor.available_timeslots);
    } else {
        document.getElementById('availability-email').value = '';
        renderAvailabilityGrid([]);
    }
}

function renderAvailabilityGrid(availableSlots) {
    const tbody = document.getElementById('availability-grid');
    tbody.innerHTML = '';

    // Time ranges (simplified for demo)
    const ranges = [
        { start: 8, end: 10 },
        { start: 10, end: 12 },
        { start: 12, end: 14 },
        { start: 14, end: 16 },
        { start: 16, end: 18 }
    ];

    const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];

    ranges.forEach(range => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${range.start}:00 - ${range.end}:00</td>`;

        days.forEach(day => {
            // Check if this slot is available (mock logic: check if any timeslot matches day/hour)
            // In real app, we'd match against state.timeslots IDs
            const isAvailable = Math.random() > 0.5; // Mock for visual
            const statusClass = isAvailable ? 'on' : 'off';
            const statusText = isAvailable ? 'On' : 'Off';

            tr.innerHTML += `
                <td>
                    <button class="toggle-btn ${statusClass}" onclick="toggleAvailability(this)">
                        ${statusText}
                    </button>
                </td>
            `;
        });
        tbody.appendChild(tr);
    });
}

function toggleAvailability(btn) {
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

// ===== Schedule Generation =====
async function generateSchedule() {
    const btn = document.getElementById('generate-btn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';

    try {
        const response = await fetch(`${API_BASE}/generate`, { method: 'POST' });
        const result = await response.json();

        if (response.ok && result.success) {
            state.schedule = result.schedule;
            showNotification('¡Horario Generado!', 'El horario se ha generado correctamente.', 'success');
            // Switch to Horario view
            document.querySelector('[data-view="horario"]').click();
        } else {
            showNotification('Error', result.error || 'No se pudo generar el horario', 'error');
        }
    } catch (error) {
        showNotification('Error', `Error al generar: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

function renderScheduleView() {
    const emptyState = document.getElementById('no-schedule-msg');
    const table = document.getElementById('schedule-table');
    const tbody = document.getElementById('schedule-body');

    if (!state.schedule) {
        emptyState.style.display = 'block';
        table.style.display = 'none';
        return;
    }

    emptyState.style.display = 'none';
    table.style.display = 'table';
    tbody.innerHTML = '';

    state.schedule.assignments.forEach(assignment => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div style="font-weight: 600;">${assignment.course_name}</div>
                <div style="font-size: 0.85rem; color: var(--text-gray);">${assignment.course_code}</div>
            </td>
            <td>${assignment.professor_name}</td>
            <td><span class="badge badge-ready">${assignment.timeslot_display}</span></td>
            <td>A1</td>
        `;
        tbody.appendChild(tr);
    });
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

        setTimeout(updateUI, 500);
    } catch (error) {
        console.error("Connection error", error);
    }
}

function updateUI() {
    document.getElementById('course-count').textContent = state.courses.length;
    document.getElementById('professor-count').textContent = state.professors.length;
    document.getElementById('timeslot-count').textContent = state.timeslots.length;

    // Update upload cards status
    updateCardState('course-upload', state.dataLoaded.courses);
    updateCardState('professor-upload', state.dataLoaded.professors);
    updateCardState('timeslot-upload', state.dataLoaded.timeslots);
}

function updateCardState(inputId, loaded) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const card = input.closest('.upload-card');
    if (loaded) {
        card.style.borderColor = 'var(--success)';
        card.querySelector('.upload-icon').style.color = 'var(--success)';
    }
}

function showNotification(title, message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.className = `notification ${type}`;
    notification.innerHTML = `<strong>${title}</strong><br>${message}`;
    notification.style.display = 'block';
    setTimeout(() => notification.style.display = 'none', 5000);
}
