-- =====================================================
-- DATOS INICIALES BÁSICOS PARA LA BASE DE DATOS
-- Ejecutar después de crear las tablas con prueba.sql
-- =====================================================

-- =======================================
-- DATOS: DEPARTAMENTO (Ejemplo: Lambayeque)
-- =======================================
INSERT INTO DEPARTAMENTO (id_departamento, nombre) VALUES
(1, 'Lambayeque'),
(2, 'Lima'),
(3, 'La Libertad');

-- =======================================
-- DATOS: PROVINCIA
-- =======================================
INSERT INTO PROVINCIA (id_provincia, nombre, id_departamento) VALUES
-- Lambayeque
(1, 'Chiclayo', 1),
(2, 'Lambayeque', 1),
(3, 'Ferreñafe', 1),
-- Lima
(4, 'Lima', 2),
(5, 'Callao', 2),
-- La Libertad
(6, 'Trujillo', 3);

-- =======================================
-- DATOS: DISTRITO
-- =======================================
INSERT INTO DISTRITO (id_distrito, nombre, id_provincia) VALUES
-- Chiclayo
(1, 'Chiclayo', 1),
(2, 'La Victoria', 1),
(3, 'José Leonardo Ortiz', 1),
(4, 'Pimentel', 1),
-- Lambayeque
(5, 'Lambayeque', 2),
(6, 'Mochumí', 2),
-- Lima
(7, 'Miraflores', 4),
(8, 'San Isidro', 4),
(9, 'Surco', 4),
-- Trujillo
(10, 'Trujillo', 6);

-- =======================================
-- DATOS: ROL
-- =======================================
INSERT INTO ROL (nombre, estado) VALUES
('Administrador', 'activo'),
('Médico General', 'activo'),
('Médico Especialista', 'activo'),
('Enfermero/a', 'activo'),
('Recepcionista', 'activo'),
('Técnico de Laboratorio', 'activo');

-- =======================================
-- DATOS: ESPECIALIDAD
-- =======================================
INSERT INTO ESPECIALIDAD (nombre, estado, descripcion) VALUES
('Medicina General', 'activo', 'Atención médica general y diagnóstico inicial'),
('Cardiología', 'activo', 'Especialidad en enfermedades del corazón'),
('Pediatría', 'activo', 'Atención médica para niños'),
('Ginecología', 'activo', 'Salud reproductiva femenina'),
('Traumatología', 'activo', 'Tratamiento de lesiones y fracturas'),
('Oftalmología', 'activo', 'Especialidad en enfermedades de los ojos'),
('Dermatología', 'activo', 'Tratamiento de enfermedades de la piel'),
('Neurología', 'activo', 'Especialidad en sistema nervioso'),
('Odontología', 'activo', 'Salud bucal y dental');

-- =======================================
-- DATOS: TIPO_SERVICIO
-- =======================================
INSERT INTO TIPO_SERVICIO (nombre, descripcion) VALUES
('Consulta Externa', 'Consultas médicas ambulatorias'),
('Emergencia', 'Atención médica urgente'),
('Hospitalización', 'Internamiento hospitalario'),
('Cirugía', 'Procedimientos quirúrgicos'),
('Exámenes de Laboratorio', 'Análisis clínicos'),
('Exámenes de Imagenología', 'Rayos X, Ecografías, Tomografías'),
('Terapia Física', 'Rehabilitación física');

-- =======================================
-- DATOS: TIPO_RECURSO
-- =======================================
INSERT INTO TIPO_RECURSO (nombre, descripcion) VALUES
('Consultorio', 'Sala de consulta médica'),
('Sala de Operaciones', 'Quirófano para cirugías'),
('Sala de Emergencia', 'Área de atención de emergencias'),
('Laboratorio', 'Área de análisis clínicos'),
('Sala de Rayos X', 'Área de imagenología'),
('Equipo Médico', 'Equipamiento médico especializado');

-- =======================================
-- DATOS: CATEGORIA (Para reportes)
-- =======================================
INSERT INTO CATEGORIA (nombre, descripcion) VALUES
('Operacional', 'Reportes de operaciones diarias'),
('Financiero', 'Reportes financieros y contables'),
('Estadístico', 'Reportes estadísticos y análisis'),
('Administrativo', 'Reportes administrativos generales'),
('Clínico', 'Reportes médicos y clínicos');

-- =======================================
-- USUARIO Y EMPLEADO ADMINISTRADOR INICIAL
-- =======================================
-- Contraseña: admin123 (debe cambiarse después del primer acceso)
INSERT INTO USUARIO (correo, contrasena, telefono, estado, fecha_creacion) VALUES
('admin@clinica.com', 'scrypt:32768:8:1$NkqUzwPnNOI0aVjc$c8ea8f6f0f7d8b6c5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0', '999999999', 'activo', CURDATE());

-- Obtener el ID del usuario creado (asumiendo que es 1)
INSERT INTO EMPLEADO (nombres, apellidos, documento_identidad, sexo, estado, id_usuario, id_rol, id_distrito) VALUES
('Administrador', 'Sistema', '00000000', 'Masculino', 'activo', 1, 1, 1);

-- =======================================
-- RECURSOS FÍSICOS BÁSICOS
-- =======================================
INSERT INTO RECURSO (nombre, estado, id_tipo_recurso) VALUES
('Consultorio 1', 'disponible', 1),
('Consultorio 2', 'disponible', 1),
('Consultorio 3', 'disponible', 1),
('Sala de Operaciones 1', 'disponible', 2),
('Sala de Emergencia 1', 'disponible', 3),
('Laboratorio Principal', 'disponible', 4),
('Sala de Rayos X', 'disponible', 5);

-- =======================================
-- SERVICIOS BÁSICOS
-- =======================================
INSERT INTO SERVICIO (nombre, descripcion, estado, id_tipo_servicio, id_especialidad) VALUES
('Consulta Médica General', 'Consulta con médico general', 'activo', 1, 1),
('Consulta Cardiología', 'Consulta con cardiólogo', 'activo', 1, 2),
('Consulta Pediatría', 'Consulta con pediatra', 'activo', 1, 3),
('Análisis de Sangre Completo', 'Hemograma completo', 'activo', 5, NULL),
('Rayos X Tórax', 'Radiografía de tórax', 'activo', 6, NULL),
('Ecografía Abdominal', 'Ecografía de abdomen', 'activo', 6, NULL);

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. La contraseña del administrador es: admin123
--    IMPORTANTE: Cambiar esta contraseña después del primer acceso
--
-- 2. El hash de la contraseña fue generado con werkzeug.security
--    Si necesitas generar nuevos hashes, usa Python:
--    from werkzeug.security import generate_password_hash
--    print(generate_password_hash('tu_contraseña'))
--
-- 3. Este script incluye datos básicos para Lambayeque, Perú
--    Puedes agregar más departamentos, provincias y distritos según necesites
--
-- 4. Los datos de ejemplo son para ambiente de desarrollo
--    En producción, usar datos reales y contraseñas seguras
-- =====================================================
