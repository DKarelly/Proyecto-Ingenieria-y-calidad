# Gestión de Cancelaciones - Sistema de Clínica

## Descripción

Módulo completo para gestionar la cancelación de reservas médicas con una interfaz moderna y funcional. Permite buscar, filtrar y cancelar citas médicas de manera eficiente.

## Características Principales

### 1. **Dashboard con Estadísticas**
   - Total de reservas activas
   - Reservas pendientes
   - Reservas confirmadas
   - Actualización en tiempo real

### 2. **Búsqueda y Filtros**
   - Búsqueda por DNI del paciente (8 dígitos)
   - Filtro por estado (Pendiente, Confirmada, Completada)
   - Validación de formato de DNI
   - Limpieza de filtros con un click

### 3. **Tabla de Reservas Mejorada**
   - Información completa: ID, DNI, Paciente, Servicio, Médico, Fecha/Hora, Estado
   - Badges de colores según el estado
   - Hover effects para mejor UX
   - Diseño responsivo

### 4. **Modal de Cancelación Profesional**
   - Formulario modal con información de la reserva
   - Campo de motivo con validaciones:
     - Mínimo 10 caracteres
     - Máximo 500 caracteres
     - Contador de caracteres en tiempo real
   - Advertencias y confirmaciones
   - Cierre con ESC o click fuera

### 5. **Validaciones de Seguridad**
   - Autenticación requerida (solo empleados)
   - Validación de DNI (8 dígitos numéricos)
   - Validación de motivo de cancelación
   - Verificación de estado de reserva
   - Prevención de doble cancelación
   - Protección contra reservas completadas

### 6. **Notificaciones**
   - Mensajes de éxito/error
   - Notificaciones toast animadas
   - Feedback visual inmediato

## Instalación y Configuración

### 1. Cargar Datos de Prueba

Ejecuta el archivo SQL con los datos de prueba:

```bash
mysql -u tu_usuario -p CLINICA < datos_prueba_gestion_cancelaciones.sql
```

O desde MySQL Workbench o phpMyAdmin, importa el archivo:
```
datos_prueba_gestion_cancelaciones.sql
```

Este archivo incluye:
- 3 Departamentos, 3 Provincias, 5 Distritos
- 5 Especialidades médicas
- 6 Servicios
- 8 Pacientes con DNIs: 12345678, 23456789, 34567890, 45678901, 56789012, 67890123, 78901234, 89012345
- 5 Médicos con diferentes especialidades
- 24 Horarios disponibles
- 18 Programaciones
- 15 Reservas (10 activas para gestionar)

### 2. Verificar Rutas

Las rutas ya están configuradas en `routes/reservas.py`:
- `GET /reservas/gestionar-cancelaciones` - Página principal
- `GET /reservas/api/reservas-activas` - Obtener reservas (con filtro opcional por DNI)
- `POST /reservas/api/cancelar-reserva` - Cancelar una reserva

### 3. Acceso al Módulo

1. Inicia sesión como empleado
2. Navega a `/reservas/gestionar-cancelaciones`
3. La interfaz se cargará automáticamente

## Uso del Sistema

### Buscar Reservas

**Por DNI:**
1. Ingresa el DNI del paciente (8 dígitos)
2. Click en "Buscar" o presiona Enter
3. Se mostrarán solo las reservas de ese paciente

**Por Estado:**
1. Selecciona el estado en el filtro
2. Las reservas se filtran automáticamente

**Limpiar Filtros:**
- Click en "Limpiar" para volver a mostrar todas las reservas

### Cancelar una Reserva

1. Localiza la reserva en la tabla
2. Click en el botón "Cancelar" de la fila correspondiente
3. Se abrirá un modal mostrando:
   - Nombre del paciente
   - Servicio
   - Fecha y hora de la cita
4. Ingresa el motivo de cancelación (mínimo 10 caracteres)
5. El contador mostrará los caracteres ingresados:
   - Rojo: Menos de 10 caracteres (inválido)
   - Verde: 10-450 caracteres (válido)
   - Naranja: 451-500 caracteres (cerca del límite)
6. Click en "Confirmar Cancelación"
7. La reserva se cancelará y la tabla se actualizará automáticamente

### Estados de Reservas

- **Pendiente** (Amarillo): Reserva creada pero no confirmada
- **Confirmada** (Verde): Reserva confirmada por el paciente/empleado
- **Completada** (Azul): Cita ya realizada (no se puede cancelar)
- **Cancelada** (Rojo): Reserva cancelada (no aparece en lista activa)

## Estructura de Archivos

```
Proyecto-Ingenieria-y-calidad/
├── templates/
│   └── GestionarCancelaciones.html      # Interfaz mejorada
├── routes/
│   └── reservas.py                      # Rutas y APIs con validaciones
├── models/
│   └── reserva.py                       # Modelo de datos
├── datos_prueba_gestion_cancelaciones.sql  # Datos de prueba
└── README_GESTION_CANCELACIONES.md      # Este archivo
```

## APIs Disponibles

### GET `/reservas/api/reservas-activas`

Obtiene todas las reservas activas (no canceladas).

**Parámetros Query:**
- `dni` (opcional): DNI del paciente (8 dígitos)

**Respuesta:**
```json
{
  "reservas": [
    {
      "id_reserva": 1,
      "estado": "pendiente",
      "nombre_paciente": "Juan Carlos Pérez González",
      "documento_identidad": "12345678",
      "fecha_cita": "2025-11-03",
      "hora_inicio": "09:00:00",
      "hora_fin": "10:00:00",
      "servicio": "Consulta General",
      "nombre_empleado": "Luis Alberto González Vega"
    }
  ]
}
```

### POST `/reservas/api/cancelar-reserva`

Cancela una reserva específica.

**Body JSON:**
```json
{
  "id_reserva": 1,
  "motivo": "Paciente tuvo un inconveniente laboral urgente"
}
```

**Validaciones:**
- `id_reserva`: Requerido, debe ser un número válido
- `motivo`: Requerido, mínimo 10 caracteres, máximo 500 caracteres
- La reserva debe existir y no estar cancelada o completada

**Respuesta Exitosa:**
```json
{
  "success": true,
  "message": "Reserva cancelada exitosamente",
  "id_reserva": 1
}
```

**Respuesta de Error:**
```json
{
  "error": "Mensaje descriptivo del error"
}
```

## DNIs de Pacientes de Prueba

Puedes usar estos DNIs para probar la búsqueda:

| DNI | Nombre Completo | Reservas |
|-----|----------------|----------|
| 12345678 | Juan Carlos Pérez González | 2 |
| 23456789 | María Elena García Rojas | 2 |
| 34567890 | Carlos Alberto López Mendoza | 2 |
| 45678901 | Ana Sofía Martínez Cruz | 2 |
| 56789012 | Luis Fernando Rodríguez Silva | 1 |
| 67890123 | Sofía Isabella Torres Vargas | 1 |
| 78901234 | Pedro José Sánchez Ramírez | 1 |
| 89012345 | Carmen Rosa Flores Huamán | 1 |

## Características Técnicas

### Frontend
- **Framework CSS**: Tailwind CSS
- **Iconos**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JS (ES6+)
- **Características**:
  - Fetch API para llamadas asíncronas
  - DOM manipulation
  - Event listeners
  - Validaciones en tiempo real
  - Animaciones CSS

### Backend
- **Framework**: Flask (Python)
- **Base de Datos**: MySQL 8.x
- **Arquitectura**: MVC (Modelos, Vistas, Controladores)
- **Seguridad**:
  - Autenticación basada en sesión
  - Validación de datos en servidor
  - Prepared statements para prevenir SQL injection
  - Control de acceso por rol

### Modelos Utilizados
- `Reserva`: Gestión de reservas médicas
- `Paciente`: Información de pacientes
- `Empleado`: Información de médicos
- `Servicio`: Servicios médicos disponibles
- `Programacion`: Programación de horarios

## Mejoras Futuras Sugeridas

1. **Exportación de Datos**
   - Exportar lista de cancelaciones a PDF/Excel
   - Reportes de motivos de cancelación

2. **Notificaciones**
   - Enviar email/SMS al paciente cuando se cancela
   - Notificación al médico

3. **Auditoría**
   - Tabla de auditoría para rastrear cancelaciones
   - Historial de cambios

4. **Búsqueda Avanzada**
   - Búsqueda por rango de fechas
   - Búsqueda por médico
   - Búsqueda por servicio

5. **Reprogramación Directa**
   - Permitir reprogramar desde el mismo modal
   - Sugerir horarios disponibles

## Solución de Problemas

### No se cargan las reservas
- Verifica que los datos de prueba estén cargados
- Revisa la conexión a la base de datos en `bd.py`
- Verifica que estés autenticado como empleado

### Error al cancelar
- Asegúrate de ingresar al menos 10 caracteres en el motivo
- Verifica que la reserva no esté ya cancelada
- Comprueba que tengas permisos de empleado

### DNI no encontrado
- Verifica que el DNI tenga exactamente 8 dígitos
- Asegúrate de que el paciente exista en la base de datos
- Revisa que el paciente tenga reservas activas

## Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.

---

**Versión**: 1.0.0
**Última actualización**: Octubre 2025
**Desarrollado con**: Flask + MySQL + Tailwind CSS
