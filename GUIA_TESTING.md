# Guía de Testing - Validaciones y Filtros de Especialidad

## Requisitos Previos

- Sistema médico con múltiples especialidades (Cardiología, Urología, Medicina General, etc.)
- Múltiples médicos asignados a cada especialidad
- Exámenes y operaciones creadas con especialidades asignadas
- Tabla `EMPLEADO_SERVICIO` con permisos configurados

---

## Test 1: Filtrado de Exámenes por Especialidad

### 🎯 Objetivo
Verificar que un médico solo vea exámenes de su especialidad cuando intenta autorizar.

### 📋 Pasos

1. **Preparación en BD**:
   ```sql
   -- Verifica que existan exámenes de diferentes especialidades
   SELECT id_servicio, nombre, id_especialidad, id_tipo_servicio 
   FROM SERVICIO 
   WHERE id_tipo_servicio = 4 
   ORDER BY id_especialidad;
   
   -- Resultado esperado: Exámenes de Cardiología, Urología, etc.
   ```

2. **Acción en Frontend**:
   - Loguear como **Médico de Cardiología** (id_especialidad = 3)
   - Ir a Panel Médico → Diagnósticos
   - Seleccionar una cita
   - Hacer clic en "Autorizar Examen"

3. **Verificación**:
   - ✅ **Exámenes mostrados**: Solo de Cardiología (ECG, Ecocardiografía, etc.)
   - ❌ **Exámenes NO mostrados**: De otras especialidades (Ecografía de Próstata, etc.)
   - Abrir consola del navegador (F12)
   - Verificar llamada: `GET /medico/api/obtener_servicios_examen`
   - Response contiene solo exámenes correctos

### 🔍 Verificación de Backend

```python
# En routes/medico.py - línea ~1117
# Debe obtener especialidad del médico:
cursor.execute("SELECT id_especialidad FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
# Debe pasar al modelo:
servicios = AutorizacionProcedimiento.obtener_servicios_examen(id_especialidad_medico)
```

### ❌ Posibles Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| Aparecen todos los exámenes | Parámetro no se pasa | Verificar que `id_especialidad_medico` se envía |
| Aparecen exámenes de otra especialidad | SQL incorrecto | Verificar cláusula WHERE en modelo |
| 404 Not Found | Endpoint no existe | Verificar ruta `/medico/api/obtener_servicios_examen` |

---

## Test 2: Derivación sin Selector de Especialidad

### 🎯 Objetivo
Verificar que al derivar una operación, se carguen automáticamente médicos de la misma especialidad del médico logueado (sin mostrar selector de especialidad).

### 📋 Pasos

1. **Preparación en BD**:
   ```sql
   -- Verifica múltiples médicos en Cardiología
   SELECT e.id_empleado, CONCAT(e.nombres, ' ', e.apellidos) as nombre,
          es.nombre as especialidad
   FROM EMPLEADO e
   INNER JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
   WHERE e.id_especialidad = 3  -- Cardiología
   AND e.id_rol = 2  -- Médicos
   AND e.estado = 'activo'
   ORDER BY e.apellidos;
   
   -- Resultado esperado: Mínimo 2-3 médicos de Cardiología
   ```

2. **Acción en Frontend**:
   - Loguear como **Dr. Cardiólogo A** (id_empleado = 10)
   - Panel Médico → Diagnósticos
   - Seleccionar cita
   - Marcar "Autorizar Operación"
   - Seleccionar "Tipo de Operación"

3. **Verificación**:
   - ✅ **NO aparece selector de especialidad** (antes sí aparecía)
   - ✅ **Aparece selector de médicos** con:
     - Opción "-- Yo realizaré la operación --"
     - Dr. Cardiólogo B
     - Dr. Cardiólogo C
     - (Otros cardiólogos, EXCEPTO el actual)
   - ✅ **Texto informativo**: "Solo se muestran médicos de su especialidad"

4. **Verificación de Red**:
   - F12 → Network
   - Buscar request: `GET /medico/api/obtener_medicos_mi_especialidad`
   - Response JSON:
     ```json
     {
       "success": true,
       "medicos": [
         {
           "id_empleado": 11,
           "nombre_completo": "Dr. Otro Cardiólogo",
           "especialidad": "Cardiología"
         },
         ...
       ],
       "especialidad_nombre": "Cardiología"
     }
     ```

### 🔍 Verificación de Backend

```python
# En routes/medico.py - línea ~1173 (NUEVO endpoint)
# Debe obtener especialidad actual:
cursor.execute("SELECT id_especialidad FROM EMPLEADO WHERE id_empleado = %s")
# Debe cargar médicos de esa especialidad:
medicos = AutorizacionProcedimiento.obtener_medicos_por_especialidad(id_especialidad_medico)
# Debe filtrar al médico actual:
medicos_filtrados = [m for m in medicos if m['id_empleado'] != id_empleado]
```

### ❌ Posibles Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| Aparece selector de especialidad | HTML no actualizado | Verificar cambio en `div_derivar_operacion` |
| No aparecen médicos | Endpoint falla | Ver error en console (F12) |
| Aparece el médico actual | Filtro no funciona | Verificar línea de `medicos_filtrados` |
| Error 404 | Endpoint no existe | Verificar ruta `/medico/api/obtener_medicos_mi_especialidad` |

---

## Test 3: Validación - Médico SIN Permiso para Operar

### 🎯 Objetivo
Verificar que si un médico NO tiene permiso en `EMPLEADO_SERVICIO` para una operación, al intentar "Yo realizaré" debe mostrar ERROR.

### 📋 Pasos

1. **Preparación en BD**:
   ```sql
   -- Médico de Medicina General intenta autorizar operación de Urología
   -- Verificar que NO existe en EMPLEADO_SERVICIO:
   SELECT * FROM EMPLEADO_SERVICIO 
   WHERE id_empleado = 1  -- Médico Medicina General
   AND id_servicio = 10;  -- Operación de Próstata (ejemplo)
   
   -- Resultado: 0 filas (médico NO tiene permiso)
   ```

2. **Acción en Frontend**:
   - Loguear como **Médico de Medicina General**
   - Panel Médico → Diagnósticos
   - Seleccionar cita
   - Marcar "Autorizar Operación"
   - Seleccionar "Operación de Próstata"
   - **IMPORTANTE**: Dejar como "-- Yo realizaré la operación --"
   - Hacer clic "Guardar Diagnóstico"

3. **Verificación**:
   - ✅ **Aparece ERROR**:
     ```
     Error: No está autorizado para esta operación. 
     Debe derivarla a otro médico.
     ```
   - ✅ **Diagnóstico NO se guarda**
   - ✅ **Cita sigue en estado "Pendiente"** (no se marca como Completada)

4. **Verificación de Red**:
   - F12 → Network
   - POST request a `/medico/diagnosticos/guardar`
   - Response: Status **403**
   - Body:
     ```json
     {
       "success": false,
       "message": "Usted no está autorizado para realizar esta operación. Debe derivarla a otro médico."
     }
     ```

### 🔍 Verificación de Backend

```python
# En routes/medico.py - línea ~880 (nuevo código)
# Cuando no se deriv:
if not id_medico_derivar:
    # Valida que tenga permiso
    cursor.execute("""
        SELECT COUNT(*) as puede_operar
        FROM SERVICIO s
        INNER JOIN EMPLEADO_SERVICIO es ON s.id_servicio = es.id_servicio
        WHERE s.id_servicio = %s 
        AND es.id_empleado = %s
        AND s.id_tipo_servicio = 2
    """)
    
    puede_operar = cursor.fetchone()['puede_operar']
    
    if not puede_operar:
        # Retorna error 403
        return jsonify({
            'success': False,
            'message': 'Usted no está autorizado...'
        }), 403
```

### ❌ Posibles Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| No muestra error | Validación no se ejecuta | Verificar que `id_medico_derivar` está vacío |
| Autoriza sin validar | Query no se ejecuta | Verificar sintaxis de SELECT COUNT |
| Status 500 en lugar de 403 | Error en código | Ver logs del servidor |
| Autoriza con error | Lógica de error reversa | Verificar que retorna error si `puede_operar == 0` |

---

## Test 4: Validación - Médico CON Permiso para Operar

### 🎯 Objetivo
Verificar que si un médico TIENE permiso, al elegir "Yo realizaré" se autoriza correctamente.

### 📋 Pasos

1. **Preparación en BD**:
   ```sql
   -- Médico de Cardiología intenta autorizar "Ablación Cardíaca"
   -- Verificar que EXISTE en EMPLEADO_SERVICIO:
   SELECT * FROM EMPLEADO_SERVICIO 
   WHERE id_empleado = 10  -- Cardiólogo
   AND id_servicio = 15;  -- Ablación Cardíaca
   
   -- Resultado: 1 fila (médico SÍ tiene permiso)
   ```

2. **Acción en Frontend**:
   - Loguear como **Cardiólogo CON permiso**
   - Panel Médico → Diagnósticos
   - Seleccionar cita
   - Marcar "Autorizar Operación"
   - Seleccionar "Ablación Cardíaca"
   - Dejar "-- Yo realizaré la operación --" (NO derivar)
   - Guardar diagnóstico

3. **Verificación**:
   - ✅ **Mensaje de éxito**:
     ```
     Diagnóstico guardado exitosamente. 
     Se autorizaron: operación.
     ```
   - ✅ **Cita marcada como Completada**
   - ✅ **Autorización creada con `id_medico_asignado` = médico logueado**

4. **Verificación en BD**:
   ```sql
   SELECT * FROM AUTORIZACION_PROCEDIMIENTO 
   WHERE id_cita = [CITA_TESTEADA]
   AND tipo_procedimiento = 'OPERACION'
   AND id_medico_asignado = 10;  -- Debe ser el médico actual
   ```

---

## Test 5: Derivación Exitosa

### 🎯 Objetivo
Verificar que al derivar a otro médico, se crea la autorización correctamente.

### 📋 Pasos

1. **Acción en Frontend**:
   - Loguear como **Médico Cardiología A**
   - Panel Médico → Diagnósticos
   - Seleccionar cita
   - Marcar "Autorizar Operación"
   - Seleccionar "Ablación Cardíaca"
   - **Seleccionar otro médico** en el dropdown (ej: "Dr. Cardiólogo B")
   - Guardar

2. **Verificación**:
   - ✅ **Éxito**: "Diagnóstico guardado. Se autorizaron: operación."
   - ✅ **Autorización creada con `id_medico_asignado` = Dr. Cardiólogo B**

3. **Verificación en BD**:
   ```sql
   SELECT id_autorizacion, id_medico_autoriza, id_medico_asignado, estado
   FROM AUTORIZACION_PROCEDIMIENTO 
   WHERE id_cita = [CITA]
   AND tipo_procedimiento = 'OPERACION';
   
   -- Resultado esperado:
   -- id_medico_autoriza = 10 (quien autorizó)
   -- id_medico_asignado = 11 (a quién se derivó)
   -- estado = 'PENDIENTE'
   ```

---

## Test 6: Performance - Carga de Selectores

### 🎯 Objetivo
Verificar que los selectores se cargan rápidamente sin lag.

### 📋 Pasos

1. F12 → Performance
2. Grabar sesión
3. Marcar "Autorizar Operación"
4. Seleccionar tipo de operación
5. Detener grabación

### ✅ Criterios de Aceptación

- ⏱️ Tiempo total < 500ms
- ⏱️ Network request < 200ms
- ⏱️ Rendering < 100ms
- 🎯 Sin jank (saltos en animación)

---

## Checklist de Testing Completo

- [ ] **Test 1**: Filtrado de exámenes ✓
- [ ] **Test 2**: Derivación sin selector especialidad ✓
- [ ] **Test 3**: Error si no tiene permiso ✓
- [ ] **Test 4**: Éxito si tiene permiso ✓
- [ ] **Test 5**: Derivación a otro médico ✓
- [ ] **Test 6**: Performance aceptable ✓
- [ ] **Test 7**: Sin errores en consola (F12)
- [ ] **Test 8**: Funciona en navegadores: Chrome, Firefox, Safari
- [ ] **Test 9**: Notificaciones creadas correctamente
- [ ] **Test 10**: Auditoría registrada en BD

---

## Comandos Útiles para Debugging

### Ver especialidad de médico logueado
```sql
SELECT id_empleado, CONCAT(nombres, ' ', apellidos) as nombre,
       id_especialidad, id_rol
FROM EMPLEADO 
WHERE id_empleado = 10;
```

### Ver exámenes de Cardiología
```sql
SELECT s.id_servicio, s.nombre, e.nombre as especialidad
FROM SERVICIO s
LEFT JOIN ESPECIALIDAD e ON s.id_especialidad = e.id_especialidad
WHERE s.id_tipo_servicio = 4  -- EXAMEN
AND s.estado = 'activo'
AND (s.id_especialidad = 3 OR s.id_especialidad IS NULL);  -- Cardiología = 3
```

### Ver permisos de médico para operar
```sql
SELECT s.id_servicio, s.nombre, es.nombre as especialidad
FROM EMPLEADO_SERVICIO emp_srv
INNER JOIN SERVICIO s ON emp_srv.id_servicio = s.id_servicio
INNER JOIN ESPECIALIDAD es ON s.id_especialidad = es.id_especialidad
WHERE emp_srv.id_empleado = 10
AND s.id_tipo_servicio = 2;  -- OPERACION
```

### Ver autorizaciones creadas
```sql
SELECT id_autorizacion, id_medico_autoriza, id_medico_asignado,
       tipo_procedimiento, estado, fecha_creacion
FROM AUTORIZACION_PROCEDIMIENTO 
WHERE id_cita = [CITA_ID]
ORDER BY fecha_creacion DESC;
```

---

## Logs a Revisar

### Console del Navegador (F12 → Console)
```javascript
// Errores de fetch
Uncaught (in promise) TypeError: Failed to fetch

// Errores de JSON
SyntaxError: Unexpected token < in JSON at position 0

// Errores lógicos
undefined is not a function: cargarMedicosMiEspecialidad
```

### Logs del Servidor (Terminal/Logs de Flask)
```
ERROR en guardar diagnóstico: ...
Error al obtener médicos de mi especialidad: ...
```

---

## Contacto para Problemas

- 🐛 **Errores en Tests**: Revisar console del navegador (F12)
- 🔧 **Backend Issues**: Revisar logs del servidor
- 📊 **BD Issues**: Ejecutar queries de debugging arriba listadas
- 📚 **Documentación**: Ver `VALIDACIONES_AUTORIZACIONES.md`

---

**Última actualización**: 19 de Noviembre de 2025
**Versión de Testing**: 1.0

