from bd import obtener_conexion
from datetime import date, time, datetime

class Reserva:
    def __init__(self, id_reserva=None, fecha_registro=None, hora_registro=None,
                 tipo=None, estado='pendiente', motivo_cancelacion=None,
                 id_paciente=None, id_programacion=None):
        self.id_reserva = id_reserva
        self.fecha_registro = fecha_registro
        self.hora_registro = hora_registro
        self.tipo = tipo
        self.estado = estado
        self.motivo_cancelacion = motivo_cancelacion
        self.id_paciente = id_paciente
        self.id_programacion = id_programacion

    @staticmethod
    def crear(tipo, id_paciente, id_programacion):
        """Crea una nueva reserva"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                ahora = datetime.now()
                sql = """INSERT INTO RESERVA (fecha_registro, hora_registro, tipo, estado, 
                         id_paciente, id_programacion) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (ahora.date(), ahora.time(), tipo, 'pendiente', 
                                   id_paciente, id_programacion))
                conexion.commit()
                return {'success': True, 'id_reserva': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todas las reservas"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           s.nombre as servicio,
                           ts.nombre as tipo_servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           esp.nombre as especialidad
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    ORDER BY r.fecha_registro DESC, r.hora_registro DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_reserva):
        """Obtiene una reserva por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           p.sexo,
                           u.correo,
                           u.telefono,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           prog.estado as estado_programacion,
                           s.nombre as servicio,
                           s.descripcion as descripcion_servicio,
                           ts.nombre as tipo_servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           e.id_empleado,
                           esp.nombre as especialidad
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE r.id_reserva = %s
                """
                cursor.execute(sql, (id_reserva,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_paciente(id_paciente):
        """Obtiene reservas de un paciente específico"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           s.nombre as servicio,
                           ts.nombre as tipo_servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           esp.nombre as especialidad
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE r.id_paciente = %s
                    ORDER BY prog.fecha DESC, prog.hora_inicio DESC
                """
                cursor.execute(sql, (id_paciente,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_empleado(id_empleado):
        """Obtiene reservas de un empleado específico"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           s.nombre as servicio,
                           ts.nombre as tipo_servicio
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                    WHERE h.id_empleado = %s
                    ORDER BY prog.fecha DESC, prog.hora_inicio DESC
                """
                cursor.execute(sql, (id_empleado,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_fecha(fecha):
        """Obtiene reservas de una fecha específica"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           s.nombre as servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE prog.fecha = %s
                    ORDER BY prog.hora_inicio
                """
                cursor.execute(sql, (fecha,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar_estado(id_reserva, estado, motivo_cancelacion=None):
        """Actualiza el estado de una reserva"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE RESERVA SET estado = %s, motivo_cancelacion = %s WHERE id_reserva = %s"
                cursor.execute(sql, (estado, motivo_cancelacion, id_reserva))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def reprogramar(id_reserva, nuevo_id_programacion):
        """Reprograma una reserva a una nueva programación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE RESERVA SET id_programacion = %s WHERE id_reserva = %s"
                cursor.execute(sql, (nuevo_id_programacion, id_reserva))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def cancelar(id_reserva, motivo):
        """Cancela una reserva"""
        return Reserva.actualizar_estado(id_reserva, 'cancelada', motivo)

    @staticmethod
    def confirmar(id_reserva):
        """Confirma una reserva"""
        return Reserva.actualizar_estado(id_reserva, 'confirmada')

    @staticmethod
    def completar(id_reserva):
        """Marca una reserva como completada"""
        return Reserva.actualizar_estado(id_reserva, 'completada')

    @staticmethod
    def obtener_por_estado(estado):
        """Obtiene reservas por estado"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           s.nombre as servicio
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    WHERE r.estado = %s
                    ORDER BY prog.fecha, prog.hora_inicio
                """
                cursor.execute(sql, (estado,))
                return cursor.fetchall()
        finally:
            conexion.close()
