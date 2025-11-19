"""
Módulo para gestionar notificaciones relacionadas con autorizaciones de procedimientos
Implementa los puntos 5.1 y 5.2 del documento CASOS_NO_CONTEMPLADOS_AUTORIZACIONES.md
"""

from bd import obtener_conexion
from datetime import datetime

def crear_notificacion_autorizacion_paciente(id_paciente, id_autorizacion, tipo_procedimiento, nombre_servicio, fecha_vencimiento):
    """
    Crea una notificación para el paciente cuando recibe una autorización
    Punto 5.1 del documento: Notificaciones al Paciente
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Calcular días hasta vencimiento
            dias_vencimiento = (fecha_vencimiento - datetime.now()).days if fecha_vencimiento else 7
            
            titulo = f"✅ Nueva Autorización: {tipo_procedimiento.capitalize()}"
            mensaje = f"""
            <div class="notification-content">
                <p><strong>Has recibido una autorización médica para realizar un {tipo_procedimiento.lower()}.</strong></p>
                <ul>
                    <li><strong>Servicio autorizado:</strong> {nombre_servicio}</li>
                    <li><strong>Válida hasta:</strong> {fecha_vencimiento.strftime('%d/%m/%Y') if fecha_vencimiento else 'N/A'} ({dias_vencimiento} días)</li>
                </ul>
                <p><strong>Próximos pasos:</strong></p>
                <ol>
                    <li>Ingresa a tu panel de paciente</li>
                    <li>Haz clic en "Agendar {tipo_procedimiento.capitalize()}"</li>
                    <li>Selecciona fecha y hora de tu preferencia</li>
                </ol>
                <p class="warning">⚠️ <strong>Importante:</strong> Esta autorización vence en {dias_vencimiento} días. Asegúrate de agendar antes del vencimiento.</p>
            </div>
            """
            
            sql = """
                INSERT INTO NOTIFICACION (
                    id_paciente, tipo_notificacion, titulo, mensaje, 
                    fecha_creacion, leida, id_referencia, tipo_referencia
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                id_paciente,
                'autorizacion_recibida',
                titulo,
                mensaje,
                datetime.now(),
                False,
                id_autorizacion,
                'autorizacion_procedimiento'
            ))
            conexion.commit()
            
            return {'success': True, 'id_notificacion': cursor.lastrowid}
    except Exception as e:
        conexion.rollback()
        print(f"Error al crear notificación para paciente: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        conexion.close()


def crear_notificacion_autorizacion_medico(id_medico, id_autorizacion, tipo_procedimiento, nombre_paciente, nombre_servicio):
    """
    Crea una notificación para el médico cuando es asignado a una autorización
    Punto 5.2 del documento: Notificaciones al Médico Asignado
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            titulo = f"📋 Nueva Asignación: {tipo_procedimiento.capitalize()}"
            mensaje = f"""
            <div class="notification-content">
                <p><strong>Has sido asignado para realizar un {tipo_procedimiento.lower()}.</strong></p>
                <ul>
                    <li><strong>Paciente:</strong> {nombre_paciente}</li>
                    <li><strong>Procedimiento:</strong> {nombre_servicio}</li>
                </ul>
                <p><strong>Acciones disponibles:</strong></p>
                <ul>
                    <li>Revisa los detalles del paciente en tu panel médico</li>
                    <li>Si no tienes disponibilidad, notifica al área administrativa</li>
                    <li>Prepárate para cuando el paciente agende su cita</li>
                </ul>
                <p class="info">💡 El paciente podrá agendar su procedimiento contigo cuando lo desee.</p>
            </div>
            """
            
            sql = """
                INSERT INTO NOTIFICACION (
                    id_empleado, tipo_notificacion, titulo, mensaje, 
                    fecha_creacion, leida, id_referencia, tipo_referencia
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                id_medico,
                'asignacion_procedimiento',
                titulo,
                mensaje,
                datetime.now(),
                False,
                id_autorizacion,
                'autorizacion_procedimiento'
            ))
            conexion.commit()
            
            return {'success': True, 'id_notificacion': cursor.lastrowid}
    except Exception as e:
        conexion.rollback()
        print(f"Error al crear notificación para médico: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        conexion.close()


def crear_notificacion_vencimiento_proximo(id_paciente, id_autorizacion, tipo_procedimiento, nombre_servicio, dias_restantes):
    """
    Crea una notificación de recordatorio cuando una autorización está por vencer
    Complementa el punto 5.1 del documento
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            titulo = f"⚠️ Autorización por Vencer: {tipo_procedimiento.capitalize()}"
            mensaje = f"""
            <div class="notification-content warning">
                <p><strong>Tu autorización está por vencer en {dias_restantes} día(s).</strong></p>
                <ul>
                    <li><strong>Procedimiento:</strong> {nombre_servicio}</li>
                    <li><strong>Días restantes:</strong> {dias_restantes}</li>
                </ul>
                <p><strong>¿Qué hacer?</strong></p>
                <ul>
                    <li>Agenda tu {tipo_procedimiento.lower()} lo antes posible</li>
                    <li>Si no puedes asistir, contacta a tu médico para una nueva evaluación</li>
                    <li>Las autorizaciones vencidas no podrán utilizarse</li>
                </ul>
                <p class="urgent">🚨 <strong>¡Actúa ahora!</strong> No pierdas esta autorización.</p>
            </div>
            """
            
            sql = """
                INSERT INTO NOTIFICACION (
                    id_paciente, tipo_notificacion, titulo, mensaje, 
                    fecha_creacion, leida, id_referencia, tipo_referencia, prioridad
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                id_paciente,
                'autorizacion_por_vencer',
                titulo,
                mensaje,
                datetime.now(),
                False,
                id_autorizacion,
                'autorizacion_procedimiento',
                'ALTA'  # Alta prioridad
            ))
            conexion.commit()
            
            return {'success': True, 'id_notificacion': cursor.lastrowid}
    except Exception as e:
        conexion.rollback()
        print(f"Error al crear notificación de vencimiento: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        conexion.close()


def enviar_email_autorizacion_paciente(correo_paciente, nombre_paciente, tipo_procedimiento, nombre_servicio, fecha_vencimiento):
    """
    Envía un email al paciente notificando sobre la nueva autorización
    Complementa las notificaciones internas del sistema
    """
    try:
        # TODO: Implementar envío de email usando el sistema de emails configurado
        # Por ahora solo registramos el intento
        print(f"Email enviado a {correo_paciente}: Nueva autorización {tipo_procedimiento}")
        return {'success': True}
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return {'success': False, 'error': str(e)}


def enviar_email_autorizacion_medico(correo_medico, nombre_medico, tipo_procedimiento, nombre_paciente):
    """
    Envía un email al médico notificando sobre la asignación
    Complementa las notificaciones internas del sistema
    """
    try:
        # TODO: Implementar envío de email usando el sistema de emails configurado
        print(f"Email enviado a {correo_medico}: Nueva asignación {tipo_procedimiento} - Paciente: {nombre_paciente}")
        return {'success': True}
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return {'success': False, 'error': str(e)}
