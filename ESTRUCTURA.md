# Estructura del Proyecto UTP Scheduler

## Nueva Organización Modular

```
proyect-utp/
├── python_backend/
│   ├── models/                  # Modelos de datos
│   │   ├── __init__.py
│   │   ├── course.py           # Modelo Course (con campo cuatrimestre)
│   │   ├── professor.py        # Modelo Professor
│   │   ├── timeslot.py         # Modelo TimeSlot
│   │   └── schedule.py         # Modelo Schedule
│   │
│   ├── data/                    # Datos predefinidos
│   │   ├── __init__.py
│   │   └── curriculum.py       # Currículo completo (10 cuatrimestres)
│   │
│   ├── services/                # Lógica de negocio (futuro)
│   │   └── __init__.py
│   │
│   ├── routes/                  # Rutas API (futuro)
│   │   └── __init__.py
│   │
│   ├── config/                  # Configuración
│   │   └── __init__.py
│   │
│   ├── app.py                   # Aplicación Flask principal
│   ├── data_loader.py           # Cargador de datos
│   ├── validators.py            # Validadores
│   └── setup.py                 # Build Cython
│
├── frontend/
│   ├── index.html               # UI principal
│   ├── app.js                   # Lógica JavaScript
│   └── styles.css               # Estilos CSS
│
└── sample_data/
    ├── professors.json
    └── timeslots.csv
```

## Cambios Principales

### 1. Modelos Separados
- Cada modelo en su propio archivo
- Importación centralizada desde `models/__init__.py`
- Campo `cuatrimestre` en lugar de `semester`

### 2. Datos del Currículo
- Currículo completo en `data/curriculum.py`
- 10 cuatrimestres predefinidos
- Mapeo de ciclos a cuatrimestres

### 3. Terminología Correcta
- **Cuatrimestre** en lugar de semestre
- Ciclos de 4 meses (Sept-Dec, Jan-Apr, May-Aug)

## Importaciones

```python
# Desde app.py
from models import Course, Professor, TimeSlot, Schedule
from data import get_all_courses, get_courses_for_cycle, get_available_cycles
```

## Próximos Pasos

1. Mover lógica de validación a `services/`
2. Separar rutas API en `routes/`
3. Configuración centralizada en `config/`
