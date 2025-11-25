"""
Custodio_De_Agenda - Sistema de Notificaciones de Alta Precisión
Genera notificaciones estructuradas para Clínica Unión siguiendo el protocolo:
- Qué: Especialidad médica (Rama_De_Curación)
- Quién: Doctor/Especialista (Artífice_Clínico)
- Cuándo: Fecha y hora exacta (Coordenada_Temporal)
- Con Qué Frecuencia: Intervalo de recordatorios (Pulso_De_Recordatorio)

Restricción Absoluta: Prohibido enviar mensajes vagos.
"""

from datetime import datetime
from utils.email_service import email_service


class Capsula_De_Cita:
    """
    Estructura de datos para encapsular información de una cita médica.
    Utiliza nomenclatura específica para mejorar la generación de mensajes.
    """
    
    def __init__(self, doctor, especialidad, fecha, frecuencia_alerta):
        """
        Inicializa la cápsula de cita con los datos necesarios.
        
        Args:
            doctor (str): Nombre del doctor o especialista (Artífice_Clínico)
            especialidad (str): Especialidad médica (Rama_De_Curación)
            fecha (str|datetime): Fecha y hora exacta de la cita (Coordenada_Temporal)
            frecuencia_alerta (str): Intervalo de tiempo para alertas (Pulso_De_Recordatorio)
                                    Ej: "Cada 24 horas", "30 minutos antes", "Cada 12 horas"
        """
        self.Artífice_Clínico = doctor
        self.Rama_De_Curación = especialidad
        self.Coordenada_Temporal = fecha
        self.Pulso_De_Recordatorio = frecuencia_alerta


class Custodio_De_Agenda:
    """
    Sistema automatizado para generar notificaciones de alta precisión.
    Prohibido enviar mensajes vagos - cada transmisión debe responder:
    Qué, Quién, Cuándo y Con Qué Frecuencia.
    """
    
    NOMBRE_CLINICA = "Clínica Unión"
    
    @staticmethod
    def generar_mensaje_nexo(capsula_cita, nombre_paciente):
        """
        Genera el mensaje [Mensaje_Nexo] siguiendo la estructura mental especificada.
        
        Estructura:
        1. Identificación: Saluda al paciente e identifica la clínica
        2. Anclaje: Indica doctor y especialidad
        3. Sincronización: Muestra fecha y hora
        4. Protocolo de Insistencia: Informa sobre frecuencia de recordatorios
        
        Args:
            capsula_cita (Capsula_De_Cita): Objeto con los datos de la cita
            nombre_paciente (str): Nombre completo del paciente
            
        Returns:
            dict: Diccionario con 'asunto' y 'mensaje_html' formateado
        """
        # Formatear la coordenada temporal
        if isinstance(capsula_cita.Coordenada_Temporal, datetime):
            fecha_hora_str = capsula_cita.Coordenada_Temporal.strftime('%d de %B de %Y a las %H:%M')
        else:
            fecha_hora_str = str(capsula_cita.Coordenada_Temporal)
        
        # Generar asunto según plantilla obligatoria
        asunto = f"🔔 Confirmación de Encuentro Médico - {capsula_cita.Rama_De_Curación}"
        
        # Construir mensaje HTML siguiendo la plantilla obligatoria
        mensaje_html = f"""
<div style="margin: 20px 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <!-- Identificación: Saludo e identificación de la clínica -->
    <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 1.6;">
        Hola,
    </p>
    
    <p style="margin: 0 0 25px 0; color: #374151; font-size: 15px; line-height: 1.6;">
        Tu salud es nuestra prioridad en <strong style="color: #0891b2;">{Custodio_De_Agenda.NOMBRE_CLINICA}</strong>. 
        Tu espacio ha sido reservado con éxito.
    </p>
    
    <!-- Detalles del Encuentro -->
    <div style="background-color: #ffffff; border: 2px solid #0891b2; border-radius: 8px; padding: 25px; margin: 25px 0;">
        <h3 style="margin: 0 0 20px 0; color: #0891b2; font-size: 20px; font-weight: 600; border-bottom: 2px solid #e0f2fe; padding-bottom: 10px;">
            Detalles del Encuentro
        </h3>
        
        <!-- Anclaje: Doctor y Especialidad -->
        <div style="margin: 15px 0; padding: 15px; background-color: #f0f9ff; border-left: 4px solid #0891b2; border-radius: 4px;">
            <p style="margin: 0 0 8px 0; color: #0c4a6e; font-size: 15px; font-weight: 600;">
                👨‍⚕️ Especialista a Cargo ({capsula_cita.Artífice_Clínico}):
            </p>
            <p style="margin: 0; color: #374151; font-size: 14px; line-height: 1.6;">
                Te atenderá en el área de <strong style="color: #0891b2;">{capsula_cita.Rama_De_Curación}</strong>.
            </p>
        </div>
        
        <!-- Sincronización: Fecha y Hora -->
        <div style="margin: 15px 0; padding: 15px; background-color: #f0f9ff; border-left: 4px solid #0891b2; border-radius: 4px;">
            <p style="margin: 0 0 8px 0; color: #0c4a6e; font-size: 15px; font-weight: 600;">
                📅 Momento de la Verdad ({fecha_hora_str}):
            </p>
            <p style="margin: 0; color: #374151; font-size: 14px; line-height: 1.6;">
                Por favor, llega <strong style="color: #f59e0b;">10 minutos antes</strong>.
            </p>
        </div>
        
        <!-- Protocolo de Insistencia: CRÍTICO - Informar sobre frecuencia -->
        <div style="margin: 20px 0 0 0; padding: 15px; background-color: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 4px;">
            <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
                <strong>⚠️ Aviso de Seguimiento:</strong> Para asegurar tu asistencia, este sistema automático 
                te enviará un recordatorio <strong style="color: #d97706;">{capsula_cita.Pulso_De_Recordatorio}</strong> 
                hasta el momento de tu cita.
            </p>
        </div>
    </div>
    
    <!-- Firma del sistema -->
    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
        <p style="margin: 0; color: #6b7280; font-size: 12px; font-style: italic; text-align: center;">
            [Custodio_De_Agenda] - Sistema Automatizado
        </p>
    </div>
</div>
        """
        
        return {
            'asunto': asunto,
            'mensaje_html': mensaje_html
        }
    
    @staticmethod
    def enviar_notificacion_cita(paciente_email, paciente_nombre, capsula_cita):
        """
        Envía la notificación de cita usando el sistema de email existente.
        
        Args:
            paciente_email (str): Email del paciente
            paciente_nombre (str): Nombre completo del paciente
            capsula_cita (Capsula_De_Cita): Objeto con los datos de la cita
            
        Returns:
            dict: Resultado del envío {'success': True/False, 'message': str}
        """
        # Generar el mensaje usando la lógica del Custodio
        mensaje_data = Custodio_De_Agenda.generar_mensaje_nexo(capsula_cita, paciente_nombre)
        
        # Enviar usando el servicio de email existente
        resultado = email_service.enviar_notificacion_email(
            destinatario_email=paciente_email,
            destinatario_nombre=paciente_nombre,
            titulo=mensaje_data['asunto'],
            mensaje=mensaje_data['mensaje_html'],
            tipo='confirmacion'
        )
        
        return resultado
    
    @staticmethod
    def crear_capsula_desde_reserva(id_reserva, frecuencia_alerta="Cada 24 horas"):
        """
        Crea una Capsula_De_Cita desde los datos de una reserva en la base de datos.
        Útil para integrar con el sistema existente.
        
        Args:
            id_reserva (int): ID de la reserva en la base de datos
            frecuencia_alerta (str): Frecuencia de recordatorios (default: "Cada 24 horas")
            
        Returns:
            Capsula_De_Cita: Objeto con los datos de la cita, o None si hay error
        """
        from bd import obtener_conexion
        
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener datos completos de la reserva
                sql = """
                    SELECT 
                        CONCAT(emp.nombres, ' ', emp.apellidos) as nombre_medico,
                        COALESCE(esp.nombre, 'General') as especialidad,
                        p.fecha,
                        p.hora_inicio
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                    LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                    WHERE r.id_reserva = %s
                """
                cursor.execute(sql, (id_reserva,))
                reserva = cursor.fetchone()
                
                if not reserva:
                    return None
                
                # Construir datetime si tenemos fecha y hora
                fecha_hora = None
                if reserva['fecha'] and reserva['hora_inicio']:
                    fecha_base = reserva['fecha']
                    hora = reserva['hora_inicio']
                    
                    # Convertir a datetime si es necesario
                    if isinstance(fecha_base, str):
                        try:
                            fecha_base = datetime.strptime(fecha_base, '%Y-%m-%d').date()
                        except:
                            pass
                    
                    if isinstance(hora, str):
                        try:
                            hora = datetime.strptime(hora, '%H:%M:%S').time()
                        except:
                            try:
                                hora = datetime.strptime(hora, '%H:%M').time()
                            except:
                                pass
                    
                    if isinstance(fecha_base, datetime):
                        fecha_base = fecha_base.date()
                    
                    if isinstance(hora, datetime):
                        hora = hora.time()
                    
                    if fecha_base and hora:
                        try:
                            fecha_hora = datetime.combine(fecha_base, hora)
                        except Exception as e:
                            print(f"⚠️ Error combinando fecha y hora: {e}")
                            fecha_hora = None
                
                # Crear la cápsula
                capsula = Capsula_De_Cita(
                    doctor=reserva['nombre_medico'] or 'Por asignar',
                    especialidad=reserva['especialidad'],
                    fecha=fecha_hora or f"{reserva['fecha']} {reserva['hora_inicio']}",
                    frecuencia_alerta=frecuencia_alerta
                )
                
                return capsula
                
        except Exception as e:
            print(f"❌ Error creando cápsula desde reserva: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            conexion.close()
    
    @staticmethod
    def enviar_notificacion_desde_reserva(id_reserva, frecuencia_alerta="Cada 24 horas"):
        """
        Función helper para enviar notificación usando Custodio_De_Agenda desde una reserva.
        Integra con el sistema existente de reservas.
        
        Args:
            id_reserva (int): ID de la reserva en la base de datos
            frecuencia_alerta (str): Frecuencia de recordatorios (default: "Cada 24 horas")
            
        Returns:
            dict: Resultado del envío {'success': True/False, 'message': str}
        """
        from bd import obtener_conexion
        
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener datos del paciente y la reserva
                sql = """
                    SELECT 
                        p.id_paciente,
                        CONCAT(pac.nombres, ' ', pac.apellidos) as nombre_paciente,
                        u.correo as email_paciente,
                        CONCAT(emp.nombres, ' ', emp.apellidos) as nombre_medico,
                        COALESCE(esp.nombre, 'General') as especialidad,
                        prog.fecha,
                        prog.hora_inicio
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                    INNER JOIN USUARIO u ON pac.id_usuario = u.id_usuario
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                    WHERE r.id_reserva = %s
                """
                cursor.execute(sql, (id_reserva,))
                datos = cursor.fetchone()
                
                if not datos:
                    return {
                        'success': False,
                        'message': 'Reserva no encontrada'
                    }
                
                if not datos.get('email_paciente'):
                    return {
                        'success': False,
                        'message': 'Email del paciente no disponible'
                    }
                
                # Construir datetime
                fecha_hora = None
                if datos['fecha'] and datos['hora_inicio']:
                    fecha_base = datos['fecha']
                    hora = datos['hora_inicio']
                    
                    # Convertir a datetime si es necesario
                    if isinstance(fecha_base, str):
                        try:
                            fecha_base = datetime.strptime(fecha_base, '%Y-%m-%d').date()
                        except:
                            pass
                    
                    if isinstance(hora, str):
                        try:
                            hora = datetime.strptime(hora, '%H:%M:%S').time()
                        except:
                            try:
                                hora = datetime.strptime(hora, '%H:%M').time()
                            except:
                                pass
                    
                    if isinstance(fecha_base, datetime):
                        fecha_base = fecha_base.date()
                    
                    if isinstance(hora, datetime):
                        hora = hora.time()
                    
                    if fecha_base and hora:
                        try:
                            fecha_hora = datetime.combine(fecha_base, hora)
                        except Exception as e:
                            print(f"⚠️ Error combinando fecha y hora: {e}")
                            fecha_hora = None
                
                # Crear cápsula de cita
                capsula = Capsula_De_Cita(
                    doctor=datos['nombre_medico'] or 'Por asignar',
                    especialidad=datos['especialidad'],
                    fecha=fecha_hora or f"{datos['fecha']} {datos['hora_inicio']}",
                    frecuencia_alerta=frecuencia_alerta
                )
                
                # Enviar notificación
                resultado = Custodio_De_Agenda.enviar_notificacion_cita(
                    paciente_email=datos['email_paciente'],
                    paciente_nombre=datos['nombre_paciente'],
                    capsula_cita=capsula
                )
                
                return resultado
                
        except Exception as e:
            print(f"❌ Error enviando notificación desde reserva: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
        finally:
            conexion.close()

