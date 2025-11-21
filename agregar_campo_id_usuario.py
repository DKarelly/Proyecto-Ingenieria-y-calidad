#!/usr/bin/env python3
"""
Script para agregar el campo id_usuario a la tabla NOTIFICACION
Ejecutar: python agregar_campo_id_usuario.py
"""

import sys
from bd import obtener_conexion

def ejecutar_actualizacion():
    """Ejecuta el script SQL para agregar id_usuario a NOTIFICACION"""
    
    conexion = obtener_conexion()
    
    try:
        with conexion.cursor() as cursor:
            # Verificar si el campo ya existe
            cursor.execute("DESCRIBE NOTIFICACION")
            columnas = [row['Field'] for row in cursor.fetchall()]
            
            if 'id_usuario' in columnas:
                print("[OK] El campo 'id_usuario' ya existe en la tabla NOTIFICACION")
                return True
            
            print("[INFO] Agregando campo 'id_usuario' a la tabla NOTIFICACION...")
            print("-" * 60)
            
            # Leer el script SQL
            with open('scripts/agregar_id_usuario_notificacion.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Dividir el script en declaraciones individuales
            statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
            
            print(f"[INFO] Ejecutando {len(statements)} comandos SQL...")
            
            for i, statement in enumerate(statements, 1):
                if not statement or statement.upper().startswith('--'):
                    continue
                
                try:
                    print(f"[{i}/{len(statements)}] Ejecutando: {statement[:80]}...")
                    cursor.execute(statement)
                    conexion.commit()
                    print(f"     [OK]")
                except Exception as e:
                    error_str = str(e).lower()
                    if 'duplicate column' in error_str or 'already exists' in error_str:
                        print(f"     [ADVERTENCIA] El campo ya existe, continuando...")
                        conexion.rollback()
                    else:
                        print(f"     [ERROR] {str(e)}")
                        conexion.rollback()
                        return False
            
            print("-" * 60)
            print("[OK] Actualizacion completada exitosamente")
            print("\nCambios realizados:")
            print("   - Agregada columna 'id_usuario' a tabla NOTIFICACION")
            print("   - Agregado indice 'idx_id_usuario'")
            print("   - Agregada foreign key constraint a tabla USUARIO")
            
            # Verificar que se agregó correctamente
            cursor.execute("DESCRIBE NOTIFICACION")
            columnas = [row['Field'] for row in cursor.fetchall()]
            if 'id_usuario' in columnas:
                print("\n[OK] Verificacion: El campo 'id_usuario' existe correctamente")
                return True
            else:
                print("\n[ERROR] Verificacion fallida: El campo no se agrego")
                return False
            
    except FileNotFoundError:
        print("[ERROR] No se encontro el archivo scripts/agregar_id_usuario_notificacion.sql")
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
    print("Agregar campo id_usuario a NOTIFICACION")
    print("=" * 60)
    
    exito = ejecutar_actualizacion()
    
    if exito:
        print("\nProceso completado exitosamente!")
        print("Ahora las notificaciones del medico deberian funcionar correctamente.")
    else:
        print("\nEl proceso fallo. Revisa los errores arriba.")
    
    sys.exit(0 if exito else 1)

