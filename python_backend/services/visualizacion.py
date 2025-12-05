"""
Visualización de estructuras de datos del algoritmo de scheduling
Genera datos para visualización del grafo de conflictos y árbol de backtracking
"""

def generar_datos_visualizacion(cursos, profesores, bloques_tiempo, asignaciones):
    """
    Genera datos de visualización de las estructuras de datos del algoritmo
    
    Returns:
        dict con nodos y aristas para visualización
    """
    
    # Grafo de conflictos entre cursos
    grafo_conflictos = {
        'nodos': [],
        'aristas': []
    }
    
    # Crear nodos para cada curso
    for curso in cursos:
        grafo_conflictos['nodos'].append({
            'id': f'curso_{curso.id}',
            'label': curso.code,
            'titulo': curso.name,
            'tipo': 'curso',
            'cuatrimestre': curso.cuatrimestre,
            'creditos': curso.credits,
            'grupo': curso.cuatrimestre  # Para colorear por cuatrimestre
        })
    
    # Crear aristas de conflicto (profesores compartidos, horarios solapados)
    for i, curso1 in enumerate(cursos):
        for curso2 in cursos[i+1:]:
            # Conflicto si comparten profesor
            if curso1.professor_id and curso2.professor_id:
                if curso1.professor_id == curso2.professor_id:
                    grafo_conflictos['aristas'].append({
                        'desde': f'curso_{curso1.id}',
                        'hasta': f'curso_{curso2.id}',
                        'tipo': 'profesor_compartido',
                        'label': 'Mismo Profesor',
                        'color': '#ef4444'
                    })
    
    # Red de restricciones
    red_restricciones = {
        'nodos': [],
        'aristas': []
    }
    
    # Nodos: Cursos, Profesores, Bloques de Tiempo
    for curso in cursos:
        red_restricciones['nodos'].append({
            'id': f'c_{curso.id}',
            'label': curso.code,
            'tipo': 'curso',
            'grupo': 1
        })
    
    for profesor in profesores:
        red_restricciones['nodos'].append({
            'id': f'p_{profesor.id}',
            'label': profesor.name[:15],
            'tipo': 'profesor',
            'grupo': 2
        })
    
    # Aristas: Asignaciones y disponibilidad
    for asignacion in asignaciones:
        # Curso -> Profesor
        red_restricciones['aristas'].append({
            'desde': f'c_{asignacion["course_id"]}',
            'hasta': f'p_{asignacion["professor_id"]}',
            'tipo': 'asignacion',
            'color': '#10b981'
        })
    
    # Árbol de backtracking (simplificado)
    arbol_backtracking = {
        'nodos': [],
        'aristas': []
    }
    
    # Nodo raíz
    arbol_backtracking['nodos'].append({
        'id': 'root',
        'label': 'Inicio',
        'tipo': 'raiz',
        'nivel': 0
    })
    
    # Simular niveles del árbol (uno por curso asignado)
    for i, asignacion in enumerate(asignaciones[:10]):  # Limitar a 10 para visualización
        nodo_id = f'nivel_{i}'
        arbol_backtracking['nodos'].append({
            'id': nodo_id,
            'label': f'{asignacion["course_code"]}',
            'tipo': 'asignacion_exitosa',
            'nivel': i + 1,
            'grupo': 3
        })
        
        # Arista desde nodo padre
        padre_id = f'nivel_{i-1}' if i > 0 else 'root'
        arbol_backtracking['aristas'].append({
            'desde': padre_id,
            'hasta': nodo_id,
            'tipo': 'exito'
        })
    
    return {
        'grafo_conflictos': grafo_conflictos,
        'red_restricciones': red_restricciones,
        'arbol_backtracking': arbol_backtracking,
        'estadisticas': {
            'total_cursos': len(cursos),
            'total_profesores': len(profesores),
            'total_bloques': len(bloques_tiempo),
            'asignaciones_exitosas': len(asignaciones),
            'conflictos_detectados': len(grafo_conflictos['aristas'])
        }
    }
