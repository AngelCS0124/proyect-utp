# Resumen de Restricciones de Tiempo UTP

## ✅ Implementado

### Bloques de Tiempo
- **8 bloques predefinidos** de 54 minutos cada uno
- **Lunes a Viernes** únicamente (no fines de semana)
- **Horario**: 7:00 AM - 2:49 PM

### Estructura Diaria
```
Bloque 1: 7:00 - 7:54   (54 min)
Bloque 2: 7:55 - 8:49   (54 min)
Bloque 3: 8:50 - 9:44   (54 min)
Bloque 4: 9:45 - 10:39  (54 min)

🍽️ RECESO: 10:40 - 11:09 (29 min) - OBLIGATORIO

Bloque 5: 11:10 - 12:04 (54 min)
Bloque 6: 12:05 - 12:59 (54 min)
Bloque 7: 13:00 - 13:54 (54 min)
Bloque 8: 14:00 - 14:54 (54 min)
Bloque 9: 14:55 - 15:49 (54 min)
```

### Archivos Creados
1. `config/time_blocks.py` - Configuración y validaciones
2. `sample_data/timeslots.json` - 40 bloques predefinidos (8×5 días)
3. `bloques_tiempo.md` - Documentación completa

### Validaciones Activas
✅ Solo días entre semana  
✅ Horario 7:00 AM - 2:49 PM  
✅ Bloques de 54 minutos exactos  
✅ Receso 10:40-11:09 protegido  
✅ Sin horarios personalizados  
✅ Pausas de 1 minuto entre bloques  

## 📊 Total de Bloques Disponibles
**40 bloques** = 8 bloques/día × 5 días/semana

## 🎯 Objetivo
Evitar huecos en el horario y garantizar que todos tengan el mismo receso.
