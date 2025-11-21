#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script temporal para asociar el usuario dante@gmail.com a un empleado recepcionista
"""

from bd import obtener_conexion

def asociar_dante_empleado():
    """Asocia el usuario dante@gmail.com a un empleado recepcionista"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # 1. Obtener el id_usuario de dante@gmail.com
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s", ('dante@gmail.com',))
            usuario = cursor.fetchone()
            
            if not usuario:
                print("❌ Error: No se encontró el usuario dante@gmail.com")
                return False
            
            id_usuario = usuario['id_usuario']
            print(f"✅ Usuario encontrado: id_usuario = {id_usuario}")
            
            # 2. Verificar si ya existe un empleado con ese id_usuario
            cursor.execute("SELECT id_empleado, nombres, apellidos, id_rol FROM EMPLEADO WHERE id_usuario = %s", (id_usuario,))
            empleado_existente = cursor.fetchone()
            
            if empleado_existente:
                print(f"⚠️  Ya existe un empleado asociado:")
                print(f"   ID Empleado: {empleado_existente['id_empleado']}")
                print(f"   Nombre: {empleado_existente['nombres']} {empleado_existente['apellidos']}")
                print(f"   Rol: {empleado_existente['id_rol']}")
                
                # Si ya es recepcionista (id_rol = 3), no hacer nada
                if empleado_existente['id_rol'] == 3:
                    print("✅ El empleado ya es recepcionista. No se necesita hacer cambios.")
                    return True
                else:
                    # Actualizar el rol a recepcionista
                    print(f"🔄 Actualizando rol a recepcionista (id_rol = 3)...")
                    cursor.execute("UPDATE EMPLEADO SET id_rol = 3 WHERE id_empleado = %s", (empleado_existente['id_empleado'],))
                    conexion.commit()
                    print("✅ Rol actualizado exitosamente")
                    return True
            
            # 3. Buscar un empleado recepcionista sin usuario asociado o crear uno nuevo
            cursor.execute("""
                SELECT id_empleado, nombres, apellidos 
                FROM EMPLEADO 
                WHERE id_rol = 3 AND id_usuario IS NULL 
                LIMIT 1
            """)
            empleado_sin_usuario = cursor.fetchone()
            
            if empleado_sin_usuario:
                # Asociar el empleado existente al usuario
                print(f"🔄 Asociando empleado existente al usuario...")
                print(f"   Empleado: {empleado_sin_usuario['nombres']} {empleado_sin_usuario['apellidos']}")
                cursor.execute(
                    "UPDATE EMPLEADO SET id_usuario = %s WHERE id_empleado = %s",
                    (id_usuario, empleado_sin_usuario['id_empleado'])
                )
                conexion.commit()
                print("✅ Empleado asociado exitosamente")
                return True
            else:
                # Crear un nuevo empleado recepcionista
                print("🆕 Creando nuevo empleado recepcionista...")
                from datetime import date
                fecha_nacimiento = date(1990, 1, 1)  # Fecha temporal
                
                # Obtener un distrito disponible (usar el primero disponible)
                cursor.execute("SELECT id_distrito FROM DISTRITO LIMIT 1")
                distrito = cursor.fetchone()
                id_distrito = distrito['id_distrito'] if distrito else None
                
                cursor.execute("""
                    INSERT INTO EMPLEADO (nombres, apellidos, documento_identidad, sexo, fecha_nacimiento, estado, id_usuario, id_rol, id_distrito)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    'Dante',  # nombres
                    'Cabrera',  # apellidos
                    '00000000',  # documento_identidad (temporal)
                    'M',  # sexo
                    fecha_nacimiento,  # fecha_nacimiento
                    'Activo',  # estado
                    id_usuario,  # id_usuario
                    3,  # id_rol (Recepcionista)
                    id_distrito  # id_distrito
                ))
                conexion.commit()
                id_empleado = cursor.lastrowid
                print(f"✅ Empleado recepcionista creado exitosamente")
                print(f"   ID Empleado: {id_empleado}")
                print(f"   Nombre: Dante Cabrera")
                print(f"   Rol: Recepcionista (id_rol = 3)")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conexion.rollback()
        return False
    finally:
        conexion.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Script temporal: Asociar dante@gmail.com a empleado recepcionista")
    print("=" * 60)
    print()
    
    if asociar_dante_empleado():
        print()
        print("=" * 60)
        print("✅ Proceso completado exitosamente")
        print("=" * 60)
        print()
        print("Ahora puedes iniciar sesión con dante@gmail.com y serás")
        print("redirigido automáticamente al panel de recepcionista.")
    else:
        print()
        print("=" * 60)
        print("❌ El proceso falló. Revisa los errores arriba.")
        print("=" * 60)

