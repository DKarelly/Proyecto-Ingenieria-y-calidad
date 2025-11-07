# 🎨 Guía de Colores y Estilos de Notificaciones

## 📊 Paleta de Colores por Tipo

### 1️⃣ **Confirmación** (Reserva Generada)
```
🎨 Color Principal: Verde (#10b981)
📦 Badge: bg-green-100 text-green-800
🔖 Label: "✓ Confirmación"
🎯 Icono: Check circle verde
💬 Uso: "Su reserva ha sido generada exitosamente"
```

### 2️⃣ **Estado de Reserva** (Dinámico según estado)

#### Estado: Pendiente
```
🎨 Color Principal: Ámbar (#f59e0b)
📦 Badge: bg-amber-100 text-amber-800
🔖 Label: "◐ Pendiente"
🎯 Icono: Info circle ámbar
💬 Uso: "Su reserva está pendiente de confirmación"
```

#### Estado: Confirmada
```
🎨 Color Principal: Azul (#3b82f6)
📦 Badge: bg-blue-100 text-blue-800
🔖 Label: "● Confirmada"
🎯 Icono: Info circle azul
💬 Uso: "Su reserva ha sido confirmada"
```

#### Estado: Cancelada
```
🎨 Color Principal: Rojo (#ef4444)
📦 Badge: bg-red-100 text-red-800
🔖 Label: "✕ Cancelada"
🎯 Icono: Info circle rojo
💬 Uso: "Su reserva ha sido cancelada"
```

### 3️⃣ **Recordatorio**
```
🎨 Color Principal: Púrpura (#8b5cf6)
📦 Badge: bg-purple-100 text-purple-800
🔖 Label: "🔔 Recordatorio"
🎯 Icono: Bell púrpura
💬 Uso: "Tiene una cita programada para..."
```

### 4️⃣ **Reprogramación**
```
🎨 Color Principal: Cyan (#06b6d4)
📦 Badge: bg-cyan-100 text-cyan-800
🔖 Label: "↻ Reprogramación"
🎯 Icono: Refresh cyan
💬 Uso: "Su reserva fue reprogramada para..."
```

### 5️⃣ **Seguridad**
```
🎨 Color Principal: Rojo oscuro (#dc2626)
📦 Badge: bg-red-100 text-red-800
🔖 Label: "🔒 Seguridad"
🎯 Icono: Lock rojo
💬 Uso: "Su contraseña ha sido cambiada exitosamente"
```

### 6️⃣ **Cancelación**
```
🎨 Color Principal: Rojo (#ef4444)
📦 Badge: bg-red-100 text-red-800
🔖 Label: "✕ Cancelación"
🎯 Icono: X circle rojo
💬 Uso: "Su reserva ha sido cancelada"
```

---

## 🎯 Elementos de Diseño

### Estructura de Cada Notificación

```
┌─────────────────────────────────────────────────────────┐
│ ║ (Borde izquierdo coloreado - 4px)                     │
│ ║                                                        │
│ ║  [Icono]  [Badge Tipo] [●]                           │
│ ║            ↓            ↑                              │
│ ║         Confirmación   Punto animado (si no leída)    │
│ ║                                                        │
│ ║         Título en negrita                              │
│ ║         Mensaje descriptivo                            │
│ ║         ⏱ Hace X minutos                   [✓ Botón]  │
└─────────────────────────────────────────────────────────┘
```

### Estados Visuales

#### No Leída
- ✨ **Punto rojo animado** (pulse)
- 🎨 **Borde izquierdo coloreado** (según tipo)
- ✅ **Botón "marcar como leída"** visible
- 📦 **Badge de tipo** coloreado
- 🔆 **Opacidad**: 100%
- 🖱️ **Hover**: Escala 1.01

#### Leída
- ⚫ **Sin punto animado**
- 🎨 **Borde izquierdo coloreado** (mismo color, más tenue)
- ✅ **Icono de check** en lugar del botón
- 📦 **Badge de tipo** coloreado (mismo)
- 🌫️ **Opacidad**: 70%
- 🖱️ **Hover**: Escala 1.01

---

## 📱 Dropdown Mejorado

### Header
```
┌─────────────────────────────────────┐
│  Notificaciones                      │
└─────────────────────────────────────┘
```

### Body (con scroll si > 96px altura)
```
┌─────────────────────────────────────┐
│  ║ [●] ✓ Confirmación              │ ← No leída (más visible)
│  ║ [●] ◐ Pendiente                 │ ← No leída
│  ║ [✓] 🔔 Recordatorio             │ ← Leída (más tenue)
└─────────────────────────────────────┘
```

### Footer
```
┌─────────────────────────────────────┐
│  → Ver todas las notificaciones     │
└─────────────────────────────────────┘
```

### Estado Vacío
```
┌─────────────────────────────────────┐
│                                      │
│          [Icono campana grande]      │
│       No tienes notificaciones       │
│  Aquí aparecerán tus notificaciones  │
│           importantes                │
│                                      │
└─────────────────────────────────────┘
```

---

## 🔄 Ordenamiento

### Prioridad de Visualización
1. **No leídas primero** (CASE WHEN leida = FALSE THEN 0 ELSE 1 END)
2. **Más recientes primero** (ORDER BY fecha_envio DESC)
3. **Por hora descendente** (ORDER BY hora_envio DESC)

**Resultado**: Las 3 notificaciones nuevas aparecen JUNTAS al principio ✅

### Ejemplo Visual
```
Dropdown después de crear reserva:

┌─────────────────────────────────────────┐
│ No leídas (aparecen primero)            │
├─────────────────────────────────────────┤
│ ║ [●] ✓ Confirmación - Hace un momento  │ ← Nueva #1
│ ║ [●] ◐ Pendiente - Hace un momento     │ ← Nueva #2
│ ║ [●] 🔔 Recordatorio - Hace un momento │ ← Nueva #3 (solo si cita es hoy)
├─────────────────────────────────────────┤
│ Leídas (más abajo, con opacidad)       │
├─────────────────────────────────────────┤
│ ║ [✓] ↻ Reprogramación - Hace 2 horas  │
│ ║ [✓] ✓ Confirmación - Hace 1 día      │
└─────────────────────────────────────────┘
```

---

## 🎨 Paleta de Colores Completa

| Tipo | Color Borde | Color Badge BG | Color Badge Text | Color Icono |
|------|------------|----------------|------------------|-------------|
| Confirmación | `#10b981` | `bg-green-100` | `text-green-800` | `text-green-600` |
| Estado: Pendiente | `#f59e0b` | `bg-amber-100` | `text-amber-800` | `text-amber-600` |
| Estado: Confirmada | `#3b82f6` | `bg-blue-100` | `text-blue-800` | `text-blue-600` |
| Estado: Cancelada | `#ef4444` | `bg-red-100` | `text-red-800` | `text-red-600` |
| Recordatorio | `#8b5cf6` | `bg-purple-100` | `text-purple-800` | `text-purple-600` |
| Reprogramación | `#06b6d4` | `bg-cyan-100` | `text-cyan-800` | `text-cyan-600` |
| Seguridad | `#dc2626` | `bg-red-100` | `text-red-800` | `text-red-600` |
| Cancelación | `#ef4444` | `bg-red-100` | `text-red-800` | `text-red-600` |

---

## ✨ Animaciones y Efectos

### Punto Animado (No Leída)
```css
animate-pulse  /* Pulso constante en rojo */
```

### Hover en Notificación
```css
hover:scale-[1.01]  /* Escala suave al pasar el mouse */
transition-all duration-200  /* Transición suave */
```

### Botón Marcar Como Leída
```css
hover:bg-cyan-100  /* Fondo cyan al hover */
group-hover:text-cyan-700  /* Icono más oscuro al hover */
```

---

## 🧪 Ejemplos de Uso Real

### Escenario 1: Paciente crea reserva para mañana
```
Al crear:
┌─────────────────────────────────────────┐
│ ║ [●] ✓ Confirmación                    │ ← Verde
│ ║     Reserva Generada                   │
│ ║     Su reserva ha sido generada...     │
│ ║     ⏱ Hace un momento           [✓]   │
├─────────────────────────────────────────┤
│ ║ [●] ◐ Pendiente                       │ ← Ámbar
│ ║     Estado de Reserva                  │
│ ║     Su reserva está pendiente...       │
│ ║     ⏱ Hace un momento           [✓]   │
└─────────────────────────────────────────┘

Badge: 2
```

### Escenario 2: Mañana (24h antes de la cita)
```
┌─────────────────────────────────────────┐
│ ║ [●] 🔔 Recordatorio                   │ ← Púrpura
│ ║     Recordatorio de Cita               │
│ ║     Tiene una cita programada...       │
│ ║     ⏱ Hace un momento           [✓]   │
├─────────────────────────────────────────┤
│ ║ [●] ✓ Confirmación                    │ ← Verde
│ ║ [●] ◐ Pendiente                       │ ← Ámbar
└─────────────────────────────────────────┘

Badge: 3
```

### Escenario 3: Después de marcar confirmación como leída
```
┌─────────────────────────────────────────┐
│ ║ [●] 🔔 Recordatorio                   │ ← Púrpura
│ ║ [●] ◐ Pendiente                       │ ← Ámbar
├─────────────────────────────────────────┤
│ ║ [✓] ✓ Confirmación                    │ ← Verde (opacidad 70%)
└─────────────────────────────────────────┘

Badge: 2
```

---

## 🎯 Coherencia con el Diseño de la Página

### Colores Principales de la Clínica
- **Cyan**: `#06b6d4` (usado en botones principales)
- **Azul**: `#3b82f6` (usado en enlaces y highlights)

### Integración
- ✅ Los colores de las notificaciones complementan la paleta existente
- ✅ Verde para confirmaciones (positivo)
- ✅ Ámbar para pendientes (atención)
- ✅ Rojo para cancelaciones/seguridad (crítico)
- ✅ Púrpura para recordatorios (informativo)
- ✅ Cyan para reprogramaciones (acción)

### Tipografía
- **Títulos**: `font-semibold text-sm`
- **Mensajes**: `text-xs text-gray-600`
- **Fechas**: `text-xs text-gray-400`
- **Badges**: `text-xs font-medium`

---

## 📊 Resumen de Mejoras

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Colores** | Solo cyan genérico | 6 colores específicos por tipo |
| **Estado de reserva** | No diferenciado | 3 colores según estado |
| **Ordenamiento** | Por fecha | No leídas primero + fecha |
| **Iconos** | Solo punto | Icono específico por tipo |
| **Badges** | Sin badge | Badge coloreado con tipo |
| **Animación** | Ninguna | Pulse en no leídas + hover |
| **Opacidad** | Uniforme | 70% para leídas |
| **Borde** | Sin borde | Borde coloreado 4px |

---

**🎨 Diseño completamente renovado y coherente con la identidad de la clínica**
