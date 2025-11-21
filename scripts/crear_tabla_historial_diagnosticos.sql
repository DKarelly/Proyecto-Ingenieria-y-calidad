-- =====================================================
-- Script: Creación de tabla para historial de diagnósticos
-- Propósito: Registrar todas las modificaciones realizadas a los diagnósticos
-- Fecha: 21 de Noviembre de 2025
-- =====================================================

-- Crear tabla para el historial de modificaciones de diagnósticos
CREATE TABLE IF NOT EXISTS historial_diagnosticos (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    diagnostico_anterior TEXT,
    observaciones_anterior TEXT,
    fecha_modificacion DATETIME NOT NULL,
    id_medico_modifica INT NOT NULL,
    FOREIGN KEY (id_cita) REFERENCES CITA(id_cita) ON DELETE CASCADE,
    FOREIGN KEY (id_medico_modifica) REFERENCES EMPLEADO(id_empleado) ON DELETE RESTRICT,
    INDEX idx_cita_fecha (id_cita, fecha_modificacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='Historial de modificaciones de diagnósticos médicos';

-- Agregar campo fecha_diagnostico a la tabla CITA si no existe
-- (para registrar cuándo se guardó el diagnóstico por primera vez)
ALTER TABLE CITA 
ADD COLUMN IF NOT EXISTS fecha_diagnostico DATETIME NULL
COMMENT 'Fecha y hora en que se registró el diagnóstico';

-- Crear índice para mejorar búsquedas por fecha
CREATE INDEX IF NOT EXISTS idx_fecha_diagnostico ON CITA(fecha_diagnostico);

-- Comentarios en las columnas existentes para documentar el sistema
ALTER TABLE CITA 
MODIFY COLUMN diagnostico TEXT 
COMMENT 'Diagnóstico médico - Validación: Solo se puede registrar desde hora inicio hasta medianoche del día de la cita';

ALTER TABLE CITA 
MODIFY COLUMN observaciones TEXT 
COMMENT 'Observaciones adicionales del diagnóstico';

-- Insertar comentario informativo
SELECT 'Tabla historial_diagnosticos creada exitosamente' AS Resultado;
SELECT 'Campo fecha_diagnostico agregado a tabla CITA' AS Resultado;

-- Mostrar estructura de las tablas
DESCRIBE historial_diagnosticos;
DESCRIBE CITA;
