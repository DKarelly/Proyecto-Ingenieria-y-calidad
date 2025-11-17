# Ejemplos de Uso - Sistema de Autorizaciones

## 📚 Casos de Uso Detallados

### Caso 1: Diagnóstico Simple con Examen

**Contexto:** El Dr. García atiende a Juan Pérez que tiene síntomas de diabetes.

**Pasos:**

1. **Doctor completa diagnóstico:**
   - Ingresa diagnóstico: "Sospecha de diabetes mellitus tipo 2"
   - Observaciones: "Control cada 3 meses"
   - Selecciona examen: "Glucosa en Ayunas"
   - Observaciones del examen: "Realizar en ayuno de 8 horas mínimo"
   - Guarda diagnóstico

2. **Sistema crea:**
   - Actualiza cita a "Completada"
   - Crea registro en AUTORIZACION_EXAMEN
   - Estado: "Pendiente"

3. **Paciente accede:**
   - Va a `/paciente/autorizaciones`
   - Ve: "Glucosa en Ayunas - Autorizado por Dr. García"
   - Click en "Programar Examen"
   - Sistema redirige a formulario de reserva

**Resultado:**
```
✅ Diagnóstico registrado
✅ Examen autorizado
✅ Paciente puede programar
```

---

### Caso 2: Operación - Mismo Médico

**Contexto:** La Dra. Fernández atiende a María López que necesita cirugía ginecológica.

**Pasos:**

1. **Doctor completa diagnóstico:**
   - Ingresa diagnóstico: "Miomas uterinos múltiples"
   - Selecciona operación: "Cirugía Ginecológica"
   - Deja combo de médico en: "Yo realizaré la operación"
   - Observaciones: "Programar en 2-3 semanas. Preparación prequirúrgica necesaria"
   - Guarda diagnóstico

2. **Sistema crea:**
   - Actualiza cita a "Completada"
   - Crea registro en AUTORIZACION_OPERACION
   - id_empleado_asignado = id de Dra. Fernández
   - es_derivacion = 0
   - Estado: "Pendiente"

3. **Paciente accede:**
   - Ve: "Cirugía Ginecológica"
   - Médico asignado: "Dra. Fernández" (misma doctora)
   - Click en "Programar Operación"

**Resultado:**
```
✅ Diagnóstico registrado
✅ Operación autorizada
✅ Mismo médico la realizará
✅ Paciente puede programar
```

---

### Caso 3: Operación - Derivación

**Contexto:** El Dr. Rodríguez (Traumatología) atiende a Pedro Sánchez que necesita artroscopía, pero el Dr. Rodríguez no puede realizarla.

**Pasos:**

1. **Doctor completa diagnóstico:**
   - Ingresa diagnóstico: "Lesión de menisco, requiere artroscopía"
   - Selecciona operación: "Artroscopía"
   - Selecciona médico: "Dr. Miguel Rodríguez Castro - Traumatología"
   - Observaciones: "Derivado por disponibilidad de quirófano"
   - Guarda diagnóstico

2. **Sistema verifica:**
   - Ambos médicos tienen especialidad: Traumatología ✅
   - Dr. Miguel tiene horarios activos ✅
   - Servicio "Artroscopía" es de tipo Operación ✅

3. **Sistema crea:**
   - Actualiza cita a "Completada"
   - Crea registro en AUTORIZACION_OPERACION
   - id_empleado_autoriza = Dr. Rodríguez (quien autoriza)
   - id_empleado_asignado = Dr. Miguel (quien operará)
   - es_derivacion = 1 ✅
   - Estado: "Pendiente"

4. **Paciente accede:**
   - Ve: "Artroscopía" con etiqueta "Derivado" 🔄
   - Autorizado por: "Dr. Rodríguez"
   - Médico asignado: "Dr. Miguel Rodríguez Castro"
   - Click en "Programar Operación"

**Resultado:**
```
✅ Diagnóstico registrado
✅ Operación autorizada
✅ Derivado a especialista disponible
✅ Paciente puede programar
```

---

### Caso 4: Diagnóstico Completo (Examen + Operación)

**Contexto:** El Dr. García (Cardiólogo) atiende a Ana Ramírez con problemas cardíacos serios.

**Pasos:**

1. **Doctor completa diagnóstico:**
   - Diagnóstico: "Enfermedad coronaria severa, requiere evaluación prequirúrgica"
   - **Autoriza examen:**
     - Selecciona: "Ecocardiograma"
     - Observaciones: "Evaluar función ventricular antes de cirugía"
   - **Autoriza operación:**
     - Selecciona: "Cirugía Cardiovascular"
     - Médico: "Yo realizaré la operación"
     - Observaciones: "Pendiente de resultados de eco. Cirugía en 4-6 semanas"
   - Guarda diagnóstico

2. **Sistema crea:**
   - Actualiza cita a "Completada"
   - Crea registro en AUTORIZACION_EXAMEN
   - Crea registro en AUTORIZACION_OPERACION
   - Ambos con estado: "Pendiente"

3. **Paciente accede:**
   - Ve 2 autorizaciones:
     1. **Examen:** "Ecocardiograma" → Botón "Programar Examen"
     2. **Operación:** "Cirugía Cardiovascular" → Botón "Programar Operación"
   - Puede programar ambos en orden que prefiera

**Resultado:**
```
✅ Diagnóstico registrado
✅ Examen autorizado
✅ Operación autorizada
✅ Paciente puede programar ambos
```

---

### Caso 5: Solo Diagnóstico (Sin Autorizaciones)

**Contexto:** La Dra. López atiende consulta de control de presión arterial.

**Pasos:**

1. **Doctor completa diagnóstico:**
   - Diagnóstico: "Presión arterial controlada. Continuar con medicación actual"
   - Observaciones: "Control en 6 meses"
   - NO selecciona examen (deja en "-- No autorizar examen --")
   - NO selecciona operación (deja en "-- No autorizar operación --")
   - Guarda diagnóstico

2. **Sistema crea:**
   - Actualiza cita a "Completada"
   - NO crea registros de autorización

3. **Paciente accede:**
   - Ve mensaje: "No tienes autorizaciones pendientes"
   - No hay botones de programación

**Resultado:**
```
✅ Diagnóstico registrado
⚪ Sin autorizaciones necesarias
⚪ Paciente NO necesita programar nada
```

---

## 🎨 Interfaces de Usuario

### Pantalla del Médico - Formulario de Diagnóstico

```
┌─────────────────────────────────────────────────────────┐
│ Registrar Diagnóstico                                   │
│ Paciente: Juan Pérez - DNI: 12345678                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Diagnóstico: *                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Sospecha de diabetes mellitus tipo 2...            │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Observaciones del Diagnóstico:                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Control cada 3 meses...                             │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ═══════════════ Autorizaciones ═══════════════         │
│                                                         │
│ 🧪 Autorizar Examen                                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Glucosa en Ayunas                            ▼     │ │
│ └─────────────────────────────────────────────────────┘ │
│ Observaciones:                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Realizar en ayuno de 8 horas mínimo                │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🔪 Autorizar Operación                                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ -- No autorizar operación --                 ▼     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [Guardar Diagnóstico]  [Cancelar]                      │
└─────────────────────────────────────────────────────────┘
```

### Pantalla del Paciente - Autorizaciones

```
┌─────────────────────────────────────────────────────────┐
│ 🎫 Autorizaciones Médicas                               │
│ Exámenes y operaciones autorizados por tu médico       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 🧪 EXÁMENES AUTORIZADOS                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🔬 Glucosa en Ayunas                                │ │
│ │                                                     │ │
│ │ Autorizado por: Dr. Carlos García                  │ │
│ │ Fecha: 15 de noviembre 2024                        │ │
│ │                                                     │ │
│ │ ℹ️ Realizar en ayuno de 8 horas mínimo            │ │
│ │                                                     │ │
│ │                        [📅 Programar Examen]       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🔪 OPERACIONES AUTORIZADAS                              │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ No tienes operaciones autorizadas pendientes       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Estados del Sistema

### Estados de Autorización

```
┌──────────────┐
│  Pendiente   │ → Estado inicial al crear autorización
└──────┬───────┘
       │ Paciente programa
       ▼
┌──────────────┐
│  Programado  │ → Tiene reserva/cita asociada
└──────┬───────┘
       │ Se realiza el procedimiento
       ▼
┌──────────────┐
│  Completado  │ → Procedimiento finalizado
└──────────────┘

       O

┌──────────────┐
│  Cancelado   │ → Autorización anulada (cualquier momento)
└──────────────┘
```

### Transiciones de Estado

| Estado Actual | Acción | Estado Final |
|--------------|---------|-------------|
| Pendiente | Paciente programa | Programado |
| Pendiente | Médico cancela | Cancelado |
| Programado | Se realiza | Completado |
| Programado | Se cancela reserva | Pendiente |
| Cualquiera | Cancelación definitiva | Cancelado |

---

## 💡 Consejos de Uso

### Para Médicos

1. **Siempre complete el diagnóstico primero**
   - Es el campo obligatorio
   - Las autorizaciones son opcionales

2. **Use observaciones específicas**
   - Ayudan al paciente a prepararse
   - Ejemplo: "ayuno de 8 horas", "traer acompañante"

3. **Derive solo cuando sea necesario**
   - Por especialización específica
   - Por disponibilidad de agenda
   - Por equipamiento especial

4. **Revise la especialidad antes de derivar**
   - Solo aparecen médicos de la misma especialidad
   - Todos están activos y con horarios disponibles

### Para Pacientes

1. **Revise regularmente sus autorizaciones**
   - Acceda a `/paciente/autorizaciones`
   - Programe lo antes posible

2. **Lea las observaciones del médico**
   - Contienen instrucciones importantes
   - Ej: preparación, ayuno, documentos necesarios

3. **Priorice según urgencia**
   - Algunos exámenes son pre-operatorios
   - Consulte con el médico si tiene dudas

---

## 🐛 Resolución de Problemas

### Problema: No veo ninguna autorización

**Posibles causas:**
- El médico no autorizó ningún procedimiento
- Ya fueron programadas todas (estado = "Programado")
- Error en la carga de datos

**Solución:**
1. Verificar en historial clínico si hay diagnóstico
2. Contactar al médico si esperaba autorización
3. Revisar consola del navegador (F12) para errores

### Problema: No aparecen operaciones en el combo box

**Posibles causas:**
- El médico no tiene especialidad asignada
- No hay operaciones para esa especialidad
- Servicios inactivos en catálogo

**Solución:**
1. Verificar especialidad del médico en EMPLEADO
2. Verificar servicios activos tipo_servicio = 2
3. Revisar logs del servidor

### Problema: No aparecen médicos para derivar

**Posibles causas:**
- No hay otros médicos de la misma especialidad
- Otros médicos no tienen horarios activos
- Otros médicos están inactivos

**Solución:**
1. Verificar tabla EMPLEADO: especialidad y estado
2. Verificar tabla HORARIO: activo = 1
3. El médico deberá realizar la operación él mismo

---

## 📊 Reportes Útiles (SQL)

### Ver autorizaciones pendientes por médico

```sql
SELECT 
    CONCAT(e.nombres, ' ', e.apellidos) as medico,
    COUNT(ae.id_autorizacion_examen) as examenes_pendientes,
    COUNT(ao.id_autorizacion_operacion) as operaciones_pendientes
FROM EMPLEADO e
LEFT JOIN AUTORIZACION_EXAMEN ae ON e.id_empleado = ae.id_empleado_autoriza 
    AND ae.estado = 'Pendiente'
LEFT JOIN AUTORIZACION_OPERACION ao ON e.id_empleado = ao.id_empleado_autoriza 
    AND ao.estado = 'Pendiente'
WHERE e.id_rol = 2
GROUP BY e.id_empleado
ORDER BY (COUNT(ae.id_autorizacion_examen) + COUNT(ao.id_autorizacion_operacion)) DESC;
```

### Ver autorizaciones por paciente

```sql
SELECT 
    CONCAT(p.nombres, ' ', p.apellidos) as paciente,
    'Examen' as tipo,
    s.nombre as servicio,
    ae.fecha_autorizacion,
    ae.estado
FROM AUTORIZACION_EXAMEN ae
INNER JOIN PACIENTE p ON ae.id_paciente = p.id_paciente
INNER JOIN SERVICIO s ON ae.id_servicio = s.id_servicio
WHERE p.id_paciente = ?
UNION ALL
SELECT 
    CONCAT(p.nombres, ' ', p.apellidos) as paciente,
    'Operación' as tipo,
    s.nombre as servicio,
    ao.fecha_autorizacion,
    ao.estado
FROM AUTORIZACION_OPERACION ao
INNER JOIN PACIENTE p ON ao.id_paciente = p.id_paciente
INNER JOIN SERVICIO s ON ao.id_servicio = s.id_servicio
WHERE p.id_paciente = ?
ORDER BY fecha_autorizacion DESC;
```

---

## ✅ Checklist de Pruebas

- [ ] Crear diagnóstico sin autorizaciones
- [ ] Crear diagnóstico con examen
- [ ] Crear diagnóstico con operación (mismo médico)
- [ ] Crear diagnóstico con operación derivada
- [ ] Crear diagnóstico con examen + operación
- [ ] Ver autorizaciones como paciente (sin autorizaciones)
- [ ] Ver autorizaciones como paciente (con autorizaciones)
- [ ] Intentar acceder como usuario no autenticado
- [ ] Intentar acceder como médico a página de paciente
- [ ] Verificar combo boxes se cargan correctamente
- [ ] Verificar filtrado por especialidad funciona
- [ ] Verificar que solo aparecen médicos activos para derivación
