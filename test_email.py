#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el envío de emails del sistema
Prueba todos los casos: creación de reserva, cambios de estado, recuperación de contraseña
"""

import os
import sys
from dotenv import load_dotenv

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
        enviar_email_cambio_estado_reserva,
        enviar_email_cancelacion_aprobada,
        enviar_email_cancelacion_medico,
        enviar_email_reprogramacion_aprobada,
        enviar_email_reprogramacion_medico,
        enviar_email_confirmacion_reserva,
        enviar_email_recordatorio_24h,
        enviar_email_recordatorio_2h
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
# Puede pasarse como argumento: python test_email.py email@ejemplo.com [opcion]
# Si solo se pasa un argumento y contiene "@", es el email; si no, es la opción
EMAIL_PRUEBA = None
opcion_arg = None

if len(sys.argv) > 1:
    arg1 = sys.argv[1].strip()
    if "@" in arg1:
        # Es un email
        EMAIL_PRUEBA = arg1
        if len(sys.argv) > 2:
            opcion_arg = sys.argv[2]
    else:
        # Es la opción
        opcion_arg = arg1

if not EMAIL_PRUEBA:
    EMAIL_PRUEBA = smtp_email  # Usar el email del .env por defecto

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

def test_email_cancelacion_aprobada():
    """Prueba: Email de cancelación aprobada"""
    print("🧪 PRUEBA: Email de cancelación aprobada")
    print("-" * 70)
    
    try:
        resultado = enviar_email_cancelacion_aprobada(
            paciente_email=EMAIL_PRUEBA,
            paciente_nombre="Juan Pérez",
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            medico_nombre="Dr. Carlos García",
            especialidad="Cardiología",
            servicio="Consulta Médica General",
            motivo_cancelacion="Emergencia familiar",
            comentario_admin="Su cancelación ha sido procesada. Puede reagendar cuando lo desee."
        )
        
        if resultado.get('success'):
            print("✅ Email de cancelación aprobada enviado exitosamente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_cancelacion_medico():
    """Prueba: Email de cancelación al médico"""
    print("🧪 PRUEBA: Email de cancelación al médico")
    print("-" * 70)
    
    try:
        resultado = enviar_email_cancelacion_medico(
            medico_email=EMAIL_PRUEBA,
            medico_nombre="Dr. Carlos García",
            paciente_nombre="Juan Pérez",
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            servicio="Consulta Médica General",
            motivo_cancelacion="Emergencia familiar del paciente"
        )
        
        if resultado.get('success'):
            print("✅ Email de cancelación al médico enviado exitosamente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_reprogramacion_aprobada():
    """Prueba: Email de reprogramación aprobada"""
    print("🧪 PRUEBA: Email de reprogramación aprobada")
    print("-" * 70)
    
    try:
        resultado = enviar_email_reprogramacion_aprobada(
            paciente_email=EMAIL_PRUEBA,
            paciente_nombre="Juan Pérez",
            fecha_anterior="25/12/2024",
            hora_inicio_anterior="10:00",
            hora_fin_anterior="11:00",
            fecha_nueva="28/12/2024",
            hora_inicio_nueva="14:00",
            hora_fin_nueva="15:00",
            medico_nombre="Dr. Carlos García",
            especialidad="Cardiología",
            servicio="Consulta Médica General",
            motivo_reprogramacion="Solicitud del paciente",
            comentario_admin="Su solicitud ha sido aprobada. Nueva fecha confirmada."
        )
        
        if resultado.get('success'):
            print("✅ Email de reprogramación aprobada enviado exitosamente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_reprogramacion_medico():
    """Prueba: Email de reprogramación al médico"""
    print("🧪 PRUEBA: Email de reprogramación al médico")
    print("-" * 70)
    
    try:
        resultado = enviar_email_reprogramacion_medico(
            medico_email=EMAIL_PRUEBA,
            medico_nombre="Dr. Carlos García",
            paciente_nombre="Juan Pérez",
            fecha_anterior="25/12/2024",
            hora_inicio_anterior="10:00",
            hora_fin_anterior="11:00",
            fecha_nueva="28/12/2024",
            hora_inicio_nueva="14:00",
            hora_fin_nueva="15:00",
            servicio="Consulta Médica General",
            motivo_reprogramacion="Solicitud del paciente"
        )
        
        if resultado.get('success'):
            print("✅ Email de reprogramación al médico enviado exitosamente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_confirmacion_reserva():
    """Prueba: Email de confirmación de reserva"""
    print("🧪 PRUEBA: Email de confirmación de reserva")
    print("-" * 70)
    
    try:
        resultado = enviar_email_confirmacion_reserva(
            paciente_email=EMAIL_PRUEBA,
            paciente_nombre="Juan Pérez",
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            medico_nombre="Dr. Carlos García",
            especialidad="Cardiología",
            servicio="Consulta Médica General"
        )
        
        if resultado.get('success'):
            print("✅ Email de confirmación enviado exitosamente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_recordatorio_24h():
    """Prueba: Email de recordatorio 24 horas"""
    print("🧪 PRUEBA: Email de recordatorio 24 horas antes")
    print("-" * 70)
    
    try:
        resultado = enviar_email_recordatorio_24h(
            paciente_email=EMAIL_PRUEBA,
            paciente_nombre="Juan Pérez",
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            medico_nombre="Dr. Carlos García",
            especialidad="Cardiología",
            servicio="Consulta Médica General"
        )
        
        if resultado.get('success'):
            print("✅ Email de recordatorio 24h enviado exitosamente")
            print(f"   Mensaje: {resultado.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Error al enviar email: {resultado.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_recordatorio_2h():
    """Prueba: Email de recordatorio 2 horas"""
    print("🧪 PRUEBA: Email de recordatorio 2 horas antes")
    print("-" * 70)
    
    try:
        resultado = enviar_email_recordatorio_2h(
            paciente_email=EMAIL_PRUEBA,
            paciente_nombre="Juan Pérez",
            fecha="25/12/2024",
            hora_inicio="10:00",
            hora_fin="11:00",
            medico_nombre="Dr. Carlos García",
            especialidad="Cardiología"
        )
        
        if resultado.get('success'):
            print("✅ Email de recordatorio 2h enviado exitosamente")
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
    global EMAIL_PRUEBA, opcion_arg
    
    print("🚀 Iniciando pruebas de envío de emails...")
    print()
    
    # Usar opción del argumento si está disponible, sino preguntar
    if opcion_arg:
        opcion = opcion_arg
    else:
        # Menú de opciones
        print("Selecciona qué pruebas ejecutar:")
        print("1. Todas las pruebas (recomendado) - PRUEBA COMPLETA")
        print("2. Solo creación de reserva (paciente y médico)")
        print("3. Solo cambios de estado")
        print("4. Solo notificación genérica")
        print("5. Prueba individual de estado")
        print("6. Pruebas de cancelación")
        print("7. Pruebas de reprogramación")
        print("8. Pruebas de recordatorios")
        print()
        
        try:
            opcion = input("Opción (1-8): ").strip()
        except (EOFError, KeyboardInterrupt):
            # Si no hay input disponible (ejecución automática), usar opción 1
            print("\n⚠️ No se puede leer input, usando opción 1 (Todas las pruebas)")
            opcion = "1"
    
    if opcion == "1":
        # TODAS LAS PRUEBAS - Prueba completa de todos los eventos
        print("\n🎯 EJECUTANDO PRUEBA COMPLETA DE TODOS LOS EVENTOS\n")
        
        # 1. Creación de reserva
        print("=" * 70)
        print("📋 SECCIÓN 1: CREACIÓN DE RESERVA")
        print("=" * 70)
        test_email_reserva_creada_paciente()
        test_email_reserva_creada_medico()
        
        # 2. Confirmación de reserva
        print("=" * 70)
        print("📋 SECCIÓN 2: CONFIRMACIÓN DE RESERVA")
        print("=" * 70)
        test_email_confirmacion_reserva()
        
        # 3. Cambios de estado
        print("=" * 70)
        print("📋 SECCIÓN 3: CAMBIOS DE ESTADO")
        print("=" * 70)
        test_email_cambio_estado("Confirmada", "verde")
        test_email_cambio_estado("Cancelada", "rojo")
        test_email_cambio_estado("Completada", "azul")
        test_email_cambio_estado("Inasistida", "naranja")
        test_email_cambio_estado("Pendiente", "índigo")
        
        # 4. Cancelación
        print("=" * 70)
        print("📋 SECCIÓN 4: CANCELACIÓN DE RESERVA")
        print("=" * 70)
        test_email_cancelacion_aprobada()
        test_email_cancelacion_medico()
        
        # 5. Reprogramación
        print("=" * 70)
        print("📋 SECCIÓN 5: REPROGRAMACIÓN DE RESERVA")
        print("=" * 70)
        test_email_reprogramacion_aprobada()
        test_email_reprogramacion_medico()
        
        # 6. Recordatorios
        print("=" * 70)
        print("📋 SECCIÓN 6: RECORDATORIOS")
        print("=" * 70)
        test_email_recordatorio_24h()
        test_email_recordatorio_2h()
        
        # 7. Notificación genérica
        print("=" * 70)
        print("📋 SECCIÓN 7: NOTIFICACIÓN GENÉRICA")
        print("=" * 70)
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
        
    elif opcion == "6":
        test_email_cancelacion_aprobada()
        test_email_cancelacion_medico()
        
    elif opcion == "7":
        test_email_reprogramacion_aprobada()
        test_email_reprogramacion_medico()
        
    elif opcion == "8":
        test_email_recordatorio_24h()
        test_email_recordatorio_2h()
        
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

