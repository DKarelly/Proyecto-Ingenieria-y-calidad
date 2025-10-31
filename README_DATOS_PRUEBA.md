# Guía de Datos de Prueba - Sistema de Clínica

## Descripción

El archivo `datos_prueba_gestion_cancelaciones.sql` contiene datos de prueba completos para verificar todas las funcionalidades de los módulos de **Reservas** y **Notificaciones**.

## Contenido del Archivo

### 1. Datos Geográficos
- 3 Departamentos
- 3 Provincias
- 5 Distritos

### 2. Roles y Usuarios
- **6 Roles:**
  - Administrador (ID: 1)
  - Médico General (ID: 2)
  - Médico Especialista (ID: 3)
  - Enfermero/a (ID: 4)
  - Recepcionista (ID: 5)
  - Técnico de Laboratorio (ID: 6)

### 3. Especialidades y Servicios
- **7 Especialidades Médicas:**
  - Medicina General
  - Cardiología
  - Pediatría
  - Traumatología
  - Dermatología
  - Oftalmología
  - Neurología

- **5 Tipos de Servicio**
- **15 Servicios** distribuidos por especialidad

### 4. Usuarios y Empleados
- **10 Pacientes** con datos completos
- **10 Empleados:**
  - 1 Administrador
  - 7 Médicos (2 Médicos Generales + 5 Médicos Especialistas)
  - 3 Personal no médico (Enfermera, Recepcionista, Técnico)

### 5. Horarios y Programaciones
- **31 Horarios** distribuidos entre los médicos
- **25 Programaciones** para diferentes servicios

### 6. Reservas
- **23 Reservas en total:**
  - 7 Pendientes (para confirmar)
  - 7 Confirmadas (listas para atención)
  - 5 Completadas (atenciones pasadas)
  - 4 Canceladas (para pruebas de gestión)

### 7. Notificaciones
- **6 Tipos de Notificación**
- **4 Canales** (Email, SMS, WhatsApp, Push)
- **13 Notificaciones:**
  - 6 Enviadas
  - 4 Pendientes
  - 2 Fallidas (para pruebas de reenvío)

## Cómo Usar el Archivo

### Opción 1: Ejecutar desde MySQL Workbench
1. Abre MySQL Workbench
2. Conecta a tu servidor MySQL
3. Abre el archivo `datos_prueba_gestion_cancelaciones.sql`
4. Ejecuta todo el script (Ctrl + Shift + Enter)

### Opción 2: Ejecutar desde línea de comandos
```bash
mysql -u usuario -p CLINICA < datos_prueba_gestion_cancelaciones.sql
```

### Opción 3: Ejecutar secciones específicas
Puedes ejecutar solo las secciones que necesites. El archivo está bien organizado por secciones numeradas.

## Consultas de Verificación Incluidas

El archivo incluye 10 consultas SELECT al final que te permiten verificar:

1. **Listado de Médicos** - Solo muestra empleados con roles 2 o 3 y especialidad asignada
2. **Empleados No Médicos** - Personal que NO debe aparecer en "Consultar Servicios por Médico"
3. **Servicios por Especialidad** - Servicios disponibles para cada especialidad
4. **Reservas Activas** - Para pruebas de Gestión de Cancelaciones
5. **Disponibilidad de Horarios** - Horarios disponibles para agendar
6. **Notificaciones por Estado** - Resumen de notificaciones
7. **Notificaciones Pendientes** - Para Gestión de Recordatorios
8. **Reservas para Reprogramar** - Reservas que pueden ser reprogramadas
9. **Servicios Más Solicitados** - Reporte estadístico
10. **Confirmaciones Pendientes** - Citas que requieren confirmación

## Verificación de Funcionalidades

### Panel de Reservas

#### 1. Consultar Servicios por Médico
- **URL:** `/reservas/consultar-servicio-medico`
- **Verificación:** Debe mostrar SOLO 7 médicos (no recepcionistas ni enfermeras)
- **Consulta de verificación:** CONSULTA 1 y 2 del script

#### 2. Consultar Disponibilidad
- **URL:** `/reservas/consultar-disponibilidad`
- **Verificación:** Debe mostrar 31 horarios disponibles
- **Consulta de verificación:** CONSULTA 5

#### 3. Consultar Servicios por Tipo
- **URL:** `/reservas/consultar-servicio-tipo`
- **Verificación:** Debe mostrar 5 tipos de servicio con 15 servicios totales
- **Consulta de verificación:** CONSULTA 3

#### 4. Generar Reserva
- **URL:** `/reservas/generar-reserva`
- **Datos de prueba:** Usar cualquiera de los 10 pacientes (DNI: 12345678 a 01234567)

#### 5. Reprogramar Reserva
- **URL:** `/reservas/reprogramar-reserva`
- **Datos de prueba:** Usar DNI de paciente para buscar reservas activas
- **Consulta de verificación:** CONSULTA 8

#### 6. Gestionar Cancelaciones
- **URL:** `/reservas/gestionar-cancelaciones`
- **Datos de prueba:**
  - 14 reservas activas disponibles para cancelar
  - 4 reservas ya canceladas (para referencia)
- **Consulta de verificación:** CONSULTA 4

#### 7. Reporte de Servicios
- **URL:** `/reservas/reporte-servicios`
- **Verificación:** Debe mostrar estadísticas de servicios
- **Consulta de verificación:** CONSULTA 9

### Panel de Notificaciones

#### 1. Gestionar Confirmación de Citas
- **URL:** `/notificaciones/gestionar-confirmacion`
- **Datos de prueba:** 7 citas pendientes de confirmación
- **Consulta de verificación:** CONSULTA 10

#### 2. Gestionar Recordatorios
- **URL:** `/notificaciones/gestionar-recordatorios`
- **Datos de prueba:**
  - 4 notificaciones pendientes de envío
  - 2 notificaciones fallidas para reenviar
- **Consulta de verificación:** CONSULTA 7

## Datos de Ejemplo para Pruebas

### Pacientes (DNI para búsqueda)
- Juan Carlos Pérez González: `12345678`
- María Elena García Rojas: `23456789`
- Carlos Alberto López Mendoza: `34567890`
- Ana Sofía Martínez Cruz: `45678901`
- Luis Fernando Rodríguez Silva: `56789012`

### Médicos (con especialidad)
- Dr. Luis Alberto González Vega (Medicina General)
- Dra. Ana Patricia Martínez Ruiz (Cardiología)
- Dr. Roberto Carlos Ramírez Díaz (Pediatría)
- Dra. Laura Beatriz Castro Paredes (Traumatología)
- Dr. Miguel Ángel Morales Soto (Medicina General)
- Dra. Patricia Elena Silva Campos (Dermatología)
- Dr. Fernando José Vargas Ramos (Oftalmología)

### Personal NO Médico (NO deben aparecer en "Consultar por Médico")
- Rosa María López Fernández (Enfermera)
- Juan Carlos Torres Mendoza (Recepcionista)
- Mario Alberto Rojas Paz (Técnico de Laboratorio)

## Notas Importantes

1. **Filtrado de Médicos:** El sistema filtra correctamente solo empleados con `id_rol IN (2, 3)` y `id_especialidad IS NOT NULL`

2. **Servicios por Especialidad:** Cada médico solo puede ver/ofrecer servicios de su especialidad asignada

3. **Estados de Reservas:**
   - `pendiente`: Recién creada, requiere confirmación
   - `confirmada`: Confirmada, lista para atención
   - `completada`: Atención ya realizada
   - `cancelada`: Reserva cancelada (no aparece en listados activos)

4. **Estados de Notificaciones:**
   - `pendiente`: Programada para envío futuro
   - `enviada`: Enviada exitosamente
   - `fallida`: Falló el envío, requiere reenvío

## Solución de Problemas

### Si aparecen recepcionistas en "Consultar por Médico"
1. Verificar que el método `Empleado.obtener_medicos()` existe en `models/empleado.py`
2. Verificar que la ruta usa `Empleado.obtener_medicos()` y no `Empleado.obtener_todos()`
3. Ejecutar CONSULTA 1 y 2 del script para verificar los datos

### Si no aparecen servicios para un médico
1. Verificar que el médico tiene `id_especialidad` asignado
2. Verificar que existen servicios activos para esa especialidad
3. Ejecutar CONSULTA 3 para ver servicios por especialidad

### Si las fechas están desactualizadas
- Las fechas están configuradas para Noviembre 2025
- Puedes actualizar las fechas en las secciones 6 (HORARIOS) y 7 (RESERVAS) según necesites

## Contacto y Soporte

Para cualquier duda o problema con los datos de prueba, revisar:
- Archivo: `datos_prueba_gestion_cancelaciones.sql`
- Modelos: `models/empleado.py`, `models/servicio.py`
- Rutas: `routes/reservas.py`, `routes/notificaciones.py`
