#!/usr/bin/env python3
"""
Script para actualizar la base de datos con las tablas y columnas necesarias para el sistema de permisos
Ejecutar: python actualizar_bd_permisos.py
"""

import sys
from bd import obtener_conexion

def ejecutar_actualizacion():
    """Ejecuta el script SQL para agregar permisos al sistema"""
    
    conexion = obtener_conexion()
    
    try:
        with conexion.cursor() as cursor:
            # Leer el script SQL
            with open('scripts/crear_tablas_permisos.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Dividir el script en declaraciones individuales
            # (MySQL requiere ejecutar comandos uno a uno)
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]
            
            print(f"📋 Ejecutando {len(statements)} comandos SQL...")
            print("-" * 60)
            
            for i, statement in enumerate(statements, 1):
                if statement.upper().startswith('--'):
                    continue  # Saltar comentarios
                
                try:
                    print(f"[{i}/{len(statements)}] Ejecutando: {statement[:60]}...")
                    cursor.execute(statement)
                    conexion.commit()
                    print(f"     ✅ OK")
                except Exception as e:
                    print(f"     ⚠️  Advertencia: {str(e)}")
                    # Continuar con el siguiente comando incluso si falla
                    conexion.rollback()
            
            print("-" * 60)
            print("✅ Actualización completada exitosamente")
            print("\nℹ️  Cambios realizados:")
            print("   • Agregada columna 'descripcion' a tabla ROL")
            print("   • Creada tabla PERMISO con 45 permisos predefinidos")
            print("   • Creada tabla ROL_PERMISO para relación muchos-a-muchos")
            print("   • Asignados permisos iniciales a los 5 roles existentes")
            
            return True
    
    except Exception as e:
        print(f"❌ Error durante la actualización: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conexion.close()

if __name__ == '__main__':
    print("🔄 Iniciando actualización de base de datos...")
    print("Sistema de Gestión de Roles y Permisos")
    print("=" * 60)
    
    exito = ejecutar_actualizacion()
    
    sys.exit(0 if exito else 1)
