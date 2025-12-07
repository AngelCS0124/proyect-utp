"""
Curriculum data for UTP - All 10 cuatrimestres
Predefined courses for each academic cycle
"""

from modelos import Curso

# Complete curriculum data extracted from the plan de estudios
CURRICULUM = {
    1: [  # Primer cuatrimestre
        {"id": 101, "name": "INGLÉS I", "code": "ING1", "credits": 75, "enrollment": 30},
        {"id": 102, "name": "DESARROLLO HUMANO Y VALORES", "code": "DHV", "credits": 60, "enrollment": 30},
        {"id": 103, "name": "FUNDAMENTOS MATEMÁTICOS", "code": "FM", "credits": 105, "enrollment": 30},
        {"id": 104, "name": "FUNDAMENTOS DE REDES", "code": "FR", "credits": 60, "enrollment": 30},
        {"id": 105, "name": "FÍSICA", "code": "FIS", "credits": 90, "enrollment": 30},
        {"id": 106, "name": "FUNDAMENTOS DE PROGRAMACIÓN", "code": "FP", "credits": 60, "enrollment": 30},
        {"id": 107, "name": "COMUNICACIÓN Y HABILIDADES DIGITALES", "code": "CHD", "credits": 75, "enrollment": 30},
    ],
    2: [  # Segundo cuatrimestre
        {"id": 201, "name": "INGLÉS II", "code": "ING2", "credits": 75, "enrollment": 30},
        {"id": 202, "name": "LIDERAZGO SOCIOEMOCIONAL (ES ÉTICO)", "code": "LSE", "credits": 60, "enrollment": 30},
        {"id": 203, "name": "CÁLCULO DIFERENCIAL", "code": "CD", "credits": 90, "enrollment": 30},
        {"id": 204, "name": "CONMUTACIÓN Y ENRUTAMIENTO DE REDES", "code": "CER", "credits": 75, "enrollment": 30},
        {"id": 205, "name": "PROBABILIDAD Y ESTADÍSTICA", "code": "PE", "credits": 75, "enrollment": 30},
        {"id": 206, "name": "PROGRAMACIÓN ESTRUCTURADA", "code": "PEST", "credits": 75, "enrollment": 30},
        {"id": 207, "name": "SISTEMAS OPERATIVOS", "code": "SO", "credits": 75, "enrollment": 30},
    ],
    3: [  # Tercer cuatrimestre
        {"id": 301, "name": "INGLÉS III", "code": "ING3", "credits": 75, "enrollment": 30},
        {"id": 302, "name": "LIDERAZGO Y TOMA DE DECISIONES", "code": "LTD", "credits": 60, "enrollment": 30},
        {"id": 303, "name": "CÁLCULO INTEGRAL", "code": "CI", "credits": 60, "enrollment": 30},
        {"id": 304, "name": "TÓPICOS DE CÁLCULO APLICADO AL DISEÑO DE SOFTWARE", "code": "TCADS", "credits": 90, "enrollment": 30},
        {"id": 305, "name": "BASES DE DATOS", "code": "BD", "credits": 75, "enrollment": 30},
        {"id": 306, "name": "PROGRAMACIÓN ORIENTADA A OBJETOS", "code": "POO", "credits": 105, "enrollment": 30},
        {"id": 307, "name": "PROYECTO INTEGRADOR I", "code": "PI1", "credits": 60, "enrollment": 30},
    ],
    4: [  # Cuarto cuatrimestre
        {"id": 401, "name": "INGLÉS IV", "code": "ING4", "credits": 75, "enrollment": 30},
        {"id": 402, "name": "ÉTICA PROFESIONAL", "code": "EP", "credits": 60, "enrollment": 30},
        {"id": 403, "name": "CÁLCULO DE VARIAS VARIABLES", "code": "CVV", "credits": 75, "enrollment": 30},
        {"id": 404, "name": "APLICACIONES WEB", "code": "AW", "credits": 75, "enrollment": 30},
        {"id": 405, "name": "ESTRUCTURA DE DATOS", "code": "ED", "credits": 75, "enrollment": 30},
        {"id": 406, "name": "DESARROLLO DE APLICACIONES MÓVILES", "code": "DAM", "credits": 90, "enrollment": 30},
        {"id": 407, "name": "ANÁLISIS Y DISEÑO DE SOFTWARE", "code": "ADS", "credits": 75, "enrollment": 30},
    ],
    5: [  # Quinto cuatrimestre
        {"id": 501, "name": "INGLÉS V", "code": "ING5", "credits": 75, "enrollment": 30},
        {"id": 502, "name": "LIDERAZGO DE EQUIPOS DE ALTO DESEMPEÑO", "code": "LEAD", "credits": 60, "enrollment": 30},
        {"id": 503, "name": "ECUACIONES DIFERENCIALES", "code": "EDIF", "credits": 75, "enrollment": 30},
        {"id": 504, "name": "APLICACIONES WEB ORIENTADAS A SERVICIOS", "code": "AWOS", "credits": 90, "enrollment": 30},
        {"id": 505, "name": "BASES DE DATOS AVANZADAS", "code": "BDA", "credits": 75, "enrollment": 30},
        {"id": 506, "name": "INGENIERÍA DE MÉTRICAS PARA EL DESARROLLO DE SOFTWARE", "code": "IMDS", "credits": 90, "enrollment": 30},
        {"id": 507, "name": "PROYECTO INTEGRADOR II", "code": "PI2", "credits": 60, "enrollment": 30},
    ],
    6: [  # Sexto cuatrimestre - ESTADIA
        {"id": 601, "name": "ESTADIA EN DESARROLLO DE SOFTWARE MULTIPLATAFORMA", "code": "EDSM", "credits": 600, "enrollment": 30},
    ],
    7: [  # Séptimo cuatrimestre
        {"id": 701, "name": "INGLÉS VI", "code": "ING6", "credits": 75, "enrollment": 30},
        {"id": 702, "name": "HABILIDADES GERENCIALES", "code": "HG", "credits": 60, "enrollment": 30},
        {"id": 703, "name": "FORMULACIÓN DE PROYECTOS DE TECNOLOGÍA", "code": "FPT", "credits": 60, "enrollment": 30},
        {"id": 704, "name": "FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL", "code": "FIA", "credits": 90, "enrollment": 30},
        {"id": 705, "name": "LEGISLACIÓN EN TECNOLOGÍAS DE LA INFORMACIÓN", "code": "LMTI", "credits": 60, "enrollment": 30},
        {"id": 706, "name": "OPTATIVA I MODELACIÓN DE DATOS EN LA NUBE", "code": "OAMDN", "credits": 90, "enrollment": 30},
        {"id": 707, "name": "SEGURIDAD INFORMÁTICA", "code": "SI", "credits": 90, "enrollment": 30},
    ],
    8: [  # Octavo cuatrimestre
        {"id": 801, "name": "INGLÉS VII", "code": "ING7", "credits": 75, "enrollment": 30},
        {"id": 802, "name": "ELECTRÓNICA DIGITAL", "code": "EDIG", "credits": 75, "enrollment": 30},
        {"id": 803, "name": "GESTIÓN DE PROYECTOS DE TECNOLOGÍA", "code": "GPT", "credits": 60, "enrollment": 30},
        {"id": 804, "name": "PROGRAMACIÓN PARA INTELIGENCIA ARTIFICIAL", "code": "PAIA", "credits": 75, "enrollment": 30},
        {"id": 805, "name": "ADMINISTRACIÓN DE SERVIDORES", "code": "AS", "credits": 75, "enrollment": 30},
        {"id": 806, "name": "OPTATIVA II PROGRAMACIÓN MÓVIL AVANZADA", "code": "OPMA", "credits": 90, "enrollment": 30},
        {"id": 807, "name": "INFORMÁTICA FORENSE", "code": "IF", "credits": 75, "enrollment": 30},
    ],
    9: [  # Noveno cuatrimestre
        {"id": 901, "name": "INGLÉS VIII", "code": "ING8", "credits": 75, "enrollment": 30},
        {"id": 902, "name": "INTERNET DE LAS COSAS", "code": "IOT", "credits": 75, "enrollment": 30},
        {"id": 903, "name": "EVALUACIÓN DE PROYECTOS DE TECNOLOGÍA", "code": "EPT", "credits": 60, "enrollment": 30},
        {"id": 904, "name": "CIENCIA DE DATOS", "code": "CDAT", "credits": 90, "enrollment": 30},
        {"id": 905, "name": "TECNOLOGÍAS DISRUPTIVAS", "code": "TD", "credits": 75, "enrollment": 30},
        {"id": 906, "name": "OPTATIVA III FRAMEWORKS PARA EL DESARROLLO", "code": "OFD", "credits": 90, "enrollment": 30},
        {"id": 907, "name": "PROYECTO INTEGRADOR III", "code": "PI3", "credits": 60, "enrollment": 30},
    ],
    10: [  # Décimo cuatrimestre - LICENCIATURA
        {"id": 1001, "name": "ESTADIA EN LICENCIATURA EN INGENIERÍA EN TECNOLOGÍAS DE LA INFORMACIÓN E INNOVACIÓN DIGITAL", "code": "LITIID", "credits": 600, "enrollment": 30},
    ],
}

# Cycle to cuatrimestre mapping
CYCLE_MAPPING = {
    "sept-dec": [1, 4, 7, 10],  # Septiembre a Diciembre
    "jan-apr": [2, 5, 8],        # Enero a Abril
    "may-aug": [3, 6, 9],        # Mayo a Agosto
}

CYCLE_NAMES = {
    "sept-dec": "Septiembre - Diciembre",
    "jan-apr": "Enero - Abril",
    "may-aug": "Mayo - Agosto",
}


def get_all_courses():
    """
    Get all courses from the curriculum as Curso objects
    Returns: List of Curso objects
    """
    courses = []
    for cuatrimestre, cuatrimestre_courses in CURRICULUM.items():
        for course_data in cuatrimestre_courses:
            course = Curso(
                id=course_data["id"],
                nombre=course_data["name"],
                codigo=course_data["code"],
                creditos=course_data["credits"],
                matricula=course_data["enrollment"],
                prerequisitos=[],  # Can be added later if needed
                id_profesor=None,
                cuatrimestre=cuatrimestre
            )
            courses.append(course)
    return courses


def get_courses_for_cycle(cycle):
    """
    Get courses for a specific cycle
    Args:
        cycle: One of 'sept-dec', 'jan-apr', 'may-aug' or Spanish equivalent 'Sep-Dic 2024'
    Returns: List of Curso objects for that cycle
    """
    # Normalizar ciclo (quitar año y mapear español -> inglés si es necesario)
    parts = cycle.split(' ')
    base_cycle = parts[0]
    
    # Mapa de compatibilidad
    mapping_es_en = {
        "Ene-Abr": "jan-apr",
        "May-Ago": "may-aug",
        "Sep-Dic": "sept-dec",
        "Sept-Dic": "sept-dec",
        "jan-apr": "jan-apr",
        "may-aug": "may-aug",
        "sept-dec": "sept-dec"
    }
    
    key = mapping_es_en.get(base_cycle, base_cycle)
    
    if key not in CYCLE_MAPPING:
        raise ValueError(f"Invalid cycle: {cycle} (mapped to {key}). Must be one of {list(CYCLE_MAPPING.keys())} or Spanish equivalents.")
    
    cuatrimestres = CYCLE_MAPPING[key]
    courses = []
    
    for cuatrimestre in cuatrimestres:
        if cuatrimestre in CURRICULUM:
            for course_data in CURRICULUM[cuatrimestre]:
                course = Curso(
                    id=course_data["id"],
                    nombre=course_data["name"],
                    codigo=course_data["code"],
                    creditos=course_data["credits"],
                    matricula=course_data["enrollment"],
                    prerequisitos=[],
                    id_profesor=None,
                    cuatrimestre=cuatrimestre
                )
                courses.append(course)
    
    return courses


def get_available_cycles():
    """
    Get list of available cycles with metadata
    Returns: List of cycle dictionaries
    """
    return [
        {
            "id": "sept-dec",
            "name": CYCLE_NAMES["sept-dec"],
            "cuatrimestres": CYCLE_MAPPING["sept-dec"],
            "months": "Septiembre - Diciembre"
        },
        {
            "id": "jan-apr",
            "name": CYCLE_NAMES["jan-apr"],
            "cuatrimestres": CYCLE_MAPPING["jan-apr"],
            "months": "Enero - Abril"
        },
        {
            "id": "may-aug",
            "name": CYCLE_NAMES["may-aug"],
            "cuatrimestres": CYCLE_MAPPING["may-aug"],
            "months": "Mayo - Agosto"
        }
    ]


def get_cuatrimestre_name(cuatrimestre):
    """Get display name for cuatrimestre number"""
    ordinals = {
        1: "Primer", 2: "Segundo", 3: "Tercer", 4: "Cuarto", 5: "Quinto",
        6: "Sexto", 7: "Séptimo", 8: "Octavo", 9: "Noveno", 10: "Décimo"
    }
    return f"{ordinals.get(cuatrimestre, str(cuatrimestre))} Cuatrimestre"
