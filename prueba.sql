CREATE TABLE DEPARTAMENTO (
  id_departamento INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PROVINCIA (
  id_provincia INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_departamento INT NOT NULL,
  FOREIGN KEY (id_departamento) REFERENCES DEPARTAMENTO(id_departamento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE DISTRITO (
  id_distrito INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_provincia INT NOT NULL,
  FOREIGN KEY (id_provincia) REFERENCES PROVINCIA(id_provincia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ROL (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  descripcion TEXT,
  estado VARCHAR(20) DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ESPECIALIDAD (
  id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  estado VARCHAR(20) DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE EMPLEADO (
  id_empleado INT AUTO_INCREMENT PRIMARY KEY,
  nombres VARCHAR(100) NOT NULL,
  apellidos VARCHAR(100) NOT NULL,
  documento VARCHAR(20) NOT NULL UNIQUE,
  cargo VARCHAR(50),
  contacto VARCHAR(100),
  especialidad VARCHAR(100),
  estado VARCHAR(20) DEFAULT 'activo',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE TIPO_SERVICIO (
  id_tipo_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE SERVICIO (
  id_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  duracion_estimada INT,
  estado VARCHAR(20) DEFAULT 'activo',
  id_tipo_servicio INT NOT NULL,
  id_especialidad INT NOT NULL,
  FOREIGN KEY (id_tipo_servicio) REFERENCES TIPO_SERVICIO(id_tipo_servicio),
  FOREIGN KEY (id_especialidad) REFERENCES ESPECIALIDAD(id_especialidad)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE TIPO_RECURSO (
  id_tipo_recurso INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE RECURSO (
  id_recurso INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  ubicacion VARCHAR(100),
  estado VARCHAR(20) DEFAULT 'disponible',
  id_tipo_recurso INT NOT NULL,
  FOREIGN KEY (id_tipo_recurso) REFERENCES TIPO_RECURSO(id_tipo_recurso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE SERVICIO_RECURSO (
  id_servicio_recurso INT AUTO_INCREMENT PRIMARY KEY,
  cantidad_requerida INT DEFAULT 1,
  uso_exclusivo TINYINT(1) DEFAULT 1,
  id_servicio INT NOT NULL,
  id_recurso INT NOT NULL,
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio),
  FOREIGN KEY (id_recurso) REFERENCES RECURSO(id_recurso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PACIENTE (
  id_paciente INT AUTO_INCREMENT PRIMARY KEY,
  nombres VARCHAR(100) NOT NULL,
  apellidos VARCHAR(100) NOT NULL,
  documento_identidad VARCHAR(20) NOT NULL UNIQUE,
  telefono VARCHAR(20),
  correo VARCHAR(100),
  fecha_nacimiento DATE,
  estado VARCHAR(20) DEFAULT 'activo',
  id_departamento INT NOT NULL,
  id_provincia INT NOT NULL,
  id_distrito INT NOT NULL,
  FOREIGN KEY (id_departamento) REFERENCES DEPARTAMENTO(id_departamento),
  FOREIGN KEY (id_provincia) REFERENCES PROVINCIA(id_provincia),
  FOREIGN KEY (id_distrito) REFERENCES DISTRITO(id_distrito)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE USUARIO (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  contrasena VARCHAR(255) NOT NULL,
  correo_electronico VARCHAR(100) NOT NULL UNIQUE,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso TIMESTAMP NULL,
  estado VARCHAR(20) DEFAULT 'activo',
  -- Columna para definir el tipo de usuario (paciente o empleado)
  tipo_usuario ENUM('paciente', 'empleado') NOT NULL,
  id_paciente INT NULL UNIQUE, -- Un paciente solo puede tener un usuario
  id_empleado INT NULL UNIQUE, -- Un empleado solo puede tener un usuario
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente),
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado),
  -- Restricción para asegurar la integridad de los datos
  CONSTRAINT chk_tipo_usuario CHECK (
    (tipo_usuario = 'paciente' AND id_paciente IS NOT NULL AND id_empleado IS NULL) OR
    (tipo_usuario = 'empleado' AND id_empleado IS NOT NULL AND id_paciente IS NULL)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PROGRAMACION (
  id_programacion INT AUTO_INCREMENT PRIMARY KEY,
  dia_semana VARCHAR(15) NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  disponibilidad TINYINT(1) DEFAULT 1,
  estado VARCHAR(20) DEFAULT 'activo',
  id_empleado INT NOT NULL,
  id_servicio INT NOT NULL,
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE BLOQUEO_PROGRAMACION (
  id_bloqueo INT AUTO_INCREMENT PRIMARY KEY,
  fecha DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  motivo TEXT,
  estado VARCHAR(20) DEFAULT 'activo',
  id_programacion INT NOT NULL,
  FOREIGN KEY (id_programacion) REFERENCES PROGRAMACION(id_programacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE RESERVA (
  id_reserva INT AUTO_INCREMENT PRIMARY KEY,
  fecha_reserva DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  estado VARCHAR(20) DEFAULT 'pendiente',
  motivo_cancelacion TEXT,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  id_paciente INT NOT NULL,
  id_servicio INT NOT NULL,
  id_programacion INT NOT NULL,
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente),
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio),
  FOREIGN KEY (id_programacion) REFERENCES PROGRAMACION(id_programacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE CITA (
  id_cita INT AUTO_INCREMENT PRIMARY KEY,
  fecha_cita DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  diagnostico TEXT,
  observaciones TEXT,
  estado VARCHAR(20) DEFAULT 'programada',
  id_reserva INT NOT NULL,
  id_empleado INT NOT NULL,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE CAMBIO (
  id_cambio INT AUTO_INCREMENT PRIMARY KEY,
  fecha_anterior DATE,
  hora_anterior TIME,
  fecha_nueva DATE,
  hora_nueva TIME,
  motivo TEXT,
  aprobado TINYINT(1) DEFAULT 0,
  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  id_reserva INT NOT NULL,
  id_paciente INT NOT NULL,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE NOTIFICACION (
  id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
  destinatario VARCHAR(255),
  canal VARCHAR(50),
  titulo VARCHAR(255),
  mensaje TEXT,
  tipo VARCHAR(30),
  fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  estado VARCHAR(20) DEFAULT 'pendiente',
  id_reserva INT NOT NULL,
  id_cambio INT NOT NULL,
  FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
  FOREIGN KEY (id_cambio) REFERENCES CAMBIO(id_cambio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE CITA_RECURSO (
  id_cita_recurso INT AUTO_INCREMENT PRIMARY KEY,
  estado VARCHAR(20) DEFAULT 'asignado',
  id_cita INT NOT NULL,
  id_recurso INT NOT NULL,
  FOREIGN KEY (id_cita) REFERENCES CITA(id_cita),
  FOREIGN KEY (id_recurso) REFERENCES RECURSO(id_recurso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE CATEGORIA (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE REPORTE (
  id_reporte INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) UNIQUE,
  nombre VARCHAR(100),
  tipo VARCHAR(50),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ruta_almacenamiento TEXT,
  id_categoria INT NOT NULL,
  usuario_responsable INT NOT NULL,
  FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(id_categoria),
  FOREIGN KEY (usuario_responsable) REFERENCES EMPLEADO(id_empleado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE registro_actividad (
  id_registro INT AUTO_INCREMENT PRIMARY KEY,
  fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  id_usuario INT,
  entidad_afectada VARCHAR(50),
  id_entidad INT,
  accion VARCHAR(30),
  descripcion TEXT,
  ip_origen VARCHAR(50),
  FOREIGN KEY (id_usuario) REFERENCES EMPLEADO(id_empleado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE INCIDENCIA (
  id_incidencia INT AUTO_INCREMENT PRIMARY KEY,
  descripcion TEXT NOT NULL,
  fecha_reporte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  estado VARCHAR(20) DEFAULT 'abierta',
  categoria VARCHAR(50),
  id_responsable INT NOT NULL,
  id_paciente INT NOT NULL,
  FOREIGN KEY (id_responsable) REFERENCES EMPLEADO(id_empleado),
  FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE REPORTE_OCUPACION (
  id_reporte INT AUTO_INCREMENT PRIMARY KEY,
  fecha_inicio_periodo DATE,
  fecha_fin_periodo DATE,
  porcentaje_uso DECIMAL(5,2),
  tiempo_total_ocupado INT,
  tiempo_disponible INT,
  fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  observaciones TEXT,
  id_recurso INT NOT NULL,
  id_servicio INT NOT NULL,
  FOREIGN KEY (id_recurso) REFERENCES RECURSO(id_recurso),
  FOREIGN KEY (id_servicio) REFERENCES SERVICIO(id_servicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
