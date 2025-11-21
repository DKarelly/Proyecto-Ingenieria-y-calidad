"""
Script de prueba de login para debugging
"""
from models.usuario import Usuario
import sys

def test_login(correo, contrasena):
    print(f"\n{'='*60}")
    print(f"PRUEBA DE LOGIN")
    print(f"{'='*60}")
    print(f"Correo: {correo}")
    print(f"Contraseña: {'*' * len(contrasena)}")
    print()
    
    # 1. Verificar que el usuario existe
    print("1. Buscando usuario...")
    usuario = Usuario.obtener_por_correo(correo)
    
    if not usuario:
        print("❌ Usuario no encontrado")
        return
    
    print(f"✓ Usuario encontrado: ID {usuario['id_usuario']}")
    print(f"  - Correo: {usuario['correo']}")
    print(f"  - Estado: {usuario['estado']}")
    print(f"  - Tipo: {usuario.get('tipo_usuario', 'N/A')}")
    
    # 2. Verificar estado
    print("\n2. Verificando estado...")
    if usuario['estado'] != 'Activo':
        print(f"❌ Usuario inactivo (estado: '{usuario['estado']}')")
        return
    
    print("✓ Usuario activo")
    
    # 3. Verificar contraseña
    print("\n3. Verificando contraseña...")
    from werkzeug.security import check_password_hash
    
    if check_password_hash(usuario['contrasena'], contrasena):
        print("✓ Contraseña correcta")
    else:
        print("❌ Contraseña incorrecta")
        print(f"   Hash almacenado: {usuario['contrasena'][:50]}...")
        return
    
    # 4. Intentar login
    print("\n4. Intentando login completo...")
    resultado = Usuario.login(correo, contrasena)
    
    if 'error' in resultado:
        print(f"❌ Error en login: {resultado['error']}")
        return
    
    print("✅ LOGIN EXITOSO")
    print(f"   ID Usuario: {resultado['usuario']['id_usuario']}")
    print(f"   Nombre: {resultado['usuario']['nombre']}")
    print(f"   Tipo: {resultado['usuario']['tipo_usuario']}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        correo = sys.argv[1]
        contrasena = sys.argv[2]
    else:
        # Valores de prueba
        correo = input("Correo: ").strip()
        contrasena = input("Contraseña: ").strip()
    
    test_login(correo, contrasena)
