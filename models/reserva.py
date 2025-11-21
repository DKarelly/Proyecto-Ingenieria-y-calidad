from bd import obtener_conexion
from datetime import date, time, datetime

class Reserva:
    def __init__(self, id_reserva=None, fecha_registro=None, hora_registro=None,
                 tipo=None, tipo_reserva='CITA_MEDICA', estado='pendiente', 
                 motivo_cancelacion=None, cita_origen_id=None,
                 id_paciente=None, id_programacion=None):
        self.id_reserva = id_reserva
        self.fecha_registro = fecha_registro
        self.hora_registro = hora_registro
        self.tipo = tipo
        self.tipo_reserva = tipo_reserva
        self.estado = estado
        self.motivo_cancelacion = motivo_cancelacion
        self.cita_origen_id = cita_origen_id
        self.id_paciente = id_paciente
        self.id_programacion = id_programacion

    @staticmethod
    @staticmethod
    def crear(tipo, id_paciente, id_programacion, tipo_reserva='CITA_MEDICA', cita_origen_id=None):
        """Crea una nueva reserva
        
        Args:
            tipo: Tipo de reserva (1 por defecto)
            id_paciente: ID del paciente
            id_programacion: ID de la programación
            tipo_reserva: Parámetro heredado (se ignora, solo para compatibilidad)
            cita_origen_id: Parámetro heredado (se ignora, solo para compatibilidad)
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                ahora = datetime.now()
                # NOTA: La tabla RESERVA solo tiene: id_reserva, fecha_registro, hora_registro, tipo, estado, motivo_cancelacion, id_paciente, id_programacion
                sql = """INSERT INTO RESERVA (fecha_registro, hora_registro, tipo, estado, id_paciente, id_programacion) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (ahora.date(), ahora.time(), tipo, 'Confirmada', id_paciente, id_programacion))
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
        """Obtiene reservas de un paciente específico con información del servicio desde PROGRAMACION"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           prog.id_servicio,
                           s.nombre as servicio,
                           ts.nombre as tipo_servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           esp.nombre as especialidad
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
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
        """Actualiza el estado de una reserva y envía notificaciones por email"""
        conexion = obtener_conexion()
        estado_anterior = None
        try:
            with conexion.cursor() as cursor:
                # Obtener el estado anterior y datos de la reserva
                cursor.execute("""
                    SELECT r.estado as estado_anterior, r.id_paciente, r.id_programacion,
                           p.fecha, p.hora_inicio, p.hora_fin, p.id_servicio
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                    WHERE r.id_reserva = %s
                """, (id_reserva,))
                reserva_data = cursor.fetchone()
                
                if not reserva_data:
                    return {'error': 'Reserva no encontrada'}
                
                estado_anterior = reserva_data.get('estado_anterior')
                
                # Si el estado no cambió, no hacer nada
                if estado_anterior == estado:
                    return {'success': True, 'affected_rows': 0, 'message': 'Estado sin cambios'}
                
                # Actualizar estado
                sql = "UPDATE RESERVA SET estado = %s, motivo_cancelacion = %s WHERE id_reserva = %s"
                cursor.execute(sql, (estado, motivo_cancelacion, id_reserva))
                conexion.commit()
                
                # Enviar emails de notificación
                try:
                    from utils.email_service import enviar_email_cambio_estado_reserva
                    
                    # Obtener datos del paciente
                    cursor.execute("""
                        SELECT CONCAT(pac.nombres, ' ', pac.apellidos) as nombre_paciente,
                               u_paciente.correo as email_paciente
                        FROM PACIENTE pac
                        INNER JOIN USUARIO u_paciente ON pac.id_usuario = u_paciente.id_usuario
                        WHERE pac.id_paciente = %s
                    """, (reserva_data['id_paciente'],))
                    paciente_data = cursor.fetchone()
                    
                    # Obtener datos del médico y servicio
                    cursor.execute("""
                        SELECT CONCAT(e.nombres, ' ', e.apellidos) as nombre_medico,
                               u_medico.correo as email_medico,
                               s.nombre as servicio_nombre
                        FROM PROGRAMACION prog
                        INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                        INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                        INNER JOIN USUARIO u_medico ON e.id_usuario = u_medico.id_usuario
                        INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                        WHERE prog.id_programacion = %s
                    """, (reserva_data['id_programacion'],))
                    medico_data = cursor.fetchone()
                    
                    if paciente_data and medico_data:
                        # Formatear fecha y hora
                        fecha = reserva_data.get('fecha')
                        fecha_str = fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else str(fecha)
                        hora_inicio = reserva_data.get('hora_inicio')
                        hora_inicio_str = str(hora_inicio)[:5] if hora_inicio else ''
                        hora_fin = reserva_data.get('hora_fin')
                        hora_fin_str = str(hora_fin)[:5] if hora_fin else ''
                        
                        # Enviar emails
                        resultado_email = enviar_email_cambio_estado_reserva(
                            paciente_email=paciente_data.get('email_paciente'),
                            paciente_nombre=paciente_data.get('nombre_paciente', 'Paciente'),
                            medico_email=medico_data.get('email_medico'),
                            medico_nombre=medico_data.get('nombre_medico', 'Médico'),
                            id_reserva=id_reserva,
                            estado_anterior=estado_anterior,
                            estado_nuevo=estado,
                            fecha=fecha_str,
                            hora_inicio=hora_inicio_str,
                            hora_fin=hora_fin_str,
                            servicio=medico_data.get('servicio_nombre', ''),
                            motivo=motivo_cancelacion
                        )
                        
                        if resultado_email.get('paciente') and resultado_email['paciente'].get('success'):
                            print(f"📧✅ Email de cambio de estado enviado al paciente: {paciente_data.get('email_paciente')}")
                        if resultado_email.get('medico') and resultado_email['medico'].get('success'):
                            print(f"📧✅ Email de cambio de estado enviado al médico: {medico_data.get('email_medico')}")
                except Exception as e:
                    print(f"📧❌ Error enviando emails de cambio de estado: {e}")
                    import traceback
                    traceback.print_exc()
                    # No fallar la actualización si el email falla
                
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
        return Reserva.actualizar_estado(id_reserva, 'Cancelada', motivo)

    @staticmethod
    def confirmar(id_reserva):
        """Confirma una reserva"""
        return Reserva.actualizar_estado(id_reserva, 'Confirmada')

    @staticmethod
    def completar(id_reserva):
        """Marca una reserva como completada"""
        return Reserva.actualizar_estado(id_reserva, 'Completada')

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
                    LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    WHERE r.estado = %s
                    ORDER BY prog.fecha, prog.hora_inicio
                """
                cursor.execute(sql, (estado,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_tipo(tipo_reserva, id_paciente=None):
        """Obtiene reservas por tipo (CITA_MEDICA, OPERACION, EXAMEN)
        
        Args:
            tipo_reserva: Tipo de reserva a filtrar
            id_paciente: ID del paciente (opcional)
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                if id_paciente:
                    sql = """
                        SELECT r.*,
                               CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
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
                        LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                        LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                        LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                        LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                        LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                        WHERE r.tipo_reserva = %s AND r.id_paciente = %s
                        ORDER BY prog.fecha DESC, prog.hora_inicio DESC
                    """
                    cursor.execute(sql, (tipo_reserva, id_paciente))
                else:
                    sql = """
                        SELECT r.*,
                               CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
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
                        LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                        LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                        LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                        LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                        LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                        WHERE r.tipo_reserva = %s
                        ORDER BY prog.fecha DESC, prog.hora_inicio DESC
                    """
                    cursor.execute(sql, (tipo_reserva,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_derivadas(id_cita_origen):
        """Obtiene todas las reservas derivadas de una cita médica"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           r.tipo_reserva,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           COALESCE(s.nombre, 'Sin servicio') as servicio
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    WHERE r.cita_origen_id = %s
                    ORDER BY prog.fecha DESC
                """
                cursor.execute(sql, (id_cita_origen,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_historial_clinico(id_paciente):
        """Obtiene el historial clínico (solo citas completadas con diagnóstico)"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.id_reserva,
                           r.fecha_registro,
                           c.fecha_cita,
                           c.diagnostico,
                           c.observaciones,
                           c.tratamiento,
                           c.estado as estado_cita,
                           CONCAT(e.nombres, ' ', e.apellidos) as medico,
                           esp.nombre as especialidad,
                           COALESCE(s.nombre, 'Consulta General') as servicio,
                           (SELECT COUNT(*) FROM RESERVA WHERE cita_origen_id = r.id_reserva 
                            AND tipo_reserva = 'OPERACION') as operaciones_derivadas,
                           (SELECT COUNT(*) FROM RESERVA WHERE cita_origen_id = r.id_reserva 
                            AND tipo_reserva = 'EXAMEN') as examenes_derivados
                    FROM RESERVA r
                    INNER JOIN CITA c ON r.id_reserva = c.id_reserva
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE r.id_paciente = %s
                      AND r.tipo_reserva = 'CITA_MEDICA'
                      AND r.estado = 'completada'
                      AND c.diagnostico IS NOT NULL
                      AND c.diagnostico != ''
                    ORDER BY c.fecha_cita DESC
                """
                cursor.execute(sql, (id_paciente,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_con_filtros(id_paciente=None, tipo_reserva=None, estado=None, 
                           fecha_desde=None, fecha_hasta=None, id_especialidad=None,
                           id_empleado=None):
        """Obtiene reservas con múltiples filtros opcionales"""
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
                           COALESCE(s.nombre, 'Sin servicio') as servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           esp.nombre as especialidad
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE 1=1
                """
                params = []
                
                if id_paciente:
                    sql += " AND r.id_paciente = %s"
                    params.append(id_paciente)
                
                if tipo_reserva:
                    sql += " AND r.tipo_reserva = %s"
                    params.append(tipo_reserva)
                
                if estado:
                    sql += " AND r.estado = %s"
                    params.append(estado)
                
                if fecha_desde:
                    sql += " AND prog.fecha >= %s"
                    params.append(fecha_desde)
                
                if fecha_hasta:
                    sql += " AND prog.fecha <= %s"
                    params.append(fecha_hasta)
                
                if id_especialidad:
                    sql += " AND e.id_especialidad = %s"
                    params.append(id_especialidad)
                
                if id_empleado:
                    sql += " AND h.id_empleado = %s"
                    params.append(id_empleado)
                
                sql += " ORDER BY prog.fecha DESC, prog.hora_inicio DESC"
                
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            conexion.close()
