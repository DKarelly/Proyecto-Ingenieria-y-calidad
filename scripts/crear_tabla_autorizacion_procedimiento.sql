-- Script para crear la tabla de autorizaciones de procedimientos médicos
-- Permite que un médico autorice a un paciente a realizar exámenes u operaciones

DROP TABLE IF EXISTS `AUTORIZACION_PROCEDIMIENTO`;

CREATE TABLE `AUTORIZACION_PROCEDIMIENTO` (
  `id_autorizacion` INT NOT NULL AUTO_INCREMENT,
  `id_cita` INT NOT NULL,
  `id_paciente` INT NOT NULL,
  `id_medico_autoriza` INT NOT NULL,
  `tipo_procedimiento` ENUM('EXAMEN', 'OPERACION') NOT NULL,
  `id_servicio` INT NOT NULL,
  `id_especialidad_requerida` INT NULL,
  `id_medico_asignado` INT NULL,
  `fecha_autorizacion` DATETIME NOT NULL,
  `fecha_actualizacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id_autorizacion`),
  
  KEY `idx_cita` (`id_cita`),
  KEY `idx_paciente` (`id_paciente`),
  KEY `idx_medico_autoriza` (`id_medico_autoriza`),
  KEY `idx_medico_asignado` (`id_medico_asignado`),
  KEY `idx_tipo_procedimiento` (`tipo_procedimiento`),
  KEY `idx_paciente_tipo` (`id_paciente`, `tipo_procedimiento`),
  KEY `idx_especialidad_requerida` (`id_especialidad_requerida`),
  KEY `idx_servicio` (`id_servicio`),
  
  CONSTRAINT `fk_autorizacion_cita` 
    FOREIGN KEY (`id_cita`) REFERENCES `CITA` (`id_cita`) ON DELETE CASCADE,
  
  CONSTRAINT `fk_autorizacion_paciente` 
    FOREIGN KEY (`id_paciente`) REFERENCES `PACIENTE` (`id_paciente`) ON DELETE CASCADE,
  
  CONSTRAINT `fk_autorizacion_medico_autoriza` 
    FOREIGN KEY (`id_medico_autoriza`) REFERENCES `EMPLEADO` (`id_empleado`) ON DELETE RESTRICT,
  
  CONSTRAINT `fk_autorizacion_medico_asignado` 
    FOREIGN KEY (`id_medico_asignado`) REFERENCES `EMPLEADO` (`id_empleado`) ON DELETE SET NULL,
    
  CONSTRAINT `fk_autorizacion_especialidad` 
    FOREIGN KEY (`id_especialidad_requerida`) REFERENCES `ESPECIALIDAD` (`id_especialidad`) ON DELETE SET NULL,
  
  CONSTRAINT `fk_autorizacion_servicio` 
    FOREIGN KEY (`id_servicio`) REFERENCES `SERVICIO` (`id_servicio`) ON DELETE RESTRICT,
  
  CONSTRAINT `chk_especialidad_operacion` 
    CHECK (
      (tipo_procedimiento = 'EXAMEN' AND id_especialidad_requerida IS NULL) OR
      (tipo_procedimiento = 'OPERACION')
    )
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX `idx_paciente_tipo` ON `AUTORIZACION_PROCEDIMIENTO` (`id_paciente`, `tipo_procedimiento`);


