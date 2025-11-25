"""
Ejemplo de uso del sistema Custodio_De_Agenda
Este script demuestra cómo usar el sistema de notificaciones de alta precisión
"""

from datetime import datetime, timedelta
from utils.custodio_agenda import Capsula_De_Cita, Custodio_De_Agenda

def ejemplo_uso_directo():
    """Ejemplo de uso directo con Capsula_De_Cita"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Uso Directo con Capsula_De_Cita")
    print("="*60)
    
    # Crear una cápsula de cita
    fecha_cita = datetime.now() + timedelta(days=3)
    capsula = Capsula_De_Cita(
        doctor="Dra. Ana Polo",
        especialidad="Cardiología",
        fecha=fecha_cita,
        frecuencia_alerta="Cada 24 horas"
    )
    
    print(f"\n📋 Cápsula creada:")
    print(f"   Artífice_Clínico: {capsula.Artífice_Clínico}")
    print(f"   Rama_De_Curación: {capsula.Rama_De_Curación}")
    print(f"   Coordenada_Temporal: {capsula.Coordenada_Temporal}")
    print(f"   Pulso_De_Recordatorio: {capsula.Pulso_De_Recordatorio}")
    
    # Generar mensaje (sin enviar)
    mensaje_data = Custodio_De_Agenda.generar_mensaje_nexo(
        capsula_cita=capsula,
        nombre_paciente="María González"
    )
    
    print(f"\n📧 Mensaje generado:")
    print(f"   Asunto: {mensaje_data['asunto']}")
    print(f"   Mensaje HTML: {len(mensaje_data['mensaje_html'])} caracteres")
    
    # Para enviar realmente, descomentar:
    # resultado = Custodio_De_Agenda.enviar_notificacion_cita(
    #     paciente_email="paciente@example.com",
    #     paciente_nombre="María González",
    #     capsula_cita=capsula
    # )
    # print(f"\n📧 Resultado del envío: {resultado}")


def ejemplo_desde_reserva():
    """Ejemplo de uso desde una reserva existente"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Uso desde Reserva Existente")
    print("="*60)
    
    # Nota: Requiere una reserva existente en la base de datos
    # Reemplazar con un ID de reserva válido
    id_reserva_ejemplo = 1  # Cambiar por un ID real
    
    print(f"\n📋 Intentando crear cápsula desde reserva #{id_reserva_ejemplo}...")
    
    # Crear cápsula desde reserva
    capsula = Custodio_De_Agenda.crear_capsula_desde_reserva(
        id_reserva_ejemplo,
        frecuencia_alerta="Cada 24 horas"
    )
    
    if capsula:
        print(f"   ✅ Cápsula creada exitosamente:")
        print(f"      Artífice_Clínico: {capsula.Artífice_Clínico}")
        print(f"      Rama_De_Curación: {capsula.Rama_De_Curación}")
        print(f"      Coordenada_Temporal: {capsula.Coordenada_Temporal}")
        print(f"      Pulso_De_Recordatorio: {capsula.Pulso_De_Recordatorio}")
    else:
        print(f"   ❌ No se pudo crear la cápsula (reserva no encontrada o error)")
    
    # Para enviar notificación desde reserva, usar:
    # resultado = Custodio_De_Agenda.enviar_notificacion_desde_reserva(
    #     id_reserva=id_reserva_ejemplo,
    #     frecuencia_alerta="Cada 24 horas"
    # )
    # print(f"\n📧 Resultado del envío: {resultado}")


def ejemplo_diferentes_frecuencias():
    """Ejemplo con diferentes frecuencias de recordatorio"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Diferentes Frecuencias de Recordatorio")
    print("="*60)
    
    fecha_cita = datetime.now() + timedelta(days=1)
    
    frecuencias = [
        "Cada 24 horas",
        "Cada 12 horas",
        "30 minutos antes",
        "2 horas antes",
        "Cada 6 horas hasta la cita"
    ]
    
    for frecuencia in frecuencias:
        capsula = Capsula_De_Cita(
            doctor="Dr. Juan Pérez",
            especialidad="Dermatología",
            fecha=fecha_cita,
            frecuencia_alerta=frecuencia
        )
        
        mensaje_data = Custodio_De_Agenda.generar_mensaje_nexo(
            capsula_cita=capsula,
            nombre_paciente="Carlos Rodríguez"
        )
        
        print(f"\n📧 Frecuencia: {frecuencia}")
        print(f"   Asunto: {mensaje_data['asunto']}")
        # El mensaje incluirá la frecuencia en el "Protocolo de Insistencia")


if __name__ == "__main__":
    print("\n" + "🏥"*30)
    print("  EJEMPLOS DE USO - CUSTODIO_DE_AGENDA")
    print("  Sistema de Notificaciones de Alta Precisión")
    print("  Clínica Unión")
    print("🏥"*30)
    
    # Ejecutar ejemplos
    ejemplo_uso_directo()
    ejemplo_desde_reserva()
    ejemplo_diferentes_frecuencias()
    
    print("\n" + "="*60)
    print("✅ EJEMPLOS COMPLETADOS")
    print("="*60)
    print("\n💡 Nota: Los ejemplos muestran la generación de mensajes.")
    print("   Para enviar emails reales, descomentar las líneas de envío")
    print("   y asegurarse de tener configurado SMTP_EMAIL y SMTP_PASSWORD.\n")

