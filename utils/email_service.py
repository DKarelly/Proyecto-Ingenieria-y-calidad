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
            return {
                'success': False,
                'message': 'Credenciales de email no configuradas'
            }
        
        try:
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
            
            # Enviar el correo
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'message': f'Email enviado exitosamente a {destinatario_email}'
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Error de autenticación. Verifica las credenciales de email.'
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'message': f'Error SMTP: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al enviar email: {str(e)}'
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
                                <a href="#" style="display: inline-block; background: linear-gradient(135deg, {color} 0%, {color}dd 100%); color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 8px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.2s;">
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
