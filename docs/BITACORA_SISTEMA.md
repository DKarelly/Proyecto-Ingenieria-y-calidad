# 📋 SISTEMA DE BITÁCORA - DOCUMENTACIÓN

## 🎯 OBJETIVO

El sistema de bitácora registra todas las acciones importantes del sistema para:
- **Auditoría**: Trazabilidad completa de cambios
- **Seguridad**: Detección de actividades sospechosas
- **Cumplimiento**: Registro de acciones administrativas críticas
- **Análisis**: Identificación de patrones y problemas

---

## 📊 ESTRUCTURA DE LA TABLA

### **Tabla: `BITACORA_SISTEMA`**

La tabla principal almacena todos los eventos del sistema con la siguiente estructura:

#### **Campos Principales**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_bitacora` | INT | ID único del registro |
| `fecha_hora` | DATETIME | Fecha y hora del evento |
| `id_usuario_actor` | INT | ID del usuario que realiza la acción |
| `tipo_usuario_actor` | VARCHAR(20) | Tipo de usuario (paciente/empleado) |
| `id_empleado_actor` | INT | ID del empleado si es empleado |
| `nombre_actor` | VARCHAR(255) | Nombre completo del actor |
| `correo_actor` | VARCHAR(100) | Correo del actor |
| `id_usuario_afectado` | INT | ID del usuario afectado |
| `tipo_usuario_afectado` | VARCHAR(20) | Tipo de usuario afectado |
| `nombre_afectado` | VARCHAR(255) | Nombre del usuario afectado |
| `correo_afectado` | VARCHAR(100) | Correo del usuario afectado |
| `modulo` | VARCHAR(50) | Módulo del sistema |
| `accion` | VARCHAR(100) | Tipo de acción realizada |
| `tipo_evento` | VARCHAR(50) | Categoría del evento |
| `descripcion` | TEXT | Descripción detallada |
| `ip_address` | VARCHAR(45) | IP desde donde se realizó |
| `user_agent` | TEXT | Navegador/cliente |
| `endpoint` | VARCHAR(255) | Ruta accedida |
| `valores_anteriores` | JSON | Valores antes del cambio |
| `valores_nuevos` | JSON | Valores después del cambio |
| `cambios_detallados` | TEXT | Descripción de cambios |
| `resultado` | VARCHAR(20) | Exitoso/Fallido/Pendiente |
| `codigo_error` | VARCHAR(50) | Código de error |
| `mensaje_error` | TEXT | Mensaje de error |
| `metadata` | JSON | Información adicional |

---

## 🔄 EVENTOS REGISTRADOS AUTOMÁTICAMENTE

### **1. Creación de Usuarios**
- **Trigger**: `trg_bitacora_usuario_creado`
- **Cuándo**: Al insertar en tabla `USUARIO`
- **Datos registrados**: ID, correo, teléfono, estado, fecha

### **2. Modificación de Usuarios**
- **Trigger**: `trg_bitacora_usuario_modificado`
- **Cuándo**: Al actualizar correo, teléfono o estado en `USUARIO`
- **Datos registrados**: Valores anteriores y nuevos, cambios específicos

### **3. Cambio de Roles en Empleados**
- **Trigger**: `trg_bitacora_empleado_rol_cambiado`
- **Cuándo**: Al cambiar `id_rol` en tabla `EMPLEADO`
- **Datos registrados**: Rol anterior y nuevo

### **4. Creación de Empleados**
- **Trigger**: `trg_bitacora_empleado_creado`
- **Cuándo**: Al insertar en tabla `EMPLEADO`
- **Datos registrados**: ID empleado, usuario, rol, especialidad

### **5. Creación de Pacientes**
- **Trigger**: `trg_bitacora_paciente_creado`
- **Cuándo**: Al insertar en tabla `PACIENTE`
- **Datos registrados**: ID paciente, usuario, documento, nombres

---

## 📝 PROCEDIMIENTOS ALMACENADOS

### **1. `sp_registrar_intento_registro`**

Registra intentos de registro (exitosos o fallidos).

**Parámetros**:
- `p_correo`: Correo del usuario que intenta registrarse
- `p_ip_address`: IP del cliente
- `p_resultado`: 'Exitoso' o 'Fallido'
- `p_mensaje_error`: Mensaje de error si falló
- `p_metadata`: Información adicional en JSON

**Ejemplo de uso**:
```sql
CALL sp_registrar_intento_registro(
    'usuario@ejemplo.com',
    '192.168.1.100',
    'Fallido',
    'Correo ya existe',
    JSON_OBJECT('documento', '12345678')
);
```

### **2. `sp_registrar_cambio_contrasena`**

Registra cambios de contraseña (exitosos o fallidos).

**Parámetros**:
- `p_id_usuario`: ID del usuario que cambia la contraseña
- `p_id_usuario_actor`: ID del usuario que realiza la acción (puede ser el mismo)
- `p_ip_address`: IP del cliente
- `p_resultado`: 'Exitoso' o 'Fallido'
- `p_mensaje_error`: Mensaje de error si falló

**Ejemplo de uso**:
```sql
CALL sp_registrar_cambio_contrasena(
    123,
    123,
    '192.168.1.100',
    'Exitoso',
    NULL
);
```

### **3. `sp_registrar_cambio_rol_admin`**

Registra cambios de roles realizados por administradores.

**Parámetros**:
- `p_id_empleado`: ID del empleado afectado
- `p_id_admin`: ID del administrador que realiza el cambio
- `p_rol_anterior`: ID del rol anterior
- `p_rol_nuevo`: ID del rol nuevo
- `p_ip_address`: IP del administrador

**Ejemplo de uso**:
```sql
CALL sp_registrar_cambio_rol_admin(
    45,  -- ID empleado
    1,   -- ID admin
    2,   -- Rol anterior (Médico)
    1,   -- Rol nuevo (Administrador)
    '192.168.1.50'
);
```

### **4. `sp_registrar_accion_admin`**

Registra cualquier acción administrativa general.

**Parámetros**:
- `p_id_admin`: ID del administrador
- `p_modulo`: Módulo del sistema
- `p_accion`: Tipo de acción
- `p_tipo_evento`: Categoría del evento
- `p_descripcion`: Descripción detallada
- `p_id_usuario_afectado`: ID del usuario afectado (opcional)
- `p_ip_address`: IP del administrador
- `p_valores_anteriores`: Valores antes (JSON, opcional)
- `p_valores_nuevos`: Valores después (JSON, opcional)
- `p_resultado`: 'Exitoso' o 'Fallido'
- `p_metadata`: Información adicional (JSON, opcional)

**Ejemplo de uso**:
```sql
CALL sp_registrar_accion_admin(
    1,  -- ID admin
    'roles',
    'asignar_permisos',
    'administracion',
    'Permisos asignados al rol Médico',
    NULL,
    '192.168.1.50',
    NULL,
    JSON_OBJECT('permisos', JSON_ARRAY(1, 2, 3)),
    'Exitoso',
    NULL
);
```

---

## 🔍 VISTAS ÚTILES

### **1. `v_bitacora_seguridad`**

Muestra todas las acciones relacionadas con seguridad:
- Intentos de login
- Cambios de contraseña
- Bloqueos de cuenta
- Accesos no autorizados

**Uso**:
```sql
SELECT * FROM v_bitacora_seguridad 
WHERE fecha_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY fecha_hora DESC;
```

### **2. `v_bitacora_administracion`**

Muestra todas las acciones administrativas:
- Cambios de roles
- Modificaciones de usuarios
- Configuraciones del sistema

**Uso**:
```sql
SELECT * FROM v_bitacora_administracion 
WHERE nombre_actor = 'Juan Pérez'
ORDER BY fecha_hora DESC;
```

### **3. `v_bitacora_registros`**

Muestra todos los registros de usuarios:
- Registros exitosos
- Intentos de registro fallidos
- Creación de cuentas

**Uso**:
```sql
SELECT * FROM v_bitacora_registros 
WHERE resultado = 'Fallido'
ORDER BY fecha_hora DESC;
```

### **4. `v_bitacora_cambios_roles`**

Muestra todos los cambios de roles:
- Cambios realizados por admins
- Cambios automáticos del sistema

**Uso**:
```sql
SELECT * FROM v_bitacora_cambios_roles 
WHERE fecha_hora >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY fecha_hora DESC;
```

---

## 📊 CONSULTAS ÚTILES

### **Acciones de un usuario específico**
```sql
SELECT 
    fecha_hora,
    modulo,
    accion,
    descripcion,
    resultado
FROM BITACORA_SISTEMA
WHERE id_usuario_afectado = 123
ORDER BY fecha_hora DESC
LIMIT 50;
```

### **Acciones realizadas por un admin**
```sql
SELECT 
    fecha_hora,
    nombre_afectado,
    modulo,
    accion,
    descripcion
FROM BITACORA_SISTEMA
WHERE id_empleado_actor = 1
  AND tipo_evento = 'administracion'
ORDER BY fecha_hora DESC;
```

### **Intentos de registro fallidos**
```sql
SELECT 
    fecha_hora,
    correo_afectado,
    ip_address,
    mensaje_error
FROM BITACORA_SISTEMA
WHERE accion = 'intento_registro'
  AND resultado = 'Fallido'
ORDER BY fecha_hora DESC;
```

### **Cambios de roles en los últimos 30 días**
```sql
SELECT 
    fecha_hora,
    nombre_actor,
    nombre_afectado,
    cambios_detallados,
    ip_address
FROM BITACORA_SISTEMA
WHERE accion LIKE '%rol%'
  AND fecha_hora >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY fecha_hora DESC;
```

### **Actividad por IP sospechosa**
```sql
SELECT 
    fecha_hora,
    correo_afectado,
    accion,
    descripcion,
    resultado
FROM BITACORA_SISTEMA
WHERE ip_address = '192.168.1.100'
ORDER BY fecha_hora DESC;
```

### **Estadísticas de acciones por módulo**
```sql
SELECT 
    modulo,
    COUNT(*) as total_acciones,
    SUM(CASE WHEN resultado = 'Exitoso' THEN 1 ELSE 0 END) as exitosas,
    SUM(CASE WHEN resultado = 'Fallido' THEN 1 ELSE 0 END) as fallidas
FROM BITACORA_SISTEMA
WHERE fecha_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY modulo
ORDER BY total_acciones DESC;
```

---

## 🛡️ TIPOS DE EVENTOS

| Tipo | Descripción | Ejemplos |
|------|-------------|----------|
| `seguridad` | Acciones relacionadas con seguridad | Login, cambio de contraseña, bloqueos |
| `administracion` | Acciones administrativas | Cambios de roles, modificaciones de usuarios |
| `registro` | Registros de usuarios | Creación de cuentas, intentos de registro |
| `modificacion` | Modificaciones de datos | Cambios en perfiles, actualizaciones |
| `eliminacion` | Eliminaciones | Desactivación de usuarios, eliminación de datos |
| `consulta` | Consultas importantes | Accesos a información sensible |

---

## 📈 MANTENIMIENTO

### **Limpieza de registros antiguos**

Para mantener el rendimiento, se recomienda limpiar registros antiguos periódicamente:

```sql
-- Eliminar registros de más de 1 año
DELETE FROM BITACORA_SISTEMA 
WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- O crear una tabla de archivo para registros antiguos
CREATE TABLE BITACORA_SISTEMA_ARCHIVO LIKE BITACORA_SISTEMA;

-- Mover registros antiguos
INSERT INTO BITACORA_SISTEMA_ARCHIVO 
SELECT * FROM BITACORA_SISTEMA 
WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL 1 YEAR);

DELETE FROM BITACORA_SISTEMA 
WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### **Optimización de índices**

Los índices se crean automáticamente, pero puedes verificar su uso:

```sql
-- Ver uso de índices
SHOW INDEX FROM BITACORA_SISTEMA;

-- Analizar tabla
ANALYZE TABLE BITACORA_SISTEMA;
```

---

## ⚠️ CONSIDERACIONES IMPORTANTES

1. **Rendimiento**: La tabla puede crecer rápidamente. Considera:
   - Limpieza periódica de registros antiguos
   - Particionamiento por fecha
   - Archivo de registros antiguos

2. **Privacidad**: Los registros pueden contener información sensible:
   - Implementar políticas de retención
   - Encriptar datos sensibles si es necesario
   - Controlar acceso a la bitácora

3. **Integridad**: Los triggers se ejecutan automáticamente:
   - No deben fallar las transacciones principales
   - Manejar errores en triggers
   - Verificar que los triggers no afecten el rendimiento

---

## 🔗 INTEGRACIÓN CON CÓDIGO PYTHON

Para registrar acciones desde el código Python, puedes usar los procedimientos almacenados:

```python
from bd import obtener_conexion

def registrar_accion_admin(id_admin, modulo, accion, descripcion, ip_address):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('sp_registrar_accion_admin', (
                id_admin,
                modulo,
                accion,
                'administracion',
                descripcion,
                None,  # id_usuario_afectado
                ip_address,
                None,  # valores_anteriores
                None,  # valores_nuevos
                'Exitoso',
                None   # metadata
            ))
            conexion.commit()
    finally:
        conexion.close()
```

---

**Última actualización**: 2024
**Versión**: 1.0

