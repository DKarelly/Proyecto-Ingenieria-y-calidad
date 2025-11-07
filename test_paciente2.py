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
        # Ver reservas del paciente 2 con todos los detalles
        cursor.execute("""
            SELECT r.id_reserva, r.id_paciente, r.estado, r.fecha_registro,
                   p.fecha as fecha_cita, p.hora_inicio, p.hora_fin,
                   s.nombre as servicio, e.nombres, e.apellidos
            FROM RESERVA r
            LEFT JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
            LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
            LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
            WHERE r.id_paciente = 2
        """)
        reservas = cursor.fetchall()
        print(f"Reservas del paciente 2: {len(reservas)}")
        for r in reservas:
            print(f"\nReserva {r['id_reserva']}:")
            print(f"  - Estado: {r['estado']}")
            print(f"  - Fecha cita: {r['fecha_cita']}")
            print(f"  - Hora: {r['hora_inicio']} - {r['hora_fin']}")
            print(f"  - Servicio: {r['servicio']}")
            print(f"  - Empleado: {r['nombres']} {r['apellidos']}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
