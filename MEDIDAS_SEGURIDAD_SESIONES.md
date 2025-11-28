# 🔒 MEDIDAS DE SEGURIDAD PARA SESIONES

## 📋 RESUMEN

Se han implementado medidas de seguridad robustas para proteger las sesiones de usuario y prevenir ataques por cookies guardadas o sesiones abandonadas.

---

## ✅ MEDIDAS IMPLEMENTADAS

### 1. **Timeout de Sesión Universal (10 minutos)**

**Aplicación**: TODOS los roles (pacientes, médicos, administradores, empleados)

**Funcionamiento**:
- Cada usuario tiene un timeout de **10 minutos de inactividad**
- El contador se reinicia con cada petición HTTP (Rolling Window)
- Si un usuario está inactivo por más de 10 minutos, su sesión se cierra automáticamente
- Previene que las cookies guardadas sean utilizadas por atacantes

**Archivos modificados**:
- `app.py`: Función `check_session_timeout()` (líneas 93-150)
- `routes/usuarios.py`: Inicialización de `last_activity` en `login()` y `api_login()`

### 2. **Configuración Segura de Cookies**

**Implementado en `app.py`**:

```python
# Cookies HttpOnly: Previene acceso desde JavaScript (XSS)
app.config['SESSION_COOKIE_HTTPONLY'] = True

# SameSite Lax: Protección contra CSRF
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Secure en producción: Solo transmisión por HTTPS
if os.getenv('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
```

**Beneficios**:
- **HttpOnly**: Previene que JavaScript malicioso acceda a las cookies
- **SameSite**: Previene ataques CSRF (Cross-Site Request Forgery)
- **Secure**: En producción, solo transmite cookies por HTTPS

### 3. **Limpieza Completa de Sesión**

Cuando el timeout expira:
- Se ejecuta `session.clear()` para eliminar TODOS los datos de sesión
- Se redirige al login con mensaje informativo
- No se mantiene ningún dato residual

---

## 🛡️ RECOMENDACIONES ADICIONALES

### **A. Autenticación de Dos Factores (2FA)**

**Descripción**: Requerir un código adicional (SMS, email, app autenticadora) además de la contraseña.

**Implementación sugerida**:
```python
# En routes/usuarios.py
@usuarios_bp.route('/login/2fa', methods=['POST'])
def verify_2fa():
    codigo = request.form.get('codigo_2fa')
    # Verificar código con servicio SMS/Email o TOTP
    # Si es válido, completar login
```

**Beneficios**:
- Protección incluso si la contraseña es comprometida
- Estándar de seguridad para aplicaciones médicas

---

### **B. Rate Limiting (Límite de Intentos de Login)**

**Descripción**: Bloquear IPs o usuarios después de X intentos fallidos de login.

**Implementación sugerida**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@usuarios_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Máximo 5 intentos por minuto
def login():
    # ... código de login
```

**Beneficios**:
- Previene fuerza bruta
- Protege contra ataques automatizados

---

### **C. Registro de Actividad de Sesiones (Auditoría)**

**Descripción**: Registrar todos los inicios de sesión, cierres y actividades sospechosas.

**Implementación sugerida**:
```python
# Crear tabla en BD
CREATE TABLE log_sesiones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    accion VARCHAR(50),  # 'login', 'logout', 'timeout', 'fallido'
    fecha_hora DATETIME,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario)
);

# En app.py o routes/usuarios.py
def registrar_actividad_sesion(usuario_id, accion, ip_address, user_agent):
    # Insertar en log_sesiones
    pass
```

**Beneficios**:
- Detección de accesos no autorizados
- Trazabilidad para auditorías
- Identificación de patrones sospechosos

---

### **D. Tokens CSRF**

**Descripción**: Generar tokens únicos para cada formulario y validarlos en el servidor.

**Implementación sugerida**:
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# En templates, agregar:
# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

**Beneficios**:
- Previene ataques CSRF
- Protege formularios críticos (cambios de datos, transacciones)

---

### **E. Validación de IP y User-Agent**

**Descripción**: Detectar cambios sospechosos en la IP o navegador durante una sesión.

**Implementación sugerida**:
```python
@app.before_request
def verificar_cambio_ip():
    if 'usuario_id' in session:
        ip_actual = request.remote_addr
        user_agent_actual = request.headers.get('User-Agent')
        
        ip_guardada = session.get('ip_address')
        user_agent_guardado = session.get('user_agent')
        
        if ip_guardada and (ip_actual != ip_guardada or user_agent_actual != user_agent_guardado):
            # Cambio sospechoso: cerrar sesión
            session.clear()
            flash('Se detectó un cambio de dispositivo o red. Por seguridad, su sesión ha sido cerrada.', 'warning')
            return redirect(url_for('usuarios.login'))
```

**Beneficios**:
- Detecta sesiones robadas o compartidas
- Protección adicional contra ataques

---

### **F. Encriptación de Datos Sensibles en Sesión**

**Descripción**: No almacenar datos sensibles directamente en la sesión, o encriptarlos.

**Implementación sugerida**:
```python
from cryptography.fernet import Fernet

# Generar clave una vez y guardarla en .env
key = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(key)

# Al guardar en sesión:
session['datos_sensibles'] = cipher.encrypt(datos_sensibles.encode()).decode()

# Al leer:
datos = cipher.decrypt(session['datos_sensibles'].encode()).decode()
```

**Beneficios**:
- Protege datos sensibles incluso si la sesión es comprometida
- Cumplimiento con regulaciones de privacidad (HIPAA, GDPR)

---

### **G. Notificaciones de Sesión**

**Descripción**: Enviar email/SMS cuando se detecte un login desde un dispositivo o IP nueva.

**Implementación sugerida**:
```python
def notificar_login_nuevo(usuario, ip_address, user_agent):
    if not session.get('dispositivo_verificado'):
        # Enviar email con código de verificación
        # O simplemente notificar al usuario
        enviar_email(
            usuario['correo'],
            'Nuevo inicio de sesión detectado',
            f'Se detectó un inicio de sesión desde {ip_address}'
        )
```

**Beneficios**:
- Usuario es notificado de accesos no autorizados
- Permite acción rápida si es un ataque

---

### **H. Sesiones Concurrentes Limitadas**

**Descripción**: Limitar el número de sesiones activas simultáneas por usuario.

**Implementación sugerida**:
```python
# Almacenar sesiones activas en Redis o BD
def verificar_sesiones_concurrentes(usuario_id, max_sesiones=3):
    sesiones_activas = obtener_sesiones_activas(usuario_id)
    if len(sesiones_activas) >= max_sesiones:
        # Cerrar la sesión más antigua
        cerrar_sesion_antigua(usuario_id)
```

**Beneficios**:
- Previene compartir credenciales
- Control de acceso más estricto

---

## 📊 COMPARATIVA DE MEDIDAS

| Medida | Complejidad | Impacto Seguridad | Prioridad |
|--------|-------------|-------------------|-----------|
| ✅ Timeout 10 min | Baja | Alto | ✅ Implementado |
| ✅ Cookies seguras | Baja | Medio | ✅ Implementado |
| Rate Limiting | Media | Alto | 🔴 Alta |
| 2FA | Alta | Muy Alto | 🟡 Media |
| Auditoría | Media | Medio | 🟡 Media |
| Tokens CSRF | Baja | Alto | 🔴 Alta |
| Validación IP/UA | Media | Medio | 🟢 Baja |
| Encriptación sesión | Alta | Alto | 🟡 Media |
| Notificaciones | Media | Medio | 🟢 Baja |
| Sesiones concurrentes | Alta | Medio | 🟢 Baja |

---

## 🚀 PLAN DE IMPLEMENTACIÓN RECOMENDADO

### **Fase 1 (Inmediato - Ya implementado)**
- ✅ Timeout de 10 minutos para todos los roles
- ✅ Configuración segura de cookies

### **Fase 2 (Corto plazo - 1-2 semanas)**
1. **Rate Limiting**: Implementar límite de intentos de login
2. **Tokens CSRF**: Proteger formularios críticos

### **Fase 3 (Mediano plazo - 1 mes)**
3. **Auditoría**: Sistema de logs de sesiones
4. **Validación IP/User-Agent**: Detección de cambios sospechosos

### **Fase 4 (Largo plazo - 2-3 meses)**
5. **2FA**: Autenticación de dos factores
6. **Notificaciones**: Alertas de logins nuevos

---

## 📝 NOTAS IMPORTANTES

### **Consideraciones de Usabilidad**
- El timeout de 10 minutos puede ser molesto para usuarios que trabajan con formularios largos
- **Solución**: Considerar extender el timeout a 15 minutos para roles administrativos si es necesario
- **Alternativa**: Implementar "recordar actividad" con JavaScript que envíe peticiones periódicas

### **Compatibilidad**
- `SESSION_COOKIE_SAMESITE='Lax'` es compatible con la mayoría de navegadores modernos
- `SESSION_COOKIE_SECURE=True` requiere HTTPS en producción

### **Rendimiento**
- El timeout se verifica en cada petición, pero es muy ligero (solo lectura de sesión)
- No impacta significativamente el rendimiento

---

## 🔍 MONITOREO Y MANTENIMIENTO

### **Métricas a Monitorear**:
1. Número de timeouts por día
2. Intentos de login fallidos
3. Cambios de IP durante sesiones
4. Sesiones concurrentes por usuario

### **Alertas Recomendadas**:
- Más de 10 intentos de login fallidos desde una IP en 5 minutos
- Más de 5 sesiones concurrentes para un usuario
- Cambios de IP frecuentes en la misma sesión

---

## 📚 REFERENCIAS

- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [HIPAA Security Requirements](https://www.hhs.gov/hipaa/for-professionals/security/index.html)

---

**Última actualización**: 2024
**Versión**: 1.0

