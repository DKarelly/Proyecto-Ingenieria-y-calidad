from bd import obtener_conexion
from datetime import date

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
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
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
                           DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
                    FROM MEDICAMENTO
                    WHERE nombre LIKE %s OR descripcion LIKE %s
                    ORDER BY nombre
                """, (like, like))
                rows = cursor.fetchall()
                return _rows_to_dicts(cursor, rows)
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

class DetalleMedicamento:
    @staticmethod
    def registrar_entrega(id_empleado, id_paciente, id_medicamento, cantidad):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            try:
                # Bloqueo y verificación de stock
                # Dependiendo del conector, FOR UPDATE funciona si la transacción está activa.
                cursor.execute("SELECT stock FROM MEDICAMENTO WHERE id_medicamento = %s FOR UPDATE", (id_medicamento,))
                med = cursor.fetchone()
                if not med:
                    return {'error': 'Medicamento no encontrado'}
                # med puede ser tuple o dict
                stock_actual = med[0] if not isinstance(med, dict) else med.get('stock')
                if stock_actual is None or stock_actual < cantidad:
                    return {'error': 'Stock insuficiente'}

                cursor.execute("""
                    INSERT INTO DETALLE_MEDICAMENTO (id_empleado, id_paciente, id_medicamento, cantidad)
                    VALUES (%s, %s, %s, %s)
                """, (id_empleado, id_paciente, id_medicamento, cantidad))

                cursor.execute("""
                    UPDATE MEDICAMENTO SET stock = stock - %s WHERE id_medicamento = %s
                """, (cantidad, id_medicamento))

                conexion.commit()
                return {'id_detalle': cursor.lastrowid}
            except Exception as e:
                conexion.rollback()
                return {'error': str(e)}
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def listar_entregas():
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT d.id_detalle, d.cantidad,
                           m.nombre as medicamento,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado
                    FROM DETALLE_MEDICAMENTO d
                    JOIN MEDICAMENTO m ON d.id_medicamento = m.id_medicamento
                    JOIN PACIENTE p ON d.id_paciente = p.id_paciente
                    JOIN EMPLEADO e ON d.id_empleado = e.id_empleado
                    ORDER BY d.id_detalle DESC
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