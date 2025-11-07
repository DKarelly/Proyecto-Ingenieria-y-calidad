# 📧 Configuración de Envío de Emails para Notificaciones

## ✨ Funcionalidad Implementada

Ahora cada vez que se crea una notificación en el sistema, automáticamente se enviará un correo electrónico al paciente con un diseño profesional y adaptado al tipo de notificación.

## 🎯 Tipos de Notificaciones que Envían Email

1. **🔔 Recordatorio** - Recordatorios de citas programadas
2. **✅ Confirmación** - Confirmación de reservas generadas
3. **📋 Estado** - Actualizaciones del estado de reservas
4. **❌ Cancelación** - Notificación de cancelación de reservas
5. **ℹ️ Información** - Información general importante

## 🔧 Configuración Requerida

### Paso 1: Crear archivo .env

Si no existe, crea un archivo `.env` en la raíz del proyecto y copia el contenido de `.env.example`:

```bash
copy .env.example .env
```

### Paso 2: Configurar Gmail

Para usar Gmail como servidor SMTP, necesitas generar una **Contraseña de Aplicación**:

#### 📋 Pasos detallados:

1. **Ir a tu Cuenta de Google**
   - Accede a: https://myaccount.google.com/

2. **Activar Verificación en Dos Pasos**
   - Ve a: Seguridad → Verificación en dos pasos
   - Si no está activada, actívala primero

3. **Generar Contraseña de Aplicación**
   - Ve a: Seguridad → Contraseñas de aplicaciones
   - Selecciona "Correo" como la aplicación
   - Selecciona "Otro" como dispositivo y escribe "Sistema Clínica"
   - Haz clic en "Generar"

4. **Copiar la Contraseña**
   - Google te mostrará una contraseña de 16 caracteres
   - Cópiala (sin espacios)

5. **Configurar en .env**
   ```env
   SMTP_EMAIL=clinicaunion.cix.1@gmail.com
   SMTP_PASSWORD=tu_contraseña_de_16_caracteres
   ```

### Paso 3: Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales:

```env
# Configuración del servidor SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Credenciales de email (IMPORTANTE: Configurar con tus datos)
SMTP_EMAIL=clinicaunion.cix.1@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Contraseña de aplicación de Gmail

# Nombre del remitente
SMTP_SENDER_NAME=Clínica Unión
```

⚠️ **IMPORTANTE**: 
- NO uses tu contraseña normal de Gmail
- Debes usar una "Contraseña de Aplicación" generada específicamente
- Esta contraseña es diferente para cada aplicación

## 🧪 Probar la Configuración

### Prueba Simple de Envío

```bash
python test_notificacion_email.py
```

Selecciona la opción 2 para hacer una prueba simple:
- Ingresa tu email
- Ingresa tu nombre
- Se enviará un correo de prueba

### Prueba Completa por Tipo

Selecciona la opción 1 para probar diferentes tipos de notificaciones:
- Elige el tipo de notificación (1-5)
- Se enviará un email con el diseño correspondiente

## 🎨 Diseño de Emails

Los emails incluyen:
- ✅ Diseño responsive (se adapta a móviles y desktop)
- ✅ Header con color según tipo de notificación
- ✅ Emoji identificador del tipo
- ✅ Contenido personalizado con nombre del paciente
- ✅ Formato HTML profesional
- ✅ Fallback a texto plano si no se soporta HTML
- ✅ Footer con información y fecha de envío

### Colores por Tipo:
- 🔔 Recordatorio: Naranja (#FFA500)
- ✅ Confirmación: Verde (#22C55E)
- 📋 Estado: Azul (#3B82F6)
- ❌ Cancelación: Rojo (#EF4444)
- ℹ️ Información: Índigo (#6366F1)

## 🚀 Uso Automático

Una vez configurado, el sistema enviará emails automáticamente cuando:

1. **Se crea una reserva** → Email de confirmación
2. **Se cambia el estado de una reserva** → Email de actualización de estado
3. **Se programa un recordatorio** → Email de recordatorio en la fecha/hora especificada
4. **Se cancela una reserva** → Email de cancelación

### Ejemplo en Código:

```python
from models.notificacion import Notificacion

# Crear una notificación (automáticamente envía email)
resultado = Notificacion.crear(
    titulo="Reserva Confirmada",
    mensaje="Su reserva ha sido confirmada para el 15/11/2025 a las 14:00",
    tipo="confirmacion",
    id_paciente=1,
    id_reserva=5
)

# El resultado incluye información sobre el envío del email
print(resultado)
# {
#     'success': True,
#     'id_notificacion': 123,
#     'email_enviado': True,
#     'email_mensaje': 'Email enviado exitosamente a paciente@email.com'
# }
```

## 🔍 Verificar que Funciona

1. **Crear una notificación de prueba** desde el sistema
2. **Revisar la bandeja de entrada** del correo del paciente
3. **Verificar que no esté en spam** (puede tardar unos segundos)

## ❗ Solución de Problemas

### Email no se envía

1. **Verifica las credenciales**
   - Asegúrate de usar la contraseña de aplicación correcta
   - Verifica que SMTP_EMAIL esté correcto

2. **Revisa los logs**
   - El sistema muestra en consola si hay errores
   - Lee el mensaje de error específico

3. **Problemas comunes**
   - "Authentication failed" → Contraseña incorrecta
   - "Connection timeout" → Problema de red/firewall
   - "Invalid email" → Email del paciente incorrecto

### Email llega a spam

- Gmail puede marcar los primeros emails como spam
- Pide al usuario que marque como "No es spam"
- Después de algunos envíos, Gmail aprenderá

## 📊 Información Técnica

### Archivos Creados/Modificados:

1. **`utils/email_service.py`** (NUEVO)
   - Servicio de envío de emails
   - Maneja conexión SMTP
   - Genera HTML de notificaciones

2. **`models/notificacion.py`** (MODIFICADO)
   - Ahora envía email automáticamente al crear notificación
   - Retorna información sobre el envío

3. **`test_notificacion_email.py`** (NUEVO)
   - Script de prueba para emails
   - Verifica configuración

4. **`.env.example`** (NUEVO)
   - Plantilla de configuración
   - Instrucciones de uso

### Dependencias Requeridas:

Todas las librerías necesarias ya están incluidas en Python:
- `smtplib` - Cliente SMTP
- `email.mime` - Construcción de mensajes
- `python-dotenv` - Variables de entorno

## 🎯 Próximos Pasos

1. ✅ Configurar el archivo `.env` con tus credenciales
2. ✅ Ejecutar `test_notificacion_email.py` para probar
3. ✅ Verificar que recibes el email de prueba
4. ✅ Comenzar a usar el sistema normalmente

---

**¡Listo!** Ahora cada notificación que se registre en el sistema también se enviará automáticamente por correo electrónico con un diseño profesional. 📧✨
