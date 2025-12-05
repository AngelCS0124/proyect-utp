/**
 * Visualización del Algoritmo de Scheduling
 * Usa Vis.js para renderizar grafos interactivos
 */

// Variables globales para visualización
let datosVisualizacion = null;
let network = null;
let vistaActual = 'conflictos';

// Colores por cuatrimestre
const COLORES_CUATRIMESTRE = {
    1: '#ef4444',  // Rojo
    2: '#f97316',  // Naranja
    3: '#f59e0b',  // Ámbar
    4: '#eab308',  // Amarillo
    5: '#84cc16',  // Lima
    6: '#22c55e',  // Verde
    7: '#10b981',  // Esmeralda
    8: '#14b8a6',  // Teal
    9: '#06b6d4',  // Cian
    10: '#0ea5e9'  // Azul
};

/**
 * Mostrar modal de visualización y cargar datos
 */
async function mostrarVisualizacion() {
    try {
        // Cargar datos del backend
        const respuesta = await fetch(`${API_BASE}/visualization`);
        
        if (!respuesta.ok) {
            const error = await respuesta.json();
            showNotification('Error', error.error || 'No se pudo cargar la visualización', 'error');
            return;
        }
        
        datosVisualizacion = await respuesta.json();
        
        // Mostrar modal
        document.getElementById('visualization-modal').style.display = 'flex';
        
        // Actualizar estadísticas
        actualizarEstadisticasViz();
        
        // Renderizar vista por defecto (conflictos)
        vistaActual = 'conflictos';
        renderizarGrafoConflictos();
        
    } catch (error) {
        showNotification('Error', `Error al cargar visualización: ${error.message}`, 'error');
    }
}

/**
 * Cerrar modal de visualización
 */
function cerrarVisualizacion() {
    document.getElementById('visualization-modal').style.display = 'none';
    if (network) {
        network.destroy();
        network = null;
    }
}

/**
 * Cambiar entre vistas de visualización
 */
function cambiarVistaViz(vista) {
    vistaActual = vista;
    
    // Actualizar tabs activos
    document.querySelectorAll('.viz-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-viz="${vista}"]`).classList.add('active');
    
    // Renderizar vista correspondiente
    switch(vista) {
        case 'conflictos':
            renderizarGrafoConflictos();
            break;
        case 'restricciones':
            renderizarRedRestricciones();
            break;
        case 'backtracking':
            renderizarArbolBacktracking();
            break;
    }
}

/**
 * Renderizar grafo de conflictos
 */
function renderizarGrafoConflictos() {
    const datos = datosVisualizacion.grafo_conflictos;
    
    // Configurar nodos
    const nodos = new vis.DataSet(datos.nodos.map(n => ({
        id: n.id,
        label: n.label,
        title: `${n.titulo}\nCuatrimestre: ${n.cuatrimestre}°\nCréditos: ${n.creditos}`,
        group: n.grupo,
        color: {
            background: COLORES_CUATRIMESTRE[n.cuatrimestre] || '#6b7280',
            border: '#ffffff',
            highlight: {
                background: COLORES_CUATRIMESTRE[n.cuatrimestre] || '#6b7280',
                border: '#000000'
            }
        },
        font: {
            color: '#ffffff',
            size: 14,
            face: 'Inter'
        }
    })));
    
    // Configurar aristas
    const aristas = new vis.DataSet(datos.aristas.map(a => ({
        from: a.desde,
        to: a.hasta,
        label: a.label,
        color: {
            color: a.color,
            highlight: a.color
        },
        dashes: true,
        width: 2
    })));
    
    // Crear red
    const container = document.getElementById('network-container');
    const data = { nodes: nodos, edges: aristas };
    const options = {
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -3000,
                springLength: 150,
                springConstant: 0.04
            },
            stabilization: {
                iterations: 150
            }
        },
        nodes: {
            shape: 'dot',
            size: 25,
            borderWidth: 3,
            shadow: true
        },
        edges: {
            smooth: {
                type: 'continuous'
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            navigationButtons: true,
            keyboard: true
        }
    };
    
    // Destruir red anterior si existe
    if (network) {
        network.destroy();
    }
    
    network = new vis.Network(container, data, options);
    
    // Actualizar leyenda
    actualizarLeyenda('conflictos');
}

/**
 * Renderizar red de restricciones
 */
function renderizarRedRestricciones() {
    const datos = datosVisualizacion.red_restricciones;
    
    // Configurar nodos con colores por tipo
    const nodos = new vis.DataSet(datos.nodos.map(n => {
        let color, shape;
        
        if (n.tipo === 'curso') {
            color = '#3b82f6'; // Azul
            shape = 'dot';
        } else if (n.tipo === 'profesor') {
            color = '#8b5cf6'; // Morado
            shape = 'diamond';
        } else {
            color = '#10b981'; // Verde
            shape = 'square';
        }
        
        return {
            id: n.id,
            label: n.label,
            title: `Tipo: ${n.tipo}\n${n.label}`,
            color: {
                background: color,
                border: '#ffffff'
            },
            shape: shape,
            size: 20,
            font: {
                color: '#ffffff',
                size: 12
            }
        };
    })));
    
    // Configurar aristas
    const aristas = new vis.DataSet(datos.aristas.map(a => ({
        from: a.desde,
        to: a.hasta,
        color: {
            color: a.color,
            highlight: a.color
        },
        width: 2,
        arrows: {
            to: {
                enabled: true,
                scaleFactor: 0.5
            }
        }
    })));
    
    // Crear red con layout jerárquico
    const container = document.getElementById('network-container');
    const data = { nodes: nodos, edges: aristas };
    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'UD',
                sortMethod: 'directed',
                levelSeparation: 150,
                nodeSpacing: 100
            }
        },
        physics: {
            enabled: false
        },
        nodes: {
            borderWidth: 2,
            shadow: true
        },
        edges: {
            smooth: {
                type: 'cubicBezier'
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            navigationButtons: true
        }
    };
    
    if (network) {
        network.destroy();
    }
    
    network = new vis.Network(container, data, options);
    
    actualizarLeyenda('restricciones');
}

/**
 * Renderizar árbol de backtracking
 */
function renderizarArbolBacktracking() {
    const datos = datosVisualizacion.arbol_backtracking;
    
    // Configurar nodos
    const nodos = new vis.DataSet(datos.nodos.map(n => {
        let color;
        
        if (n.tipo === 'raiz') {
            color = '#6b7280'; // Gris
        } else if (n.tipo === 'asignacion_exitosa') {
            color = '#10b981'; // Verde
        } else {
            color = '#ef4444'; // Rojo (backtrack)
        }
        
        return {
            id: n.id,
            label: n.label,
            title: `Nivel: ${n.nivel}\n${n.label}`,
            level: n.nivel,
            color: {
                background: color,
                border: '#ffffff'
            },
            shape: 'box',
            font: {
                color: '#ffffff',
                size: 12
            }
        };
    })));
    
    // Configurar aristas
    const aristas = new vis.DataSet(datos.aristas.map(a => ({
        from: a.desde,
        to: a.hasta,
        color: {
            color: a.tipo === 'exito' ? '#10b981' : '#ef4444'
        },
        width: 2,
        arrows: {
            to: {
                enabled: true,
                scaleFactor: 0.5
            }
        },
        dashes: a.tipo !== 'exito'
    })));
    
    // Crear red con layout jerárquico
    const container = document.getElementById('network-container');
    const data = { nodes: nodos, edges: aristas };
    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'UD',
                sortMethod: 'directed',
                levelSeparation: 100,
                nodeSpacing: 80
            }
        },
        physics: {
            enabled: false
        },
        nodes: {
            borderWidth: 2,
            shadow: true
        },
        edges: {
            smooth: {
                type: 'cubicBezier'
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            navigationButtons: true
        }
    };
    
    if (network) {
        network.destroy();
    }
    
    network = new vis.Network(container, data, options);
    
    actualizarLeyenda('backtracking');
}

/**
 * Actualizar leyenda según la vista
 */
function actualizarLeyenda(vista) {
    const legendContent = document.getElementById('legend-content');
    
    if (vista === 'conflictos') {
        legendContent.innerHTML = `
            <div class="legend-item">
                <div class="legend-line" style="background: #ef4444;"></div>
                <span>Conflicto: Mismo Profesor</span>
            </div>
            <div class="legend-item">
                <div class="legend-node" style="background: #10b981;"></div>
                <span>Curso sin conflictos</span>
            </div>
            <div class="legend-item">
                <div class="legend-node" style="background: #ef4444;"></div>
                <span>1° Cuatrimestre</span>
            </div>
            <div class="legend-item">
                <div class="legend-node" style="background: #0ea5e9;"></div>
                <span>10° Cuatrimestre</span>
            </div>
        `;
    } else if (vista === 'restricciones') {
        legendContent.innerHTML = `
            <div class="legend-item">
                <div class="legend-node circle" style="background: #3b82f6;"></div>
                <span>Curso</span>
            </div>
            <div class="legend-item">
                <div class="legend-node diamond" style="background: #8b5cf6;"></div>
                <span>Profesor</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background: #10b981;"></div>
                <span>Asignación</span>
            </div>
        `;
    } else if (vista === 'backtracking') {
        legendContent.innerHTML = `
            <div class="legend-item">
                <div class="legend-node box" style="background: #6b7280;"></div>
                <span>Nodo Raíz</span>
            </div>
            <div class="legend-item">
                <div class="legend-node box" style="background: #10b981;"></div>
                <span>Asignación Exitosa</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background: #10b981;"></div>
                <span>Camino Exitoso</span>
            </div>
        `;
    }
}

/**
 * Actualizar estadísticas de visualización
 */
function actualizarEstadisticasViz() {
    if (!datosVisualizacion || !datosVisualizacion.estadisticas) return;
    
    const stats = datosVisualizacion.estadisticas;
    
    document.getElementById('stat-cursos').textContent = stats.total_cursos || 0;
    document.getElementById('stat-profesores').textContent = stats.total_profesores || 0;
    document.getElementById('stat-conflictos').textContent = stats.conflictos_detectados || 0;
    document.getElementById('stat-asignaciones').textContent = stats.asignaciones_exitosas || 0;
}

/**
 * Exportar visualización como imagen
 */
function exportarVisualizacion() {
    if (!network) {
        showNotification('Error', 'No hay visualización para exportar', 'error');
        return;
    }
    
    // Capturar canvas del network
    const canvas = document.querySelector('#network-container canvas');
    if (canvas) {
        canvas.toBlob(blob => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `visualizacion-${vistaActual}-${Date.now()}.png`;
            link.click();
            URL.revokeObjectURL(url);
            showNotification('¡Éxito!', 'Imagen exportada correctamente', 'success');
        });
    }
}

/**
 * Exportar horario (placeholder)
 */
function exportarHorario() {
    showNotification('Info', 'Función de exportación en desarrollo', 'info');
}

// Exponer funciones globalmente
window.mostrarVisualizacion = mostrarVisualizacion;
window.cerrarVisualizacion = cerrarVisualizacion;
window.cambiarVistaViz = cambiarVistaViz;
window.exportarVisualizacion = exportarVisualizacion;
window.exportarHorario = exportarHorario;
