
import csv
import os
import sys

# Agregar directorio actual al path para importar curriculum
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.curriculum import CURRICULUM

def generar_csv_completo():
    ruta_salida = 'courses_full.csv'
    
    encabezados = ['id', 'name', 'code', 'credits', 'enrollment', 'prerequisites', 'professor_id']
    
    cursos_planos = []
    
    # Aplanar el diccionario de curriculum
    for cuatri, cursos in CURRICULUM.items():
        for curso in cursos:
            cursos_planos.append({
                'id': curso['id'],
                'name': curso['name'],
                'code': curso['code'],
                'credits': curso['credits'],
                'enrollment': curso['enrollment'],
                'prerequisites': '', # Dejar vacío si no hay datos explícitos en este dict
                'professor_id': ''   # Vacío para que el usuario rellene
            })
            
    print(f"Generando {ruta_salida} con {len(cursos_planos)} cursos...")
    
    with open(ruta_salida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        writer.writeheader()
        writer.writerows(cursos_planos)
        
    print("¡Archivo generado con éxito!")
    print(f"Ubicación: {os.path.abspath(ruta_salida)}")

if __name__ == "__main__":
    generar_csv_completo()
