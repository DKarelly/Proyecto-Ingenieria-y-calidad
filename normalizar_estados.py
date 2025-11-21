"""
Script para normalizar los estados de usuario en la base de datos
Ejecutar: python normalizar_estados.py
"""
from bd import obtener_conexion

def normalizar_estados():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        
        # Ver estados actuales
        print("=== Estados ANTES de la normalización ===")
        cursor.execute("SELECT DISTINCT estado FROM USUARIO")
        estados = cursor.fetchall()
        for estado in estados:
            estado_val = estado['estado'] if isinstance(estado, dict) else estado[0]
            print(f"  - '{estado_val}'")
        
        # Contar por estado
        cursor.execute("SELECT estado, COUNT(*) as total FROM USUARIO GROUP BY estado")
        conteos = cursor.fetchall()
        print("\nConteo por estado:")
        for row in conteos:
            if isinstance(row, dict):
                print(f"  - '{row['estado']}': {row['total']} usuarios")
            else:
                print(f"  - '{row[0]}': {row[1]} usuarios")
        
        # Normalizar a 'Activo'
        print("\n=== Normalizando estados ===")
        cursor.execute("UPDATE USUARIO SET estado = 'Activo' WHERE LOWER(estado) = 'activo'")
        activos = cursor.rowcount
        print(f"✓ Actualizados {activos} registros a 'Activo'")
        
        # Normalizar a 'Inactivo'
        cursor.execute("UPDATE USUARIO SET estado = 'Inactivo' WHERE LOWER(estado) = 'inactivo'")
        inactivos = cursor.rowcount
        print(f"✓ Actualizados {inactivos} registros a 'Inactivo'")
        
        # Commit de cambios
        conexion.commit()
        print("\n✓ Cambios guardados en la base de datos")
        
        # Ver estados DESPUÉS
        print("\n=== Estados DESPUÉS de la normalización ===")
        cursor.execute("SELECT DISTINCT estado FROM USUARIO")
        estados = cursor.fetchall()
        for estado in estados:
            estado_val = estado['estado'] if isinstance(estado, dict) else estado[0]
            print(f"  - '{estado_val}'")
        
        # Conteo final
        cursor.execute("SELECT estado, COUNT(*) as total FROM USUARIO GROUP BY estado")
        conteos = cursor.fetchall()
        print("\nConteo final por estado:")
        for row in conteos:
            if isinstance(row, dict):
                print(f"  - '{row['estado']}': {row['total']} usuarios")
            else:
                print(f"  - '{row[0]}': {row[1]} usuarios")
        
        print("\n✅ Normalización completada exitosamente")
        print("   Solo se permiten: 'Activo' e 'Inactivo' (con mayúscula inicial)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    print("=" * 60)
    print("NORMALIZACIÓN DE ESTADOS DE USUARIO")
    print("=" * 60)
    normalizar_estados()
    print("=" * 60)
