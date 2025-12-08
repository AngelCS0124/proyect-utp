# ✅ Datos Basados en professors.json

## Archivo Base: `datos_muestra/professors.json`

He creado **45 cursos** basándome EXACTAMENTE en los códigos de `available_courses` del archivo `professors.json`.

## 📊 Cursos Creados

Basado en 24 profesores reales del archivo `professors.json`, creé 45 cursos usando los códigos exactos:

| ID | Código | Nombre del Curso |
|----|--------|------------------|
| 1 | FP | Fundamentos de Programación |
| 2 | POO | Programación Orientada a Objetos |
| 3 | BD | Bases de Datos |
| 4 | BDA | Bases de Datos Avanzadas |
| 5 | SO | Sistemas Operativos |
| 6 | TCADS | Ciencia de Datos |
| 7 | ADS | Algoritmos y Estructura de Datos |
| 8 | AW | Aplicaciones Web |
| 9 | AWOS | Aplicaciones Web con Open Source |
| 10 | PI1 | Proyecto Integrador I |
| 11 | PI2 | Proyecto Integrador II |
| 12 | PI3 | Proyecto Integrador III |
| 13 | CD | Cálculo Diferencial |
| 14 | CI | Cálculo Integral |
| 15 | FIS | Física |
| 16 | FM | Fundamentos de Matemáticas |
| 17 | PEST | Probabilidad y Estadística |
| 18-22 | ING1-ING5 | Inglés I a V |
| 23 | LSE | Liderazgo Socioemocional |
| 24 | DHV | Desarrollo de Habilidades y Valores |
| 25 | LTD | Liderazgo y Trabajo en Equipo |
| 26 | EP | Ética Profesional |
| 27 | LEAD | Liderazgo |
| 28 | FIA | Inteligencia Artificial |
| 29 | PE | Expresión Oral y Escrita |
| 30 | CER | Conmutación y Enrutamiento |
| 31 | CHD | Circuitos y Dispositivos |
| 32 | CVV | Convergencia de Voz y Video |
| 33 | EDIF | Estructura y Diseño de Internet Fijo |
| 34 | EDIG | Estructura y Diseño de Internet Inalámbrico |
| 35 | DAM | Desarrollo de Aplicaciones Móviles |
| 36 | IMDS | Minería de Datos |
| 37 | CDAT | Ciencia de Datos Aplicada a Telecomunicaciones |
| 38 | AS | Análisis y Seguridad |
| 39 | IOT | Internet de las Cosas |
| 40 | HG | Herramientas de Google |
| 41 | GPT | Gestión de Proyectos Tecnológicos |
| 42 | FR | Fundamentos de Redes |
| 43 | FPT | Fundamentos de Proyectos Tecnológicos |
| 44 | EPT | Enrutamiento de Proyectos Tecnológicos |
| 45 | OAMDN | Operación y Administración de Móviles |

## 🎯 Características

- **45 cursos** con códigos exactos de `professors.json`
- **1 sesión por semana** cada uno = 45 sesiones totales
- **Cuatrimestre 2** (todos unificados)
- **Grupos únicos** (1-45) para evitar conflictos
- **Sin profesores pre-asignados** (se asignarán automáticamente por matching de códigos)

## 📁 Archivos

- **Base**: `/home/jared/proyect-utp/datos_muestra/professors.json` (NO MODIFICADO)
- **Creado**: `/home/jared/proyect-utp/datos_muestra/cursos.csv` (ACTUALIZADO)

## 🚀 Para Usar

### Opción 1: Cargar desde el Frontend

```bash
# 1. Iniciar servidor
cd python_backend
python3 aplicacion.py

# 2. En frontend: http://localhost:5000
# Click "Cargar Datos por Defecto"
# Click "Generar Horario"
```

### Opción 2: Vía API

```bash
# Cargar datos
curl -X POST http://localhost:5000/api/load-defaults

# Verificar
curl http://localhost:5000/api/status

# Generar
curl -X POST http://localhost:5000/api/generate
```

## ✨ Resultado Esperado

Con los 45 cursos basados en `professors.json`:

```
📅 CALENDARIO COMPLETO
──────────────────────
Lunes:      9 clases
Martes:     9 clases
Miércoles:  9 clases
Jueves:     9 clases
Viernes:    9 clases
──────────────────────
TOTAL:     45 clases
```

El sistema reconocerá automáticamente los códigos y asignará profesores según los `available_courses` definidos en `professors.json`.

## ⚠️ Importante

El archivo `professors.json` usa un esquema DIFERENTE a `profesores.json`:
- `available_courses` (en lugar de `materias_capaces`)
- `available_timeslots` (bloques con IDs como 1-409)
- Nombres reales de profesores de ITI

Los cursos ahora están alineados con este esquema correcto.
