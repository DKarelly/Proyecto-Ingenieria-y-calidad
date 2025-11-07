"""
Script de prueba para verificar el envío de emails al crear notificaciones
"""
from utils.email_service import email_service
from datetime import datetime

def test_envio_email_notificacion():
    """Prueba el envío de una notificación por email"""
    
    print("=" * 70)
    print("PRUEBA DE ENVÍO DE NOTIFICACIONES POR EMAIL")
    print("=" * 70)
    print()
    
    # Solicitar datos al usuario
    print("Por favor, ingresa los siguientes datos para la prueba:\n")
    
    destinatario_email = input("📧 Email del destinatario: ").strip()
    if not destinatario_email:
        print("❌ Email requerido")
        return
    
    destinatario_nombre = input("👤 Nombre del destinatario: ").strip() or "Usuario"
    
    print("\n📋 Tipos de notificación disponibles:")
    print("  1. Recordatorio")
    print("  2. Confirmación")
    print("  3. Estado")
    print("  4. Cancelación")
    print("  5. Información")
    
    tipo_opcion = input("\nSelecciona el tipo (1-5): ").strip()
    
    tipos = {
        '1': 'recordatorio',
        '2': 'confirmacion',
        '3': 'estado',
        '4': 'cancelacion',
        '5': 'informacion'
    }
    
    tipo = tipos.get(tipo_opcion, 'informacion')
    
    # Mensajes de ejemplo según el tipo
    mensajes_ejemplo = {
        'recordatorio': {
            'titulo': 'Recordatorio de Cita',
            'mensaje': 'Tiene una cita programada para el 15/11/2025 a las 14:00:00'
        },
        'confirmacion': {
            'titulo': 'Reserva Confirmada',
            'mensaje': 'Su reserva ha sido confirmada exitosamente. Le esperamos en la fecha y hora acordada.'
        },
        'estado': {
            'titulo': 'Estado de Reserva',
            'mensaje': 'Su reserva está pendiente de confirmación. Le notificaremos cuando sea procesada.'
        },
        'cancelacion': {
            'titulo': 'Reserva Cancelada',
            'mensaje': 'Su reserva ha sido cancelada. Motivo: Reprogramación solicitada por el paciente.'
        },
        'informacion': {
            'titulo': 'Información Importante',
            'mensaje': 'Le informamos que hay actualizaciones importantes sobre su atención médica.'
        }
    }
    
    mensaje_data = mensajes_ejemplo.get(tipo, mensajes_ejemplo['informacion'])
    
    print(f"\n🔄 Enviando notificación de tipo '{tipo}' a {destinatario_email}...\n")
    
    # Enviar el email
    resultado = email_service.enviar_notificacion_email(
        destinatario_email=destinatario_email,
        destinatario_nombre=destinatario_nombre,
        titulo=mensaje_data['titulo'],
        mensaje=mensaje_data['mensaje'],
        tipo=tipo
    )
    
    print("\n" + "=" * 70)
    if resultado['success']:
        print("✅ ¡Email enviado exitosamente!")
        print(f"📬 Destinatario: {destinatario_email}")
        print(f"📝 Tipo: {tipo.capitalize()}")
        print(f"💬 Título: {mensaje_data['titulo']}")
    else:
        print("❌ Error al enviar el email")
        print(f"⚠️  Mensaje: {resultado['message']}")
    print("=" * 70)

def test_email_simple():
    """Prueba básica de envío de email"""
    
    print("\n" + "=" * 70)
    print("PRUEBA SIMPLE DE ENVÍO DE EMAIL")
    print("=" * 70)
    print()
    
    email = input("📧 Ingresa tu email: ").strip()
    if not email:
        print("❌ Email requerido")
        return
    
    nombre = input("👤 Ingresa tu nombre: ").strip() or "Usuario de Prueba"
    
    print(f"\n🔄 Enviando email de prueba a {email}...\n")
    
    resultado = email_service.enviar_notificacion_email(
        destinatario_email=email,
        destinatario_nombre=nombre,
        titulo="Prueba del Sistema de Notificaciones",
        mensaje="Este es un correo de prueba del sistema de notificaciones automáticas. Si recibes este mensaje, significa que todo está funcionando correctamente.",
        tipo="informacion"
    )
    
    print("=" * 70)
    if resultado['success']:
        print("✅ ¡Email de prueba enviado exitosamente!")
        print(f"📬 Revisa tu bandeja de entrada: {email}")
    else:
        print("❌ Error al enviar el email")
        print(f"⚠️  Mensaje: {resultado['message']}")
        print("\n💡 Sugerencias:")
        print("   • Verifica que el archivo .env esté configurado correctamente")
        print("   • Asegúrate de usar una contraseña de aplicación de Gmail")
        print("   • Revisa que SMTP_EMAIL y SMTP_PASSWORD estén correctos")
    print("=" * 70)

if __name__ == "__main__":
    print("\n🏥 Sistema de Notificaciones - Clínica Unión")
    print()
    print("Selecciona una opción:")
    print("  1. Prueba completa de notificación por tipo")
    print("  2. Prueba simple de envío de email")
    print()
    
    opcion = input("Opción (1-2): ").strip()
    
    if opcion == '1':
        test_envio_email_notificacion()
    elif opcion == '2':
        test_email_simple()
    else:
        print("❌ Opción no válida")
