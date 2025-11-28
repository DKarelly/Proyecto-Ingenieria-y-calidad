# 📚 DOCUMENTO DE ESTUDIO COMPLETO DEL PROYECTO
## Sistema de Gestión Médica - Guía de Navegación y Validaciones

---

## 📋 ÍNDICE

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Mapa de Rutas por Módulo](#mapa-de-rutas-por-módulo)
3. [Validaciones y Decoradores](#validaciones-y-decoradores)
4. [Guía de Navegación para Cambios](#guía-de-navegación-para-cambios)
5. [Validaciones Detalladas por Funcionalidad](#validaciones-detalladas-por-funcionalidad)
6. [Ejemplos Prácticos de Modificaciones](#ejemplos-prácticos-de-modificaciones)

---

## 🏗️ ESTRUCTURA DEL PROYECTO

```
Proyecto-Ingenieria-y-calidad/
├── app.py                    # Punto de entrada principal
├── bd.py                     # Gestión de conexiones DB
├── routes/                   # Blueprints (módulos de rutas)
│   ├── usuarios.py          # Autenticación y gestión de usuarios
│   ├── admin.py              # Panel de administración
│   ├── medico.py             # Panel médico
│   ├── recepcionista.py      # Panel recepcionista
│   ├── paciente.py          # Funcionalidades para pacientes
│   ├── reservas.py           # Gestión de reservas
│   ├── notificaciones.py     # Sistema de notificaciones
│   ├── farmacia.py           # Gestión de farmacia
│   ├── seguridad.py          # Seguridad e incidencias
│   ├── reportes.py           # Reportes y estadísticas
│   └── cuentas.py            # Gestión de cuentas
├── models/                   # Modelos de datos
│   ├── usuario.py
│   ├── paciente.py
│   ├── empleado.py
│   ├── reserva.py
│   ├── agenda.py
│   └── ...
├── templates/                # Plantillas HTML
└── utils/                    # Utilidades
    └── email_service.py
```

---

## 🗺️ MAPA DE RUTAS POR MÓDULO

### 📁 **MÓDULO: USUARIOS** (`routes/usuarios.py`)

#### **Rutas de Autenticación**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/usuarios/login` | GET, POST | Inicio de sesión | Campos requeridos, usuario activo | `routes/usuarios.py:29` |
| `/usuarios/logout` | GET | Cerrar sesión | Sesión activa | `routes/usuarios.py:91` |
| `/usuarios/recuperar-contrasena` | GET | Vista recuperación | - | `routes/usuarios.py:98` |
| `/usuarios/cambiar-contrasena` | GET, POST | Cambiar contraseña | Contraseña actual, nueva >= 8 chars, mayúsculas, minúsculas, números | `routes/usuarios.py:1171` |

#### **Rutas de Perfil**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/usuarios/perfil` | GET | Ver perfil | `@login_required` | `routes/usuarios.py:109` |
| `/usuarios/editar-perfil` | GET, POST | Editar perfil propio | Edad 18-100 años, no cambiar sexo | `routes/usuarios.py:338` |

#### **Rutas de Gestión (Solo Empleados)**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/usuarios/listar` | GET | Listar usuarios | `@login_required`, `@empleado_required` | `routes/usuarios.py:197` |
| `/usuarios/crear` | GET, POST | Crear usuario | Contraseña >= 6 chars, campos requeridos | `routes/usuarios.py:205` |
| `/usuarios/editar/<id>` | GET, POST | Editar usuario | `@empleado_required` | `routes/usuarios.py:277` |
| `/usuarios/eliminar/<id>` | POST | Desactivar usuario | `@empleado_required` | `routes/usuarios.py:448` |
| `/usuarios/gestion` | GET | Gestión unificada | `@empleado_required` | `routes/usuarios.py:1244` |

#### **APIs de Usuarios**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/usuarios/api/login` | POST | API login | JSON: correo, contrasena | `routes/usuarios.py:463` |
| `/usuarios/api/register` | POST | API registro | Unicidad: correo, teléfono, DNI | `routes/usuarios.py:568` |
| `/usuarios/api/session` | GET | Obtener sesión | Sesión activa | `routes/usuarios.py:523` |
| `/usuarios/api/usuarios` | GET | Listar usuarios | `@empleado_required` | `routes/usuarios.py:664` |
| `/usuarios/api/forgot-password` | POST | Recuperar contraseña | Código 6 dígitos, válido 15 min | `routes/usuarios.py:830` |
| `/usuarios/api/verify-code` | POST | Verificar código | Código no usado, vigente | `routes/usuarios.py:948` |
| `/usuarios/api/reset-password` | POST | Restablecer contraseña | Código válido, nueva >= 6 chars | `routes/usuarios.py:999` |
| `/usuarios/api/cambiar-contrasena` | POST | Cambiar contraseña | Contraseña actual correcta | `routes/usuarios.py:1127` |
| `/usuarios/api/departamentos` | GET | Listar departamentos | - | `routes/usuarios.py:702` |
| `/usuarios/api/provincias/<id>` | GET | Listar provincias | - | `routes/usuarios.py:716` |
| `/usuarios/api/distritos/<id>` | GET | Listar distritos | - | `routes/usuarios.py:733` |
| `/usuarios/api/send-email` | POST | Enviar email | SMTP configurado | `routes/usuarios.py:750` |
| `/usuarios/medicos` | GET | Lista de médicos | - | `routes/usuarios.py:1076` |

---

### 📁 **MÓDULO: ADMIN** (`routes/admin.py`)

#### **Rutas de Panel**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/admin/` | GET | Panel admin | `id_rol == 1` (Administrador) | `routes/admin.py:13` |
| `/admin/consultar-agenda-medica` | GET | Consultar agenda | `@empleado_required` | `routes/admin.py:35` |
| `/admin/consultar-incidencia` | GET | Consultar incidencias | `@empleado_required` | `routes/admin.py:46` |
| `/admin/gestionar-bloqueo-horarios` | GET | Bloqueo horarios | `@empleado_required` | `routes/admin.py:57` |
| `/admin/gestionar-catalogo-servicios` | GET | Catálogo servicios | `@empleado_required` | `routes/admin.py:68` |
| `/admin/gestionar-programacion` | GET | Gestión programación | `@empleado_required` | `routes/admin.py:79` |
| `/admin/gestionar-horarios-laborales` | GET | Horarios laborales | `@empleado_required` | `routes/admin.py:90` |
| `/admin/gestionar-recursos-fisicos` | GET | Recursos físicos | `@empleado_required` | `routes/admin.py:101` |

#### **APIs de Servicios**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/admin/api/servicios` | GET | Listar servicios | `@empleado_required` | `routes/admin.py:114` |
| `/admin/api/servicios` | POST | Crear servicio | Nombre, descripción, tipo requeridos | `routes/admin.py:188` |
| `/admin/api/servicios/<id>` | PUT | Actualizar servicio | `@empleado_required` | `routes/admin.py:210` |
| `/admin/api/servicios/<id>` | DELETE | Eliminar servicio | `@empleado_required` | `routes/admin.py:241` |
| `/admin/api/servicios/buscar` | POST | Buscar servicios | Filtros opcionales | `routes/admin.py:146` |

#### **APIs de Recursos**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/admin/api/recursos` | GET | Listar recursos | `@empleado_required` | `routes/admin.py:255` |
| `/admin/api/recursos` | POST | Crear recurso | Nombre, tipo requeridos | `routes/admin.py:299` |
| `/admin/api/recursos/<id>` | PUT | Actualizar recurso | `@empleado_required` | `routes/admin.py:319` |
| `/admin/api/recursos/<id>` | DELETE | Eliminar recurso | `@empleado_required` | `routes/admin.py:348` |

#### **APIs de Horarios**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/admin/api/horarios` | GET | Listar horarios | `@empleado_required` | `routes/admin.py:362` |
| `/admin/api/horarios` | POST | Crear horario | Fecha, hora_inicio, hora_fin requeridos | `routes/admin.py:432` |
| `/admin/api/horarios/<id>` | PUT | Actualizar horario | `@empleado_required` | `routes/admin.py:454` |
| `/admin/api/horarios/<id>` | DELETE | Desactivar horario | `@empleado_required` | `routes/admin.py:492` |
| `/admin/api/horarios/empleados/<id>` | GET | Horarios por empleado | `@empleado_required` | `routes/admin.py:735` |

#### **APIs de Programación**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/admin/api/programaciones` | GET | Listar programaciones | Filtros opcionales | `routes/admin.py:549` |
| `/admin/api/programaciones` | POST | Crear programación | Fecha, horas, servicio, horario requeridos | `routes/admin.py:645` |
| `/admin/api/programaciones/<id>` | PUT | Actualizar programación | `@empleado_required` | `routes/admin.py:668` |
| `/admin/api/programaciones/<id>` | DELETE | Eliminar programación | `@empleado_required` | `routes/admin.py:723` |

#### **APIs de Bloqueos**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/admin/api/bloqueos` | GET | Listar bloqueos | `@empleado_required` | `routes/admin.py:756` |
| `/admin/api/bloqueos` | POST | Crear bloqueo | Fecha, horas, motivo requeridos | `routes/admin.py:794` |
| `/admin/api/bloqueos/<id>` | PUT | Actualizar bloqueo | `@empleado_required` | `routes/admin.py:817` |
| `/admin/api/bloqueos/<id>` | DELETE | Eliminar bloqueo | `@empleado_required` | `routes/admin.py:864` |

---

### 📁 **MÓDULO: MÉDICO** (`routes/medico.py`)

#### **Rutas de Panel**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/medico/` | GET | Panel médico | `@medico_required` (id_rol == 2) | `routes/medico.py:648` |
| `/medico/dashboard` | GET | Dashboard médico | `@medico_required` | `routes/medico.py:783` |
| `/medico/agenda` | GET | Agenda médica | `@medico_required` | `routes/medico.py:806` |
| `/medico/pacientes` | GET | Lista pacientes | `@medico_required` | `routes/medico.py:824` |
| `/medico/historial_paciente/<id>` | GET | Historial paciente | `@medico_required` | `routes/medico.py:843` |
| `/medico/diagnosticos` | GET | Ver diagnósticos | `@medico_required` | `routes/medico.py:1040` |
| `/medico/diagnosticos/nuevo` | GET | Nuevo diagnóstico | `@medico_required` | `routes/medico.py:1041` |
| `/medico/diagnosticos/guardar` | POST | Guardar diagnóstico | Solo el día de la cita, validación temporal | `routes/medico.py:1053` |
| `/medico/historial` | GET | Historial médico | `@medico_required` | `routes/medico.py:1409` |
| `/medico/recetas` | GET | Ver recetas | `@medico_required` | `routes/medico.py:1421` |
| `/medico/recetas/nueva` | POST | Nueva receta | `@medico_required` | `routes/medico.py:1433` |
| `/medico/reportes` | GET | Reportes médico | `@medico_required` | `routes/medico.py:1457` |
| `/medico/notificaciones` | GET | Notificaciones | `@medico_required` | `routes/medico.py:1469` |

#### **APIs de Médico**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/medico/api/obtener_diagnostico/<id>` | GET | Obtener diagnóstico | `@medico_required` | `routes/medico.py:1482` |
| `/medico/api/citas-hoy` | GET | Citas del día | `@medico_required` | `routes/medico.py:1522` |
| `/medico/api/estadisticas` | GET | Estadísticas médico | `@medico_required` | `routes/medico.py:1551` |
| `/medico/api/buscar-paciente` | GET | Buscar paciente | `@medico_required` | `routes/medico.py:1571` |
| `/medico/api/obtener_especialidades` | GET | Listar especialidades | `@medico_required` | `routes/medico.py:1586` |
| `/medico/api/verificar_autorizaciones/<id>` | GET | Verificar autorizaciones | `@medico_required` | `routes/medico.py:1780` |
| `/medico/api/obtener_autorizaciones_cita/<id>` | GET | Autorizaciones de cita | `@medico_required` | `routes/medico.py:1795` |
| `/medico/api/notificaciones-recientes` | GET | Notificaciones médico | `@medico_required` | `routes/medico.py:1810` |
| `/medico/api/citas_sin_diagnostico_pendientes` | GET | Citas sin diagnóstico | `@medico_required` | `routes/medico.py:1946` |

---

### 📁 **MÓDULO: RECEPCIONISTA** (`routes/recepcionista.py`)

#### **Rutas de Panel**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/recepcionista/` | GET | Panel recepcionista | `@recepcionista_required` (id_rol == 3) | `routes/recepcionista.py:317` |
| `/recepcionista/panel` | GET | Panel recepcionista | `@recepcionista_required` | `routes/recepcionista.py:318` |

#### **APIs de Pacientes**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/recepcionista/pacientes/listar` | GET | Listar pacientes | `@recepcionista_required` | `routes/recepcionista.py:399` |
| `/recepcionista/pacientes/buscar` | GET | Buscar pacientes | `@recepcionista_required` | `routes/recepcionista.py:409` |
| `/recepcionista/pacientes/<id>` | GET | Detalles paciente | `@recepcionista_required` | `routes/recepcionista.py:493` |
| `/recepcionista/pacientes/registrar` | POST | Registrar paciente | DNI único, correo único, teléfono único, contraseña >= 6 | `routes/recepcionista.py:539` |

#### **APIs de Incidencias**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/recepcionista/incidencias/listar` | GET | Listar incidencias | `@recepcionista_required` | `routes/recepcionista.py:711` |
| `/recepcionista/incidencias/generar` | POST | Generar incidencia | Tipo, descripción, prioridad requeridos | `routes/recepcionista.py:810` |

#### **APIs de Reservas**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/recepcionista/reservas/listar` | GET | Listar reservas | `@recepcionista_required` | `routes/recepcionista.py:848` |

---

### 📁 **MÓDULO: PACIENTE** (`routes/paciente.py`)

#### **Rutas de Paciente**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/paciente/historial-clinico` | GET | Historial clínico | `tipo_usuario == 'paciente'` | `routes/paciente.py:11` |
| `/paciente/api/historial-clinico` | GET | API historial | `tipo_usuario == 'paciente'` | `routes/paciente.py:23` |
| `/paciente/api/autorizacion/<id>/programaciones` | GET | Programaciones autorización | Autorización pendiente, pertenece al paciente | `routes/paciente.py:184` |

---

### 📁 **MÓDULO: RESERVAS** (`routes/reservas.py`)

#### **Rutas de Reservas**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/reservas/` | GET | Panel reservas | `tipo_usuario == 'empleado'` | `routes/reservas.py:94` |
| `/reservas/consultar-servicio-medico` | GET | Consultar por médico | `tipo_usuario == 'empleado'` | `routes/reservas.py:105` |
| `/reservas/consultar-disponibilidad` | GET | Consultar disponibilidad | `tipo_usuario == 'empleado'` | `routes/reservas.py:140` |
| `/reservas/listar-reservas` | GET | Listar reservas | - | `routes/reservas.py:158` |

#### **APIs de Reservas**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/reservas/api/listar-reservas` | GET | API listar reservas | Filtros opcionales | `routes/reservas.py:179` |
| `/reservas/api/detalle-reserva/<id>` | GET | Detalle reserva | - | `routes/reservas.py:309` |
| `/reservas/api/servicios-por-medico/<id>` | GET | Servicios por médico | Empleado es médico (id_rol 2 o 3) | `routes/reservas.py:120` |

---

### 📁 **MÓDULO: NOTIFICACIONES** (`routes/notificaciones.py`)

#### **Rutas de Notificaciones**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/notificaciones/` | GET | Panel notificaciones | `tipo_usuario == 'empleado'` | `routes/notificaciones.py:8` |
| `/notificaciones/historial` | GET | Historial notificaciones | `tipo_usuario == 'paciente'` | `routes/notificaciones.py:525` |

#### **APIs de Notificaciones (Pacientes)**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/notificaciones/api/no-leidas-count` | GET | Contador no leídas | `tipo_usuario == 'paciente'` | `routes/notificaciones.py:55` |
| `/notificaciones/api/recientes` | GET | Notificaciones recientes | `tipo_usuario == 'paciente'` | `routes/notificaciones.py:114` |
| `/notificaciones/api/marcar-leida/<id>` | POST | Marcar como leída | Pertenece al paciente | `routes/notificaciones.py:244` |
| `/notificaciones/api/marcar-todas-leidas` | POST | Marcar todas leídas | `tipo_usuario == 'paciente'` | `routes/notificaciones.py:292` |

#### **APIs de Notificaciones (Médicos)**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/notificaciones/api/recientes-medico` | GET | Notificaciones médico | `tipo_usuario == 'empleado'` | `routes/notificaciones.py:332` |
| `/notificaciones/api/marcar-leida-medico/<id>` | POST | Marcar leída médico | Pertenece al médico | `routes/notificaciones.py:459` |
| `/notificaciones/api/marcar-todas-leidas-medico` | POST | Marcar todas leídas médico | `tipo_usuario == 'empleado'` | `routes/notificaciones.py:496` |

---

### 📁 **MÓDULO: FARMACIA** (`routes/farmacia.py`)

#### **Rutas de Farmacia**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/farmacia/` | GET | Panel farmacia | `id_rol == 4` (Farmacéutico) | `routes/farmacia.py:8` |
| `/farmacia/gestionar-medicamentos` | GET | Gestión medicamentos | `id_rol == 4` | `routes/farmacia.py:138` |
| `/farmacia/gestionar-entrega-medicamentos` | GET | Entrega medicamentos | `id_rol == 4` | `routes/farmacia.py:144` |
| `/farmacia/gestionar-recepcion-medicamentos` | GET | Recepción medicamentos | `id_rol == 4` | `routes/farmacia.py:150` |

#### **APIs de Farmacia**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/farmacia/api/medicamentos` | GET, POST | CRUD medicamentos | `id_rol == 4` | `routes/farmacia.py:157` |
| `/farmacia/api/entregas` | GET, POST | Gestión entregas | `id_rol == 4` | `routes/farmacia.py:214` |
| `/farmacia/api/ingreso` | POST | Ingreso medicamentos | `id_rol == 4` | `routes/farmacia.py:306` |

---

### 📁 **MÓDULO: SEGURIDAD** (`routes/seguridad.py`)

#### **Rutas de Seguridad**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/seguridad/` | GET | Panel seguridad | `tipo_usuario == 'empleado'` | `routes/seguridad.py:7` |
| `/seguridad/consultar-actividad` | GET | Consultar actividad | `tipo_usuario == 'empleado'` | `routes/seguridad.py:28` |
| `/seguridad/incidencias` | GET | Gestión incidencias | `tipo_usuario == 'empleado'` | `routes/seguridad.py:43` |

#### **APIs de Seguridad**
| Ruta | Método | Descripción | Validaciones | Ubicación |
|------|--------|-------------|--------------|-----------|
| `/seguridad/api/incidencias` | GET | Listar incidencias | `tipo_usuario == 'empleado'` | `routes/seguridad.py:103` |
| `/seguridad/api/incidencias/crear` | POST | Crear incidencia | Campos requeridos | `routes/seguridad.py:366` |
| `/seguridad/api/incidencias/<id>/asignar` | POST | Asignar responsable | `tipo_usuario == 'empleado'` | `routes/seguridad.py:221` |
| `/seguridad/api/actividad/estadisticas` | GET | Estadísticas actividad | `tipo_usuario == 'empleado'` | `routes/seguridad.py:249` |

---

## 🔒 VALIDACIONES Y DECORADORES

### **Decoradores de Autenticación/Autorización**

#### **1. `@login_required`**
**Ubicación**: `routes/usuarios.py:10`
```python
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.login'))
        return f(*args, **kwargs)
    return decorated_function
```
**Uso**: Protege rutas que requieren sesión activa
**Dónde modificar**: `routes/usuarios.py:10-17`

---

#### **2. `@empleado_required`**
**Ubicación**: `routes/usuarios.py:20`
```python
def empleado_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tipo_usuario' not in session or session['tipo_usuario'] != 'empleado':
            flash('No tiene permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.perfil'))
        return f(*args, **kwargs)
    return decorated_function
```
**Uso**: Solo empleados pueden acceder
**Dónde modificar**: `routes/usuarios.py:20-27`

---

#### **3. `@medico_required`**
**Ubicación**: `routes/medico.py:628`
```python
def medico_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('cuentas.login'))
        if session.get('id_rol') != 2:
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```
**Uso**: Solo médicos (id_rol == 2)
**Dónde modificar**: `routes/medico.py:628-645`

---

#### **4. `@recepcionista_required`**
**Ubicación**: `routes/recepcionista.py:267`
```python
def recepcionista_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('usuarios.login'))
        id_rol = session.get('id_rol')
        if id_rol != 3:
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
```
**Uso**: Solo recepcionistas (id_rol == 3)
**Dónde modificar**: `routes/recepcionista.py:267-314`

---

#### **5. `@trabajador_required`**
**Ubicación**: `routes/trabajador.py:7`
```python
def trabajador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        if session.get('tipo_usuario') != 'empleado':
            return redirect(url_for('home'))
        id_rol = session.get('id_rol')
        if id_rol == 1:  # No administradores
            return redirect(url_for('admin_panel'))
        if id_rol is None or id_rol not in [2, 3, 4, 5]:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
```
**Uso**: Empleados no administradores (id_rol 2, 3, 4, 5)
**Dónde modificar**: `routes/trabajador.py:7-28`

---

### **Validaciones de Negocio**

#### **1. Validación de Unicidad (Correo, Teléfono, DNI)**
**Ubicación**: `routes/usuarios.py:593-620`
```python
# Verificar correo único
cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s", (correo,))
if cursor.fetchone():
    return jsonify({'error': 'El correo ya está registrado'}), 400

# Verificar teléfono único
cursor.execute("SELECT id_usuario FROM USUARIO WHERE telefono = %s", (telefono,))
if cursor.fetchone():
    return jsonify({'error': 'El teléfono ya está registrado'}), 400

# Verificar DNI único (en PACIENTE y EMPLEADO)
cursor.execute("SELECT id_paciente FROM PACIENTE WHERE documento_identidad = %s", (dni,))
if cursor.fetchone():
    return jsonify({'error': 'El DNI ya está registrado'}), 400
```
**Dónde modificar**: 
- Registro: `routes/usuarios.py:593-620`
- Recepcionista: `routes/recepcionista.py:613-643`

---

#### **2. Validación de Contraseña**
**Ubicación**: `routes/usuarios.py:226-228` (creación), `routes/usuarios.py:1189-1205` (cambio)
```python
# Creación: mínimo 6 caracteres
if len(contrasena) < 6:
    flash('La contraseña debe tener al menos 6 caracteres', 'warning')

# Cambio: mínimo 8 caracteres, mayúsculas, minúsculas, números
if len(nueva_contrasena) < 8:
    flash('La contraseña debe tener al menos 8 caracteres', 'error')
if not re.search(r'[A-Z]', nueva_contrasena):
    flash('Debe contener al menos una mayúscula', 'error')
if not re.search(r'[a-z]', nueva_contrasena):
    flash('Debe contener al menos una minúscula', 'error')
if not re.search(r'\d', nueva_contrasena):
    flash('Debe contener al menos un número', 'error')
```
**Dónde modificar**:
- Creación: `routes/usuarios.py:226-228`
- Cambio: `routes/usuarios.py:1189-1205`

---

#### **3. Validación de Edad (18-100 años)**
**Ubicación**: `routes/usuarios.py:388-407`
```python
fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
ahora = datetime.now()
edad = ahora.year - fecha_nac.year
if (ahora.month, ahora.day) < (fecha_nac.month, fecha_nac.day):
    edad -= 1

# Validar edad mínima (18 años)
edad_minima = datetime.now() - timedelta(days=18*365.25)
if fecha_nac > edad_minima:
    flash('Debes ser mayor de 18 años', 'danger')

# Validar edad máxima (100 años)
if edad > 100:
    flash('La edad no puede superar los 100 años', 'danger')
```
**Dónde modificar**: `routes/usuarios.py:388-407`

---

#### **4. Validación de Documento de Identidad**
**Ubicación**: `routes/recepcionista.py:581-597`
```python
if tipo_documento == 'DNI':
    if len(documento_identidad) != 8 or not documento_identidad.isdigit():
        return jsonify({'error': 'El DNI debe tener exactamente 8 dígitos'}), 400
elif tipo_documento == 'CE':
    if len(documento_identidad) < 9 or len(documento_identidad) > 12:
        return jsonify({'error': 'El CE debe tener entre 9 y 12 dígitos'}), 400
elif tipo_documento == 'PASAPORTE':
    if len(documento_identidad) < 6 or len(documento_identidad) > 15:
        return jsonify({'error': 'El Pasaporte debe tener entre 6 y 15 caracteres'}), 400
```
**Dónde modificar**: `routes/recepcionista.py:581-597`

---

#### **5. Validación Temporal de Diagnóstico**
**Ubicación**: `routes/medico.py:1053` (función `diagnosticos_guardar`)
```python
# Solo se puede registrar diagnóstico el día de la cita
# Desde hora_inicio hasta 23:59:59
fecha_actual = date.today()
hora_actual = datetime.now().time()

if fecha_cita != fecha_actual:
    flash('Solo se puede registrar diagnóstico el día de la cita', 'danger')
    return redirect(url_for('medico.diagnosticos'))

if fecha_cita == fecha_actual:
    if hora_actual < hora_inicio:
        flash('No se puede registrar diagnóstico antes de la hora de inicio', 'danger')
        return redirect(url_for('medico.diagnosticos'))
```
**Dónde modificar**: Buscar función `diagnosticos_guardar` en `routes/medico.py`

---

#### **6. Validación de Disponibilidad de Reserva**
**Ubicación**: `models/reserva.py` (método `crear`)
```python
# Verificar que la programación esté disponible
if programacion['estado'] != 'Disponible':
    return {'error': 'La programación no está disponible'}

# Verificar que no haya solapamiento de reservas
# Un paciente no puede tener 2 reservas en el mismo horario
```
**Dónde modificar**: `models/reserva.py` (método `crear`)

---

#### **7. Validación de Código de Recuperación**
**Ubicación**: `routes/usuarios.py:970-986`
```python
# Código válido por 15 minutos, no usado
cursor.execute("""
    SELECT id_recuperacion
    FROM RECUPERACION_CONTRASENA
    WHERE id_usuario = %s
      AND codigo = %s
      AND usado = FALSE
      AND TIMESTAMPDIFF(MINUTE, fecha_creacion, NOW()) <= 15
""", (id_usuario, codigo))
```
**Dónde modificar**: `routes/usuarios.py:970-986`

---

## 🗺️ GUÍA DE NAVEGACIÓN PARA CAMBIOS

### **¿Dónde modificar validaciones de autenticación?**

#### **Cambiar requisitos de login**
📍 **Ubicación**: `routes/usuarios.py:29-89`
- Validación de campos: línea 36-38
- Verificación de usuario activo: `models/usuario.py` (método `login`)
- Redirección según rol: líneas 71-87

#### **Cambiar requisitos de contraseña**
📍 **Creación de usuario**:
- Mínimo 6 caracteres: `routes/usuarios.py:226-228`
- Validación en modelo: `models/usuario.py` (método `crear_usuario`)

📍 **Cambio de contraseña**:
- Mínimo 8 caracteres: `routes/usuarios.py:1189`
- Mayúsculas: `routes/usuarios.py:1195`
- Minúsculas: `routes/usuarios.py:1199`
- Números: `routes/usuarios.py:1203`

#### **Cambiar validación de edad**
📍 **Ubicación**: `routes/usuarios.py:388-407`
- Edad mínima (18 años): línea 400
- Edad máxima (100 años): línea 405

---

### **¿Dónde modificar validaciones de negocio?**

#### **Cambiar validación de unicidad (correo, teléfono, DNI)**
📍 **Registro de usuarios**:
- `routes/usuarios.py:593-620` (API register)
- `routes/recepcionista.py:613-643` (Registro recepcionista)

#### **Cambiar validación de documento de identidad**
📍 **Ubicación**: `routes/recepcionista.py:581-597`
- DNI: 8 dígitos
- CE: 9-12 dígitos
- Pasaporte: 6-15 caracteres alfanuméricos

#### **Cambiar validación temporal de diagnóstico**
📍 **Ubicación**: Buscar función `diagnosticos_guardar` en `routes/medico.py`
- Validación de fecha: solo el día de la cita
- Validación de hora: desde hora_inicio hasta 23:59:59

#### **Cambiar validación de disponibilidad de reserva**
📍 **Ubicación**: `models/reserva.py` (método `crear`)
- Verificar estado de programación
- Verificar solapamiento de reservas

---

### **¿Dónde agregar nuevas validaciones?**

#### **Agregar validación en creación de usuario**
1. Ir a `routes/usuarios.py:205` (función `crear`)
2. Agregar validación después de línea 218 (validaciones existentes)
3. Ejemplo:
```python
# Nueva validación
if not validar_nuevo_campo(campo):
    flash('Mensaje de error', 'warning')
    return render_template('crearcuentaPaciente.html')
```

#### **Agregar validación en API**
1. Identificar el endpoint en la tabla de rutas
2. Ir a la ubicación indicada
3. Agregar validación antes del procesamiento
4. Retornar error JSON si falla

---

### **¿Dónde modificar permisos de acceso?**

#### **Cambiar acceso a ruta de empleados**
📍 **Ubicación**: Decorador `@empleado_required` en `routes/usuarios.py:20`
- Modificar condición: línea 23
- Cambiar mensaje: línea 24
- Cambiar redirección: línea 25

#### **Cambiar acceso a ruta de médicos**
📍 **Ubicación**: Decorador `@medico_required` en `routes/medico.py:628`
- Modificar condición: línea 640 (`id_rol != 2`)
- Cambiar mensaje: línea 641
- Cambiar redirección: línea 642

#### **Cambiar acceso a ruta de recepcionistas**
📍 **Ubicación**: Decorador `@recepcionista_required` en `routes/recepcionista.py:267`
- Modificar condición: línea 307 (`id_rol != 3`)
- Cambiar mensaje: línea 309
- Cambiar redirección: línea 310

---

## 📝 VALIDACIONES DETALLADAS POR FUNCIONALIDAD

### **1. REGISTRO DE USUARIOS**

#### **Validaciones en Creación de Paciente**
| Validación | Ubicación | Mensaje de Error |
|------------|-----------|------------------|
| Campos requeridos | `routes/usuarios.py:218` | "Debe completar todos los campos obligatorios" |
| Contraseñas coinciden | `routes/usuarios.py:222` | "Las contraseñas no coinciden" |
| Contraseña >= 6 chars | `routes/usuarios.py:226` | "La contraseña debe tener al menos 6 caracteres" |
| Correo único | `routes/usuarios.py:596-599` | "El correo electrónico ya está registrado" |
| Teléfono único | `routes/usuarios.py:602-607` | "El teléfono ya está registrado" |
| DNI único | `routes/usuarios.py:611-620` | "El documento de identidad ya está registrado" |

#### **Validaciones en Registro por Recepcionista**
| Validación | Ubicación | Mensaje de Error |
|------------|-----------|------------------|
| DNI: 8 dígitos | `routes/recepcionista.py:588` | "El DNI debe tener exactamente 8 dígitos" |
| CE: 9-12 dígitos | `routes/recepcionista.py:591` | "El CE debe tener entre 9 y 12 dígitos" |
| Pasaporte: 6-15 chars | `routes/recepcionista.py:594` | "El Pasaporte debe tener entre 6 y 15 caracteres" |

---

### **2. CAMBIO DE CONTRASEÑA**

#### **Validaciones**
| Validación | Ubicación | Mensaje de Error |
|------------|-----------|------------------|
| Campos requeridos | `routes/usuarios.py:1181` | "Todos los campos son obligatorios" |
| Contraseñas coinciden | `routes/usuarios.py:1185` | "La nueva contraseña y su confirmación no coinciden" |
| Contraseña >= 8 chars | `routes/usuarios.py:1189` | "La contraseña debe tener al menos 8 caracteres" |
| Tiene mayúscula | `routes/usuarios.py:1195` | "Debe contener al menos una mayúscula" |
| Tiene minúscula | `routes/usuarios.py:1199` | "Debe contener al menos una minúscula" |
| Tiene número | `routes/usuarios.py:1203` | "Debe contener al menos un número" |
| Contraseña actual correcta | `routes/usuarios.py:1214` | "La contraseña actual es incorrecta" |

---

### **3. RECUPERACIÓN DE CONTRASEÑA**

#### **Validaciones**
| Validación | Ubicación | Mensaje de Error |
|------------|-----------|------------------|
| Correo requerido | `routes/usuarios.py:840` | "El correo electrónico es requerido" |
| Usuario existe | `routes/usuarios.py:848` | (No se revela si existe) |
| Código válido | `routes/usuarios.py:970-986` | "Código inválido o expirado" |
| Código no usado | `routes/usuarios.py:977` | "Código inválido o expirado" |
| Código vigente (15 min) | `routes/usuarios.py:978` | "Código inválido o expirado" |
| Nueva contraseña >= 6 | `routes/usuarios.py:1012` | "La contraseña debe tener al menos 6 caracteres" |

---

### **4. EDICIÓN DE PERFIL**

#### **Validaciones**
| Validación | Ubicación | Mensaje de Error |
|------------|-----------|------------------|
| Edad mínima (18 años) | `routes/usuarios.py:400` | "Debes ser mayor de 18 años" |
| Edad máxima (100 años) | `routes/usuarios.py:405` | "La edad no puede superar los 100 años" |
| Sexo no modificable | `routes/usuarios.py:381-383` | (No se permite cambio) |

---

### **5. REGISTRO DE DIAGNÓSTICO**

#### **Validaciones**
| Validación | Ubicación | Mensaje de Error |
|------------|-----------|------------------|
| Solo el día de la cita | Buscar en `routes/medico.py` | "Solo se puede registrar diagnóstico el día de la cita" |
| Después de hora_inicio | Buscar en `routes/medico.py` | "No se puede registrar diagnóstico antes de la hora de inicio" |
| Cita existe | Buscar en `routes/medico.py` | "Cita no encontrada" |
| Médico es el asignado | Buscar en `routes/medico.py` | "No tiene permisos para registrar este diagnóstico" |

---

### **6. CREACIÓN DE RESERVA**

#### **Validaciones**
| Validación | Ubicación | Mensaje de Error |
|------------|-----------|------------------|
| Programación disponible | `models/reserva.py` | "La programación no está disponible" |
| No solapamiento | `models/reserva.py` | "Ya tiene una reserva en este horario" |
| Paciente existe | `models/reserva.py` | "Paciente no encontrado" |
| Fecha futura | `models/reserva.py` | "No se pueden reservar fechas pasadas" |

---

## 🔧 EJEMPLOS PRÁCTICOS DE MODIFICACIONES

### **Ejemplo 1: Cambiar validación de contraseña mínima**

**Situación**: Cambiar de 6 a 8 caracteres mínimos en creación de usuario

**Pasos**:
1. Ir a `routes/usuarios.py:226`
2. Cambiar:
```python
# ANTES
if len(contrasena) < 6:
    flash('La contraseña debe tener al menos 6 caracteres', 'warning')

# DESPUÉS
if len(contrasena) < 8:
    flash('La contraseña debe tener al menos 8 caracteres', 'warning')
```

3. También cambiar en `routes/recepcionista.py:604` (registro por recepcionista)

---

### **Ejemplo 2: Agregar validación de formato de correo**

**Situación**: Validar que el correo tenga formato válido

**Pasos**:
1. Ir a `routes/usuarios.py:218` (después de validaciones existentes)
2. Agregar:
```python
import re

# Después de línea 228
if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
    flash('El formato del correo electrónico no es válido', 'warning')
    return render_template('crearcuentaPaciente.html')
```

3. También agregar en `routes/usuarios.py:568` (API register) y `routes/recepcionista.py:539` (registro recepcionista)

---

### **Ejemplo 3: Cambiar edad mínima de 18 a 16 años**

**Situación**: Permitir registro a partir de 16 años

**Pasos**:
1. Ir a `routes/usuarios.py:399`
2. Cambiar:
```python
# ANTES
edad_minima = datetime.now() - timedelta(days=18*365.25)
if fecha_nac > edad_minima:
    flash('Debes ser mayor de 18 años', 'danger')

# DESPUÉS
edad_minima = datetime.now() - timedelta(days=16*365.25)
if fecha_nac > edad_minima:
    flash('Debes ser mayor de 16 años', 'danger')
```

---

### **Ejemplo 4: Agregar validación de teléfono (9 dígitos)**

**Situación**: Validar que el teléfono tenga exactamente 9 dígitos

**Pasos**:
1. Ir a `routes/usuarios.py:218` (función `crear`)
2. Agregar después de línea 228:
```python
# Validar formato de teléfono
if telefono:
    if not telefono.isdigit() or len(telefono) != 9:
        flash('El teléfono debe tener exactamente 9 dígitos', 'warning')
        return render_template('crearcuentaPaciente.html')
```

3. También agregar en `routes/usuarios.py:568` (API register)

---

### **Ejemplo 5: Cambiar tiempo de validez del código de recuperación**

**Situación**: Cambiar de 15 minutos a 30 minutos

**Pasos**:
1. Ir a `routes/usuarios.py:978` (validación de código)
2. Cambiar:
```python
# ANTES
AND TIMESTAMPDIFF(MINUTE, fecha_creacion, NOW()) <= 15

# DESPUÉS
AND TIMESTAMPDIFF(MINUTE, fecha_creacion, NOW()) <= 30
```

3. También cambiar en `routes/usuarios.py:1033` (reset-password)

---

### **Ejemplo 6: Agregar validación de horario laboral**

**Situación**: Validar que las reservas solo se puedan hacer en horario laboral (8:00-18:00)

**Pasos**:
1. Ir a `models/reserva.py` (método `crear`)
2. Agregar validación:
```python
from datetime import time

hora_inicio = programacion.get('hora_inicio')
if isinstance(hora_inicio, timedelta):
    total_seconds = int(hora_inicio.total_seconds())
    hours = total_seconds // 3600
    hora_inicio_time = time(hours, 0)

if hora_inicio_time < time(8, 0) or hora_inicio_time > time(18, 0):
    return {'error': 'Las reservas solo se pueden hacer en horario laboral (8:00-18:00)'}
```

---

### **Ejemplo 7: Modificar validación de diagnóstico (permitir día anterior)**

**Situación**: Permitir registrar diagnóstico el día anterior a la cita

**Pasos**:
1. Buscar función `diagnosticos_guardar` en `routes/medico.py`
2. Cambiar validación de fecha:
```python
# ANTES
if fecha_cita != fecha_actual:
    flash('Solo se puede registrar diagnóstico el día de la cita', 'danger')

# DESPUÉS
fecha_anterior = fecha_actual - timedelta(days=1)
if fecha_cita not in [fecha_actual, fecha_anterior]:
    flash('Solo se puede registrar diagnóstico el día de la cita o el día anterior', 'danger')
```

---

## 📌 RESUMEN DE UBICACIONES CLAVE

### **Archivos de Rutas Principales**
- `routes/usuarios.py` - Autenticación y gestión de usuarios
- `routes/admin.py` - Panel de administración
- `routes/medico.py` - Panel médico y diagnósticos
- `routes/recepcionista.py` - Panel recepcionista
- `routes/paciente.py` - Funcionalidades para pacientes
- `routes/reservas.py` - Gestión de reservas
- `routes/notificaciones.py` - Sistema de notificaciones

### **Archivos de Modelos**
- `models/usuario.py` - Modelo de usuario
- `models/paciente.py` - Modelo de paciente
- `models/reserva.py` - Modelo de reserva
- `models/agenda.py` - Modelo de agenda

### **Decoradores de Validación**
- `@login_required` - `routes/usuarios.py:10`
- `@empleado_required` - `routes/usuarios.py:20`
- `@medico_required` - `routes/medico.py:628`
- `@recepcionista_required` - `routes/recepcionista.py:267`
- `@trabajador_required` - `routes/trabajador.py:7`

---

## 🎯 CONCLUSIÓN

Este documento proporciona un mapa completo de todas las rutas, validaciones y ubicaciones del proyecto. Para hacer cambios:

1. **Identifica la funcionalidad** en la tabla de rutas
2. **Localiza la ruta** usando la columna "Ubicación"
3. **Revisa las validaciones** en la sección correspondiente
4. **Sigue los ejemplos prácticos** para modificaciones comunes

**Recuerda**: Siempre verifica que los cambios no afecten otras partes del sistema y prueba exhaustivamente antes de desplegar.

---

**Última actualización**: Generado automáticamente
**Versión del documento**: 1.0

