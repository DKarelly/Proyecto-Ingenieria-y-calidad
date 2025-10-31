from bd import obtener_conexion

class Servicio:
    def __init__(self, id_servicio=None, nombre=None, descripcion=None,
                 estado='activo', id_tipo_servicio=None, id_especialidad=None):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado
        self.id_tipo_servicio = id_tipo_servicio
        self.id_especialidad = id_especialidad

    @staticmethod
    def crear(nombre, descripcion, id_tipo_servicio, id_especialidad=None):
        """Crea un nuevo servicio"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO SERVICIO (nombre, descripcion, estado, 
                         id_tipo_servicio, id_especialidad) 
                         VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (nombre, descripcion, 'activo', 
                                   id_tipo_servicio, id_especialidad))
                conexion.commit()
                return {'success': True, 'id_servicio': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los servicios"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT s.*,
                           ts.nombre as tipo_servicio,
                           ts.descripcion as descripcion_tipo,
                           esp.nombre as especialidad
                    FROM SERVICIO s
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
                    ORDER BY s.nombre
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_servicio):
        """Obtiene un servicio por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT s.*,
                           ts.nombre as tipo_servicio,
                           ts.descripcion as descripcion_tipo,
                           esp.nombre as especialidad,
                           esp.descripcion as descripcion_especialidad
                    FROM SERVICIO s
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
                    WHERE s.id_servicio = %s
                """
                cursor.execute(sql, (id_servicio,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_tipo(id_tipo_servicio):
        """Obtiene servicios por tipo"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT s.*,
                           ts.nombre as tipo_servicio,
                           esp.nombre as especialidad
                    FROM SERVICIO s
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
                    WHERE s.id_tipo_servicio = %s AND s.estado = 'activo'
                    ORDER BY s.nombre
                """
                cursor.execute(sql, (id_tipo_servicio,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_especialidad(id_especialidad):
        """Obtiene servicios por especialidad"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT s.*,
                           ts.nombre as tipo_servicio,
                           esp.nombre as especialidad
                    FROM SERVICIO s
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
                    WHERE s.id_especialidad = %s AND s.estado = 'activo'
                    ORDER BY s.nombre
                """
                cursor.execute(sql, (id_especialidad,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_servicio, nombre=None, descripcion=None, estado=None,
                  id_tipo_servicio=None, id_especialidad=None):
        """Actualiza un servicio existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                if nombre:
                    campos.append("nombre = %s")
                    valores.append(nombre)
                
                if descripcion:
                    campos.append("descripcion = %s")
                    valores.append(descripcion)
                
                if estado:
                    campos.append("estado = %s")
                    valores.append(estado)
                
                if id_tipo_servicio:
                    campos.append("id_tipo_servicio = %s")
                    valores.append(id_tipo_servicio)
                
                if id_especialidad is not None:
                    campos.append("id_especialidad = %s")
                    valores.append(id_especialidad)
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_servicio)
                sql = f"UPDATE SERVICIO SET {', '.join(campos)} WHERE id_servicio = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_servicio):
        """Desactiva un servicio"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE SERVICIO SET estado = 'inactivo' WHERE id_servicio = %s"
                cursor.execute(sql, (id_servicio,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def buscar(termino):
        """Busca servicios por nombre o descripción"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT s.*,
                           ts.nombre as tipo_servicio,
                           esp.nombre as especialidad
                    FROM SERVICIO s
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
                    WHERE s.nombre LIKE %s OR s.descripcion LIKE %s
                    ORDER BY s.nombre
                """
                termino_busqueda = f"%{termino}%"
                cursor.execute(sql, (termino_busqueda, termino_busqueda))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_activos():
        """Obtiene todos los servicios activos"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT s.*,
                           ts.nombre as tipo_servicio,
                           ts.descripcion as descripcion_tipo,
                           esp.nombre as especialidad
                    FROM SERVICIO s
                    LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    LEFT JOIN ESPECIALIDAD esp ON s.id_especialidad = esp.id_especialidad
                    WHERE s.estado = 'activo'
                    ORDER BY s.nombre
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()