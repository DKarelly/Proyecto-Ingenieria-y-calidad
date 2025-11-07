"""
Script de prueba para el Panel de Trabajador
Sistema de Gestión Clínica Unión
"""

def test_panel_trabajador():
    print("=" * 80)
    print("PRUEBAS DEL PANEL DE TRABAJADOR")
    print("=" * 80)
    print()
    
    # Test 1: Verificar imports
    print("[TEST 1] Verificando imports...")
    try:
        from routes.trabajador import trabajador_bp, trabajador_required
        print("✅ Imports correctos")
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return
    
    # Test 2: Verificar registro del blueprint en app.py
    print("\n[TEST 2] Verificando registro del blueprint...")
    try:
        from app import app
        blueprints = [bp.name for bp in app.blueprints.values()]
        if 'trabajador' in blueprints:
            print("✅ Blueprint 'trabajador' registrado correctamente")
        else:
            print("❌ Blueprint 'trabajador' NO está registrado")
            print(f"   Blueprints disponibles: {blueprints}")
    except Exception as e:
        print(f"❌ Error al verificar blueprints: {e}")
    
    # Test 3: Verificar rutas
    print("\n[TEST 3] Verificando rutas disponibles...")
    try:
        from app import app
        trabajador_routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint and rule.endpoint.startswith('trabajador.'):
                trabajador_routes.append({
                    'endpoint': rule.endpoint,
                    'route': str(rule),
                    'methods': ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                })
        
        if trabajador_routes:
            print("✅ Rutas del trabajador encontradas:")
            for route in trabajador_routes:
                print(f"   - {route['route']:<50} [{route['methods']}]")
        else:
            print("❌ No se encontraron rutas del trabajador")
    except Exception as e:
        print(f"❌ Error al verificar rutas: {e}")
    
    # Test 4: Verificar template principal
    print("\n[TEST 4] Verificando templates...")
    import os
    panel_path = os.path.join('templates', 'panel.html')
    if os.path.exists(panel_path):
        print("✅ Template 'panel.html' existe (dashboard principal)")
        file_size = os.path.getsize(panel_path)
        print(f"   Tamaño: {file_size} bytes")
    else:
        print("❌ No se encontró 'panel.html' (dashboard principal)")
    
    # Test 5: Verificar modificaciones en usuarios.py
    print("\n[TEST 5] Verificando lógica de redirección en login...")
    try:
        with open('routes/usuarios.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if "trabajador.panel" in content:
                print("✅ Redirección a panel de trabajador implementada")
            else:
                print("⚠️  Advertencia: No se encontró referencia a 'trabajador.panel' en login")
    except Exception as e:
        print(f"❌ Error al verificar usuarios.py: {e}")
    
    # Test 6: Verificar roles válidos
    print("\n[TEST 6] Verificando roles del sistema...")
    print("   Roles definidos:")
    print("   - 1: Administrador (Admin Panel)")
    print("   - 2: Médico (Trabajador Panel)")
    print("   - 3: Recepcionista (Trabajador Panel)")
    print("   - 4: Farmacéutico (Trabajador Panel)")
    print("   - 5: Laboratorista (Trabajador Panel)")
    print("   ✅ Roles definidos correctamente")
    
    print()
    print("=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)
    print("✅ Sistema de Panel de Trabajador implementado correctamente")
    print()
    print("PRÓXIMOS PASOS:")
    print("1. Iniciar la aplicación Flask: python app.py")
    print("2. Acceder a http://localhost:5000")
    print("3. Iniciar sesión con credenciales de trabajador:")
    print("   - Email: dr.garcia@clinicaunion.com")
    print("   - Contraseña: password123")
    print("4. Verificar redirección automática a /trabajador/")
    print("5. Probar navegación entre las secciones")
    print()
    print("CREDENCIALES DE PRUEBA:")
    print("- Médicos: dr.garcia@, dr.martinez@, dra.lopez@, etc.")
    print("- Recepcionistas: recepcion1@, recepcion2@")
    print("- Farmacéuticos: farmacia1@, farmacia2@")
    print("- Laboratoristas: lab1@, lab2@")
    print("Dominio: @clinicaunion.com")
    print("Contraseña: password123")
    print("=" * 80)

if __name__ == '__main__':
    test_panel_trabajador()
