-- ============================================================================
-- SCRIPT DE CREACIÓN DE BITÁCORA DEL SISTEMA
-- Registra todas las acciones importantes del sistema para auditoría
-- ============================================================================

-- Tabla principal de bitácora
CREATE TABLE IF NOT EXISTS BITACORA_SISTEMA (
    id_bitacora INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Información del usuario que realiza la acción
    id_usuario_actor INT NULL COMMENT 'ID del usuario que realiza la acción',
    tipo_usuario_actor VARCHAR(20) NULL COMMENT 'Tipo de usuario (paciente/empleado)',
    id_empleado_actor INT NULL COMMENT 'ID del empleado si es empleado',
    nombre_actor VARCHAR(255) NULL COMMENT 'Nombre completo del usuario que realiza la acción',
    correo_actor VARCHAR(100) NULL COMMENT 'Correo del usuario que realiza la acción',
    
    -- Información del usuario afectado (si aplica)
    id_usuario_afectado INT NULL COMMENT 'ID del usuario afectado por la acción',
    tipo_usuario_afectado VARCHAR(20) NULL COMMENT 'Tipo de usuario afectado',
    nombre_afectado VARCHAR(255) NULL COMMENT 'Nombre del usuario afectado',
    correo_afectado VARCHAR(100) NULL COMMENT 'Correo del usuario afectado',
    
    -- Información de la acción
    modulo VARCHAR(50) NOT NULL COMMENT 'Módulo del sistema (usuarios, roles, reservas, etc.)',
    accion VARCHAR(100) NOT NULL COMMENT 'Tipo de acción (crear, modificar, eliminar, login, etc.)',
    tipo_evento VARCHAR(50) NOT NULL COMMENT 'Categoría del evento (seguridad, administracion, registro, etc.)',
    descripcion TEXT NOT NULL COMMENT 'Descripción detallada de la acción',
    
    -- Información técnica
    ip_address VARCHAR(45) NULL COMMENT 'IP desde donde se realizó la acción',
    user_agent TEXT NULL COMMENT 'Navegador/cliente utilizado',
    endpoint VARCHAR(255) NULL COMMENT 'Endpoint o ruta accedida',
    
    -- Información de cambios (JSON para flexibilidad)
    valores_anteriores JSON NULL COMMENT 'Valores antes del cambio (JSON)',
    valores_nuevos JSON NULL COMMENT 'Valores después del cambio (JSON)',
    cambios_detallados TEXT NULL COMMENT 'Descripción de cambios específicos',
    
    -- Estado y resultado
    resultado VARCHAR(20) NOT NULL DEFAULT 'Exitoso' COMMENT 'Exitoso, Fallido, Pendiente',
    codigo_error VARCHAR(50) NULL COMMENT 'Código de error si falló',
    mensaje_error TEXT NULL COMMENT 'Mensaje de error si falló',
    
    -- Metadatos adicionales
    metadata JSON NULL COMMENT 'Información adicional en formato JSON',
    
    -- Índices para búsquedas rápidas
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_usuario_actor (id_usuario_actor),
    INDEX idx_usuario_afectado (id_usuario_afectado),
    INDEX idx_modulo (modulo),
    INDEX idx_accion (accion),
    INDEX idx_tipo_evento (tipo_evento),
    INDEX idx_resultado (resultado),
    INDEX idx_ip_address (ip_address),
    INDEX idx_fecha_modulo (fecha_hora, modulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bitácora completa del sistema para auditoría y trazabilidad';

-- ============================================================================
-- TRIGGERS PARA REGISTRO AUTOMÁTICO
-- ============================================================================

-- Trigger para registrar creación de usuarios
DELIMITER $$

DROP TRIGGER IF EXISTS trg_bitacora_usuario_creado$$
CREATE TRIGGER trg_bitacora_usuario_creado
AFTER INSERT ON USUARIO
FOR EACH ROW
BEGIN
    INSERT INTO BITACORA_SISTEMA (
        id_usuario_afectado,
        tipo_usuario_afectado,
        correo_afectado,
        modulo,
        accion,
        tipo_evento,
        descripcion,
        valores_nuevos,
        resultado
    ) VALUES (
        NEW.id_usuario,
        'usuario',
        NEW.correo,
        'usuarios',
        'crear_usuario',
        'registro',
        CONCAT('Usuario creado: ', NEW.correo),
        JSON_OBJECT(
            'id_usuario', NEW.id_usuario,
            'correo', NEW.correo,
            'telefono', NEW.telefono,
            'estado', NEW.estado,
            'fecha_creacion', NEW.fecha_creacion
        ),
        'Exitoso'
    );
END$$

-- Trigger para registrar cambios en usuarios
DROP TRIGGER IF EXISTS trg_bitacora_usuario_modificado$$
CREATE TRIGGER trg_bitacora_usuario_modificado
AFTER UPDATE ON USUARIO
FOR EACH ROW
BEGIN
    -- Solo registrar si hay cambios importantes
    IF OLD.correo != NEW.correo OR 
       OLD.telefono != NEW.telefono OR 
       OLD.estado != NEW.estado THEN
        
        INSERT INTO BITACORA_SISTEMA (
            id_usuario_afectado,
            tipo_usuario_afectado,
            correo_afectado,
            modulo,
            accion,
            tipo_evento,
            descripcion,
            valores_anteriores,
            valores_nuevos,
            cambios_detallados,
            resultado
        ) VALUES (
            NEW.id_usuario,
            'usuario',
            NEW.correo,
            'usuarios',
            'modificar_usuario',
            CASE 
                WHEN OLD.estado != NEW.estado THEN 'administracion'
                ELSE 'modificacion'
            END,
            CONCAT('Usuario modificado: ', NEW.correo),
            JSON_OBJECT(
                'correo', OLD.correo,
                'telefono', OLD.telefono,
                'estado', OLD.estado
            ),
            JSON_OBJECT(
                'correo', NEW.correo,
                'telefono', NEW.telefono,
                'estado', NEW.estado
            ),
            CONCAT_WS(', ',
                IF(OLD.correo != NEW.correo, CONCAT('Correo: ', OLD.correo, ' → ', NEW.correo), NULL),
                IF(OLD.telefono != NEW.telefono, CONCAT('Teléfono: ', OLD.telefono, ' → ', NEW.telefono), NULL),
                IF(OLD.estado != NEW.estado, CONCAT('Estado: ', OLD.estado, ' → ', NEW.estado), NULL)
            ),
            'Exitoso'
        );
    END IF;
END$$

-- Trigger para registrar cambios de rol en empleados
DROP TRIGGER IF EXISTS trg_bitacora_empleado_rol_cambiado$$
CREATE TRIGGER trg_bitacora_empleado_rol_cambiado
AFTER UPDATE ON EMPLEADO
FOR EACH ROW
BEGIN
    -- Registrar cambio de rol
    IF OLD.id_rol != NEW.id_rol THEN
        INSERT INTO BITACORA_SISTEMA (
            id_usuario_afectado,
            tipo_usuario_afectado,
            modulo,
            accion,
            tipo_evento,
            descripcion,
            valores_anteriores,
            valores_nuevos,
            cambios_detallados,
            resultado
        ) VALUES (
            NEW.id_usuario,
            'empleado',
            'roles',
            'cambiar_rol',
            'administracion',
            CONCAT('Rol de empleado cambiado'),
            JSON_OBJECT(
                'id_rol_anterior', OLD.id_rol,
                'id_empleado', OLD.id_empleado
            ),
            JSON_OBJECT(
                'id_rol_nuevo', NEW.id_rol,
                'id_empleado', NEW.id_empleado
            ),
            CONCAT('Rol cambiado de ', OLD.id_rol, ' a ', NEW.id_rol),
            'Exitoso'
        );
    END IF;
END$$

-- Trigger para registrar creación de empleados
DROP TRIGGER IF EXISTS trg_bitacora_empleado_creado$$
CREATE TRIGGER trg_bitacora_empleado_creado
AFTER INSERT ON EMPLEADO
FOR EACH ROW
BEGIN
    INSERT INTO BITACORA_SISTEMA (
        id_usuario_afectado,
        tipo_usuario_afectado,
        modulo,
        accion,
        tipo_evento,
        descripcion,
        valores_nuevos,
        resultado
    ) VALUES (
        NEW.id_usuario,
        'empleado',
        'usuarios',
        'crear_empleado',
        'registro',
        CONCAT('Empleado creado con rol ', NEW.id_rol),
        JSON_OBJECT(
            'id_empleado', NEW.id_empleado,
            'id_usuario', NEW.id_usuario,
            'id_rol', NEW.id_rol,
            'id_especialidad', NEW.id_especialidad
        ),
        'Exitoso'
    );
END$$

-- Trigger para registrar creación de pacientes
DROP TRIGGER IF EXISTS trg_bitacora_paciente_creado$$
CREATE TRIGGER trg_bitacora_paciente_creado
AFTER INSERT ON PACIENTE
FOR EACH ROW
BEGIN
    INSERT INTO BITACORA_SISTEMA (
        id_usuario_afectado,
        tipo_usuario_afectado,
        modulo,
        accion,
        tipo_evento,
        descripcion,
        valores_nuevos,
        resultado
    ) VALUES (
        NEW.id_usuario,
        'paciente',
        'usuarios',
        'crear_paciente',
        'registro',
        CONCAT('Paciente creado: ', NEW.nombres, ' ', NEW.apellidos),
        JSON_OBJECT(
            'id_paciente', NEW.id_paciente,
            'id_usuario', NEW.id_usuario,
            'documento_identidad', NEW.documento_identidad,
            'nombres', NEW.nombres,
            'apellidos', NEW.apellidos
        ),
        'Exitoso'
    );
END$$

DELIMITER ;

-- ============================================================================
-- PROCEDIMIENTOS ALMACENADOS PARA REGISTRAR ACCIONES MANUALMENTE
-- ============================================================================

DELIMITER $$

-- Procedimiento para registrar intentos de registro
DROP PROCEDURE IF EXISTS sp_registrar_intento_registro$$
CREATE PROCEDURE sp_registrar_intento_registro(
    IN p_correo VARCHAR(100),
    IN p_ip_address VARCHAR(45),
    IN p_resultado VARCHAR(20),
    IN p_mensaje_error TEXT,
    IN p_metadata JSON
)
BEGIN
    INSERT INTO BITACORA_SISTEMA (
        correo_afectado,
        modulo,
        accion,
        tipo_evento,
        descripcion,
        ip_address,
        resultado,
        mensaje_error,
        metadata
    ) VALUES (
        p_correo,
        'usuarios',
        'intento_registro',
        'registro',
        CONCAT('Intento de registro: ', p_correo),
        p_ip_address,
        p_resultado,
        p_mensaje_error,
        p_metadata
    );
END$$

-- Procedimiento para registrar cambios de contraseña
DROP PROCEDURE IF EXISTS sp_registrar_cambio_contrasena$$
CREATE PROCEDURE sp_registrar_cambio_contrasena(
    IN p_id_usuario INT,
    IN p_id_usuario_actor INT,
    IN p_ip_address VARCHAR(45),
    IN p_resultado VARCHAR(20),
    IN p_mensaje_error TEXT
)
BEGIN
    DECLARE v_correo VARCHAR(100);
    DECLARE v_nombre_actor VARCHAR(255);
    
    -- Obtener correo del usuario afectado
    SELECT correo INTO v_correo FROM USUARIO WHERE id_usuario = p_id_usuario;
    
    -- Obtener nombre del actor
    SELECT CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, ''), 
                  COALESCE(e.nombres, ''), ' ', COALESCE(e.apellidos, ''))
    INTO v_nombre_actor
    FROM USUARIO u
    LEFT JOIN PACIENTE p ON u.id_usuario = p.id_usuario
    LEFT JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
    WHERE u.id_usuario = p_id_usuario_actor;
    
    INSERT INTO BITACORA_SISTEMA (
        id_usuario_actor,
        nombre_actor,
        id_usuario_afectado,
        correo_afectado,
        modulo,
        accion,
        tipo_evento,
        descripcion,
        ip_address,
        resultado,
        mensaje_error
    ) VALUES (
        p_id_usuario_actor,
        v_nombre_actor,
        p_id_usuario,
        v_correo,
        'usuarios',
        'cambiar_contrasena',
        'seguridad',
        CONCAT('Cambio de contraseña para usuario: ', v_correo),
        p_ip_address,
        p_resultado,
        p_mensaje_error
    );
END$$

-- Procedimiento para registrar cambios de roles por admin
DROP PROCEDURE IF EXISTS sp_registrar_cambio_rol_admin$$
CREATE PROCEDURE sp_registrar_cambio_rol_admin(
    IN p_id_empleado INT,
    IN p_id_admin INT,
    IN p_rol_anterior INT,
    IN p_rol_nuevo INT,
    IN p_ip_address VARCHAR(45)
)
BEGIN
    DECLARE v_nombre_admin VARCHAR(255);
    DECLARE v_correo_admin VARCHAR(100);
    DECLARE v_nombre_empleado VARCHAR(255);
    DECLARE v_correo_empleado VARCHAR(100);
    DECLARE v_id_usuario_empleado INT;
    
    -- Obtener información del admin
    SELECT CONCAT(e.nombres, ' ', e.apellidos), u.correo
    INTO v_nombre_admin, v_correo_admin
    FROM EMPLEADO e
    JOIN USUARIO u ON e.id_usuario = u.id_usuario
    WHERE e.id_empleado = p_id_admin;
    
    -- Obtener información del empleado afectado
    SELECT CONCAT(e.nombres, ' ', e.apellidos), u.correo, e.id_usuario
    INTO v_nombre_empleado, v_correo_empleado, v_id_usuario_empleado
    FROM EMPLEADO e
    JOIN USUARIO u ON e.id_usuario = u.id_usuario
    WHERE e.id_empleado = p_id_empleado;
    
    INSERT INTO BITACORA_SISTEMA (
        id_usuario_actor,
        id_empleado_actor,
        nombre_actor,
        correo_actor,
        id_usuario_afectado,
        nombre_afectado,
        correo_afectado,
        modulo,
        accion,
        tipo_evento,
        descripcion,
        valores_anteriores,
        valores_nuevos,
        cambios_detallados,
        ip_address,
        resultado
    ) VALUES (
        (SELECT id_usuario FROM EMPLEADO WHERE id_empleado = p_id_admin),
        p_id_admin,
        v_nombre_admin,
        v_correo_admin,
        v_id_usuario_empleado,
        v_nombre_empleado,
        v_correo_empleado,
        'roles',
        'cambiar_rol_admin',
        'administracion',
        CONCAT('Admin cambió rol de empleado: ', v_nombre_empleado),
        JSON_OBJECT('id_rol', p_rol_anterior),
        JSON_OBJECT('id_rol', p_rol_nuevo),
        CONCAT('Rol cambiado de ', p_rol_anterior, ' a ', p_rol_nuevo, ' por administrador'),
        p_ip_address,
        'Exitoso'
    );
END$$

-- Procedimiento para registrar acciones administrativas generales
DROP PROCEDURE IF EXISTS sp_registrar_accion_admin$$
CREATE PROCEDURE sp_registrar_accion_admin(
    IN p_id_admin INT,
    IN p_modulo VARCHAR(50),
    IN p_accion VARCHAR(100),
    IN p_tipo_evento VARCHAR(50),
    IN p_descripcion TEXT,
    IN p_id_usuario_afectado INT,
    IN p_ip_address VARCHAR(45),
    IN p_valores_anteriores JSON,
    IN p_valores_nuevos JSON,
    IN p_resultado VARCHAR(20),
    IN p_metadata JSON
)
BEGIN
    DECLARE v_nombre_admin VARCHAR(255);
    DECLARE v_correo_admin VARCHAR(100);
    DECLARE v_id_empleado_admin INT;
    
    -- Obtener información del admin
    SELECT CONCAT(e.nombres, ' ', e.apellidos), u.correo, e.id_empleado
    INTO v_nombre_admin, v_correo_admin, v_id_empleado_admin
    FROM EMPLEADO e
    JOIN USUARIO u ON e.id_usuario = u.id_usuario
    WHERE e.id_empleado = p_id_admin;
    
    INSERT INTO BITACORA_SISTEMA (
        id_usuario_actor,
        id_empleado_actor,
        nombre_actor,
        correo_actor,
        id_usuario_afectado,
        modulo,
        accion,
        tipo_evento,
        descripcion,
        valores_anteriores,
        valores_nuevos,
        ip_address,
        resultado,
        metadata
    ) VALUES (
        (SELECT id_usuario FROM EMPLEADO WHERE id_empleado = p_id_admin),
        p_id_admin,
        v_nombre_admin,
        v_correo_admin,
        p_id_usuario_afectado,
        p_modulo,
        p_accion,
        p_tipo_evento,
        p_descripcion,
        p_valores_anteriores,
        p_valores_nuevos,
        p_ip_address,
        p_resultado,
        p_metadata
    );
END$$

DELIMITER ;

-- ============================================================================
-- VISTAS ÚTILES PARA CONSULTAS FRECUENTES
-- ============================================================================

-- Vista de acciones de seguridad (logins, cambios de contraseña, etc.)
CREATE OR REPLACE VIEW v_bitacora_seguridad AS
SELECT 
    id_bitacora,
    fecha_hora,
    nombre_actor,
    correo_actor,
    correo_afectado,
    accion,
    descripcion,
    ip_address,
    resultado,
    mensaje_error
FROM BITACORA_SISTEMA
WHERE tipo_evento = 'seguridad'
ORDER BY fecha_hora DESC;

-- Vista de acciones administrativas
CREATE OR REPLACE VIEW v_bitacora_administracion AS
SELECT 
    id_bitacora,
    fecha_hora,
    nombre_actor,
    correo_actor,
    nombre_afectado,
    correo_afectado,
    modulo,
    accion,
    descripcion,
    cambios_detallados,
    resultado
FROM BITACORA_SISTEMA
WHERE tipo_evento = 'administracion'
ORDER BY fecha_hora DESC;

-- Vista de registros de usuarios
CREATE OR REPLACE VIEW v_bitacora_registros AS
SELECT 
    id_bitacora,
    fecha_hora,
    correo_afectado,
    accion,
    descripcion,
    ip_address,
    resultado,
    mensaje_error
FROM BITACORA_SISTEMA
WHERE tipo_evento = 'registro' OR accion LIKE '%registro%' OR accion LIKE '%crear%'
ORDER BY fecha_hora DESC;

-- Vista de cambios de roles
CREATE OR REPLACE VIEW v_bitacora_cambios_roles AS
SELECT 
    id_bitacora,
    fecha_hora,
    nombre_actor,
    correo_actor,
    nombre_afectado,
    correo_afectado,
    descripcion,
    cambios_detallados,
    valores_anteriores,
    valores_nuevos,
    ip_address
FROM BITACORA_SISTEMA
WHERE accion LIKE '%rol%'
ORDER BY fecha_hora DESC;

-- ============================================================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ============================================================================

-- Agregar comentarios a las columnas importantes
ALTER TABLE BITACORA_SISTEMA 
MODIFY COLUMN tipo_evento VARCHAR(50) 
COMMENT 'Tipos: seguridad, administracion, registro, modificacion, eliminacion, consulta';

ALTER TABLE BITACORA_SISTEMA 
MODIFY COLUMN resultado VARCHAR(20) 
COMMENT 'Valores: Exitoso, Fallido, Pendiente';

-- ============================================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================================================

-- Índice compuesto para búsquedas por usuario y fecha
CREATE INDEX idx_usuario_fecha ON BITACORA_SISTEMA(id_usuario_afectado, fecha_hora DESC);

-- Índice compuesto para búsquedas por módulo y acción
CREATE INDEX idx_modulo_accion ON BITACORA_SISTEMA(modulo, accion);

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================

