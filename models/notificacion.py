from bd import obtener_conexion
from datetime import datetime

class Notificacion:
    def __init__(self, id_notificacion=None, titulo=None, mensaje=None,
                 tipo=None, fecha_envio=None, hora_envio=None,
                 id_reserva=None, id_paciente=None):
        self.id_notificacion = id_notificacion
        self.titulo = titulo
        self.mensaje = mensaje
        self.tipo = tipo
        self.fecha_envio = fecha_envio
        self.hora_envio = hora_envio
        self.id_reserva = id_reserva
        self.id_paciente = id_paciente

    @staticmethod
    def crear(titulo, mensaje, tipo, id_paciente, id_reserva=None):
        """Crea una nueva notificación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                ahora = datetime.now()
                sql = """INSERT INTO NOTIFICACION (titulo, mensaje, tipo, fecha_envio, 
                         hora_envio, id_reserva, id_paciente) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (titulo, mensaje, tipo, ahora.date(), 
                                   ahora.time(), id_reserva, id_paciente))
                conexion.commit()
                return {'success': True, 'id_notificacion': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todas():
        """Obtiene todas las notificaciones"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT n.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                           p.documento_identidad,
                           r.id_reserva,
                           r.estado as estado_reserva
                    FROM NOTIFICACION n
                    INNER JOIN PACIENTE p ON n.id_paciente = p.id_paciente
                    LEFT JOIN RESERVA r ON n.id_reserva = r.id_reserva
                    ORDER BY n.fecha_envio DESC, n.hora_envio DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_notificacion):
        """Obtiene una notificación por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT n.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                           p.documento_identidad,
                           u.correo,
                           u.telefono
                    FROM NOTIFICACION n
                    INNER JOIN PACIENTE p ON n.id_paciente = p.id_paciente
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    WHERE n.id_notificacion = %s
                """
                cursor.execute(sql, (id_notificacion,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_paciente(id_paciente):
        """Obtiene notificaciones de un paciente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT n.*
                    FROM NOTIFICACION n
                    WHERE n.id_paciente = %s
                    ORDER BY n.fecha_envio DESC, n.hora_envio DESC
                """
                cursor.execute(sql, (id_paciente,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_tipo(tipo):
        """Obtiene notificaciones por tipo"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT n.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente
                    FROM NOTIFICACION n
                    INNER JOIN PACIENTE p ON n.id_paciente = p.id_paciente
                    WHERE n.tipo = %s
                    ORDER BY n.fecha_envio DESC, n.hora_envio DESC
                """
                cursor.execute(sql, (tipo,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_reserva(id_reserva):
        """Obtiene notificaciones de una reserva"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT n.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente
                    FROM NOTIFICACION n
                    INNER JOIN PACIENTE p ON n.id_paciente = p.id_paciente
                    WHERE n.id_reserva = %s
                    ORDER BY n.fecha_envio DESC, n.hora_envio DESC
                """
                cursor.execute(sql, (id_reserva,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_fecha(fecha):
        """Obtiene notificaciones de una fecha"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT n.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente
                    FROM NOTIFICACION n
                    INNER JOIN PACIENTE p ON n.id_paciente = p.id_paciente
                    WHERE n.fecha_envio = %s
                    ORDER BY n.hora_envio DESC
                """
                cursor.execute(sql, (fecha,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_notificacion):
        """Elimina una notificación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM NOTIFICACION WHERE id_notificacion = %s"
                cursor.execute(sql, (id_notificacion,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def crear_recordatorio_cita(id_paciente, id_reserva, fecha_cita, hora_cita):
        """Crea una notificación de recordatorio de cita"""
        titulo = "Recordatorio de Cita"
        mensaje = f"Tiene una cita programada para el {fecha_cita} a las {hora_cita}"
        return Notificacion.crear(titulo, mensaje, 'recordatorio', id_paciente, id_reserva)

    @staticmethod
    def crear_confirmacion_reserva(id_paciente, id_reserva):
        """Crea una notificación de confirmación de reserva"""
        titulo = "Reserva Confirmada"
        mensaje = "Su reserva ha sido confirmada exitosamente"
        return Notificacion.crear(titulo, mensaje, 'confirmacion', id_paciente, id_reserva)

    @staticmethod
    def crear_cancelacion_reserva(id_paciente, id_reserva, motivo):
        """Crea una notificación de cancelación de reserva"""
        titulo = "Reserva Cancelada"
        mensaje = f"Su reserva ha sido cancelada. Motivo: {motivo}"
        return Notificacion.crear(titulo, mensaje, 'cancelacion', id_paciente, id_reserva)
