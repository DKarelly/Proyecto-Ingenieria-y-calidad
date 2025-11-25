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
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%d/%m/%Y') as fecha_vencimiento
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
                           DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%d/%m/%Y') as fecha_vencimiento
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
    def obtener_recientes(limite=7):
        """Obtiene los medicamentos más recientes registrados"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                # Convertir limite a int para evitar problemas con el formato
                limite = int(limite)
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, %s) as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, %s) as fecha_vencimiento,
                           stock as cantidad
                    FROM MEDICAMENTO
                    ORDER BY fecha_registro DESC
                    LIMIT """ + str(limite), ('%d/%m/%Y', '%d/%m/%Y'))
                rows = cursor.fetchall()
                print(f"DEBUG obtener_recientes: {len(rows)} medicamentos encontrados")
                resultado = _rows_to_dicts(cursor, rows)
                return resultado
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
        fecha_limite_str = fecha_limite.strftime('%Y-%m-%d')

        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                query = """
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_registro, '%%d/%%m/%%Y') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%%d/%%m/%%Y') as fecha_vencimiento,
                           DATEDIFF(fecha_vencimiento, CURDATE()) as dias_para_vencer
                    FROM MEDICAMENTO
                    WHERE fecha_vencimiento <= %s AND fecha_vencimiento >= CURDATE()
                    ORDER BY fecha_vencimiento ASC
                """
                params = [fecha_limite_str]

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
                           DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%d/%m/%Y') as fecha_vencimiento
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
    def obtener_ingresos_recientes(limite=7):
        """Obtiene los medicamentos más recientes registrados, ordenados por fecha de registro"""
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                # Convertir limite a int para evitar problemas con el formato
                limite = int(limite)
                cursor.execute("""
                    SELECT id_medicamento, nombre, descripcion, stock,
                           DATE_FORMAT(fecha_vencimiento, %s) as fecha_vencimiento,
                           stock as cantidad,
                           DATE_FORMAT(fecha_registro, %s) as fecha_ingreso
                    FROM MEDICAMENTO
                    ORDER BY fecha_registro DESC
                    LIMIT """ + str(limite), ('%d/%m/%Y', '%d/%m/%Y'))
                rows = cursor.fetchall()
                print(f"DEBUG obtener_ingresos_recientes: {len(rows)} medicamentos encontrados")
                resultado = _rows_to_dicts(cursor, rows)
                return resultado
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
                           DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%d/%m/%Y') as fecha_vencimiento,
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
                           DATE_FORMAT(fecha_registro, '%d/%m/%Y') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%d/%m/%Y') as fecha_vencimiento,
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
                           DATE_FORMAT(fecha_registro, '%%d/%%m/%%Y') as fecha_registro,
                           DATE_FORMAT(fecha_vencimiento, '%%d/%%m/%%Y') as fecha_vencimiento
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



class DetalleMedicamento:
    @staticmethod
    def registrar_entrega(id_empleado, id_paciente, id_medicamento, cantidad):
        print(f"DEBUG: Registrando entrega - Empleado: {id_empleado}, Paciente: {id_paciente}, Medicamento: {id_medicamento}, Cantidad: {cantidad}")
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            try:
                # Bloqueo y verificación de stock
                # Dependiendo del conector, FOR UPDATE funciona si la transacción está activa.
                print(f"DEBUG: Verificando stock para medicamento {id_medicamento}")
                cursor.execute("SELECT stock FROM MEDICAMENTO WHERE id_medicamento = %s FOR UPDATE", (id_medicamento,))
                med = cursor.fetchone()
                print(f"DEBUG: Resultado de SELECT stock: {med}")
                if not med:
                    print("DEBUG: Medicamento no encontrado")
                    return {'error': 'Medicamento no encontrado'}
                # med puede ser tuple o dict
                stock_actual = med[0] if not isinstance(med, dict) else med.get('stock')
                print(f"DEBUG: Stock actual: {stock_actual}")
                if stock_actual is None or stock_actual < cantidad:
                    print(f"DEBUG: Stock insuficiente. Actual: {stock_actual}, Requerido: {cantidad}")
                    return {'error': 'Stock insuficiente'}

                print("DEBUG: Insertando detalle de medicamento")
                cursor.execute("""
                    INSERT INTO DETALLE_MEDICAMENTO (id_empleado, id_paciente, id_medicamento, cantidad, fecha_entrega)
                    VALUES (%s, %s, %s, %s, CURDATE())
                """, (id_empleado, id_paciente, id_medicamento, cantidad))
                id_detalle = cursor.lastrowid
                print(f"DEBUG: ID detalle insertado: {id_detalle}")

                print("DEBUG: Actualizando stock")
                cursor.execute("""
                    UPDATE MEDICAMENTO SET stock = stock - %s WHERE id_medicamento = %s
                """, (cantidad, id_medicamento))

                conexion.commit()
                print(f"DEBUG: Entrega registrada exitosamente con ID: {id_detalle}")
                return {'id_detalle': id_detalle}
            except Exception as e:
                print(f"DEBUG: Error en la transacción: {str(e)}")
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
                    SELECT d.id_detalle as id, d.cantidad, d.id_empleado, d.id_paciente, d.id_medicamento,
                           m.nombre as medicamento,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           d.fecha_entrega
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

    @staticmethod
    def obtener_entrega_por_id(id_detalle):
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT d.id_detalle as id, d.cantidad, d.id_empleado, d.id_paciente, d.id_medicamento,
                           m.nombre as medicamento,
                           CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           d.fecha_entrega
                    FROM DETALLE_MEDICAMENTO d
                    JOIN MEDICAMENTO m ON d.id_medicamento = m.id_medicamento
                    JOIN PACIENTE p ON d.id_paciente = p.id_paciente
                    JOIN EMPLEADO e ON d.id_empleado = e.id_empleado
                    WHERE d.id_detalle = %s
                """, (id_detalle,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return _rows_to_dicts(cursor, [row])[0]
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
        finally:
            conexion.close()

    @staticmethod
    def actualizar_entrega(id_detalle, id_empleado, id_paciente, id_medicamento, cantidad):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            try:
                # Get current delivery
                cursor.execute("SELECT cantidad, id_medicamento FROM DETALLE_MEDICAMENTO WHERE id_detalle = %s", (id_detalle,))
                current = cursor.fetchone()
                if not current:
                    return {'error': 'Entrega no encontrada'}
                old_quantity = current['cantidad']
                old_medicamento = current['id_medicamento']

                # If medication changed, adjust stocks
                if id_medicamento != old_medicamento:
                    # Return stock to old medication
                    cursor.execute("UPDATE MEDICAMENTO SET stock = stock + %s WHERE id_medicamento = %s", (old_quantity, old_medicamento))
                    # Check and take from new medication
                    cursor.execute("SELECT stock FROM MEDICAMENTO WHERE id_medicamento = %s FOR UPDATE", (id_medicamento,))
                    med = cursor.fetchone()
                    if not med:
                        return {'error': 'Medicamento no encontrado'}
                    stock_actual = med['stock']
                    if stock_actual < cantidad:
                        return {'error': 'Stock insuficiente'}
                    cursor.execute("UPDATE MEDICAMENTO SET stock = stock - %s WHERE id_medicamento = %s", (cantidad, id_medicamento))
                else:
                    # Same medication, adjust difference
                    difference = cantidad - old_quantity
                    if difference > 0:
                        # Need more stock
                        cursor.execute("SELECT stock FROM MEDICAMENTO WHERE id_medicamento = %s FOR UPDATE", (id_medicamento,))
                        med = cursor.fetchone()
                        stock_actual = med['stock']
                        if stock_actual < difference:
                            return {'error': 'Stock insuficiente'}
                        cursor.execute("UPDATE MEDICAMENTO SET stock = stock - %s WHERE id_medicamento = %s", (difference, id_medicamento))
                    elif difference < 0:
                        # Return excess stock
                        cursor.execute("UPDATE MEDICAMENTO SET stock = stock + %s WHERE id_medicamento = %s", (-difference, id_medicamento))

                # Update delivery
                cursor.execute("""
                    UPDATE DETALLE_MEDICAMENTO
                    SET id_empleado = %s, id_paciente = %s, id_medicamento = %s, cantidad = %s
                    WHERE id_detalle = %s
                """, (id_empleado, id_paciente, id_medicamento, cantidad, id_detalle))

                conexion.commit()
                return {'modified_rows': cursor.rowcount}
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


class Paciente:
    @staticmethod
    def buscar(termino):
        conexion = obtener_conexion()
        try:
            cursor = _get_cursor(conexion)
            try:
                cursor.execute("""
                    SELECT id_paciente, nombres as nombre, apellidos as apellido, documento_identidad as dni
                    FROM PACIENTE
                    WHERE nombres LIKE %s OR apellidos LIKE %s OR documento_identidad LIKE %s
                    LIMIT 10
                """, (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
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
