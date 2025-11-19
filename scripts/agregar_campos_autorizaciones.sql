-- Script para agregar nuevos campos a la tabla AUTORIZACION_PROCEDIMIENTO
-- Soluciona puntos 1.1 y 1.3 del documento CASOS_NO_CONTEMPLADOS_AUTORIZACIONES.md
-- 
-- Para ejecutar este script desde PowerShell en Windows:
-- mysql -u usuario -p nombre_bd < scripts/agregar_campos_autorizaciones.sql
--
-- O desde MySQL CLI:
-- mysql> source scripts/agregar_campos_autorizaciones.sql;

-- Agregar campo fecha_vencimiento (7 días desde la autorización por defecto)
ALTER TABLE AUTORIZACION_PROCEDIMIENTO 
ADD COLUMN fecha_vencimiento DATETIME NULL COMMENT 'Fecha de vencimiento de la autorización (7 días desde emisión)';

-- Agregar campo fecha_uso (cuándo fue utilizada la autorización)
ALTER TABLE AUTORIZACION_PROCEDIMIENTO 
ADD COLUMN fecha_uso DATETIME NULL COMMENT 'Fecha en que se utilizó/consumió la autorización';

-- Agregar campo id_reserva_generada (vínculo con la reserva/examen/operación generada)
ALTER TABLE AUTORIZACION_PROCEDIMIENTO 
ADD COLUMN id_reserva_generada INT NULL COMMENT 'ID de la reserva/procedimiento generado con esta autorización';

-- Crear tabla de auditoría para cambios en autorizaciones (punto 1.2)
CREATE TABLE IF NOT EXISTS AUTORIZACION_PROCEDIMIENTO_AUDITORIA (
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
    id_autorizacion INT NOT NULL,
    campo_modificado VARCHAR(100) NOT NULL,
    valor_anterior TEXT NULL,
    valor_nuevo TEXT NULL,
    id_usuario_modifica INT NOT NULL,
    fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT NULL,
    FOREIGN KEY (id_autorizacion) REFERENCES AUTORIZACION_PROCEDIMIENTO(id_autorizacion),
    FOREIGN KEY (id_usuario_modifica) REFERENCES USUARIO(id_usuario),
    INDEX idx_autorizacion (id_autorizacion),
    INDEX idx_fecha (fecha_modificacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Auditoría de cambios en autorizaciones de procedimientos';

-- Actualizar autorizaciones existentes con fecha de vencimiento (7 días desde la creación)
UPDATE AUTORIZACION_PROCEDIMIENTO 
SET fecha_vencimiento = DATE_ADD(fecha_autorizacion, INTERVAL 7 DAY)
WHERE fecha_vencimiento IS NULL;

-- Crear índices para optimizar consultas
CREATE INDEX idx_fecha_vencimiento ON AUTORIZACION_PROCEDIMIENTO(fecha_vencimiento);
CREATE INDEX idx_fecha_uso ON AUTORIZACION_PROCEDIMIENTO(fecha_uso);
CREATE INDEX idx_reserva_generada ON AUTORIZACION_PROCEDIMIENTO(id_reserva_generada);

-- Agregar estado VENCIDA al ENUM de estado
ALTER TABLE AUTORIZACION_PROCEDIMIENTO 
MODIFY COLUMN estado ENUM('PENDIENTE', 'APROBADA', 'RECHAZADA', 'COMPLETADA', 'VENCIDA') DEFAULT 'PENDIENTE';

-- Crear vista para autorizaciones activas (no vencidas, no usadas)
CREATE OR REPLACE VIEW v_autorizaciones_activas AS
SELECT 
    ap.*,
    CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
    p.documento_identidad,
    CONCAT(med_aut.nombres, ' ', med_aut.apellidos) as medico_autoriza,
    esp_aut.nombre as especialidad_autoriza,
    CONCAT(med_asig.nombres, ' ', med_asig.apellidos) as medico_asignado,
    esp_req.nombre as especialidad_requerida,
    s.nombre as servicio_nombre,
    DATEDIFF(ap.fecha_vencimiento, NOW()) as dias_restantes
FROM AUTORIZACION_PROCEDIMIENTO ap
INNER JOIN PACIENTE p ON ap.id_paciente = p.id_paciente
INNER JOIN EMPLEADO med_aut ON ap.id_medico_autoriza = med_aut.id_empleado
INNER JOIN SERVICIO s ON ap.id_servicio = s.id_servicio
LEFT JOIN ESPECIALIDAD esp_aut ON med_aut.id_especialidad = esp_aut.id_especialidad
LEFT JOIN EMPLEADO med_asig ON ap.id_medico_asignado = med_asig.id_empleado
LEFT JOIN ESPECIALIDAD esp_req ON ap.id_especialidad_requerida = esp_req.id_especialidad
WHERE ap.estado = 'PENDIENTE'
  AND (ap.fecha_vencimiento IS NULL OR ap.fecha_vencimiento > NOW())
  AND ap.id_reserva_generada IS NULL;

-- Comentarios explicativos
SELECT 'Script ejecutado exitosamente' as resultado;
SELECT 'Nuevos campos agregados: fecha_vencimiento, fecha_uso, id_reserva_generada' as info;
SELECT 'Tabla de auditoría creada: AUTORIZACION_PROCEDIMIENTO_AUDITORIA' as info;
SELECT 'Nuevo estado agregado: VENCIDA' as info;
SELECT 'Vista creada: v_autorizaciones_activas' as info;
