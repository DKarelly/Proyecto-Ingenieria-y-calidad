ges nuesagrefrom bd import obtener_conexion

conn = obtener_conexion()
cursor = conn.cursor()

# Actualizar categorías
cursor.execute("""
    UPDATE INCIDENCIA SET categoria = CASE
        WHEN id_incidencia % 5 = 0 THEN 'Personal'
        WHEN id_incidencia % 4 = 0 THEN 'Equipamiento'
        WHEN id_incidencia % 3 = 0 THEN 'Infraestructura'
        WHEN id_incidencia % 2 = 0 THEN 'Administrativa'
        ELSE 'Técnica'
    END
""")

# Actualizar prioridades
cursor.execute("""
    UPDATE INCIDENCIA SET prioridad = CASE
        WHEN id_incidencia % 3 = 0 THEN 'Alta'
        WHEN id_incidencia % 2 = 0 THEN 'Media'
        ELSE 'Baja'
    END
""")

conn.commit()
print('Datos actualizados')
