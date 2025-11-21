-- Script para corregir el campo 'tipo' en la tabla RESERVA
-- Basado en el id_tipo_servicio de la programación asociada
-- 
-- Mapeo correcto:
-- tipo = 1: Consultas Médicas (id_tipo_servicio = 1)
-- tipo = 2: Operaciones (id_tipo_servicio = 2)
-- tipo = 3: Exámenes (id_tipo_servicio = 4)

USE bd_calidad;

-- Mostrar estado ANTES de la corrección
SELECT 'ESTADO ANTES DE LA CORRECCIÓN' as '';
SELECT 
    r.tipo as tipo_actual,
    ts.id_tipo_servicio,
    ts.nombre as tipo_servicio,
    COUNT(*) as cantidad_reservas
FROM RESERVA r
INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
GROUP BY r.tipo, ts.id_tipo_servicio, ts.nombre
ORDER BY r.tipo, ts.id_tipo_servicio;

-- Tabla temporal para guardar los cambios que se van a realizar
CREATE TEMPORARY TABLE cambios_reserva AS
SELECT 
    r.id_reserva,
    r.tipo as tipo_anterior,
    CASE 
        WHEN s.id_tipo_servicio = 2 THEN 2  -- Operaciones
        WHEN s.id_tipo_servicio = 4 THEN 3  -- Exámenes
        ELSE 1                              -- Consultas médicas (por defecto)
    END as tipo_nuevo,
    s.nombre as servicio,
    ts.nombre as tipo_servicio
FROM RESERVA r
INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
WHERE r.tipo != CASE 
    WHEN s.id_tipo_servicio = 2 THEN 2
    WHEN s.id_tipo_servicio = 4 THEN 3
    ELSE 1
END;

-- Mostrar las reservas que se van a corregir
SELECT 'RESERVAS QUE SERÁN CORREGIDAS' as '';
SELECT 
    id_reserva,
    servicio,
    tipo_servicio,
    tipo_anterior,
    tipo_nuevo,
    CASE tipo_nuevo
        WHEN 1 THEN 'Consulta Médica'
        WHEN 2 THEN 'Operación'
        WHEN 3 THEN 'Examen'
    END as descripcion_tipo_nuevo
FROM cambios_reserva
ORDER BY id_reserva;

-- Contar cuántas reservas se van a modificar
SELECT 'RESUMEN DE CAMBIOS' as '';
SELECT 
    COUNT(*) as total_reservas_a_corregir,
    SUM(CASE WHEN tipo_nuevo = 2 THEN 1 ELSE 0 END) as cambios_a_operacion,
    SUM(CASE WHEN tipo_nuevo = 3 THEN 1 ELSE 0 END) as cambios_a_examen
FROM cambios_reserva;

-- Realizar la actualización
UPDATE RESERVA r
INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
SET r.tipo = CASE 
    WHEN s.id_tipo_servicio = 2 THEN 2  -- Operaciones
    WHEN s.id_tipo_servicio = 4 THEN 3  -- Exámenes
    ELSE 1                              -- Consultas médicas
END
WHERE r.tipo != CASE 
    WHEN s.id_tipo_servicio = 2 THEN 2
    WHEN s.id_tipo_servicio = 4 THEN 3
    ELSE 1
END;

-- Mostrar el resultado de la actualización
SELECT 'RESULTADO DE LA ACTUALIZACIÓN' as '';
SELECT ROW_COUNT() as reservas_actualizadas;

-- Mostrar estado DESPUÉS de la corrección
SELECT 'ESTADO DESPUÉS DE LA CORRECCIÓN' as '';
SELECT 
    r.tipo,
    CASE r.tipo
        WHEN 1 THEN 'Consulta Médica'
        WHEN 2 THEN 'Operación'
        WHEN 3 THEN 'Examen'
    END as descripcion_tipo,
    ts.id_tipo_servicio,
    ts.nombre as tipo_servicio,
    COUNT(*) as cantidad_reservas
FROM RESERVA r
INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
GROUP BY r.tipo, ts.id_tipo_servicio, ts.nombre
ORDER BY r.tipo, ts.id_tipo_servicio;

-- Verificar que no haya inconsistencias
SELECT 'VERIFICACIÓN FINAL - NO DEBERÍAN APARECER REGISTROS' as '';
SELECT 
    r.id_reserva,
    r.tipo as tipo_reserva,
    s.id_tipo_servicio,
    ts.nombre as tipo_servicio,
    s.nombre as servicio
FROM RESERVA r
INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
WHERE (r.tipo = 2 AND s.id_tipo_servicio != 2)  -- tipo=2 debe ser id_tipo_servicio=2
   OR (r.tipo = 3 AND s.id_tipo_servicio != 4)  -- tipo=3 debe ser id_tipo_servicio=4
   OR (r.tipo = 1 AND s.id_tipo_servicio IN (2, 4));  -- tipo=1 no debe ser operación ni examen

SELECT '✅ SCRIPT COMPLETADO EXITOSAMENTE' as '';
