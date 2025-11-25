"""
Servicio de envío de correos electrónicos
Maneja el envío de notificaciones por email a los usuarios del sistema
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime
import threading
import socket

# Import condicional de Flask para evitar errores si se usa fuera de contexto
try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    current_app = None

# Cargar variables de entorno
load_dotenv()

class EmailService:
    """Servicio para enviar correos electrónicos"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SMTP_EMAIL')
        self.sender_password = os.getenv('SMTP_PASSWORD')
        self.sender_name = os.getenv('SMTP_SENDER_NAME', 'Clínica Unión')
        # URL del frontend para enlaces en emails
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5000')
        # Asegurar que la URL no termine con /
        if self.frontend_url.endswith('/'):
            self.frontend_url = self.frontend_url.rstrip('/')
        
        # Log de configuración (sin mostrar contraseña)
        if self.sender_email and self.sender_password:
            print(f"📧✅ EmailService inicializado: {self.sender_email} en {self.smtp_server}:{self.smtp_port}")
            print(f"📧✅ Frontend URL configurada: {self.frontend_url}")
        else:
            print(f"⚠️ EmailService: Credenciales SMTP no configuradas (SMTP_EMAIL o SMTP_PASSWORD faltantes)")
    
    def enviar_notificacion_email(self, destinatario_email, destinatario_nombre, titulo, mensaje, tipo='informacion'):
        """
        Envía una notificación por correo electrónico
        
        Args:
            destinatario_email (str): Email del destinatario
            destinatario_nombre (str): Nombre del destinatario
            titulo (str): Título de la notificación
            mensaje (str): Mensaje de la notificación
            tipo (str): Tipo de notificación (recordatorio, confirmacion, estado, cancelacion, informacion)
        
        Returns:
            dict: Resultado del envío {'success': True/False, 'message': str}
        """
        
        # Verificar que las credenciales estén configuradas
        if not self.sender_email or not self.sender_password:
            error_msg = 'Credenciales de email no configuradas. Verifica SMTP_EMAIL y SMTP_PASSWORD en .env'
            print(f"📧❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
        
        # Verificar que el email del destinatario sea válido
        if not destinatario_email or not destinatario_email.strip():
            error_msg = f'Email del destinatario inválido: {destinatario_email}'
            print(f"📧❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
        
        # Llamar al método interno de envío
        return self._enviar_email_sync(destinatario_email, destinatario_nombre, titulo, mensaje, tipo)
    
    def _enviar_email_sync(self, destinatario_email, destinatario_nombre, titulo, mensaje, tipo):
        """
        Método interno para enviar email de forma síncrona
        """
        try:
            print(f"📧 Enviando email a {destinatario_email}...")
            # Crear el mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = destinatario_email
            msg['Subject'] = f"{self._get_emoji_tipo(tipo)} {titulo}"
            
            # Generar contenido HTML
            html_content = self._generar_html_notificacion(
                destinatario_nombre,
                titulo,
                mensaje,
                tipo
            )
            
            # Generar contenido de texto plano como respaldo
            text_content = f"""
Hola {destinatario_nombre},

{titulo}

{mensaje}

---
Este es un mensaje automático del Sistema de Gestión Médica de {self.sender_name}.
Por favor, no responda a este correo.

Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """
            
            # Adjuntar ambos tipos de contenido
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar el correo con timeout reducido y reintentos
            print(f"📧 Conectando a {self.smtp_server}:{self.smtp_port}...")
            # Timeout reducido a 10 segundos para evitar que bloquee el worker
            max_intentos = 3
            intento = 0
            ultimo_error = None
            
            while intento < max_intentos:
                try:
                    with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                        print(f"📧 Iniciando TLS...")
                        server.starttls()
                        print(f"📧 Autenticando con {self.sender_email}...")
                        server.login(self.sender_email, self.sender_password)
                        print(f"📧 Enviando mensaje a {destinatario_email}...")
                        server.send_message(msg)
                        print(f"📧✅ Email enviado exitosamente a {destinatario_email}")
                        break  # Éxito, salir del bucle
                except (smtplib.SMTPConnectError, ConnectionError, OSError, socket.timeout, socket.gaierror) as e:
                    intento += 1
                    ultimo_error = e
                    if intento < max_intentos:
                        print(f"📧⚠️ Intento {intento}/{max_intentos} falló. Reintentando en 2 segundos...")
                        import time
                        time.sleep(2)
                    else:
                        # Último intento falló, lanzar excepción
                        raise
            
            return {
                'success': True,
                'message': f'Email enviado exitosamente a {destinatario_email}'
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f'Error de autenticación SMTP. Verifica las credenciales de email. Detalle: {str(e)}'
            print(f"📧❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
        except (smtplib.SMTPConnectError, ConnectionError, OSError, TimeoutError, socket.timeout, socket.gaierror) as e:
            error_msg = f'Error conectando al servidor SMTP {self.smtp_server}:{self.smtp_port}. Detalle: {str(e)}'
            print(f"📧❌ {error_msg}")
            
            # Mensaje adicional para errores de red en Render
            if '101' in str(e) or 'inalcanzable' in str(e).lower() or 'unreachable' in str(e).lower():
                print("⚠️ NOTA: Este error puede deberse a restricciones de red en Render.")
                print("💡 Soluciones posibles:")
                print("   1. Verificar que Render permita conexiones salientes al puerto 587")
                print("   2. Considerar usar un servicio de email alternativo (SendGrid, Mailgun, AWS SES)")
                print("   3. Verificar configuración de firewall de Gmail")
            
            # No es crítico - el sistema puede funcionar sin email
            return {
                'success': False,
                'message': error_msg
            }
        except smtplib.SMTPException as e:
            error_msg = f'Error SMTP: {str(e)}'
            print(f"📧❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': error_msg
            }
        except Exception as e:
            # Capturar cualquier otro error (incluyendo timeouts del sistema)
            error_msg = f'Error inesperado al enviar email: {str(e)}'
            print(f"📧❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': error_msg
            }
    
    def _get_emoji_tipo(self, tipo):
        """Retorna un emoji según el tipo de notificación"""
        emojis = {
            'recordatorio': '🔔',
            'confirmacion': '✅',
            'estado': '📋',
            'cancelacion': '❌',
            'informacion': 'ℹ️'
        }
        return emojis.get(tipo, 'ℹ️')
    
    def _get_color_tipo(self, tipo):
        """Retorna un color según el tipo de notificación"""
        colores = {
            'recordatorio': '#FFA500',  # Naranja
            'confirmacion': '#22C55E',  # Verde
            'estado': '#3B82F6',        # Azul
            'cancelacion': '#EF4444',   # Rojo
            'informacion': '#6366F1'    # Índigo
        }
        return colores.get(tipo, '#6366F1')
    
    def _generar_html_notificacion(self, nombre, titulo, mensaje, tipo):
        """Genera el contenido HTML para la notificación"""
        color = self._get_color_tipo(tipo)
        emoji = self._get_emoji_tipo(tipo)
        fecha_actual = datetime.now().strftime('%d de %B de %Y a las %H:%M')
        
        # Generar URL del login con parámetro para mostrar el modal
        login_url = f"{self.frontend_url}/?show_login=true"
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f5f5;">
        <tr>
            <td style="padding: 40px 20px;">
                <!-- Container principal -->
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    
                    <!-- Header con color según tipo -->
                    <tr>
                        <td style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                {emoji} {self.sender_name}
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Contenido principal -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <!-- Saludo -->
                            <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 1.6;">
                                Hola <strong>{nombre}</strong>,
                            </p>
                            
                            <!-- Título de la notificación -->
                            <div style="background-color: #f9fafb; border-left: 4px solid {color}; padding: 20px; margin: 20px 0; border-radius: 4px;">
                                <h2 style="margin: 0 0 10px 0; color: #111827; font-size: 20px; font-weight: 600;">
                                    {titulo}
                                </h2>
                                <p style="margin: 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
                                    {mensaje}
                                </p>
                            </div>
                            
                            <!-- Nota informativa -->
                            <div style="background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 6px; padding: 15px; margin: 25px 0;">
                                <p style="margin: 0; color: #1e40af; font-size: 14px; line-height: 1.5;">
                                    <strong>💡 Nota:</strong> Para más detalles sobre sus reservas y notificaciones, 
                                    ingrese a su cuenta en nuestro sistema.
                                </p>
                            </div>
                            
                            <!-- CTA Button -->
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{login_url}" style="display: inline-block; background: linear-gradient(135deg, {color} 0%, {color}dd 100%); color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 8px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.2s;">
                                    Ver en el Sistema
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 13px; line-height: 1.5; text-align: center;">
                                Este es un mensaje automático del Sistema de Gestión Médica de <strong>{self.sender_name}</strong>.<br>
                                Por favor, no responda a este correo.
                            </p>
                            <p style="margin: 10px 0 0 0; color: #9ca3af; font-size: 12px; text-align: center;">
                                Enviado el {fecha_actual}
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
                <!-- Footer adicional fuera del contenedor -->
                <table role="presentation" style="max-width: 600px; margin: 20px auto 0;">
                    <tr>
                        <td style="text-align: center; padding: 0 20px;">
                            <p style="margin: 0; color: #9ca3af; font-size: 12px; line-height: 1.5;">
                                © {datetime.now().year} {self.sender_name}. Todos los derechos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
        """
        return html

# Instancia global del servicio
email_service = EmailService()


# ============================================
# PROTOCOLO DE ENVÍO ASÍNCRONO (NO BLOQUEANTE)
# ============================================
# Solución para evitar que Gunicorn mate el worker por timeout
# cuando se intenta enviar emails de forma síncrona

def lanzar_mensajero_fantasma(app_context, funcion_envio, **datos_mision):
    """
    Ejecuta el envío de correo en un plano existencial separado (otro hilo),
    permitiendo que el hilo principal responda al usuario de inmediato.
    
    Args:
        app_context: Contexto de Flask necesario para acceder a configuración
        funcion_envio: Función que envía el email (email_service.enviar_notificacion_email)
        **datos_mision: Datos para el envío (destinatario_email, destinatario_nombre, titulo, mensaje, tipo)
    """
    # Necesitamos empujar el contexto de Flask manualmente porque el nuevo hilo
    # nace "desnudo" y no conoce la configuración de tu app.
    with app_context:
        try:
            destinatario = datos_mision.get('destinatario_email', 'desconocido')
            print(f"👻 [Fantasma] Iniciando transmisión a {destinatario}...")
            
            # Ejecutar el envío real
            resultado = funcion_envio(**datos_mision)
            
            if resultado.get('success'):
                print(f"👻 [Fantasma] Misión cumplida. El correo ha partido hacia {destinatario}.")
            else:
                print(f"💀 [Fantasma] Fallo en la misión hacia {destinatario}: {resultado.get('message', 'Error desconocido')}")
                
        except Exception as e:
            print(f"💀 [Fantasma] Error crítico en la misión: {e}")
            import traceback
            traceback.print_exc()


def invocar_protocolo_envio_rapido(email_service_instance, destinatario_email, destinatario_nombre, titulo, mensaje, tipo='informacion'):
    """
    Esta es la función que llamarás desde tu ruta/controlador en lugar de la llamada directa.
    Envía el email en un hilo separado para no bloquear la respuesta HTTP.
    
    Args:
        email_service_instance: Instancia de EmailService (usar email_service)
        destinatario_email: Email del destinatario
        destinatario_nombre: Nombre del destinatario
        titulo: Título del mensaje
        mensaje: Contenido del mensaje
        tipo: Tipo de notificación (confirmacion, recordatorio, etc.)
    
    Returns:
        bool: True si el hilo fue lanzado exitosamente (el email se enviará en segundo plano)
    """
    try:
        # Capturamos el 'alma' de la aplicación actual (su contexto/configuración)
        # Si no hay contexto de Flask (ej: fuera de una request), usar None
        alma_app = None
        
        if FLASK_AVAILABLE:
            try:
                # Intentar obtener el contexto actual de Flask
                alma_app = current_app.app_context()
            except RuntimeError:
                # Si no hay contexto de Flask activo, intentar obtenerlo desde el módulo app
                try:
                    import app
                    if hasattr(app, 'app'):
                        alma_app = app.app.app_context()
                    else:
                        print("⚠️ [Fantasma] No se encontró la instancia de Flask en app.app")
                except Exception as e:
                    print(f"⚠️ [Fantasma] No se pudo obtener contexto de Flask: {e}")
                    alma_app = None
        else:
            print("⚠️ [Fantasma] Flask no está disponible. El email se enviará sin contexto.")
        
        # Preparamos los datos de la misión
        paquete_secreto = {
            'destinatario_email': destinatario_email,
            'destinatario_nombre': destinatario_nombre,
            'titulo': titulo,
            'mensaje': mensaje,
            'tipo': tipo
        }
        
        # Si no hay contexto, intentar enviar de forma síncrona como fallback
        if alma_app is None:
            print("⚠️ [Fantasma] Sin contexto de Flask, enviando de forma síncrona como fallback")
            resultado = email_service_instance.enviar_notificacion_email(**paquete_secreto)
            return resultado.get('success', False)
        
        # Creamos el hilo (el agente sombra)
        agente_sombra = threading.Thread(
            target=lanzar_mensajero_fantasma,
            args=(alma_app, email_service_instance.enviar_notificacion_email),
            kwargs=paquete_secreto,
            daemon=True  # El hilo morirá cuando termine la aplicación principal
        )
        
        # .start() dispara el hilo y deja que el código principal continúe INMEDIATAMENTE
        agente_sombra.start()
        
        print(f"🚀 [Fantasma] Agente sombra despachado para {destinatario_email}. El usuario recibirá respuesta inmediata.")
        return True
        
    except Exception as e:
        print(f"❌ [Fantasma] Error al lanzar agente sombra: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: intentar envío síncrono
        try:
            resultado = email_service_instance.enviar_notificacion_email(
                destinatario_email=destinatario_email,
                destinatario_nombre=destinatario_nombre,
                titulo=titulo,
                mensaje=mensaje,
                tipo=tipo
            )
            return resultado.get('success', False)
        except:
            return False


def enviar_email_reserva_creada(paciente_email, paciente_nombre, fecha, hora_inicio, hora_fin, 
                                medico_nombre, especialidad, servicio, id_reserva):
    """Envía email al paciente cuando se crea una reserva"""
    titulo = "Reserva Médica Confirmada"
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        Su reserva ha sido registrada exitosamente en nuestro sistema.
    </p>
    
    <div style="text-align: center; margin: 25px 0;">
        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; font-weight: 600;">Código de Reserva</p>
        <div style="display: inline-block; background-color: #f0f9ff; border: 3px solid #0891b2; border-radius: 12px; padding: 20px 40px;">
            <span style="font-size: 36px; font-weight: bold; letter-spacing: 3px; color: #0891b2;">#{id_reserva}</span>
        </div>
    </div>
    
    <div style="background-color: #ffffff; border: 2px solid #0891b2; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #0891b2; font-size: 18px;">📋 Detalles de su Reserva</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>👨‍⚕️ Médico:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{medico_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>🏥 Especialidad:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{especialidad}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
            <strong>⚠️ Aviso de Seguimiento:</strong> Para asegurar su asistencia, este sistema automático le enviará recordatorios <strong>cada 24 horas</strong> hasta el momento de su cita. El próximo recordatorio será <strong>2 horas antes</strong> de su cita programada.
        </p>
    </div>
    
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
            <strong>⚠️ Importante:</strong> Por favor, llegue 15 minutos antes de su cita. 
            Si necesita cancelar o reprogramar, hágalo con al menos 24 horas de anticipación.
        </p>
    </div>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        paciente_email, paciente_nombre, titulo, mensaje, tipo='confirmacion'
    )


def enviar_email_reserva_creada_medico(medico_email, medico_nombre, paciente_nombre, 
                                       fecha, hora_inicio, hora_fin, servicio, id_reserva):
    """Envía email al médico cuando se crea una reserva"""
    titulo = "Nueva Reserva Asignada"
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        Se ha registrado una nueva reserva médica en su agenda.
    </p>
    
    <div style="text-align: center; margin: 25px 0;">
        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; font-weight: 600;">Código de Reserva</p>
        <div style="display: inline-block; background-color: #f0f9ff; border: 3px solid #0891b2; border-radius: 12px; padding: 20px 40px;">
            <span style="font-size: 36px; font-weight: bold; letter-spacing: 3px; color: #0891b2;">#{id_reserva}</span>
        </div>
    </div>
    
    <div style="background-color: #ffffff; border: 2px solid #0891b2; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #0891b2; font-size: 18px;">📋 Detalles de la Reserva</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>👤 Paciente:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{paciente_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
    </div>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        medico_email, medico_nombre, titulo, mensaje, tipo='informacion'
    )


def enviar_email_cambio_estado_reserva(paciente_email, paciente_nombre, medico_email, medico_nombre,
                                       id_reserva, estado_anterior, estado_nuevo, fecha, hora_inicio, hora_fin,
                                       servicio, motivo=None):
    """
    Envía emails tanto al paciente como al médico cuando cambia el estado de una reserva
    """
    resultados = {'paciente': None, 'medico': None}
    
    # Determinar colores y mensajes según el estado
    estados_info = {
        'Confirmada': {
            'color': '#22c55e',
            'icono': '✅',
            'titulo_paciente': 'Reserva Confirmada',
            'titulo_medico': 'Reserva Confirmada',
            'mensaje_paciente': 'Su reserva ha sido confirmada exitosamente.',
            'mensaje_medico': 'La reserva ha sido confirmada.'
        },
        'Cancelada': {
            'color': '#ef4444',
            'icono': '❌',
            'titulo_paciente': 'Reserva Cancelada',
            'titulo_medico': 'Reserva Cancelada',
            'mensaje_paciente': 'Su reserva ha sido cancelada.',
            'mensaje_medico': 'Una reserva ha sido cancelada.'
        },
        'Completada': {
            'color': '#3b82f6',
            'icono': '✓',
            'titulo_paciente': 'Reserva Completada',
            'titulo_medico': 'Reserva Completada',
            'mensaje_paciente': 'Su cita médica ha sido completada.',
            'mensaje_medico': 'La cita médica ha sido completada.'
        },
        'Inasistida': {
            'color': '#f59e0b',
            'icono': '⚠️',
            'titulo_paciente': 'Reserva Marcada como Inasistida',
            'titulo_medico': 'Reserva Marcada como Inasistida',
            'mensaje_paciente': 'Su reserva ha sido marcada como inasistida.',
            'mensaje_medico': 'Una reserva ha sido marcada como inasistida.'
        },
        'Pendiente': {
            'color': '#6366f1',
            'icono': '⏳',
            'titulo_paciente': 'Reserva Pendiente',
            'titulo_medico': 'Reserva Pendiente',
            'mensaje_paciente': 'Su reserva está pendiente de confirmación.',
            'mensaje_medico': 'Una reserva está pendiente de confirmación.'
        }
    }
    
    info = estados_info.get(estado_nuevo, {
        'color': '#0891b2',
        'icono': 'ℹ️',
        'titulo_paciente': f'Estado de Reserva Actualizado',
        'titulo_medico': f'Estado de Reserva Actualizado',
        'mensaje_paciente': f'El estado de su reserva ha cambiado a: {estado_nuevo}',
        'mensaje_medico': f'El estado de la reserva ha cambiado a: {estado_nuevo}'
    })
    
    # Email al paciente
    if paciente_email:
        mensaje_paciente = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        {info['mensaje_paciente']}
    </p>
    
    <div style="text-align: center; margin: 25px 0;">
        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; font-weight: 600;">Código de Reserva</p>
        <div style="display: inline-block; background-color: #f0f9ff; border: 3px solid {info['color']}; border-radius: 12px; padding: 20px 40px;">
            <span style="font-size: 36px; font-weight: bold; letter-spacing: 3px; color: {info['color']};">#{id_reserva}</span>
        </div>
    </div>
    
    <div style="background-color: #ffffff; border: 2px solid {info['color']}; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: {info['color']}; font-size: 18px;">{info['icono']} Detalles de la Reserva</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>Estado:</strong></td>
                <td style="padding: 8px 0; color: {info['color']}; font-size: 14px; font-weight: 600;">{estado_nuevo}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
    </div>
"""
        if motivo:
            mensaje_paciente += f"""
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
            <strong>📝 Motivo:</strong> {motivo}
        </p>
    </div>
"""
        mensaje_paciente += "</div>"
        
        resultados['paciente'] = email_service.enviar_notificacion_email(
            paciente_email, paciente_nombre, info['titulo_paciente'], mensaje_paciente, tipo='estado'
        )
    
    # Email al médico
    if medico_email and medico_nombre:
        mensaje_medico = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        {info['mensaje_medico']}
    </p>
    
    <div style="text-align: center; margin: 25px 0;">
        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; font-weight: 600;">Código de Reserva</p>
        <div style="display: inline-block; background-color: #f0f9ff; border: 3px solid {info['color']}; border-radius: 12px; padding: 20px 40px;">
            <span style="font-size: 36px; font-weight: bold; letter-spacing: 3px; color: {info['color']};">#{id_reserva}</span>
        </div>
    </div>
    
    <div style="background-color: #ffffff; border: 2px solid {info['color']}; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: {info['color']}; font-size: 18px;">{info['icono']} Detalles de la Reserva</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>Estado:</strong></td>
                <td style="padding: 8px 0; color: {info['color']}; font-size: 14px; font-weight: 600;">{estado_nuevo}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>👤 Paciente:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{paciente_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
    </div>
"""
        if motivo:
            mensaje_medico += f"""
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
            <strong>📝 Motivo:</strong> {motivo}
        </p>
    </div>
"""
        mensaje_medico += "</div>"
        
        resultados['medico'] = email_service.enviar_notificacion_email(
            medico_email, medico_nombre, info['titulo_medico'], mensaje_medico, tipo='informacion'
        )
    
    return resultados


def enviar_email_cancelacion_aprobada(paciente_email, paciente_nombre, fecha, hora_inicio, hora_fin,
                                      medico_nombre, especialidad, servicio, motivo_cancelacion, 
                                      comentario_admin=None):
    """Envía email al paciente cuando se aprueba su solicitud de cancelación"""
    titulo = "Cancelación de Reserva Aprobada"
    
    comentario_html = ""
    if comentario_admin:
        comentario_html = f"""
        <div style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 4px;">
            <p style="margin: 0; color: #1e40af; font-size: 14px;">
                <strong>💬 Comentario del personal:</strong><br>
                {comentario_admin}
            </p>
        </div>
        """
    
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        Su solicitud de cancelación ha sido <strong style="color: #22c55e;">aprobada</strong>.
    </p>
    
    <div style="background-color: #fee2e2; border: 2px solid #ef4444; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #dc2626; font-size: 18px;">❌ Reserva Cancelada</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>👨‍⚕️ Médico:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{medico_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>🏥 Especialidad:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{especialidad}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
        
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #fecaca;">
            <p style="margin: 0; color: #991b1b; font-size: 13px;">
                <strong>Motivo de cancelación:</strong> {motivo_cancelacion}
            </p>
        </div>
    </div>
    
    {comentario_html}
    
    <p style="margin: 20px 0 0 0; color: #374151; font-size: 14px;">
        Puede realizar una nueva reserva en cualquier momento a través de nuestro sistema.
    </p>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        paciente_email, paciente_nombre, titulo, mensaje, tipo='cancelacion'
    )


def enviar_email_cancelacion_medico(medico_email, medico_nombre, paciente_nombre, fecha, 
                                    hora_inicio, hora_fin, servicio, motivo_cancelacion):
    """Envía email al médico cuando se cancela una cita"""
    titulo = "Cita Médica Cancelada"
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        Una cita médica asignada a usted ha sido <strong style="color: #ef4444;">cancelada</strong>.
    </p>
    
    <div style="background-color: #fee2e2; border: 2px solid #ef4444; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #dc2626; font-size: 18px;">❌ Cita Cancelada</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>👤 Paciente:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{paciente_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
        
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #fecaca;">
            <p style="margin: 0; color: #991b1b; font-size: 13px;">
                <strong>Motivo:</strong> {motivo_cancelacion}
            </p>
        </div>
    </div>
    
    <p style="margin: 20px 0 0 0; color: #374151; font-size: 14px;">
        Este espacio en su agenda ahora está disponible para nuevas reservas.
    </p>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        medico_email, medico_nombre, titulo, mensaje, tipo='cancelacion'
    )


def enviar_email_reprogramacion_aprobada(paciente_email, paciente_nombre, 
                                        fecha_anterior, hora_inicio_anterior, hora_fin_anterior,
                                        fecha_nueva, hora_inicio_nueva, hora_fin_nueva,
                                        medico_nombre, especialidad, servicio, 
                                        motivo_reprogramacion, comentario_admin=None):
    """Envía email al paciente cuando se aprueba su solicitud de reprogramación"""
    titulo = "Reprogramación de Reserva Aprobada"
    
    comentario_html = ""
    if comentario_admin:
        comentario_html = f"""
        <div style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 4px;">
            <p style="margin: 0; color: #1e40af; font-size: 14px;">
                <strong>💬 Comentario del personal:</strong><br>
                {comentario_admin}
            </p>
        </div>
        """
    
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        Su solicitud de reprogramación ha sido <strong style="color: #22c55e;">aprobada</strong>.
    </p>
    
    <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; margin: 20px 0; align-items: center;">
        <!-- Fecha Anterior -->
        <div style="background-color: #fee2e2; border: 2px solid #ef4444; border-radius: 8px; padding: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #dc2626; font-size: 14px; text-align: center;">❌ Fecha Anterior</h4>
            <p style="margin: 5px 0; color: #111827; font-size: 13px; text-align: center;">
                <strong>📅</strong> {fecha_anterior}<br>
                <strong>⏰</strong> {hora_inicio_anterior} - {hora_fin_anterior}
            </p>
        </div>
        
        <!-- Flecha -->
        <div style="text-align: center; font-size: 24px; color: #0891b2;">
            ➡️
        </div>
        
        <!-- Fecha Nueva -->
        <div style="background-color: #d1fae5; border: 2px solid #22c55e; border-radius: 8px; padding: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #16a34a; font-size: 14px; text-align: center;">✅ Nueva Fecha</h4>
            <p style="margin: 5px 0; color: #111827; font-size: 13px; text-align: center;">
                <strong>📅</strong> {fecha_nueva}<br>
                <strong>⏰</strong> {hora_inicio_nueva} - {hora_fin_nueva}
            </p>
        </div>
    </div>
    
    <div style="background-color: #ffffff; border: 2px solid #0891b2; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #0891b2; font-size: 18px;">📋 Detalles de la Cita</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>👨‍⚕️ Médico:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{medico_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>🏥 Especialidad:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{especialidad}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
        
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0f2fe;">
            <p style="margin: 0; color: #0c4a6e; font-size: 13px;">
                <strong>Motivo de reprogramación:</strong> {motivo_reprogramacion}
            </p>
        </div>
    </div>
    
    {comentario_html}
    
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
            <strong>⚠️ Recuerde:</strong> Por favor, llegue 15 minutos antes de su nueva cita.
        </p>
    </div>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        paciente_email, paciente_nombre, titulo, mensaje, tipo='confirmacion'
    )


def enviar_email_reprogramacion_medico(medico_email, medico_nombre, paciente_nombre,
                                      fecha_anterior, hora_inicio_anterior, hora_fin_anterior,
                                      fecha_nueva, hora_inicio_nueva, hora_fin_nueva,
                                      servicio, motivo_reprogramacion):
    """Envía email al médico cuando se reprograma una cita"""
    titulo = "Cita Médica Reprogramada"
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        Una cita médica asignada a usted ha sido <strong style="color: #0891b2;">reprogramada</strong>.
    </p>
    
    <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; margin: 20px 0; align-items: center;">
        <!-- Fecha Anterior -->
        <div style="background-color: #fee2e2; border: 2px solid #ef4444; border-radius: 8px; padding: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #dc2626; font-size: 14px; text-align: center;">❌ Fecha Anterior</h4>
            <p style="margin: 5px 0; color: #111827; font-size: 13px; text-align: center;">
                <strong>📅</strong> {fecha_anterior}<br>
                <strong>⏰</strong> {hora_inicio_anterior} - {hora_fin_anterior}
            </p>
        </div>
        
        <!-- Flecha -->
        <div style="text-align: center; font-size: 24px; color: #0891b2;">
            ➡️
        </div>
        
        <!-- Fecha Nueva -->
        <div style="background-color: #d1fae5; border: 2px solid #22c55e; border-radius: 8px; padding: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #16a34a; font-size: 14px; text-align: center;">✅ Nueva Fecha</h4>
            <p style="margin: 5px 0; color: #111827; font-size: 13px; text-align: center;">
                <strong>📅</strong> {fecha_nueva}<br>
                <strong>⏰</strong> {hora_inicio_nueva} - {hora_fin_nueva}
            </p>
        </div>
    </div>
    
    <div style="background-color: #ffffff; border: 2px solid #0891b2; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>👤 Paciente:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{paciente_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
        
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0f2fe;">
            <p style="margin: 0; color: #0c4a6e; font-size: 13px;">
                <strong>Motivo:</strong> {motivo_reprogramacion}
            </p>
        </div>
    </div>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        medico_email, medico_nombre, titulo, mensaje, tipo='informacion'
    )


def enviar_email_confirmacion_reserva(paciente_email, paciente_nombre, fecha, hora_inicio, hora_fin,
                                     medico_nombre, especialidad, servicio):
    """Envía email de confirmación cuando el trabajador confirma una reserva"""
    titulo = "Reserva Médica Confirmada"
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
        Su reserva ha sido <strong style="color: #22c55e;">confirmada</strong> por nuestro personal.
    </p>
    
    <div style="background-color: #d1fae5; border: 2px solid #22c55e; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #16a34a; font-size: 18px;">✅ Cita Confirmada</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>👨‍⚕️ Médico:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{medico_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>🏥 Especialidad:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{especialidad}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #1e40af; font-size: 14px; line-height: 1.6;">
            <strong>✨ Su cita está confirmada.</strong> Por favor, llegue 15 minutos antes de la hora programada.
        </p>
    </div>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        paciente_email, paciente_nombre, titulo, mensaje, tipo='confirmacion'
    )


def enviar_email_recordatorio_24h(paciente_email, paciente_nombre, fecha, hora_inicio, hora_fin,
                                  medico_nombre, especialidad, servicio):
    """Envía recordatorio 24 horas antes de la cita"""
    titulo = "Recordatorio: Cita Médica Mañana"
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 16px; color: #374151;">
        Le recordamos que tiene una <strong>cita médica mañana</strong>.
    </p>
    
    <div style="background-color: #fef3c7; border: 2px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #d97706; font-size: 18px;">🔔 Cita Programada para Mañana</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 40%;"><strong>📅 Fecha:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px; font-size: 16px; font-weight: bold;">{hora_inicio} - {hora_fin}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>👨‍⚕️ Médico:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{medico_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>🏥 Especialidad:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{especialidad}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;"><strong>📋 Servicio:</strong></td>
                <td style="padding: 8px 0; color: #111827; font-size: 14px;">{servicio}</td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
            <strong>⚠️ Aviso de Seguimiento:</strong> Para asegurar su asistencia, este sistema automático le enviará recordatorios <strong>cada 24 horas</strong> hasta el momento de su cita. El próximo recordatorio será <strong>2 horas antes</strong> de su cita programada.
        </p>
    </div>
    
    <div style="background-color: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0 0 10px 0; color: #1e40af; font-size: 14px; font-weight: bold;">
            📝 Recomendaciones:
        </p>
        <ul style="margin: 0; padding-left: 20px; color: #1e3a8a; font-size: 13px; line-height: 1.8;">
            <li>Llegue 15 minutos antes de su cita</li>
            <li>Traiga su documento de identidad</li>
            <li>Si tiene exámenes previos, tráigalos</li>
            <li>Si necesita cancelar, hágalo con anticipación</li>
        </ul>
    </div>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        paciente_email, paciente_nombre, titulo, mensaje, tipo='recordatorio'
    )


def enviar_email_recordatorio_2h(paciente_email, paciente_nombre, fecha, hora_inicio, hora_fin,
                                 medico_nombre, especialidad):
    """Envía recordatorio 2 horas antes de la cita"""
    titulo = "Recordatorio: Cita Médica en 2 Horas"
    mensaje = f"""
<div style="margin: 20px 0;">
    <p style="margin: 10px 0; font-size: 17px; color: #dc2626; font-weight: bold;">
        ⏰ Su cita médica es en aproximadamente <span style="color: #ef4444;">2 HORAS</span>
    </p>
    
    <div style="background-color: #fee2e2; border: 3px solid #ef4444; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0 0 15px 0; color: #dc2626; font-size: 20px;">🚨 Cita Próxima</h3>
        
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 10px 0; color: #6b7280; font-size: 15px; width: 35%;"><strong>📅 Hoy:</strong></td>
                <td style="padding: 10px 0; color: #111827; font-size: 15px;">{fecha}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #6b7280; font-size: 15px;"><strong>⏰ Hora:</strong></td>
                <td style="padding: 10px 0; color: #dc2626; font-size: 18px; font-weight: bold;">{hora_inicio}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #6b7280; font-size: 15px;"><strong>👨‍⚕️ Médico:</strong></td>
                <td style="padding: 10px 0; color: #111827; font-size: 15px;">{medico_nombre}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #6b7280; font-size: 15px;"><strong>🏥 Especialidad:</strong></td>
                <td style="padding: 10px 0; color: #111827; font-size: 15px;">{especialidad}</td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #991b1b; font-size: 14px; line-height: 1.6;">
            <strong>🚨 Recordatorio Final:</strong> Este es el último recordatorio antes de su cita. El sistema le ha estado enviando recordatorios <strong>cada 24 horas</strong> y ahora le notifica <strong>2 horas antes</strong> de su cita programada.
        </p>
    </div>
    
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #92400e; font-size: 15px; font-weight: bold;">
            ⚠️ Recuerde llegar 15 minutos antes. ¡Nos vemos pronto!
        </p>
    </div>
</div>
    """
    
    return email_service.enviar_notificacion_email(
        paciente_email, paciente_nombre, titulo, mensaje, tipo='recordatorio'
    )