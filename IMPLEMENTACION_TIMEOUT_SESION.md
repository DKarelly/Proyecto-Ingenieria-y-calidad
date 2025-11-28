# 🔒 IMPLEMENTACIÓN: TIMEOUT DE SESIÓN DIFERENCIADO POR ROL

## 📋 RESUMEN

Se ha implementado un sistema de **timeout de sesión diferenciado** que aplica una política de seguridad específica para pacientes en computadoras compartidas:

- **Pacientes**: Sesión expira automáticamente tras **15 minutos de inactividad**
- **Otros roles** (médicos, administradores, empleados): Sin restricción de timeout

---

## 📁 ARCHIVOS MODIFICADOS

### 1. `app.py`
**Ubicación**: Líneas 93-151

**Cambios realizados**:
- Importación de `datetime`, `timedelta` y `flash`
- Nuevo hook `@app.before_request` llamado `check_patient_session_timeout()`

### 2. `routes/usuarios.py`
**Ubicación**: 
- Líneas 66-69 (función `login`)
- Líneas 516-519 (función `api_login`)

**Cambios realizados**:
- Inicialización del timestamp `last_activity` cuando un paciente inicia sesión

---

## 🔧 CÓMO FUNCIONA EL "RELOJ DE INACTIVIDAD"

### **Mecanismo de Rolling Window**

El sistema utiliza un **"reloj de inactividad"** basado en el concepto de **Rolling Window** (ventana deslizante):

1. **Inicialización**: Cuando un paciente inicia sesión, se guarda un timestamp `last_activity` en la sesión con la fecha/hora actual.

2. **Actualización continua**: En cada petición HTTP que realiza el paciente, el sistema:
   - Verifica si ha pasado más de 15 minutos desde `last_activity`
   - Si NO ha pasado el tiempo límite: actualiza `last_activity` con la hora actual (reinicia el contador)
   - Si SÍ ha pasado: cierra la sesión automáticamente

3. **Ejemplo práctico**:
   ```
   Tiempo 0:00  - Paciente inicia sesión → last_activity = 0:00
   Tiempo 0:05  - Paciente hace clic → last_activity = 0:05 (reinicia contador)
   Tiempo 0:18  - Paciente hace clic → last_activity = 0:18 (reinicia contador)
   Tiempo 0:35  - Paciente inactivo → Sesión expira (35 - 18 = 17 minutos > 15)
   ```

### **Flujo de Verificación**

```
┌─────────────────────────────────────────┐
│  Petición HTTP del usuario             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  ¿Es archivo estático?                  │
│  ¿Es ruta de login/logout?              │
└──────────────┬──────────────────────────┘
               │ NO
               ▼
┌─────────────────────────────────────────┐
│  ¿Es usuario tipo 'paciente'?           │
└──────────────┬──────────────────────────┘
               │ SÍ
               ▼
┌─────────────────────────────────────────┐
│  ¿Existe 'last_activity' en sesión?    │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
       NO            SÍ
        │             │
        ▼             ▼
┌──────────────┐  ┌──────────────────────────┐
│ Inicializar  │  │ Calcular tiempo          │
│ timestamp    │  │ de inactividad           │
└──────────────┘  └──────────┬───────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              > 15 min          <= 15 min
                    │                 │
                    ▼                 ▼
         ┌──────────────────┐  ┌──────────────┐
         │ Cerrar sesión    │  │ Actualizar   │
         │ Redirigir login  │  │ timestamp    │
         └──────────────────┘  └──────────────┘
```

---

## 🛡️ CARACTERÍSTICAS DE SEGURIDAD

### **1. Resistente a Fallos**
- Si el timestamp no existe o está corrupto, se reinicializa automáticamente
- Manejo de excepciones para evitar que errores de parsing rompan la aplicación

### **2. Exclusivo para Pacientes**
- Solo se aplica cuando `session.get('tipo_usuario') == 'paciente'`
- Otros roles (empleados, médicos, etc.) no se ven afectados

### **3. No Interfiere con Configuración Global**
- **NO** modifica `PERMANENT_SESSION_LIFETIME` de Flask
- La lógica es independiente y solo afecta a pacientes

### **4. Exclusión de Rutas Críticas**
- No se aplica a rutas estáticas (`/static/`)
- No se aplica a login/logout para evitar bucles de redirección
- No se aplica a la ruta home (`/`)

---

## 📝 DETALLES TÉCNICOS

### **Almacenamiento del Timestamp**

El timestamp se guarda en la sesión de Flask como un string ISO:
```python
session['last_activity'] = datetime.now().isoformat()
# Ejemplo: "2024-01-15T14:30:45.123456"
```

### **Cálculo de Inactividad**

```python
last_activity = datetime.fromisoformat(session.get('last_activity'))
now = datetime.now()
inactivity_time = now - last_activity
timeout_duration = timedelta(minutes=15)

if inactivity_time > timeout_duration:
    # Cerrar sesión
```

### **Actualización del Timestamp (Rolling Window)**

Cada petición activa reinicia el contador:
```python
session['last_activity'] = datetime.now().isoformat()
```

Esto significa que si un paciente está navegando activamente, su sesión nunca expirará. Solo expira si está **inactivo** por 15 minutos consecutivos.

---

## 🧪 CASOS DE USO

### **Caso 1: Paciente Activo**
- Paciente inicia sesión a las 10:00
- Hace clic a las 10:05 → `last_activity` = 10:05
- Hace clic a las 10:12 → `last_activity` = 10:12
- Hace clic a las 10:20 → `last_activity` = 10:20
- **Resultado**: Sesión activa (siempre se renueva con actividad)

### **Caso 2: Paciente Inactivo**
- Paciente inicia sesión a las 10:00
- Última actividad a las 10:05 → `last_activity` = 10:05
- No hace nada hasta las 10:21
- **Resultado**: Sesión expira (16 minutos de inactividad > 15)

### **Caso 3: Médico (No Afectado)**
- Médico inicia sesión a las 10:00
- No hace nada hasta las 12:00
- **Resultado**: Sesión sigue activa (no aplica timeout)

---

## 🔍 VERIFICACIÓN

### **Cómo Probar**

1. **Iniciar sesión como paciente**
2. **Esperar 15 minutos sin hacer ninguna acción**
3. **Intentar hacer clic en cualquier enlace**
4. **Resultado esperado**: Redirección al login con mensaje "Su sesión ha expirado por seguridad"

### **Logs de Debugging**

Si necesitas verificar el funcionamiento, puedes agregar logs temporales:

```python
print(f"[TIMEOUT] Usuario: {session.get('tipo_usuario')}, "
      f"Última actividad: {last_activity_str}, "
      f"Inactividad: {inactivity_time}")
```

---

## ⚠️ NOTAS IMPORTANTES

1. **El timeout es de INACTIVIDAD, no de duración total**: Si el paciente está navegando activamente, su sesión nunca expirará.

2. **No afecta a otros roles**: Médicos, administradores y empleados mantienen su sesión sin restricciones.

3. **El logout manual siempre funciona**: `session.clear()` limpia todo, incluyendo el timestamp.

4. **Compatible con sesiones existentes**: Si un paciente ya tenía sesión antes de esta implementación, el sistema inicializa el timestamp en la primera petición.

---

## 📌 UBICACIONES DEL CÓDIGO

### **Hook de Verificación**
- **Archivo**: `app.py`
- **Líneas**: 93-151
- **Función**: `check_patient_session_timeout()`

### **Inicialización en Login**
- **Archivo**: `routes/usuarios.py`
- **Líneas**: 66-69 (login normal)
- **Líneas**: 516-519 (API login)

---

## ✅ ENTREGABLE COMPLETADO

1. ✅ Código modificado en `app.py` y `routes/usuarios.py`
2. ✅ Explicación del "reloj de inactividad" (Rolling Window)
3. ✅ Resistente a fallos
4. ✅ No afecta configuración global
5. ✅ Exclusivo para pacientes

---

**Implementado por**: Ingeniero de Backend Senior especializado en Seguridad
**Fecha**: 2024
**Versión**: 1.0

