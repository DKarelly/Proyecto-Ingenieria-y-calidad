# 🔒 IMPLEMENTACIÓN: RATE LIMITING Y SEGURIDAD DE LOGIN

## 📋 RESUMEN

Se ha implementado un sistema robusto de **rate limiting** y **prevención de ataques de fuerza bruta** para el sistema de login, con las siguientes características:

- ✅ **Máximo 5 intentos de login** por IP en 15 minutos
- ✅ **Bloqueo solo por IP** (no por correo) - permite que usuarios legítimos intenten múltiples correos
- ✅ **Mensajes genéricos de error** (no revelan si el correo o contraseña están incorrectos)
- ✅ **Bloqueo temporal** de 15 minutos después de 5 intentos fallidos desde la misma IP
- ✅ **Limpieza automática** de intentos cuando el login es exitoso
- ✅ **Registro de intentos fallidos** en base de datos para auditoría (incluye correo e IP)

---

## 📁 ARCHIVOS MODIFICADOS/CREADOS

### 1. **`requirements.txt`**
- ✅ Agregado `Flask-Limiter==3.5.0`

### 2. **`app.py`**
- ✅ Configurado `Flask-Limiter` con límites globales
- ✅ Rate limiting base: 200 peticiones/día, 50 peticiones/hora por IP

### 3. **`models/usuario.py`**
- ✅ Modificado método `Usuario.login()` para devolver mensajes genéricos
- ✅ Todos los errores ahora dicen "Credenciales incorrectas" (no revela si el correo existe o la contraseña está mal)

### 4. **`routes/usuarios.py`**
- ✅ Modificado `login()` para verificar bloqueos antes de intentar login
- ✅ Modificado `api_login()` para verificar bloqueos antes de intentar login
- ✅ Registro de intentos fallidos
- ✅ Limpieza de intentos cuando el login es exitoso

### 5. **`utils/security_helper.py`** (NUEVO)
- ✅ Clase `SecurityHelper` con todas las funciones de seguridad
- ✅ Verificación de bloqueos solo por IP (no por correo)
- ✅ Registro de intentos fallidos (con correo e IP para auditoría)
- ✅ Limpieza automática de intentos antiguos
- ✅ Creación automática de tabla si no existe

### 6. **`scripts/crear_tabla_intentos_login.sql`** (NUEVO)
- ✅ Script SQL para crear la tabla de intentos fallidos

---

## 🔧 CÓMO FUNCIONA

### **1. Flujo de Login con Rate Limiting**

```
┌─────────────────┐
│ Usuario intenta │
│ iniciar sesión  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Verificar bloqueo por   │
│ correo e IP             │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
Bloqueado  No bloqueado
    │         │
    │         ▼
    │    ┌──────────────────┐
    │    │ Intentar login    │
    │    └────────┬──────────┘
    │             │
    │        ┌────┴────┐
    │        │        │
    │        ▼        ▼
    │    Exitoso   Fallido
    │        │        │
    │        │        ▼
    │        │    ┌──────────────────────┐
    │        │    │ Registrar intento   │
    │        │    │ fallido              │
    │        │    └──────────┬───────────┘
    │        │               │
    │        │               ▼
    │        │    ┌──────────────────────┐
    │        │    │ ¿5 intentos?        │
    │        │    └──────────┬──────────┘
    │        │               │
    │        │          ┌────┴────┐
    │        │          │        │
    │        │          ▼        ▼
    │        │      Bloquear  Continuar
    │        │          │        │
    │        │          └────┬───┘
    │        │               │
    │        └───────────────┘
    │
    └─────────────────────────┘
```

### **2. Mensajes de Error Genéricos**

**ANTES** (Inseguro):
- ❌ "Usuario no encontrado" → Revela que el correo no existe
- ❌ "Contraseña incorrecta" → Revela que el correo existe pero la contraseña está mal
- ❌ "Usuario inactivo" → Revela información sobre el estado del usuario

**AHORA** (Seguro):
- ✅ "Credenciales incorrectas" → Mensaje genérico siempre
- ✅ No revela si el correo existe o no
- ✅ No revela si la contraseña está mal
- ✅ No revela el estado del usuario

### **3. Sistema de Bloqueo**

**Parámetros**:
- **Máximo intentos**: 5
- **Ventana de tiempo**: 15 minutos
- **Tiempo de bloqueo**: 15 minutos después del 5to intento

**Ejemplo**:
```
Tiempo 0:00  - Intento 1 fallido → Registrado
Tiempo 0:02  - Intento 2 fallido → Registrado
Tiempo 0:05  - Intento 3 fallido → Registrado
Tiempo 0:08  - Intento 4 fallido → Registrado
Tiempo 0:10  - Intento 5 fallido → Registrado + BLOQUEO ACTIVADO
Tiempo 0:25  - Intento bloqueado → "Demasiados intentos. Intente en 15 minutos"
Tiempo 0:26  - Bloqueo expirado → Puede intentar nuevamente
```

### **4. Limpieza Automática**

- ✅ Cuando un login es **exitoso**, se limpian todos los intentos fallidos de esa IP
- ✅ Los intentos antiguos (más de 1 hora) se limpian automáticamente
- ✅ Esto permite que usuarios legítimos puedan intentar nuevamente después de olvidar su contraseña
- ✅ Los intentos se registran con correo e IP para auditoría, pero el bloqueo solo se aplica por IP

---

## 🛡️ CARACTERÍSTICAS DE SEGURIDAD

### **1. Bloqueo por IP**
- Bloqueo solo por **IP**: Previene ataques de fuerza bruta desde una IP específica
- **No bloquea por correo**: Permite que usuarios legítimos intenten múltiples correos si olvidan su contraseña
- Los intentos se registran con correo e IP para auditoría, pero el bloqueo solo se aplica por IP

### **2. Ventana Deslizante**
- Los intentos se cuentan por IP en una ventana de 15 minutos
- Si pasan 15 minutos sin intentos desde una IP, el contador se reinicia
- Esto evita bloqueos permanentes
- Un usuario puede intentar diferentes correos desde la misma IP sin ser bloqueado (hasta 5 intentos totales)

### **3. Resistente a Fallos**
- Si la tabla no existe, se crea automáticamente
- Si hay errores de base de datos, el sistema permite el intento (fail-open)
- No bloquea el acceso legítimo por errores técnicos

### **4. Auditoría**
- Todos los intentos fallidos se registran con:
  - Correo intentado
  - IP del cliente
  - Fecha y hora
  - Razón (siempre genérica)

---

## 📊 ESTRUCTURA DE BASE DE DATOS

### **Tabla: `intentos_login_fallidos`**

```sql
CREATE TABLE intentos_login_fallidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    razon VARCHAR(255) DEFAULT 'Credenciales incorrectas',
    fecha_intento DATETIME NOT NULL,
    INDEX idx_correo (correo),
    INDEX idx_ip (ip_address),
    INDEX idx_fecha (fecha_intento)
);
```

**Índices**:
- `idx_correo`: Para búsquedas rápidas por correo
- `idx_ip`: Para búsquedas rápidas por IP
- `idx_fecha`: Para limpieza eficiente de registros antiguos

---

## 🚀 USO

### **Para Desarrolladores**

El sistema funciona automáticamente. No se requiere configuración adicional.

**Ejemplo de uso en código**:
```python
from utils.security_helper import SecurityHelper

# Obtener IP del cliente
ip_address = SecurityHelper.obtener_ip_cliente()

# Verificar bloqueo antes de login (solo por IP)
bloqueo = SecurityHelper.verificar_bloqueo(ip_address=ip_address)
if bloqueo['bloqueado']:
    return {'error': bloqueo['mensaje']}

# Registrar intento fallido (se registra con correo e IP para auditoría)
SecurityHelper.registrar_intento_fallido(correo, ip_address)

# Limpiar intentos cuando login es exitoso (solo por IP)
SecurityHelper.limpiar_intentos_exitoso(ip_address)
```

### **Para Administradores**

**Ver intentos fallidos**:
```sql
SELECT * FROM intentos_login_fallidos 
WHERE fecha_intento >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
ORDER BY fecha_intento DESC;
```

**Limpiar intentos manualmente**:
```sql
DELETE FROM intentos_login_fallidos 
WHERE fecha_intento < DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

**Desbloquear una IP específica**:
```sql
DELETE FROM intentos_login_fallidos 
WHERE ip_address = '192.168.1.100';
```

**Ver intentos por IP**:
```sql
SELECT ip_address, COUNT(*) as intentos
FROM intentos_login_fallidos
WHERE fecha_intento >= DATE_SUB(NOW(), INTERVAL 15 MINUTE)
GROUP BY ip_address
ORDER BY intentos DESC;
```

---

## ⚙️ CONFIGURACIÓN

### **Parámetros Ajustables en `utils/security_helper.py`**:

```python
MAX_INTENTOS = 5                    # Máximo de intentos permitidos
TIEMPO_BLOQUEO_MINUTOS = 15         # Tiempo de bloqueo después de 5 intentos
TIEMPO_VENTANA_MINUTOS = 15         # Ventana de tiempo para contar intentos
```

### **Rate Limiting Global en `app.py`**:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],  # Límites globales
    storage_uri="memory://"  # En producción, usar Redis
)
```

---

## 🔍 MONITOREO

### **Métricas Recomendadas**:

1. **Intentos fallidos por hora**:
   ```sql
   SELECT COUNT(*) as intentos
   FROM intentos_login_fallidos
   WHERE fecha_intento >= DATE_SUB(NOW(), INTERVAL 1 HOUR);
   ```

2. **IPs más bloqueadas** (útil para identificar ataques):
   ```sql
   SELECT ip_address, COUNT(*) as intentos
   FROM intentos_login_fallidos
   WHERE fecha_intento >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
   GROUP BY ip_address
   HAVING intentos >= 5
   ORDER BY intentos DESC
   LIMIT 10;
   ```

3. **Correos más intentados** (para auditoría, no afecta bloqueo):
   ```sql
   SELECT correo, COUNT(*) as intentos
   FROM intentos_login_fallidos
   WHERE fecha_intento >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
   GROUP BY correo
   ORDER BY intentos DESC
   LIMIT 10;
   ```

---

## ⚠️ CONSIDERACIONES

### **1. Usuarios Legítimos Bloqueados**

Si un usuario legítimo es bloqueado por IP:
- Esperar 15 minutos para que expire el bloqueo
- O limpiar manualmente los intentos de esa IP en la base de datos:
  ```sql
  DELETE FROM intentos_login_fallidos WHERE ip_address = 'IP_DEL_USUARIO';
  ```
- Considerar implementar un sistema de recuperación de cuenta

### **2. IPs Compartidas**

Si múltiples usuarios comparten la misma IP (ej: oficina, red pública):
- El bloqueo por IP puede afectar a todos los usuarios de esa IP
- Considerar ajustar `TIEMPO_BLOQUEO_MINUTOS` si es necesario
- **Ventaja**: Un usuario puede intentar diferentes correos sin ser bloqueado individualmente
- **Desventaja**: Si una IP es bloqueada, todos los usuarios de esa IP quedan bloqueados temporalmente

### **3. Producción**

En producción:
- Considerar usar Redis para almacenar intentos (más rápido)
- Configurar alertas para múltiples bloqueos desde la misma IP
- Monitorear la tabla de intentos regularmente

---

## 📝 PRUEBAS

### **Prueba Manual**:

1. Intentar login con credenciales incorrectas 5 veces
2. Verificar que el 6to intento muestra mensaje de bloqueo
3. Esperar 15 minutos o limpiar la tabla
4. Verificar que se puede intentar nuevamente

### **Prueba de Mensajes Genéricos**:

1. Intentar login con correo que no existe → "Credenciales incorrectas"
2. Intentar login con correo correcto pero contraseña incorrecta → "Credenciales incorrectas"
3. Verificar que ambos mensajes son idénticos

---

## 🔗 REFERENCIAS

- [OWASP - Brute Force Attack](https://owasp.org/www-community/attacks/Brute_force_attack)
- [Flask-Limiter Documentation](https://flask-limiter.readthedocs.io/)
- [OWASP - Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Última actualización**: 2024
**Versión**: 1.0

