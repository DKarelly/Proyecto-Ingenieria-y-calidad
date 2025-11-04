"""
Script de prueba para verificar la configuración de correo electrónico
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_smtp_connection():
    """Prueba la conexión SMTP con Gmail"""
    
    print("=" * 60)
    print("PRUEBA DE CONFIGURACIÓN DE EMAIL")
    print("=" * 60)
    
    # Obtener configuración
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SMTP_EMAIL')
    sender_password = os.getenv('SMTP_PASSWORD')
    
    print(f"\nConfiguración:")
    print(f"  Servidor SMTP: {smtp_server}")
    print(f"  Puerto: {smtp_port}")
    print(f"  Email: {sender_email}")
    print(f"  Contraseña: {'*' * len(sender_password) if sender_password else 'NO CONFIGURADA'}")
    
    if not sender_email or not sender_password:
        print("\n❌ ERROR: Credenciales no configuradas en el archivo .env")
        print("\nPor favor, configura las variables en el archivo .env:")
        print("  SMTP_EMAIL=clinicaunion.cix.1@gmail.com")
        print("  SMTP_PASSWORD=tu_contraseña_de_aplicacion")
        return False
    
    try:
        print("\n🔄 Conectando al servidor SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        
        print("🔄 Iniciando TLS...")
        server.starttls()
        
        print("🔄 Autenticando...")
        server.login(sender_email, sender_password)
        
        print("\n✅ ¡Conexión exitosa!")
        
        # Preguntar si desea enviar un correo de prueba
        enviar_prueba = input("\n¿Deseas enviar un correo de prueba? (s/n): ").lower().strip()
        
        if enviar_prueba == 's':
            email_destino = input("Ingresa el correo destino: ").strip()
            
            if email_destino:
                print(f"\n📧 Enviando correo de prueba a {email_destino}...")
                
                # Crear mensaje
                msg = MIMEMultipart('alternative')
                msg['From'] = f"Clínica Unión <{sender_email}>"
                msg['To'] = email_destino
                msg['Subject'] = "Prueba de Configuración - Clínica Unión"
                
                body_text = """
¡Hola!

Este es un correo de prueba del Sistema de Gestión Médica de Clínica Unión.

Si recibes este mensaje, significa que la configuración de correo está funcionando correctamente.

Atentamente,
Equipo de Clínica Unión
                """
                
                body_html = """
                <html>
                  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                      <div style="text-align: center; margin-bottom: 20px;">
                        <h2 style="color: #0891b2;">✅ Clínica Unión</h2>
                      </div>
                      <h3>¡Configuración Exitosa!</h3>
                      <p>Este es un correo de prueba del Sistema de Gestión Médica de Clínica Unión.</p>
                      <p>Si recibes este mensaje, significa que la configuración de correo está funcionando correctamente. ✨</p>
                      <div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #0891b2; font-weight: bold;">🎉 ¡Todo está listo para enviar códigos de recuperación!</p>
                      </div>
                      <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                      <p style="font-size: 12px; color: #666; text-align: center;">
                        Este es un mensaje de prueba del Sistema de Gestión Médica de Clínica Unión.
                      </p>
                    </div>
                  </body>
                </html>
                """
                
                text_part = MIMEText(body_text, 'plain', 'utf-8')
                html_part = MIMEText(body_html, 'html', 'utf-8')
                
                msg.attach(text_part)
                msg.attach(html_part)
                
                # Enviar
                server.send_message(msg)
                print(f"✅ Correo enviado exitosamente a {email_destino}")
                print("\n📬 Verifica tu bandeja de entrada (y la carpeta de SPAM)")
        
        server.quit()
        print("\n" + "=" * 60)
        print("PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ ERROR DE AUTENTICACIÓN")
        print(f"Detalles: {e}")
        print("\n💡 Soluciones:")
        print("  1. Verifica que la contraseña en .env sea una 'Contraseña de Aplicación'")
        print("  2. Activa la verificación en 2 pasos en Gmail")
        print("  3. Genera una nueva contraseña de aplicación en:")
        print("     https://myaccount.google.com/apppasswords")
        print("\nLee INSTRUCCIONES_GMAIL.md para más detalles")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ ERROR DE CONEXIÓN")
        print(f"Detalles: {e}")
        print("\n💡 Soluciones:")
        print("  1. Verifica tu conexión a internet")
        print("  2. Verifica que el servidor SMTP sea correcto: smtp.gmail.com")
        print("  3. Verifica que el puerto sea 587")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR DESCONOCIDO")
        print(f"Detalles: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_smtp_connection()
