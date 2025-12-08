#!/usr/bin/env python3
"""
Script para eliminar TODOS los degradados del horario
"""
import re

def eliminar_gradientes_adicionales():
    # Leer el archivo CSS
    with open('/home/jared/proyect-utp/frontend/styles.css', 'r', encoding='utf-8', errors='ignore') as f:
        contenido = f.read()
    
    # Hacer una copia de seguridad
    with open('/home/jared/proyect-utp/frontend/styles_backup_minimalista.css', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    # Reemplazos adicionales para áreas que quedaron pendientes
    # Línea 1746 - cell-content base
    contenido = contenido.replace(
        '.cell-content {\n    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);',
        '.cell-content {\n    background: #e8eaf6;'
    )
    
    # Guardar
    with open('/home/jared/proyect-utp/frontend/styles.css', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✓ Gradientes adicionales eliminados")
    print("✓ Backup creado en styles_backup_minimalista.css")

if __name__ == '__main__':
    eliminar_gradientes_adicionales()
