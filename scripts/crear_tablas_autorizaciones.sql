-- Script para crear tablas de autorizaciones de exámenes y operaciones
-- Compatible con MySQL Workbench

USE `bd_calidad`;

-- Tabla para autorizar exámenes a pacientes después de un diagnóstico
DROP TABLE IF EXISTS `AUTORIZACION_EXAMEN`;
CREATE TABLE `AUTORIZACION_EXAMEN` (
  `id_autorizacion_examen` INT NOT NULL AUTO_INCREMENT,
  `id_cita` INT NOT NULL COMMENT 'Cita donde se autorizó el examen',
  `id_paciente` INT NOT NULL COMMENT 'Paciente autorizado',
  `id_empleado_autoriza` INT NOT NULL COMMENT 'Médico que autoriza',
  `id_servicio` INT NOT NULL COMMENT 'Servicio de examen autorizado',
  `estado` VARCHAR(20) NOT NULL DEFAULT 'Pendiente' COMMENT 'Pendiente, Programado, Completado, Cancelado',
  `fecha_autorizacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `observaciones` TEXT,
  `id_examen` INT DEFAULT NULL COMMENT 'ID del examen cuando se programa',
  PRIMARY KEY (`id_autorizacion_examen`),
  KEY `idx_cita` (`id_cita`),
  KEY `idx_paciente` (`id_paciente`),
  KEY `idx_empleado` (`id_empleado_autoriza`),
  KEY `idx_servicio` (`id_servicio`),
  KEY `idx_examen` (`id_examen`),
  CONSTRAINT `fk_autorizacion_examen_cita` FOREIGN KEY (`id_cita`) REFERENCES `CITA` (`id_cita`),
  CONSTRAINT `fk_autorizacion_examen_paciente` FOREIGN KEY (`id_paciente`) REFERENCES `PACIENTE` (`id_paciente`),
  CONSTRAINT `fk_autorizacion_examen_empleado` FOREIGN KEY (`id_empleado_autoriza`) REFERENCES `EMPLEADO` (`id_empleado`),
  CONSTRAINT `fk_autorizacion_examen_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `SERVICIO` (`id_servicio`),
  CONSTRAINT `fk_autorizacion_examen_examen` FOREIGN KEY (`id_examen`) REFERENCES `EXAMEN` (`id_examen`),
  CONSTRAINT `chk_autorizacion_examen_estado` CHECK (`estado` IN ('Pendiente', 'Programado', 'Completado', 'Cancelado'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla para autorizar operaciones a pacientes después de un diagnóstico
DROP TABLE IF EXISTS `AUTORIZACION_OPERACION`;
CREATE TABLE `AUTORIZACION_OPERACION` (
  `id_autorizacion_operacion` INT NOT NULL AUTO_INCREMENT,
  `id_cita` INT NOT NULL COMMENT 'Cita donde se autorizó la operación',
  `id_paciente` INT NOT NULL COMMENT 'Paciente autorizado',
  `id_empleado_autoriza` INT NOT NULL COMMENT 'Médico que autoriza',
  `id_empleado_asignado` INT DEFAULT NULL COMMENT 'Médico asignado para realizar la operación (puede ser el mismo o derivado)',
  `id_servicio` INT NOT NULL COMMENT 'Servicio de operación autorizado',
  `estado` VARCHAR(20) NOT NULL DEFAULT 'Pendiente' COMMENT 'Pendiente, Programado, Completado, Cancelado',
  `fecha_autorizacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `observaciones` TEXT,
  `id_operacion` INT DEFAULT NULL COMMENT 'ID de la operación cuando se programa',
  `es_derivacion` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Indica si la operación fue derivada a otro médico',
  PRIMARY KEY (`id_autorizacion_operacion`),
  KEY `idx_cita` (`id_cita`),
  KEY `idx_paciente` (`id_paciente`),
  KEY `idx_empleado_autoriza` (`id_empleado_autoriza`),
  KEY `idx_empleado_asignado` (`id_empleado_asignado`),
  KEY `idx_servicio` (`id_servicio`),
  KEY `idx_operacion` (`id_operacion`),
  CONSTRAINT `fk_autorizacion_operacion_cita` FOREIGN KEY (`id_cita`) REFERENCES `CITA` (`id_cita`),
  CONSTRAINT `fk_autorizacion_operacion_paciente` FOREIGN KEY (`id_paciente`) REFERENCES `PACIENTE` (`id_paciente`),
  CONSTRAINT `fk_autorizacion_operacion_empleado_autoriza` FOREIGN KEY (`id_empleado_autoriza`) REFERENCES `EMPLEADO` (`id_empleado`),
  CONSTRAINT `fk_autorizacion_operacion_empleado_asignado` FOREIGN KEY (`id_empleado_asignado`) REFERENCES `EMPLEADO` (`id_empleado`),
  CONSTRAINT `fk_autorizacion_operacion_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `SERVICIO` (`id_servicio`),
  CONSTRAINT `fk_autorizacion_operacion_operacion` FOREIGN KEY (`id_operacion`) REFERENCES `OPERACION` (`id_operacion`),
  CONSTRAINT `chk_autorizacion_operacion_estado` CHECK (`estado` IN ('Pendiente', 'Programado', 'Completado', 'Cancelado'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Índices para mejorar el rendimiento de las consultas
CREATE INDEX idx_autorizacion_examen_estado ON AUTORIZACION_EXAMEN(estado);
CREATE INDEX idx_autorizacion_operacion_estado ON AUTORIZACION_OPERACION(estado);
CREATE INDEX idx_autorizacion_examen_paciente_estado ON AUTORIZACION_EXAMEN(id_paciente, estado);
CREATE INDEX idx_autorizacion_operacion_paciente_estado ON AUTORIZACION_OPERACION(id_paciente, estado);
