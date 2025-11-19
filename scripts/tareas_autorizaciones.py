"""
Script para tareas programadas de autorizaciones
Debe ejecutarse diariamente (cron job o tarea programada)

Tareas:
1. Marcar autorizaciones vencidas
2. Enviar recordatorios de autorizaciones por vencer (2 días antes)
"""

from models.autorizacion_procedimiento import AutorizacionProcedimiento
from utils.notificaciones_autorizaciones import crear_notificacion_vencimiento_proximo
from datetime import datetime

def ejecutar_tareas_autorizaciones():
    """
    Ejecuta todas las tareas programadas relacionadas con autorizaciones
    """
    print(f"[{datetime.now()}] Iniciando tareas programadas de autorizaciones...")
    
    # Tarea 1: Marcar autorizaciones vencidas
    resultado_vencidas = AutorizacionProcedimiento.marcar_vencidas()
    if resultado_vencidas.get('success'):
        cantidad_vencidas = resultado_vencidas.get('autorizaciones_vencidas', 0)
        print(f"✓ {cantidad_vencidas} autorizaciones marcadas como vencidas")
    else:
        print(f"✗ Error al marcar vencidas: {resultado_vencidas.get('error')}")
    
    # Tarea 2: Enviar recordatorios de autorizaciones por vencer (2 días)
    autorizaciones_por_vencer = AutorizacionProcedimiento.obtener_por_vencer(dias=2)
    
    if autorizaciones_por_vencer:
        print(f"📧 Enviando {len(autorizaciones_por_vencer)} recordatorios de vencimiento...")
        
        for auth in autorizaciones_por_vencer:
            try:
                # Verificar que no se haya enviado ya una notificación de vencimiento hoy
                from bd import obtener_conexion
                conexion = obtener_conexion()
                with conexion.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) as count
                        FROM NOTIFICACION
                        WHERE id_referencia = %s
                        AND tipo_referencia = 'autorizacion_procedimiento'
                        AND tipo_notificacion = 'autorizacion_por_vencer'
                        AND DATE(fecha_creacion) = CURDATE()
                    """, (auth['id_autorizacion'],))
                    
                    result = cursor.fetchone()
                    if result and result['count'] > 0:
                        continue  # Ya se envió notificación hoy
                
                conexion.close()
                
                # Crear notificación de vencimiento próximo
                crear_notificacion_vencimiento_proximo(
                    auth['id_paciente'],
                    auth['id_autorizacion'],
                    auth['tipo_procedimiento'],
                    auth.get('servicio_nombre', 'Procedimiento médico'),
                    auth['dias_restantes']
                )
                
                print(f"  ✓ Recordatorio enviado a paciente ID {auth['id_paciente']}")
            except Exception as e:
                print(f"  ✗ Error al enviar recordatorio para autorización {auth['id_autorizacion']}: {e}")
    else:
        print("No hay autorizaciones por vencer en los próximos 2 días")
    
    print(f"[{datetime.now()}] Tareas completadas\n")


if __name__ == "__main__":
    # Ejecutar las tareas cuando se llama directamente
    ejecutar_tareas_autorizaciones()
