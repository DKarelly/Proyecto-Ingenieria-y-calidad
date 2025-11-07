"""
Script para ejecutar las actualizaciones de base de datos para roles y permisos
"""
import pymysql
from bd import obtener_conexion

def ejecutar_script_sql():
    """Ejecuta el script SQL para crear tablas de permisos"""
    print("\n" + "=" * 60)
    print("ACTUALIZACIÓN DE BASE DE DATOS - SISTEMA DE PERMISOS")
    print("=" * 60 + "\n")
    
    print("📄 Leyendo script SQL...")
    
    # Leer el archivo SQL
    try:
        with open('scripts/crear_tablas_permisos.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        print("✅ Script cargado correctamente\n")
    except FileNotFoundError:
        print("❌ ERROR: No se encontró el archivo 'scripts/crear_tablas_permisos.sql'")
        return False
    
    # Dividir en sentencias individuales
    sentencias = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"🚀 Ejecutando {len(sentencias)} comandos SQL...\n")
    
    print("📡 Conectando a la base de datos...")
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    print("✅ Conexión exitosa\n")
    
    ejecutados = 0
    advertencias = 0
    
    try:
        for i, sentencia in enumerate(sentencias, 1):
            try:
                cursor.execute(sentencia)
                ejecutados += 1
                
                # Mostrar progreso específico
                if 'ALTER TABLE' in sentencia.upper() and 'ROL' in sentencia.upper():
                    print(f"   [{i}/{len(sentencias)}] ✓ Columna 'descripcion' agregada a ROL")
                elif 'CREATE TABLE' in sentencia.upper() and 'PERMISO' in sentencia.upper() and 'ROL_PERMISO' not in sentencia.upper():
                    print(f"   [{i}/{len(sentencias)}] ✓ Tabla PERMISO creada")
                elif 'CREATE TABLE' in sentencia.upper() and 'ROL_PERMISO' in sentencia.upper():
                    print(f"   [{i}/{len(sentencias)}] ✓ Tabla ROL_PERMISO creada")
                elif 'UPDATE' in sentencia.upper() and 'ROL' in sentencia.upper():
                    print(f"   [{i}/{len(sentencias)}] ✓ Descripción de rol actualizada")
                elif 'INSERT INTO' in sentencia.upper() and 'PERMISO' in sentencia.upper() and 'ROL_PERMISO' not in sentencia.upper():
                    print(f"   [{i}/{len(sentencias)}] ✓ Permisos insertados")
                elif 'INSERT INTO' in sentencia.upper() and 'ROL_PERMISO' in sentencia.upper():
                    if 'SELECT 1' in sentencia:
                        print(f"   [{i}/{len(sentencias)}] ✓ Permisos asignados al Administrador")
                    elif 'SELECT 2' in sentencia:
                        print(f"   [{i}/{len(sentencias)}] ✓ Permisos asignados al Médico")
                    elif 'SELECT 3' in sentencia:
                        print(f"   [{i}/{len(sentencias)}] ✓ Permisos asignados al Recepcionista")
                    elif 'SELECT 4' in sentencia:
                        print(f"   [{i}/{len(sentencias)}] ✓ Permisos asignados al Farmacéutico")
                    elif 'SELECT 5' in sentencia:
                        print(f"   [{i}/{len(sentencias)}] ✓ Permisos asignados al Laboratorista")
                elif 'DROP TABLE' in sentencia.upper():
                    print(f"   [{i}/{len(sentencias)}] ✓ Tabla eliminada (preparación)")
                    
            except pymysql.Error as err:
                advertencias += 1
                error_msg = str(err)
                
                # Ignorar errores comunes de re-ejecución
                if "Duplicate column name" in error_msg:
                    print(f"   [{i}/{len(sentencias)}] ⚠ Columna ya existe, continuando...")
                elif "already exists" in error_msg:
                    print(f"   [{i}/{len(sentencias)}] ⚠ Tabla ya existe, continuando...")
                elif "Duplicate entry" in error_msg:
                    print(f"   [{i}/{len(sentencias)}] ⚠ Registro duplicado, continuando...")
                elif "Unknown table" in error_msg and "DROP TABLE" in sentencia.upper():
                    print(f"   [{i}/{len(sentencias)}] ⚠ Tabla no existe (normal en primera ejecución)")
                else:
                    print(f"   [{i}/{len(sentencias)}] ❌ Error: {err}")
                    # No lanzar excepción, continuar con el siguiente comando
        
        conexion.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ ACTUALIZACIÓN COMPLETADA")
        print(f"   Comandos ejecutados: {ejecutados}/{len(sentencias)}")
        if advertencias > 0:
            print(f"   Advertencias: {advertencias}")
        print("=" * 60 + "\n")
        
        # Verificar resultados
        print("🔍 Verificando instalación...\n")
        
        # Verificar tabla PERMISO
        cursor.execute("SELECT COUNT(*) as total FROM PERMISO")
        result = cursor.fetchone()
        total_permisos = result['total'] if isinstance(result, dict) else result[0]
        print(f"   ✓ Tabla PERMISO: {total_permisos} permisos registrados")
        
        # Verificar tabla ROL_PERMISO
        cursor.execute("SELECT COUNT(*) as total FROM ROL_PERMISO")
        result = cursor.fetchone()
        total_asignaciones = result['total'] if isinstance(result, dict) else result[0]
        print(f"   ✓ Tabla ROL_PERMISO: {total_asignaciones} asignaciones")
        
        # Verificar roles con permisos
        cursor.execute("""
            SELECT r.nombre, COUNT(rp.id_permiso) as permisos
            FROM ROL r
            LEFT JOIN ROL_PERMISO rp ON r.id_rol = rp.id_rol
            GROUP BY r.id_rol, r.nombre
            ORDER BY r.id_rol
        """)
        
        print("\n   Permisos por rol:")
        for row in cursor.fetchall():
            if isinstance(row, dict):
                print(f"      • {row['nombre']}: {row['permisos']} permisos")
            else:
                print(f"      • {row[0]}: {row[1]} permisos")
        
        print("\n" + "=" * 60)
        print("🎉 ¡LISTO! El sistema de permisos está instalado.")
        print("   Ahora puedes acceder a /cuentas/gestionar-roles-permisos")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        conexion.rollback()
        print("\n" + "=" * 60)
        print(f"❌ ERROR CRÍTICO: {e}")
        print("=" * 60 + "\n")
        return False
        
    finally:
        cursor.close()
        conexion.close()
        print("📡 Conexión cerrada\n")

if __name__ == "__main__":
    print("\n⚠️  IMPORTANTE: Este script actualizará la base de datos CLINICA")
    print("   Se agregarán las tablas necesarias para el sistema de permisos.\n")
    
    respuesta = input("¿Deseas continuar? (S/N): ").strip().upper()
    
    if respuesta == 'S':
        exito = ejecutar_script_sql()
        
        if exito:
            print("\n✅ Actualización completada exitosamente.")
            print("   Puedes iniciar la aplicación y usar /cuentas/gestionar-roles-permisos\n")
        else:
            print("\n❌ La actualización falló. Revisa los errores anteriores.\n")
    else:
        print("\n⚠️  Actualización cancelada.\n")
    
    input("Presiona ENTER para salir...")

