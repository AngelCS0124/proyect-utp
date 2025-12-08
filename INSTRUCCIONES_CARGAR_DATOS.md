# INSTRUCCIONES: Cargar Datos Actualizados en el Frontend

## 🎯 Problema
El frontend no muestra todos los 30 cursos / 46 clases porque el servidor puede estar:
1. Cargando datos antiguos en caché
2. Leyendo de una ubicación diferente
3. Aplicando filtros que ocultan cursos

## ✅ Solución: Pasos para Cargar Datos Correctos

### Opción 1: Usar el Endpoint de Carga (Recomendado)

1. **Iniciar el servidor**:
   ```bash
   cd python_backend
   python3 aplicacion.py
   ```

2. **Abrir el frontend**: 
   - Ir a `http://localhost:5000`

3. **Cargar datos por defecto**:
   - En el frontend, buscar el botón "**Cargar Datos por Defecto**" o "**Load Defaults**"
   - Hacer clic
   - Esto cargará los archivos de `datos_muestra/`

4. **Generar horario**:
   - Clic en "**Generar Horario**" o "**Generate Schedule**"
   - Esperar ~1-2 segundos

### Opción 2: Subir el CSV Manualmente

1. **En el frontend**, buscar opción de **Upload** o **Subir Archivo**

2. **Subir el CSV**:
   - Seleccionar `datos_muestra/cursos.csv`
   - Tipo de dato: "courses" o "cursos"
   - Upload

3. **Generar horario**

### Opción 3: Usar API Directa (para debugging)

```bash
# Terminal 1: Iniciar servidor
cd python_backend
python3 aplicacion.py

# Terminal 2: Cargar datos vía API
curl -X POST http://localhost:5000/api/load-defaults

# Verificar datos cargados
curl http://localhost:5000/api/status

# Generar horario
curl -X POST http://localhost:5000/api/generate
```

## 🔍 Verificar que se Cargaron los Datos

### En el Frontend
Después de cargar, deberías ver:
- **Cursos**: 30
- **Profesores**: 15
- **Bloques de tiempo**: 45

### Vía API
```bash
curl http://localhost:5000/api/status
```

Debería mostrar:
```json
{
  "data_loaded": {
    "courses": 30,
    "professors": 15,
    "timeslots": 45
  }
}
```

## ⚠️ Problemas Comunes

### 1. "Solo veo 4-10 cursos"
**Causa**: Servidor cargando datos antiguos
**Solución**: 
- Detener servidor (Ctrl+C)
- Reiniciar: `python3 aplicacion.py`
- Cargar datos por defecto de nuevo

### 2. "El calendario se ve vacío después de generar"
**Causa**: Filtro de cuatrimestre activo
**Solución**: 
- Verificar que en `cursos.csv` todos los cursos tengan `cuatrimestre=2`
- Ya está corregido en el archivo actual

### 3. "Error al generar horario"
**Causa**: Scheduler C++ no disponible
**Solución**: El sistema automáticamente usa CSP Scheduler en Python (más lento pero funciona)

## 📊 Resultado Esperado

Después de generar, deberías ver:

```
📅 Calendario:
- Lunes: 9 clases
- Martes: 9 clases
- Miércoles: 9 clases
- Jueves: 10 clases
- Viernes: 9 clases
────────────────────
TOTAL: 46 clases
```

## 🛠️ Debugging Avanzado

Si aún no funciona, ejecutar diagnóstico:

```bash
# Ver qué cursos tiene el servidor en memoria
curl http://localhost:5000/api/data/courses | python3 -m json.tool | grep "nombre" | wc -l

# Ver estado completo
curl http://localhost:5000/api/status | python3 -m json.tool
```

## 💡 Nota Importante

El archivo `datos_muestra/cursos.csv` YA tiene:
- ✅ 30 cursos
- ✅ Todos en cuatrimestre 2
- ✅ 46 sesiones totales (1-2 por curso)
- ✅ Grupos únicos (1-30)

Solo necesitas que el **servidor los cargue correctamente**.
