-- =====================================================
-- DATOS DE PRUEBA COMPLETOS PARA EL SISTEMA DE CLÍNICA
-- Incluye datos para todos los módulos: Reservas y Notificaciones
-- =====================================================
--chero
-- Usar la base de datos CLINICA
USE CLINICA;

-- =====================================================
-- 1. DATOS GEOGRÁFICOS
-- =====================================================

INSERT INTO DEPARTAMENTO (id_departamento, nombre) VALUES
(1, 'Lima'),
(2, 'Arequipa'),
(3, 'Cusco');

INSERT INTO PROVINCIA (id_provincia, nombre, id_departamento) VALUES
(1, 'Lima', 1),
(2, 'Callao', 1),
(3, 'Arequipa', 2);

INSERT INTO DISTRITO (id_distrito, nombre, id_provincia) VALUES
(1, 'San Isidro', 1),
(2, 'Miraflores', 1),
(3, 'Surco', 1),
(4, 'Bellavista', 2),
(5, 'Cercado', 3);

-- =====================================================
-- 2. ROLES
-- =====================================================

INSERT INTO ROL (id_rol, nombre, estado) VALUES
(1, 'Administrador', 'activo'),
(2, 'Médico General', 'activo'),
(3, 'Médico Especialista', 'activo'),
(4, 'Enfermero/a', 'activo'),
(5, 'Recepcionista', 'activo'),
(6, 'Técnico de Laboratorio', 'activo');

-- =====================================================
-- 3. ESPECIALIDADES Y TIPOS DE SERVICIO
-- =====================================================

INSERT INTO ESPECIALIDAD (id_especialidad, nombre, estado, descripcion) VALUES
(1, 'Medicina General', 'activo', 'Atención médica general y preventiva'),
(2, 'Cardiología', 'activo', 'Especialidad en enfermedades del corazón'),
(3, 'Pediatría', 'activo', 'Atención médica para niños'),
(4, 'Traumatología', 'activo', 'Especialidad en lesiones y fracturas'),
(5, 'Dermatología', 'activo', 'Especialidad en enfermedades de la piel'),
(6, 'Oftalmología', 'activo', 'Especialidad en enfermedades de los ojos'),
(7, 'Neurología', 'activo', 'Especialidad en sistema nervioso');

INSERT INTO TIPO_SERVICIO (id_tipo_servicio, nombre, descripcion) VALUES
(1, 'Consulta Médica', 'Consultas médicas generales y especializadas'),
(2, 'Exámenes de Laboratorio', 'Análisis clínicos y pruebas diagnósticas'),
(3, 'Procedimientos', 'Procedimientos médicos menores'),
(4, 'Cirugía', 'Procedimientos quirúrgicos'),
(5, 'Emergencia', 'Atención médica urgente');

INSERT INTO SERVICIO (id_servicio, nombre, descripcion, estado, id_tipo_servicio, id_especialidad) VALUES
-- Medicina General
(1, 'Consulta General', 'Consulta médica general', 'activo', 1, 1),
(2, 'Chequeo Preventivo', 'Chequeo médico general preventivo', 'activo', 1, 1),
-- Cardiología
(3, 'Consulta Cardiológica', 'Evaluación cardiológica especializada', 'activo', 1, 2),
(4, 'Electrocardiograma', 'Estudio del ritmo cardíaco', 'activo', 3, 2),
(5, 'Ecocardiograma', 'Ultrasonido del corazón', 'activo', 3, 2),
-- Pediatría
(6, 'Control Pediátrico', 'Control de niño sano', 'activo', 1, 3),
(7, 'Vacunación', 'Aplicación de vacunas', 'activo', 3, 3),
-- Traumatología
(8, 'Evaluación Traumatológica', 'Evaluación de lesiones osteomusculares', 'activo', 1, 4),
(9, 'Radiografía', 'Estudios radiológicos', 'activo', 2, 4),
-- Dermatología
(10, 'Consulta Dermatológica', 'Evaluación de enfermedades de la piel', 'activo', 1, 5),
(11, 'Tratamiento de Acné', 'Tratamiento especializado para acné', 'activo', 3, 5),
-- Oftalmología
(12, 'Evaluación Oftalmológica', 'Examen de la vista', 'activo', 1, 6),
(13, 'Test de Agudeza Visual', 'Prueba de visión', 'activo', 2, 6),
-- Neurología
(14, 'Consulta Neurológica', 'Evaluación del sistema nervioso', 'activo', 1, 7),
(15, 'Electroencefalograma', 'Estudio de actividad cerebral', 'activo', 2, 7);

-- =====================================================
-- 4. USUARIOS Y PACIENTES
-- =====================================================

-- Usuarios para pacientes
INSERT INTO USUARIO (id_usuario, correo, contrasena, telefono, estado, fecha_creacion) VALUES
(1, 'juan.perez@email.com', 'pbkdf2:sha256:260000$salt$hash1', '987654321', 'activo', '2024-01-15'),
(2, 'maria.garcia@email.com', 'pbkdf2:sha256:260000$salt$hash2', '987654322', 'activo', '2024-01-16'),
(3, 'carlos.lopez@email.com', 'pbkdf2:sha256:260000$salt$hash3', '987654323', 'activo', '2024-01-17'),
(4, 'ana.martinez@email.com', 'pbkdf2:sha256:260000$salt$hash4', '987654324', 'activo', '2024-01-18'),
(5, 'luis.rodriguez@email.com', 'pbkdf2:sha256:260000$salt$hash5', '987654325', 'activo', '2024-01-19'),
(6, 'sofia.torres@email.com', 'pbkdf2:sha256:260000$salt$hash6', '987654326', 'activo', '2024-01-20'),
(7, 'pedro.sanchez@email.com', 'pbkdf2:sha256:260000$salt$hash7', '987654327', 'activo', '2024-01-21'),
(8, 'carmen.flores@email.com', 'pbkdf2:sha256:260000$salt$hash8', '987654328', 'activo', '2024-01-22'),
(9, 'diego.ramirez@email.com', 'pbkdf2:sha256:260000$salt$hash9', '987654329', 'activo', '2024-01-23'),
(10, 'lucia.mendoza@email.com', 'pbkdf2:sha256:260000$salt$hash10', '987654330', 'activo', '2024-01-24');

-- Pacientes
INSERT INTO PACIENTE (id_paciente, nombres, apellidos, documento_identidad, sexo, fecha_nacimiento, id_usuario, id_distrito) VALUES
(1, 'Juan Carlos', 'Pérez González', '12345678', 'Masculino', '1990-05-15', 1, 1),
(2, 'María Elena', 'García Rojas', '23456789', 'Femenino', '1985-08-22', 2, 2),
(3, 'Carlos Alberto', 'López Mendoza', '34567890', 'Masculino', '1978-12-10', 3, 3),
(4, 'Ana Sofía', 'Martínez Cruz', '45678901', 'Femenino', '1995-03-18', 4, 1),
(5, 'Luis Fernando', 'Rodríguez Silva', '56789012', 'Masculino', '1988-07-25', 5, 2),
(6, 'Sofía Isabella', 'Torres Vargas', '67890123', 'Femenino', '2015-11-30', 6, 3),
(7, 'Pedro José', 'Sánchez Ramírez', '78901234', 'Masculino', '1982-09-14', 7, 1),
(8, 'Carmen Rosa', 'Flores Huamán', '89012345', 'Femenino', '1992-06-08', 8, 2),
(9, 'Diego Alejandro', 'Ramírez Castro', '90123456', 'Masculino', '2010-04-12', 9, 3),
(10, 'Lucía Valentina', 'Mendoza Ríos', '01234567', 'Femenino', '1980-10-20', 10, 1);

-- =====================================================
-- 5. USUARIOS Y EMPLEADOS
-- =====================================================

-- Usuarios para empleados (Administrador)
INSERT INTO USUARIO (id_usuario, correo, contrasena, telefono, estado, fecha_creacion) VALUES
(20, 'admin@clinica.com', 'pbkdf2:sha256:260000$salt$hashadmin', '999111222', 'activo', '2023-01-01');

-- Usuarios para médicos
INSERT INTO USUARIO (id_usuario, correo, contrasena, telefono, estado, fecha_creacion) VALUES
(30, 'dr.gonzalez@clinica.com', 'pbkdf2:sha256:260000$salt$hash30', '999888777', 'activo', '2023-06-01'),
(31, 'dra.martinez@clinica.com', 'pbkdf2:sha256:260000$salt$hash31', '999888778', 'activo', '2023-06-02'),
(32, 'dr.ramirez@clinica.com', 'pbkdf2:sha256:260000$salt$hash32', '999888779', 'activo', '2023-06-03'),
(33, 'dra.castro@clinica.com', 'pbkdf2:sha256:260000$salt$hash33', '999888780', 'activo', '2023-06-04'),
(34, 'dr.morales@clinica.com', 'pbkdf2:sha256:260000$salt$hash34', '999888781', 'activo', '2023-06-05'),
(35, 'dra.silva@clinica.com', 'pbkdf2:sha256:260000$salt$hash35', '999888782', 'activo', '2023-06-06'),
(36, 'dr.vargas@clinica.com', 'pbkdf2:sha256:260000$salt$hash36', '999888783', 'activo', '2023-06-07');

-- Usuarios para personal no médico
INSERT INTO USUARIO (id_usuario, correo, contrasena, telefono, estado, fecha_creacion) VALUES
(40, 'enfermera.lopez@clinica.com', 'pbkdf2:sha256:260000$salt$hash40', '999777666', 'activo', '2023-07-01'),
(41, 'recepcion.torres@clinica.com', 'pbkdf2:sha256:260000$salt$hash41', '999777667', 'activo', '2023-07-02'),
(42, 'tecnico.rojas@clinica.com', 'pbkdf2:sha256:260000$salt$hash42', '999777668', 'activo', '2023-07-03');

-- Empleado Administrador
INSERT INTO EMPLEADO (id_empleado, nombres, apellidos, documento_identidad, sexo, estado, id_usuario, id_rol, id_distrito, id_especialidad) VALUES
(1, 'Carlos Eduardo', 'Administrador Sistema', '10123456', 'Masculino', 'activo', 20, 1, 1, NULL);

-- Empleados Médicos
INSERT INTO EMPLEADO (id_empleado, nombres, apellidos, documento_identidad, sexo, estado, id_usuario, id_rol, id_distrito, id_especialidad) VALUES
(10, 'Luis Alberto', 'González Vega', '20123456', 'Masculino', 'activo', 30, 2, 1, 1),      -- Medicina General
(11, 'Ana Patricia', 'Martínez Ruiz', '20234567', 'Femenino', 'activo', 31, 3, 2, 2),       -- Cardiología (Especialista)
(12, 'Roberto Carlos', 'Ramírez Díaz', '20345678', 'Masculino', 'activo', 32, 3, 3, 3),     -- Pediatría (Especialista)
(13, 'Laura Beatriz', 'Castro Paredes', '20456789', 'Femenino', 'activo', 33, 3, 1, 4),     -- Traumatología (Especialista)
(14, 'Miguel Ángel', 'Morales Soto', '20567890', 'Masculino', 'activo', 34, 2, 2, 1),       -- Medicina General
(15, 'Patricia Elena', 'Silva Campos', '20678901', 'Femenino', 'activo', 35, 3, 3, 5),      -- Dermatología (Especialista)
(16, 'Fernando José', 'Vargas Ramos', '20789012', 'Masculino', 'activo', 36, 3, 1, 6);      -- Oftalmología (Especialista)

-- Empleados NO médicos (no deben aparecer en listado de médicos)
INSERT INTO EMPLEADO (id_empleado, nombres, apellidos, documento_identidad, sexo, estado, id_usuario, id_rol, id_distrito, id_especialidad) VALUES
(20, 'Rosa María', 'López Fernández', '30123456', 'Femenino', 'activo', 40, 4, 1, NULL),    -- Enfermera
(21, 'Juan Carlos', 'Torres Mendoza', '30234567', 'Masculino', 'activo', 41, 5, 2, NULL),   -- Recepcionista
(22, 'Mario Alberto', 'Rojas Paz', '30345678', 'Masculino', 'activo', 42, 6, 3, NULL);      -- Técnico

-- =====================================================
-- 6. HORARIOS Y PROGRAMACIONES
-- =====================================================

-- Horarios para médicos (próximos días - Noviembre 2025)
INSERT INTO HORARIO (id_horario, id_empleado, fecha, hora_inicio, hora_fin, estado) VALUES
-- Dr. González (Medicina General) - Lunes a Viernes
(1, 10, '2025-11-03', '08:00:00', '12:00:00', 'disponible'),
(2, 10, '2025-11-03', '14:00:00', '18:00:00', 'disponible'),
(3, 10, '2025-11-04', '08:00:00', '12:00:00', 'disponible'),
(4, 10, '2025-11-04', '14:00:00', '18:00:00', 'disponible'),
(5, 10, '2025-11-05', '08:00:00', '12:00:00', 'disponible'),
(6, 10, '2025-11-05', '14:00:00', '18:00:00', 'disponible'),

-- Dra. Martínez (Cardiología) - Martes y Jueves
(7, 11, '2025-11-04', '09:00:00', '13:00:00', 'disponible'),
(8, 11, '2025-11-04', '15:00:00', '19:00:00', 'disponible'),
(9, 11, '2025-11-06', '09:00:00', '13:00:00', 'disponible'),
(10, 11, '2025-11-06', '15:00:00', '19:00:00', 'disponible'),

-- Dr. Ramírez (Pediatría) - Lunes a Viernes
(11, 12, '2025-11-03', '08:00:00', '14:00:00', 'disponible'),
(12, 12, '2025-11-04', '08:00:00', '14:00:00', 'disponible'),
(13, 12, '2025-11-05', '08:00:00', '14:00:00', 'disponible'),
(14, 12, '2025-11-06', '08:00:00', '14:00:00', 'disponible'),
(15, 12, '2025-11-07', '08:00:00', '14:00:00', 'disponible'),

-- Dra. Castro (Traumatología) - Lunes, Miércoles, Viernes
(16, 13, '2025-11-03', '10:00:00', '14:00:00', 'disponible'),
(17, 13, '2025-11-03', '16:00:00', '20:00:00', 'disponible'),
(18, 13, '2025-11-05', '10:00:00', '14:00:00', 'disponible'),
(19, 13, '2025-11-05', '16:00:00', '20:00:00', 'disponible'),
(20, 13, '2025-11-07', '10:00:00', '14:00:00', 'disponible'),

-- Dr. Morales (Medicina General) - Lunes a Viernes
(21, 14, '2025-11-03', '07:00:00', '15:00:00', 'disponible'),
(22, 14, '2025-11-04', '07:00:00', '15:00:00', 'disponible'),
(23, 14, '2025-11-05', '07:00:00', '15:00:00', 'disponible'),
(24, 14, '2025-11-06', '07:00:00', '15:00:00', 'disponible'),

-- Dra. Silva (Dermatología) - Martes y Jueves
(25, 15, '2025-11-04', '10:00:00', '14:00:00', 'disponible'),
(26, 15, '2025-11-04', '16:00:00', '20:00:00', 'disponible'),
(27, 15, '2025-11-06', '10:00:00', '14:00:00', 'disponible'),
(28, 15, '2025-11-06', '16:00:00', '20:00:00', 'disponible'),

-- Dr. Vargas (Oftalmología) - Lunes, Miércoles, Viernes
(29, 16, '2025-11-03', '09:00:00', '13:00:00', 'disponible'),
(30, 16, '2025-11-05', '09:00:00', '13:00:00', 'disponible'),
(31, 16, '2025-11-07', '09:00:00', '13:00:00', 'disponible');

-- Programaciones basadas en horarios
INSERT INTO PROGRAMACION (id_programacion, fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario) VALUES
-- Consultas Generales - Dr. González
(1, '2025-11-03', '09:00:00', '10:00:00', 'disponible', 1, 1),
(2, '2025-11-03', '10:00:00', '11:00:00', 'disponible', 1, 1),
(3, '2025-11-03', '15:00:00', '16:00:00', 'disponible', 1, 2),
(4, '2025-11-04', '09:00:00', '10:00:00', 'disponible', 1, 3),
(5, '2025-11-04', '10:00:00', '11:00:00', 'disponible', 1, 3),
(6, '2025-11-05', '09:00:00', '10:00:00', 'disponible', 2, 5),

-- Consultas Cardiológicas - Dra. Martínez
(7, '2025-11-04', '10:00:00', '11:00:00', 'disponible', 3, 7),
(8, '2025-11-04', '16:00:00', '17:00:00', 'disponible', 3, 8),
(9, '2025-11-06', '10:00:00', '11:00:00', 'disponible', 3, 9),
(10, '2025-11-06', '10:00:00', '11:00:00', 'disponible', 4, 9),

-- Control Pediátrico - Dr. Ramírez
(11, '2025-11-03', '09:00:00', '10:00:00', 'disponible', 6, 11),
(12, '2025-11-04', '09:00:00', '10:00:00', 'disponible', 6, 12),
(13, '2025-11-05', '11:00:00', '12:00:00', 'disponible', 6, 13),
(14, '2025-11-06', '09:00:00', '10:00:00', 'disponible', 7, 14),

-- Evaluación Traumatológica - Dra. Castro
(15, '2025-11-03', '11:00:00', '12:00:00', 'disponible', 8, 16),
(16, '2025-11-03', '17:00:00', '18:00:00', 'disponible', 8, 17),
(17, '2025-11-05', '11:00:00', '12:00:00', 'disponible', 9, 18),

-- Consultas Generales - Dr. Morales
(18, '2025-11-03', '08:00:00', '09:00:00', 'disponible', 1, 21),
(19, '2025-11-04', '08:00:00', '09:00:00', 'disponible', 1, 22),
(20, '2025-11-05', '08:00:00', '09:00:00', 'disponible', 2, 23),

-- Consultas Dermatológicas - Dra. Silva
(21, '2025-11-04', '11:00:00', '12:00:00', 'disponible', 10, 25),
(22, '2025-11-04', '17:00:00', '18:00:00', 'disponible', 11, 26),
(23, '2025-11-06', '11:00:00', '12:00:00', 'disponible', 10, 27),

-- Consultas Oftalmológicas - Dr. Vargas
(24, '2025-11-03', '10:00:00', '11:00:00', 'disponible', 12, 29),
(25, '2025-11-05', '10:00:00', '11:00:00', 'disponible', 13, 30);

-- =====================================================
-- 7. RESERVAS (Estados: pendiente, confirmada, completada, cancelada)
-- =====================================================

INSERT INTO RESERVA (id_reserva, fecha_registro, hora_registro, tipo, estado, motivo_cancelacion, id_paciente, id_programacion) VALUES
-- Reservas PENDIENTES (para confirmar)
(1, '2025-10-28', '10:30:00', 1, 'pendiente', NULL, 1, 1),  -- Juan Pérez - Consulta General
(2, '2025-10-28', '11:15:00', 1, 'pendiente', NULL, 2, 2),  -- María García - Consulta General
(3, '2025-10-28', '14:20:00', 1, 'pendiente', NULL, 3, 7),  -- Carlos López - Cardiología
(4, '2025-10-29', '08:45:00', 1, 'pendiente', NULL, 4, 11), -- Ana Martínez - Pediatría
(5, '2025-10-29', '09:30:00', 1, 'pendiente', NULL, 5, 15), -- Luis Rodríguez - Traumatología
(6, '2025-10-29', '10:00:00', 1, 'pendiente', NULL, 6, 21), -- Sofía Torres - Dermatología
(7, '2025-10-29', '11:00:00', 1, 'pendiente', NULL, 7, 24), -- Pedro Sánchez - Oftalmología

-- Reservas CONFIRMADAS (listas para atención)
(8, '2025-10-27', '15:00:00', 1, 'confirmada', NULL, 8, 3),  -- Carmen Flores - Consulta General
(9, '2025-10-27', '16:30:00', 1, 'confirmada', NULL, 9, 8),  -- Diego Ramírez - Cardiología
(10, '2025-10-28', '08:00:00', 1, 'confirmada', NULL, 10, 18), -- Lucía Mendoza - Consulta General
(11, '2025-10-28', '10:00:00', 1, 'confirmada', NULL, 1, 4),  -- Juan Pérez - Consulta General
(12, '2025-10-28', '12:00:00', 1, 'confirmada', NULL, 2, 12), -- María García - Pediatría
(13, '2025-10-29', '09:00:00', 1, 'confirmada', NULL, 3, 19), -- Carlos López - Consulta General
(14, '2025-10-29', '10:30:00', 1, 'confirmada', NULL, 4, 22), -- Ana Martínez - Dermatología

-- Reservas COMPLETADAS (atenciones pasadas)
(15, '2025-10-20', '09:00:00', 1, 'completada', NULL, 5, 5),
(16, '2025-10-21', '10:00:00', 1, 'completada', NULL, 6, 6),
(17, '2025-10-22', '11:00:00', 1, 'completada', NULL, 7, 16),
(18, '2025-10-23', '14:00:00', 1, 'completada', NULL, 8, 13),
(19, '2025-10-24', '15:00:00', 1, 'completada', NULL, 9, 20),

-- Reservas CANCELADAS (para pruebas de gestión de cancelaciones)
(20, '2025-10-15', '08:00:00', 1, 'cancelada', 'Paciente tuvo un inconveniente laboral de último momento', 1, 9),
(21, '2025-10-16', '09:00:00', 1, 'cancelada', 'Duplicado por error del sistema al momento de registrar', 2, 10),
(22, '2025-10-17', '10:00:00', 1, 'cancelada', 'Paciente solicitó reprogramación por viaje de emergencia', 3, 14),
(23, '2025-10-18', '11:00:00', 1, 'cancelada', 'Médico no disponible por emergencia familiar', 4, 17);

-- =====================================================
-- 8. TIPOS DE NOTIFICACIÓN Y CANALES
-- =====================================================

INSERT INTO TIPO_NOTIFICACION (id_tipo_notificacion, nombre, descripcion) VALUES
(1, 'Confirmación de Cita', 'Notificación enviada al confirmar una reserva'),
(2, 'Recordatorio de Cita', 'Recordatorio enviado antes de la cita'),
(3, 'Cancelación de Cita', 'Notificación de cancelación de reserva'),
(4, 'Reprogramación de Cita', 'Notificación de cambio de fecha/hora'),
(5, 'Cambio de Médico', 'Notificación de cambio de médico asignado'),
(6, 'Recordatorio de Resultados', 'Notificación sobre resultados disponibles');

INSERT INTO CANAL (id_canal, nombre, descripcion) VALUES
(1, 'Correo Electrónico', 'Notificaciones enviadas por email'),
(2, 'SMS', 'Notificaciones enviadas por mensaje de texto'),
(3, 'WhatsApp', 'Notificaciones enviadas por WhatsApp'),
(4, 'Notificación Push', 'Notificaciones push en la aplicación móvil');

-- =====================================================
-- 9. NOTIFICACIONES
-- =====================================================

INSERT INTO NOTIFICACION (id_notificacion, fecha_envio, hora_envio, mensaje, estado, id_paciente, id_tipo_notificacion, id_canal) VALUES
-- Notificaciones de Confirmación
(1, '2025-10-27', '15:05:00', 'Su cita ha sido confirmada para el 03/11/2025 a las 15:00 con Dr. González - Consulta General', 'enviada', 8, 1, 1),
(2, '2025-10-27', '16:35:00', 'Su cita ha sido confirmada para el 04/11/2025 a las 16:00 con Dra. Martínez - Cardiología', 'enviada', 9, 1, 2),
(3, '2025-10-28', '08:05:00', 'Su cita ha sido confirmada para el 03/11/2025 a las 08:00 con Dr. Morales - Consulta General', 'enviada', 10, 1, 1),

-- Notificaciones de Recordatorio (24 horas antes)
(4, '2025-11-02', '09:00:00', 'Recordatorio: Tiene una cita mañana 03/11/2025 a las 09:00 con Dr. González', 'enviada', 1, 2, 2),
(5, '2025-11-02', '10:00:00', 'Recordatorio: Tiene una cita mañana 03/11/2025 a las 10:00 con Dr. González', 'enviada', 2, 2, 1),
(6, '2025-11-02', '15:00:00', 'Recordatorio: Tiene una cita mañana 03/11/2025 a las 15:00 con Dr. González', 'enviada', 8, 2, 3),

-- Notificaciones Pendientes (programadas para envío)
(7, '2025-11-03', '08:00:00', 'Recordatorio: Tiene una cita mañana 04/11/2025 a las 10:00 con Dra. Martínez', 'pendiente', 3, 2, 1),
(8, '2025-11-03', '09:00:00', 'Recordatorio: Tiene una cita mañana 04/11/2025 a las 09:00 con Dr. Ramírez', 'pendiente', 4, 2, 2),
(9, '2025-11-03', '10:00:00', 'Recordatorio: Tiene una cita mañana 04/11/2025 a las 08:00 con Dr. Morales', 'pendiente', 10, 2, 1),

-- Notificaciones de Cancelación
(10, '2025-10-15', '08:30:00', 'Su cita del 04/11/2025 ha sido cancelada. Motivo: Paciente tuvo un inconveniente laboral', 'enviada', 1, 3, 1),
(11, '2025-10-16', '09:30:00', 'Su cita del 06/11/2025 ha sido cancelada. Motivo: Duplicado por error del sistema', 'enviada', 2, 3, 2),

-- Notificaciones Fallidas (para pruebas de reenvío)
(12, '2025-10-29', '14:00:00', 'Recordatorio: Tiene una cita mañana 30/10/2025 a las 11:00', 'fallida', 5, 2, 2),
(13, '2025-10-29', '15:00:00', 'Su cita ha sido confirmada para el 05/11/2025 a las 11:00', 'fallida', 7, 1, 1);

-- =====================================================
-- 10. CONSULTAS DE VERIFICACIÓN
-- =====================================================

-- ===========================================
-- CONSULTA 1: Verificar MÉDICOS (solo roles 2 y 3)
-- ===========================================
SELECT
    '=== LISTADO DE MÉDICOS ===' as Seccion,
    NULL as id, NULL as nombre, NULL as rol, NULL as especialidad, NULL as correo
UNION ALL
SELECT
    '',
    e.id_empleado,
    CONCAT(e.nombres, ' ', e.apellidos) as nombre,
    r.nombre as rol,
    esp.nombre as especialidad,
    u.correo
FROM EMPLEADO e
INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
LEFT JOIN ROL r ON e.id_rol = r.id_rol
LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
WHERE e.id_rol IN (2, 3)
  AND e.id_especialidad IS NOT NULL
  AND e.estado = 'activo'
ORDER BY e.apellidos, e.nombres;

-- ===========================================
-- CONSULTA 2: Verificar EMPLEADOS NO MÉDICOS (no deben aparecer en listado de médicos)
-- ===========================================
SELECT
    '=== EMPLEADOS NO MÉDICOS (NO DEBEN APARECER EN CONSULTA POR MÉDICO) ===' as Seccion,
    NULL as id, NULL as nombre, NULL as rol, NULL as correo
UNION ALL
SELECT
    '',
    e.id_empleado,
    CONCAT(e.nombres, ' ', e.apellidos) as nombre,
    r.nombre as rol,
    u.correo
FROM EMPLEADO e
INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
LEFT JOIN ROL r ON e.id_rol = r.id_rol
WHERE e.id_rol NOT IN (2, 3)
  AND e.estado = 'activo'
ORDER BY e.apellidos, e.nombres;

-- ===========================================
-- CONSULTA 3: Verificar SERVICIOS POR ESPECIALIDAD
-- ===========================================
SELECT
    '=== SERVICIOS POR ESPECIALIDAD ===' as Seccion,
    NULL as especialidad, NULL as servicio, NULL as tipo, NULL as estado
UNION ALL
SELECT
    '',
    esp.nombre as especialidad,
    s.nombre as servicio,
    ts.nombre as tipo_servicio,
    s.estado
FROM SERVICIO s
LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
ORDER BY esp.nombre, s.nombre;

-- ===========================================
-- CONSULTA 4: Verificar RESERVAS ACTIVAS (para Gestión de Cancelaciones)
-- ===========================================
SELECT
    '=== RESERVAS ACTIVAS (PENDIENTES Y CONFIRMADAS) ===' as Seccion,
    NULL as id_reserva, NULL as DNI, NULL as Paciente, NULL as Servicio,
    NULL as Medico, NULL as Fecha, NULL as Hora, NULL as Estado
UNION ALL
SELECT
    '',
    r.id_reserva,
    p.documento_identidad as DNI,
    CONCAT(p.nombres, ' ', p.apellidos) as Paciente,
    s.nombre as Servicio,
    CONCAT(e.nombres, ' ', e.apellidos) as Medico,
    prog.fecha as Fecha,
    CONCAT(prog.hora_inicio, ' - ', prog.hora_fin) as Hora,
    r.estado as Estado
FROM RESERVA r
INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE r.estado IN ('pendiente', 'confirmada')
ORDER BY prog.fecha, prog.hora_inicio;

-- ===========================================
-- CONSULTA 5: Verificar DISPONIBILIDAD DE HORARIOS
-- ===========================================
SELECT
    '=== HORARIOS DISPONIBLES ===' as Seccion,
    NULL as Medico, NULL as Especialidad, NULL as Fecha, NULL as Horario, NULL as Estado
UNION ALL
SELECT
    '',
    CONCAT(e.nombres, ' ', e.apellidos) as Medico,
    esp.nombre as Especialidad,
    h.fecha,
    CONCAT(h.hora_inicio, ' - ', h.hora_fin) as Horario,
    h.estado
FROM HORARIO h
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
WHERE h.estado = 'disponible'
  AND h.fecha >= CURDATE()
ORDER BY h.fecha, h.hora_inicio;

-- ===========================================
-- CONSULTA 6: Verificar NOTIFICACIONES (todas por estado)
-- ===========================================
SELECT
    '=== NOTIFICACIONES POR ESTADO ===' as Seccion,
    NULL as Estado, NULL as Cantidad
UNION ALL
SELECT
    '',
    estado,
    COUNT(*) as cantidad
FROM NOTIFICACION
GROUP BY estado
ORDER BY estado;

-- ===========================================
-- CONSULTA 7: Verificar NOTIFICACIONES PENDIENTES (para Gestión de Recordatorios)
-- ===========================================
SELECT
    '=== NOTIFICACIONES PENDIENTES ===' as Seccion,
    NULL as id, NULL as Paciente, NULL as Tipo, NULL as Canal, NULL as Fecha_Envio, NULL as Mensaje
UNION ALL
SELECT
    '',
    n.id_notificacion,
    CONCAT(p.nombres, ' ', p.apellidos) as Paciente,
    tn.nombre as Tipo,
    c.nombre as Canal,
    CONCAT(n.fecha_envio, ' ', n.hora_envio) as Fecha_Envio,
    n.mensaje
FROM NOTIFICACION n
INNER JOIN PACIENTE p ON n.id_paciente = p.id_paciente
LEFT JOIN TIPO_NOTIFICACION tn ON n.id_tipo_notificacion = tn.id_tipo_notificacion
LEFT JOIN CANAL c ON n.id_canal = c.id_canal
WHERE n.estado = 'pendiente'
ORDER BY n.fecha_envio, n.hora_envio;

-- ===========================================
-- CONSULTA 8: Verificar RESERVAS PARA REPROGRAMACIÓN
-- ===========================================
SELECT
    '=== RESERVAS DISPONIBLES PARA REPROGRAMAR ===' as Seccion,
    NULL as id_reserva, NULL as Paciente, NULL as Servicio, NULL as Fecha_Actual, NULL as Estado
UNION ALL
SELECT
    '',
    r.id_reserva,
    CONCAT(p.nombres, ' ', p.apellidos) as Paciente,
    s.nombre as Servicio,
    CONCAT(prog.fecha, ' ', prog.hora_inicio) as Fecha_Actual,
    r.estado
FROM RESERVA r
INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
WHERE r.estado IN ('pendiente', 'confirmada')
  AND prog.fecha >= CURDATE()
ORDER BY prog.fecha, prog.hora_inicio;

-- ===========================================
-- CONSULTA 9: Reporte de SERVICIOS MÁS SOLICITADOS
-- ===========================================
SELECT
    '=== REPORTE: SERVICIOS MÁS SOLICITADOS ===' as Seccion,
    NULL as Servicio, NULL as Especialidad, NULL as Total_Reservas
UNION ALL
SELECT
    '',
    s.nombre as Servicio,
    esp.nombre as Especialidad,
    COUNT(r.id_reserva) as Total_Reservas
FROM SERVICIO s
LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
LEFT JOIN PROGRAMACION prog ON prog.id_servicio = s.id_servicio
LEFT JOIN RESERVA r ON r.id_programacion = prog.id_programacion
GROUP BY s.id_servicio, s.nombre, esp.nombre
ORDER BY Total_Reservas DESC, s.nombre;

-- ===========================================
-- CONSULTA 10: Verificar CONFIRMACIONES PENDIENTES
-- ===========================================
SELECT
    '=== CITAS PENDIENTES DE CONFIRMACIÓN ===' as Seccion,
    NULL as id_reserva, NULL as Paciente, NULL as Telefono, NULL as Servicio, NULL as Medico, NULL as Fecha_Cita
UNION ALL
SELECT
    '',
    r.id_reserva,
    CONCAT(p.nombres, ' ', p.apellidos) as Paciente,
    u.telefono,
    s.nombre as Servicio,
    CONCAT(e.nombres, ' ', e.apellidos) as Medico,
    CONCAT(prog.fecha, ' ', prog.hora_inicio) as Fecha_Cita
FROM RESERVA r
INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
WHERE r.estado = 'pendiente'
ORDER BY prog.fecha, prog.hora_inicio;

-- =====================================================
-- RESUMEN DE DATOS INSERTADOS
-- =====================================================
SELECT '=== RESUMEN DE DATOS INSERTADOS ===' as Resumen;
SELECT '3 Departamentos' as Item UNION ALL
SELECT '3 Provincias' UNION ALL
SELECT '5 Distritos' UNION ALL
SELECT '6 Roles' UNION ALL
SELECT '7 Especialidades' UNION ALL
SELECT '5 Tipos de Servicio' UNION ALL
SELECT '15 Servicios' UNION ALL
SELECT '10 Pacientes' UNION ALL
SELECT '10 Empleados (7 Médicos + 3 No Médicos)' UNION ALL
SELECT '31 Horarios' UNION ALL
SELECT '25 Programaciones' UNION ALL
SELECT '23 Reservas (14 activas: 7 pendientes + 7 confirmadas, 5 completadas, 4 canceladas)' UNION ALL
SELECT '6 Tipos de Notificación' UNION ALL
SELECT '4 Canales de Notificación' UNION ALL
SELECT '13 Notificaciones (6 enviadas, 4 pendientes, 2 fallidas)';

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
