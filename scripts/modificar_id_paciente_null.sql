-- Modificar la columna id_paciente para permitir NULL
-- Esto permite que las notificaciones de médico no requieran id_paciente
ALTER TABLE NOTIFICACION 
MODIFY COLUMN id_paciente INT NULL;

