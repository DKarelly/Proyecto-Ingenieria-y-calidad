# Mejoras Implementadas - Sistema de Autorizaciones de Procedimientos

Este documento detalla todas las mejoras implementadas para solucionar los casos no contemplados identificados en `CASOS_NO_CONTEMPLADOS_AUTORIZACIONES.md`.

## Fecha de Implementación
**18 de Noviembre de 2025**

## Última Actualización (Simplificación)
**18 de Noviembre de 2025** - Se removieron los campos `descripcion` y `prioridad` para simplificar la implementación. Ver `CAMPOS_REMOVIDOS.md` para detalles.

---

## 📋 Resumen de Implementaciones

### ✅ Punto 0.1: Claridad en la Interfaz del Paciente
**Problema**: Pacientes confundidos cuando no tienen autorizaciones pendientes.

**Solución Implementada**:
- Mensajes informativos en `home.html` que explican claramente el estado de sus autorizaciones
- Tres estados posibles:
  1. **Con autorización aprobada**: Mensaje verde confirmando que puede agendar
  2. **Sin autorización**: Mensaje azul explicando que necesita consulta médica
  3. **Diagnóstico completo**: Mensaje verde indicando que no requiere procedimientos

**Archivos modificados**:
- `templates/home.html`
- `routes/usuarios.py` (nuevo endpoint `/api/usuario/actual`)

---

### ✅ Punto 1.1: Vencimiento de Autorizaciones
**Problema**: Autorizaciones sin fecha de vencimiento permanecen vigentes indefinidamente.

**Solución Implementada**:
- Campo `fecha_vencimiento` (7 días desde emisión por defecto)
- Nuevo estado: `VENCIDA`
- Método `marcar_vencidas()` para marcar autorizaciones expiradas
- Método `obtener_por_vencer(dias)` para obtener autorizaciones próximas a vencer
- Vista SQL `v_autorizaciones_activas` que excluye vencidas

**Archivos modificados**:
- `models/autorizacion_procedimiento.py`
- `scripts/agregar_campos_autorizaciones.sql`

---

### ✅ Punto 1.2: Modificación de Autorizaciones
**Problema**: No se pueden editar autorizaciones después de creadas.

**Solución Implementada**:
- Nuevo método `editar_pendiente()` que permite editar solo en estado PENDIENTE
- Tabla de auditoría `AUTORIZACION_PROCEDIMIENTO_AUDITORIA` para rastrear cambios
- Método `_registrar_auditoria()` que registra automáticamente todos los cambios
- Actualización del método `actualizar()` para soportar auditoría opcional

**Campos editables**:
- `id_medico_asignado`
- `id_servicio`
- `estado`
- `id_especialidad_requerida`
- `fecha_vencimiento`

**Archivos modificados**:
- `models/autorizacion_procedimiento.py`
- `scripts/agregar_campos_autorizaciones.sql`

---

### ✅ Punto 1.3: Consumo de Autorizaciones
**Problema**: No hay vínculo entre autorizaciones y procedimientos generados.

**Solución Implementada**:
- Campo `id_reserva_generada` para vincular autorización con reserva/procedimiento
- Campo `fecha_uso` para registrar cuándo fue utilizada
- Método `consumir_autorizacion()` que:
  - Valida que no haya sido usada antes
  - Verifica que no esté vencida
  - Vincula con la reserva generada
  - Marca como COMPLETADA
- Prevención de uso múltiple de la misma autorización

**Archivos modificados**:
- `models/autorizacion_procedimiento.py`
- `scripts/agregar_campos_autorizaciones.sql`

---

### ✅ Punto 2.1: Validación de Especialidad del Médico
**Problema**: Se puede asignar cualquier médico sin validar especialidad.

**Solución Implementada**:
- Método `asignar_medico()` actualizado con validación automática
- Verificación que el médico tenga la especialidad requerida
- Parámetro opcional `validar_especialidad` para casos excepcionales
- Retorno de error específico si especialidad no coincide

**Flujo de validación**:
```python
resultado = AutorizacionProcedimiento.asignar_medico(
    id_autorizacion=123,
    id_medico=456,
    validar_especialidad=True  # Por defecto
)

if not resultado['success']:
    if resultado.get('requiere_confirmacion'):
        # Médico no tiene especialidad - pedir confirmación administrativa
        pass
```

**Archivos modificados**:
- `models/autorizacion_procedimiento.py`

---

### ✅ Punto 5.1: Notificaciones al Paciente
**Problema**: Paciente no es notificado cuando recibe autorización.

**Solución Implementada**:
- Sistema automático de notificaciones al crear autorizaciones
- Notificación detallada con:
  - Tipo de procedimiento autorizado
  - Servicio específico
  - Fecha de vencimiento y días restantes
  - Pasos claros para agendar
  - Advertencia de vencimiento
- Notificaciones de recordatorio 2 días antes del vencimiento

**Tipos de notificaciones**:
1. `autorizacion_recibida`: Al crear la autorización
2. `autorizacion_por_vencer`: 2 días antes del vencimiento

**Archivos creados/modificados**:
- `utils/notificaciones_autorizaciones.py` (nuevo)
- `models/autorizacion_procedimiento.py`
- `scripts/tareas_autorizaciones.py` (nuevo)

---

### ✅ Punto 5.2: Notificaciones al Médico Asignado
**Problema**: Médico no sabe cuando es asignado a un procedimiento.

**Solución Implementada**:
- Notificación automática al asignar médico
- Información incluida:
  - Datos del paciente
  - Tipo de procedimiento
  - Servicio a realizar
  - Instrucciones para prepararse
- Método `asignar_medico()` actualizado para enviar notificaciones

**Archivos modificados**:
- `utils/notificaciones_autorizaciones.py`
- `models/autorizacion_procedimiento.py`

---

### ✅ Punto 7.1: Vista del Paciente - Mensajes Explicativos
**Problema**: Botones deshabilitados sin explicación clara.

**Solución Implementada**:
- Sistema JavaScript que verifica autorizaciones al cargar página
- Mensajes contextuales según estado:
  - **Con autorización**: Mensaje verde de confirmación
  - **Sin autorización**: Mensaje azul explicando que necesita consulta
  - **Sin procedimientos**: Mensaje verde indicando diagnóstico completo
- Botones deshabilitados con tooltips explicativos
- Estilo visual diferenciado (opacidad reducida + cursor no permitido)

**Archivos modificados**:
- `templates/home.html`

---

## 🗄️ Nuevos Campos de Base de Datos

### Tabla: AUTORIZACION_PROCEDIMIENTO

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha_vencimiento` | DATETIME | Fecha límite para usar la autorización (7 días) |
| `fecha_uso` | DATETIME | Fecha en que se consumió la autorización |
| `id_reserva_generada` | INT | ID de la reserva/procedimiento generado |

### Nueva Tabla: AUTORIZACION_PROCEDIMIENTO_AUDITORIA

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_auditoria` | INT | ID único de la auditoría |
| `id_autorizacion` | INT | Autorización modificada |
| `campo_modificado` | VARCHAR(100) | Campo que cambió |
| `valor_anterior` | TEXT | Valor antes del cambio |
| `valor_nuevo` | TEXT | Valor después del cambio |
| `id_usuario_modifica` | INT | Usuario que realizó el cambio |
| `fecha_modificacion` | DATETIME | Cuándo se hizo el cambio |
| `observaciones` | TEXT | Notas adicionales |

### Nueva Vista: v_autorizaciones_activas
Filtra automáticamente autorizaciones pendientes, no vencidas y no utilizadas.

---

## 📁 Archivos Nuevos Creados

1. **scripts/agregar_campos_autorizaciones.sql**
   - Script SQL para agregar nuevos campos
   - Crear tabla de auditoría
   - Crear vista de autorizaciones activas
   - Actualizar índices

2. **utils/notificaciones_autorizaciones.py**
   - `crear_notificacion_autorizacion_paciente()`
   - `crear_notificacion_autorizacion_medico()`
   - `crear_notificacion_vencimiento_proximo()`
   - `enviar_email_autorizacion_paciente()` (preparado para integración)
   - `enviar_email_autorizacion_medico()` (preparado para integración)

3. **scripts/tareas_autorizaciones.py**
   - Script para ejecutar tareas programadas
   - Marcar autorizaciones vencidas
   - Enviar recordatorios de vencimiento

---

## 🔧 Métodos Nuevos/Actualizados

### models/autorizacion_procedimiento.py

**Nuevos métodos**:
- `editar_pendiente(id_autorizacion, data, id_usuario_modifica)` - Editar solo PENDIENTES
- `_registrar_auditoria()` - Registrar cambios en auditoría
- `consumir_autorizacion(id_autorizacion, id_reserva)` - Vincular con procedimiento
- `marcar_vencidas()` - Marcar autorizaciones expiradas
- `obtener_por_vencer(dias)` - Obtener autorizaciones próximas a vencer

**Métodos actualizados**:
- `crear()` - Ahora incluye fecha_vencimiento y envía notificaciones
- `actualizar()` - Soporta auditoría opcional
- `asignar_medico()` - Valida especialidad y envía notificaciones
- `obtener_pendientes_por_paciente()` - Excluye vencidas y usadas

---

## 🚀 Instrucciones de Despliegue

### 1. Ejecutar Script SQL
```bash
mysql -u usuario -p nombre_bd < scripts/agregar_campos_autorizaciones.sql
```

### 2. Configurar Tarea Programada (Cron Job)

**En Linux/Mac**:
```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar diariamente a las 6:00 AM
0 6 * * * cd /ruta/proyecto && python scripts/tareas_autorizaciones.py >> logs/tareas_autorizaciones.log 2>&1
```

**En Windows (Task Scheduler)**:
1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Nombre: "Tareas Autorizaciones Clínica"
4. Disparador: Diario a las 6:00 AM
5. Acción: Iniciar programa
   - Programa: `python.exe`
   - Argumentos: `scripts/tareas_autorizaciones.py`
   - Directorio: Ruta del proyecto

### 3. Reiniciar Aplicación
```bash
# Si usa systemd
sudo systemctl restart clinica-app

# O reiniciar servidor web
```

---

## 📊 Flujos de Trabajo Mejorados

### Flujo 1: Crear Autorización
```
1. Médico crea autorización desde cita
2. Sistema:
   - Establece fecha_vencimiento (+ 7 días)
   - Guarda en BD
   - Envía notificación al paciente ✉️
   - Si hay médico asignado, le notifica ✉️
3. Paciente recibe notificación con instrucciones
4. Médico asignado recibe notificación
```

### Flujo 2: Paciente Agenda Procedimiento
```
1. Paciente ingresa al sistema
2. JavaScript verifica autorizaciones disponibles
3. Si tiene autorización:
   - Muestra mensaje verde de confirmación
   - Habilita botón de agendar
4. Si NO tiene autorización:
   - Muestra mensaje explicativo
   - Deshabilita botón con tooltip
5. Al agendar:
   - Sistema consume autorización
   - Vincula con reserva generada
   - Marca como COMPLETADA
```

### Flujo 3: Recordatorios Automáticos
```
Tarea programada diaria:
1. Marca autorizaciones vencidas
2. Busca autorizaciones por vencer (2 días)
3. Envía recordatorio a cada paciente
4. Registra en log
```

---

## 🧪 Pruebas Recomendadas

### Test 1: Crear Autorización
```python
data = {
    'id_cita': 123,
    'id_paciente': 456,
    'id_medico_autoriza': 789,
    'tipo_procedimiento': 'EXAMEN',
    'id_servicio': 10,
    'id_especialidad_requerida': 3,
    'id_medico_asignado': 790
}

resultado = AutorizacionProcedimiento.crear(data)
assert resultado['success'] == True
assert 'fecha_vencimiento' in resultado
```

### Test 2: Validar Especialidad
```python
# Asignar médico con especialidad incorrecta
resultado = AutorizacionProcedimiento.asignar_medico(
    id_autorizacion=123,
    id_medico=999,  # Médico sin especialidad requerida
    validar_especialidad=True
)

assert resultado['success'] == False
assert resultado.get('requiere_confirmacion') == True
```

### Test 3: Consumir Autorización
```python
# Primera vez - debe funcionar
resultado = AutorizacionProcedimiento.consumir_autorizacion(
    id_autorizacion=123,
    id_reserva=456
)
assert resultado['success'] == True

# Segunda vez - debe fallar
resultado2 = AutorizacionProcedimiento.consumir_autorizacion(
    id_autorizacion=123,
    id_reserva=457
)
assert resultado2['success'] == False
assert 'ya fue utilizada' in resultado2['error']
```

### Test 4: Marcar Vencidas
```python
resultado = AutorizacionProcedimiento.marcar_vencidas()
assert resultado['success'] == True
print(f"Autorizaciones vencidas: {resultado['autorizaciones_vencidas']}")
```

---

## 📈 Métricas e Indicadores

### KPIs Sugeridos
1. **Tasa de uso de autorizaciones**: `(autorizaciones_usadas / autorizaciones_creadas) * 100`
2. **Tiempo promedio de uso**: Días entre `fecha_autorizacion` y `fecha_uso`
3. **Tasa de vencimiento**: `(autorizaciones_vencidas / autorizaciones_creadas) * 100`
4. **Autorizaciones por vencer hoy**: Para priorizar recordatorios

### Consultas SQL Útiles
```sql
-- Autorizaciones por estado
SELECT estado, COUNT(*) as cantidad
FROM AUTORIZACION_PROCEDIMIENTO
GROUP BY estado;

-- Autorizaciones sin usar próximas a vencer
SELECT * FROM v_autorizaciones_activas
WHERE dias_restantes <= 2;

-- Histórico de cambios de una autorización
SELECT *
FROM AUTORIZACION_PROCEDIMIENTO_AUDITORIA
WHERE id_autorizacion = 123
ORDER BY fecha_modificacion DESC;
```

---

## 🔮 Futuras Mejoras Sugeridas

### Punto 2.2: Capacidad y Disponibilidad del Médico
- Integrar con sistema de horarios
- Verificar disponibilidad antes de asignar
- Mostrar carga de trabajo actual
- Sugerir médicos con disponibilidad inmediata

### Integraciones de Email/SMS
- Completar funciones `enviar_email_*` en `utils/notificaciones_autorizaciones.py`
- Integrar con servicio de envío de SMS
- Templates HTML para emails

### Dashboard de Autorizaciones
- Panel para administradores con métricas en tiempo real
- Gráficos de uso y vencimiento
- Alertas de autorizaciones por vencer
- Reporte mensual automatizado

---

## 📞 Soporte

Para dudas o problemas con la implementación, contactar al equipo de desarrollo.

**Última actualización**: 18 de Noviembre de 2025
