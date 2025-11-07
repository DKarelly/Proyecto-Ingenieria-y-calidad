import pymysql

try:
    conn = pymysql.connect(
        host='trolley.proxy.rlwy.net',
        port=40902,
        user='root',
        password='EOFxUnNipaqUHGATGeTGjiOzlcdEvKwL',
        db='CLINICA',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cursor:
        # Ver la programación de la reserva 14
        cursor.execute("""
            SELECT p.*, r.id_reserva, r.id_paciente
            FROM PROGRAMACION p
            LEFT JOIN RESERVA r ON r.id_programacion = p.id_programacion
            WHERE r.id_paciente = 2
        """)
        result = cursor.fetchall()
        print(f"Programación del paciente 2:")
        for row in result:
            print(f"\n  id_programacion: {row['id_programacion']}")
            print(f"  id_servicio: {row['id_servicio']}")
            print(f"  id_horario: {row['id_horario']}")
            print(f"  fecha: {row['fecha']}")
            
        # Verificar si id_servicio existe en SERVICIO
        if result:
            id_servicio = result[0]['id_servicio']
            if id_servicio:
                cursor.execute("SELECT * FROM SERVICIO WHERE id_servicio = %s", (id_servicio,))
                servicio = cursor.fetchone()
                print(f"\nServicio {id_servicio}: {servicio}")
            else:
                print("\nid_servicio es NULL")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
