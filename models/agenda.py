from bd import obtener_conexion

class Agenda:
    def __init__(self):
        pass

    @staticmethod
    def consultar_agenda(id_empleado=None, fecha=None, id_servicio=None):
        """Consulta la agenda médica con filtros opcionales"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT
                        e.id_empleado,
                        CONCAT(e.nombres, ' ', e.apellidos) AS nombre_empleado,
                        r.tipo,
                        CASE r.tipo
                            WHEN 1 THEN 'CITA'
                            WHEN 2 THEN 'OPERACIÓN'
                            WHEN 3 THEN 'EXAMEN'
                            ELSE 'DESCONOCIDO'
                        END AS tipo_reserva,
                        pr.fecha AS fecha,
                        pr.hora_inicio AS hora_inicio,
                        pr.hora_fin AS hora_fin,
                        s.nombre AS servicio,
                        COALESCE(c.estado, o.observaciones, ex.estado, r.estado) AS estado_atencion
                    FROM EMPLEADO e
                    JOIN HORARIO h ON e.id_empleado = h.id_empleado
                    JOIN PROGRAMACION pr ON h.id_horario = pr.id_horario
                    JOIN SERVICIO s ON pr.id_servicio = s.id_servicio
                    JOIN RESERVA r ON pr.id_programacion = r.id_programacion
                    LEFT JOIN CITA c ON r.id_reserva = c.id_reserva
                    LEFT JOIN OPERACION o ON r.id_reserva = o.id_reserva
                    LEFT JOIN EXAMEN ex ON r.id_reserva = ex.id_reserva
                    WHERE s.estado = 'activo'
                """

                params = []

                # Aplicar filtros
                if id_empleado:
                    sql += " AND e.id_empleado = %s"
                    params.append(id_empleado)

                if fecha:
                    sql += " AND pr.fecha = %s"
                    params.append(fecha)

                if id_servicio:
                    sql += " AND s.id_servicio = %s"
                    params.append(id_servicio)

                sql += " ORDER BY pr.fecha, pr.hora_inicio"

                cursor.execute(sql, params)
                resultados = cursor.fetchall()

                # Convertir resultados a lista de diccionarios
                agenda = []
                for row in resultados:
                    agenda.append({
                        'id_empleado': row['id_empleado'],
                        'nombre_empleado': row['nombre_empleado'],
                        'tipo': row['tipo'],
                        'tipo_reserva': row['tipo_reserva'],
                        'fecha': row['fecha'].isoformat() if row['fecha'] else None,
                        'hora_inicio': str(row['hora_inicio']) if row['hora_inicio'] else None,
                        'hora_fin': str(row['hora_fin']) if row['hora_fin'] else None,
                        'servicio': row['servicio'],
                        'estado_atencion': row['estado_atencion']
                    })

                return agenda
        finally:
            conexion.close()
