from bd import obtener_conexion
from datetime import datetime
from utils.email_service import email_service

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
        """Crea una nueva notificación y envía email al paciente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Allow scheduling notifications for a future date/time by using
                # optional override attributes set on this class temporarily.
                ahora = datetime.now()
                fecha_envio = ahora.date()
                hora_envio = ahora.time()
                # Backwards compatible: some callers will not provide overrides.
                if hasattr(Notificacion, '_override_fecha_envio') and Notificacion._override_fecha_envio:
                    fecha_envio = Notificacion._override_fecha_envio
                if hasattr(Notificacion, '_override_hora_envio') and Notificacion._override_hora_envio:
                    hora_envio = Notificacion._override_hora_envio

                # Intentar insertar con id_usuario primero
                try:
                    sql = """INSERT INTO NOTIFICACION (titulo, mensaje, tipo, fecha_envio, 
                             hora_envio, id_reserva, id_paciente, id_usuario) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (titulo, mensaje, tipo, fecha_envio, hora_envio, id_reserva, id_paciente, None))
                    conexion.commit()
                except Exception as e:
                    # Si falla porque no existe el campo id_usuario, intentar sin él
                    error_str = str(e).lower()
                    if 'id_usuario' in error_str or 'unknown column' in error_str:
                        print(f"⚠️ Campo id_usuario no existe en NOTIFICACION, insertando sin él...")
                        sql = """INSERT INTO NOTIFICACION (titulo, mensaje, tipo, fecha_envio, 
                                 hora_envio, id_reserva, id_paciente) 
                                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                        cursor.execute(sql, (titulo, mensaje, tipo, fecha_envio, hora_envio, id_reserva, id_paciente))
                        conexion.commit()
                    else:
                        raise
                
                id_notificacion = cursor.lastrowid
                
                # Obtener datos del paciente para enviar email
                sql_paciente = """
                    SELECT CONCAT(p.nombres, ' ', p.apellidos) as nombre_completo, u.correo
                    FROM PACIENTE p
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    WHERE p.id_paciente = %s
                """
                cursor.execute(sql_paciente, (id_paciente,))
                paciente = cursor.fetchone()
                
                # Enviar email al paciente (NO CRÍTICO - si falla, la notificación ya está creada)
                # USO DE PROTOCOLO ASÍNCRONO: El email se envía en segundo plano para no bloquear la respuesta HTTP
                email_enviado = False
                email_mensaje = ''
                if paciente and paciente['correo']:
                    try:
                        # Usar envío asíncrono (no bloqueante) para evitar timeouts de Gunicorn
                        from utils.email_service import invocar_protocolo_envio_rapido
                        
                        # Esto retorna inmediatamente (no espera a Gmail)
                        # El email se enviará en un hilo separado
                        email_lanzado = invocar_protocolo_envio_rapido(
                            email_service,
                            destinatario_email=paciente['correo'],
                            destinatario_nombre=paciente['nombre_completo'],
                            titulo=titulo,
                            mensaje=mensaje,
                            tipo=tipo
                        )
                        
                        # Como es asíncrono, asumimos que se enviará (no podemos saber el resultado inmediatamente)
                        email_enviado = email_lanzado
                        email_mensaje = 'Email despachado en segundo plano' if email_lanzado else 'Error al despachar email'
                        
                    except Exception as e:
                        # Error enviando email NO debe fallar la creación de notificación
                        print(f"⚠️ Error despachando email de notificación (no crítico): {e}")
                        email_enviado = False
                        email_mensaje = f'Error al despachar email: {str(e)}'
                else:
                    email_mensaje = 'Correo del paciente no disponible'
                
                # SIEMPRE devolver éxito - la notificación ya está creada
                return {
                    'success': True, 
                    'id_notificacion': id_notificacion,
                    'email_enviado': email_enviado,
                    'email_mensaje': email_mensaje
                }
                    
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
        """Obtiene notificaciones de un paciente con estado de reserva"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT n.*, r.estado as estado_reserva
                    FROM NOTIFICACION n
                    LEFT JOIN RESERVA r ON n.id_reserva = r.id_reserva
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
        """Crea una notificación de recordatorio de cita con información completa"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener información completa de la reserva
                sql = """
                    SELECT 
                        r.id_reserva,
                        p.fecha,
                        TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                        TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                        CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                        esp.nombre as especialidad,
                        s.nombre as servicio_nombre
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                    INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    WHERE r.id_reserva = %s
                """
                cursor.execute(sql, (id_reserva,))
                reserva_data = cursor.fetchone()
                
                if reserva_data:
                    medico_nombre = reserva_data.get('medico_nombre', 'Médico')
                    especialidad = reserva_data.get('especialidad', '')
                    servicio = reserva_data.get('servicio_nombre', '')
                    
                    # Formatear fecha
                    fecha_obj = reserva_data.get('fecha')
                    if fecha_obj:
                        if hasattr(fecha_obj, 'strftime'):
                            fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                        else:
                            fecha_formateada = str(fecha_obj)
                    else:
                        fecha_formateada = str(fecha_cita) if fecha_cita else 'Fecha no disponible'
                    
                    # Formatear hora
                    hora_obj = reserva_data.get('hora_inicio')
                    if hora_obj:
                        if hasattr(hora_obj, 'strftime'):
                            hora_formateada = hora_obj.strftime('%H:%M')
                        elif isinstance(hora_obj, str):
                            hora_formateada = hora_obj[:5] if len(hora_obj) >= 5 else hora_obj
                        else:
                            hora_formateada = str(hora_obj)[:5] if len(str(hora_obj)) >= 5 else str(hora_obj)
                    else:
                        hora_formateada = str(hora_cita) if hora_cita else 'Hora no disponible'
                    
                    titulo = "Recordatorio de Cita Médica"
                    mensaje = f"""
                    <div style="margin: 15px 0;">
                        <p style="margin: 10px 0; font-size: 15px; color: #374151;">
                            Le recordamos que tiene una <strong>cita médica programada</strong>.
                        </p>
                        <div style="background-color: #f9fafb; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 4px;">
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>👨‍⚕️ Médico:</strong> {medico_nombre}</p>
                            {f'<p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>🏥 Especialidad:</strong> {especialidad}</p>' if especialidad else ''}
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>📅 Fecha:</strong> {fecha_formateada}</p>
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>⏰ Hora:</strong> {hora_formateada}</p>
                        </div>
                        <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; border-radius: 4px;">
                            <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
                                <strong>⚠️ Aviso de Seguimiento:</strong> Para asegurar su asistencia, este sistema automático le enviará recordatorios <strong>cada 24 horas</strong> hasta el momento de su cita. El próximo recordatorio será <strong>2 horas antes</strong> de su cita programada.
                            </p>
                        </div>
                    </div>
                    """
                else:
                    # Fallback si no se encuentra la reserva
                    titulo = "Recordatorio de Cita"
                    mensaje = f"Tiene una cita programada para el {fecha_cita} a las {hora_cita}"
                
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de reserva para recordatorio: {e}")
            titulo = "Recordatorio de Cita"
            mensaje = f"Tiene una cita programada para el {fecha_cita} a las {hora_cita}"
        finally:
            conexion.close()
        
        # Temporarily override the fecha/hora used by crear to schedule this notification
        try:
            # Convertir fecha_cita a date si es necesario
            fecha_envio_obj = fecha_cita
            if isinstance(fecha_cita, str):
                from datetime import datetime as dt
                try:
                    fecha_envio_obj = dt.strptime(fecha_cita, '%Y-%m-%d').date()
                except:
                    try:
                        fecha_envio_obj = dt.strptime(fecha_cita, '%d/%m/%Y').date()
                    except:
                        fecha_envio_obj = datetime.now().date()
            
            # Convertir hora_cita a time si es necesario
            hora_envio_obj = hora_cita
            if isinstance(hora_cita, str):
                from datetime import datetime as dt
                # Limpiar la hora (remover espacios y caracteres extra)
                hora_limpia = hora_cita.strip().rstrip(':')
                try:
                    # Intentar parsear como HH:MM o HH:MM:SS
                    if ':' in hora_limpia:
                        hora_parts = hora_limpia.split(':')
                        if len(hora_parts) >= 2:
                            hora_str = f"{hora_parts[0].zfill(2)}:{hora_parts[1].zfill(2)}"
                            hora_envio_obj = dt.strptime(hora_str, '%H:%M').time()
                        else:
                            hora_envio_obj = datetime.now().time()
                    else:
                        hora_envio_obj = datetime.now().time()
                except Exception as e:
                    print(f"⚠️ Error parseando hora '{hora_cita}': {e}")
                    # Si falla, usar hora actual como fallback
                    hora_envio_obj = datetime.now().time()
            elif not hasattr(hora_cita, 'hour'):
                # Si no es un objeto time, usar hora actual
                hora_envio_obj = datetime.now().time()
            
            Notificacion._override_fecha_envio = fecha_envio_obj
            Notificacion._override_hora_envio = hora_envio_obj
            return Notificacion.crear(titulo, mensaje, 'recordatorio', id_paciente, id_reserva)
        finally:
            Notificacion._override_fecha_envio = None
            Notificacion._override_hora_envio = None

    @staticmethod
    def crear_confirmacion_reserva(id_paciente, id_reserva):
        """Crea una notificación de confirmación de reserva con información completa"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener información completa de la reserva
                sql = """
                    SELECT 
                        r.id_reserva,
                        p.fecha,
                        p.hora_inicio,
                        p.hora_fin,
                        CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                        esp.nombre as especialidad,
                        s.nombre as servicio_nombre
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                    INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    WHERE r.id_reserva = %s
                """
                cursor.execute(sql, (id_reserva,))
                reserva_data = cursor.fetchone()
                
                if reserva_data:
                    medico_nombre = reserva_data.get('medico_nombre', 'Médico')
                    especialidad = reserva_data.get('especialidad', '')
                    servicio = reserva_data.get('servicio_nombre', '')
                    fecha_obj = reserva_data.get('fecha')
                    hora_inicio_obj = reserva_data.get('hora_inicio')
                    hora_fin_obj = reserva_data.get('hora_fin')
                    
                    # Formatear fecha
                    if fecha_obj:
                        if hasattr(fecha_obj, 'strftime'):
                            fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                        else:
                            fecha_formateada = str(fecha_obj)
                    else:
                        fecha_formateada = 'Fecha no disponible'
                    
                    # Formatear horas
                    if hora_inicio_obj:
                        if hasattr(hora_inicio_obj, 'strftime'):
                            hora_inicio = hora_inicio_obj.strftime('%H:%M')
                        elif isinstance(hora_inicio_obj, str):
                            hora_inicio = hora_inicio_obj[:5] if len(hora_inicio_obj) >= 5 else hora_inicio_obj
                        else:
                            hora_inicio = str(hora_inicio_obj)[:5] if len(str(hora_inicio_obj)) >= 5 else str(hora_inicio_obj)
                    else:
                        hora_inicio = 'Hora no disponible'
                    
                    if hora_fin_obj:
                        if hasattr(hora_fin_obj, 'strftime'):
                            hora_fin = hora_fin_obj.strftime('%H:%M')
                        elif isinstance(hora_fin_obj, str):
                            hora_fin = hora_fin_obj[:5] if len(hora_fin_obj) >= 5 else hora_fin_obj
                        else:
                            hora_fin = str(hora_fin_obj)[:5] if len(str(hora_fin_obj)) >= 5 else str(hora_fin_obj)
                    else:
                        hora_fin = ''
                    
                    hora_completa = f"{hora_inicio} - {hora_fin}" if hora_fin else hora_inicio
                    
                    titulo = "Reserva Médica Generada"
                    mensaje = f"""
                    <div style="margin: 15px 0;">
                        <p style="margin: 10px 0; font-size: 15px; color: #374151;">
                            Su reserva ha sido generada exitosamente en nuestro sistema.
                        </p>
                        <div style="background-color: #f9fafb; border-left: 4px solid #22c55e; padding: 15px; margin: 15px 0; border-radius: 4px;">
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>👨‍⚕️ Médico:</strong> {medico_nombre}</p>
                            {f'<p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>🏥 Especialidad:</strong> {especialidad}</p>' if especialidad else ''}
                            {f'<p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>📋 Servicio:</strong> {servicio}</p>' if servicio else ''}
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>📅 Fecha:</strong> {fecha_formateada}</p>
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>⏰ Hora:</strong> {hora_completa}</p>
                        </div>
                    </div>
                    """
                else:
                    # Fallback si no se encuentra la reserva
                    titulo = "Reserva Generada"
                    mensaje = "Su reserva ha sido generada exitosamente"
                
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de reserva para confirmación: {e}")
            titulo = "Reserva Generada"
            mensaje = "Su reserva ha sido generada exitosamente"
        finally:
            conexion.close()
        
        return Notificacion.crear(titulo, mensaje, 'confirmacion', id_paciente, id_reserva)
    
    @staticmethod
    def crear_notificacion_estado_reserva(id_paciente, id_reserva, estado):
        """Crea una notificación informando el estado actual de la reserva con información completa"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener información completa de la reserva
                sql = """
                    SELECT 
                        r.id_reserva,
                        r.estado,
                        p.fecha,
                        p.hora_inicio,
                        p.hora_fin,
                        CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                        esp.nombre as especialidad,
                        s.nombre as servicio_nombre
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                    INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    WHERE r.id_reserva = %s
                """
                cursor.execute(sql, (id_reserva,))
                reserva_data = cursor.fetchone()
                
                # Mensajes personalizados según el estado
                mensajes_estado = {
                    'Pendiente': 'Su reserva está pendiente de confirmación',
                    'Confirmada': 'Su reserva ha sido confirmada',
                    'Cancelada': 'Su reserva ha sido cancelada',
                    'Completada': 'Su reserva ha sido completada'
                }
                
                mensaje_estado = mensajes_estado.get(estado, f'Su reserva está en estado: {estado}')
                
                if reserva_data:
                    medico_nombre = reserva_data.get('medico_nombre', 'Médico')
                    especialidad = reserva_data.get('especialidad', '')
                    servicio = reserva_data.get('servicio_nombre', '')
                    fecha_obj = reserva_data.get('fecha')
                    hora_inicio_obj = reserva_data.get('hora_inicio')
                    hora_fin_obj = reserva_data.get('hora_fin')
                    
                    # Formatear fecha
                    if fecha_obj:
                        if hasattr(fecha_obj, 'strftime'):
                            fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                        else:
                            fecha_formateada = str(fecha_obj)
                    else:
                        fecha_formateada = 'Fecha no disponible'
                    
                    # Formatear horas
                    if hora_inicio_obj:
                        if hasattr(hora_inicio_obj, 'strftime'):
                            hora_inicio = hora_inicio_obj.strftime('%H:%M')
                        elif isinstance(hora_inicio_obj, str):
                            hora_inicio = hora_inicio_obj[:5] if len(hora_inicio_obj) >= 5 else hora_inicio_obj
                        else:
                            hora_inicio = str(hora_inicio_obj)[:5] if len(str(hora_inicio_obj)) >= 5 else str(hora_inicio_obj)
                    else:
                        hora_inicio = 'Hora no disponible'
                    
                    if hora_fin_obj:
                        if hasattr(hora_fin_obj, 'strftime'):
                            hora_fin = hora_fin_obj.strftime('%H:%M')
                        elif isinstance(hora_fin_obj, str):
                            hora_fin = hora_fin_obj[:5] if len(hora_fin_obj) >= 5 else hora_fin_obj
                        else:
                            hora_fin = str(hora_fin_obj)[:5] if len(str(hora_fin_obj)) >= 5 else str(hora_fin_obj)
                    else:
                        hora_fin = ''
                    
                    hora_completa = f"{hora_inicio} - {hora_fin}" if hora_fin else hora_inicio
                    
                    titulo = f"Estado de Reserva: {estado}"
                    mensaje = f"""
                    <div style="margin: 15px 0;">
                        <p style="margin: 10px 0; font-size: 15px; color: #374151;">
                            {mensaje_estado}
                        </p>
                        <div style="background-color: #f9fafb; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 4px;">
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>👨‍⚕️ Médico:</strong> {medico_nombre}</p>
                            {f'<p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>🏥 Especialidad:</strong> {especialidad}</p>' if especialidad else ''}
                            {f'<p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>📋 Servicio:</strong> {servicio}</p>' if servicio else ''}
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>📅 Fecha:</strong> {fecha_formateada}</p>
                            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>⏰ Hora:</strong> {hora_completa}</p>
                        </div>
                    </div>
                    """
                else:
                    # Fallback si no se encuentra la reserva
                    titulo = "Estado de Reserva"
                    mensaje = mensaje_estado
                
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de reserva para estado: {e}")
            titulo = "Estado de Reserva"
            mensaje = mensajes_estado.get(estado, f'Su reserva está en estado: {estado}')
        finally:
            conexion.close()
        
        return Notificacion.crear(titulo, mensaje, 'estado', id_paciente, id_reserva)

    @staticmethod
    def crear_cancelacion_reserva(id_paciente, id_reserva, motivo):
        """Crea una notificación de cancelación de reserva"""
        titulo = "Reserva Cancelada"
        mensaje = f"Su reserva ha sido cancelada. Motivo: {motivo}"
        return Notificacion.crear(titulo, mensaje, 'cancelacion', id_paciente, id_reserva)

    @staticmethod
    def marcar_como_leida(id_notificacion):
        """Marca una notificación como leída"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                ahora = datetime.now()
                sql = """UPDATE NOTIFICACION 
                         SET leida = TRUE, fecha_leida = %s 
                         WHERE id_notificacion = %s"""
                cursor.execute(sql, (ahora, id_notificacion))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def marcar_todas_como_leidas(id_paciente):
        """Marca todas las notificaciones de un paciente como leídas"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                ahora = datetime.now()
                sql = """UPDATE NOTIFICACION 
                         SET leida = TRUE, fecha_leida = %s 
                         WHERE id_paciente = %s AND leida = FALSE"""
                cursor.execute(sql, (ahora, id_paciente))
                conexion.commit()
                return {'success': True, 'count': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def crear_para_medico(titulo, mensaje, tipo, id_usuario, id_reserva=None):
        """Crea una nueva notificación para un médico (empleado)"""
        print(f"🔍 [DEBUG crear_para_medico] Iniciando. titulo={titulo}, mensaje={mensaje}, tipo={tipo}, id_usuario={id_usuario}, id_reserva={id_reserva}")
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                ahora = datetime.now()
                fecha_envio = ahora.date()
                hora_envio = ahora.time()
                
                print(f"🔍 [DEBUG crear_para_medico] Fecha: {fecha_envio}, Hora: {hora_envio}")
                
                # Intentar insertar con id_usuario, id_paciente como NULL (ya que es para médico)
                try:
                    # Para notificaciones de médico, id_paciente es NULL
                    sql = """INSERT INTO NOTIFICACION (titulo, mensaje, tipo, fecha_envio, 
                             hora_envio, id_reserva, id_paciente, id_usuario) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                    print(f"🔍 [DEBUG crear_para_medico] Ejecutando SQL con id_usuario (id_paciente=NULL): {sql}")
                    print(f"🔍 [DEBUG crear_para_medico] Parámetros: titulo={titulo}, mensaje={mensaje}, tipo={tipo}, fecha_envio={fecha_envio}, hora_envio={hora_envio}, id_reserva={id_reserva}, id_paciente=NULL, id_usuario={id_usuario}")
                    
                    cursor.execute(sql, (titulo, mensaje, tipo, fecha_envio, hora_envio, id_reserva, None, id_usuario))
                    conexion.commit()
                    id_notificacion = cursor.lastrowid
                    
                    print(f"✅ [DEBUG crear_para_medico] Notificación creada exitosamente. ID: {id_notificacion}")
                    return {
                        'success': True, 
                        'id_notificacion': id_notificacion
                    }
                except Exception as e:
                    # Si falla porque no existe el campo id_usuario, intentar sin él
                    error_str = str(e).lower()
                    print(f"⚠️ [DEBUG crear_para_medico] Error al insertar: {e}")
                    
                    if 'id_usuario' in error_str or 'unknown column' in error_str:
                        print(f"⚠️ Campo id_usuario no existe, intentando sin él...")
                        # Si id_usuario no existe, intentar sin él pero tampoco con id_paciente
                        sql = """INSERT INTO NOTIFICACION (titulo, mensaje, tipo, fecha_envio, 
                                 hora_envio, id_reserva) 
                                 VALUES (%s, %s, %s, %s, %s, %s)"""
                        cursor.execute(sql, (titulo, mensaje, tipo, fecha_envio, hora_envio, id_reserva))
                        conexion.commit()
                        id_notificacion = cursor.lastrowid
                        print(f"⚠️ Notificación creada sin id_usuario. Ejecuta el script SQL para agregar el campo.")
                        return {
                            'success': True, 
                            'id_notificacion': id_notificacion,
                            'warning': 'Campo id_usuario no existe en la tabla'
                        }
                    else:
                        raise
        except Exception as e:
            conexion.rollback()
            print(f"❌ Error en crear_para_medico: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_usuario(id_usuario):
        """Obtiene notificaciones de un usuario (médico) con estado de reserva"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Intentar primero con id_usuario
                try:
                    sql = """
                        SELECT n.*, r.estado as estado_reserva
                        FROM NOTIFICACION n
                        LEFT JOIN RESERVA r ON n.id_reserva = r.id_reserva
                        WHERE n.id_usuario = %s
                        ORDER BY n.fecha_envio DESC, n.hora_envio DESC
                    """
                    cursor.execute(sql, (id_usuario,))
                    return cursor.fetchall()
                except Exception as e:
                    # Si falla porque no existe el campo id_usuario, retornar lista vacía
                    error_str = str(e).lower()
                    if 'id_usuario' in error_str or 'unknown column' in error_str:
                        print(f"⚠️ Campo id_usuario no existe en NOTIFICACION. Ejecuta el script SQL para agregarlo.")
                        return []
                    else:
                        raise
        except Exception as e:
            print(f"❌ Error en obtener_por_usuario: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            conexion.close()

    @staticmethod
    def marcar_todas_como_leidas_medico(id_usuario):
        """Marca todas las notificaciones de un médico como leídas"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                ahora = datetime.now()
                sql = """UPDATE NOTIFICACION 
                         SET leida = TRUE, fecha_leida = %s 
                         WHERE id_usuario = %s AND leida = FALSE"""
                cursor.execute(sql, (ahora, id_usuario))
                conexion.commit()
                return {'success': True, 'count': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()
