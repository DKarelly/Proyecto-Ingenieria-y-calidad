"""
Script para ejecutar manualmente la actualización de horarios vencidos.
Este script actualiza permanentemente los horarios con fecha pasada.
"""

from bd import obtener_conexion
from datetime import date

def ejecutar_actualizacion_horarios():
    """
    Ejecuta la actualización de horarios vencidos a estado 'Completado'.
    """
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        fecha_actual = date.today()
        print(f"\n{'='*70}")
        print(f"ACTUALIZACIÓN DE HORARIOS VENCIDOS")
        print(f"{'='*70}")
        print(f"Fecha actual: {fecha_actual.strftime('%Y-%m-%d')}")
        print(f"{'='*70}\n")
        
        # Primero mostrar cuántos serán actualizados
        query_count = """
            SELECT COUNT(*) as total
            FROM HORARIO
            WHERE fecha < %s 
            AND estado != 'Completado'
        """
        
        cursor.execute(query_count, (fecha_actual,))
        result = cursor.fetchone()
        total_a_actualizar = result['total']
        
        if total_a_actualizar == 0:
            print("✓ No hay horarios que necesiten actualización.")
            print("Todos los horarios con fecha pasada ya están en estado 'Completado'.\n")
            return
        
        print(f"⚠️  Se van a actualizar {total_a_actualizar} horarios a estado 'Completado'\n")
        
        # Confirmar
        respuesta = input("¿Desea continuar con la actualización? (SI/NO): ").strip().upper()
        
        if respuesta != 'SI':
            print("\n❌ Actualización cancelada por el usuario.\n")
            return
        
        # Actualizar horarios
        query_update = """
            UPDATE HORARIO 
            SET estado = 'Completado'
            WHERE fecha < %s 
            AND estado != 'Completado'
        """
        
        cursor.execute(query_update, (fecha_actual,))
        registros_actualizados = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ ACTUALIZACIÓN EXITOSA")
        print(f"{'='*70}")
        print(f"Se actualizaron {registros_actualizados} horarios a estado 'Completado'")
        print(f"{'='*70}\n")
        
        # Mostrar estadísticas después de la actualización
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
        
        print(f"ESTADÍSTICAS ACTUALIZADAS:")
        print(f"{'-'*70}")
        print(f"{'Estado':<15} {'Total':<10} {'Pasados':<10} {'Futuros':<10}")
        print(f"{'-'*15} {'-'*10} {'-'*10} {'-'*10}")
        
        for stat in estadisticas:
            print(f"{stat['estado']:<15} {stat['total']:<10} {stat['pasados']:<10} {stat['futuros']:<10}")
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Error al actualizar horarios: {str(e)}")
        if conn:
            conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    ejecutar_actualizacion_horarios()
