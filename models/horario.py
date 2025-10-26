from bd import obtener_conexion
from datetime import date, time

class Horario:
    def __init__(self, id_horario=None, id_empleado=None, fecha=None,
                 hora_inicio=None, hora_fin=None, estado='disponible'):
        self.id_horario = id_horario
        self.id_empleado = id_empleado
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.estado = estado

    @staticmethod
    def crear(id_empleado, fecha, hora_inicio, hora_fin):
        """Crea un nuevo horario"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, 
                         hora_fin, estado) VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (id_empleado, fecha, hora_inicio, 
                                   hora_fin, 'disponible'))
                conexion.commit()
                return {'success': True, 'id_horario': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los horarios"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT h.*,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           r.nombre as rol,
                           esp.nombre as especialidad
                    FROM HORARIO h
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    ORDER BY h.fecha DESC, h.hora_inicio
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_horario):
        """Obtiene un horario por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT h.*,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           e.documento_identidad,
                           r.nombre as rol,
                           esp.nombre as especialidad
                    FROM HORARIO h
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE h.id_horario = %s
                """
                cursor.execute(sql, (id_horario,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_empleado(id_empleado):
        """Obtiene horarios de un empleado"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT h.*
                    FROM HORARIO h
                    WHERE h.id_empleado = %s
                    ORDER BY h.fecha DESC, h.hora_inicio
                """
                cursor.execute(sql, (id_empleado,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_fecha(fecha):
        """Obtiene horarios de una fecha específica"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT h.*,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           r.nombre as rol,
                           esp.nombre as especialidad
                    FROM HORARIO h
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE h.fecha = %s
                    ORDER BY h.hora_inicio
                """
                cursor.execute(sql, (fecha,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_disponibles(fecha, id_empleado=None):
        """Obtiene horarios disponibles"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT h.*,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           esp.nombre as especialidad
                    FROM HORARIO h
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE h.fecha = %s AND h.estado = 'disponible'
                """
                params = [fecha]
                
                if id_empleado:
                    sql += " AND h.id_empleado = %s"
                    params.append(id_empleado)
                
                sql += " ORDER BY h.hora_inicio"
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar_estado(id_horario, estado):
        """Actualiza el estado de un horario"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE HORARIO SET estado = %s WHERE id_horario = %s"
                cursor.execute(sql, (estado, id_horario))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_horario, fecha=None, hora_inicio=None, 
                  hora_fin=None, estado=None):
        """Actualiza un horario existente"""
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
                
                if estado:
                    campos.append("estado = %s")
                    valores.append(estado)
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_horario)
                sql = f"UPDATE HORARIO SET {', '.join(campos)} WHERE id_horario = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_horario):
        """Elimina un horario"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM HORARIO WHERE id_horario = %s"
                cursor.execute(sql, (id_horario,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()
