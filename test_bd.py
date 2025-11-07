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
        # Ver cuántas reservas hay
        cursor.execute("SELECT COUNT(*) as total FROM RESERVA")
        result = cursor.fetchone()
        print(f"Total de reservas en BD: {result['total']}")
        
        # Ver algunas reservas
        cursor.execute("SELECT id_reserva, id_paciente, estado, fecha_registro FROM RESERVA LIMIT 5")
        reservas = cursor.fetchall()
        print("\nPrimeras 5 reservas:")
        for r in reservas:
            print(f"  - ID: {r['id_reserva']}, Paciente: {r['id_paciente']}, Estado: {r['estado']}")
        
        # Ver reservas con estado 'Pendiente'
        cursor.execute("SELECT COUNT(*) as total FROM RESERVA WHERE estado = 'Pendiente'")
        result = cursor.fetchone()
        print(f"\nReservas con estado 'Pendiente': {result['total']}")
        
        # Ver qué pacientes existen
        cursor.execute("SELECT DISTINCT id_paciente FROM RESERVA LIMIT 5")
        pacientes = cursor.fetchall()
        print(f"\nPacientes con reservas: {[p['id_paciente'] for p in pacientes]}")
        
    conn.close()
    print("\n✓ Conexión exitosa")
    
except Exception as e:
    print(f"❌ Error: {e}")
