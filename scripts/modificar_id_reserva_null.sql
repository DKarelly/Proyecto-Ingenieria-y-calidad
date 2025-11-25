-- Modificar la columna id_reserva para permitir NULL
-- Esto permite que las notificaciones de médico sin reserva asociada (como derivaciones de operación)
-- puedan ser creadas sin requerir un id_reserva

-- Primero, eliminar la foreign key constraint si existe
ALTER TABLE NOTIFICACION 
DROP FOREIGN KEY IF EXISTS NOTIFICACION_ibfk_2;

-- Modificar la columna para permitir NULL
ALTER TABLE NOTIFICACION 
MODIFY COLUMN id_reserva INT NULL;

-- Recrear la foreign key constraint si la columna no es NULL
-- (solo para las filas que tengan id_reserva)
-- Nota: MySQL no permite foreign keys condicionales, así que la constraint aplicará a todas las filas
-- con id_reserva no NULL
ALTER TABLE NOTIFICACION 
ADD CONSTRAINT NOTIFICACION_ibfk_2 
FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva);

