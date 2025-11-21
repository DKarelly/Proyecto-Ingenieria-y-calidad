-- Script para agregar columna tipo_solicitud a la tabla SOLICITUD
-- Fecha: 21/11/2025
-- Descripción: Permite diferenciar entre solicitudes de Cancelación y Reprogramación

USE clinica;

-- Agregar columna tipo_solicitud
ALTER TABLE SOLICITUD 
ADD COLUMN tipo_solicitud VARCHAR(20) NOT NULL DEFAULT 'Cancelación' 
AFTER id_reserva;

-- Actualizar solicitudes existentes
-- Las que tienen nueva_programacion_id son reprogramaciones
UPDATE SOLICITUD 
SET tipo_solicitud = 'Reprogramación' 
WHERE nueva_programacion_id IS NOT NULL;

-- Las que no tienen nueva_programacion_id son cancelaciones
UPDATE SOLICITUD 
SET tipo_solicitud = 'Cancelación' 
WHERE nueva_programacion_id IS NULL;

-- Agregar constraint para validar solo estos dos valores
ALTER TABLE SOLICITUD 
ADD CONSTRAINT chk_tipo_solicitud 
CHECK (tipo_solicitud IN ('Cancelación', 'Reprogramación'));

-- Actualizar también el constraint de estado para incluir 'Completada'
-- Primero eliminar el constraint antiguo (solo si existe)
ALTER TABLE SOLICITUD 
DROP CHECK chk_sol_estado;

-- Agregar el nuevo constraint con 'Completada'
ALTER TABLE SOLICITUD 
ADD CONSTRAINT chk_sol_estado 
CHECK (estado IN ('Pendiente', 'Aprobada', 'Rechazada', 'Completada'));

-- Verificar cambios
SELECT 
    id_solicitud,
    id_reserva,
    tipo_solicitud,
    estado,
    nueva_programacion_id,
    motivo,
    fecha_solicitud
FROM SOLICITUD
ORDER BY id_solicitud DESC
LIMIT 10;
