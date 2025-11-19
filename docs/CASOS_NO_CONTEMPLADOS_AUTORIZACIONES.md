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
- Agregar campo `fecha_vencimiento` (ej: 7 días desde autorización)
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
