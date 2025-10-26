"""
Script para generar hash de contraseñas
Útil para crear usuarios administradores o actualizar contraseñas en la BD
"""

from werkzeug.security import generate_password_hash, check_password_hash

def generar_hash(contrasena):
    """Genera un hash de contraseña"""
    hash_generado = generate_password_hash(contrasena)
    print(f"\nContraseña: {contrasena}")
    print(f"Hash generado: {hash_generado}")
    print(f"\nInsert SQL:")
    print(f"UPDATE USUARIO SET contrasena = '{hash_generado}' WHERE id_usuario = [ID];")
    return hash_generado

def verificar_hash(contrasena, hash_almacenado):
    """Verifica si una contraseña coincide con un hash"""
    resultado = check_password_hash(hash_almacenado, contrasena)
    print(f"\n¿La contraseña '{contrasena}' coincide con el hash? {resultado}")
    return resultado

if __name__ == "__main__":
    print("=" * 60)
    print("GENERADOR DE HASH DE CONTRASEÑAS")
    print("=" * 60)
    
    # Generar hash para contraseña del administrador
    print("\n1. Generando hash para administrador...")
    admin_hash = generar_hash("admin123")
    
    # Verificar que funciona
    print("\n2. Verificando el hash generado...")
    verificar_hash("admin123", admin_hash)
    
    # Generar hash para una contraseña de ejemplo
    print("\n3. Ejemplo con otra contraseña...")
    ejemplo_hash = generar_hash("Password123!")
    
    print("\n" + "=" * 60)
    print("INSTRUCCIONES:")
    print("=" * 60)
    print("1. Copia el hash generado")
    print("2. Usa el SQL de actualización o insértalo directamente en la BD")
    print("3. Recuerda cambiar las contraseñas por defecto en producción")
    print("=" * 60)
