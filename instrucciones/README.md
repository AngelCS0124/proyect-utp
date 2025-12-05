# Guía de Instalación y Ejecución

Este documento detalla los pasos para instalar y ejecutar el Sistema de Horarios UTP en diferentes sistemas operativos.

## Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado:

*   **Python 3.8+**
*   **Compilador C++** (GCC/G++ en Linux, MSVC o MinGW en Windows)
*   **Git** (opcional, para clonar el repositorio)

## Instrucciones de Instalación

### Linux (Ubuntu/Debian)

1.  **Clonar o descargar el proyecto**:
    ```bash
    git clone <url-del-repo>
    cd proyect-utp
    ```

2.  **Crear un entorno virtual (recomendado)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependencias de Python**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Compilar el núcleo de C++**:
    Es necesario compilar la extensión de C++ para que el algoritmo de scheduling funcione.
    ```bash
    cd python_backend
    python3 setup.py build_ext --inplace
    ```
    *Nota: Si tienes errores de `Python.h`, asegúrate de tener instalado `python3-dev`: `sudo apt-get install python3-dev`.*

5.  **Ejecutar el servidor**:
    ```bash
    # Desde la carpeta python_backend
    python3 app.py
    ```

6.  **Abrir la aplicación**:
    Abre tu navegador web y ve a: `http://localhost:5000`

### Windows

1.  **Clonar o descargar el proyecto**:
    Descarga el ZIP y extráelo, o usa git bash.
    ```bash
    cd proyect-utp
    ```

2.  **Crear un entorno virtual**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Compilar el núcleo de C++**:
    Necesitas tener instalado "Build Tools for Visual Studio" con el compilador de C++.
    ```bash
    cd python_backend
    python setup.py build_ext --inplace
    ```

5.  **Ejecutar el servidor**:
    ```bash
    python app.py
    ```

6.  **Abrir la aplicación**:
    Ve a `http://localhost:5000` en tu navegador.

## Uso del Sistema

1.  **Cargar Datos**:
    *   Ve al **Dashboard**.
    *   Sube los archivos CSV de Cursos, Profesores y Horarios (puedes usar los de `sample_data/`).
    *   Verifica que aparezcan los "checks" verdes en las tarjetas.

2.  **Gestionar Maestros**:
    *   Ve a la sección **Maestros** para añadir, editar o eliminar profesores.

3.  **Gestionar Disponibilidad**:
    *   Ve a **Disponibilidad**.
    *   Selecciona un maestro (puedes filtrar por materia).
    *   Marca las casillas "On" para indicar disponibilidad y guarda.

4.  **Generar Horario**:
    *   Vuelve al **Dashboard**.
    *   Haz clic en **Generar Horario**.
    *   Observa la visualización del algoritmo y espera a que se muestre el resultado en la pestaña **Horario**.

## Estructura del Proyecto

*   `cpp_core/`: Código fuente C++ del algoritmo de scheduling (Grafos, Backtracking).
*   `python_backend/`: Servidor Flask y API REST.
*   `frontend/`: Interfaz de usuario (HTML, CSS, JS).
*   `sample_data/`: Archivos CSV de ejemplo para pruebas.
