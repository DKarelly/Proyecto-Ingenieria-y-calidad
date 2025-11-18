# Casos No Contemplados - Sistema de Autorizaciones de Procedimientos

Este documento identifica casos de uso, escenarios y situaciones que el sistema actual de autorizaciones de procedimientos médicos **NO está contemplando** y que deberían considerarse para futuras mejoras.

---

## 0. DIAGNÓSTICOS SIN AUTORIZACIONES ⚠️

### 0.1 Claridad en la Interfaz del Paciente
**Escenario**: Paciente no entiende por qué los botones de examen/operación están deshabilitados cuando NO necesita ningún procedimiento.

**Situación actual**:
- ✅ Sistema funciona correctamente: diagnósticos sin autorizaciones no habilitan botones
- ❌ Pero puede causar confusión al paciente
- No hay mensaje que explique "Este diagnóstico no requiere procedimientos adicionales"

**Problemas**:
- Paciente ve botones deshabilitados y no sabe si:
  - Necesita autorización del médico
  - O simplemente no necesita esos procedimientos
- Puede pensar que es un error del sistema
- Puede llamar innecesariamente a la clínica

**Impacto**: 
- Confusión del usuario
- Llamadas de soporte innecesarias
- Mala experiencia de usuario

**Solución sugerida**:
```html
<!-- Si NO tiene autorizaciones pendientes -->
<div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
  <div class="flex items-center gap-2">
    <span class="material-symbols-outlined text-green-600">check_circle</span>
    <p class="text-sm text-green-800">
      <strong>Su diagnóstico está completo.</strong> 
      No requiere exámenes ni operaciones adicionales en este momento.
    </p>
  </div>
</div>

<!-- Botones deshabilitados con tooltip -->
<button disabled class="opacity-50 cursor-not-allowed" 
        title="No requiere exámenes según su diagnóstico">
  Agendar Examen
</button>
```

## 1. GESTIÓN DE AUTORIZACIONES

### 1.1 Vencimiento de Autorizaciones
**Escenario**: Un médico autoriza un examen pero el paciente no lo realiza en un tiempo razonable.

**Problemas**:
- No hay fecha de vencimiento para las autorizaciones
- Las autorizaciones permanecen vigentes indefinidamente
- No hay alertas de autorizaciones antiguas sin usar

**Impacto**: 
- Pacientes podrían usar autorizaciones muy antiguas que ya no son relevantes
- Acumulación de autorizaciones obsoletas en el sistema

**Solución sugerida**:
- Agregar campo `fecha_vencimiento` (ej: 30 días desde autorización)
- Proceso automático que marque como vencidas
- Alertas para médico y paciente antes del vencimiento

---

### 1.2 Modificación de Autorizaciones
**Escenario**: Un médico se equivoca o necesita cambiar los detalles de una autorización ya emitida.

**Problemas**:
- No hay funcionalidad para editar autorizaciones
- No se puede actualizar descripción, prioridad o médico asignado después de crear
- No hay historial de cambios en autorizaciones

**Impacto**:
- Necesidad de cancelar y crear nueva autorización (pierde trazabilidad)
- Errores permanecen sin corrección

**Solución sugerida**:
- Implementar edición de autorizaciones en estado PENDIENTE
- Log de auditoría de cambios
- Notificación al paciente si hay cambios significativos

---

### 1.3 Consumo de Autorizaciones
**Escenario**: Un paciente tiene autorización pero aún no agenda/realiza el procedimiento.

**Problemas**:
- No hay vínculo directo entre AUTORIZACION_PROCEDIMIENTO y RESERVA/EXAMEN/OPERACION
- Podría usarse múltiples veces la misma autorización
- No se registra cuándo/cómo fue utilizada

**Impacto**:
- Falta de control sobre uso de autorizaciones
- Datos inconsistentes entre autorizaciones y procedimientos reales
- No hay trazabilidad del consumo

**Solución sugerida**:
- Agregar `id_reserva_generada` en AUTORIZACION_PROCEDIMIENTO
- Agregar `fecha_uso` en AUTORIZACION_PROCEDIMIENTO
- Prevenir múltiples usos de la misma autorización

---

## 2. CONTROL Y VALIDACIONES

### 2.1 Validación de Especialidad del Médico
**Escenario**: Se autoriza una operación de cardiología pero se asigna a un traumatólogo.

**Problemas**:
- No hay validación que el médico asignado tenga la especialidad requerida
- Se puede asignar cualquier médico independiente de su especialidad
- El sistema no previene asignaciones incorrectas

**Impacto**:
- Riesgo de errores médicos graves
- Pacientes asignados a médicos no capacitados

**Solución sugerida**:
- Validación en backend: `id_medico_asignado` debe tener `id_especialidad` = `id_especialidad_requerida`
- Mostrar solo médicos compatibles en el frontend
- Alerta si se intenta asignar médico incompatible

---

### 2.2 Capacidad y Disponibilidad del Médico
**Escenario**: Se asigna una operación urgente a un médico que ya tiene agenda llena.

**Problemas**:
- No se verifica disponibilidad del médico antes de asignar
- No se considera carga de trabajo actual
- No hay alertas de sobrecarga

**Impacto**:
- Retrasos en procedimientos urgentes
- Sobrecarga de ciertos médicos
- Pacientes esperan más tiempo del necesario

**Solución sugerida**:
- Integrar con sistema de horarios para verificar disponibilidad
- Mostrar carga de trabajo al asignar médico
- Sugerir médicos con disponibilidad inmediata

---

### 2.3 Conflictos de Autorizaciones
**Escenario**: Dos médicos autorizan operaciones diferentes para el mismo paciente sin coordinación.

**Problemas**:
- No hay validación de autorizaciones duplicadas o conflictivas
- No se alertan autorizaciones múltiples recientes
- Falta de coordinación entre médicos

**Impacto**:
- Procedimientos duplicados o contradictorios
- Riesgo para la salud del paciente
- Desperdicio de recursos

**Solución sugerida**:
- Alertar cuando hay autorizaciones múltiples del mismo tipo para un paciente
- Dashboard de autorizaciones activas del paciente
- Sistema de coordinación entre médicos

---

### 4.2 Coordinación con Disponibilidad de Recursos
**Escenario**: Se autoriza operación pero no hay quirófano disponible o equipamiento necesario.

**Problemas**:
- No se verifica disponibilidad de quirófanos
- No se considera equipamiento médico necesario
- No hay reserva automática de recursos

**Impacto**:
- Operaciones autorizadas pero no realizables
- Retrasos por falta de recursos
- Frustración de pacientes y médicos

**Solución sugerida**:
- Sistema de gestión de recursos (quirófanos, equipos)
- Validación de recursos antes de aprobar
- Reserva automática al aprobar autorización
- Alertas de conflictos de recursos

---

### 4.3 Comunicación con Laboratorios Externos
**Escenario**: Examen debe realizarse en laboratorio externo o con equipos especializados.

**Problemas**:
- No hay indicación de dónde realizar el procedimiento
- No se coordinan citas con proveedores externos
- Paciente debe gestionar todo manualmente

**Impacto**:
- Confusión del paciente sobre dónde ir
- Retrasos en obtención de resultados
- Falta de seguimiento

**Solución sugerida**:
- Campo `ubicacion_procedimiento` (interno/externo)
- Lista de laboratorios/proveedores asociados
- Integración para agendar automáticamente
- Seguimiento de resultados externos

---

## 5. COMUNICACIÓN Y NOTIFICACIONES

### 5.1 Notificaciones al Paciente
**Escenario**: Paciente recibe autorización pero no es notificado adecuadamente.

**Problemas**:
- No hay sistema de notificaciones para autorizaciones
- Paciente debe entrar al sistema para saber si tiene autorizaciones
- No sabe pasos a seguir después de recibir autorización

**Impacto**:
- Autorizaciones no utilizadas por desconocimiento
- Procedimientos no realizados
- Vencimiento de autorizaciones sin uso

**Solución sugerida**:
- Email/SMS automático al crear autorización
- Instrucciones claras de próximos pasos
- Recordatorios periódicos si no se usa
- Alerta de próximo vencimiento

---

### 5.2 Notificaciones al Médico Asignado
**Escenario**: Médico es asignado a operación pero no se entera hasta que el paciente agenda.

**Problemas**:
- No notifica al médico cuando se le asigna
- Médico no puede prepararse con anticipación
- No puede rechazar si no tiene disponibilidad

**Impacto**:
- Médicos sorprendidos con asignaciones
- Falta de preparación adecuada
- Conflictos de agenda

**Solución sugerida**:
- Notificación inmediata al asignar médico
- Opción para médico de aceptar/rechazar asignación
- Vista de autorizaciones pendientes en dashboard médico
- Tiempo de preparación antes de agendar con paciente

---

## 7. EXPERIENCIA DEL USUARIO

### 7.1 Vista del Paciente - Botones Deshabilitados
**Escenario**: Paciente ve botones de examen/operación pero no entiende por qué están deshabilitados.

**Problemas**:
- No hay mensaje explicativo claro
- Paciente no sabe que necesita autorización médica
- No se indica cómo obtener autorización

**Impacto**:
- Confusión del paciente
- Llamadas innecesarias a soporte
- Frustración

**Solución sugerida**:
- Tooltip explicativo en botones deshabilitados
- Mensaje: "Necesita autorización médica para este procedimiento"
- Enlace a "¿Cómo obtener autorización?"
- Indicar próxima cita con médico

---

### 7.2 Vista del Paciente - Historial de Autorizaciones
**Escenario**: Paciente quiere ver qué autorizaciones ha recibido históricamente.

**Problemas**:
- No hay vista de autorizaciones para pacientes
- No puede ver estado de sus autorizaciones
- No sabe si están pendientes, vencidas, o usadas

**Impacto**:
- Falta de transparencia
- Paciente no puede planificar
- Llamadas constantes para consultar estado

**Solución sugerida**:
- Dashboard de autorizaciones para paciente
- Estado claro de cada autorización
- Fecha de vencimiento visible
- Instrucciones de qué hacer con cada una

---

### 7.3 Dashboard del Médico - Autorizaciones Otorgadas
**Escenario**: Médico quiere ver qué autorizaciones ha dado y su estado.

**Problemas**:
- No hay vista consolidada de autorizaciones otorgadas
- No puede ver si fueron usadas o están pendientes
- No hay métricas de sus autorizaciones

**Impacto**:
- Falta de seguimiento
- No sabe si pacientes siguieron indicaciones
- No puede evaluar efectividad de sus autorizaciones

**Solución sugerida**:
- Sección "Mis Autorizaciones" en panel médico
- Filtros por estado, tipo, paciente, fecha
- Métricas: total autorizadas, usadas, vencidas, pendientes
- Alertas de autorizaciones importantes sin usar

---

## 8. CASOS ESPECIALES Y EDGE CASES

### 8.1 Cambio de Médico Tratante
**Escenario**: Paciente cambia de médico tratante pero tiene autorizaciones del médico anterior.

**Problemas**:
- No hay mecanismo para transferir autorizaciones
- Nuevo médico no ve autorizaciones del anterior
- Paciente debe solicitar autorizaciones nuevamente

**Impacto**:
- Duplicación de esfuerzos
- Retrasos innecesarios
- Pérdida de continuidad

**Solución sugerida**:
- Función de transferencia de autorizaciones
- Nuevo médico puede validar y adoptar autorizaciones existentes
- Historial accesible para nuevo médico

---

### 8.2 Cancelación del Paciente
**Escenario**: Paciente decide no realizarse el procedimiento autorizado.

**Problemas**:
- No hay forma clara para paciente de cancelar autorización
- Queda como vigente indefinidamente
- No se libera el recurso del médico asignado

**Impacto**:
- Datos inconsistentes
- Médicos asignados sin necesidad
- Métricas incorrectas

**Solución sugerida**:
- Agregar tabla CANCELACION_AUTORIZACION con motivo y fecha
- Botón de "Rechazar/Cancelar procedimiento" para paciente
- Campo de motivo de cancelación
- Notificar a médico autorizante y asignado
- Liberar recursos automáticamente

---

### 8.3 Procedimientos Múltiples o Secuenciales
**Escenario**: Paciente necesita serie de exámenes o múltiples operaciones relacionadas.

**Problemas**:
- Cada autorización es independiente
- No hay concepto de "paquete" o "tratamiento"
- No se maneja secuencia o dependencias

**Impacto**:
- Difícil coordinar tratamientos complejos
- Riesgo de hacer procedimientos fuera de orden
- Falta de visión integral

**Solución sugerida**:
- Nueva tabla PLAN_TRATAMIENTO que agrupa autorizaciones
- Campo `orden_secuencia` en autorizaciones
- Indicar dependencias entre autorizaciones
- Validar que se completen en orden correcto
- Vista consolidada del tratamiento completo

---

### 8.4 Procedimientos Recurrentes
**Escenario**: Paciente necesita exámenes de control periódicos (ej: cada 3 meses).

**Problemas**:
- Debe solicitar autorización cada vez
- No hay autorizaciones recurrentes
- Médico debe autorizar manualmente cada instancia

**Impacto**:
- Carga administrativa innecesaria
- Retrasos en tratamientos crónicos
- Pacientes olvidan solicitar

**Solución sugerida**:
- Autorizaciones recurrentes con frecuencia definida
- Generación automática de nuevas autorizaciones
- Alertas automáticas al paciente en cada periodo
- Revisión médica periódica del plan recurrente


## 11. ESCALABILIDAD Y RENDIMIENTO

### 11.1 Gran Volumen de Autorizaciones
**Escenario**: Hospital crece y tiene miles de autorizaciones activas.

**Problemas**:
- Queries pueden volverse lentos
- No hay índices optimizados
- Dashboard puede tardar en cargar

**Impacto**:
- Sistema lento
- Mala experiencia de usuario
- Timeouts en operaciones

**Solución sugerida**:
- Índices compuestos en campos más consultados
- Paginación en todas las listas
- Cache de consultas frecuentes
- Archivado automático de autorizaciones antiguas
- Optimización de queries

---