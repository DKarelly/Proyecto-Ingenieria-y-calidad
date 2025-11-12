"""
Script para enviar recordatorios automáticos por email
Se debe ejecutar periódicamente (ej: cada hora mediante cron/task scheduler)

Envía dos tipos de recordatorios:
1. 24 horas antes de la cita
2. 2 horas antes de la cita
"""

import sys
from datetime import datetime, timedelta, date, time as dt_time
from bd import obtener_conexion
from utils.email_service import enviar_email_recordatorio_24h, enviar_email_recordatorio_2h
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def enviar_recordatorios_24h():
    """Envía recordatorios a pacientes con citas mañana"""
    print("\n" + "="*60)
    print("🔔 INICIANDO ENVÍO DE RECORDATORIOS 24H")
    print("="*60)
    
    # Calcular fecha de mañana
    manana = date.today() + timedelta(days=1)
    print(f"📅 Buscando citas para: {manana.strftime('%d/%m/%Y')}")
    
    conexion = None
    enviados = 0
    errores = 0
    
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Buscar todas las reservas confirmadas para mañana
            sql = """
                SELECT 
                    r.id_reserva,
                    p.fecha,
                    TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio,
                    TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin,
                    CONCAT(pac.nombres, ' ', pac.apellidos) as nombre_paciente,
                    pac.correo as paciente_email,
                    CONCAT(emp.nombres, ' ', emp.apellidos) as nombre_medico,
                    esp.nombre as especialidad,
                    COALESCE(serv.nombre, 'Consulta Médica') as servicio
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                LEFT JOIN SERVICIO serv ON p.id_servicio = serv.id_servicio
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                WHERE r.estado IN ('Confirmada', 'Pendiente')
                AND DATE(p.fecha) = %s
                AND pac.correo IS NOT NULL
                AND pac.correo != ''
            """
            
            cursor.execute(sql, (manana,))
            citas = cursor.fetchall()
            
            print(f"📋 Citas encontradas: {len(citas)}")
            
            for cita in citas:
                try:
                    fecha_formateada = cita['fecha'].strftime('%d de %B de %Y') if isinstance(cita['fecha'], (date, datetime)) else str(cita['fecha'])
                    
                    resultado = enviar_email_recordatorio_24h(
                        paciente_email=cita['paciente_email'],
                        paciente_nombre=cita['nombre_paciente'],
                        fecha=fecha_formateada,
                        hora_inicio=cita['hora_inicio'],
                        hora_fin=cita['hora_fin'],
                        medico_nombre=cita['nombre_medico'] or 'Por asignar',
                        especialidad=cita['especialidad'] or 'General',
                        servicio=cita['servicio']
                    )
                    
                    if resultado['success']:
                        print(f"  ✅ Recordatorio 24h enviado a: {cita['paciente_email']} (Reserva #{cita['id_reserva']})")
                        enviados += 1
                    else:
                        print(f"  ❌ Error al enviar a {cita['paciente_email']}: {resultado['message']}")
                        errores += 1
                        
                except Exception as e:
                    print(f"  ❌ Error procesando reserva #{cita['id_reserva']}: {e}")
                    errores += 1
            
            print(f"\n📊 Resumen Recordatorios 24h:")
            print(f"   ✅ Enviados exitosamente: {enviados}")
            print(f"   ❌ Errores: {errores}")
            
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


def enviar_recordatorios_2h():
    """Envía recordatorios a pacientes con citas en 2 horas"""
    print("\n" + "="*60)
    print("🚨 INICIANDO ENVÍO DE RECORDATORIOS 2H")
    print("="*60)
    
    # Calcular hora dentro de 2 horas (ventana de +/- 30 minutos)
    ahora = datetime.now()
    hora_objetivo = ahora + timedelta(hours=2)
    hora_inicio_ventana = hora_objetivo - timedelta(minutes=30)
    hora_fin_ventana = hora_objetivo + timedelta(minutes=30)
    
    print(f"⏰ Hora actual: {ahora.strftime('%H:%M')}")
    print(f"🎯 Buscando citas entre: {hora_inicio_ventana.strftime('%H:%M')} y {hora_fin_ventana.strftime('%H:%M')}")
    
    conexion = None
    enviados = 0
    errores = 0
    
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Buscar reservas para hoy en la ventana de tiempo
            sql = """
                SELECT 
                    r.id_reserva,
                    p.fecha,
                    p.hora_inicio,
                    p.hora_fin,
                    TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio_fmt,
                    TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin_fmt,
                    CONCAT(pac.nombres, ' ', pac.apellidos) as nombre_paciente,
                    pac.correo as paciente_email,
                    CONCAT(emp.nombres, ' ', emp.apellidos) as nombre_medico,
                    esp.nombre as especialidad
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                WHERE r.estado IN ('Confirmada', 'Pendiente')
                AND DATE(p.fecha) = CURDATE()
                AND p.hora_inicio >= %s
                AND p.hora_inicio <= %s
                AND pac.correo IS NOT NULL
                AND pac.correo != ''
            """
            
            cursor.execute(sql, (
                hora_inicio_ventana.time(),
                hora_fin_ventana.time()
            ))
            citas = cursor.fetchall()
            
            print(f"📋 Citas encontradas: {len(citas)}")
            
            for cita in citas:
                try:
                    fecha_formateada = cita['fecha'].strftime('%d de %B de %Y') if isinstance(cita['fecha'], (date, datetime)) else str(cita['fecha'])
                    
                    resultado = enviar_email_recordatorio_2h(
                        paciente_email=cita['paciente_email'],
                        paciente_nombre=cita['nombre_paciente'],
                        fecha=fecha_formateada,
                        hora_inicio=cita['hora_inicio_fmt'],
                        hora_fin=cita['hora_fin_fmt'],
                        medico_nombre=cita['nombre_medico'] or 'Por asignar',
                        especialidad=cita['especialidad'] or 'General'
                    )
                    
                    if resultado['success']:
                        print(f"  ✅ Recordatorio 2h enviado a: {cita['paciente_email']} (Reserva #{cita['id_reserva']})")
                        enviados += 1
                    else:
                        print(f"  ❌ Error al enviar a {cita['paciente_email']}: {resultado['message']}")
                        errores += 1
                        
                except Exception as e:
                    print(f"  ❌ Error procesando reserva #{cita['id_reserva']}: {e}")
                    errores += 1
            
            print(f"\n📊 Resumen Recordatorios 2h:")
            print(f"   ✅ Enviados exitosamente: {enviados}")
            print(f"   ❌ Errores: {errores}")
            
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


def main():
    """Función principal"""
    print("\n" + "🏥"*30)
    print("  SISTEMA DE RECORDATORIOS AUTOMÁTICOS POR EMAIL")
    print("  Clínica Unión")
    print("🏥"*30)
    print(f"\n📅 Fecha/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificar configuración de email
    if not os.getenv('SMTP_EMAIL') or not os.getenv('SMTP_PASSWORD'):
        print("\n❌ ERROR: Variables de entorno de email no configuradas")
        print("   Configure SMTP_EMAIL y SMTP_PASSWORD en el archivo .env")
        return
    
    print(f"📧 Servidor SMTP: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
    print(f"📧 Email remitente: {os.getenv('SMTP_EMAIL')}")
    
    # Enviar recordatorios
    enviar_recordatorios_24h()
    enviar_recordatorios_2h()
    
    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
