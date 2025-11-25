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
        """Crea una notificación de recordatorio de cita"""
        titulo = "Recordatorio de Cita"
        mensaje = f"Tiene una cita programada para el {fecha_cita} a las {hora_cita}"
        # Temporarily override the fecha/hora used by crear to schedule this notification
        try:
            Notificacion._override_fecha_envio = fecha_cita
            Notificacion._override_hora_envio = hora_cita
            return Notificacion.crear(titulo, mensaje, 'recordatorio', id_paciente, id_reserva)
        finally:
            Notificacion._override_fecha_envio = None
            Notificacion._override_hora_envio = None

    @staticmethod
    def crear_confirmacion_reserva(id_paciente, id_reserva):
        """Crea una notificación de confirmación de reserva"""
        titulo = "Reserva Generada"
        mensaje = "Su reserva ha sido generada exitosamente"
        return Notificacion.crear(titulo, mensaje, 'confirmacion', id_paciente, id_reserva)
    
    @staticmethod
    def crear_notificacion_estado_reserva(id_paciente, id_reserva, estado):
        """Crea una notificación informando el estado actual de la reserva"""
        titulo = "Estado de Reserva"
        
        # Mensajes personalizados según el estado
        mensajes_estado = {
            'Pendiente': 'Su reserva está pendiente de confirmación',
            'Confirmada': 'Su reserva ha sido confirmada',
            'Cancelada': 'Su reserva ha sido cancelada',
            'Completada': 'Su reserva ha sido completada'
        }
        
        mensaje = mensajes_estado.get(estado, f'Su reserva está en estado: {estado}')
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
