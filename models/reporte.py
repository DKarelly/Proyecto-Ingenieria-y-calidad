from bd import obtener_conexion
from datetime import datetime

class Reporte:
    def __init__(self, id_reporte=None, codigo=None, nombre=None, tipo=None,
                 fecha_creacion=None, id_categoria=None, id_empleado=None,
                 id_servicio=None, id_recurso=None):
        self.id_reporte = id_reporte
        self.codigo = codigo
        self.nombre = nombre
        self.tipo = tipo
        self.fecha_creacion = fecha_creacion
        self.id_categoria = id_categoria
        self.id_empleado = id_empleado
        self.id_servicio = id_servicio
        self.id_recurso = id_recurso

    @staticmethod
    def crear(codigo, nombre, tipo, id_categoria, id_empleado, 
              id_servicio=None, id_recurso=None):
        """Crea un nuevo reporte"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO REPORTE (codigo, nombre, tipo, fecha_creacion, 
                         id_categoria, id_empleado, id_servicio, id_recurso) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (codigo, nombre, tipo, datetime.now(), 
                                   id_categoria, id_empleado, id_servicio, id_recurso))
                conexion.commit()
                return {'success': True, 'id_reporte': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los reportes"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           c.nombre as categoria,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           s.nombre as servicio,
                           rec.nombre as recurso
                    FROM REPORTE r
                    LEFT JOIN CATEGORIA c ON r.id_categoria = c.id_categoria
                    LEFT JOIN EMPLEADO e ON r.id_empleado = e.id_empleado
                    LEFT JOIN SERVICIO s ON r.id_servicio = s.id_servicio
                    LEFT JOIN RECURSO rec ON r.id_recurso = rec.id_recurso
                    ORDER BY r.fecha_creacion DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_reporte):
        """Obtiene un reporte por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           c.nombre as categoria,
                           c.descripcion as descripcion_categoria,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           e.id_empleado,
                           s.nombre as servicio,
                           s.descripcion as descripcion_servicio,
                           rec.nombre as recurso,
                           rec.estado as estado_recurso
                    FROM REPORTE r
                    LEFT JOIN CATEGORIA c ON r.id_categoria = c.id_categoria
                    LEFT JOIN EMPLEADO e ON r.id_empleado = e.id_empleado
                    LEFT JOIN SERVICIO s ON r.id_servicio = s.id_servicio
                    LEFT JOIN RECURSO rec ON r.id_recurso = rec.id_recurso
                    WHERE r.id_reporte = %s
                """
                cursor.execute(sql, (id_reporte,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_categoria(id_categoria):
        """Obtiene reportes por categoría"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           c.nombre as categoria,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           s.nombre as servicio
                    FROM REPORTE r
                    LEFT JOIN CATEGORIA c ON r.id_categoria = c.id_categoria
                    LEFT JOIN EMPLEADO e ON r.id_empleado = e.id_empleado
                    LEFT JOIN SERVICIO s ON r.id_servicio = s.id_servicio
                    WHERE r.id_categoria = %s
                    ORDER BY r.fecha_creacion DESC
                """
                cursor.execute(sql, (id_categoria,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_tipo(tipo):
        """Obtiene reportes por tipo"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           c.nombre as categoria,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado
                    FROM REPORTE r
                    LEFT JOIN CATEGORIA c ON r.id_categoria = c.id_categoria
                    LEFT JOIN EMPLEADO e ON r.id_empleado = e.id_empleado
                    WHERE r.tipo = %s
                    ORDER BY r.fecha_creacion DESC
                """
                cursor.execute(sql, (tipo,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_empleado(id_empleado):
        """Obtiene reportes creados por un empleado"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           c.nombre as categoria,
                           s.nombre as servicio,
                           rec.nombre as recurso
                    FROM REPORTE r
                    LEFT JOIN CATEGORIA c ON r.id_categoria = c.id_categoria
                    LEFT JOIN SERVICIO s ON r.id_servicio = s.id_servicio
                    LEFT JOIN RECURSO rec ON r.id_recurso = rec.id_recurso
                    WHERE r.id_empleado = %s
                    ORDER BY r.fecha_creacion DESC
                """
                cursor.execute(sql, (id_empleado,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_fechas(fecha_inicio, fecha_fin):
        """Obtiene reportes entre fechas"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           c.nombre as categoria,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           s.nombre as servicio
                    FROM REPORTE r
                    LEFT JOIN CATEGORIA c ON r.id_categoria = c.id_categoria
                    LEFT JOIN EMPLEADO e ON r.id_empleado = e.id_empleado
                    LEFT JOIN SERVICIO s ON r.id_servicio = s.id_servicio
                    WHERE DATE(r.fecha_creacion) BETWEEN %s AND %s
                    ORDER BY r.fecha_creacion DESC
                """
                cursor.execute(sql, (fecha_inicio, fecha_fin))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_reporte, codigo=None, nombre=None, tipo=None, id_categoria=None):
        """Actualiza un reporte existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                if codigo:
                    campos.append("codigo = %s")
                    valores.append(codigo)
                
                if nombre:
                    campos.append("nombre = %s")
                    valores.append(nombre)
                
                if tipo:
                    campos.append("tipo = %s")
                    valores.append(tipo)
                
                if id_categoria:
                    campos.append("id_categoria = %s")
                    valores.append(id_categoria)
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_reporte)
                sql = f"UPDATE REPORTE SET {', '.join(campos)} WHERE id_reporte = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_reporte):
        """Elimina un reporte"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM REPORTE WHERE id_reporte = %s"
                cursor.execute(sql, (id_reporte,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def generar_codigo():
        """Genera un código único para el reporte"""
        from random import randint
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_num = randint(1000, 9999)
        return f"REP-{timestamp}-{random_num}"
