# 📬 Sistema de Notificaciones Mejorado

## 🎯 Flujo de Notificaciones por Evento

### 1️⃣ **Al Crear una Reserva**
Se generan **3 notificaciones**:

#### a) Notificación Inmediata de Creación
- **Tipo**: `confirmacion`
- **Título**: "Reserva Generada"
- **Mensaje**: "Su reserva ha sido generada exitosamente"
- **Cuándo se muestra**: Inmediatamente (aparece en el dropdown)
- **Badge**: ✅ Suma al contador

#### b) Notificación Inmediata de Estado
- **Tipo**: `estado`
- **Título**: "Estado de Reserva"
- **Mensaje**: Según el estado en BD:
  - `Pendiente` → "Su reserva está pendiente de confirmación"
  - `Confirmada` → "Su reserva ha sido confirmada"
  - `Cancelada` → "Su reserva ha sido cancelada"
  - `Completada` → "Su reserva ha sido completada"
- **Cuándo se muestra**: Inmediatamente (aparece en el dropdown)
- **Badge**: ✅ Suma al contador

#### c) Recordatorio de Cita
- **Tipo**: `recordatorio`
- **Título**: "Recordatorio de Cita"
- **Mensaje**: "Tiene una cita programada para el {fecha} a las {hora}"
- **Cuándo se muestra**: Solo cuando `fecha_envio <= HOY` (dentro de 24 horas)
- **Badge**: ✅ Suma al contador (solo si está dentro de las 24h)

---

### 2️⃣ **Al Reprogramar una Reserva**
Se generan **3 notificaciones**:

#### a) Notificación Inmediata de Reprogramación
- **Tipo**: `reprogramacion`
- **Título**: "Reserva Reprogramada"
- **Mensaje**: "Su reserva fue reprogramada para {fecha} a las {hora}"
- **Cuándo se muestra**: Inmediatamente
- **Badge**: ✅ Suma al contador

#### b) Notificación Actualizada de Estado
- **Tipo**: `estado`
- **Título**: "Estado de Reserva"
- **Mensaje**: Estado actual de la reserva reprogramada
- **Cuándo se muestra**: Inmediatamente
- **Badge**: ✅ Suma al contador

#### c) Nuevo Recordatorio
- **Tipo**: `recordatorio`
- **Título**: "Recordatorio de Cita"
- **Mensaje**: Recordatorio para la nueva fecha/hora
- **Cuándo se muestra**: Solo dentro de las 24 horas previas
- **Badge**: ✅ Suma (solo si está dentro de las 24h)

---

### 3️⃣ **Al Cambiar Contraseña** (Solo Pacientes)
Se genera **1 notificación**:

#### Notificación de Seguridad
- **Tipo**: `seguridad`
- **Título**: "Cambio de Contraseña"
- **Mensaje**: "Su contraseña ha sido cambiada exitosamente"
- **Cuándo se muestra**: Inmediatamente
- **Badge**: ✅ Suma al contador

---

## 🎨 Estados Visuales en el Frontend

### Badge (Contador Rojo)
- **Muestra**: Solo notificaciones NO LEÍDAS
- **Cuenta**:
  - ✅ Notificaciones inmediatas (confirmación, estado, reprogramación, seguridad)
  - ✅ Recordatorios cuya `fecha_envio <= HOY`
  - ❌ Notificaciones ya marcadas como leídas
  - ❌ Recordatorios futuros (fecha > hoy)

### Dropdown de Notificaciones

#### Notificaciones NO LEÍDAS
- 🎨 **Fondo**: Cyan claro (`bg-cyan-50`)
- 🔵 **Punto**: Azul (`bg-cyan-500`)
- ✅ **Botón Check**: Visible
- 👆 **Click**: Marca como leída automáticamente

#### Notificaciones LEÍDAS
- ⚪ **Fondo**: Blanco con opacidad (`opacity-60`)
- ⚫ **Punto**: Gris (`bg-gray-300`)
- ❌ **Botón Check**: Oculto
- 👆 **Click**: No tiene efecto

---

## 🔄 Ciclo de Vida de las Notificaciones

```
┌─────────────────────────────────────────────────────────────┐
│ 1. EVENTO (Crear/Reprogramar Reserva o Cambiar Contraseña) │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. BACKEND: Inserta notificaciones en BD                    │
│    - Notificaciones inmediatas: fecha_envio = HOY           │
│    - Recordatorios: fecha_envio = FECHA_CITA                │
│    - Todas con leida = FALSE                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. API /notificaciones/api/recientes                        │
│    - Filtra: tipo != 'recordatorio' OR fecha_envio <= HOY   │
│    - Devuelve JSON con campo 'leida'                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FRONTEND: cargarBovedaNotificaciones()                   │
│    - Cuenta no leídas → actualiza badge                     │
│    - Renderiza todas en dropdown (con estilos diferentes)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. USUARIO: Click en notificación                           │
│    - Frontend llama POST /api/marcar-leida/{id}             │
│    - Backend: UPDATE NOTIFICACION SET leida=TRUE            │
│    - Frontend recarga y actualiza badge/dropdown            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Paciente crea reserva para mañana
**Resultado inmediato en el dropdown**:
1. 🔵 "Reserva Generada - Su reserva ha sido generada exitosamente"
2. 🔵 "Estado de Reserva - Su reserva está pendiente de confirmación"

**Badge**: Muestra `2`

**Mañana (dentro de 24h)**:
3. 🔵 "Recordatorio de Cita - Tiene una cita programada para..."

**Badge**: Muestra `3` (si las otras 2 no se marcaron como leídas)

---

### Ejemplo 2: Paciente marca 1 notificación como leída
**Antes del click**:
- Badge: `3`
- Dropdown: 3 notificaciones con fondo cyan

**Después del click**:
- Badge: `2`
- Dropdown:
  - 1 notificación con fondo blanco opaco (leída)
  - 2 notificaciones con fondo cyan (no leídas)

---

## 🔧 Archivos Modificados

### Backend
1. `models/notificacion.py`
   - ✅ `crear_confirmacion_reserva()` - Título actualizado
   - ✅ `crear_notificacion_estado_reserva()` - **NUEVO**
   - ✅ `marcar_como_leida()` - **NUEVO**
   - ✅ `marcar_todas_como_leidas()` - **NUEVO**

2. `routes/notificaciones.py`
   - ✅ `api/recientes` - Devuelve campo `leida`
   - ✅ `POST api/marcar-leida/<id>` - **NUEVO**
   - ✅ `POST api/marcar-todas-leidas` - **NUEVO**

3. `routes/reservas.py`
   - ✅ `api_crear_reserva()` - Genera 3 notificaciones
   - ✅ `paciente_crear_reserva()` - Genera 3 notificaciones
   - ✅ `api_reprogramar_reserva()` - Genera 3 notificaciones

### Frontend
4. `templates/header.html`
   - ✅ `cargarBovedaNotificaciones()` - Cuenta solo no leídas
   - ✅ `marcarComoLeida()` - **NUEVO**
   - ✅ Renderizado diferenciado (leídas/no leídas)
   - ✅ Event listeners para marcar al hacer clic

### Base de Datos
5. Script SQL ejecutado:
   - ✅ Campo `leida` BOOLEAN DEFAULT FALSE
   - ✅ Campo `fecha_leida` DATETIME
   - ✅ Índice `idx_leida`

---

## 🧪 Cómo Probar

1. **Login como paciente**
2. **Crear una reserva** → Deberías ver badge con `2` (confirmación + estado)
3. **Abrir dropdown** → Ver 2 notificaciones con fondo cyan
4. **Click en una** → Badge baja a `1`, notificación se vuelve gris
5. **Recargar página** → Badge mantiene `1` (persistencia)
6. **Esperar a que la cita esté dentro de 24h** → Badge sube a `2` (aparece recordatorio)

---

## ✅ Ventajas del Sistema

1. **Claridad**: El paciente sabe exactamente qué pasó (reserva creada) y cuál es el estado
2. **Transparencia**: El estado de la reserva es visible inmediatamente
3. **Recordatorios oportunos**: Solo aparecen cuando son relevantes (24h antes)
4. **UX mejorada**: Las notificaciones leídas quedan visibles pero diferenciadas
5. **Sincronización**: Badge y dropdown siempre coherentes
6. **Persistencia**: Las notificaciones marcadas como leídas se mantienen tras recargar

---

## 🎯 Tipos de Notificación

| Tipo | Cuándo se genera | Cuándo aparece en dropdown |
|------|------------------|---------------------------|
| `confirmacion` | Al crear reserva | Inmediatamente |
| `estado` | Al crear/reprogramar reserva | Inmediatamente |
| `recordatorio` | Al crear/reprogramar reserva | Solo si fecha_envio <= HOY |
| `reprogramacion` | Al reprogramar reserva | Inmediatamente |
| `seguridad` | Al cambiar contraseña | Inmediatamente |
| `cancelacion` | Al cancelar reserva | Inmediatamente |

---

**🚀 Sistema implementado y funcionando correctamente**
