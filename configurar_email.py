"""
Script de configuración interactiva de email
Ayuda a configurar y verificar las credenciales de email
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def leer_env():
    """Lee el archivo .env y retorna un diccionario con las variables"""
    env_path = '.env'
    env_vars = {}
    
    if not os.path.exists(env_path):
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def guardar_env(env_vars):
    """Guarda las variables en el archivo .env"""
    env_path = '.env'
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# ============================================\n")
        f.write("# CONFIGURACIÓN DE EMAIL\n")
        f.write("# ============================================\n\n")
        
        f.write("# Configuración del servidor SMTP\n")
        f.write(f"SMTP_SERVER={env_vars.get('SMTP_SERVER', 'smtp.gmail.com')}\n")
        f.write(f"SMTP_PORT={env_vars.get('SMTP_PORT', '587')}\n\n")
        
        f.write("# Credenciales de email\n")
        f.write(f"SMTP_EMAIL={env_vars.get('SMTP_EMAIL', '')}\n")
        f.write(f"SMTP_PASSWORD={env_vars.get('SMTP_PASSWORD', '')}\n\n")
        
        f.write("# Nombre del remitente que aparecerá en los emails\n")
        f.write(f"SMTP_SENDER_NAME={env_vars.get('SMTP_SENDER_NAME', 'Clínica Unión')}\n")

def configurar_credenciales():
    """Configura las credenciales de email interactivamente"""
    print("\n" + "=" * 70)
    print("CONFIGURACIÓN DE CREDENCIALES DE EMAIL")
    print("=" * 70)
    
    env_vars = leer_env()
    
    print("\n📝 Configuración actual:")
    print(f"   Email: {env_vars.get('SMTP_EMAIL', 'NO CONFIGURADO')}")
    print(f"   Password: {'*' * len(env_vars.get('SMTP_PASSWORD', '')) if env_vars.get('SMTP_PASSWORD') else 'NO CONFIGURADO'}")
    print(f"   Nombre: {env_vars.get('SMTP_SENDER_NAME', 'NO CONFIGURADO')}")
    
    print("\n" + "=" * 70)
    print("⚠️  IMPORTANTE: Necesitas una CONTRASEÑA DE APLICACIÓN de Gmail")
    print("=" * 70)
    print("\n📋 Pasos para obtener una contraseña de aplicación:")
    print("   1. Ve a: https://myaccount.google.com/")
    print("   2. Seguridad → Verificación en dos pasos (actívala si no lo está)")
    print("   3. Seguridad → Contraseñas de aplicaciones")
    print("   4. Selecciona 'Correo' y 'Otro dispositivo'")
    print("   5. Escribe 'Sistema Clínica' como nombre")
    print("   6. Copia la contraseña de 16 caracteres que te genera")
    print("\n⚠️  NO uses tu contraseña normal de Gmail")
    print("=" * 70)
    
    input("\nPresiona ENTER cuando hayas generado tu contraseña de aplicación...")
    
    print("\n📧 Ingresa tus credenciales:\n")
    
    email = input(f"Email [{env_vars.get('SMTP_EMAIL', 'clinicaunion.cix.1@gmail.com')}]: ").strip()
    if not email:
        email = env_vars.get('SMTP_EMAIL', 'clinicaunion.cix.1@gmail.com')
    
    password = input("Contraseña de aplicación (16 caracteres): ").strip()
    if not password:
        password = env_vars.get('SMTP_PASSWORD', '')
    
    nombre = input(f"Nombre del remitente [{env_vars.get('SMTP_SENDER_NAME', 'Clínica Unión')}]: ").strip()
    if not nombre:
        nombre = env_vars.get('SMTP_SENDER_NAME', 'Clínica Unión')
    
    env_vars['SMTP_EMAIL'] = email
    env_vars['SMTP_PASSWORD'] = password
    env_vars['SMTP_SENDER_NAME'] = nombre
    env_vars['SMTP_SERVER'] = env_vars.get('SMTP_SERVER', 'smtp.gmail.com')
    env_vars['SMTP_PORT'] = env_vars.get('SMTP_PORT', '587')
    
    guardar_env(env_vars)
    
    print("\n✅ Credenciales guardadas en .env")
    
    return env_vars

def probar_conexion(env_vars):
    """Prueba la conexión SMTP"""
    print("\n" + "=" * 70)
    print("PROBANDO CONEXIÓN SMTP")
    print("=" * 70)
    
    smtp_server = env_vars.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(env_vars.get('SMTP_PORT', '587'))
    email = env_vars.get('SMTP_EMAIL')
    password = env_vars.get('SMTP_PASSWORD')
    
    if not email or not password:
        print("\n❌ ERROR: Credenciales no configuradas")
        return False
    
    try:
        print(f"\n🔄 Conectando a {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        
        print("🔄 Iniciando TLS...")
        server.starttls()
        
        print("🔄 Autenticando...")
        server.login(email, password)
        
        print("\n✅ ¡Conexión exitosa!")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ ERROR DE AUTENTICACIÓN")
        print("⚠️  La contraseña es incorrecta")
        print("💡 Verifica que estés usando la contraseña de aplicación (no tu contraseña normal)")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def enviar_email_prueba(env_vars):
    """Envía un email de prueba"""
    print("\n" + "=" * 70)
    print("ENVIAR EMAIL DE PRUEBA")
    print("=" * 70)
    
    destinatario = input("\n📧 Ingresa el email donde quieres recibir la prueba: ").strip()
    
    if not destinatario:
        print("❌ Email requerido")
        return False
    
    smtp_server = env_vars.get('SMTP_SERVER')
    smtp_port = int(env_vars.get('SMTP_PORT'))
    sender_email = env_vars.get('SMTP_EMAIL')
    sender_password = env_vars.get('SMTP_PASSWORD')
    sender_name = env_vars.get('SMTP_SENDER_NAME')
    
    try:
        print(f"\n🔄 Enviando email de prueba a {destinatario}...")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = destinatario
        msg['Subject'] = "✅ Prueba de Configuración - Sistema de Notificaciones"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f9fafb; border-radius: 10px; padding: 30px;">
                <h2 style="color: #22C55E;">✅ ¡Configuración Exitosa!</h2>
                <p>Hola,</p>
                <p>Este es un email de prueba del <strong>Sistema de Notificaciones de {sender_name}</strong>.</p>
                <p>Si recibes este mensaje, significa que la configuración de email está funcionando correctamente.</p>
                <div style="background: #dcfce7; border-left: 4px solid #22C55E; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>✓ Conexión SMTP exitosa</strong></p>
                    <p style="margin: 5px 0 0 0;"><strong>✓ Autenticación correcta</strong></p>
                    <p style="margin: 5px 0 0 0;"><strong>✓ Envío de emails funcionando</strong></p>
                </div>
                <p>Ya puedes comenzar a usar el sistema de notificaciones automáticas.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">
                    Email enviado por {sender_name}<br>
                    Sistema de Gestión Médica
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
¡Configuración Exitosa!

Este es un email de prueba del Sistema de Notificaciones de {sender_name}.

Si recibes este mensaje, significa que la configuración de email está funcionando correctamente.

✓ Conexión SMTP exitosa
✓ Autenticación correcta
✓ Envío de emails funcionando

Ya puedes comenzar a usar el sistema de notificaciones automáticas.

---
Email enviado por {sender_name}
Sistema de Gestión Médica
        """
        
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print("\n" + "=" * 70)
        print("✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
        print("=" * 70)
        print(f"\n📬 Revisa tu bandeja de entrada: {destinatario}")
        print("⏱️  Puede tardar unos segundos en llegar")
        print("📂 Si no lo ves, revisa la carpeta de SPAM")
        print("\n💡 Si está en spam, márcalo como 'No es spam' para futuros emails")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR al enviar email: {str(e)}")
        return False

def main():
    print("\n" + "=" * 70)
    print("🏥 CONFIGURADOR DE EMAIL - SISTEMA DE NOTIFICACIONES")
    print("=" * 70)
    
    # Leer configuración actual
    env_vars = leer_env()
    
    tiene_credenciales = env_vars.get('SMTP_EMAIL') and env_vars.get('SMTP_PASSWORD')
    
    if not tiene_credenciales:
        print("\n⚠️  No hay credenciales configuradas")
        print("📝 Vamos a configurarlas ahora...\n")
        env_vars = configurar_credenciales()
    else:
        print("\n✓ Credenciales encontradas")
        print(f"  Email: {env_vars.get('SMTP_EMAIL')}")
        
        reconfigurar = input("\n¿Deseas reconfigurar las credenciales? (s/n): ").lower().strip()
        if reconfigurar == 's':
            env_vars = configurar_credenciales()
    
    # Probar conexión
    print("\n¿Deseas probar la conexión SMTP? (s/n): ", end='')
    if input().lower().strip() == 's':
        if not probar_conexion(env_vars):
            print("\n⚠️  Hay problemas con las credenciales")
            reconfigurar = input("¿Deseas reconfigurar? (s/n): ").lower().strip()
            if reconfigurar == 's':
                env_vars = configurar_credenciales()
                probar_conexion(env_vars)
    
    # Enviar email de prueba
    print("\n¿Deseas enviar un email de prueba? (s/n): ", end='')
    if input().lower().strip() == 's':
        enviar_email_prueba(env_vars)
    
    print("\n" + "=" * 70)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 70)
    print("\n📝 Archivo .env actualizado con las credenciales")
    print("🚀 El sistema ya puede enviar notificaciones por email automáticamente")
    print("\n💡 Cada vez que crees una notificación, se enviará un email al paciente")
    print("=" * 70)

if __name__ == "__main__":
    main()
