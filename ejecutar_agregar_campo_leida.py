"""
Script para agregar el campo 'leida' a la tabla NOTIFICACION
Ejecuta las modificaciones necesarias en la base de datos
"""
from bd import obtener_conexion

def agregar_campo_leida():
    """Agrega los campos leida y fecha_leida a la tabla NOTIFICACION"""
    conexion = None
    try:
        conexion = obtener_conexion()
        if not conexion:
            print("❌ Error: No se pudo obtener la conexión a la base de datos")
            return False
        
        print("✅ Conexión a la base de datos establecida")
        
        with conexion.cursor() as cursor:
            # 1. Agregar columna 'leida'
            print("\n📝 Agregando columna 'leida'...")
            try:
                cursor.execute("""
                    ALTER TABLE NOTIFICACION 
                    ADD COLUMN leida BOOLEAN DEFAULT FALSE AFTER hora_envio
                """)
                print("✅ Columna 'leida' agregada exitosamente")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  La columna 'leida' ya existe")
                else:
                    raise
            
            # 2. Agregar columna 'fecha_leida'
            print("\n📝 Agregando columna 'fecha_leida'...")
            try:
                cursor.execute("""
                    ALTER TABLE NOTIFICACION 
                    ADD COLUMN fecha_leida DATETIME DEFAULT NULL AFTER leida
                """)
                print("✅ Columna 'fecha_leida' agregada exitosamente")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  La columna 'fecha_leida' ya existe")
                else:
                    raise
            
            # 3. Crear índice
            print("\n📝 Creando índice en 'leida'...")
            try:
                cursor.execute("""
                    CREATE INDEX idx_leida ON NOTIFICACION(leida)
                """)
                print("✅ Índice 'idx_leida' creado exitosamente")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("⚠️  El índice 'idx_leida' ya existe")
                else:
                    raise
            
            # Confirmar cambios
            conexion.commit()
            print("\n✅ Todos los cambios se han aplicado correctamente")
            
            # 4. Mostrar estructura actualizada
            print("\n📊 Estructura actualizada de la tabla NOTIFICACION:")
            cursor.execute("DESCRIBE NOTIFICACION")
            resultados = cursor.fetchall()
            
            print("\n{:<20} {:<15} {:<10} {:<5} {:<10}".format(
                "Campo", "Tipo", "Null", "Key", "Default"
            ))
            print("-" * 70)
            for row in resultados:
                print("{:<20} {:<15} {:<10} {:<5} {:<10}".format(
                    row.get('Field', ''),
                    row.get('Type', ''),
                    row.get('Null', ''),
                    row.get('Key', ''),
                    str(row.get('Default', ''))[:10]
                ))
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error al ejecutar el script: {str(e)}")
        import traceback
        traceback.print_exc()
        if conexion:
            try:
                conexion.rollback()
                print("↩️  Cambios revertidos (rollback)")
            except:
                pass
        return False
        
    finally:
        if conexion:
            try:
                conexion.close()
                print("\n🔌 Conexión cerrada")
            except:
                pass

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Ejecutando migración: Agregar campo 'leida' a NOTIFICACION")
    print("=" * 70)
    
    exito = agregar_campo_leida()
    
    print("\n" + "=" * 70)
    if exito:
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("\nPróximos pasos:")
        print("1. Reinicia la aplicación Flask")
        print("2. Crea una nueva reserva como paciente")
        print("3. Haz clic en las notificaciones para marcarlas como leídas")
        print("4. Observa cómo el badge se actualiza automáticamente")
    else:
        print("❌ MIGRACIÓN FALLÓ - Revisa los errores arriba")
    print("=" * 70)
