"""
Script para actualizar las contraseñas de todos los médicos (id_rol = 2) a "Doctor123"
Este script se conecta a la base de datos y actualiza las contraseñas de forma segura.
"""

from werkzeug.security import generate_password_hash
import pymysql
import pymysql.cursors
import os

def get_db_connection():
    """Obtiene la conexión a la base de datos usando PyMySQL"""
    try:
        connection = pymysql.connect(
            host='interchange.proxy.rlwy.net',
            port=27536,
            user='root',
            password='lkzttuSAneuJecLBIWToEmnXaILvqDYI',
            db='bd_finalcalidad',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def generar_hash_password(password):
    """Genera el hash de la contraseña usando scrypt (método de werkzeug)"""
    return generate_password_hash(password, method='scrypt')

def actualizar_passwords_doctores():
    """Actualiza las contraseñas de todos los usuarios con id_rol = 2 (Médicos)"""
    
    nueva_password = "Doctor123"
    password_hash = generar_hash_password(nueva_password)
    
    print("=" * 60)
    print("ACTUALIZADOR DE CONTRASEÑAS PARA MÉDICOS")
    print("=" * 60)
    print(f"\nNueva contraseña: {nueva_password}")
    print(f"Hash generado: {password_hash[:50]}...")
    print()
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo establecer la conexión a la base de datos.")
        print("\nPuedes ejecutar este SQL manualmente:")
        print("-" * 60)
        print(f"""
UPDATE USUARIO u
INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
SET u.contrasena = '{password_hash}'
WHERE e.id_rol = 2;
        """)
        return False
    
    cursor = None
    try:
        cursor = connection.cursor()  # PyMySQL ya usa DictCursor por defecto según la configuración
        
        # Primero, obtener la lista de médicos que serán actualizados
        query_select = """
            SELECT 
                u.id_usuario,
                u.correo,
                e.nombres,
                e.apellidos,
                esp.nombre as especialidad
            FROM USUARIO u
            INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
            LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
            WHERE e.id_rol = 2
            ORDER BY e.id_empleado
        """
        
        cursor.execute(query_select)
        medicos = cursor.fetchall()
        
        print(f"Se encontraron {len(medicos)} médicos para actualizar:")
        print("-" * 60)
        
        for medico in medicos:
            print(f"  - {medico['nombres']} {medico['apellidos']} ({medico['correo']})")
            if medico['especialidad']:
                print(f"    Especialidad: {medico['especialidad']}")
        
        print("-" * 60)
        
        # Confirmar antes de actualizar
        respuesta = input("\n¿Desea continuar con la actualización? (s/n): ")
        
        if respuesta.lower() != 's':
            print("Operación cancelada.")
            return False
        
        # Ejecutar la actualización
        query_update = """
            UPDATE USUARIO u
            INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
            SET u.contrasena = %s
            WHERE e.id_rol = 2
        """
        
        cursor.execute(query_update, (password_hash,))
        connection.commit()
        
        print(f"\n✓ Se actualizaron {cursor.rowcount} registros exitosamente.")
        print(f"✓ Nueva contraseña para todos los médicos: {nueva_password}")
        
        return True
        
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("\nConexión a la base de datos cerrada.")

def generar_sql_manual():
    """Genera el SQL para ejecutar manualmente si no hay conexión"""
    nueva_password = "Doctor123"
    password_hash = generar_hash_password(nueva_password)
    
    sql = f"""
-- ==============================================================
-- SQL GENERADO AUTOMÁTICAMENTE
-- Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Contraseña: Doctor123
-- ==============================================================

USE bd_calidad;

-- Actualizar contraseñas de todos los médicos (id_rol = 2)
UPDATE USUARIO u
INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
SET u.contrasena = '{password_hash}'
WHERE e.id_rol = 2;

-- Verificar la actualización
SELECT 
    e.id_empleado,
    CONCAT(e.nombres, ' ', e.apellidos) as nombre_completo,
    u.correo,
    'Doctor123' as nueva_contrasena
FROM EMPLEADO e
INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
WHERE e.id_rol = 2
ORDER BY e.id_empleado;
"""
    
    # Guardar en archivo
    with open('sql_actualizar_passwords_doctores_generado.sql', 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print("=" * 60)
    print("SQL GENERADO")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    print("\nEl SQL ha sido guardado en: sql_actualizar_passwords_doctores_generado.sql")
    
    return sql

if __name__ == "__main__":
    print("\n¿Qué desea hacer?")
    print("1. Actualizar contraseñas directamente en la base de datos")
    print("2. Generar SQL para ejecutar manualmente")
    
    opcion = input("\nSeleccione una opción (1 o 2): ")
    
    if opcion == "1":
        actualizar_passwords_doctores()
    elif opcion == "2":
        generar_sql_manual()
    else:
        print("Opción no válida. Generando SQL por defecto...")
        generar_sql_manual()
