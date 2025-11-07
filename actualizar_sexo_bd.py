"""
Script para actualizar los valores de sexo en la base de datos
De 'M'/'F' a 'Masculino'/'Femenino'
"""

import bd

def actualizar_sexo():
    """Actualiza todos los registros de sexo en PACIENTE y EMPLEADO"""
    
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()
    
    try:
        print("=" * 60)
        print("ACTUALIZANDO VALORES DE SEXO EN LA BASE DE DATOS")
        print("=" * 60)
        
        # Verificar registros actuales en PACIENTE
        cursor.execute("SELECT COUNT(*) as total FROM PACIENTE WHERE sexo = 'M'")
        result = cursor.fetchone()
        pacientes_m = result['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM PACIENTE WHERE sexo = 'F'")
        result = cursor.fetchone()
        pacientes_f = result['total']
        
        print(f"\n📊 ESTADO ACTUAL - PACIENTE:")
        print(f"   • Pacientes con sexo 'M': {pacientes_m}")
        print(f"   • Pacientes con sexo 'F': {pacientes_f}")
        
        # Verificar registros actuales en EMPLEADO
        cursor.execute("SELECT COUNT(*) as total FROM EMPLEADO WHERE sexo = 'M'")
        result = cursor.fetchone()
        empleados_m = result['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM EMPLEADO WHERE sexo = 'F'")
        result = cursor.fetchone()
        empleados_f = result['total']
        
        print(f"\n📊 ESTADO ACTUAL - EMPLEADO:")
        print(f"   • Empleados con sexo 'M': {empleados_m}")
        print(f"   • Empleados con sexo 'F': {empleados_f}")
        
        # Actualizar PACIENTE
        if pacientes_m > 0:
            print(f"\n🔄 Actualizando {pacientes_m} pacientes de 'M' a 'Masculino'...")
            cursor.execute("UPDATE PACIENTE SET sexo = 'Masculino' WHERE sexo = 'M'")
            print(f"   ✅ Pacientes actualizados: {cursor.rowcount}")
        
        if pacientes_f > 0:
            print(f"🔄 Actualizando {pacientes_f} pacientes de 'F' a 'Femenino'...")
            cursor.execute("UPDATE PACIENTE SET sexo = 'Femenino' WHERE sexo = 'F'")
            print(f"   ✅ Pacientes actualizados: {cursor.rowcount}")
        
        # Actualizar EMPLEADO
        if empleados_m > 0:
            print(f"\n🔄 Actualizando {empleados_m} empleados de 'M' a 'Masculino'...")
            cursor.execute("UPDATE EMPLEADO SET sexo = 'Masculino' WHERE sexo = 'M'")
            print(f"   ✅ Empleados actualizados: {cursor.rowcount}")
        
        if empleados_f > 0:
            print(f"🔄 Actualizando {empleados_f} empleados de 'F' a 'Femenino'...")
            cursor.execute("UPDATE EMPLEADO SET sexo = 'Femenino' WHERE sexo = 'F'")
            print(f"   ✅ Empleados actualizados: {cursor.rowcount}")
        
        # Confirmar cambios
        conexion.commit()
        
        # Verificar estado final
        cursor.execute("SELECT COUNT(*) as total FROM PACIENTE WHERE sexo = 'Masculino'")
        result = cursor.fetchone()
        pacientes_masculino = result['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM PACIENTE WHERE sexo = 'Femenino'")
        result = cursor.fetchone()
        pacientes_femenino = result['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM EMPLEADO WHERE sexo = 'Masculino'")
        result = cursor.fetchone()
        empleados_masculino = result['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM EMPLEADO WHERE sexo = 'Femenino'")
        result = cursor.fetchone()
        empleados_femenino = result['total']
        
        print("\n" + "=" * 60)
        print("✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        print(f"\n📊 ESTADO FINAL:")
        print(f"\n   PACIENTE:")
        print(f"      • Masculino: {pacientes_masculino}")
        print(f"      • Femenino: {pacientes_femenino}")
        print(f"\n   EMPLEADO:")
        print(f"      • Masculino: {empleados_masculino}")
        print(f"      • Femenino: {empleados_femenino}")
        
        print("\n✅ Todos los registros han sido actualizados correctamente")
        print("=" * 60)
        
    except Exception as e:
        conexion.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conexion.close()

if __name__ == '__main__':
    actualizar_sexo()
