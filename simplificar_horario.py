#!/usr/bin/env python3
"""
Script para convertir el horario a un diseño minimalista
Elimina todos los degradados y usa colores sólidos
"""

def simplificar_horario():
    # Leer el archivo CSS
    with open('/home/jared/proyect-utp/frontend/styles.css', 'r', encoding='utf-8', errors='ignore') as f:
        contenido = f.read()
    
    # Reemplazos para hacer el diseño minimalista
    reemplazos = [
        # Eliminar gradientes de las tarjetas de curso (primera aparición)
        (
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Morado */',
            'background: #e8eaf6;\n    color: #3f51b5;\n    border: 1px solid #c5cae9;'
        ),
        (
            'background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); /* Rosa */',
            'background: #fce4ec;\n    color: #c2185b;\n    border: 1px solid #f8bbd0;'
        ),
        (
            'background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); /* Cyan */',
            'background: #e0f7fa;\n    color: #0097a7;\n    border: 1px solid #b2ebf2;'
        ),
        (
            'background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); /* Verde */',
            'background: #e8f5e9;\n    color: #388e3c;\n    border: 1px solid #c8e6c9;'
        ),
        (
            'background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); /* Rosa-Amarillo */',
            'background: #fff3e0;\n    color: #f57c00;\n    border: 1px solid #ffe0b2;'
        ),
        # Gradientes con !important (segunda aparición)
        (
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;\n    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;',
            'background: #e8eaf6 !important;\n    color: #3f51b5 !important;\n    border: 1px solid #c5cae9 !important;'
        ),
        (
            'background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;\n    box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3) !important;',
            'background: #fce4ec !important;\n    color: #c2185b !important;\n    border: 1px solid #f8bbd0 !important;'
        ),
        (
            'background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;\n    box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3) !important;',
            'background: #e0f7fa !important;\n    color: #0097a7 !important;\n    border: 1px solid #b2ebf2 !important;'
        ),
        (
            'background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;\n    box-shadow: 0 4px 12px rgba(67, 233, 123, 0.3) !important;',
            'background: #e8f5e9 !important;\n    color: #388e3c !important;\n    border: 1px solid #c8e6c9 !important;'
        ),
        (
            'background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;\n    box-shadow: 0 4px 12px rgba(250, 112, 154, 0.3) !important;',
            'background: #fff3e0 !important;\n    color: #f57c00 !important;\n    border: 1px solid #ffe0b2 !important;'
        ),
        # Tabla encabezados
        (
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;',
            'background: #f5f5f5 !important;'
        ),
        (
            'background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;',
            'background: #fafafa !important;'
        ),
        # Celdas de tiempo
        (
            'font-weight: 700 !important;\n    color: #495057 !important;',
            'font-weight: 500 !important;\n    color: #757575 !important;'
        ),
        # Texto de curso
        (
            'color: white !important;\n    line-height: 1.3 !important;\n    font-size: 0.85rem !important;\n    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);',
            'color: inherit !important;\n    line-height: 1.3 !important;\n    font-size: 0.85rem !important;'
        ),
        (
            'color: rgba(255, 255, 255, 0.9) !important;',
            'color: inherit !important;\n    opacity: 0.75 !important;'
        ),
        (
            'color: rgba(255, 255, 255, 0.95) !important;',
            'color: inherit !important;\n    opacity: 0.75 !important;'
        ),
        # Efectos hover y sombras
        (
            'transform: translateY(-3px);\n    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);',
            'background: #c5cae9;\n    border-color: #9fa8da;'
        ),
        (
            'transform: translateY(-4px) scale(1.02);\n    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4) !important;',
            'background: #c5cae9 !important;\n    border-color: #9fa8da !important;'
        ),
        (
            'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);',
            'border: 1px solid #c5cae9;'
        ),
        (
            'box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;',
            'border: 1px solid #c5cae9 !important;'
        ),
        # Bordes de grupo de calendario
        (
            'border-bottom: 3px solid #667eea;',
            'border-bottom: 2px solid #e0e0e0;'
        ),
        # Eliminar efectos before
        (
            '''/* Efecto de brillo  sutil */
.cell-content::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s;
}

.cell-content:hover::before {
    opacity: 1;
}''',
            ''
        ),
        # Text shadow
        (
            'text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);',
            ''
        ),
        # Encabezado de tabla color
        (
            'color: white !important;\n    font-weight: 700 !important;',
            'color: #616161 !important;\n    font-weight: 600 !important;'
        ),
    ]
    
    # Aplicar todos los reemplazos
    for original, nuevo in reemplazos:
        contenido = contenido.replace(original, nuevo)
    
    # Guardar el archivo modificado
    with open('/home/jared/proyect-utp/frontend/styles.css', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✓ Horario convertido a diseño minimalista")
    print("✓ Eliminados todos los degradados de colores")
    print("✓ Aplicados colores sólidos y sobrios")

if __name__ == '__main__':
    simplificar_horario()
