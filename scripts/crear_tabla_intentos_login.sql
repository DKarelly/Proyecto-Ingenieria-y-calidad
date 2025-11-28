-- Script para crear la tabla de intentos de login fallidos
-- Esta tabla se usa para rate limiting y prevención de ataques de fuerza bruta

CREATE TABLE IF NOT EXISTS intentos_login_fallidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    razon VARCHAR(255) DEFAULT 'Credenciales incorrectas',
    fecha_intento DATETIME NOT NULL,
    INDEX idx_correo (correo),
    INDEX idx_ip (ip_address),
    INDEX idx_fecha (fecha_intento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comentarios sobre la tabla
ALTER TABLE intentos_login_fallidos COMMENT = 'Registra intentos fallidos de login para rate limiting y prevención de fuerza bruta';

