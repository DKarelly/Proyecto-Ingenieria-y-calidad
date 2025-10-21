import pymysql 

def obtener_conexion():
    return pymysql.connect(host='localhost',
                                port=3306,
                                user='root',
                                password='',
                                db='clinica_union')

try:
    conexion = obtener_conexion()
    if conexion.open: 
        print("✅ Conectado correctamente a MySQL")
    else:
        print("❌ No se pudo conectar a MySQL")
except Exception as e:
    print("❌ Error al conectar:", e)
finally:
    if 'conexion' in locals() and conexion.open:
        conexion.close()