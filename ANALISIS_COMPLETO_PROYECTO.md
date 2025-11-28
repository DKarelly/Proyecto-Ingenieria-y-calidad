# 📋 ANÁLISIS COMPLETO DEL PROYECTO - SISTEMA DE GESTIÓN MÉDICA

## 🎯 DESCRIPCIÓN GENERAL

Sistema de gestión médica desarrollado en **Flask (Python)** con base de datos **MySQL** que gestiona:
- Reservas y citas médicas
- Diagnósticos y autorizaciones de procedimientos
- Notificaciones por email y en sistema
- Gestión de usuarios (pacientes y empleados)
- Roles y permisos
- Reportes y estadísticas

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### **Stack Tecnológico**
- **Backend**: Flask 3.1.2 (Python)
- **Base de Datos**: MySQL (Railway)
- **ORM**: PyMySQL con pool de conexiones
- **Frontend**: HTML5, CSS (TailwindCSS), JavaScript
- **Email**: SMTP (Gmail)
- **Servidor**: Gunicorn (producción)

### **Estructura de Directorios**
```
Proyecto-Ingenieria-y-calidad/
├── app.py                 # Punto de entrada principal
├── bd.py                  # Gestión de conexiones DB
├── models/                # Modelos de datos (MVC)
├── routes/                # Blueprints de rutas
├── utils/                 # Utilidades (email, notificaciones)
├── templates/             # Plantillas Jinja2
├── static/                # CSS, JS, imágenes
├── scripts/               # Scripts SQL y Python
└── docs/                  # Documentación
```

---

## 🔐 SISTEMA DE AUTENTICACIÓN Y ROLES

### **Tipos de Usuarios**
1. **Paciente** (`tipo_usuario = 'paciente'`)
   - Acceso limitado a su información
   - Puede agendar citas y ver historial

2. **Empleado** (`tipo_usuario = 'empleado'`)
   - **Rol 1**: Administrador
   - **Rol 2**: Médico
   - **Rol 3**: Recepcionista
   - **Rol 4**: Farmacéutico
   - **Rol 5**: Laboratorista

### **Flujo de Autenticación**
```
1. Usuario ingresa correo y contraseña
2. Sistema verifica en tabla USUARIO
3. Obtiene datos de PACIENTE o EMPLEADO según corresponda
4. Carga información de rol y permisos
5. Crea sesión con:
   - usuario_id
   - tipo_usuario
   - id_rol
   - id_empleado / id_paciente
   - nombre_usuario
6. Redirige según rol:
   - Admin → /admin/panel
   - Médico → /medico/panel
   - Paciente → Panel de paciente
```

### **Sistema de Permisos**
- Tabla `PERMISO` con permisos por módulo
- Tabla `ROL_PERMISO` relaciona roles con permisos
- Verificación en decoradores (`@medico_required`, etc.)

---

## 📅 FLUJO PRINCIPAL: RESERVA DE CITA MÉDICA

### **1. Creación de Horarios (Admin/Recepcionista)**
```
Admin/Recepcionista → Crear HORARIO
├── Selecciona empleado (médico)
├── Define fecha y hora_inicio/hora_fin
├── Crea PROGRAMACION con estado 'Disponible'
└── Sistema valida que no haya solapamientos
```

### **2. Paciente Solicita Cita**
```
Paciente → /reservas/paciente/registrar-cita
├── Paso 1: Selecciona especialidad
├── Paso 2: Selecciona médico
├── Paso 3: Selecciona servicio
├── Paso 4: Selecciona fecha y hora disponible
└── Paso 5: Confirma reserva
```

### **3. Proceso de Creación de Reserva**
```python
# routes/reservas.py - paciente_crear_reserva()
1. Validar que programación esté 'Disponible'
2. Verificar que no haya solapamiento con otras reservas del paciente
3. Actualizar PROGRAMACION: estado = 'Ocupado'
4. Crear RESERVA:
   - tipo = 1 (CITA_MEDICA)
   - estado = 'Confirmada'
   - fecha_registro, hora_registro = NOW()
5. Crear CITA:
   - fecha_cita, hora_inicio, hora_fin
   - estado = 'Pendiente'
6. Enviar notificaciones:
   - Email al paciente (confirmación)
   - Email al médico (nueva cita asignada)
   - Notificación en sistema
```

### **4. Estados de Reserva**
- **Confirmada**: Reserva creada, pendiente de atención
- **Pendiente**: Cita en espera de diagnóstico
- **Completada**: Cita atendida con diagnóstico
- **Cancelada**: Reserva cancelada
- **Inasistida**: Paciente no asistió

---

## 🩺 FLUJO: REGISTRO DE DIAGNÓSTICO MÉDICO

### **1. Médico Accede a Cita**
```
Médico → Panel Médico → Diagnósticos
├── Ve lista de citas pendientes
├── Selecciona cita del día
└── Abre formulario de diagnóstico
```

### **2. Validaciones Temporales**
```python
# routes/medico.py - guardar_diagnostico()
✅ Validación 1: No antes de hora_inicio de la cita
✅ Validación 2: Máximo hasta 23:59:59 del día de la cita
✅ Validación 3: No en citas canceladas
✅ Validación 4: Solo el médico que registró puede modificar
```

### **3. Registro de Diagnóstico**
```python
1. Guardar diagnóstico y observaciones en CITA
2. Cambiar estado de CITA a 'Completada'
3. Si es modificación: guardar en historial_diagnosticos
4. Si se autorizan procedimientos:
   ├── Crear AUTORIZACION_PROCEDIMIENTO (EXAMEN u OPERACION)
   ├── Fecha vencimiento: +7 días desde autorización
   ├── Enviar notificación al paciente
   └── Enviar notificación al médico asignado (si aplica)
```

### **4. Autorización de Procedimientos**
```
Médico autoriza → Crear AUTORIZACION_PROCEDIMIENTO
├── Tipo: EXAMEN (id_tipo_servicio = 4) u OPERACION (id_tipo_servicio = 2)
├── Servicio específico
├── Médico asignado (puede ser el mismo o derivado)
├── Especialidad requerida
└── Válida por 7 días
```

---

## 🔄 FLUJO: AGENDAMIENTO DE PROCEDIMIENTOS (EXAMEN/OPERACIÓN)

### **1. Paciente Ve Autorizaciones Pendientes**
```
Paciente → Panel → Ver autorizaciones
├── Sistema verifica AUTORIZACION_PROCEDIMIENTO
├── Filtra: fecha_uso IS NULL AND fecha_vencimiento > NOW()
└── Muestra botones "Agendar Examen" / "Agendar Operación"
```

### **2. Proceso de Agendamiento**
```python
# routes/paciente.py - api_reservar_procedimiento_cita()
1. Validar autorización:
   ├── Existe y no está vencida
   ├── No ha sido utilizada (fecha_uso IS NULL)
   └── Pertenece al paciente
2. Seleccionar programación disponible del médico asignado
3. Crear RESERVA:
   ├── tipo = 2 (OPERACION) o 3 (EXAMEN)
   └── estado = 'Confirmada'
4. Crear EXAMEN u OPERACION según corresponda
5. Actualizar autorización:
   ├── fecha_uso = NOW()
   └── id_reserva_generada = id_reserva
6. Actualizar PROGRAMACION: estado = 'Ocupado'
7. Enviar notificaciones
```

---

## 📧 SISTEMA DE NOTIFICACIONES

### **Tipos de Notificaciones**

#### **1. Notificaciones en Sistema (Tabla NOTIFICACION)**
- Al crear reserva
- Al cambiar estado de reserva
- Al recibir autorización
- Al asignar médico a procedimiento
- Recordatorios de citas

#### **2. Notificaciones por Email**
```python
# utils/email_service.py
✅ Reserva creada (paciente y médico)
✅ Cambio de estado de reserva
✅ Cancelación aprobada
✅ Reprogramación aprobada
✅ Recordatorio 24h antes
✅ Recordatorio 2h antes
✅ Autorización recibida
✅ Procedimiento derivado
```

### **Envío Asíncrono de Emails**
```python
# Protocolo "Mensajero Fantasma"
1. Request HTTP llega
2. Se lanza thread separado para enviar email
3. Request responde inmediatamente al usuario
4. Email se envía en background
5. Evita timeouts de Gunicorn
```

---

## 🔄 FLUJOS SECUNDARIOS

### **1. Cancelación de Reserva**
```
Paciente solicita cancelación
├── Recepcionista/Admin revisa
├── Aprueba o rechaza
├── Si aprueba:
│   ├── Cambia estado a 'Cancelada'
│   ├── Libera PROGRAMACION (estado = 'Disponible')
│   ├── Envía email al paciente
│   └── Envía email al médico
└── Si rechaza: notifica motivo
```

### **2. Reprogramación de Reserva**
```
Paciente solicita reprogramación
├── Recepcionista/Admin revisa
├── Busca nueva programación disponible
├── Actualiza RESERVA: id_programacion = nuevo
├── Libera programación anterior
├── Envía email con comparación de fechas
└── Notifica al médico
```

### **3. Gestión de Usuarios (Admin)**
```
Admin → Gestión de Cuentas
├── Crear empleado:
│   ├── Crear USUARIO
│   ├── Crear EMPLEADO
│   ├── Asignar ROL
│   └── Asignar ESPECIALIDAD (si es médico)
├── Crear paciente:
│   ├── Crear USUARIO
│   └── Crear PACIENTE
└── Editar/Eliminar (soft delete: estado = 'Inactivo')
```

### **4. Gestión de Horarios**
```
Admin/Médico → Crear horarios
├── Selecciona médico
├── Define fecha y bloques de tiempo
├── Sistema crea PROGRAMACION para cada bloque
└── Estado inicial: 'Disponible'
```

---

## 🗄️ MODELO DE DATOS PRINCIPAL

### **Tablas Core**
```
USUARIO
├── id_usuario (PK)
├── correo (UNIQUE)
├── contrasena (hashed)
├── telefono
└── estado

PACIENTE
├── id_paciente (PK)
├── id_usuario (FK → USUARIO)
├── nombres, apellidos
├── documento_identidad (UNIQUE)
└── fecha_nacimiento

EMPLEADO
├── id_empleado (PK)
├── id_usuario (FK → USUARIO)
├── id_rol (FK → ROL)
├── id_especialidad (FK → ESPECIALIDAD)
└── nombres, apellidos

ROL
├── id_rol (PK)
└── nombre (Administrador, Médico, etc.)

PERMISO
├── id_permiso (PK)
├── codigo
├── modulo
└── descripcion

ROL_PERMISO
├── id_rol (FK)
└── id_permiso (FK)
```

### **Tablas de Reservas**
```
HORARIO
├── id_horario (PK)
├── id_empleado (FK → EMPLEADO)
├── fecha
├── hora_inicio, hora_fin
└── activo (bool)

PROGRAMACION
├── id_programacion (PK)
├── id_horario (FK → HORARIO)
├── id_servicio (FK → SERVICIO)
├── fecha
├── hora_inicio, hora_fin
└── estado ('Disponible', 'Ocupado', 'Bloqueado')

RESERVA
├── id_reserva (PK)
├── id_paciente (FK → PACIENTE)
├── id_programacion (FK → PROGRAMACION)
├── tipo (1=CITA, 2=OPERACION, 3=EXAMEN)
├── estado
├── fecha_registro, hora_registro
└── motivo_cancelacion

CITA
├── id_cita (PK)
├── id_reserva (FK → RESERVA)
├── fecha_cita
├── hora_inicio, hora_fin
├── diagnostico
├── observaciones
└── estado
```

### **Tablas de Autorizaciones**
```
AUTORIZACION_PROCEDIMIENTO
├── id_autorizacion (PK)
├── id_cita (FK → CITA)
├── id_paciente (FK → PACIENTE)
├── id_medico_autoriza (FK → EMPLEADO)
├── id_medico_asignado (FK → EMPLEADO)
├── id_tipo_servicio (FK → TIPO_SERVICIO)
├── id_servicio (FK → SERVICIO)
├── id_especialidad_requerida (FK → ESPECIALIDAD)
├── fecha_autorizacion
├── fecha_vencimiento (7 días)
├── fecha_uso (cuando se agendó)
└── id_reserva_generada (FK → RESERVA)
```

### **Tablas de Notificaciones**
```
NOTIFICACION
├── id_notificacion (PK)
├── id_usuario (FK → USUARIO)
├── titulo
├── mensaje (HTML)
├── tipo
├── fecha_envio, hora_envio
├── leida (bool)
├── fecha_leida
└── id_reserva (FK → RESERVA, opcional)
```

---

## 🔧 COMPONENTES TÉCNICOS

### **1. Pool de Conexiones (bd.py)**
```python
class SimpleConnectionPool:
    - Pool de 10 conexiones
    - Reutilización de conexiones
    - Verificación con ping()
    - Fallback a conexión directa si pool falla
```

### **2. Sistema de Email (utils/email_service.py)**
```python
EmailService:
- Configuración SMTP desde .env
- Templates HTML responsivos
- Envío asíncrono (threading)
- Manejo de errores y reintentos
- Timeout de 10 segundos
```

### **3. Blueprints de Rutas**
```
routes/
├── usuarios.py      # Login, registro, perfil
├── cuentas.py       # Gestión de usuarios (admin)
├── reservas.py      # Reservas y citas
├── medico.py         # Panel médico, diagnósticos
├── paciente.py      # Panel paciente
├── admin.py         # Panel administrador
├── recepcionista.py # Panel recepcionista
├── notificaciones.py # Gestión de notificaciones
├── reportes.py      # Reportes y estadísticas
└── farmacia.py      # Gestión de farmacia
```

### **4. Modelos (models/)**
```
Cada modelo tiene métodos estáticos:
- crear()
- obtener_por_id()
- obtener_todos()
- actualizar()
- eliminar()
- Métodos específicos según necesidad
```

---

## 🔄 FLUJOS DE DATOS COMPLETOS

### **Flujo 1: Cita Médica Completa**
```
1. Admin crea horario → PROGRAMACION (Disponible)
2. Paciente selecciona → RESERVA creada
3. PROGRAMACION → Ocupado
4. CITA creada (Pendiente)
5. Email a paciente y médico
6. Recordatorio 24h antes
7. Recordatorio 2h antes
8. Médico registra diagnóstico
9. CITA → Completada
10. Si autoriza procedimiento → AUTORIZACION_PROCEDIMIENTO
11. Paciente agenda procedimiento → Nueva RESERVA
12. Procedimiento completado
```

### **Flujo 2: Autorización y Procedimiento**
```
1. Médico en diagnóstico → Autoriza EXAMEN/OPERACION
2. AUTORIZACION_PROCEDIMIENTO creada (válida 7 días)
3. Notificación a paciente
4. Notificación a médico asignado
5. Paciente ve autorización pendiente
6. Selecciona fecha/hora disponible
7. RESERVA creada (tipo 2 o 3)
8. EXAMEN u OPERACION creado
9. AUTORIZACION_PROCEDIMIENTO → fecha_uso = NOW()
10. Notificaciones de confirmación
```

---

## 📊 SISTEMA DE REPORTES Y ESTADÍSTICAS

### **Panel Médico**
- Citas del día
- Citas pendientes de diagnóstico
- Pacientes únicos de la semana
- Estadísticas de atención

### **Panel Admin**
- Total de reservas
- Reservas por estado
- Reservas por médico
- Reservas por servicio
- Reportes exportables (PDF)

---

## 🔒 SEGURIDAD

### **Medidas Implementadas**
1. **Contraseñas**: Hash con Werkzeug (bcrypt)
2. **Sesiones**: Flask session con SECRET_KEY
3. **Validaciones**: Backend y frontend
4. **SQL Injection**: Uso de parámetros (%s)
5. **XSS**: Jinja2 auto-escape
6. **CSRF**: (Pendiente implementar tokens)

### **Validaciones de Negocio**
- Unicidad de DNI, correo, teléfono
- Edad mínima 18 años
- Validación de horarios (no solapamiento)
- Validación temporal de diagnósticos
- Verificación de especialidades en autorizaciones

---

## 🚀 OPTIMIZACIONES IMPLEMENTADAS

### **Base de Datos**
- Pool de conexiones
- Índices en campos frecuentes
- Queries optimizadas con STRAIGHT_JOIN
- Caché simple para consultas frecuentes (5 min)

### **Frontend**
- Lazy loading de blueprints
- Carga condicional de datos según subsistema
- Pre-cálculo de datos en backend
- Minimización de queries N+1

### **Email**
- Envío asíncrono (no bloquea requests)
- Timeout reducido (10s)
- Reintentos automáticos (3 intentos)

---

## 📝 PUNTOS IMPORTANTES

### **Estados y Transiciones**
```
PROGRAMACION:
Disponible → Ocupado (al crear reserva)
Ocupado → Disponible (al cancelar)

RESERVA:
Confirmada → Pendiente (al iniciar cita)
Pendiente → Completada (con diagnóstico)
Confirmada → Cancelada
Confirmada → Inasistida

CITA:
Pendiente → Completada (con diagnóstico)
Pendiente → Cancelada
```

### **Validaciones Críticas**
1. **Solapamiento de reservas**: Un paciente no puede tener 2 reservas en el mismo horario
2. **Disponibilidad**: Solo se pueden reservar PROGRAMACION con estado 'Disponible'
3. **Vencimiento de autorizaciones**: 7 días desde creación
4. **Tiempo de diagnóstico**: Solo el día de la cita, desde hora_inicio hasta 23:59:59

---

## 🔄 TAREAS AUTOMÁTICAS (Pendientes de Implementar)

### **Recordatorios Automáticos**
- Script que corre cada hora
- Busca citas en 24 horas
- Busca citas en 2 horas
- Envía emails automáticos

### **Limpieza de Autorizaciones Vencidas**
- Marcar autorizaciones vencidas
- Notificar a pacientes

### **Actualización de Horarios Vencidos**
- Cambiar PROGRAMACION vencidas a 'Ocupado'
- Ejecuta cada 5 minutos (en memoria)

---

## 📚 DOCUMENTACIÓN ADICIONAL

El proyecto incluye documentación detallada en `docs/`:
- `SISTEMA_EMAILS_NOTIFICACIONES.md`
- `IMPLEMENTACION_DIAGNOSTICOS.md`
- `IMPLEMENTACION_MEJORAS_AUTORIZACIONES.md`
- `SISTEMA_ROLES_PERMISOS.md`
- `CONFIGURACION_EMAIL_NOTIFICACIONES.md`

---

## 🎯 CONCLUSIÓN

Sistema completo de gestión médica con:
- ✅ Gestión de usuarios y roles
- ✅ Reservas y citas médicas
- ✅ Diagnósticos y autorizaciones
- ✅ Notificaciones (email + sistema)
- ✅ Reportes y estadísticas
- ✅ Optimizaciones de rendimiento
- ✅ Validaciones de negocio
- ✅ Seguridad básica

**Arquitectura**: MVC con Flask Blueprints
**Base de Datos**: MySQL relacional
**Comunicación**: Email SMTP + Notificaciones en sistema
**Frontend**: HTML/CSS/JS con TailwindCSS

