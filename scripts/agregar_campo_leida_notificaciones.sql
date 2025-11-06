-- Script para agregar el campo 'leida' a la tabla NOTIFICACION
-- Ejecutar este script en la base de datos CLINICA

USE CLINICA;

-- Agregar columna leida si no existe
ALTER TABLE NOTIFICACION 
ADD COLUMN IF NOT EXISTS leida BOOLEAN DEFAULT FALSE AFTER hora_envio;

-- Agregar columna fecha_leida para registrar cuándo se marcó como leída
ALTER TABLE NOTIFICACION 
ADD COLUMN IF NOT EXISTS fecha_leida DATETIME DEFAULT NULL AFTER leida;

-- Crear índice para mejorar consultas de notificaciones no leídas
CREATE INDEX IF NOT EXISTS idx_leida ON NOTIFICACION(leida);

-- Mostrar estructura actualizada
DESCRIBE NOTIFICACION;
