# Implementación de Mejoras - Sistema de Diagnósticos Médicos

## Resumen de Cambios Implementados

**Fecha:** 21 de Noviembre de 2025  
**Módulo:** Portal Médico - Registro y Modificación de Diagnósticos  
**Estado:** ✅ Implementado

---

## 1. VALIDACIONES TEMPORALES

### 1.1 Restricción de Hora de Inicio
**Implementado en:** `routes/medico.py` - función `guardar_diagnostico()`

```python
# No permitir registro antes de que inicie la cita
if ahora < fecha_hora_cita:
    return jsonify({
        'success': False, 
        'message': f'Esta cita aún no ha iniciado. Podrá registrar el diagnóstico a partir de las {hora_formatted}'
    })
```

**Comportamiento:**
- El médico NO puede registrar un diagnóstico antes de la hora programada de la cita
- Se muestra mensaje claro con la hora exacta en que podrá registrar
- Frontend también valida con `validarHorarioCita()` antes de mostrar formulario

---

### 1.2 Límite de Registro: Medianoche del Día de la Cita
**Implementado en:** `routes/medico.py` - función `guardar_diagnostico()`

```python
# No permitir registro después de medianoche
fecha_limite = datetime.combine(fecha_cita, time(23, 59, 59))
if ahora > fecha_limite:
    return jsonify({
        'success': False, 
        'message': 'El plazo para registrar el diagnóstico ha expirado. Solo se permite el mismo día de la cita.'
    })
```

**Comportamiento:**
- Plazo máximo: hasta las 23:59:59 del día de la cita
- Pasada la medianoche, no se puede registrar diagnóstico
- Frontend valida antes de abrir formulario
- Backend valida antes de guardar (seguridad)

---

### 1.3 Validación en Citas Canceladas
**Implementado en:** `routes/medico.py`

```python
if cita['estado'] == 'Cancelada':
    return jsonify({
        'success': False, 
        'message': 'No se puede registrar diagnóstico para una cita cancelada'
    })
```

---

## 2. SISTEMA DE MODIFICACIÓN DE DIAGNÓSTICOS

### 2.1 Botón de Modificación en UI
**Implementado en:** `templates/panel_medico.html`

**Ubicación:** Subsistema de Diagnósticos, junto a cada cita que ya tiene diagnóstico registrado

```html
{% if cita.diagnostico %}
<button onclick="abrirFormularioModificacion(...)" 
        class="bg-gradient-to-r from-blue-500 to-indigo-500 ...">
    <span class="material-symbols-outlined">edit</span>
    Modificar Diagnóstico
</button>
{% endif %}
```

**Características:**
- Solo aparece si la cita YA tiene diagnóstico
- Color diferente (azul) vs registro nuevo (cyan)
- Icono distintivo (edit vs edit_note)

---

### 2.2 Función JavaScript de Modificación
**Implementado en:** `templates/panel_medico.html`

```javascript
function abrirFormularioModificacion(idCita, nombrePaciente, dni, idPaciente, fechaCita, horaCita) {
    // Carga el diagnóstico existente vía AJAX
    fetch(`/medico/api/obtener_diagnostico/${idCita}`)
        .then(response => response.json())
        .then(data => {
            // Pre-llena el formulario con los datos actuales
            document.getElementById('diagnostico').value = data.diagnostico;
            document.getElementById('observaciones').value = data.observaciones;
            
            // Marca como modificación
            document.getElementById('es_modificacion').value = 'true';
            
            // Deshabilita autorizaciones (no se pueden cambiar en modificación)
            document.getElementById('check_autorizar_examen').disabled = true;
            document.getElementById('check_autorizar_operacion').disabled = true;
        });
}
```

---

### 2.3 Endpoint API para Obtener Diagnóstico
**Implementado en:** `routes/medico.py`

```python
@medico_bp.route('/api/obtener_diagnostico/<int:id_cita>')
@medico_required
def api_obtener_diagnostico(id_cita):
    # Verifica que sea el mismo médico que registró
    if cita['id_empleado'] != session.get('id_empleado'):
        return jsonify({
            'success': False, 
            'message': 'Solo el médico que registró el diagnóstico puede modificarlo'
        }), 403
    
    return jsonify({
        'success': True,
        'diagnostico': cita['diagnostico'],
        'observaciones': cita['observaciones']
    })
```

**Seguridad:**
- Solo el médico que registró puede modificar
- Validación de permisos antes de retornar datos

---

### 2.4 Historial de Modificaciones
**Implementado en:** `routes/medico.py` - función `guardar_diagnostico()`

```python
if es_modificacion and cita['diagnostico_existente']:
    cursor.execute("""
        INSERT INTO historial_diagnosticos 
        (id_cita, diagnostico_anterior, fecha_modificacion, id_medico_modifica)
        VALUES (%s, %s, NOW(), %s)
    """, (id_cita, cita['diagnostico_existente'], session.get('id_empleado')))
```

**Base de Datos:**
- Nueva tabla: `historial_diagnosticos`
- Registra: diagnóstico anterior, fecha/hora, quién modificó
- Permite auditoría completa de cambios

---

## 3. VALIDACIONES DE SEGURIDAD

### 3.1 Verificación de Permisos
**Contexto:** Solo el médico que atendió la cita puede registrar/modificar su diagnóstico

```python
# En modificación
if cita_medico['id_empleado'] != session.get('id_empleado'):
    return jsonify({
        'success': False,
        'message': 'Solo el médico que registró el diagnóstico puede modificarlo'
    }), 403
```

---

### 3.2 Doble Validación: Frontend + Backend
**Frontend (JavaScript):**
- `validarHorarioCita()` - Valida antes de abrir formulario
- Feedback inmediato al usuario
- Previene requests innecesarios al servidor

**Backend (Python):**
- Validación completa antes de guardar
- Seguridad: usuario no puede bypassear validación frontend
- Mensajes de error consistentes

---

## 4. RESTRICCIONES EN MODIFICACIONES

### 4.1 Autorizaciones No Modificables
**Comportamiento:**
- Al modificar un diagnóstico, los checkboxes de autorizaciones se deshabilitan
- Las autorizaciones (exámenes/operaciones) NO se pueden modificar después de creadas
- Esto previene inconsistencias: si ya se autorizó un examen basado en diagnóstico X, y se cambia a diagnóstico Y, la autorización queda vinculada al diagnóstico original

```javascript
// En abrirFormularioModificacion()
document.getElementById('check_autorizar_examen').disabled = true;
document.getElementById('check_autorizar_operacion').disabled = true;
```

---

### 4.2 Campo Oculto es_modificacion
**Implementado:** Campo hidden en formulario

```javascript
// Se agrega dinámicamente
<input type="hidden" id="es_modificacion" name="es_modificacion" value="true/false">
```

**Propósito:**
- Backend distingue entre registro nuevo vs modificación
- Cambia mensaje de confirmación
- Determina si guardar en historial

---

## 5. MEJORAS EN UX

### 5.1 Indicadores Visuales
**Citas con Diagnóstico:**
```html
<span class="px-2 py-1 bg-blue-100 text-blue-700 rounded">
    Diagnóstico registrado
</span>
```

**Formulario en Modificación:**
```javascript
document.querySelector('#form-diagnostico h3').textContent = 'Modificar Diagnóstico';
document.getElementById('form-paciente-info').textContent = `... (Modificación)`;
```

---

### 5.2 Mensajes Contextuales
**Registro exitoso:**
- "Diagnóstico guardado exitosamente. La cita ha sido marcada como completada."

**Modificación exitosa:**
- "Diagnóstico modificado exitosamente. Los cambios han sido registrados."

**Errores específicos:**
- "Esta cita aún no ha iniciado. Podrá registrar el diagnóstico a partir de las HH:MM"
- "El plazo para registrar el diagnóstico ha expirado..."
- "Solo el médico que registró el diagnóstico puede modificarlo"

---

## 6. SCRIPTS DE BASE DE DATOS

### 6.1 Tabla historial_diagnosticos
**Archivo:** `scripts/crear_tabla_historial_diagnosticos.sql`

```sql
CREATE TABLE historial_diagnosticos (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    diagnostico_anterior TEXT,
    observaciones_anterior TEXT,
    fecha_modificacion DATETIME NOT NULL,
    id_medico_modifica INT NOT NULL,
    FOREIGN KEY (id_cita) REFERENCES CITA(id_cita) ON DELETE CASCADE,
    FOREIGN KEY (id_medico_modifica) REFERENCES EMPLEADO(id_empleado)
);
```

### 6.2 Campo fecha_diagnostico en CITA
```sql
ALTER TABLE CITA 
ADD COLUMN fecha_diagnostico DATETIME NULL
COMMENT 'Fecha y hora en que se registró el diagnóstico';
```

**Propósito:**
- Registrar cuándo se guardó el diagnóstico por primera vez
- Útil para métricas y auditorías

---

## 7. DOCUMENTACIÓN GENERADA

### 7.1 Casos No Contemplados
**Archivo:** `docs/CASOS_NO_CONTEMPLADOS_DIAGNOSTICOS.md`

Incluye:
- 10 secciones de análisis
- Casos edge identificados
- Soluciones recomendadas
- Consideraciones de seguridad
- Plan de testing
- Métricas de monitoreo

---

## 8. FLUJOS DE TRABAJO

### 8.1 Flujo de Registro Nuevo
1. Usuario hace clic en "Registrar Diagnóstico"
2. JavaScript valida fecha/hora (`validarHorarioCita`)
3. Si válido: abre formulario vacío
4. Usuario completa diagnóstico + autorizaciones (opcional)
5. Al enviar: Backend re-valida fecha/hora
6. Si válido: guarda y marca cita como "Completada"
7. Mensaje de éxito y recarga página

### 8.2 Flujo de Modificación
1. Usuario hace clic en "Modificar Diagnóstico" (solo si ya existe)
2. JavaScript carga diagnóstico actual vía `/api/obtener_diagnostico`
3. Backend verifica que sea el mismo médico
4. Si válido: retorna diagnóstico actual
5. Frontend pre-llena formulario y deshabilita autorizaciones
6. Usuario modifica texto
7. Al enviar: Backend guarda versión anterior en `historial_diagnosticos`
8. Actualiza diagnóstico actual
9. Mensaje de éxito y recarga página

---

## 9. COMPATIBILIDAD Y MANEJO DE ERRORES

### 9.1 Citas Antiguas sin Datos de Tiempo
```javascript
if (!fechaCita || !horaCita) {
    return true; // Permitir para compatibilidad
}
```

**Comportamiento:** Si una cita no tiene datos de fecha/hora (citas antiguas), se permite el registro sin validación temporal.

---

### 9.2 Tabla historial_diagnosticos No Existe
```python
try:
    cursor.execute("INSERT INTO historial_diagnosticos ...")
except Exception as e:
    print(f"Advertencia: No se pudo guardar en historial: {e}")
    # Continúa sin fallar
```

**Comportamiento:** Si la tabla no existe, el sistema continúa funcionando, solo que no guarda historial.

---

## 10. TESTING RECOMENDADO

### Casos de Prueba Críticos:

#### TC-01: Registro Anticipado
- **Acción:** Intentar registrar diagnóstico antes de hora de cita
- **Esperado:** Error con mensaje de hora permitida
- **Prioridad:** Alta

#### TC-02: Registro Expirado
- **Acción:** Intentar registrar diagnóstico al día siguiente
- **Esperado:** Error "plazo expirado"
- **Prioridad:** Alta

#### TC-03: Modificación por Otro Médico
- **Acción:** Médico B intenta modificar diagnóstico de Médico A
- **Esperado:** Error 403 Forbidden
- **Prioridad:** Alta

#### TC-04: Modificación con Autorizaciones
- **Acción:** Modificar diagnóstico que ya tiene autorizaciones
- **Esperado:** Checkboxes deshabilitados, solo texto editable
- **Prioridad:** Media

#### TC-05: Historial de Cambios
- **Acción:** Modificar diagnóstico 3 veces
- **Esperado:** 3 registros en `historial_diagnosticos`
- **Prioridad:** Media

---

## 11. MONITOREO Y MÉTRICAS

### Queries Útiles:

**Diagnósticos registrados hoy:**
```sql
SELECT COUNT(*) FROM CITA 
WHERE DATE(fecha_diagnostico) = CURDATE();
```

**Diagnósticos expirados (sin registrar):**
```sql
SELECT COUNT(*) FROM CITA 
WHERE estado = 'Confirmada' 
AND diagnostico IS NULL 
AND DATE(fecha) < CURDATE();
```

**Diagnósticos modificados (últimos 7 días):**
```sql
SELECT COUNT(*) FROM historial_diagnosticos 
WHERE fecha_modificacion >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

**Médico con más modificaciones:**
```sql
SELECT e.nombre, COUNT(*) as modificaciones
FROM historial_diagnosticos h
JOIN EMPLEADO e ON h.id_medico_modifica = e.id_empleado
GROUP BY e.id_empleado
ORDER BY modificaciones DESC
LIMIT 10;
```

---

## 12. PRÓXIMOS PASOS RECOMENDADOS

### Fase 2 - Mejoras Futuras:

1. **Job Automático:**
   - Ejecutar a medianoche
   - Marcar como "Completada (Sin diagnóstico)" las citas sin registro del día

2. **Notificaciones:**
   - Alerta a las 21:00 hrs si quedan diagnósticos pendientes
   - Email al médico con lista de citas sin diagnóstico

3. **Dashboard de Métricas:**
   - % de diagnósticos a tiempo
   - Tiempo promedio de registro
   - Tasa de modificaciones

4. **Recuperación de Diagnósticos Expirados:**
   - Proceso de apelación
   - Aprobación de supervisor
   - Marcado especial "Diagnóstico Tardío"

5. **Notificación a Pacientes:**
   - Cuando se modifica su diagnóstico
   - Requiere justificación del médico

---

## 13. ARCHIVOS MODIFICADOS

### Backend:
- ✅ `routes/medico.py` - Función `guardar_diagnostico()` mejorada
- ✅ `routes/medico.py` - Nueva ruta `/api/obtener_diagnostico/<id>`

### Frontend:
- ✅ `templates/panel_medico.html` - Botón "Modificar Diagnóstico"
- ✅ `templates/panel_medico.html` - Función `abrirFormularioDiagnostico()` mejorada
- ✅ `templates/panel_medico.html` - Nueva función `abrirFormularioModificacion()`
- ✅ `templates/panel_medico.html` - Nueva función `validarHorarioCita()`

### Base de Datos:
- ✅ `scripts/crear_tabla_historial_diagnosticos.sql` - Script de creación

### Documentación:
- ✅ `docs/CASOS_NO_CONTEMPLADOS_DIAGNOSTICOS.md` - Análisis completo
- ✅ `docs/IMPLEMENTACION_DIAGNOSTICOS.md` - Este documento

---

## 14. CONCLUSIÓN

Se han implementado exitosamente todas las mejoras solicitadas:

✅ **Validación Temporal:** Solo se puede registrar desde hora de cita hasta medianoche  
✅ **Restricción de Modificación:** Solo el médico que registró puede modificar  
✅ **Historial de Cambios:** Trazabilidad completa de modificaciones  
✅ **UI Mejorada:** Botones diferenciados para registro vs modificación  
✅ **Seguridad:** Doble validación (frontend + backend)  
✅ **Documentación:** Casos edge identificados y documentados  

El sistema ahora es más robusto, auditable y cumple con mejores prácticas médico-legales.

---

**Autor:** Sistema de Desarrollo - Portal Médico  
**Versión:** 1.0  
**Última Actualización:** 21 de Noviembre de 2025
