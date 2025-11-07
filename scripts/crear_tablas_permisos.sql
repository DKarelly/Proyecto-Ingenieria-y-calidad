-- Script para agregar funcionalidad de permisos al sistema
-- Ejecutar este script después de bd_clinica_05_11.sql

-- 1. Agregar descripción a la tabla ROL
ALTER TABLE `ROL` 
ADD COLUMN `descripcion` TEXT AFTER `nombre`;

-- Actualizar roles existentes con descripciones
UPDATE `ROL` SET `descripcion` = 'Acceso total al sistema con permisos de administración' WHERE `nombre` = 'Administrador';
UPDATE `ROL` SET `descripcion` = 'Gestión de consultas médicas y atención de pacientes' WHERE `nombre` = 'Médico';
UPDATE `ROL` SET `descripcion` = 'Gestión de citas y atención en recepción' WHERE `nombre` = 'Recepcionista';
UPDATE `ROL` SET `descripcion` = 'Gestión de medicamentos y farmacia' WHERE `nombre` = 'Farmacéutico';
UPDATE `ROL` SET `descripcion` = 'Gestión de exámenes y análisis de laboratorio' WHERE `nombre` = 'Laboratorista';

-- 2. Crear tabla de PERMISOS
DROP TABLE IF EXISTS `PERMISO`;
CREATE TABLE `PERMISO` (
  `id_permiso` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `codigo` VARCHAR(50) NOT NULL,
  `descripcion` TEXT,
  `modulo` VARCHAR(50) NOT NULL,
  `estado` VARCHAR(20) DEFAULT 'Activo',
  PRIMARY KEY (`id_permiso`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3. Crear tabla de relación ROL_PERMISO
DROP TABLE IF EXISTS `ROL_PERMISO`;
CREATE TABLE `ROL_PERMISO` (
  `id_rol` INT NOT NULL,
  `id_permiso` INT NOT NULL,
  PRIMARY KEY (`id_rol`, `id_permiso`),
  KEY `id_permiso` (`id_permiso`),
  CONSTRAINT `ROL_PERMISO_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `ROL` (`id_rol`) ON DELETE CASCADE,
  CONSTRAINT `ROL_PERMISO_ibfk_2` FOREIGN KEY (`id_permiso`) REFERENCES `PERMISO` (`id_permiso`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4. Insertar permisos predefinidos

-- Módulo: Administración
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Ver Panel Administración', 'admin.panel.ver', 'Permite acceder al panel de administración', 'Administración'),
('Gestionar Programación', 'admin.programacion.gestionar', 'Permite crear y modificar programaciones', 'Administración'),
('Gestionar Recursos Físicos', 'admin.recursos.gestionar', 'Permite administrar recursos físicos', 'Administración'),
('Gestionar Horarios', 'admin.horarios.gestionar', 'Permite configurar horarios laborables', 'Administración'),
('Gestionar Bloqueos', 'admin.bloqueos.gestionar', 'Permite bloquear y desbloquear horarios', 'Administración'),
('Consultar Agenda Médica', 'admin.agenda.consultar', 'Permite consultar la agenda médica', 'Administración'),
('Gestionar Catálogo de Servicios', 'admin.catalogo.gestionar', 'Permite administrar el catálogo de servicios', 'Administración');

-- Módulo: Reservas
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Ver Panel Reservas', 'reservas.panel.ver', 'Permite acceder al panel de reservas', 'Reservas'),
('Generar Reserva', 'reservas.generar', 'Permite crear nuevas reservas', 'Reservas'),
('Consultar Disponibilidad', 'reservas.disponibilidad.consultar', 'Permite consultar disponibilidad de servicios', 'Reservas'),
('Reprogramar Reserva', 'reservas.reprogramar', 'Permite reprogramar citas existentes', 'Reservas'),
('Gestionar Cancelaciones', 'reservas.cancelaciones.gestionar', 'Permite cancelar reservas', 'Reservas'),
('Gestionar Confirmaciones', 'reservas.confirmaciones.gestionar', 'Permite confirmar citas', 'Reservas');

-- Módulo: Cuentas
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Ver Panel Cuentas', 'cuentas.panel.ver', 'Permite acceder al panel de cuentas', 'Cuentas'),
('Gestionar Cuentas Internas', 'cuentas.internas.gestionar', 'Permite administrar cuentas de empleados', 'Cuentas'),
('Gestionar Roles y Permisos', 'cuentas.roles.gestionar', 'Permite configurar roles y permisos', 'Cuentas'),
('Gestionar Datos Pacientes', 'cuentas.pacientes.gestionar', 'Permite administrar datos de pacientes', 'Cuentas');

-- Módulo: Notificaciones
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Ver Panel Notificaciones', 'notificaciones.panel.ver', 'Permite acceder al panel de notificaciones', 'Notificaciones'),
('Gestionar Recordatorios', 'notificaciones.recordatorios.gestionar', 'Permite configurar recordatorios automáticos', 'Notificaciones'),
('Gestionar Notificaciones de Cambios', 'notificaciones.cambios.gestionar', 'Permite enviar notificaciones de cambios', 'Notificaciones');

-- Módulo: Seguridad
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Ver Panel Seguridad', 'seguridad.panel.ver', 'Permite acceder al panel de seguridad', 'Seguridad'),
('Consultar Actividad', 'seguridad.actividad.consultar', 'Permite consultar logs de actividad', 'Seguridad'),
('Generar Incidencia', 'seguridad.incidencias.generar', 'Permite crear nuevas incidencias', 'Seguridad'),
('Consultar Incidencia', 'seguridad.incidencias.consultar', 'Permite ver incidencias registradas', 'Seguridad'),
('Asignar Responsable', 'seguridad.incidencias.asignar', 'Permite asignar responsables a incidencias', 'Seguridad'),
('Generar Informe', 'seguridad.incidencias.informe', 'Permite generar informes de incidencias', 'Seguridad');

-- Módulo: Reportes
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Ver Panel Reportes', 'reportes.panel.ver', 'Permite acceder al panel de reportes', 'Reportes'),
('Consultar por Categoría', 'reportes.categoria.consultar', 'Permite generar reportes por categoría', 'Reportes'),
('Generar Reporte de Actividad', 'reportes.actividad.generar', 'Permite generar reportes de actividad', 'Reportes'),
('Generar Ocupación de Recursos', 'reportes.ocupacion.generar', 'Permite generar reportes de ocupación', 'Reportes');

-- Módulo: Farmacia
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Ver Panel Farmacia', 'farmacia.panel.ver', 'Permite acceder al panel de farmacia', 'Farmacia'),
('Gestionar Entrega Medicamentos', 'farmacia.entrega.gestionar', 'Permite registrar entregas de medicamentos', 'Farmacia'),
('Gestionar Recepción Medicamentos', 'farmacia.recepcion.gestionar', 'Permite registrar recepciones de medicamentos', 'Farmacia');

-- Módulo: Exámenes y Operaciones
INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`) VALUES
('Generar Examen', 'examenes.generar', 'Permite registrar nuevos exámenes', 'Exámenes'),
('Gestionar Exámenes', 'examenes.gestionar', 'Permite administrar exámenes existentes', 'Exámenes'),
('Generar Operación', 'operaciones.generar', 'Permite registrar nuevas operaciones', 'Operaciones'),
('Gestionar Operaciones', 'operaciones.gestionar', 'Permite administrar operaciones existentes', 'Operaciones');

-- 5. Asignar todos los permisos al rol de Administrador
INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
SELECT 1, `id_permiso` FROM `PERMISO`;

-- 6. Asignar permisos al rol de Médico
INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
SELECT 2, `id_permiso` FROM `PERMISO` 
WHERE `codigo` IN (
    'admin.agenda.consultar',
    'reservas.panel.ver',
    'reservas.generar',
    'reservas.disponibilidad.consultar',
    'reservas.reprogramar',
    'notificaciones.panel.ver',
    'examenes.generar',
    'examenes.gestionar',
    'operaciones.generar',
    'operaciones.gestionar',
    'reportes.panel.ver',
    'reportes.actividad.generar'
);

-- 7. Asignar permisos al rol de Recepcionista
INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
SELECT 3, `id_permiso` FROM `PERMISO` 
WHERE `codigo` IN (
    'reservas.panel.ver',
    'reservas.generar',
    'reservas.disponibilidad.consultar',
    'reservas.reprogramar',
    'reservas.cancelaciones.gestionar',
    'reservas.confirmaciones.gestionar',
    'cuentas.panel.ver',
    'cuentas.pacientes.gestionar',
    'notificaciones.panel.ver',
    'notificaciones.recordatorios.gestionar'
);

-- 8. Asignar permisos al rol de Farmacéutico
INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
SELECT 4, `id_permiso` FROM `PERMISO` 
WHERE `codigo` IN (
    'farmacia.panel.ver',
    'farmacia.entrega.gestionar',
    'farmacia.recepcion.gestionar',
    'notificaciones.panel.ver'
);

-- 9. Asignar permisos al rol de Laboratorista
INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
SELECT 5, `id_permiso` FROM `PERMISO` 
WHERE `codigo` IN (
    'examenes.generar',
    'examenes.gestionar',
    'notificaciones.panel.ver',
    'reportes.panel.ver'
);
