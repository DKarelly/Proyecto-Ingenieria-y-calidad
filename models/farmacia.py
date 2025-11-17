from bd import obtener_conexion
from datetime import date, time

def _get_cursor(conexion):
    """
    Devuelve un cursor que intenta usar diccionarios; si el conector no soporta
    cursor(dictionary=True) devuelve cursor normal y manejamos la conversión.
    """
    try:
        return conexion.cursor(dictionary=True)
    except TypeError:
        return conexion.cursor()

def _rows_to_dicts(cursor, rows):
    """Convierte filas en tuplas a diccionarios usando cursor.description"""
    if not rows:
        return []
    # Si ya son dicts, devolver tal cual
    if isinstance(rows[0], dict):
        return rows
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in rows]

class Medicamento:
    @staticmethod
    def listar():
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                # Luego, obtener la lista actualizada
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                        DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                        DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
                    FROM MEDICAMENTO
                    ORDER BY nombre
                """)
                rows = cursor.fetchall()
                print(f"DEBUG: {len(rows)} medicamentos encontrados") 
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_medicamento):
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
                    FROM MEDICAMENTO
                    WHERE id_medicamento = %s
                """, (id_medicamento,))
                row = cursor.fetchone()
                if row is None:
                    return None
                # fetchone puede devolver tuple o dict
                return _rows_to_dicts(cursor, [row])[0]
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def crear(nombre, descripcion, stock, fecha_vencimiento):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            try:
                cursor.execute("""
                    INSERT INTO MEDICAMENTO (nombre, descripcion, stock, fecha_registro, fecha_vencimiento)
                    VALUES (%s, %s, %s, CURDATE(), %s)
                """, (nombre, descripcion, stock, fecha_vencimiento))
                conexion.commit()
                return {'id_medicamento': cursor.lastrowid}
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_medicamento, nombre, descripcion, stock, fecha_vencimiento):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            try:
                cursor.execute("""
                    UPDATE MEDICAMENTO
                    SET nombre = %s, descripcion = %s, stock = %s, fecha_vencimiento = %s
                    WHERE id_medicamento = %s
                """, (nombre, descripcion, stock, fecha_vencimiento, id_medicamento))
                conexion.commit()
                return {'modified_rows': cursor.rowcount}
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def buscar(termino):
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                like = f'%{termino}%'
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           fecha_registro, fecha_vencimiento
                    FROM MEDICAMENTO
                    WHERE nombre LIKE %s
                    ORDER BY nombre
                    LIMIT 10
                """, (like,))
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def obtener_recientes(limite=5):
        """Obtiene los medicamentos más recientes registrados"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento,
                           stock as cantidad
                    FROM MEDICAMENTO
                    ORDER BY fecha_registro DESC
                    LIMIT %s
                """, (limite,))
                rows = cursor.fetchall()
                print(f"DEBUG obtener_recientes: {len(rows)} medicamentos encontrados")
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_vencer(dias=30, limite=None):
        """Obtiene medicamentos próximos a vencer en los próximos X días"""
        from datetime import date, timedelta
        fecha_limite = date.today() + timedelta(days=dias)

        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                query = """
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento,
                           DATEDIFF(fecha_vencimiento, CURDATE()) as dias_para_vencer
                    FROM MEDICAMENTO
                    WHERE fecha_vencimiento <= %s AND fecha_vencimiento >= CURDATE()
                    ORDER BY fecha_vencimiento ASC
                """
                params = [fecha_limite]

                if limite:
                    query += " LIMIT %s"
                    params.append(limite)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()



    @staticmethod
    def obtener_recibidos_hoy():
        """Obtiene los medicamentos recibidos hoy"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
                    FROM MEDICAMENTO
                    WHERE DATE(fecha_registro) = CURDATE()
                    ORDER BY fecha_registro DESC
                """)
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def obtener_ingresos_recientes(limite=10):
        """Obtiene los medicamentos registrados en los últimos 7 días"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_vencimiento, '%%d/%%m/%%Y') as fecha_vencimiento,
                           stock as cantidad,
                           DATE_FORMAT(fecha_registro, '%%d/%%m/%%Y') as fecha_ingreso
                    FROM MEDICAMENTO
                    WHERE fecha_registro >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                    ORDER BY fecha_registro DESC
                    LIMIT %s
                """, (limite,))
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def listar_con_detalles():
        """Obtiene todos los medicamentos con detalles adicionales"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento,
                           DATEDIFF(fecha_vencimiento, CURDATE()) as dias_para_vencer
                    FROM MEDICAMENTO
                    ORDER BY nombre
                """)
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def obtener_vencidos():
        """Obtiene medicamentos que ya han vencido"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento,
                           DATEDIFF(CURDATE(), fecha_vencimiento) as dias_vencido
                    FROM MEDICAMENTO
                    WHERE fecha_vencimiento < CURDATE()
                    ORDER BY fecha_vencimiento ASC
                """)
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def obtener_stock_bajo(umbral=10):
        """Obtiene medicamentos con stock bajo (por defecto menos de 10 unidades)"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
                    FROM MEDICAMENTO
                    WHERE stock <= %s
                    ORDER BY stock ASC
                """, (umbral,))
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def retirar(id_medicamento):
        """Retira un medicamento del inventario (lo marca como retirado o elimina)"""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            try:
                # Verificar que el medicamento existe
                cursor.execute("SELECT id_medicamento FROM MEDICAMENTO WHERE id_medicamento = %s", (id_medicamento,))
                if not cursor.fetchone():
                    return {'error': 'Medicamento no encontrado'}

                # Eliminar el medicamento del inventario
                cursor.execute("DELETE FROM MEDICAMENTO WHERE id_medicamento = %s", (id_medicamento,))
                conexion.commit()
                return {'success': True, 'message': 'Medicamento retirado del inventario'}
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()



class Paciente:
    @staticmethod
    def buscar(termino):
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_paciente, nombres, apellidos
                    FROM PACIENTE
                    WHERE nombres LIKE %s OR apellidos LIKE %s
                    LIMIT 10
                """, (f'%{termino}%', f'%{termino}%'))
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

class Empleado:
    @staticmethod
    def buscar(termino):
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT e.id_empleado, e.nombres, e.apellidos
                    FROM EMPLEADO e
                    WHERE e.nombres LIKE %s OR e.apellidos LIKE %s
                    LIMIT 10
                """, (f'%{termino}%', f'%{termino}%'))
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()
