"""
Script para actualizar los triggers de AUTORIZACION_PROCEDIMIENTO
Cambiar tipo_procedimiento por id_tipo_servicio
"""

from bd import obtener_conexion

def actualizar_triggers():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    try:
        print("🔧 Eliminando triggers antiguos...")
        
        # Eliminar triggers antiguos
        cursor.execute("DROP TRIGGER IF EXISTS trg_autorizacion_before_insert")
        print("✅ Trigger trg_autorizacion_before_insert eliminado")
        
        cursor.execute("DROP TRIGGER IF EXISTS trg_autorizacion_before_update")
        print("✅ Trigger trg_autorizacion_before_update eliminado")
        
        print("\n🔧 Creando nuevos triggers con id_tipo_servicio...")
        
        # Crear trigger BEFORE INSERT
        cursor.execute("""
            CREATE TRIGGER trg_autorizacion_before_insert
            BEFORE INSERT ON AUTORIZACION_PROCEDIMIENTO
            FOR EACH ROW
            BEGIN
              -- id_tipo_servicio = 4 es EXAMEN
              -- Los exámenes no deben tener especialidad requerida
              IF NEW.id_tipo_servicio = 4 AND NEW.id_especialidad_requerida IS NOT NULL THEN 
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Los exámenes no deben tener especialidad requerida';
              END IF;
            END
        """)
        print("✅ Trigger trg_autorizacion_before_insert creado")
        
        # Crear trigger BEFORE UPDATE
        cursor.execute("""
            CREATE TRIGGER trg_autorizacion_before_update
            BEFORE UPDATE ON AUTORIZACION_PROCEDIMIENTO
            FOR EACH ROW
            BEGIN
              -- id_tipo_servicio = 4 es EXAMEN
              -- Los exámenes no deben tener especialidad requerida
              IF NEW.id_tipo_servicio = 4 AND NEW.id_especialidad_requerida IS NOT NULL THEN 
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Los exámenes no deben tener especialidad requerida';
              END IF;
            END
        """)
        print("✅ Trigger trg_autorizacion_before_update creado")
        
        conn.commit()
        print("\n✅ Triggers actualizados exitosamente")
        
        # Verificar los nuevos triggers
        print("\n🔍 Verificando triggers actualizados...")
        cursor.execute("SHOW TRIGGERS WHERE `Table` = 'AUTORIZACION_PROCEDIMIENTO'")
        triggers = cursor.fetchall()
        
        for t in triggers:
            print(f"\n{'='*80}")
            print(f"Trigger: {t['Trigger']}")
            print(f"Timing: {t['Timing']}")
            print(f"Event: {t['Event']}")
            print(f"Statement: {t['Statement'][:100]}...")
            print('='*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    actualizar_triggers()
