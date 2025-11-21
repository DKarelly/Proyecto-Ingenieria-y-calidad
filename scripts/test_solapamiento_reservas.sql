-- =====================================================
-- SCRIPT DE PRUEBA: VALIDACIÓN DE SOLAPAMIENTO DE RESERVAS
-- Fecha: 21 de noviembre de 2025
-- =====================================================
-- Este script crea datos de prueba para validar que un paciente
-- NO pueda crear reservas que se solapen en tiempo.
-- =====================================================

-- Usar la base de datos
USE bd_calidad;

-- =====================================================
-- 1. CREAR HORARIO BASE PARA LAS PRUEBAS
-- =====================================================
-- Nota: Ajusta el id_empleado según un médico existente en tu BD
-- Puedes consultar: SELECT id_empleado, nombres, apellidos FROM EMPLEADO WHERE id_especialidad = 1 LIMIT 5;

SET @id_empleado_prueba = 1; -- Ajusta este ID según tu BD
SET @fecha_prueba = '2025-11-25'; -- Lunes 25 de noviembre de 2025

-- Crear horario del médico para el día de prueba
INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo)
VALUES (@id_empleado_prueba, @fecha_prueba, '08:00:00', '18:00:00', 1);

SET @id_horario_prueba = LAST_INSERT_ID();

-- =====================================================
-- 2. CREAR PROGRAMACIONES PARA DIFERENTES ESCENARIOS
-- =====================================================
-- Nota: Ajusta el id_servicio según un servicio existente en tu BD
-- Puedes consultar: SELECT id_servicio, nombre FROM SERVICIO WHERE id_tipo_servicio = 1 LIMIT 5;

SET @id_servicio_prueba = 1; -- Ajusta este ID según tu BD (ej: Consulta General)

-- =====================================================
-- ESCENARIO 1: Reservas Consecutivas (NO deben solaparse)
-- =====================================================
-- Programación 1: 09:00 - 10:00
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '09:00:00', '10:00:00', 'Disponible');

-- Programación 2: 10:00 - 11:00 (Justo después, NO se solapa)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '10:00:00', '11:00:00', 'Disponible');

-- =====================================================
-- ESCENARIO 2: Solapamiento Parcial (inicio)
-- =====================================================
-- Programación 3: 11:00 - 12:00
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '11:00:00', '12:00:00', 'Disponible');

-- Programación 4: 11:30 - 12:30 (Se SOLAPA con la anterior)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '11:30:00', '12:30:00', 'Disponible');

-- =====================================================
-- ESCENARIO 3: Solapamiento Parcial (fin)
-- =====================================================
-- Programación 5: 13:00 - 14:00
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '13:00:00', '14:00:00', 'Disponible');

-- Programación 6: 12:30 - 13:30 (Se SOLAPA con la anterior)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '12:30:00', '13:30:00', 'Disponible');

-- =====================================================
-- ESCENARIO 4: Contenida Completamente
-- =====================================================
-- Programación 7: 14:00 - 16:00 (Ventana grande)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '14:00:00', '16:00:00', 'Disponible');

-- Programación 8: 14:30 - 15:30 (Contenida DENTRO de la anterior)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '14:30:00', '15:30:00', 'Disponible');

-- =====================================================
-- ESCENARIO 5: Reservas Separadas (NO se solapan)
-- =====================================================
-- Programación 9: 16:00 - 17:00
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '16:00:00', '17:00:00', 'Disponible');

-- Programación 10: 08:00 - 09:00 (Separada, NO se solapa)
INSERT INTO PROGRAMACION (id_horario, id_servicio, fecha, hora_inicio, hora_fin, estado)
VALUES (@id_horario_prueba, @id_servicio_prueba, @fecha_prueba, '08:00:00', '09:00:00', 'Disponible');

-- =====================================================
-- 3. CONSULTA DE VERIFICACIÓN
-- =====================================================
-- Ver todas las programaciones creadas
SELECT 
    p.id_programacion,
    p.fecha,
    TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio,
    TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin,
    p.estado,
    s.nombre as servicio,
    CONCAT(e.nombres, ' ', e.apellidos) as medico
FROM PROGRAMACION p
INNER JOIN HORARIO h ON p.id_horario = h.id_horario
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
WHERE p.fecha = @fecha_prueba
  AND h.id_empleado = @id_empleado_prueba
ORDER BY p.hora_inicio;

-- =====================================================
-- 4. GUÍA DE PRUEBAS
-- =====================================================
/*
PRUEBA A: Reservar programación 1 (09:00-10:00), luego programación 2 (10:00-11:00)
✅ RESULTADO ESPERADO: ÉXITO (no se solapan)

PRUEBA B: Reservar programación 3 (11:00-12:00), luego programación 4 (11:30-12:30)
❌ RESULTADO ESPERADO: ERROR - "Ya tienes una reserva en este horario. Conflicto con la reserva de 11:00 a 12:00."

PRUEBA C: Reservar programación 5 (13:00-14:00), luego programación 6 (12:30-13:30)
❌ RESULTADO ESPERADO: ERROR - "Ya tienes una reserva en este horario. Conflicto con la reserva de 13:00 a 14:00."

PRUEBA D: Reservar programación 7 (14:00-16:00), luego programación 8 (14:30-15:30)
❌ RESULTADO ESPERADO: ERROR - "Ya tienes una reserva en este horario. Conflicto con la reserva de 14:00 a 16:00."

PRUEBA E: Reservar programación 9 (16:00-17:00), luego programación 10 (08:00-09:00)
✅ RESULTADO ESPERADO: ÉXITO (están completamente separadas)

PRUEBA F: Mismo servicio, mismo médico, mismo día (sin solapamiento de hora)
❌ RESULTADO ESPERADO: ERROR - "Ya tienes una reserva para este mismo servicio y médico en esta fecha."
*/

-- =====================================================
-- 5. QUERIES PARA SIMULAR LA VALIDACIÓN
-- =====================================================
-- Simular validación de solapamiento
-- Reemplaza @id_paciente_prueba con un ID de paciente existente
SET @id_paciente_prueba = 1;
SET @nueva_hora_inicio = '11:30:00';
SET @nueva_hora_fin = '12:30:00';

-- Esta query debería retornar la programación 3 (11:00-12:00) como conflicto
SELECT 
    r.id_reserva, 
    TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio,
    TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin,
    'CONFLICTO DETECTADO' as resultado
FROM RESERVA r
INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
WHERE r.id_paciente = @id_paciente_prueba
  AND p.fecha = @fecha_prueba
  AND r.estado IN ('Confirmada', 'Pendiente')
  AND (
      (p.hora_inicio < @nueva_hora_fin AND p.hora_fin > @nueva_hora_inicio) OR
      (p.hora_inicio < @nueva_hora_fin AND p.hora_fin > @nueva_hora_inicio) OR
      (p.hora_inicio >= @nueva_hora_inicio AND p.hora_fin <= @nueva_hora_fin)
  )
LIMIT 1;

-- =====================================================
-- 6. LIMPIEZA (Ejecutar después de las pruebas)
-- =====================================================
/*
-- Eliminar programaciones de prueba
DELETE FROM PROGRAMACION 
WHERE id_horario = @id_horario_prueba;

-- Eliminar horario de prueba
DELETE FROM HORARIO 
WHERE id_horario = @id_horario_prueba;

-- Verificar limpieza
SELECT COUNT(*) as programaciones_restantes 
FROM PROGRAMACION 
WHERE fecha = @fecha_prueba;
*/

-- =====================================================
-- NOTAS IMPORTANTES
-- =====================================================
/*
1. Antes de ejecutar, verifica que existan:
   - Un empleado (médico) con id_empleado válido
   - Un servicio con id_servicio válido
   - Un paciente con id_paciente válido

2. Ajusta las variables @id_empleado_prueba, @id_servicio_prueba y @id_paciente_prueba

3. Consultas útiles para obtener IDs válidos:
   
   -- Ver empleados (médicos)
   SELECT id_empleado, CONCAT(nombres, ' ', apellidos) as nombre, id_especialidad 
   FROM EMPLEADO 
   WHERE id_especialidad IS NOT NULL
   LIMIT 10;
   
   -- Ver servicios
   SELECT id_servicio, nombre, id_tipo_servicio 
   FROM SERVICIO 
   WHERE id_tipo_servicio = 1
   LIMIT 10;
   
   -- Ver pacientes
   SELECT id_paciente, CONCAT(nombres, ' ', apellidos) as nombre 
   FROM PACIENTE 
   LIMIT 10;

4. Para probar desde la interfaz web:
   - Inicia sesión como paciente
   - Ve a /reservas/paciente/nueva-cita
   - Selecciona el médico y fecha de prueba
   - Intenta reservar las programaciones en el orden indicado en la Guía de Pruebas
*/
