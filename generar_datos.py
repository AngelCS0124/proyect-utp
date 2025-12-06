import csv
import os

# Asegurar que existe la carpeta de datos de muestra
os.makedirs('datos_muestra', exist_ok=True)

# 1. Generar Profesores (5 Profesores)
# Disponibilidad completa para asegurar solvabilidad
# Bloques del 1 al 35 (5 días * 7 bloques, o similar según configuración)
bloques_completos = list(range(1, 36))

profesores = [
    {"id": 1, "nombre": "Dr. Juan Pérez", "email": "juan.perez@utp.edu", "bloques_disponibles": bloques_completos},
    {"id": 2, "nombre": "Dra. María González", "email": "maria.gonzalez@utp.edu", "bloques_disponibles": bloques_completos},
    {"id": 3, "nombre": "Ing. Carlos Rodríguez", "email": "carlos.rodriguez@utp.edu", "bloques_disponibles": bloques_completos},
    {"id": 4, "nombre": "MSc. Ana Martínez", "email": "ana.martinez@utp.edu", "bloques_disponibles": bloques_completos},
    {"id": 5, "nombre": "Lic. Pedro Sánchez", "email": "pedro.sanchez@utp.edu", "bloques_disponibles": bloques_completos}
]

import json
with open('datos_muestra/profesores.json', 'w', encoding='utf-8') as f:
    json.dump(profesores, f, ensure_ascii=False, indent=2)

print("Generado datos_muestra/profesores.json")

# 2. Generar Cursos (5 Cursos, 1 por Profesor)
cursos = [
    # id, nombre, codigo, creditos, matricula, prerrequisitos, id_profesor
    [1, "Matemáticas Discretas", "MAT101", 3, 30, "", 1], # Dr. Juan
    [2, "Estructura de Datos", "CS102", 4, 25, "1", 2],   # Dra. María
    [3, "Inglés I", "LANG101", 2, 20, "", 3],             # Ing. Carlos
    [4, "Programación Web", "CS201", 3, 30, "2", 4],      # MSc. Ana
    [5, "Base de Datos", "CS202", 3, 28, "2", 5]          # Lic. Pedro
]

with open('datos_muestra/cursos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'nombre', 'codigo', 'creditos', 'matricula', 'prerrequisitos', 'id_profesor'])
    writer.writerows(cursos)

print("Generado datos_muestra/cursos.csv")

# 3. Generar Bloques de Tiempo (CSV)
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
bloques = []
id_bloque = 1
for dia in dias:
    # 9 bloques por día según nueva configuración
    horas_inicio = [7, 7, 8, 9, 11, 12, 13, 14, 14]
    minutos_inicio = [0, 55, 50, 45, 10, 5, 0, 0, 55]
    
    for i in range(len(horas_inicio)):
        h_ini = horas_inicio[i]
        m_ini = minutos_inicio[i]
        
        # Calculamos fin sumando 54 minutos aprox (simplificado)
        m_fin = m_ini + 54
        h_fin = h_ini + m_fin // 60
        m_fin = m_fin % 60
        
        bloques.append({
            "id": id_bloque, 
            "dia": dia, 
            "hora_inicio": h_ini, 
            "minuto_inicio": m_ini, 
            "hora_fin": h_fin, 
            "minuto_fin": m_fin
        })
        id_bloque += 1

with open('datos_muestra/bloques_tiempo.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "dia", "hora_inicio", "minuto_inicio", "hora_fin", "minuto_fin"])
    writer.writeheader()
    writer.writerows(bloques)

print("Generado datos_muestra/bloques_tiempo.csv")
