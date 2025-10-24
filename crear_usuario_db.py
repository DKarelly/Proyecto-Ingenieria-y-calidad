"""
Script para crear usuarios con contraseña encriptada directamente en la base de datos
"""
from werkzeug.security import generate_password_hash
from bd import obtener_conexion

def crear_usuario_directo(correo, contrasena, tipo_usuario, id_paciente=None, id_empleado=None):
    """
    Crea un usuario directamente en la base de datos con contraseña encriptada
    
    Args:
        correo: Correo electrónico del usuario
        contrasena: Contraseña en texto plano (se encriptará automáticamente)
        tipo_usuario: 'paciente' o 'empleado'
        id_paciente: ID del paciente (requerido si tipo_usuario='paciente')
        id_empleado: ID del empleado (requerido si tipo_usuario='empleado')
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Encriptar contraseña
            contrasena_hash = generate_password_hash(contrasena)
            
            # Validaciones
            if tipo_usuario == 'paciente' and not id_paciente:
                print("❌ Error: Se requiere id_paciente para tipo 'paciente'")
                return False
            
            if tipo_usuario == 'empleado' and not id_empleado:
                print("❌ Error: Se requiere id_empleado para tipo 'empleado'")
                return False
            
            # Verificar si el correo ya existe
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo_electronico = %s", (correo,))
            if cursor.fetchone():
                print(f"❌ Error: El correo {correo} ya está registrado")
                return False
            
            # Insertar usuario
            sql = """
                INSERT INTO USUARIO (contrasena, correo_electronico, tipo_usuario, id_paciente, id_empleado)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (contrasena_hash, correo, tipo_usuario, id_paciente, id_empleado))
            conexion.commit()
            
            print(f"✅ Usuario creado exitosamente:")
            print(f"   - ID: {cursor.lastrowid}")
            print(f"   - Correo: {correo}")
            print(f"   - Tipo: {tipo_usuario}")
            print(f"   - Contraseña: {'*' * len(contrasena)} (encriptada)")
            
            return True
            
    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al crear usuario: {e}")
        return False
    finally:
        conexion.close()

def actualizar_contrasena(correo, nueva_contrasena):
    """
    Actualiza la contraseña de un usuario existente
    
    Args:
        correo: Correo del usuario
        nueva_contrasena: Nueva contraseña en texto plano
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar que el usuario existe
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo_electronico = %s", (correo,))
            usuario = cursor.fetchone()
            
            if not usuario:
                print(f"❌ Error: No existe usuario con correo {correo}")
                return False
            
            # Encriptar nueva contraseña
            contrasena_hash = generate_password_hash(nueva_contrasena)
            
            # Actualizar
            cursor.execute(
                "UPDATE USUARIO SET contrasena = %s WHERE correo_electronico = %s",
                (contrasena_hash, correo)
            )
            conexion.commit()
            
            print(f"✅ Contraseña actualizada para {correo}")
            return True
            
    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al actualizar contraseña: {e}")
        return False
    finally:
        conexion.close()

if __name__ == "__main__":
    print("=== GESTIÓN DE USUARIOS ===\n")
    
    # Ejemplo 1: Actualizar contraseña del admin existente
    print("1. Actualizando contraseña del admin...")
    actualizar_contrasena('admin@clinicaunion.com', 'admin123')
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 2: Crear un nuevo usuario empleado (descomenta y modifica según necesites)
    # print("2. Creando nuevo usuario empleado...")
    # crear_usuario_directo(
    #     correo='doctor@clinicaunion.com',
    #     contrasena='doctor123',
    #     tipo_usuario='empleado',
    #     id_empleado=2  # Cambia por un ID válido
    # )
    
    print("\n✅ Proceso completado")
