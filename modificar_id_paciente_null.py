#!/usr/bin/env python3
"""
Script para modificar la columna id_paciente en NOTIFICACION para permitir NULL
Ejecutar: python modificar_id_paciente_null.py
"""

import sys
from bd import obtener_conexion

def ejecutar_actualizacion():
    """Modifica la columna id_paciente para permitir NULL"""
    
    conexion = obtener_conexion()
    
    try:
        with conexion.cursor() as cursor:
            # Verificar el estado actual de la columna
            cursor.execute("DESCRIBE NOTIFICACION")
            columnas = cursor.fetchall()
            
            id_paciente_info = None
            for col in columnas:
                if col['Field'] == 'id_paciente':
                    id_paciente_info = col
                    break
            
            if id_paciente_info:
                print(f"[INFO] Estado actual de id_paciente:")
                print(f"   - Null: {id_paciente_info.get('Null', 'N/A')}")
                print(f"   - Type: {id_paciente_info.get('Type', 'N/A')}")
                
                if id_paciente_info.get('Null') == 'YES':
                    print("[OK] La columna 'id_paciente' ya permite NULL")
                    return True
            
            print("[INFO] Modificando columna 'id_paciente' para permitir NULL...")
            print("-" * 60)
            
            # Modificar la columna para permitir NULL
            sql = "ALTER TABLE NOTIFICACION MODIFY COLUMN id_paciente INT NULL"
            
            try:
                print(f"[1/1] Ejecutando: {sql}")
                cursor.execute(sql)
                conexion.commit()
                print(f"     [OK]")
                
                print("-" * 60)
                print("[OK] Actualizacion completada exitosamente")
                print("\nCambios realizados:")
                print("   - Columna 'id_paciente' ahora permite NULL")
                print("   - Las notificaciones de medico pueden crearse sin id_paciente")
                
                # Verificar que se modificó correctamente
                cursor.execute("DESCRIBE NOTIFICACION")
                columnas = cursor.fetchall()
                for col in columnas:
                    if col['Field'] == 'id_paciente':
                        if col.get('Null') == 'YES':
                            print("\n[OK] Verificacion: La columna 'id_paciente' ahora permite NULL")
                            return True
                        else:
                            print("\n[ERROR] Verificacion fallida: La columna aun no permite NULL")
                            return False
                
                return True
                
            except Exception as e:
                error_str = str(e).lower()
                if 'duplicate' in error_str or 'already' in error_str:
                    print(f"     [ADVERTENCIA] {str(e)}")
                    conexion.rollback()
                    return True
                else:
                    print(f"     [ERROR] {str(e)}")
                    conexion.rollback()
                    return False
            
    except Exception as e:
        print(f"[ERROR] Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conexion.close()

if __name__ == '__main__':
    import io
    import sys
    # Configurar stdout para UTF-8 en Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("Iniciando actualizacion de base de datos...")
    print("Modificar columna id_paciente para permitir NULL")
    print("=" * 60)
    
    exito = ejecutar_actualizacion()
    
    if exito:
        print("\nProceso completado exitosamente!")
        print("Ahora las notificaciones del medico deberian funcionar correctamente.")
    else:
        print("\nEl proceso fallo. Revisa los errores arriba.")
    
    sys.exit(0 if exito else 1)

