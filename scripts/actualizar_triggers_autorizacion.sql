-- Script para actualizar los triggers de AUTORIZACION_PROCEDIMIENTO
-- Cambiar tipo_procedimiento por id_tipo_servicio
-- EXAMEN = 4, OPERACION = 2

-- Eliminar triggers antiguos
DROP TRIGGER IF EXISTS trg_autorizacion_before_insert;
DROP TRIGGER IF EXISTS trg_autorizacion_before_update;

-- Recrear trigger BEFORE INSERT usando id_tipo_servicio
DELIMITER $$
CREATE TRIGGER trg_autorizacion_before_insert
BEFORE INSERT ON AUTORIZACION_PROCEDIMIENTO
FOR EACH ROW
BEGIN
  -- id_tipo_servicio = 4 es EXAMEN
  -- Los exámenes no deben tener especialidad requerida
  IF NEW.id_tipo_servicio = 4 AND NEW.id_especialidad_requerida IS NOT NULL THEN 
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Los exámenes no deben tener especialidad requerida';
  END IF;
END$$
DELIMITER ;

-- Recrear trigger BEFORE UPDATE usando id_tipo_servicio
DELIMITER $$
CREATE TRIGGER trg_autorizacion_before_update
BEFORE UPDATE ON AUTORIZACION_PROCEDIMIENTO
FOR EACH ROW
BEGIN
  -- id_tipo_servicio = 4 es EXAMEN
  -- Los exámenes no deben tener especialidad requerida
  IF NEW.id_tipo_servicio = 4 AND NEW.id_especialidad_requerida IS NOT NULL THEN 
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Los exámenes no deben tener especialidad requerida';
  END IF;
END$$
DELIMITER ;
