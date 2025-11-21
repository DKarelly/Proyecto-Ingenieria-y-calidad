from bd import obtener_conexion

conn = obtener_conexion()
cursor = conn.cursor()

# Obtener triggers de la tabla AUTORIZACION_PROCEDIMIENTO
cursor.execute("SHOW TRIGGERS WHERE `Table` = 'AUTORIZACION_PROCEDIMIENTO'")
triggers = cursor.fetchall()

if triggers:
    for t in triggers:
        print("\n" + "="*80)
        print(f"Trigger: {t['Trigger']}")
        print(f"Timing: {t['Timing']}")
        print(f"Event: {t['Event']}")
        print(f"Statement:")
        print(t['Statement'])
        print("="*80)
else:
    print("No se encontraron triggers para la tabla AUTORIZACION_PROCEDIMIENTO")

conn.close()
