-- ==============================================================
-- SCRIPT: Inserts de Programaciones para Operaciones, Exámenes y Citas Médicas
-- Fecha: 2025-11-25
-- ==============================================================
-- Este script crea programaciones validando los horarios existentes de los médicos
-- TIPO_SERVICIO:
--   1 = Servicios de Consulta (Citas Médicas)
--   2 = Operación
--   3 = Farmacia
--   4 = Exámenes y Diagnóstico
-- ==============================================================

USE bd_calidad;

-- ==============================================================
-- PRIMERO: Verificar los horarios existentes de los médicos activos
-- ==============================================================
SELECT 
    h.id_horario,
    h.id_empleado,
    CONCAT(e.nombres, ' ', e.apellidos) as medico,
    esp.nombre as especialidad,
    h.fecha,
    h.hora_inicio,
    h.hora_fin,
    h.activo
FROM HORARIO h
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
WHERE e.id_rol = 2 
  AND e.estado = 'Activo'
  AND h.activo = 1
  AND h.fecha >= '2025-11-25'
ORDER BY h.fecha, h.hora_inicio;

-- ==============================================================
-- VERIFICAR SERVICIOS POR TIPO
-- ==============================================================
-- Servicios de Consulta (id_tipo_servicio = 1): IDs 1-15
-- Operaciones (id_tipo_servicio = 2): IDs 16-31
-- Farmacia (id_tipo_servicio = 3): IDs 32-36
-- Exámenes y Diagnóstico (id_tipo_servicio = 4): IDs 37-83

-- ==============================================================
-- CREAR HORARIOS PARA MÉDICOS (si no existen)
-- Se crean horarios para los próximos 7 días
-- ==============================================================

-- Insertar horarios para médicos activos que no tengan horarios futuros
-- Horarios de mañana: 07:00 - 13:00
-- Horarios de tarde: 14:00 - 22:00

-- Médicos de Cardiología (id_especialidad = 1): empleados 3, 21, 22, 23
-- Médicos de Pediatría (id_especialidad = 2): empleados 4, 24, 25, 26
-- Médicos de Dermatología (id_especialidad = 3): empleados 5, 27, 28, 29
-- Médicos de Traumatología (id_especialidad = 4): empleados 6, 30, 31, 32
-- Médicos de Ginecología (id_especialidad = 5): empleados 7, 33, 34, 35
-- Médicos de Oftalmología (id_especialidad = 6): empleados 8, 36, 37, 38
-- Médicos de Neurología (id_especialidad = 7): empleados 39, 40, 41
-- Médicos de Psiquiatría (id_especialidad = 8): empleados 42, 43, 44
-- Médicos de Medicina General (id_especialidad = 9): empleados 45, 46, 47
-- Médicos de Odontología (id_especialidad = 10): empleados 48, 49, 50

-- ==============================================================
-- INSERTAR HORARIOS PARA LOS PRÓXIMOS 7 DÍAS (26-30 Nov, 1-2 Dic 2025)
-- Solo para médicos que están activos
-- ==============================================================

-- Horarios para empleado 3 (Carlos García - Cardiología)
INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES
(3, '2025-11-26', '07:00:00', '13:00:00', 1),
(3, '2025-11-26', '14:00:00', '22:00:00', 1),
(3, '2025-11-27', '07:00:00', '13:00:00', 1),
(3, '2025-11-27', '14:00:00', '22:00:00', 1),
(3, '2025-11-28', '07:00:00', '13:00:00', 1),
(3, '2025-11-28', '14:00:00', '22:00:00', 1);

-- Horarios para empleado 4 (Pedro Martínez - Pediatría)
INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES
(4, '2025-11-26', '07:00:00', '13:00:00', 1),
(4, '2025-11-26', '14:00:00', '22:00:00', 1),
(4, '2025-11-27', '07:00:00', '13:00:00', 1),
(4, '2025-11-27', '14:00:00', '22:00:00', 1),
(4, '2025-11-28', '07:00:00', '13:00:00', 1),
(4, '2025-11-28', '14:00:00', '22:00:00', 1);

-- Horarios para empleado 5 (Isabel López - Dermatología)
INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES
(5, '2025-11-26', '07:00:00', '13:00:00', 1),
(5, '2025-11-26', '14:00:00', '22:00:00', 1),
(5, '2025-11-27', '07:00:00', '13:00:00', 1),
(5, '2025-11-27', '14:00:00', '22:00:00', 1),
(5, '2025-11-28', '07:00:00', '13:00:00', 1),
(5, '2025-11-28', '14:00:00', '22:00:00', 1);

-- Horarios para empleado 6 (Miguel Rodríguez - Traumatología)
INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES
(6, '2025-11-26', '07:00:00', '13:00:00', 1),
(6, '2025-11-26', '14:00:00', '22:00:00', 1),
(6, '2025-11-27', '07:00:00', '13:00:00', 1),
(6, '2025-11-27', '14:00:00', '22:00:00', 1),
(6, '2025-11-28', '07:00:00', '13:00:00', 1),
(6, '2025-11-28', '14:00:00', '22:00:00', 1);

-- Horarios para empleado 7 (Patricia Fernández - Ginecología)
INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES
(7, '2025-11-26', '07:00:00', '13:00:00', 1),
(7, '2025-11-26', '14:00:00', '22:00:00', 1),
(7, '2025-11-27', '07:00:00', '13:00:00', 1),
(7, '2025-11-27', '14:00:00', '22:00:00', 1),
(7, '2025-11-28', '07:00:00', '13:00:00', 1),
(7, '2025-11-28', '14:00:00', '22:00:00', 1);

-- Horarios para empleado 8 (Jorge Sánchez - Oftalmología)
INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES
(8, '2025-11-26', '07:00:00', '13:00:00', 1),
(8, '2025-11-26', '14:00:00', '22:00:00', 1),
(8, '2025-11-27', '07:00:00', '13:00:00', 1),
(8, '2025-11-27', '14:00:00', '22:00:00', 1),
(8, '2025-11-28', '07:00:00', '13:00:00', 1),
(8, '2025-11-28', '14:00:00', '22:00:00', 1);

-- ==============================================================
-- OBTENER IDS DE HORARIOS RECIÉN CREADOS
-- ==============================================================
-- Nota: Ejecutar este SELECT después de los INSERT para obtener los IDs reales
SELECT id_horario, id_empleado, fecha, hora_inicio, hora_fin 
FROM HORARIO 
WHERE fecha >= '2025-11-26' 
ORDER BY fecha, id_empleado, hora_inicio;

-- ==============================================================
-- INSERTAR PROGRAMACIONES
-- ==============================================================
-- Las programaciones se vinculan a un horario específico
-- Cada programación es de 1 hora de duración
-- Estado: 'Disponible' para nuevas programaciones

-- Variables para usar (ajustar según los IDs de horarios creados)
SET @fecha_inicio = '2025-11-26';

-- ==============================================================
-- PROGRAMACIONES PARA CITAS MÉDICAS (id_tipo_servicio = 1)
-- Servicios: 1-15
-- ==============================================================

-- Obtener el último ID de horario para cada médico y fecha
-- Luego crear las programaciones

-- MÉTODO ALTERNATIVO: Usar subconsultas para obtener los IDs de horarios

-- PROGRAMACIONES DE CITAS MÉDICAS - CARDIOLOGÍA (servicio 1)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    1, -- Consulta Cardiología
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 1 -- Cardiología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
  );

-- PROGRAMACIONES DE CITAS MÉDICAS - PEDIATRÍA (servicio 2)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    2, -- Consulta Pediatría
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 2 -- Pediatría
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
  );

-- PROGRAMACIONES DE CITAS MÉDICAS - DERMATOLOGÍA (servicio 3)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    3, -- Consulta Dermatología
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 3 -- Dermatología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
  );

-- PROGRAMACIONES DE CITAS MÉDICAS - GINECOLOGÍA (servicio 5)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    5, -- Consulta Ginecología
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 5 -- Ginecología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
  );

-- ==============================================================
-- PROGRAMACIONES PARA OPERACIONES (id_tipo_servicio = 2)
-- Servicios: 16-31
-- Las operaciones tienen duraciones más largas (2-4 horas)
-- ==============================================================

-- OPERACIONES DE CIRUGÍA GENERAL (servicio 16)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    16, -- Cirugía General
    h.fecha,
    h.hora_inicio,
    ADDTIME(h.hora_inicio, '03:00:00') as hora_fin, -- 3 horas de duración
    'Disponible'
FROM HORARIO h
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 4 -- Traumatología (puede hacer cirugías)
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '14:00:00' -- Turno de tarde para operaciones
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = h.hora_inicio
  );

-- CESÁREAS (servicio 21)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    21, -- Cesárea
    h.fecha,
    h.hora_inicio,
    ADDTIME(h.hora_inicio, '02:00:00') as hora_fin, -- 2 horas de duración
    'Disponible'
FROM HORARIO h
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 5 -- Ginecología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '14:00:00' -- Turno de tarde
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = h.hora_inicio
  );

-- CIRUGÍA TRAUMATOLÓGICA (servicio 22)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    22, -- Cirugía Traumatológica
    h.fecha,
    ADDTIME(h.hora_inicio, '04:00:00') as hora_inicio, -- Segunda operación del día
    ADDTIME(h.hora_inicio, '07:00:00') as hora_fin, -- 3 horas de duración
    'Disponible'
FROM HORARIO h
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 4 -- Traumatología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '14:00:00' -- Turno de tarde
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, '04:00:00')
  );

-- CIRUGÍA DE CATARATAS (servicio 24) - Oftalmología
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    24, -- Cirugía de Cataratas
    h.fecha,
    h.hora_inicio,
    ADDTIME(h.hora_inicio, '02:00:00') as hora_fin, -- 2 horas
    'Disponible'
FROM HORARIO h
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 6 -- Oftalmología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '14:00:00'
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = h.hora_inicio
  );

-- ==============================================================
-- PROGRAMACIONES PARA EXÁMENES Y DIAGNÓSTICO (id_tipo_servicio = 4)
-- Servicios: 37-83
-- Los exámenes tienen duraciones de 30min a 1 hora
-- ==============================================================

-- HEMOGRAMA COMPLETO (servicio 37)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    37, -- Hemograma Completo
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800)) as hora_inicio, -- slots de 30 min
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 1 -- Cardiología (puede ordenar exámenes de sangre)
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '14:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800))
        AND p.id_servicio = 37
  )
LIMIT 18; -- Limitar cantidad de programaciones

-- PERFIL LIPÍDICO (servicio 40)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    40, -- Perfil Lipídico
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 1 -- Cardiología
  AND e.estado = 'Activo'
  AND h.fecha = '2025-11-27'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
        AND p.id_servicio = 40
  );

-- ECOCARDIOGRAMA (servicio 65) - Especializado de Cardiología
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    65, -- Ecocardiograma
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 1 -- Cardiología
  AND e.estado = 'Activo'
  AND h.fecha = '2025-11-28'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
        AND p.id_servicio = 65
  );

-- ECOGRAFÍA OBSTÉTRICA (servicio 62) - Ginecología
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    62, -- Ecografía Obstétrica
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 5 -- Ginecología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
        AND p.id_servicio = 62
  );

-- ELECTROCARDIOGRAMA (servicio 72)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    72, -- Electrocardiograma
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800)) as hora_inicio, -- 30 min cada uno
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 1 -- Cardiología
  AND e.estado = 'Activo'
  AND h.fecha = '2025-11-26'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800))
        AND p.id_servicio = 72
  );

-- RADIOGRAFÍA DE TÓRAX (servicio 56)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    56, -- Radiografía de Tórax
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 1 -- Cardiología puede solicitar
  AND e.estado = 'Activo'
  AND h.fecha = '2025-11-27'
  AND h.hora_inicio = '14:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800))
        AND p.id_servicio = 56
  );

-- MAMOGRAFÍA (servicio 80) - Ginecología
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    80, -- Mamografía
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 5 -- Ginecología
  AND e.estado = 'Activo'
  AND h.fecha = '2025-11-27'
  AND h.hora_inicio = '14:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 3600)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 3600))
        AND p.id_servicio = 80
  );

-- EXAMEN DE AGUDEZA VISUAL (servicio 77) - Oftalmología
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
SELECT 
    h.id_horario,
    77, -- Examen de Agudeza Visual
    h.fecha,
    ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800)) as hora_inicio,
    ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) as hora_fin,
    'Disponible'
FROM HORARIO h
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
) slot
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE e.id_especialidad = 6 -- Oftalmología
  AND e.estado = 'Activo'
  AND h.fecha >= '2025-11-26'
  AND h.fecha <= '2025-11-28'
  AND h.hora_inicio = '07:00:00'
  AND ADDTIME(h.hora_inicio, SEC_TO_TIME((slot.n + 1) * 1800)) <= h.hora_fin
  AND NOT EXISTS (
      SELECT 1 FROM PROGRAMACION p 
      WHERE p.id_horario = h.id_horario 
        AND p.hora_inicio = ADDTIME(h.hora_inicio, SEC_TO_TIME(slot.n * 1800))
        AND p.id_servicio = 77
  );

-- ==============================================================
-- VERIFICACIÓN DE PROGRAMACIONES CREADAS
-- ==============================================================
SELECT 
    p.id_programacion,
    p.fecha,
    p.hora_inicio,
    p.hora_fin,
    p.estado,
    s.nombre as servicio,
    ts.nombre as tipo_servicio,
    CONCAT(e.nombres, ' ', e.apellidos) as medico,
    esp.nombre as especialidad
FROM PROGRAMACION p
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
INNER JOIN HORARIO h ON p.id_horario = h.id_horario
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
WHERE p.fecha >= '2025-11-26'
ORDER BY p.fecha, p.hora_inicio, ts.nombre;

-- ==============================================================
-- RESUMEN DE PROGRAMACIONES POR TIPO DE SERVICIO
-- ==============================================================
SELECT 
    ts.nombre as tipo_servicio,
    COUNT(*) as total_programaciones,
    COUNT(CASE WHEN p.estado = 'Disponible' THEN 1 END) as disponibles,
    COUNT(CASE WHEN p.estado = 'Ocupado' THEN 1 END) as ocupados
FROM PROGRAMACION p
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
WHERE p.fecha >= '2025-11-26'
GROUP BY ts.id_tipo_servicio, ts.nombre
ORDER BY ts.id_tipo_servicio;
