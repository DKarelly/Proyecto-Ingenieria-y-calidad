-- =====================================================
-- BASE DE DATOS: CLÍNICA / HOSPITAL (Modelo ER completo)
-- Compatible con MySQL 8.x
-- =====================================================

-- =======================================
-- TABLA: DEPARTAMENTO
-- =======================================
CREATE TABLE DEPARTAMENTO (
  id_departamento INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL
);

-- =======================================
-- TABLA: PROVINCIA
-- =======================================
CREATE TABLE PROVINCIA (
  id_provincia INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_departamento INT,
  FOREIGN KEY (id_departamento) REFERENCES DEPARTAMENTO(id_departamento)
);

-- =======================================
-- TABLA: DISTRITO
-- =======================================
CREATE TABLE DISTRITO (
  id_distrito INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_provincia INT,
  FOREIGN KEY (id_provincia) REFERENCES PROVINCIA(id_provincia)
);

-- =======================================
-- TABLA: ROL
-- =======================================
CREATE TABLE ROL (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  estado VARCHAR(20)
);

-- =======================================
-- TABLA: USUARIO
-- =======================================
CREATE TABLE USUARIO (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  correo VARCHAR(100),
  contrasena VARCHAR(100),
  telefono VARCHAR(9),
  estado VARCHAR(20),
  fecha_creacion DATE
);

-- =======================================
-- TABLA: ESPECIALIDAD
-- =======================================
CREATE TABLE ESPECIALIDAD (
  id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  estado VARCHAR(20),
  descripcion TEXT
);

-- =======================================
-- TABLA: EMPLEADO
-- =======================================
CREATE TABLE EMPLEADO (
  id_empleado INT AUTO_INCREMENT PRIMARY KEY,
  nombres VARCHAR(100),
  apellidos VARCHAR(100),
  documento_identidad VARCHAR(20) UNIQUE,
  sexo VARCHAR(20),
  estado VARCHAR(20),
  id_usuario INT,
  id_rol INT,
  id_distrito INT,
  id_especialidad INT,
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario),
  FOREIGN KEY (id_rol) REFERENCES ROL(id_rol),
  FOREIGN KEY (id_distrito) REFERENCES DISTRITO(id_distrito),
  FOREIGN KEY (id_especialidad) REFERENCES ESPECIALIDAD(id_especialidad)
);

-- =======================================
-- TABLA: PACIENTE
-- =======================================
CREATE TABLE PACIENTE (
  id_paciente INT AUTO_INCREMENT PRIMARY KEY,
  nombres VARCHAR(100),
  apellidos VARCHAR(100),
  documento_identidad VARCHAR(20) UNIQUE,
  sexo VARCHAR(20),
  fecha_nacimiento DATE,
  id_usuario INT,
  id_distrito INT,
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario),
  FOREIGN KEY (id_distrito) REFERENCES DISTRITO(id_distrito)
);

-- =======================================
-- TABLA: HORARIO
-- =======================================
CREATE TABLE HORARIO (
  id_horario INT AUTO_INCREMENT PRIMARY KEY,
  id_empleado INT,
  fecha DATE,
  hora_inicio TIME,
  hora_fin TIME,
  estado VARCHAR(20),
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado)
);

-- =======================================
-- TABLA: TIPO_SERVICIO
-- =======================================
CREATE TABLE TIPO_SERVICIO (
  id_tipo_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  descripcion TEXT
);

-- =======================================
-- TABLA: SERVICIO
-- =======================================
CREATE TABLE SERVICIO (
  id_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  descripcion TEXT,
  estado VARCHAR(20),
  id_tipo_servicio INT,
  id_especialidad INT,
  FOREIGN KEY (id_tipo_servicio) REFERENCES TIPO_SERVICIO(id_tipo_servicio),
  FOREIGN KEY (id_especialidad) REFERENCES ESPECIALIDAD(id_especialidad)
);

-- =======================================
-- TABLA: PROGRAMACION
-- =======================================
CREATE TABLE PROGRAMACION (
  id_programacion INT AUTO_INCREMENT PRIMARY KEY,
  fecha DATE,
  hora_inicio TIME,
  hora_fin TIME,
  estado VARCHAR(20),
  id_servicio INT,
  id_horario INT,
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio),
  FOREIGN KEY (id_horario) REFERENCES HORARIO(id_horario)
);

-- =======================================
-- TABLA: BLOQUEO_PROGRAMACION
-- =======================================
CREATE TABLE BLOQUEO_PROGRAMACION (
  id_bloqueo INT AUTO_INCREMENT PRIMARY KEY,
  fecha DATE,
  hora_inicio TIME,
  hora_fin TIME,
  motivo TEXT,
  estado VARCHAR(20),
  id_programacion INT,
  FOREIGN KEY (id_programacion) REFERENCES PROGRAMACION(id_programacion)
);

-- =======================================
-- TABLA: RESERVA
-- =======================================
CREATE TABLE RESERVA (
  id_reserva INT AUTO_INCREMENT PRIMARY KEY,
  fecha_registro DATE,
  hora_registro TIME,
  tipo INT,
  estado VARCHAR(20),
  motivo_cancelacion VARCHAR(200),
  id_paciente INT,
  id_programacion INT,
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente),
  FOREIGN KEY (id_programacion) REFERENCES PROGRAMACION(id_programacion)
);

-- =======================================
-- TABLA: CITA
-- =======================================
CREATE TABLE CITA (
  id_cita INT AUTO_INCREMENT PRIMARY KEY,
  fecha_cita DATE,
  hora_inicio TIME,
  hora_fin TIME,
  diagnostico TEXT,
  observaciones TEXT,
  estado VARCHAR(20),
  id_reserva INT,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva)
);

-- =======================================
-- TABLA: TIPO_RECURSO
-- =======================================
CREATE TABLE TIPO_RECURSO (
  id_tipo_recurso INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50),
  descripcion TEXT
);

-- =======================================
-- TABLA: RECURSO
-- =======================================
CREATE TABLE RECURSO (
  id_recurso INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  estado VARCHAR(20),
  id_tipo_recurso INT,
  FOREIGN KEY (id_tipo_recurso) REFERENCES TIPO_RECURSO(id_tipo_recurso)
);

-- =======================================
-- TABLA: OPERACION
-- =======================================
CREATE TABLE OPERACION (
  id_operacion INT AUTO_INCREMENT PRIMARY KEY,
  fecha_operacion DATE,
  hora_inicio TIME,
  hora_fin TIME,
  observaciones TEXT,
  id_reserva INT,
  id_empleado INT,
  id_cita INT,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_cita) REFERENCES CITA(id_cita)
);

-- =======================================
-- TABLA: OPERACION_RECURSO
-- =======================================
CREATE TABLE OPERACION_RECURSO (
  id_operacion_recurso INT AUTO_INCREMENT PRIMARY KEY,
  id_operacion INT,
  id_recurso INT,
  FOREIGN KEY (id_operacion) REFERENCES OPERACION(id_operacion),
  FOREIGN KEY (id_recurso) REFERENCES RECURSO(id_recurso)
);

-- =======================================
-- TABLA: EXAMEN
-- =======================================
CREATE TABLE EXAMEN (
  id_examen INT AUTO_INCREMENT PRIMARY KEY,
  fecha_examen DATE,
  hora_examen TIME,
  observacion TEXT,
  estado VARCHAR(20),
  id_reserva INT,
  id_reservaServicio INT,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_reservaServicio) REFERENCES RESERVA(id_reserva)
);

-- =======================================
-- TABLA: INCIDENCIA
-- =======================================
CREATE TABLE INCIDENCIA (
  id_incidencia INT AUTO_INCREMENT PRIMARY KEY,
  descripcion TEXT,
  fecha_registro DATE,
  id_paciente INT,
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente)
);

-- =======================================
-- TABLA: ASIGNAR_EMPLEADO_INCIDENCIA
-- =======================================
CREATE TABLE ASIGNAR_EMPLEADO_INCIDENCIA (
  id_historial INT AUTO_INCREMENT PRIMARY KEY,
  observaciones VARCHAR(200),
  estado_historial VARCHAR(20),
  fecha_resolucion DATE,
  id_empleado INT,
  id_incidencia INT,
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_incidencia) REFERENCES INCIDENCIA(id_incidencia)
);

-- =======================================
-- TABLA: NOTIFICACION
-- =======================================
CREATE TABLE NOTIFICACION (
  id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255),
  mensaje TEXT,
  tipo VARCHAR(30),
  fecha_envio DATE,
  hora_envio TIME,
  id_reserva INT,
  id_paciente INT,
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente),
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva)
);

-- =======================================
-- TABLA: CATEGORIA
-- =======================================
CREATE TABLE CATEGORIA (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  descripcion TEXT
);

-- =======================================
-- TABLA: REPORTE
-- =======================================
CREATE TABLE REPORTE (
  id_reporte INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50),
  nombre VARCHAR(100),
  tipo VARCHAR(50),
  fecha_creacion TIMESTAMP,
  id_categoria INT,
  id_empleado INT,
  id_servicio INT,
  id_recurso INT,
  FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(id_categoria),
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio),
  FOREIGN KEY (id_recurso) REFERENCES RECURSO(id_recurso)
);

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
