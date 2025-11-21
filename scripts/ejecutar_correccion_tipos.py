#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar la corrección de tipos de reserva
"""
import pymysql
import sys
from getpass import getpass

def ejecutar_script_sql(archivo_sql, host='localhost', usuario='root', base_datos='bd_calidad'):
    """Ejecuta un script SQL desde Python"""
    
    # Solicitar contraseña
    contrasena = getpass(f'Ingresa la contraseña de MySQL para {usuario}@{host}: ')
    
    try:
        # Conectar a la base de datos
        print(f"\n🔌 Conectando a {base_datos}...")
        conexion = pymysql.connect(
            host=host,
            user=usuario,
            password=contrasena,
            database=base_datos,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Conexión establecida\n")
        
        # Leer el archivo SQL
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            script_sql = f.read()
        
        # Separar las consultas por punto y coma
        consultas = [q.strip() for q in script_sql.split(';') if q.strip()]
        
        with conexion.cursor() as cursor:
            print(f"📄 Ejecutando {len(consultas)} consultas...\n")
            
            for i, consulta in enumerate(consultas, 1):
                # Ignorar comentarios y líneas vacías
                if consulta.startswith('--') or consulta.startswith('/*') or not consulta.strip():
                    continue
                
                try:
                    cursor.execute(consulta)
                    
                    # Si la consulta devuelve resultados, mostrarlos
                    if cursor.description:
                        resultados = cursor.fetchall()
                        if resultados:
                            # Mostrar encabezados
                            if isinstance(resultados[0], dict):
                                print("=" * 80)
                                for resultado in resultados:
                                    for clave, valor in resultado.items():
                                        print(f"{clave}: {valor}")
                                    print("-" * 80)
                            else:
                                for resultado in resultados:
                                    print(resultado)
                            print()
                    
                    # Confirmar los cambios después de cada consulta
                    conexion.commit()
                    
                except Exception as e:
                    print(f"❌ Error en consulta {i}: {str(e)}")
                    print(f"   Consulta: {consulta[:100]}...")
                    conexion.rollback()
        
        print("\n✅ Script ejecutado exitosamente")
        
    except pymysql.Error as e:
        print(f"❌ Error de MySQL: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {archivo_sql}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
    finally:
        if 'conexion' in locals():
            conexion.close()
            print("🔌 Conexión cerrada")

if __name__ == '__main__':
    archivo = 'scripts/corregir_tipos_reserva.sql'
    print("🔧 Corrección de tipos de RESERVA")
    print("=" * 80)
    ejecutar_script_sql(archivo)
