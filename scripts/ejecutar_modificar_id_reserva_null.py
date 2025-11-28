#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar la modificación de la tabla NOTIFICACION
para permitir NULL en id_reserva
"""
import pymysql
import sys
import os

# Agregar el directorio raíz al path para importar bd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bd import obtener_conexion

def ejecutar_modificacion():
    """Ejecuta la modificación de la tabla NOTIFICACION"""
    
    print("=" * 60)
    print("MODIFICACION DE TABLA NOTIFICACION")
    print("=" * 60)
    print("\nEste script modificara la tabla NOTIFICACION para permitir")
    print("que id_reserva sea NULL (necesario para notificaciones sin reserva).\n")
    
    # Obtener conexión
    try:
        print("Conectando a la base de datos...")
        conexion = obtener_conexion()
        print("OK - Conexion establecida\n")
    except Exception as e:
        print(f"ERROR - Error al conectar: {e}")
        return False
    
    try:
        with conexion.cursor() as cursor:
            # Paso 1: Intentar eliminar la foreign key constraint si existe
            print("[1/3] Verificando y eliminando constraint existente...")
            try:
                cursor.execute("ALTER TABLE NOTIFICACION DROP FOREIGN KEY NOTIFICACION_ibfk_2")
                print("   OK - Constraint eliminada correctamente")
            except Exception as e:
                error_str = str(e).lower()
                if "doesn't exist" in error_str or "unknown key" in error_str or "errno: 1091" in error_str:
                    print("   ADVERTENCIA - La constraint no existe (esto es normal)")
                else:
                    print(f"   ADVERTENCIA - No se pudo eliminar constraint: {str(e)[:50]}...")
            
            # Paso 2: Modificar la columna para permitir NULL
            print("\n[2/3] Modificando columna id_reserva para permitir NULL...")
            try:
                cursor.execute("ALTER TABLE NOTIFICACION MODIFY COLUMN id_reserva INT NULL")
                print("   OK - Columna modificada correctamente")
            except Exception as e:
                print(f"   ERROR - No se pudo modificar la columna: {e}")
                raise
            
            # Paso 3: Recrear la foreign key constraint
            print("\n[3/3] Recreando foreign key constraint...")
            try:
                cursor.execute("""
                    ALTER TABLE NOTIFICACION 
                    ADD CONSTRAINT NOTIFICACION_ibfk_2 
                    FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva)
                """)
                print("   OK - Constraint recreada correctamente")
            except Exception as e:
                error_str = str(e).lower()
                if "duplicate key name" in error_str or "errno: 1062" in error_str:
                    print("   ADVERTENCIA - La constraint ya existe (esto es normal)")
                else:
                    print(f"   ERROR - No se pudo recrear constraint: {e}")
                    raise
        
        # Confirmar cambios
        conexion.commit()
        print("\n" + "=" * 60)
        print("OK - MODIFICACION COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        print("\nLa tabla NOTIFICACION ahora permite NULL en id_reserva.")
        print("Las notificaciones de derivacion de operacion deberian funcionar correctamente.\n")
        return True
        
    except Exception as e:
        conexion.rollback()
        print(f"\nERROR - Error al ejecutar la modificacion: {e}")
        print("\nDetalles del error:")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conexion.close()

if __name__ == "__main__":
    print()
    # Si hay un argumento '--yes' o '-y', ejecutar sin confirmar
    if len(sys.argv) > 1 and sys.argv[1] in ['--yes', '-y', '--confirm']:
        print("Ejecutando modificacion sin confirmacion...\n")
        exito = ejecutar_modificacion()
    else:
        try:
            respuesta = input("Deseas continuar con la modificacion? (s/n): ").lower().strip()
            
            if respuesta in ['s', 'si', 'si', 'y', 'yes']:
                print()
                exito = ejecutar_modificacion()
            else:
                print("\nERROR - Operacion cancelada por el usuario.")
                sys.exit(0)
        except EOFError:
            # Si no hay input disponible (entorno no interactivo), ejecutar directamente
            print("Entorno no interactivo detectado. Ejecutando modificacion...\n")
            exito = ejecutar_modificacion()
    
    if exito:
        print("OK - Proceso completado exitosamente.")
        sys.exit(0)
    else:
        print("ERROR - El proceso fallo. Por favor, revisa los errores arriba.")
        sys.exit(1)

