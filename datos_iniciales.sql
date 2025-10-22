-- Insertar datos iniciales para DEPARTAMENTO, PROVINCIA y DISTRITO
-- Estos son necesarios para el registro de pacientes

-- Departamentos (algunos ejemplos del Perú)
INSERT INTO DEPARTAMENTO (nombre) VALUES 
('Lima'),
('Lambayeque'),
('La Libertad'),
('Arequipa'),
('Cusco'),
('Piura');

-- Provincias (ejemplos)
INSERT INTO PROVINCIA (nombre, id_departamento) VALUES 
('Lima', 1),
('Chiclayo', 2),
('Trujillo', 3),
('Arequipa', 4),
('Cusco', 5),
('Piura', 6);

-- Distritos (ejemplos)
INSERT INTO DISTRITO (nombre, id_provincia) VALUES 
('Miraflores', 1),
('San Isidro', 1),
('Surco', 1),
('Chiclayo', 2),
('José Leonardo Ortiz', 2),
('Trujillo', 3),
('Arequipa', 4),
('Cusco', 5),
('Piura', 6);

-- Insertar roles básicos
INSERT INTO ROL (nombre, descripcion) VALUES 
('Administrador', 'Acceso total al sistema'),
('Médico', 'Puede gestionar citas y pacientes'),
('Recepcionista', 'Puede gestionar reservas y citas'),
('Paciente', 'Usuario paciente con acceso limitado');

-- Insertar especialidades básicas
INSERT INTO ESPECIALIDAD (nombre, descripcion) VALUES 
('Cardiología', 'Especialidad médica del corazón y sistema cardiovascular'),
('Neurología', 'Especialidad médica del sistema nervioso'),
('Traumatología', 'Especialidad médica del sistema músculo-esquelético'),
('Pediatría', 'Especialidad médica de la salud infantil'),
('Ginecología', 'Especialidad médica de la salud femenina'),
('Medicina General', 'Atención médica general');
