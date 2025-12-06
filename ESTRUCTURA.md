# Estructura del Proyecto

Este documento describe la organización de carpetas y archivos del sistema, reflejando la traducción completa al español de los componentes del backend.

## 📂 Raíz del Proyecto
- **`README.md`**: Documentación principal y guía de uso.
- **`generar_datos.py`**: Script para crear datos de prueba en la carpeta `datos_muestra`.
- **`verificar_integracion.py`**: Script para validar que todos los componentes funcionan correctamente.
- **`datos_muestra/`**: Contiene archivos CSV y JSON con datos en formato español (`cursos.csv`, `profesores.json`, etc.).
- **`frontend/`**: Código de la interfaz web (HTML, CSS, JS).

## 🐍 Backend Python (`python_backend/`)

### Módulos Principales
- **`aplicacion.py`**: **Punto de entrada**. Servidor Flask que maneja la API y las peticiones web.
- **`cargador_datos.py`**: Clase `CargadorDatos` para leer CSV/JSON/Excel en español.
- **`validadores.py`**: Clase `Validador` para asegurar integridad de los datos.

### Paquetes
- **`modelos/`**: Definición de objetos de negocio.
  - `curso.py`: Lógica de cursos y prerrequisitos.
  - `profesor.py`: Datos de profesores y disponibilidad.
  - `bloque_tiempo.py`: Definición de slots de horario.
  - `horario.py`: Estructura del horario generado.
  
- **`servicios/`**: Lógica de negocio y algoritmos auxiliares.
  - `scheduling_helpers.py`: Ayudantes para restricciones de horario.
  - `visualizacion.py`: Generación de datos para grafos.
  - `extractor_excel.py`: Lectura específica de formatos Excel institucionales.

- **`configuracion/`**: Constantes y parámetros del sistema.
  - `bloques_tiempo.py`: Definición de horas y días válidos.

- **`datos/`**: Datos estáticos del plan de estudios.
  - `curriculum.py`: Lista maestra de materias.

## ⚙️ Núcleo C++ (`cpp_core/`)
Motor de alto rendimiento para el algoritmo de scheduling. Se compila y se integra con Python mediante `scheduler_wrapper`.
