-- =====================================================
-- SCRIPT DE INSERTS PARA BASE DE DATOS CLÍNICA UNIÓN
-- =====================================================
-- Este script contiene datos de ejemplo para todas las tablas
-- EXCEPTO: DEPARTAMENTO, PROVINCIA, DISTRITO, SERVICIO, TIPO_SERVICIO
-- (Se asume que estas tablas ya tienen datos precargados)
-- =====================================================
-- IMPORTANTE: 
-- - Todas las contraseñas están hasheadas con scrypt
-- - Contraseña de ejemplo: "password123"
-- - Asegúrate de que id_distrito=140312 (Chiclayo) existe
-- =====================================================

-- Deshabilitar verificación de claves foráneas temporalmente
SET FOREIGN_KEY_CHECKS=0;

-- =====================================================
-- 1. TABLA: ROL (ya tiene datos, pero aquí están por referencia)
-- =====================================================
-- Los roles ya existen en tu BD:
-- (1,'Administrador','Activo')
-- (2,'Médico','Activo')
-- (3,'Recepcionista','Activo')
-- (4,'Farmacéutico','Activo')
-- (5,'Laboratorista','Activo')

-- =====================================================
-- 2. TABLA: ESPECIALIDAD
-- =====================================================
INSERT INTO `ESPECIALIDAD` (`nombre`, `estado`, `descripcion`) VALUES
('Cardiología', 'Activo', 'Especialidad médica que se ocupa del corazón y sistema circulatorio'),
('Pediatría', 'Activo', 'Especialidad médica que se ocupa de la salud de niños y adolescentes'),
('Dermatología', 'Activo', 'Especialidad médica que se ocupa de la piel, cabello y uñas'),
('Traumatología', 'Activo', 'Especialidad médica que trata lesiones del sistema músculo-esquelético'),
('Ginecología', 'Activo', 'Especialidad médica que se ocupa del sistema reproductor femenino'),
('Oftalmología', 'Activo', 'Especialidad médica que se ocupa de los ojos y la visión'),
('Neurología', 'Activo', 'Especialidad médica que se ocupa del sistema nervioso'),
('Psiquiatría', 'Activo', 'Especialidad médica que se ocupa de la salud mental'),
('Medicina General', 'Activo', 'Atención médica general y preventiva'),
('Odontología', 'Activo', 'Especialidad que se ocupa de la salud bucal');

-- =====================================================
-- 3. TABLA: CATEGORIA
-- =====================================================
INSERT INTO `CATEGORIA` (`nombre`, `descripcion`) VALUES
('Consulta Médica', 'Consultas médicas generales y especializadas'),
('Exámenes', 'Exámenes de laboratorio y diagnóstico'),
('Cirugía', 'Procedimientos quirúrgicos'),
('Emergencia', 'Atención de emergencias médicas'),
('Vacunación', 'Servicios de vacunación'),
('Terapia', 'Terapias y rehabilitación'),
('Imagenología', 'Estudios de imagen (rayos X, ecografías, etc.)');

-- =====================================================
-- 4. TABLA: USUARIO
-- =====================================================
-- Contraseña hasheada: scrypt:32768:8:1$... (representa "password123")
INSERT INTO `USUARIO` (`correo`, `contrasena`, `telefono`, `estado`, `fecha_creacion`) VALUES
-- Administradores
('admin@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987654321', 'activo', '2024-01-01'),
('admin2@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987654322', 'activo', '2024-01-01'),

-- Médicos
('dr.garcia@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987111001', 'activo', '2024-01-15'),
('dr.martinez@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987111002', 'activo', '2024-01-15'),
('dra.lopez@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987111003', 'activo', '2024-01-16'),
('dr.rodriguez@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987111004', 'activo', '2024-01-16'),
('dra.fernandez@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987111005', 'activo', '2024-01-17'),
('dr.sanchez@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987111006', 'activo', '2024-01-17'),

-- Recepcionistas
('recepcion1@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987222001', 'activo', '2024-01-20'),
('recepcion2@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987222002', 'activo', '2024-01-20'),

-- Farmacéuticos
('farmacia1@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987333001', 'activo', '2024-01-22'),
('farmacia2@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987333002', 'activo', '2024-01-22'),

-- Laboratoristas
('lab1@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987444001', 'activo', '2024-01-25'),
('lab2@clinicaunion.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987444002', 'activo', '2024-01-25'),

-- Pacientes
('juan.perez@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555001', 'activo', '2024-02-01'),
('maria.garcia@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555002', 'activo', '2024-02-02'),
('carlos.lopez@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555003', 'activo', '2024-02-03'),
('ana.martinez@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555004', 'activo', '2024-02-04'),
('luis.rodriguez@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555005', 'activo', '2024-02-05'),
('sofia.sanchez@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555006', 'activo', '2024-02-06'),
('diego.torres@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555007', 'activo', '2024-02-07'),
('paula.diaz@email.com', 'scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3', '987555008', 'activo', '2024-02-08');

-- =====================================================
-- 5. TABLA: EMPLEADO
-- =====================================================
-- Nota: Asume que id_distrito=140312 (Chiclayo, Lambayeque) existe
-- Nota: fotoPerfil se deja NULL, se puede agregar después
INSERT INTO `EMPLEADO` (`nombres`, `apellidos`, `fecha_nacimiento`, `documento_identidad`, `sexo`, `estado`, `id_usuario`, `id_rol`, `id_distrito`, `id_especialidad`) VALUES
-- Administradores (usuarios 1-2, rol 1)
('Roberto', 'Mendoza Silva', '1980-05-15', '12345678', 'Masculino', 'Activo', 1, 1, 140312, NULL),
('Carmen', 'Vega Torres', '1982-08-20', '87654321', 'Femenino', 'Activo', 2, 1, 140312, NULL),

-- Médicos (usuarios 3-8, rol 2, especialidades 1-6)
('Carlos', 'García Ramírez', '1975-03-10', '11111001', 'Masculino', 'Activo', 3, 2, 140312, 1),  -- Cardiología
('Pedro', 'Martínez Flores', '1978-07-22', '11111002', 'Masculino', 'Activo', 4, 2, 140312, 2),  -- Pediatría
('Isabel', 'López Morales', '1980-11-05', '11111003', 'Femenino', 'Activo', 5, 2, 140312, 3),    -- Dermatología
('Miguel', 'Rodríguez Castro', '1977-09-18', '11111004', 'Masculino', 'Activo', 6, 2, 140312, 4), -- Traumatología
('Patricia', 'Fernández Ruiz', '1982-04-30', '11111005', 'Femenino', 'Activo', 7, 2, 140312, 5),  -- Ginecología
('Jorge', 'Sánchez Vega', '1979-12-12', '11111006', 'Masculino', 'Activo', 8, 2, 140312, 6),      -- Oftalmología

-- Recepcionistas (usuarios 9-10, rol 3)
('Laura', 'Campos Rios', '1990-06-15', '22222001', 'Femenino', 'Activo', 9, 3, 140312, NULL),
('Andrea', 'Torres Muñoz', '1992-03-20', '22222002', 'Femenino', 'Activo', 10, 3, 140312, NULL),

-- Farmacéuticos (usuarios 11-12, rol 4)
('Ricardo', 'Paredes León', '1985-08-25', '33333001', 'Masculino', 'Activo', 11, 4, 140312, NULL),
('Mónica', 'Díaz Silva', '1988-11-10', '33333002', 'Femenino', 'Activo', 12, 4, 140312, NULL),

-- Laboratoristas (usuarios 13-14, rol 5)
('Fernando', 'Gutiérrez Pinto', '1987-02-14', '44444001', 'Masculino', 'Activo', 13, 5, 140312, NULL),
('Gabriela', 'Rojas Mendoza', '1989-05-28', '44444002', 'Femenino', 'Activo', 14, 5, 140312, NULL);

-- =====================================================
-- 6. TABLA: PACIENTE
-- =====================================================
INSERT INTO `PACIENTE` (`nombres`, `apellidos`, `fecha_nacimiento`, `documento_identidad`, `sexo`, `id_usuario`, `id_distrito`) VALUES
('Juan Carlos', 'Pérez Gómez', '1985-03-15', '55551001', 'Masculino', 15, 140312),
('María Elena', 'García Ruiz', '1990-07-22', '55551002', 'Femenino', 16, 140312),
('Carlos Alberto', 'López Vega', '1978-11-08', '55551003', 'Masculino', 17, 140312),
('Ana Sofía', 'Martínez Torres', '1995-02-14', '55551004', 'Femenino', 18, 140312),
('Luis Miguel', 'Rodríguez Paredes', '1982-09-30', '55551005', 'Masculino', 19, 140312),
('Sofía Valentina', 'Sánchez Díaz', '1993-06-18', '55551006', 'Femenino', 20, 140312),
('Diego Alejandro', 'Torres Ríos', '1988-12-05', '55551007', 'Masculino', 21, 140312),
('Paula Andrea', 'Díaz Morales', '1991-04-27', '55551008', 'Femenino', 22, 140312);

-- =====================================================
-- 7. TABLA: HORARIO
-- =====================================================
-- Nota: id_empleado debe referenciar a empleados existentes (médicos 3-8)
INSERT INTO `HORARIO` (`id_empleado`, `fecha`, `hora_inicio`, `hora_fin`, `disponibilidad`, `estado`) VALUES
-- Dr. Carlos García (emp 3) - Cardiología
(3, '2024-12-02', '08:00:00', '12:00:00', 'Disponible', 'Activo'),
(3, '2024-12-03', '08:00:00', '12:00:00', 'Disponible', 'Activo'),
(3, '2024-12-04', '14:00:00', '18:00:00', 'Disponible', 'Activo'),

-- Dr. Pedro Martínez (emp 4) - Pediatría
(4, '2024-12-02', '09:00:00', '13:00:00', 'Disponible', 'Activo'),
(4, '2024-12-03', '14:00:00', '18:00:00', 'Disponible', 'Activo'),
(4, '2024-12-05', '09:00:00', '13:00:00', 'Disponible', 'Activo'),

-- Dra. Isabel López (emp 5) - Dermatología
(5, '2024-12-02', '07:00:00', '15:00:00', 'Disponible', 'Activo'),
(5, '2024-12-03', '07:00:00', '15:00:00', 'Disponible', 'Activo'),
(5, '2024-12-04', '07:00:00', '15:00:00', 'Disponible', 'Activo'),

-- Dr. Miguel Rodríguez (emp 6) - Traumatología
(6, '2024-12-02', '10:00:00', '14:00:00', 'Disponible', 'Activo'),
(6, '2024-12-03', '10:00:00', '14:00:00', 'Disponible', 'Activo'),
(6, '2024-12-04', '15:00:00', '19:00:00', 'Disponible', 'Activo'),

-- Dra. Patricia Fernández (emp 7) - Ginecología
(7, '2024-12-02', '13:00:00', '21:00:00', 'Disponible', 'Activo'),
(7, '2024-12-03', '13:00:00', '21:00:00', 'Disponible', 'Activo'),
(7, '2024-12-04', '13:00:00', '21:00:00', 'Disponible', 'Activo'),

-- Dr. Jorge Sánchez (emp 8) - Oftalmología
(8, '2024-12-02', '08:00:00', '14:00:00', 'Disponible', 'Activo'),
(8, '2024-12-03', '14:00:00', '20:00:00', 'Disponible', 'Activo'),
(8, '2024-12-04', '08:00:00', '14:00:00', 'Disponible', 'Activo');

-- =====================================================
-- 8. TABLA: PROGRAMACION
-- =====================================================
-- Nota: id_servicio puede ser NULL según necesidades
-- Nota: id_horario debe referenciar a horarios creados arriba
INSERT INTO `PROGRAMACION` (`fecha`, `hora_inicio`, `hora_fin`, `estado`, `id_servicio`, `id_horario`) VALUES
-- Programaciones para diciembre 2024
('2024-12-02', '08:00:00', '08:30:00', 'Activo', NULL, 1),
('2024-12-02', '08:30:00', '09:00:00', 'Activo', NULL, 1),
('2024-12-02', '09:00:00', '09:30:00', 'Activo', NULL, 2),
('2024-12-02', '09:30:00', '10:00:00', 'Activo', NULL, 2),
('2024-12-03', '08:00:00', '08:30:00', 'Activo', NULL, 3),
('2024-12-03', '14:00:00', '14:30:00', 'Activo', NULL, 4),
('2024-12-04', '07:00:00', '07:30:00', 'Activo', NULL, 7),
('2024-12-04', '15:00:00', '15:30:00', 'Activo', NULL, 12),
('2024-12-05', '09:00:00', '09:30:00', 'Activo', NULL, 6);

-- =====================================================
-- 9. TABLA: TIPO_RECURSO
-- =====================================================
INSERT INTO `TIPO_RECURSO` (`nombre`, `descripcion`) VALUES
('Consultorio Médico', 'Sala para consultas médicas'),
('Sala de Operaciones', 'Quirófano para cirugías'),
('Sala de Emergencias', 'Área de atención de emergencias'),
('Laboratorio', 'Sala de análisis clínicos'),
('Sala de Radiología', 'Área de estudios radiológicos'),
('Farmacia', 'Área de dispensación de medicamentos'),
('Sala de Espera', 'Área de espera para pacientes');

-- =====================================================
-- 10. TABLA: RECURSO
-- =====================================================
INSERT INTO `RECURSO` (`nombre`, `descripcion`, `estado`, `capacidad`, `id_tipo_recurso`) VALUES
-- Consultorios (tipo 1)
('Consultorio 101', 'Consultorio de Cardiología', 'disponible', 1, 1),
('Consultorio 102', 'Consultorio de Pediatría', 'disponible', 1, 1),
('Consultorio 103', 'Consultorio de Dermatología', 'disponible', 1, 1),
('Consultorio 104', 'Consultorio de Traumatología', 'disponible', 1, 1),
('Consultorio 105', 'Consultorio de Ginecología', 'disponible', 1, 1),
('Consultorio 106', 'Consultorio de Oftalmología', 'disponible', 1, 1),

-- Salas de Operaciones (tipo 2)
('Quirófano 1', 'Sala de operaciones principal', 'disponible', 1, 2),
('Quirófano 2', 'Sala de operaciones secundaria', 'disponible', 1, 2),

-- Emergencias (tipo 3)
('Emergencia 1', 'Sala de emergencias principal', 'disponible', 4, 3),

-- Laboratorio (tipo 4)
('Lab Principal', 'Laboratorio clínico principal', 'disponible', 3, 4),

-- Radiología (tipo 5)
('Rayos X 1', 'Sala de radiología', 'disponible', 1, 5),
('Ecografía 1', 'Sala de ecografías', 'disponible', 1, 5);

-- =====================================================
-- 11. TABLA: CITA
-- =====================================================
-- Nota: Las citas deben tener una reserva previa (id_reserva)
-- Nota: estado puede ser: Pendiente, Confirmada, Completada, Cancelada
INSERT INTO `CITA` (`fecha_cita`, `hora_inicio`, `hora_fin`, `diagnostico`, `observaciones`, `estado`, `id_reserva`) VALUES
('2024-11-15', '09:00:00', '09:30:00', 'Hipertensión arterial controlada', 'Control cardiológico rutinario', 'Completada', 1),
('2024-11-20', '10:30:00', '11:00:00', 'Desarrollo normal para la edad', 'Consulta pediátrica de rutina', 'Completada', 2),
('2024-12-01', '15:00:00', '15:30:00', NULL, 'Consulta dermatológica programada', 'Pendiente', 3),
('2024-12-05', '08:30:00', '09:00:00', NULL, 'Revisión traumatológica', 'Confirmada', 4),
('2024-12-10', '16:00:00', '16:30:00', NULL, 'Control ginecológico prenatal', 'Pendiente', 5),
('2024-12-15', '09:30:00', '10:00:00', NULL, 'Examen de vista programado', 'Confirmada', 6);

-- =====================================================
-- 12. TABLA: RESERVA
-- =====================================================
-- Nota: tipo puede ser 1 (primera vez) o 2 (control)
-- Nota: estado puede ser: Pendiente, Confirmada, Cancelada
-- Nota: id_programacion debe referenciar programaciones existentes
INSERT INTO `RESERVA` (`fecha_registro`, `hora_registro`, `tipo`, `estado`, `motivo_cancelacion`, `id_paciente`, `id_programacion`) VALUES
('2024-11-10', '14:30:00', 2, 'Confirmada', NULL, 1, 1),
('2024-11-18', '16:45:00', 1, 'Confirmada', NULL, 2, 2),
('2024-11-25', '10:20:00', 1, 'Pendiente', NULL, 3, 7),
('2024-11-28', '11:15:00', 2, 'Confirmada', NULL, 4, 8),
('2024-12-01', '09:30:00', 2, 'Pendiente', NULL, 5, 5),
('2024-12-10', '15:00:00', 1, 'Confirmada', NULL, 6, 3);

-- =====================================================
-- 13. TABLA: EXAMEN
-- =====================================================
-- Nota: estado puede ser: Pendiente, Realizado, Cancelado
-- Nota: id_reservaServicio puede ser NULL
INSERT INTO `EXAMEN` (`fecha_examen`, `hora_examen`, `observacion`, `estado`, `id_reserva`, `id_reservaServicio`) VALUES
('2024-11-16', '08:00:00', 'Hemograma completo - Valores normales', 'Realizado', 1, NULL),
('2024-11-16', '08:30:00', 'Perfil lipídico - Colesterol ligeramente elevado', 'Realizado', 1, NULL),
('2024-11-21', '09:00:00', 'Radiografía de tórax - Sin alteraciones', 'Realizado', 2, NULL),
('2024-12-16', '10:00:00', 'Examen de agudeza visual programado', 'Pendiente', 6, NULL);

-- =====================================================
-- 14. TABLA: OPERACION
-- =====================================================
-- Nota: id_reserva, id_cita pueden ser NULL según el caso
INSERT INTO `OPERACION` (`fecha_operacion`, `hora_inicio`, `hora_fin`, `observaciones`, `id_reserva`, `id_empleado`, `id_cita`) VALUES
('2024-12-02', '14:00:00', '15:00:00', 'Cirugía menor dermatológica - Extirpación de lesión cutánea', 3, 5, 3);

-- =====================================================
-- 15. TABLA: OPERACION_RECURSO (tabla intermedia)
-- =====================================================
INSERT INTO `OPERACION_RECURSO` (`id_operacion`, `id_recurso`) VALUES
(1, 7),  -- Quirófano 1
(1, 10); -- Lab Principal (para análisis post-operatorio)

-- =====================================================
-- 16. TABLA: BLOQUEO_PROGRAMACION
-- =====================================================
-- Nota: Bloqueos deben referenciar programaciones existentes
INSERT INTO `BLOQUEO_PROGRAMACION` (`fecha`, `hora_inicio`, `hora_fin`, `motivo`, `estado`, `id_programacion`) VALUES
('2024-12-20', '08:00:00', '12:00:00', 'Mantenimiento de consultorio', 'Activo', 1),
('2024-12-24', '08:00:00', '18:00:00', 'Cierre por festividades', 'Activo', 2),
('2024-12-25', '08:00:00', '18:00:00', 'Cierre por festividades', 'Activo', 3);

-- =====================================================
-- 17. TABLA: INCIDENCIA
-- =====================================================
-- Nota: categoria puede ser: Infraestructura, Insumos, Equipamiento Médico, Software, Hardware, Otro
-- Nota: prioridad puede ser: Alta, Media, Baja o NULL
INSERT INTO `INCIDENCIA` (`descripcion`, `fecha_registro`, `id_paciente`, `categoria`, `prioridad`) VALUES
('Aire acondicionado del consultorio 101 no funciona correctamente', '2024-11-20', 1, 'Infraestructura', 'Media'),
('Sistema de citas presenta errores al guardar datos', '2024-11-22', NULL, 'Software', 'Alta'),
('Falta de camillas en sala de emergencias', '2024-11-25', 3, 'Equipamiento Médico', 'Alta'),
('Computadora de recepción muy lenta', '2024-11-26', NULL, 'Hardware', 'Media'),
('Paciente reporta demora excesiva en atención', '2024-11-27', 4, 'Otro', 'Baja'),
('Falta de medicamentos en farmacia', '2024-11-28', NULL, 'Insumos', 'Alta');

-- =====================================================
-- 18. TABLA: ASIGNAR_EMPLEADO_INCIDENCIA
-- =====================================================
INSERT INTO `ASIGNAR_EMPLEADO_INCIDENCIA` (`id_incidencia`, `id_empleado`, `fecha_asignacion`) VALUES
(1, 1, '2024-11-20'),  -- Admin asignado a incidencia 1
(2, 9, '2024-11-22'),  -- Recepcionista asignada
(3, 10, '2024-11-25'), -- Recepcionista asignada
(4, 11, '2024-11-26'); -- Farmacéutico asignado

-- =====================================================
-- 19. TABLA: REPORTE
-- =====================================================
-- Nota: estado puede ser: Pendiente, En Proceso, Completado
-- Nota: tipo puede ser: Mensual, Semanal, Trimestral, Anual
-- Nota: id_servicio e id_recurso pueden ser NULL
INSERT INTO `REPORTE` (`codigo`, `nombre`, `tipo`, `descripcion`, `contenido_json`, `estado`, `fecha_creacion`, `id_categoria`, `id_empleado`, `id_servicio`, `id_recurso`) VALUES
('REP-20241201-001', 'Reporte Mensual de Citas - Noviembre 2024', 'Mensual', 'Resumen de citas atendidas en noviembre', NULL, 'Completado', '2024-12-01 08:00:00', 1, 1, NULL, NULL),
('REP-20241201-002', 'Reporte de Incidencias - Noviembre 2024', 'Mensual', 'Resumen de incidencias reportadas', NULL, 'Completado', '2024-12-01 09:00:00', 7, 1, NULL, NULL),
('REP-20241201-003', 'Reporte de Ocupación de Recursos', 'Mensual', 'Uso de consultorios y salas en noviembre', NULL, 'Completado', '2024-12-01 10:00:00', 4, 2, NULL, 1),
('REP-20241202-001', 'Reporte de Atenciones por Especialidad', 'Mensual', 'Análisis de consultas por especialidad', NULL, 'Completado', '2024-12-02 08:30:00', 6, 1, NULL, NULL);

-- =====================================================
-- 20. TABLA: REPORTE_ARCHIVO (archivos adjuntos de reportes)
-- =====================================================
-- Nota: fecha_subida es DATETIME con DEFAULT CURRENT_TIMESTAMP
INSERT INTO `REPORTE_ARCHIVO` (`id_reporte`, `nombre_archivo`, `ruta_archivo`, `tipo_archivo`, `tamano_bytes`, `fecha_subida`) VALUES
(1, 'reporte_citas_nov_2024.pdf', 'uploads/reportes/reporte_citas_nov_2024.pdf', 'application/pdf', 1024567, '2024-12-01 08:05:00'),
(2, 'incidencias_nov_2024.xlsx', 'uploads/reportes/incidencias_nov_2024.xlsx', 'application/vnd.ms-excel', 512345, '2024-12-01 09:05:00');

-- =====================================================
-- 20. TABLA: NOTIFICACION
-- =====================================================
-- Nota: tipo puede ser: Recordatorio, Confirmación, Cancelación, Cambio
INSERT INTO `NOTIFICACION` (`titulo`, `mensaje`, `tipo`, `fecha_envio`, `hora_envio`, `id_reserva`, `id_paciente`) VALUES
('Recordatorio de Cita', 'Tiene una cita mañana a las 09:00 AM con Dr. García', 'Recordatorio', '2024-11-14', '18:00:00', 1, 1),
('Cita Confirmada', 'Su cita ha sido confirmada para el 20/11/2024 a las 10:30 AM', 'Confirmación', '2024-11-15', '10:00:00', 2, 2),
('Recordatorio de Cita', 'Recordatorio: Consulta dermatológica el 01/12/2024', 'Recordatorio', '2024-11-30', '16:00:00', 3, 3),
('Cita Confirmada', 'Cita confirmada para el 05/12/2024 con Dr. Rodríguez', 'Confirmación', '2024-11-28', '14:30:00', 4, 4),
('Recordatorio de Cita', 'Recordatorio: Examen de vista programado para mañana', 'Recordatorio', '2024-12-14', '17:00:00', 6, 6);

-- =====================================================
-- 22. TABLA: AUDITORIA
-- =====================================================
-- Nota: fecha_registro es DATETIME con DEFAULT CURRENT_TIMESTAMP
INSERT INTO `AUDITORIA` (`id_usuario`, `id_empleado`, `accion`, `modulo`, `tipo_evento`, `descripcion`, `ip_address`, `fecha_registro`, `detalles_json`) VALUES
(15, NULL, 'Registro', 'Pacientes', 'Creación', 'Nuevo paciente registrado: Juan Carlos Pérez Gómez', '127.0.0.1', '2024-02-01 10:30:00', NULL),
(NULL, 1, 'Creación de Cita', 'Citas', 'Creación', 'Nueva cita creada para paciente ID 1', '127.0.0.1', '2024-11-10 14:45:00', NULL),
(NULL, 1, 'Actualización', 'Citas', 'Actualización', 'Cita ID 1 marcada como completada', '127.0.0.1', '2024-11-16 09:30:00', NULL),
(NULL, 1, 'Registro de Empleado', 'Empleados', 'Creación', 'Nuevo médico registrado: Dr. Carlos García', '127.0.0.1', '2024-01-15 08:00:00', NULL),
(15, NULL, 'Creación de Reserva', 'Reservas', 'Creación', 'Nueva reserva creada para cita médica', '192.168.1.100', '2024-11-10 14:30:00', NULL),
(15, NULL, 'Actualización de Perfil', 'Usuarios', 'Actualización', 'Usuario ID 15 actualizó su perfil', '192.168.1.100', '2024-11-15 16:20:00', NULL),
(NULL, 9, 'Registro de Incidencia', 'Incidencias', 'Creación', 'Nueva incidencia registrada por recepcionista', '127.0.0.1', '2024-11-20 11:00:00', NULL),
(NULL, 5, 'Programación de Operación', 'Operaciones', 'Creación', 'Nueva operación programada para el 02/12/2024', '127.0.0.1', '2024-11-25 15:30:00', NULL);

-- =====================================================
-- 23. TABLA: AUDITORIA_ARCHIVO (archivos de auditoría)
-- =====================================================
-- Nota: fecha_subida es DATETIME con DEFAULT CURRENT_TIMESTAMP
INSERT INTO `AUDITORIA_ARCHIVO` (`id_auditoria`, `nombre_archivo`, `ruta_archivo`, `tipo_archivo`, `tamano_bytes`, `fecha_subida`) VALUES
(1, 'registro_paciente_001.pdf', 'uploads/auditoria/registro_paciente_001.pdf', 'application/pdf', 256789, '2024-02-01 10:35:00'),
(6, 'modificacion_perfil_015.log', 'uploads/auditoria/modificacion_perfil_015.log', 'text/plain', 4567, '2024-11-15 16:25:00');

-- =====================================================
-- 24. TABLA: RECURSO_ARCHIVO (archivos de recursos)
-- =====================================================
-- Nota: fecha_subida es DATETIME con DEFAULT CURRENT_TIMESTAMP
INSERT INTO `RECURSO_ARCHIVO` (`id_recurso`, `nombre_archivo`, `ruta_archivo`, `tipo_archivo`, `tamano_bytes`, `fecha_subida`) VALUES
(1, 'plano_consultorio_101.pdf', 'uploads/recursos/plano_consultorio_101.pdf', 'application/pdf', 512000, '2024-01-10 09:00:00'),
(7, 'inventario_quirofano_1.xlsx', 'uploads/recursos/inventario_quirofano_1.xlsx', 'application/vnd.ms-excel', 128456, '2024-01-15 10:30:00');

-- =====================================================
-- 25. TABLA: RECUPERACION_CONTRASENA
-- =====================================================
-- Nota: usado es TINYINT(1) donde 0=no usado, 1=usado
-- Nota: fecha_creacion es TIMESTAMP con DEFAULT CURRENT_TIMESTAMP
INSERT INTO `RECUPERACION_CONTRASENA` (`id_usuario`, `codigo`, `fecha_creacion`, `usado`) VALUES
(17, '123456', '2024-11-15 10:30:00', 1),
(18, '789012', '2024-11-20 14:20:00', 0);

-- Habilitar verificación de claves foráneas
SET FOREIGN_KEY_CHECKS=1;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
-- Para verificar los datos insertados:
-- SELECT * FROM ROL;
-- SELECT * FROM ESPECIALIDAD;
-- SELECT * FROM USUARIO;
-- SELECT * FROM EMPLEADO;
-- SELECT * FROM PACIENTE;
-- SELECT * FROM CITA;
-- etc.
-- =====================================================
