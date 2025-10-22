-- Actualizar contraseña del usuario admin con hash
UPDATE USUARIO 
SET contrasena = 'scrypt:32768:8:1$YFuYmbkM1NepxToL$4ba912a0ff08260a8f08c6065b2b7dfe7d1389492a60ac77025cd2479f6bdce5cc72a766c296505059cd72e6e074b465f2815f56a974f140dcf90b7906105964'
WHERE correo_electronico = 'admin@clinicaunion.com';

-- Verificar el cambio
SELECT id_usuario, correo_electronico, LEFT(contrasena, 30) as contrasena_hash, tipo_usuario, estado 
FROM USUARIO 
WHERE correo_electronico = 'admin@clinicaunion.com';
