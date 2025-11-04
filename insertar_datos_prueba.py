import pymysql
from bd import obtener_conexion
from datetime import datetime, timedelta, time

def insertar_horarios():
    """Inserta horarios para los empleados existentes"""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Primero verificamos qué empleados existen
        cursor.execute("SELECT id_empleado, nombre, apellido FROM EMPLEADO")
        empleados = cursor.fetchall()

        print("=== EMPLEADOS EXISTENTES ===")
        for emp in empleados:
            print(f"ID: {emp['id_empleado']}, Nombre: {emp['nombre']} {emp['apellido']}")

        # Generamos horarios para las próximas 2 semanas desde hoy
        fecha_inicio = datetime.now().date()
        horarios_insertados = 0

        # Definimos franjas horarias típicas
        franjas = [
            (time(8, 0), time(12, 0)),   # Mañana
            (time(14, 0), time(18, 0)),  # Tarde
            (time(9, 0), time(13, 0)),   # Mañana alternativa
            (time(15, 0), time(19, 0)),  # Tarde alternativa
        ]

        for dia_offset in range(14):  # 14 días
            fecha = fecha_inicio + timedelta(days=dia_offset)

            # Solo días laborables (lunes a viernes)
            if fecha.weekday() < 5:
                for emp in empleados:
                    id_empleado = emp['id_empleado']

                    # Asignar 1-2 franjas por día a cada empleado
                    num_franjas = 1 if dia_offset % 2 == 0 else 2

                    for i in range(num_franjas):
                        franja = franjas[id_empleado % len(franjas)]
                        hora_inicio, hora_fin = franja

                        # Verificar si ya existe este horario
                        cursor.execute("""
                            SELECT id_horario FROM HORARIO
                            WHERE id_empleado = %s AND fecha = %s AND hora_inicio = %s
                        """, (id_empleado, fecha, hora_inicio))

                        if not cursor.fetchone():
                            cursor.execute("""
                                INSERT INTO HORARIO
                                (id_empleado, fecha, hora_inicio, hora_fin, disponibilidad, estado)
                                VALUES (%s, %s, %s, %s, 'Disponible', 'Activo')
                            """, (id_empleado, fecha, hora_inicio, hora_fin))
                            horarios_insertados += 1

        conexion.commit()
        print(f"\n✓ Se insertaron {horarios_insertados} horarios nuevos")

    except Exception as e:
        print(f"✗ Error al insertar horarios: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

def insertar_programaciones():
    """Inserta programaciones basadas en los horarios existentes"""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Obtenemos horarios disponibles
        cursor.execute("""
            SELECT id_horario, fecha, hora_inicio, hora_fin
            FROM HORARIO
            WHERE disponibilidad = 'Disponible' AND estado = 'Activo'
            AND fecha >= CURDATE()
            ORDER BY fecha, hora_inicio
        """)
        horarios = cursor.fetchall()

        # Obtenemos servicios existentes
        cursor.execute("SELECT id_servicio FROM SERVICIO")
        servicios = cursor.fetchall()

        print(f"\n=== PROGRAMACIONES ===")
        print(f"Horarios disponibles: {len(horarios)}")
        print(f"Servicios disponibles: {len(servicios)}")

        programaciones_insertadas = 0

        for horario in horarios[:50]:  # Limitamos a 50 para no saturar
            id_horario = horario['id_horario']
            fecha = horario['fecha']
            hora_inicio = horario['hora_inicio']
            hora_fin = horario['hora_fin']

            # Dividimos el horario en bloques de 30 minutos
            hora_actual = datetime.combine(fecha, hora_inicio)
            hora_final = datetime.combine(fecha, hora_fin)

            while hora_actual < hora_final:
                siguiente_hora = hora_actual + timedelta(minutes=30)

                if siguiente_hora <= hora_final:
                    # Verificar si ya existe esta programación
                    cursor.execute("""
                        SELECT id_programacion FROM PROGRAMACION
                        WHERE id_horario = %s AND fecha = %s AND hora_inicio = %s
                    """, (id_horario, fecha, hora_actual.time()))

                    if not cursor.fetchone():
                        # Asignar un servicio aleatorio (o NULL)
                        id_servicio = servicios[programaciones_insertadas % len(servicios)]['id_servicio'] if servicios else None

                        cursor.execute("""
                            INSERT INTO PROGRAMACION
                            (fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario)
                            VALUES (%s, %s, %s, 'Activo', %s, %s)
                        """, (fecha, hora_actual.time(), siguiente_hora.time(), id_servicio, id_horario))
                        programaciones_insertadas += 1

                hora_actual = siguiente_hora

        conexion.commit()
        print(f"✓ Se insertaron {programaciones_insertadas} programaciones nuevas")

    except Exception as e:
        print(f"✗ Error al insertar programaciones: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

def insertar_reservas():
    """Inserta reservas para las programaciones disponibles"""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Obtenemos programaciones activas futuras
        cursor.execute("""
            SELECT id_programacion, fecha, hora_inicio
            FROM PROGRAMACION
            WHERE estado = 'Activo' AND fecha >= CURDATE()
            ORDER BY fecha, hora_inicio
            LIMIT 30
        """)
        programaciones = cursor.fetchall()

        # Obtenemos pacientes existentes
        cursor.execute("SELECT id_paciente FROM PACIENTE")
        pacientes = cursor.fetchall()

        print(f"\n=== RESERVAS ===")
        print(f"Programaciones disponibles: {len(programaciones)}")
        print(f"Pacientes disponibles: {len(pacientes)}")

        reservas_insertadas = 0
        estados = ['Confirmada', 'Pendiente', 'Confirmada', 'Confirmada']  # Más confirmadas
        tipos = [1, 2, 1, 2, 1]  # Alternando tipos

        for i, prog in enumerate(programaciones[:20]):  # 20 reservas
            id_programacion = prog['id_programacion']
            fecha = prog['fecha']
            hora = prog['hora_inicio']

            # Verificar si ya existe reserva para esta programación
            cursor.execute("""
                SELECT id_reserva FROM RESERVA WHERE id_programacion = %s
            """, (id_programacion,))

            if not cursor.fetchone() and pacientes:
                id_paciente = pacientes[i % len(pacientes)]['id_paciente']
                estado = estados[i % len(estados)]
                tipo = tipos[i % len(tipos)]

                # Fecha de registro: 1-3 días antes de la cita
                fecha_registro = fecha - timedelta(days=(i % 3) + 1)

                cursor.execute("""
                    INSERT INTO RESERVA
                    (fecha_registro, hora_registro, tipo, estado, motivo_cancelacion, id_paciente, id_programacion)
                    VALUES (%s, %s, %s, %s, NULL, %s, %s)
                """, (fecha_registro, hora, tipo, estado, id_paciente, id_programacion))
                reservas_insertadas += 1

        conexion.commit()
        print(f"✓ Se insertaron {reservas_insertadas} reservas nuevas")

    except Exception as e:
        print(f"✗ Error al insertar reservas: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

def insertar_citas():
    """Inserta citas para las reservas confirmadas"""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Obtenemos reservas confirmadas sin cita
        cursor.execute("""
            SELECT r.id_reserva, p.fecha, p.hora_inicio, p.hora_fin
            FROM RESERVA r
            JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            WHERE r.estado = 'Confirmada'
            AND NOT EXISTS (SELECT 1 FROM CITA c WHERE c.id_reserva = r.id_reserva)
            ORDER BY p.fecha, p.hora_inicio
            LIMIT 15
        """)
        reservas = cursor.fetchall()

        print(f"\n=== CITAS ===")
        print(f"Reservas sin cita: {len(reservas)}")

        citas_insertadas = 0
        observaciones_list = [
            'Consulta general',
            'Control de rutina',
            'Seguimiento',
            'Primera consulta',
            'Evaluación inicial'
        ]

        for i, reserva in enumerate(reservas):
            id_reserva = reserva['id_reserva']
            fecha = reserva['fecha']
            hora_inicio = reserva['hora_inicio']
            hora_fin = reserva['hora_fin']

            # Estado: Pendiente para futuras, Completada para pasadas
            estado = 'Completada' if fecha < datetime.now().date() else 'Pendiente'
            observaciones = observaciones_list[i % len(observaciones_list)]

            cursor.execute("""
                INSERT INTO CITA
                (fecha_cita, hora_inicio, hora_fin, diagnostico, observaciones, estado, id_reserva)
                VALUES (%s, %s, %s, NULL, %s, %s, %s)
            """, (fecha, hora_inicio, hora_fin, observaciones, estado, id_reserva))
            citas_insertadas += 1

        conexion.commit()
        print(f"✓ Se insertaron {citas_insertadas} citas nuevas")

    except Exception as e:
        print(f"✗ Error al insertar citas: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    print("="*60)
    print("  INSERTANDO DATOS DE PRUEBA EN LA BASE DE DATOS")
    print("="*60)

    print("\n[1/4] Insertando horarios...")
    insertar_horarios()

    print("\n[2/4] Insertando programaciones...")
    insertar_programaciones()

    print("\n[3/4] Insertando reservas...")
    insertar_reservas()

    print("\n[4/4] Insertando citas...")
    insertar_citas()

    print("\n" + "="*60)
    print("  ✓ PROCESO COMPLETADO")
    print("="*60)
