import pymysql

# Configuración de la base de datos
db_config = {
    'host': 'tramway.proxy.rlwy.net',
    'port': 37865,
    'user': 'root',
    'password': 'voVwDDOsuNzPptZwHFRJtQViYgiMHCZf',
    'db': 'bd_calidad',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def add_fecha_entrega_column():
    """Agrega la columna fecha_entrega a la tabla DETALLE_MEDICAMENTO si no existe"""
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Verificar si la columna existe
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """, ('bd_calidad', 'DETALLE_MEDICAMENTO', 'fecha_entrega'))

        if cursor.fetchone():
            print("La columna fecha_entrega ya existe en la tabla DETALLE_MEDICAMENTO")
        else:
            # Agregar la columna
            cursor.execute("""
                ALTER TABLE DETALLE_MEDICAMENTO
                ADD COLUMN fecha_entrega DATE NOT NULL DEFAULT (CURDATE())
            """)
            conn.commit()
            print("Columna fecha_entrega agregada exitosamente a la tabla DETALLE_MEDICAMENTO")

    except Exception as e:
        print(f"Error al agregar la columna: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_fecha_entrega_column()
