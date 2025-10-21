CREATE TABLE DEPARTAMENTO (
  id_departamento INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL
);

CREATE TABLE PROVINCIA (
  id_provincia INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_departamento INT NOT NULL,
  FOREIGN KEY (id_departamento) REFERENCES DEPARTAMENTO(id_departamento)
);

CREATE TABLE DISTRITO (
  id_distrito INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_provincia INT NOT NULL,
  FOREIGN KEY (id_provincia) REFERENCES PROVINCIA(id_provincia)
);

CREATE TABLE ROL (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  descripcion TEXT,
  estado VARCHAR(20)
);

CREATE TABLE ESPECIALIDAD (
  id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  estado VARCHAR(20)
);

CREATE TABLE EMPLEADO (
  id_empleado INT AUTO_INCREMENT PRIMARY KEY,
  nombres VARCHAR(100) NOT NULL,
  apellidos VARCHAR(100) NOT NULL,
  documento VARCHAR(20) NOT NULL UNIQUE,
  correoEmpleado VARCHAR(100) NOT NULL,
  contraseñaEmpleado VARCHAR(200) NOT NULL,
  cargo VARCHAR(50),
  contacto VARCHAR(100),
  especialidad VARCHAR(100),
  estado VARCHAR(20),
  id_rol INT NOT NULL,
  id_departamento INT NOT NULL,
  id_provincia INT NOT NULL,
  id_distrito INT NOT NULL,
  id_especialidad INT NOT NULL,
  FOREIGN KEY (id_rol) REFERENCES ROL(id_rol),
  FOREIGN KEY (id_departamento) REFERENCES DEPARTAMENTO(id_departamento),
  FOREIGN KEY (id_provincia) REFERENCES PROVINCIA(id_provincia),
  FOREIGN KEY (id_distrito) REFERENCES DISTRITO(id_distrito),
  FOREIGN KEY (id_especialidad) REFERENCES ESPECIALIDAD(id_especialidad)
);

CREATE TABLE TIPO_SERVICIO (
  id_tipo_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT
);

CREATE TABLE SERVICIO (
  id_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  duracion_estimada INT,
  estado VARCHAR(20),
  id_tipo_servicio INT NOT NULL,
  id_especialidad INT NOT NULL,
  FOREIGN KEY (id_tipo_servicio) REFERENCES TIPO_SERVICIO(id_tipo_servicio),
  FOREIGN KEY (id_especialidad) REFERENCES ESPECIALIDAD(id_especialidad)
);

CREATE TABLE TIPO_RECURSO (
  id_tipo_recurso INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  descripcion TEXT
);

CREATE TABLE RECURSO (
  id_recurso INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  estado VARCHAR(20),
  id_tipo_recurso INT NOT NULL,
  FOREIGN KEY (id_tipo_recurso) REFERENCES TIPO_RECURSO(id_tipo_recurso)
);

CREATE TABLE SERVICIO_RECURSO (
  id_servicio_recurso INT AUTO_INCREMENT PRIMARY KEY,
  cantidad_requerida INT,
  id_servicio INT NOT NULL,
  id_recurso INT NOT NULL,
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio),
  FOREIGN KEY (id_recurso) REFERENCES RECURSO(id_recurso)
);

CREATE TABLE PACIENTE (
  id_paciente INT AUTO_INCREMENT PRIMARY KEY,
  nombres VARCHAR(100) NOT NULL,
  apellidos VARCHAR(100) NOT NULL,
  documento_identidad VARCHAR(20) NOT NULL UNIQUE,
  telefono VARCHAR(20),
  correo VARCHAR(100) NOT NULL,
  contraseña VARCHAR(200) NOT NULL,
  fecha_nacimiento DATE,
  estado VARCHAR(20),
  id_departamento INT NOT NULL,
  id_provincia INT NOT NULL,
  id_distrito INT NOT NULL,
  FOREIGN KEY (id_departamento) REFERENCES DEPARTAMENTO(id_departamento),
  FOREIGN KEY (id_provincia) REFERENCES PROVINCIA(id_provincia),
  FOREIGN KEY (id_distrito) REFERENCES DISTRITO(id_distrito)
);

CREATE TABLE PROGRAMACION (
  id_programacion INT AUTO_INCREMENT PRIMARY KEY,
  dia_semana VARCHAR(15) NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  disponibilidad TINYINT(1),
  estado VARCHAR(20),
  id_empleado INT NOT NULL,
  id_servicio INT NOT NULL,
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio)
);

CREATE TABLE BLOQUEO_PROGRAMACION (
  id_bloqueo INT AUTO_INCREMENT PRIMARY KEY,
  fecha DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  motivo TEXT,
  estado VARCHAR(20),
  id_programacion INT NOT NULL,
  FOREIGN KEY (id_programacion) REFERENCES PROGRAMACION(id_programacion)
);

CREATE TABLE RESERVA (
  id_reserva INT AUTO_INCREMENT PRIMARY KEY,
  fecha_reserva DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  estado VARCHAR(20),
  motivo_cancelacion TEXT,
  fecha_creacion TIMESTAMP,
  id_paciente INT NOT NULL,
  id_servicio INT NOT NULL,
  id_programacion INT NOT NULL,
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente),
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio),
  FOREIGN KEY (id_programacion) REFERENCES PROGRAMACION(id_programacion)
);

CREATE TABLE CITA (
  id_cita INT AUTO_INCREMENT PRIMARY KEY,
  fecha_cita DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  diagnostico TEXT,
  observaciones TEXT,
  estado VARCHAR(20),
  id_reserva INT NOT NULL,
  id_empleado INT NOT NULL,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado)
);

CREATE TABLE CAMBIO (
  id_cambio INT AUTO_INCREMENT PRIMARY KEY,
  fecha_anterior DATE,
  hora_anterior TIME,
  fecha_nueva DATE,
  hora_nueva TIME,
  motivo TEXT,
  aprobado TINYINT(1),
  fecha_registro TIMESTAMP,
  id_reserva INT NOT NULL,
  id_paciente INT NOT NULL,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente)
);

CREATE TABLE NOTIFICACION (
  id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255),
  mensaje TEXT,
  tipo VARCHAR(30),
  fecha_envio TIMESTAMP,
  estado VARCHAR(20),
  id_reserva INT NOT NULL,
  id_cambio INT NOT NULL,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_cambio) REFERENCES CAMBIO(id_cambio)
);

CREATE TABLE CITA_RECURSO (
  id_cita_recurso INT AUTO_INCREMENT PRIMARY KEY,
  estado VARCHAR(20),
  id_cita INT NOT NULL,
  id_recurso INT NOT NULL,
  FOREIGN KEY (id_cita) REFERENCES CITA(id_cita),
  FOREIGN KEY (id_recurso) REFERENCES RECURSO(id_recurso)
);

CREATE TABLE CATEGORIA (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT
);

CREATE TABLE REPORTE_OCUPACION (
  id_reporte INT AUTO_INCREMENT PRIMARY KEY,
  fecha_inicio_periodo DATE,
  fecha_fin_periodo DATE,
  porcentaje_uso DECIMAL(5,2),
  tiempo_total_ocupado INT,
  tiempo_disponible INT,
  fecha_generacion TIMESTAMP,
  observaciones TEXT,
  id_servicio_recurso INT NOT NULL,
  FOREIGN KEY (id_servicio_recurso) REFERENCES SERVICIO_RECURSO(id_servicio_recurso)
);

CREATE TABLE REPORTE (
  id_reporte INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL,
  nombre VARCHAR(100),
  tipo VARCHAR(50),
  fecha_creacion TIMESTAMP,
  id_categoria INT NOT NULL,
  usuario_responsable INT NOT NULL,
  id_servicio_recurso INT NOT NULL,
  FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(id_categoria),
  FOREIGN KEY (usuario_responsable) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_servicio_recurso) REFERENCES SERVICIO_RECURSO(id_servicio_recurso)
);

CREATE TABLE registro_actividad (
  id_registro INT AUTO_INCREMENT PRIMARY KEY,
  fecha_hora TIMESTAMP,
  id_usuario INT,
  entidad_afectada VARCHAR(50),
  id_entidad INT,
  accion VARCHAR(30),
  descripcion TEXT,
  ip_origen VARCHAR(50),
  FOREIGN KEY (id_usuario) REFERENCES EMPLEADO(id_empleado)
);

CREATE TABLE INCIDENCIA (
  id_incidencia INT AUTO_INCREMENT PRIMARY KEY,
  fecha_reporte TIMESTAMP NOT NULL,
  descripcion TEXT NOT NULL,
  estado VARCHAR(20),
  prioridad VARCHAR(30),
  categoria VARCHAR(50),
  fecha_resolucion DATE,
  observacion INT,
  id_responsable INT NOT NULL,
  id_paciente INT NOT NULL,
  FOREIGN KEY (id_responsable) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente)
);

-- INSERTAR ROLES PREDEFINIDOS

INSERT INTO ROL (nombre, descripcion, estado)
VALUES 
('Administrador', 'Acceso completo al sistema y gestión de usuarios, servicios y reportes', 'Activo'),
('Recepcionista', 'Encargado del registro de pacientes y gestión de citas', 'Activo'),
('Médico', 'Atiende citas, gestiona historiales y diagnósticos de pacientes', 'Activo'),
('Enfermero', 'Apoya en atención médica y control de recursos clínicos', 'Activo');

INSERT INTO DEPARTAMENTO (id_departamento, nombre) VALUES
(1, 'Tumbes'),
(2, 'Piura'),
(3, 'Lambayeque'),
(4, 'La Libertad'),
(5, 'Cajamarca');

-- ==========================================================
-- 🏙️ PROVINCIAS
-- ==========================================================
INSERT INTO PROVINCIA (id_provincia, nombre, id_departamento) VALUES
-- TUMBES
(1, 'Tumbes', 1),
(2, 'Zarumilla', 1),
(3, 'Contralmirante Villar', 1),

-- PIURA
(4, 'Piura', 2),
(5, 'Sullana', 2),
(6, 'Talara', 2),
(7, 'Paita', 2),
(8, 'Sechura', 2),
(9, 'Morropon', 2),

-- LAMBAYEQUE
(10, 'Chiclayo', 3),
(11, 'Lambayeque', 3),
(12, 'Ferreñafe', 3),

-- LA LIBERTAD
(13, 'Trujillo', 4),
(14, 'Chepén', 4),
(15, 'Pacasmayo', 4),

-- CAJAMARCA
(16, 'Cajamarca', 5),
(17, 'Jaén', 5),
(18, 'Cutervo', 5);

-- ==========================================================
-- 📍 DISTRITOS
-- ==========================================================
INSERT INTO DISTRITO (nombre, id_provincia) VALUES
-- ===== TUMBES =====
('Tumbes', 1),
('Corrales', 1),
('La Cruz', 1),
('Zarumilla', 2),
('Aguas Verdes', 2),
('Papayal', 2),
('Zorritos', 3),
('Canoas de Punta Sal', 3),

-- ===== PIURA =====
('Piura', 4),
('Castilla', 4),
('Catacaos', 4),
('Cura Mori', 4),
('Sullana', 5),
('Bellavista', 5),
('Marcavelica', 5),
('Querecotillo', 5),
('Pariñas', 6),
('Los Órganos', 6),
('Máncora', 6),
('El Alto', 6),
('Paita', 7),
('Colán', 7),
('La Huaca', 7),
('Sechura', 8),
('Vice', 8),
('Cristo Nos Valga', 8),
('Chulucanas', 9),
('Morropón', 9),
('La Matanza', 9),

-- ===== LAMBAYEQUE =====
('Chiclayo', 10),
('José Leonardo Ortiz', 10),
('La Victoria', 10),
('Pimentel', 10),
('Lambayeque', 11),
('Mochumí', 11),
('Túcume', 11),
('Ferreñafe', 12),
('Pítipo', 12),
('Incahuasi', 12),

-- ===== LA LIBERTAD =====
('Trujillo', 13),
('La Esperanza', 13),
('Florencia de Mora', 13),
('Víctor Larco Herrera', 13),
('Chepén', 14),
('Pacanga', 14),
('Pueblo Nuevo', 14),
('Pacasmayo', 15),
('San Pedro de Lloc', 15),
('Guadalupe', 15),

-- ===== CAJAMARCA =====
('Cajamarca', 16),
('Los Baños del Inca', 16),
('Magdalena', 16),
('Jaén', 17),
('Bellavista', 17),
('Pomahuaca', 17),
('Cutervo', 18),
('Querocotillo', 18),
('San Andrés de Cutervo', 18);

INSERT INTO ESPECIALIDAD (nombre, descripcion, estado) VALUES
('Otorrinolaringología', 'Diagnóstico y tratamiento de enfermedades del oído, nariz y garganta', 'Activo'),
('Neurología', 'Trata trastornos del sistema nervioso central y periférico', 'Activo'),
('Gastroenterología', 'Trata enfermedades del sistema digestivo', 'Activo'),
('Dermatología', 'Estudia y trata enfermedades de la piel', 'Activo'),
('Neurocirugía', 'Cirugía del cerebro y sistema nervioso', 'Activo'),
('Endocrinología', 'Trata enfermedades hormonales y metabólicas', 'Activo'),
('Urología', 'Diagnóstico y tratamiento del aparato urinario y reproductor masculino', 'Activo'),
('Medicina interna', 'Atención integral de adultos sin cirugía', 'Activo'),
('Traumatología', 'Trata lesiones del sistema musculoesquelético', 'Activo'),
('Cirugía general', 'Procedimientos quirúrgicos no especializados', 'Activo'),
('Pediatría', 'Atiende la salud infantil y adolescente', 'Activo'),
('Ginecología', 'Salud del sistema reproductor femenino', 'Activo'),
('Cardiología', 'Trata enfermedades del corazón y sistema circulatorio', 'Activo'),
('Cirugía plástica', 'Reparación o modificación de estructuras corporales', 'Activo');
