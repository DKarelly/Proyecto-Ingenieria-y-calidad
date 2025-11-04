-- ============================================================
-- INSERT PARA ADMINISTRADOR DEL SISTEMA
-- ============================================================
-- Usuario: superadmin@clinicaunion.com
-- Contraseña: Admin2024!
-- Rol: Administrador (id_rol = 1)
-- ============================================================

-- Primero, insertar el USUARIO
INSERT INTO USUARIO (contrasena, correo, telefono, estado, fecha_creacion) 
VALUES (
    'scrypt:32768:8:1$0TG3Hha3swGomhZ7$b0c7a0ea50772cfef7eef833b1fae1c2e668faf69f03d2689069f953b8035ebb2666b039589095b44e458f8150c4dda8433fa7cb82b8a74fa766c171648b3765',
    'superadmin@clinicaunion.com',
    '999888777',
    'Activo',
    NOW()
);

-- Obtener el ID del usuario recién insertado
SET @usuario_id = LAST_INSERT_ID();

-- Luego, insertar el EMPLEADO asociado con rol de Administrador
INSERT INTO EMPLEADO (
    nombres, 
    apellidos, 
    fecha_nacimiento, 
    documento_identidad, 
    sexo, 
    estado, 
    id_usuario, 
    id_rol, 
    id_distrito,
    id_especialidad,
    fotoPerfil
) 
VALUES (
    'Super',
    'Administrador',
    '1985-01-01',
    '00000001',
    'Masculino',
    'Activo',
    @usuario_id,
    1,  -- Rol: Administrador
    140312,  -- Distrito: Chiclayo
    NULL,  -- Sin especialidad (no es médico)
    NULL   -- Sin foto de perfil por ahora
);

-- ============================================================
-- VERIFICACIÓN
-- ============================================================
SELECT 
    u.id_usuario,
    u.correo,
    u.telefono,
    u.estado as estado_usuario,
    e.id_empleado,
    e.nombres,
    e.apellidos,
    e.documento_identidad,
    e.estado as estado_empleado,
    r.nombre as rol
FROM USUARIO u
INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
INNER JOIN ROL r ON e.id_rol = r.id_rol
WHERE u.correo = 'superadmin@clinicaunion.com';

-- ============================================================
-- CREDENCIALES DE ACCESO
-- ============================================================
-- Email: superadmin@clinicaunion.com
-- Contraseña: admin123
-- ============================================================
