"""
Servicio de actualización automática de estados de reservas.

Este módulo proporciona funciones para actualizar automáticamente el estado
de las reservas según las siguientes reglas:

1. Si la reserva (CITA) ya pasó su fecha/hora de inicio Y tiene diagnóstico:
   - Estado de RESERVA: 'Completada'
   - Estado de CITA: 'Completada'
   
2. Si la reserva (CITA) ya pasó su fecha/hora de inicio Y NO tiene diagnóstico:
   - Estado de RESERVA: 'Inasistida'
   - Estado de CITA: permanece igual (o se marca inasistida)

3. Para EXAMEN y OPERACION:
   - Se completan cuando el médico los marca como completados manualmente
   - Si pasan de fecha sin completarse, se pueden marcar según política

Tablas involucradas:
- RESERVA: estado puede ser 'Confirmada', 'Completada', 'Cancelada', 'Inasistida'
- CITA: estado puede ser 'Pendiente', 'Confirmada', 'Completada', 'Cancelada'
- EXAMEN: estado puede ser 'Pendiente', 'Completada', 'Cancelada'
- OPERACION: estado puede ser 'Pendiente', 'Completada', 'Cancelada'
"""

from datetime import datetime, date, time, timedelta
from bd import obtener_conexion


def actualizar_estados_reservas_citas():
    """
    Actualiza automáticamente el estado de las reservas y citas que ya pasaron.
    
    Reglas:
    - Citas con diagnóstico -> Completada
    - Citas sin diagnóstico que ya pasaron -> Inasistida
    
    Returns:
        dict: Resumen de las actualizaciones realizadas
    """
    conexion = None
    resultado = {
        'completadas': 0,
        'inasistidas': 0,
        'errores': []
    }
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        ahora = datetime.now()
        fecha_actual = ahora.date()
        hora_actual = ahora.time()
        
        # 1. Marcar como COMPLETADAS las citas que tienen diagnóstico y ya pasaron
        # (reservas tipo 1 = cita médica)
        cursor.execute("""
            UPDATE RESERVA r
            INNER JOIN CITA c ON c.id_reserva = r.id_reserva
            SET 
                r.estado = 'Completada',
                r.fecha_completada = NOW(),
                c.estado = 'Completada'
            WHERE r.estado = 'Confirmada'
            AND c.estado IN ('Pendiente', 'Confirmada')
            AND c.diagnostico IS NOT NULL 
            AND c.diagnostico != ''
            AND (
                c.fecha_cita < %s 
                OR (c.fecha_cita = %s AND c.hora_inicio < %s)
            )
        """, (fecha_actual, fecha_actual, hora_actual))
        
        resultado['completadas'] = cursor.rowcount
        
        # 2. Marcar como INASISTIDAS las citas SIN diagnóstico que ya pasaron
        # Solo si ya pasó la fecha completa (no solo la hora de inicio)
        cursor.execute("""
            UPDATE RESERVA r
            INNER JOIN CITA c ON c.id_reserva = r.id_reserva
            SET 
                r.estado = 'Inasistida',
                c.estado = 'Cancelada'
            WHERE r.estado = 'Confirmada'
            AND c.estado IN ('Pendiente', 'Confirmada')
            AND (c.diagnostico IS NULL OR c.diagnostico = '')
            AND c.fecha_cita < %s
        """, (fecha_actual,))
        
        resultado['inasistidas'] = cursor.rowcount
        
        conexion.commit()
        
        print(f"[{ahora}] Actualización de estados: {resultado['completadas']} completadas, {resultado['inasistidas']} inasistidas")
        
    except Exception as e:
        resultado['errores'].append(str(e))
        print(f"Error al actualizar estados de reservas: {e}")
        if conexion:
            conexion.rollback()
    finally:
        if conexion:
            conexion.close()
    
    return resultado


def actualizar_estados_examenes():
    """
    Actualiza el estado de los exámenes que ya pasaron sin completarse.
    
    Reglas:
    - Exámenes pendientes que pasaron de fecha -> Se marcan como Cancelada/Inasistida
    """
    conexion = None
    resultado = {
        'actualizados': 0,
        'errores': []
    }
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        ahora = datetime.now()
        fecha_actual = ahora.date()
        
        # Marcar exámenes pendientes que ya pasaron como Cancelada
        cursor.execute("""
            UPDATE EXAMEN e
            INNER JOIN RESERVA r ON e.id_reserva = r.id_reserva
            SET 
                e.estado = 'Cancelada',
                r.estado = 'Inasistida'
            WHERE e.estado = 'Pendiente'
            AND r.estado = 'Confirmada'
            AND e.fecha_examen < %s
        """, (fecha_actual,))
        
        resultado['actualizados'] = cursor.rowcount
        conexion.commit()
        
    except Exception as e:
        resultado['errores'].append(str(e))
        if conexion:
            conexion.rollback()
    finally:
        if conexion:
            conexion.close()
    
    return resultado


def actualizar_estados_operaciones():
    """
    Actualiza el estado de las operaciones que ya pasaron sin completarse.
    
    Reglas:
    - Operaciones pendientes que pasaron de fecha -> Se marcan como Cancelada
    """
    conexion = None
    resultado = {
        'actualizados': 0,
        'errores': []
    }
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        ahora = datetime.now()
        fecha_actual = ahora.date()
        
        # Marcar operaciones pendientes que ya pasaron como Cancelada
        cursor.execute("""
            UPDATE OPERACION o
            INNER JOIN RESERVA r ON o.id_reserva = r.id_reserva
            SET 
                o.estado = 'Cancelada',
                r.estado = 'Inasistida'
            WHERE o.estado = 'Pendiente'
            AND r.estado = 'Confirmada'
            AND o.fecha_operacion < %s
        """, (fecha_actual,))
        
        resultado['actualizados'] = cursor.rowcount
        conexion.commit()
        
    except Exception as e:
        resultado['errores'].append(str(e))
        if conexion:
            conexion.rollback()
    finally:
        if conexion:
            conexion.close()
    
    return resultado


def ejecutar_actualizacion_completa():
    """
    Ejecuta la actualización completa de todos los tipos de reservas.
    
    Esta función debe llamarse periódicamente (ej: cada hora o al iniciar la app)
    para mantener los estados actualizados.
    
    Returns:
        dict: Resumen completo de todas las actualizaciones
    """
    print(f"[{datetime.now()}] Iniciando actualización automática de estados de reservas...")
    
    resultados = {
        'citas': actualizar_estados_reservas_citas(),
        'examenes': actualizar_estados_examenes(),
        'operaciones': actualizar_estados_operaciones(),
        'timestamp': datetime.now().isoformat()
    }
    
    total_completadas = resultados['citas']['completadas']
    total_inasistidas = resultados['citas']['inasistidas'] + resultados['examenes']['actualizados'] + resultados['operaciones']['actualizados']
    
    print(f"[{datetime.now()}] Actualización completada: {total_completadas} completadas, {total_inasistidas} inasistidas/canceladas")
    
    return resultados


# Para ejecutar desde línea de comandos
if __name__ == '__main__':
    resultado = ejecutar_actualizacion_completa()
    print(f"\nResultado: {resultado}")
