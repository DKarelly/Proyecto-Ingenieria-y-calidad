from bd import obtener_conexion
from datetime import date, time

class Programacion:
    def __init__(self, id_programacion=None, fecha=None, hora_inicio=None,
                 hora_fin=None, id_servicio=None, id_empleado=None,
                 id_horario=None, estado='Activo'):
        self.id_programacion = id_programacion
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.id_servicio = id_servicio
        self.id_empleado = id_empleado
        self.id_horario = id_horario
        self.estado = estado

    @staticmethod
    def crear(fecha, hora_inicio, hora_fin, id_servicio, id_horario):
        """Crea una nueva programación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener id_empleado desde el horario
                sql_empleado = "SELECT id_empleado FROM HORARIO WHERE id_horario = %s"
                cursor.execute(sql_empleado, (id_horario,))
                result = cursor.fetchone()
                if not result:
                    return {'error': 'Horario no encontrado'}
                id_empleado = result['id_empleado']

                sql = """INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin,
                         id_servicio, id_empleado, id_horario, estado)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (fecha, hora_inicio, hora_fin, id_servicio,
                                   id_empleado, id_horario, 'Activo'))
                conexion.commit()
                return {'success': True, 'id_programacion': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todas las programaciones"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*,
                           s.nombre as servicio,
                           ts.nombre as tipo_servicio,
                           ts.id_tipo_servicio as id_tipo_servicio,
                           e.id_empleado as id_empleado,
                           h.id_horario as id_horario,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado
                    FROM PROGRAMACION p
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    ORDER BY p.id_programacion ASC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_programacion):
        """Obtiene una programación por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*,
                           s.nombre as servicio,
                           ts.nombre as tipo_servicio,
                           ts.id_tipo_servicio as id_tipo_servicio,
                           e.id_empleado as id_empleado,
                           h.id_horario as id_horario,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado
                    FROM PROGRAMACION p
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE p.id_programacion = %s
                """
                cursor.execute(sql, (id_programacion,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_programacion, fecha=None, hora_inicio=None,
                  hora_fin=None, id_servicio=None,
                  id_horario=None, estado=None):
        """Actualiza una programación existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []

                if fecha:
                    campos.append("fecha = %s")
                    valores.append(fecha)

                if hora_inicio:
                    campos.append("hora_inicio = %s")
                    valores.append(hora_inicio)

                if hora_fin:
                    campos.append("hora_fin = %s")
                    valores.append(hora_fin)

                if id_servicio:
                    campos.append("id_servicio = %s")
                    valores.append(id_servicio)

                if id_horario:
                    campos.append("id_horario = %s")
                    valores.append(id_horario)
                    # Si se actualiza el horario, obtener el nuevo id_empleado
                    sql_empleado = "SELECT id_empleado FROM HORARIO WHERE id_horario = %s"
                    cursor.execute(sql_empleado, (id_horario,))
                    result = cursor.fetchone()
                    if result:
                        campos.append("id_empleado = %s")
                        valores.append(result['id_empleado'])

                if estado:
                    campos.append("estado = %s")
                    valores.append(estado)

                if not campos:
                    return {'error': 'No hay campos para actualizar'}

                valores.append(id_programacion)
                sql = f"UPDATE PROGRAMACION SET {', '.join(campos)} WHERE id_programacion = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_programacion):
        """Elimina una programación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM PROGRAMACION WHERE id_programacion = %s"
                cursor.execute(sql, (id_programacion,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def buscar_por_filtros(fecha=None, id_empleado=None, estado=None, id_servicio=None, id_tipo_servicio=None):
        """Busca programaciones por filtros"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*,
                           s.nombre as servicio,
                           ts.nombre as tipo_servicio,
                           ts.id_tipo_servicio as id_tipo_servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado
                    FROM PROGRAMACION p
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE 1=1
                """
                params = []

                if fecha:
                    sql += " AND p.fecha = %s"
                    params.append(fecha)

                if id_empleado:
                    sql += " AND p.id_empleado = %s"
                    params.append(id_empleado)

                if estado:
                    sql += " AND p.estado = %s"
                    params.append(estado)

                if id_servicio:
                    sql += " AND p.id_servicio = %s"
                    params.append(id_servicio)

                if id_tipo_servicio:
                    sql += " AND ts.id_tipo_servicio = %s"
                    params.append(id_tipo_servicio)

                sql += " ORDER BY p.fecha DESC, p.hora_inicio"
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
        finally:
            conexion.close()
