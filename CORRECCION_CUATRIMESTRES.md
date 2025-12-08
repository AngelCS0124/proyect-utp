# Corrección: Unificación de Cuatrimestres

## Problema
El calendario mostraba 4 secciones separadas porque los cursos estaban distribuidos en cuatrimestres 1, 2, 3 y 4, causando que el frontend creara un grupo de calendario para cada cuatrimestre.

## Solución
Todos los **20 cursos** ahora están unificados en el **cuatrimestre 2** para que se muestren en un solo calendario integrado.

## Cambios Realizados

### Antes:
```
- Cuatrimestre 1: 7 cursos
- Cuatrimestre 2: 5 cursos  
- Cuatrimestre 3: 7 cursos
- Cuatrimestre 4: 1 curso
Total: 4 secciones separadas en el calendario
```

### Después:
```
- Cuatrimestre 2: 20 cursos
Total: 1 calendario unificado con todas las clases
```

## Resultado
- ✅ **47 clases** distribuidas en **un solo calendario**
- ✅ **Distribución equilibrada** por día:
  - Lunes: 10 clases
  - Martes: 10 clases
  - Miércoles: 9 clases
  - Jueves: 9 clases
  - Viernes: 9 clases

## Archivo Modificado
- `datos_muestra/cursos.csv` - Todos los cursos ahora tienen `cuatrimestre=2`

## Nota
Si en el futuro necesitas separar cursos por cuatrimestre (por ejemplo, para simular diferentes períodos académicos), puedes:
1. Crear archivos CSV separados para cada cuatrimestre
2. Cargar cada conjunto de cursos por separado
3. O usar el sistema de ciclos del frontend para seleccionar el período específico
