"""
Script de prueba para verificar la actualización automática de horarios vencidos.
Este script muestra los horarios que serían actualizados sin hacer cambios permanentes.
"""

from bd import obtener_conexion
from datetime import date

def verificar_horarios_vencidos():
    """
    Muestra información sobre los horarios que tienen fecha pasada
    y cuyo estado no es 'Completado'.
    """
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        fecha_actual = date.today()
        print(f"\n{'='*70}")
        print(f"VERIFICACIÓN DE HORARIOS VENCIDOS")
        print(f"{'='*70}")
        print(f"Fecha actual: {fecha_actual.strftime('%Y-%m-%d')}")
        print(f"{'='*70}\n")
        
        # Consultar horarios con fecha pasada que no están completados
        query = """
            SELECT 
                h.id_horario,
                h.id_empleado,
                CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                h.fecha,
                TIME_FORMAT(h.hora_inicio, '%%H:%%i') as hora_inicio,
                TIME_FORMAT(h.hora_fin, '%%H:%%i') as hora_fin,
                h.disponibilidad,
                h.estado
            FROM HORARIO h
            INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
            WHERE h.fecha < %s 
            AND h.estado != 'Completado'
            ORDER BY h.fecha DESC, h.hora_inicio
            LIMIT 20
        """
        
        cursor.execute(query, (fecha_actual,))
        horarios_vencidos = cursor.fetchall()
        
        if horarios_vencidos:
            print(f"✓ Se encontraron {len(horarios_vencidos)} horarios vencidos (mostrando hasta 20):\n")
            
            print(f"{'ID':<6} {'Empleado':<30} {'Fecha':<12} {'Horario':<15} {'Disponib.':<12} {'Estado Actual':<15}")
            print(f"{'-'*6} {'-'*30} {'-'*12} {'-'*15} {'-'*12} {'-'*15}")
            
            for h in horarios_vencidos:
                fecha_str = h['fecha'].strftime('%Y-%m-%d') if h['fecha'] else 'N/A'
                horario = f"{h['hora_inicio'] or 'N/A'}-{h['hora_fin'] or 'N/A'}"
                disp = h['disponibilidad'] or 'N/A'
                estado = h['estado'] or 'N/A'
                print(f"{h['id_horario']:<6} {h['empleado']:<30} {fecha_str:<12} {horario:<15} {disp:<12} {estado:<15}")
            
            print(f"\n{'='*70}")
            print(f"Estos {len(horarios_vencidos)} horarios serían actualizados a estado 'Completado'")
            print(f"{'='*70}\n")
        else:
            print("✓ No se encontraron horarios vencidos que necesiten actualización.\n")
            print("Todos los horarios con fecha pasada ya están en estado 'Completado'.\n")
        
        # Mostrar estadísticas generales
        print(f"\n{'='*70}")
        print(f"ESTADÍSTICAS GENERALES DE HORARIOS")
        print(f"{'='*70}\n")
        
        stats_query = """
            SELECT 
                estado,
                COUNT(*) as total,
                SUM(CASE WHEN fecha < %s THEN 1 ELSE 0 END) as pasados,
                SUM(CASE WHEN fecha >= %s THEN 1 ELSE 0 END) as futuros
            FROM HORARIO
            GROUP BY estado
        """
        
        cursor.execute(stats_query, (fecha_actual, fecha_actual))
        estadisticas = cursor.fetchall()
        
        if estadisticas:
            print(f"{'Estado':<15} {'Total':<10} {'Pasados':<10} {'Futuros':<10}")
            print(f"{'-'*15} {'-'*10} {'-'*10} {'-'*10}")
            
            for stat in estadisticas:
                print(f"{stat['estado']:<15} {stat['total']:<10} {stat['pasados']:<10} {stat['futuros']:<10}")
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"❌ Error al verificar horarios: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    verificar_horarios_vencidos()
