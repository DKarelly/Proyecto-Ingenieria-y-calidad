# Sistema de Gestión de Roles y Permisos

Este documento describe la implementación del sistema de gestión de roles y permisos para la clínica.

## Archivos Creados/Modificados

### Nuevos Archivos

1. **`models/rol.py`** - Modelo para gestionar roles y permisos
   - Clase `Rol`: CRUD de roles y asignación de permisos
   - Clase `Permiso`: Gestión de permisos del sistema

2. **`scripts/crear_tablas_permisos.sql`** - Script SQL para crear estructura de base de datos
   - Agrega columna `descripcion` a tabla ROL
   - Crea tabla PERMISO
   - Crea tabla ROL_PERMISO (relación muchos a muchos)
   - Inserta 45 permisos predefinidos organizados por módulos
   - Asigna permisos iniciales a roles existentes

3. **`actualizar_bd_permisos.py`** - Script para ejecutar actualización de BD

### Archivos Modificados

1. **`routes/cuentas.py`**
   - Agregados 8 endpoints API REST para gestión de roles y permisos

2. **`templates/gestionarRolesPermisos.html`**
   - Conectado a base de datos mediante JavaScript
   - Tabla dinámica con carga de roles desde API
   - Modales funcionales para crear/editar roles
   - Modal para gestionar permisos por rol
   - Operaciones CRUD completas

## Estructura de Base de Datos

### Tabla ROL
```sql
CREATE TABLE `ROL` (
  `id_rol` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL,
  `descripcion` TEXT,              -- NUEVA COLUMNA
  `estado` VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY (`id_rol`)
)
```

### Tabla PERMISO (NUEVA)
```sql
CREATE TABLE `PERMISO` (
  `id_permiso` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `codigo` VARCHAR(50) NOT NULL,
  `descripcion` TEXT,
  `modulo` VARCHAR(50) NOT NULL,
  `estado` VARCHAR(20) DEFAULT 'Activo',
  PRIMARY KEY (`id_permiso`),
  UNIQUE KEY `codigo` (`codigo`)
)
```

### Tabla ROL_PERMISO (NUEVA)
```sql
CREATE TABLE `ROL_PERMISO` (
  `id_rol` INT NOT NULL,
  `id_permiso` INT NOT NULL,
  PRIMARY KEY (`id_rol`, `id_permiso`),
  FOREIGN KEY (`id_rol`) REFERENCES `ROL` (`id_rol`) ON DELETE CASCADE,
  FOREIGN KEY (`id_permiso`) REFERENCES `PERMISO` (`id_permiso`) ON DELETE CASCADE
)
```

## Permisos Predefinidos

Se incluyen 45 permisos organizados en 8 módulos:

### 1. Administración (7 permisos)
- Ver Panel Administración
- Gestionar Programación
- Gestionar Recursos Físicos
- Gestionar Horarios
- Gestionar Bloqueos
- Consultar Agenda Médica
- Gestionar Catálogo de Servicios

### 2. Reservas (6 permisos)
- Ver Panel Reservas
- Generar Reserva
- Consultar Disponibilidad
- Reprogramar Reserva
- Gestionar Cancelaciones
- Gestionar Confirmaciones

### 3. Cuentas (4 permisos)
- Ver Panel Cuentas
- Gestionar Cuentas Internas
- Gestionar Roles y Permisos
- Gestionar Datos Pacientes

### 4. Notificaciones (3 permisos)
- Ver Panel Notificaciones
- Gestionar Recordatorios
- Gestionar Notificaciones de Cambios

### 5. Seguridad (6 permisos)
- Ver Panel Seguridad
- Consultar Actividad
- Generar Incidencia
- Consultar Incidencia
- Asignar Responsable
- Generar Informe

### 6. Reportes (4 permisos)
- Ver Panel Reportes
- Consultar por Categoría
- Generar Reporte de Actividad
- Generar Ocupación de Recursos

### 7. Farmacia (3 permisos)
- Ver Panel Farmacia
- Gestionar Entrega Medicamentos
- Gestionar Recepción Medicamentos

### 8. Exámenes y Operaciones (4 permisos)
- Generar Examen
- Gestionar Exámenes
- Generar Operación
- Gestionar Operaciones

## Asignación Inicial de Permisos

### Administrador
- **Permisos**: TODOS (45 permisos)

### Médico
- Ver Panel Administración (solo consulta de agenda)
- Todos los permisos de Reservas
- Generar y gestionar exámenes
- Generar y gestionar operaciones
- Ver y generar reportes de actividad

### Recepcionista
- Gestionar reservas completo
- Gestionar datos de pacientes
- Gestionar recordatorios y notificaciones

### Farmacéutico
- Ver y gestionar farmacia completo
- Notificaciones

### Laboratorista
- Generar y gestionar exámenes
- Ver panel de notificaciones
- Ver panel de reportes

## Endpoints API

### Roles

#### GET `/cuentas/api/roles`
Obtener todos los roles con conteo de permisos

**Respuesta:**
```json
{
  "success": true,
  "roles": [
    {
      "id_rol": 1,
      "nombre": "Administrador",
      "descripcion": "Acceso total al sistema",
      "estado": "Activo",
      "total_permisos": 45
    }
  ]
}
```

#### POST `/cuentas/api/roles`
Crear nuevo rol

**Body:**
```json
{
  "nombre": "Nuevo Rol",
  "descripcion": "Descripción del rol"
}
```

#### PUT `/cuentas/api/roles/<id_rol>`
Actualizar rol existente

**Body:**
```json
{
  "nombre": "Rol Actualizado",
  "descripcion": "Nueva descripción",
  "estado": "Activo"
}
```

#### DELETE `/cuentas/api/roles/<id_rol>`
Eliminar rol (solo si no tiene empleados asignados)

### Permisos

#### GET `/cuentas/api/permisos`
Obtener todos los permisos agrupados por módulo

**Respuesta:**
```json
{
  "success": true,
  "permisos": {
    "Administración": [
      {
        "id_permiso": 1,
        "nombre": "Ver Panel Administración",
        "codigo": "admin.panel.ver",
        "descripcion": "Permite acceder al panel de administración",
        "modulo": "Administración"
      }
    ]
  }
}
```

#### GET `/cuentas/api/roles/<id_rol>/permisos`
Obtener IDs de permisos asignados a un rol

**Respuesta:**
```json
{
  "success": true,
  "permisos_ids": [1, 2, 3, 5, 8]
}
```

#### POST `/cuentas/api/roles/<id_rol>/permisos`
Asignar permisos a un rol (reemplaza los existentes)

**Body:**
```json
{
  "permisos": [1, 2, 3, 5, 8]
}
```

## Instalación

### 1. Ejecutar actualización de base de datos

```bash
python actualizar_bd_permisos.py
```

Este script:
- Agrega la columna `descripcion` a la tabla ROL
- Crea las tablas PERMISO y ROL_PERMISO
- Inserta los 45 permisos predefinidos
- Asigna permisos iniciales a los 5 roles existentes

### 2. Verificar instalación

Acceder a: `http://localhost:5000/cuentas/gestionar-roles-permisos`

Deberías ver:
- Tabla con 5 roles (Administrador, Médico, Recepcionista, Farmacéutico, Laboratorista)
- Botón "Crear Nuevo Rol" funcional
- Botón "Gestionar Permisos" funcional en cada rol
- Opciones para editar y eliminar roles

## Uso

### Crear un Nuevo Rol

1. Clic en botón "Crear Nuevo Rol"
2. Ingresar nombre y descripción
3. Clic en "Crear Rol"
4. El rol aparecerá en la tabla sin permisos asignados

### Editar un Rol

1. Clic en ícono de editar (lápiz) en la fila del rol
2. Modificar nombre y/o descripción
3. Clic en "Guardar Cambios"

### Asignar Permisos a un Rol

1. Clic en ícono de escudo azul en la fila del rol
2. Se abre modal con todos los permisos organizados por módulo
3. Seleccionar/deseleccionar checkboxes según necesidad
4. Clic en "Guardar Cambios"
5. El conteo de permisos se actualiza en la tabla

### Eliminar un Rol

1. Clic en ícono de eliminar (basura) en la fila del rol
2. Confirmar eliminación
3. **Nota**: No se puede eliminar un rol que tenga empleados asignados

## Modelo de Clases

### Clase Rol

```python
from models.rol import Rol

# Obtener todos los roles
roles = Rol.obtener_todos()

# Obtener rol por ID
rol = Rol.obtener_por_id(1)

# Crear rol
id_nuevo = Rol.crear("Enfermero", "Gestión de enfermería")

# Actualizar rol
Rol.actualizar(5, "Enfermero Senior", "Descripción actualizada", "Activo")

# Eliminar rol
exito, mensaje = Rol.eliminar(5)

# Obtener permisos de un rol
permisos = Rol.obtener_permisos(1)

# Asignar permisos a un rol
Rol.asignar_permisos(5, [1, 2, 3, 5, 8])
```

### Clase Permiso

```python
from models.rol import Permiso

# Obtener todos los permisos
permisos = Permiso.obtener_todos()

# Obtener permisos agrupados por módulo
permisos_agrupados = Permiso.obtener_por_modulo()

# Obtener IDs de permisos de un rol
ids = Permiso.obtener_ids_por_rol(1)
```

## Códigos de Permisos

Todos los permisos tienen un código único en formato `modulo.accion.tipo`:

Ejemplos:
- `admin.panel.ver` - Ver panel de administración
- `reservas.generar` - Generar nueva reserva
- `cuentas.roles.gestionar` - Gestionar roles y permisos
- `seguridad.incidencias.asignar` - Asignar responsable a incidencia

Estos códigos pueden usarse para verificar permisos programáticamente:

```python
# Verificar si un rol tiene un permiso específico
permisos = Rol.obtener_permisos(id_rol)
tiene_permiso = any(p['codigo'] == 'admin.panel.ver' for p in permisos)
```

## Consideraciones de Seguridad

1. **Validación de sesión**: Todos los endpoints verifican sesión activa
2. **Tipo de usuario**: Solo empleados pueden acceder a gestión de roles
3. **Integridad referencial**: Los permisos se eliminan automáticamente al eliminar un rol (CASCADE)
4. **Protección de eliminación**: No se pueden eliminar roles con empleados asignados
5. **Transacciones**: Todas las operaciones de escritura usan transacciones

## Próximos Pasos (Opcional)

1. Implementar verificación de permisos en cada endpoint
2. Agregar middleware para validar permisos automáticamente
3. Crear decorador `@requiere_permiso('codigo.permiso')`
4. Agregar auditoría de cambios en roles y permisos
5. Implementar caché de permisos para mejorar rendimiento

## Soporte

Para reportar problemas o sugerencias, contactar al equipo de desarrollo.
