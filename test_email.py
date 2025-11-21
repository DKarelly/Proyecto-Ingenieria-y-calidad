#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el envío de emails del sistema
Prueba todos los casos: creación de reserva, cambios de estado, recuperación de contraseña
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar que las variables de entorno estén configuradas
print("=" * 70)
print("🔍 VERIFICANDO CONFIGURACIÓN DE EMAIL")
print("=" * 70)

smtp_email = os.getenv('SMTP_EMAIL')
smtp_password = os.getenv('SMTP_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = os.getenv('SMTP_PORT', '587')

if not smtp_email or not smtp_password:
    print("❌ ERROR: Variables de entorno no configuradas")
    print("   Asegúrate de tener configurado en .env:")
    print("   - SMTP_EMAIL")
    print("   - SMTP_PASSWORD")
    print("   - SMTP_SERVER (opcional, default: smtp.gmail.com)")
    print("   - SMTP_PORT (opcional, default: 587)")
    sys.exit(1)

print(f"✅ SMTP_SERVER: {smtp_server}")
print(f"✅ SMTP_PORT: {smtp_port}")
print(f"✅ SMTP_EMAIL: {smtp_email}")
print(f"✅ SMTP_PASSWORD: {'*' * len(smtp_password)}")
print()

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.email_service import (
        email_service,
        enviar_email_reserva_creada,
        enviar_email_reserva_creada_medico,
        enviar_email_cambio_estado_reserva
    )
    print("✅ Módulos de email importados correctamente")
except ImportError as e:
    print(f"❌ ERROR al importar módulos: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("📧 PRUEBAS DE ENVÍO DE EMAILS")
print("=" * 70)
print()

# Email de prueba (cambiar por el tuyo)
# Puede pasarse como argumento: python test_email.py jassonpuican@gmail.com
if len(sys.argv) > 1:
    EMAIL_PRUEBA = sys.argv[1]
else:
    EMAIL_PRUEBA = input("📧 Ingresa tu email para recibir las pruebas (o presiona Enter para usar el SMTP_EMAIL): ").strip()
    if not EMAIL_PRUEBA:
        EMAIL_PRUEBA = smtp_email

print(f"📬 Email de destino: {EMAIL_PRUEBA}")
print()

def test_email_reserva_creada_paciente():
    """Prueba 1: Email de creación de reserva al paciente"""
    print("🧪 PRUEBA 1: Email de creación de reserva (Paciente)")
    print("-" * 70)
    
    try:
        resultado = enviar_email_reserva_creada(
            paciente_email=EMAIL_PRUEBA,
            paciente_nombre="Juan Pérez",
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            medico_nombre="Dr. Carlos García",
            especialidad="Cardiología",
            servicio="Consulta Médica General",
            id_reserva=12345
        )
        
        if resultado.get('success'):
            print("✅ Email enviado exitosamente al paciente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_reserva_creada_medico():
    """Prueba 2: Email de creación de reserva al médico"""
    print("🧪 PRUEBA 2: Email de creación de reserva (Médico)")
    print("-" * 70)
    
    try:
        resultado = enviar_email_reserva_creada_medico(
            medico_email=EMAIL_PRUEBA,
            medico_nombre="Dr. Carlos García",
            paciente_nombre="Juan Pérez",
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            servicio="Consulta Médica General",
            id_reserva=12345
        )
        
        if resultado.get('success'):
            print("✅ Email enviado exitosamente al médico")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_cambio_estado(estado, color_nombre):
    """Prueba genérica para cambio de estado"""
    print(f"🧪 PRUEBA: Email de cambio de estado a '{estado}'")
    print("-" * 70)
    
    try:
        resultado = enviar_email_cambio_estado_reserva(
            paciente_email=EMAIL_PRUEBA,
            paciente_nombre="Juan Pérez",
            medico_email=EMAIL_PRUEBA,
            medico_nombre="Dr. Carlos García",
            id_reserva=12345,
            estado_anterior="Confirmada",
            estado_nuevo=estado,
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            servicio="Consulta Médica General",
            motivo=f"Cambio de estado a {estado} - Prueba del sistema" if estado == "Cancelada" else None
        )
        
        if resultado.get('paciente') and resultado['paciente'].get('success'):
            print(f"✅ Email enviado exitosamente al paciente (estado: {estado})")
        else:
            print(f"❌ Error al enviar email al paciente: {resultado.get('paciente', {}).get('message', 'Error desconocido')}")
        
        if resultado.get('medico') and resultado['medico'].get('success'):
            print(f"✅ Email enviado exitosamente al médico (estado: {estado})")
        else:
            print(f"❌ Error al enviar email al médico: {resultado.get('medico', {}).get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_notificacion_generica():
    """Prueba: Email de notificación genérica"""
    print("🧪 PRUEBA: Email de notificación genérica")
    print("-" * 70)
    
    try:
        resultado = email_service.enviar_notificacion_email(
            destinatario_email=EMAIL_PRUEBA,
            destinatario_nombre="Usuario de Prueba",
            titulo="Notificación de Prueba",
            mensaje="Este es un mensaje de prueba del sistema de notificaciones por email.",
            tipo='informacion'
        )
        
        if resultado.get('success'):
            print("✅ Email de notificación enviado exitosamente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas de envío de emails...")
    print()
    
    # Si se pasa opción como segundo argumento, usarla; sino preguntar
    if len(sys.argv) > 2:
        opcion = sys.argv[2]
    else:
        # Menú de opciones
        print("Selecciona qué pruebas ejecutar:")
        print("1. Todas las pruebas (recomendado)")
        print("2. Solo creación de reserva (paciente y médico)")
        print("3. Solo cambios de estado")
        print("4. Solo notificación genérica")
        print("5. Prueba individual de estado")
        print()
        
        opcion = input("Opción (1-5): ").strip()
    
    if opcion == "1":
        # Todas las pruebas
        test_email_reserva_creada_paciente()
        test_email_reserva_creada_medico()
        test_email_cambio_estado("Confirmada", "verde")
        test_email_cambio_estado("Cancelada", "rojo")
        test_email_cambio_estado("Completada", "azul")
        test_email_cambio_estado("Inasistida", "naranja")
        test_email_cambio_estado("Pendiente", "índigo")
        test_email_notificacion_generica()
        
    elif opcion == "2":
        test_email_reserva_creada_paciente()
        test_email_reserva_creada_medico()
        
    elif opcion == "3":
        test_email_cambio_estado("Confirmada", "verde")
        test_email_cambio_estado("Cancelada", "rojo")
        test_email_cambio_estado("Completada", "azul")
        test_email_cambio_estado("Inasistida", "naranja")
        test_email_cambio_estado("Pendiente", "índigo")
        
    elif opcion == "4":
        test_email_notificacion_generica()
        
    elif opcion == "5":
        print("\nEstados disponibles:")
        print("1. Confirmada")
        print("2. Cancelada")
        print("3. Completada")
        print("4. Inasistida")
        print("5. Pendiente")
        estado_opcion = input("\nSelecciona estado (1-5): ").strip()
        
        estados = {
            "1": "Confirmada",
            "2": "Cancelada",
            "3": "Completada",
            "4": "Inasistida",
            "5": "Pendiente"
        }
        
        estado = estados.get(estado_opcion, "Confirmada")
        test_email_cambio_estado(estado, "prueba")
        
    else:
        print("❌ Opción inválida")
        return
    
    print()
    print("=" * 70)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 70)
    print()
    print("📬 Revisa tu bandeja de entrada (y spam) en:", EMAIL_PRUEBA)
    print()
    print("💡 Si no recibes los emails:")
    print("   1. Verifica que SMTP_EMAIL y SMTP_PASSWORD estén correctos en .env")
    print("   2. Para Gmail, asegúrate de usar una 'Contraseña de Aplicación'")
    print("   3. Revisa la carpeta de spam")
    print("   4. Verifica los logs del servidor para más detalles")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Pruebas canceladas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

