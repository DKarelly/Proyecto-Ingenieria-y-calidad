from bd import obtener_conexion
from datetime import datetime, timedelta

def insertar_horarios_noviembre_diciembre():
    """
    Inserta horarios para noviembre y diciembre 2025
    - Solo días laborables (lunes a viernes)
    - Dos turnos: 07:00-13:00 y 14:00-22:00
    - Todos los médicos (empleados con rol de médico)
    """
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            # Obtener todos los médicos (puedes ajustar esta consulta según tu estructura)
            cursor.execute("""
                SELECT id_empleado
                FROM EMPLEADO
                WHERE id_rol = (SELECT id_rol FROM ROL WHERE nombre = 'Medico')
                AND estado = 'Activo'
            """)
            medicos = cursor.fetchall()

            if not medicos:
                print("No se encontraron médicos activos en la base de datos.")
                return

            print(f"Se encontraron {len(medicos)} médicos activos.")

            # Fechas para noviembre y diciembre 2025
            fecha_inicio = datetime(2025, 11, 10)  # Desde hoy
            fecha_fin = datetime(2025, 12, 31)

            # Turnos
            turnos = [
                ('07:00:00', '13:00:00'),  # Turno mañana
                ('14:00:00', '22:00:00')   # Turno tarde
            ]

            total_insertados = 0
            fecha_actual = fecha_inicio

            while fecha_actual <= fecha_fin:
                # Verificar si es día laborable (lunes=0, domingo=6)
                if fecha_actual.weekday() < 5:  # Lunes a viernes
                    for medico in medicos:
                        for hora_inicio, hora_fin in turnos:
                            try:
                                sql = """
                                    INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, disponibilidad, estado)
                                    VALUES (%s, %s, %s, %s, 'Disponible', 'Activo')
                                """
                                cursor.execute(sql, (
                                    medico['id_empleado'],
                                    fecha_actual.strftime('%Y-%m-%d'),
                                    hora_inicio,
                                    hora_fin
                                ))
                                total_insertados += 1
                            except Exception as e:
                                print(f"Error al insertar horario para médico {medico['id_empleado']} "
                                      f"el {fecha_actual.strftime('%Y-%m-%d')}: {e}")

                fecha_actual += timedelta(days=1)

            # Confirmar los cambios
            conexion.commit()
            print(f"\n¡Éxito! Se insertaron {total_insertados} horarios.")
            print(f"Rango de fechas: {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")
            print(f"Días laborables solamente (lunes a viernes)")
            print(f"Turnos: 07:00-13:00 y 14:00-22:00")

    except Exception as e:
        conexion.rollback()
        print(f"Error al insertar horarios: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    print("=== Inserción de Horarios Médicos ===")
    print("Noviembre y Diciembre 2025")
    print("Solo días laborables (lunes a viernes)\n")

    insertar_horarios_noviembre_diciembre()
