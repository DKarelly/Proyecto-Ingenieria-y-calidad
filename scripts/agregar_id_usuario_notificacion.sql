-- Agregar campo id_usuario a la tabla NOTIFICACION para notificaciones de médicos
ALTER TABLE NOTIFICACION 
ADD COLUMN id_usuario INT NULL AFTER id_paciente,
ADD KEY `idx_id_usuario` (`id_usuario`),
ADD CONSTRAINT `NOTIFICACION_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `USUARIO` (`id_usuario`) ON DELETE CASCADE;

