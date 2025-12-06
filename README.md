# Sistema de Horarios Universitarios (UTP Scheduler)

Sistema inteligente de generación de horarios universitarios que utiliza algoritmos de **backtracking** y **grafos** (implementados en C++) para resolver eficientemente la asignación de cursos, profesores y horarios.

## 🌟 Características

- **Motor C++ de Alto Rendimiento**: Algoritmos optimizados para resolución de conflictos.
- **Integración Python-C++**: Uso de Cython para máxima eficiencia.
- **API REST con Flask**: Backend robusto, modular y validado.
- **Interfaz Web Moderna**: Diseño intuitivo con visualización de grafos.
- **Múltiples Formatos**: Soporte para CSV, JSON y Excel.
- **Validación Completa**: Detección de conflictos de horario y restricciones.
- **Visualización Interactiva**: Grafos de dependencias y calendario.

## 🏗️ Arquitectura del Proyecto

El proyecto ha sido traducido completamente al español en su estructura interna:

```
proyect-utp/
├── cpp_core/                  # Motor C++ de scheduling (Core original)
├── python_backend/            # Backend Python
│   ├── aplicacion.py          # API Flask (Punto de entrada)
│   ├── cargador_datos.py      # Cargador multi-formato
│   ├── validadores.py         # Sistema de validación
│   ├── modelos/               # Modelos de datos (Curso, Profesor, etc.)
│   ├── servicios/             # Lógica de negocio y algoritmos
│   ├── configuracion/         # Configuración del sistema
│   └── datos/                 # Datos estáticos
├── frontend/                  # Interfaz web (HTML/JS/CSS)
├── datos_muestra/             # Datos de ejemplo en español
└── generar_datos.py           # Script para crear datos de prueba
```

## 📋 Requisitos

### Sistema
- **Python 3.8+**
- **Microsoft Visual C++ Build Tools** (para compilar motor C++)

### Dependencias Python
```bash
pip install -r requirements.txt
```

## 🚀 Instalación y Uso

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Compilar Extensión C++ (Opcional pero recomendado)

```bash
cd python_backend
python setup.py build_ext --inplace
```
*Si no se compila, el sistema usará una versión Python más lenta.*

### 3. Iniciar el Servidor

```bash
cd python_backend
python aplicacion.py
```

El servidor estará disponible en `http://localhost:5000`

### 4. Usar la Aplicación

1. Abre tu navegador en `http://localhost:5000`
2. Carga archivos de datos (o usa los valores por defecto):
   - **Cursos**: CSV/JSON/Excel
   - **Profesores**: CSV/JSON
3. Haz clic en "Generar Horario"
4. Visualiza los resultados en el calendario interactivo

## 📊 Formato de Datos (Español)

### Cursos (CSV)
```csv
id,nombre,codigo,creditos,matricula,prerrequisitos,id_profesor
1,Estructuras de Datos,CS201,4,35,,1
2,Algoritmos Avanzados,CS301,4,30,1,2
```

### Profesores (JSON)
```json
[
  {
    "id": 1,
    "nombre": "Dr. Juan Pérez",
    "email": "juan@utp.edu.mx",
    "bloques_disponibles": [1, 2, 3, 4, 5]
  }
]
```

## 🛠️ Scripts de Utilidad

- `python generar_datos.py`: Crea archivos de prueba en `datos_muestra/`
- `python verificar_integracion.py`: Ejecuta pruebas automáticas del sistema

---
*Proyecto traducido y optimizado - Diciembre 2025*
