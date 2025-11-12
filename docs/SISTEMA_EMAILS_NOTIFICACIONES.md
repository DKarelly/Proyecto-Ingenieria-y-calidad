# 📧 Sistema de Notificaciones por Email

## Descripción General

El sistema ahora envía **notificaciones automáticas por correo electrónico** además de las notificaciones dentro de la aplicación. Los emails se envían con diseño profesional HTML responsivo.

---

## 🎯 Eventos que Disparan Emails

### 1. **Creación de Reserva**
**Cuándo**: Al crear una nueva reserva médica

**Destinatarios**:
- ✅ **Paciente**: Confirmación de reserva con todos los detalles
- ✅ **Médico**: Notificación de nueva cita asignada

**Contenido**:
- Número de reserva
- Fecha y hora
- Médico y especialidad
- Servicio/tipo de consulta
- Instrucciones (llegar 15 min antes)

---

### 2. **Cancelación de Reserva (Aprobada)**
**Cuándo**: Cuando el personal aprueba una solicitud de cancelación

**Destinatarios**:
- ✅ **Paciente**: Confirmación de cancelación con detalles de la cita cancelada
- ✅ **Médico**: Notificación de cita cancelada

**Contenido**:
- Detalles de la cita cancelada
- Motivo de cancelación
- Comentario del personal (opcional)

---

### 3. **Reprogramación de Reserva (Aprobada)**
**Cuándo**: Cuando el personal aprueba una solicitud de reprogramación

**Destinatarios**:
- ✅ **Paciente**: Comparación visual fecha antigua → fecha nueva
- ✅ **Médico**: Notificación de cambio de fecha

**Contenido**:
- Comparación lado a lado: fecha anterior vs nueva
- Detalles del médico y servicio
- Motivo de reprogramación
- Comentario del personal (opcional)

---

### 4. **Recordatorio 24 Horas Antes**
**Cuándo**: 24 horas antes de la cita (automático)

**Destinatario**: 
- ✅ **Paciente**

**Contenido**:
- "Cita Médica Mañana"
- Hora destacada en grande
- Recomendaciones: llegar 15 min antes, traer documento, etc.

---

### 5. **Recordatorio 2 Horas Antes**
**Cuándo**: 2 horas antes de la cita (automático)

**Destinatario**: 
- ✅ **Paciente**

**Contenido**:
- "Cita en 2 HORAS" (urgente)
- Hora destacada
- Recordatorio de puntualidad

---

## ⚙️ Configuración

### Archivo `.env`

El sistema utiliza Gmail SMTP. Asegúrate de tener configurado:

```env
# Configuración de Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=clinicaunion.cix.1@gmail.com
SMTP_PASSWORD=siag eyoc xzen gtzj
SMTP_SENDER_NAME=Clinica Union
```

**Importante**: Si usas Gmail, debes generar una **"Contraseña de aplicación"**:
1. Ve a tu cuenta de Google
2. Seguridad → Verificación en 2 pasos (actívala)
3. Contraseñas de aplicación → Genera una nueva
4. Usa esa contraseña en `SMTP_PASSWORD`

---

## 🔄 Recordatorios Automáticos

### Ejecución Manual

Para enviar recordatorios manualmente:

```powershell
python enviar_recordatorios_email.py
```

### Ejecución Automática (Recomendado)

#### En Windows (Task Scheduler)

1. Abre **Programador de Tareas**
2. Crear Tarea Básica
3. Nombre: "Recordatorios Email Clínica"
4. Desencadenador: **Diariamente**
5. Acción: Iniciar programa
   - Programa: `python.exe` (ruta completa)
   - Argumentos: `enviar_recordatorios_email.py`
   - Directorio: `C:\Users\jasso\Downloads\trabajo_calidad\Proyecto-Ingenieria-y-calidad`
6. Configurar para ejecutar **cada hora**

#### En Linux/Mac (Cron)

Edita crontab:
```bash
crontab -e
```

Agrega:
```bash
# Ejecutar cada hora
0 * * * * cd /ruta/proyecto && /usr/bin/python3 enviar_recordatorios_email.py >> logs/recordatorios.log 2>&1
```

---

## 📊 Logs y Monitoreo

### Logs en Consola del Servidor

Todos los envíos de email se registran en la consola:

```
📧✅ Email de confirmación enviado al paciente: paciente@example.com
📧✅ Email de notificación enviado al médico: medico@example.com
📧⚠️ No se pudo enviar email al paciente: Error de conexión
❌ Error enviando emails de confirmación: SMTPAuthenticationError
```

### Logs del Script de Recordatorios

Al ejecutar `enviar_recordatorios_email.py`:

```
============================================================
🔔 INICIANDO ENVÍO DE RECORDATORIOS 24H
============================================================
📅 Buscando citas para: 13/11/2025
📋 Citas encontradas: 5
  ✅ Recordatorio 24h enviado a: juan@example.com (Reserva #123)
  ✅ Recordatorio 24h enviado a: maria@example.com (Reserva #124)

📊 Resumen Recordatorios 24h:
   ✅ Enviados exitosamente: 5
   ❌ Errores: 0
```

---

## 🎨 Diseño de Emails

### Características

- ✅ **HTML Responsivo**: Se adapta a móviles y desktop
- ✅ **Diseño Profesional**: Colores corporativos cyan/azul
- ✅ **Iconos y Emojis**: Fácil identificación visual
- ✅ **Colores por Tipo**:
  - 🟢 Verde: Confirmaciones, aprobaciones
  - 🔴 Rojo: Cancelaciones
  - 🔵 Azul/Cyan: Información general
  - 🟡 Naranja: Recordatorios, advertencias

### Ejemplo Visual

```
┌─────────────────────────────────────┐
│   🏥 Clínica Unión                  │ ← Header colorido
├─────────────────────────────────────┤
│ Hola Juan Pérez,                    │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ ✅ Reserva Confirmada       │   │ ← Contenido
│ │                             │   │
│ │ 📅 Fecha: 14 Nov 2025      │   │
│ │ ⏰ Hora: 09:00 - 09:30     │   │
│ │ 👨‍⚕️ Dr. García Especialista │   │
│ └─────────────────────────────┘   │
│                                     │
│ [Ver en el Sistema]                 │ ← Botón CTA
├─────────────────────────────────────┤
│ Mensaje automático - No responder   │ ← Footer
└─────────────────────────────────────┘
```

---

## 🔍 Verificación de Funcionamiento

### 1. Crear una Reserva

1. Crea una reserva como paciente
2. Verifica en la consola del servidor:
   ```
   📧✅ Email de confirmación enviado al paciente: xxx@example.com
   📧✅ Email de notificación enviado al médico: yyy@example.com
   ```
3. Revisa el buzón del paciente y del médico

### 2. Cancelar una Reserva

1. Solicita cancelación como paciente
2. Aprueba como administrador
3. Verifica emails de cancelación enviados

### 3. Reprogramar una Reserva

1. Solicita reprogramación como paciente
2. Aprueba con nueva fecha como administrador
3. Verifica emails con comparación de fechas

### 4. Recordatorios Automáticos

1. Ejecuta manualmente:
   ```powershell
   python enviar_recordatorios_email.py
   ```
2. Verifica el output en consola
3. Revisa emails enviados

---

## 🛠️ Solución de Problemas

### Email no se envía

**Error: "Credenciales de email no configuradas"**
- Verifica que `.env` tenga `SMTP_EMAIL` y `SMTP_PASSWORD`
- Reinicia el servidor Flask

**Error: "SMTPAuthenticationError"**
- Gmail requiere **Contraseña de aplicación** (no tu contraseña normal)
- Activa verificación en 2 pasos en Google
- Genera contraseña de aplicación específica

**Error: "SMTPServerDisconnected"**
- Verifica `SMTP_SERVER=smtp.gmail.com` y `SMTP_PORT=587`
- Verifica conexión a internet
- Firewall puede estar bloqueando puerto 587

### Emails llegan a SPAM

- Agrega `clinicaunion.cix.1@gmail.com` a contactos
- Marca como "No es spam"
- Considera configurar **SPF/DKIM** en el dominio

### Recordatorios no se envían

- Verifica que la tarea programada esté activa
- Revisa que el path al script sea absoluto
- Verifica logs de ejecución
- Ejecuta manualmente para ver errores

---

## 📝 Personalización

### Cambiar Colores

Edita `utils/email_service.py`:

```python
def _get_color_tipo(self, tipo):
    colores = {
        'confirmacion': '#22C55E',  # Verde → Cambia aquí
        'cancelacion': '#EF4444',   # Rojo → Cambia aquí
        # ...
    }
```

### Cambiar Textos

Las funciones en `utils/email_service.py` tienen los templates HTML:
- `enviar_email_reserva_creada()`
- `enviar_email_cancelacion_aprobada()`
- `enviar_email_reprogramacion_aprobada()`
- `enviar_email_recordatorio_24h()`
- `enviar_email_recordatorio_2h()`

### Agregar Logo

Reemplaza `{emoji}` con:
```html
<img src="URL_DEL_LOGO" alt="Logo" style="height: 60px;">
```

---

## 📈 Estadísticas

### Emails por Evento

| Evento | Emails Enviados |
|--------|----------------|
| Crear reserva | 2 (paciente + médico) |
| Cancelar | 2 (paciente + médico) |
| Reprogramar | 2 (paciente + médico) |
| Recordatorio 24h | 1 (paciente) |
| Recordatorio 2h | 1 (paciente) |

**Total por reserva completa**: ~7 emails

---

## ✅ Checklist de Implementación

- [x] Servicio de email configurado (`email_service.py`)
- [x] Funciones especializadas por evento
- [x] Integración en creación de reservas
- [x] Integración en cancelaciones
- [x] Integración en reprogramaciones
- [x] Script de recordatorios automáticos
- [x] Diseño HTML profesional y responsivo
- [x] Logs detallados en consola
- [x] Manejo de errores robusto
- [x] Documentación completa

---

## 🎓 Mejoras Futuras (Opcionales)

1. **Base de datos de emails enviados**
   - Tabla `EMAIL_LOG` con historial
   - Estadísticas de tasa de apertura

2. **Plantillas editables**
   - Panel admin para editar templates
   - Variables dinámicas

3. **Email con adjuntos**
   - PDF con detalles de la cita
   - QR code para check-in

4. **Notificaciones SMS**
   - Integración con Twilio
   - SMS como backup

5. **Programación inteligente**
   - Enviar recordatorios basado en preferencias
   - No enviar si ya confirmó por otro canal

---

**Desarrollado por**: Sistema de Gestión Clínica Unión  
**Fecha**: Noviembre 2025  
**Versión**: 2.0
