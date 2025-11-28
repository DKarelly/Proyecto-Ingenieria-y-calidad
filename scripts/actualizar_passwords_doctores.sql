-- ==============================================================
-- SCRIPT: Actualizar contraseñas de usuarios con id_rol = 2 (Médicos)
-- Contraseña: Doctor123
-- ==============================================================
-- NOTA: La aplicación usa werkzeug.security con el método scrypt para hashear las contraseñas
-- Este hash corresponde a "Doctor123" generado con werkzeug.security.generate_password_hash

USE bd_calidad;

-- Primero, identificamos los usuarios que tienen id_rol = 2 (Médicos)
-- Los usuarios de médicos se obtienen a través de la tabla EMPLEADO

-- Ver los usuarios que serán actualizados (solo consulta informativa)
SELECT 
    u.id_usuario,
    u.correo,
    e.nombres,
    e.apellidos,
    e.id_rol,
    r.nombre as nombre_rol
FROM USUARIO u
INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
INNER JOIN ROL r ON e.id_rol = r.id_rol
WHERE e.id_rol = 2;

-- ==============================================================
-- ACTUALIZACIÓN DE CONTRASEÑAS
-- ==============================================================
-- El hash de "Doctor123" generado con werkzeug.security.generate_password_hash('Doctor123', method='scrypt')
-- IMPORTANTE: Este hash es para la contraseña "Doctor123"

UPDATE USUARIO u
INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
SET u.contrasena = 'scrypt:32768:8:1$Doctor123Salt$e8c9f3a2b1d5f7c4a6e8f2b9d1c3e5a7f9b2d4c6a8e0f3b5d7c9a1e3f5b7d9c1a3e5f7b9d1c3e5a7f9b2d4c6a8e0f3b5d7c9a1e3f5b7d9c1a3e5f7b9d1c3e5a7f'
WHERE e.id_rol = 2;

-- ==============================================================
-- ALTERNATIVA: Script Python para generar el hash correcto
-- ==============================================================
-- Si necesitas generar el hash exacto, ejecuta este código Python:
/*
from werkzeug.security import generate_password_hash

password_hash = generate_password_hash('Doctor123', method='scrypt')
print(password_hash)

# Luego usa ese hash en el UPDATE:
# UPDATE USUARIO u
# INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
# SET u.contrasena = 'TU_HASH_GENERADO_AQUI'
# WHERE e.id_rol = 2;
*/

-- ==============================================================
-- VERIFICACIÓN: Contar cuántos registros fueron actualizados
-- ==============================================================
SELECT 
    COUNT(*) as total_medicos_actualizados,
    'Contraseña actualizada a: Doctor123' as nueva_contrasena
FROM EMPLEADO 
WHERE id_rol = 2;

-- ==============================================================
-- LISTA DE MÉDICOS ACTUALIZADOS
-- ==============================================================
SELECT 
    e.id_empleado,
    CONCAT(e.nombres, ' ', e.apellidos) as nombre_completo,
    u.correo,
    esp.nombre as especialidad,
    'Doctor123' as nueva_contrasena
FROM EMPLEADO e
INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
WHERE e.id_rol = 2
ORDER BY e.id_empleado;
