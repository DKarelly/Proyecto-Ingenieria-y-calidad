# Casos No Contemplados - Sistema de Diagnósticos Médicos

## Documento de Análisis de Errores Potenciales

**Fecha de Creación:** 21 de Noviembre de 2025  
**Sistema:** Portal Médico - Registro de Diagnósticos  
**Versión:** 1.0

---

## 1. VALIDACIÓN TEMPORAL DE DIAGNÓSTICOS

### 1.1 Citas que Inician Fuera del Horario Programado
**Escenario:** El médico intenta registrar un diagnóstico antes de que la cita haya iniciado oficialmente.

**Problema:**
- Si la cita está programada para las 15:00 hrs pero el médico intenta registrar a las 14:45 hrs
- El sistema debe prevenir registros anticipados que puedan generar inconsistencias

**Solución Implementada:**
- Validar que la hora actual sea >= hora de inicio de la cita
- Mostrar mensaje claro: "Esta cita aún no ha iniciado. Podrá registrar el diagnóstico a partir de las HH:MM"

**Casos Edge:**
- ¿Qué pasa si hay diferencia de zona horaria?
- ¿Qué pasa si el reloj del servidor está adelantado/atrasado?

---

### 1.2 Diagnósticos Registrados Después de Medianoche
**Escenario:** La cita fue durante el día pero el médico intenta registrar después de las 00:00 del día siguiente.

**Problema:**
- Cita del 21/11/2025 a las 16:00 hrs
- Médico intenta registrar el 22/11/2025 a las 00:30 hrs
- ¿Se permite o se marca como expirada?

**Solución Implementada:**
- Calcular fecha límite: mismo día de la cita hasta las 23:59:59
- Si se excede el límite, marcar automáticamente como "Completada" sin diagnóstico
- Notificar al médico que el plazo expiró

**Casos Edge:**
- Citas cerca de medianoche (23:30 hrs) - tiempo muy reducido para diagnóstico
- ¿Se permite extensión de plazo en casos excepcionales?

---

### 1.3 Citas Reprogramadas o Canceladas
**Escenario:** La cita fue reprogramada pero el médico intenta registrar diagnóstico en la fecha/hora original.

**Problema:**
- Cita original: 21/11/2025 14:00 → Reprogramada: 25/11/2025 14:00
- El registro debe validar contra la fecha ACTUAL de la cita, no la original

**Solución Implementada:**
- Siempre validar contra `cita.fecha` y `cita.hora` actuales
- Verificar estado de la cita (no permitir si está "Cancelada")

**Casos Edge:**
- Múltiples reprogramaciones en el mismo día
- Cancelación después de haber iniciado la cita

---

## 2. MODIFICACIÓN DE DIAGNÓSTICOS

### 2.1 Edición Después del Día de la Cita
**Escenario:** El médico se da cuenta de un error en el diagnóstico días después.

**Problema:**
- Diagnóstico registrado el 21/11/2025
- Médico quiere modificar el 25/11/2025
- ¿Se permite? ¿Debe quedar registro de cambios?

**Solución Implementada:**
- Permitir modificación con ventana de tiempo (ej: 7 días)
- Registrar historial de cambios con fecha/hora de cada modificación
- Marcar diagnóstico como "Modificado" con timestamp

**Casos Edge:**
- ¿Qué pasa si el paciente ya usó el diagnóstico (receta, examen autorizado)?
- ¿Se notifica al paciente del cambio?
- ¿Se requiere justificación/motivo del cambio?

---

### 2.2 Modificación con Autorizaciones Pendientes
**Escenario:** Se modificó el diagnóstico pero ya hay exámenes/operaciones autorizados.

**Problema:**
- Diagnóstico original: "Gastritis" → Autoriza endoscopia
- Diagnóstico modificado: "Alergia alimentaria" 
- La autorización de endoscopia ya no es congruente

**Solución Recomendada:**
- Al modificar diagnóstico, mostrar WARNING sobre autorizaciones existentes
- Opción de revocar/modificar autorizaciones asociadas
- Requerir confirmación explícita del médico

**Casos Edge:**
- Examen ya realizado cuando se modifica diagnóstico
- Operación ya programada con fecha
- Múltiples autorizaciones dependientes del diagnóstico original

---

### 2.3 Conflictos de Edición Concurrente
**Escenario:** Dos médicos (o médico + sistema) intentan modificar el mismo diagnóstico simultáneamente.

**Problema:**
- Médico A abre formulario de edición a las 10:00
- Sistema auto-completa cita a las 10:05 (por timeout)
- Médico A guarda cambios a las 10:10
- ¿Qué versión prevalece?

**Solución Recomendada:**
- Implementar control de versiones/timestamps
- Validar que el registro no haya cambiado desde que se abrió el formulario
- Mostrar alerta de conflicto y permitir resolver manualmente

---

## 3. ESTADO AUTOMÁTICO "COMPLETADA"

### 3.1 Transición Automática por Timeout
**Escenario:** Cita sin diagnóstico al final del día se marca como "Completada" automáticamente.

**Problema:**
- ¿Cómo diferenciar entre "Completada con diagnóstico" vs "Completada sin diagnóstico"?
- ¿Afecta estadísticas/métricas del médico?
- ¿Se notifica al médico?

**Solución Implementada:**
- Nuevo estado o flag: "Completada (Sin diagnóstico registrado)"
- Notificación automática al médico al día siguiente
- Registrar en logs para auditoría

**Casos Edge:**
- Paciente no asistió pero cita no se marcó "No Asistió"
- Emergencia del médico que impidió registrar diagnóstico a tiempo

---

### 3.2 Recuperación de Diagnósticos Expirados
**Escenario:** El médico necesita registrar diagnóstico después del plazo por razones válidas.

**Problema:**
- Cita del 20/11/2025, hoy es 23/11/2025
- Médico tiene notas manuscritas pero el sistema ya bloqueó el registro

**Solución Recomendada:**
- Rol de administrador puede "reabrir" citas expiradas
- Proceso de apelación con justificación escrita
- Registro especial marcado como "Diagnóstico Tardío"

**Casos Edge:**
- Múltiples solicitudes de reapertura del mismo médico
- Auditorías que detecten patrón de diagnósticos tardíos

---

## 4. INTEGRACIÓN CON AUTORIZACIONES

### 4.1 Autorización Sin Diagnóstico Previo
**Escenario:** El sistema permite autorizar examen/operación pero luego el diagnóstico se modifica.

**Problema:**
- Inconsistencia entre diagnóstico y procedimiento autorizado
- Riesgo médico-legal si no hay coherencia

**Solución Implementada:**
- Autorización se vincula permanentemente al diagnóstico original
- Historial de cambios muestra diagnóstico en momento de autorización
- Alerta si diagnóstico modificado afecta autorización

---

### 4.2 Cancelación de Cita con Autorizaciones Activas
**Escenario:** Cita cancelada pero quedan autorizaciones de exámenes pendientes.

**Problema:**
- Paciente intenta usar autorización de cita cancelada
- Recepción/laboratorio no sabe si es válida

**Solución Recomendada:**
- Al cancelar cita, auto-revocar autorizaciones asociadas
- O marcar autorizaciones como "Requiere Validación"
- Notificar al médico para que decida

---

## 5. CASOS DE USO ESPECIALES

### 5.1 Múltiples Citas del Mismo Paciente en un Día
**Escenario:** Paciente tiene cita de cardiología a las 10:00 y neurología a las 15:00.

**Problema:**
- ¿Ambos diagnósticos son independientes?
- ¿El segundo médico ve el diagnóstico del primero?
- ¿Puede haber conflictos de medicamentos autorizados?

**Consideraciones:**
- Mostrar alerta de múltiples citas del día
- Permitir ver diagnósticos recientes del paciente
- Validación cruzada de medicamentos/procedimientos

---

### 5.2 Telemedicina vs Presencial
**Escenario:** Validación temporal puede ser diferente para citas virtuales.

**Problema:**
- Cita presencial: validación estricta de horario
- Cita virtual: paciente puede conectarse antes/después
- ¿Mismas reglas de tiempo límite?

**Consideraciones:**
- Diferenciar tipo de consulta en validaciones
- Flexibilidad de +/- 15 minutos para telemedicina
- Registrar hora real de inicio de consulta virtual

---

### 5.3 Citas de Emergencia
**Escenario:** Atención de emergencia sin cita previa.

**Problema:**
- No hay horario programado
- ¿Cómo validar ventana temporal?
- ¿Registro inmediato obligatorio?

**Solución Recomendada:**
- Tipo especial: "Consulta de Emergencia"
- Validación: debe registrarse dentro de las 2 horas siguientes
- Prioridad alta en notificaciones

---

## 6. SEGURIDAD Y PERMISOS

### 6.1 Médico Editando Diagnóstico de Otro Médico
**Escenario:** Médico B intenta modificar diagnóstico registrado por Médico A.

**Problema:**
- Riesgo de alteración no autorizada
- Responsabilidad médico-legal compartida

**Solución Implementada:**
- SOLO el médico que registró puede modificar
- Excepción: Supervisor con rol especial
- Registro de auditoría de TODAS las modificaciones

---

### 6.2 Acceso al Historial Durante Modificación
**Escenario:** Múltiples usuarios consultando historial mientras se modifica diagnóstico.

**Problema:**
- ¿Se muestra versión antigua o nueva?
- Sincronización de datos en tiempo real

**Solución Recomendada:**
- Lock pesimista durante edición
- Actualización automática de vistas abiertas
- Indicador visual de "Diagnóstico en edición"

---

## 7. NOTIFICACIONES Y ALERTAS

### 7.1 Citas Próximas a Expirar
**Escenario:** Quedan 2 horas para fin del día y aún hay diagnósticos pendientes.

**Problema:**
- Médico no se da cuenta del tiempo límite
- Múltiples citas se marcarán como completadas sin diagnóstico

**Solución Recomendada:**
- Alerta a las 18:00 hrs con citas pendientes
- Alerta a las 21:00 hrs (última advertencia)
- Email/SMS si quedan 30 minutos

---

### 7.2 Notificación de Cambios al Paciente
**Escenario:** Diagnóstico modificado después de que paciente lo recibió.

**Problema:**
- Paciente puede estar siguiendo tratamiento del diagnóstico original
- Cambio no comunicado genera confusión/riesgo

**Solución Recomendada:**
- Notificación automática al paciente de cualquier cambio
- Incluir motivo del cambio (campo requerido)
- Opción de agendar cita de seguimiento

---

## 8. MANEJO DE ERRORES TÉCNICOS

### 8.1 Fallo de Conexión Durante Guardado
**Escenario:** Pérdida de conexión mientras se envía formulario de diagnóstico.

**Problema:**
- ¿El diagnóstico se guardó o no?
- Médico podría intentar re-enviar (duplicación)

**Solución Recomendada:**
- Implementar mecanismo de idempotencia
- Guardado local temporal (localStorage)
- Confirmación explícita de guardado exitoso

---

### 8.2 Inconsistencia de Datos por Caché
**Escenario:** Lista de citas pendientes en caché desactualizada.

**Problema:**
- Muestra citas que ya tienen diagnóstico
- Médico intenta registrar diagnóstico duplicado

**Solución Implementada:**
- Validación del lado del servidor SIEMPRE
- Revalidación de estado antes de mostrar formulario
- Mensaje claro si estado cambió desde carga de página

---

## 9. MÉTRICAS Y AUDITORÍA

### 9.1 Estadísticas de Diagnósticos Tardíos
**Problema:**
- ¿Cómo medir eficiencia del médico?
- ¿Diagnósticos expirados cuentan negativamente?

**Métricas Recomendadas:**
- % de diagnósticos registrados a tiempo
- Tiempo promedio entre fin de cita y registro
- Tasa de modificaciones post-registro

---

### 9.2 Trazabilidad para Auditorías Legales
**Problema:**
- Necesidad de demostrar quién hizo qué y cuándo
- Historial completo de cambios

**Requisitos:**
- Log inmutable de todas las operaciones
- IP, timestamp, usuario para cada cambio
- Retención de datos por 10+ años

---

## 10. RECOMENDACIONES FINALES

### Implementaciones Prioritarias:
1. ✅ **Validación temporal estricta** (inicio de cita hasta medianoche)
2. ✅ **Sistema de modificación con historial**
3. ⚠️ **Notificaciones automáticas de diagnósticos pendientes**
4. ⚠️ **Control de permisos granular para edición**
5. ⚠️ **Integración con autorizaciones (warnings de inconsistencias)**

### Testing Requerido:
- Tests unitarios de validación temporal con diferentes zonas horarias
- Tests de concurrencia para ediciones simultáneas
- Tests de integración con módulo de autorizaciones
- Tests de performance con alto volumen de citas

### Monitoreo en Producción:
- Alertas de alta tasa de diagnósticos expirados
- Dashboard de métricas de tiempo de registro
- Logs de errores de validación temporal
- Tracking de modificaciones frecuentes

---

**Documento Vivo:** Este análisis debe actualizarse conforme se descubran nuevos casos edge en producción.

**Responsable:** Equipo de Desarrollo - Portal Médico  
**Próxima Revisión:** Mensual o después de incidentes críticos
