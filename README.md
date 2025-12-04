# UTP Scheduler - Sistema de Horarios Universitarios

Sistema inteligente de generación de horarios universitarios que utiliza algoritmos de **backtracking** y **grafos** implementados en C++ para resolver el problema de asignación de cursos, profesores y horarios.

## 🌟 Características

- **Motor C++ de Alto Rendimiento**: Algoritmos de grafos y backtracking optimizados
- **Integración Python-C++**: Usando Cython para máxima eficiencia
- **API REST con Flask**: Backend robusto con validación de datos
- **Interfaz Web Moderna**: Diseño premium con drag-and-drop
- **Múltiples Formatos**: Soporte para CSV, JSON y Excel
- **Validación Completa**: Detección de conflictos de horario de profesores
- **Visualización Interactiva**: Vista de calendario y lista de horarios

## 🏗️ Arquitectura

```
proyect-utp/
├── cpp_core/              # Motor C++ de scheduling
│   ├── graph.hpp/cpp      # Estructura de datos de grafos
│   ├── constraints.hpp/cpp # Validación de restricciones
│   ├── scheduler_core.hpp/cpp # Algoritmo de backtracking
│   └── CMakeLists.txt     # Configuración de compilación
├── python_backend/        # Backend Python
│   ├── scheduler_wrapper.pyx # Wrapper Cython
│   ├── app.py            # API Flask
│   ├── models.py         # Modelos de datos
│   ├── data_loader.py    # Cargador multi-formato
│   ├── validators.py     # Validadores
│   └── setup.py          # Build Cython
├── frontend/             # Interfaz web
│   ├── index.html        # Estructura HTML
│   ├── styles.css        # Diseño CSS
│   └── app.js            # Lógica JavaScript
└── sample_data/          # Datos de ejemplo
    ├── courses.csv
    ├── professors.json
    ├── classrooms.json
    └── timeslots.csv
```

## 📋 Requisitos

### Windows
- **Python 3.8+**
- **Microsoft Visual C++ Build Tools** (para compilar C++)
  - Descarga: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Instala "Desktop development with C++"
- **CMake** (opcional, para compilación manual de C++)

### Dependencias Python
```bash
pip install -r requirements.txt
```

## 🚀 Instalación y Uso

### 1. Instalar Dependencias

```bash
# Instalar dependencias Python
pip install -r requirements.txt
```

### 2. Compilar la Extensión C++

```bash
cd python_backend
python setup.py build_ext --inplace
```

Si encuentras errores de compilación, asegúrate de tener instalado Visual C++ Build Tools.

### 3. Iniciar el Servidor

```bash
# Desde el directorio python_backend
python app.py
```

El servidor estará disponible en `http://localhost:5000`

### 4. Usar la Aplicación

1. Abre tu navegador en `http://localhost:5000`
2. Carga los archivos de datos:
   - **Cursos**: CSV/JSON/Excel con id, nombre, código, créditos, matrícula, prerrequisitos
   - **Profesores**: CSV/JSON con id, nombre, email, horarios disponibles
   - **Horarios**: CSV/JSON con id, día, hora inicio/fin
3. Haz clic en "Generar Horario"
4. Visualiza el horario generado en formato calendario y lista

## 📊 Formato de Datos

### Cursos (CSV)
```csv
id,name,code,credits,enrollment,prerequisites
1,Estructuras de Datos,CS201,4,35,
2,Algoritmos Avanzados,CS301,4,30,1
```

### Profesores (JSON)
```json
{
  "id": 1,
  "name": "Dr. Juan Pérez",
  "email": "jperez@utp.edu",
  "available_timeslots": [1, 2, 3, 4, 5]
}
```

### Horarios (CSV)
```csv
id,day,start_hour,start_minute,end_hour,end_minute
1,Lunes,8,0,10,0
```

## 🔧 API Endpoints

- `GET /api/status` - Estado del sistema
- `POST /api/upload` - Subir archivo de datos
- `GET /api/data/{type}` - Obtener datos cargados
- `POST /api/assign-professor` - Asignar profesor a curso
- `GET /api/validate` - Validar datos
- `POST /api/generate` - Generar horario
- `GET /api/schedule` - Obtener horario generado
- `POST /api/reset` - Reiniciar datos

## 🧪 Datos de Prueba

El directorio `sample_data/` contiene archivos de ejemplo:
- `courses.csv` - 10 cursos con prerrequisitos
- `professors.json` - 5 profesores con disponibilidad
- `classrooms.json` - 8 aulas con capacidades
- `timeslots.csv` - 20 bloques horarios

## 🎯 Algoritmos Implementados

### Grafos
- Representación con listas de adyacencia
- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- Detección de ciclos
- Ordenamiento topológico (para prerrequisitos)

### Backtracking
- Asignación recursiva de cursos a horarios
- Validación de restricciones en cada paso
- Retroceso automático ante conflictos
- Optimización de búsqueda

### Restricciones Validadas
- ✅ Conflictos de tiempo de profesores
- ✅ Disponibilidad de profesores
- ✅ Prerrequisitos de cursos

## 🎨 Características de la Interfaz

- **Diseño Dark Mode Premium**: Colores vibrantes y efectos glassmorphism
- **Drag & Drop**: Arrastra archivos para cargar datos
- **Animaciones Suaves**: Transiciones y micro-interacciones
- **Responsive**: Adaptable a móviles y tablets
- **Notificaciones en Tiempo Real**: Feedback visual de operaciones
- **Visualización Dual**: Vista de calendario y lista detallada

## 🐛 Solución de Problemas

### Error al compilar C++
- Verifica que Visual C++ Build Tools esté instalado
- Asegúrate de tener Python 3.8 o superior
- Intenta reinstalar Cython: `pip install --upgrade Cython`

### Servidor no inicia
- Verifica que el puerto 5000 esté disponible
- Comprueba que todas las dependencias estén instaladas
- Revisa los logs en la consola

### No se puede generar horario
- Asegúrate de cargar todos los tipos de datos
- Verifica que los datos estén en el formato correcto
- Revisa que haya suficientes aulas y horarios disponibles

## 📝 Licencia

Este proyecto fue desarrollado como parte del curso de Estructuras de Datos en la UTP.

## 👥 Autores

Proyecto de Estructuras de Datos - UTP 2024

---

**¡Disfruta generando horarios óptimos! 🎓📅**
