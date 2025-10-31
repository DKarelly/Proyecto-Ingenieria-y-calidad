from bd import obtener_conexion

class Recurso:
    def __init__(self, id_recurso=None, nombre=None, estado='activo', id_tipo_recurso=None):
        self.id_recurso = id_recurso
        self.nombre = nombre
        self.estado = estado
        self.id_tipo_recurso = id_tipo_recurso

    @staticmethod
    def crear(nombre, id_tipo_recurso):
        """Crea un nuevo recurso"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO RECURSO (nombre, estado, id_tipo_recurso)
                         VALUES (%s, %s, %s)"""
                cursor.execute(sql, (nombre, 'activo', id_tipo_recurso))
                conexion.commit()
                return {'success': True, 'id_recurso': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los recursos"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           tr.nombre as tipo_recurso,
                           tr.descripcion as descripcion_tipo
                    FROM RECURSO r
                    LEFT JOIN TIPO_RECURSO tr ON r.id_tipo_recurso = tr.id_tipo_recurso
                    ORDER BY r.nombre
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_recurso):
        """Obtiene un recurso por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           tr.nombre as tipo_recurso,
                           tr.descripcion as descripcion_tipo
                    FROM RECURSO r
                    LEFT JOIN TIPO_RECURSO tr ON r.id_tipo_recurso = tr.id_tipo_recurso
                    WHERE r.id_recurso = %s
                """
                cursor.execute(sql, (id_recurso,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_tipo(id_tipo_recurso):
        """Obtiene recursos por tipo"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           tr.nombre as tipo_recurso
                    FROM RECURSO r
                    LEFT JOIN TIPO_RECURSO tr ON r.id_tipo_recurso = tr.id_tipo_recurso
                    WHERE r.id_tipo_recurso = %s AND r.estado = 'activo'
                    ORDER BY r.nombre
                """
                cursor.execute(sql, (id_tipo_recurso,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_recurso, nombre=None, estado=None, id_tipo_recurso=None):
        """Actualiza un recurso existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []

                if nombre:
                    campos.append("nombre = %s")
                    valores.append(nombre)

                if estado:
                    campos.append("estado = %s")
                    valores.append(estado)

                if id_tipo_recurso:
                    campos.append("id_tipo_recurso = %s")
                    valores.append(id_tipo_recurso)

                if not campos:
                    return {'error': 'No hay campos para actualizar'}

                valores.append(id_recurso)
                sql = f"UPDATE RECURSO SET {', '.join(campos)} WHERE id_recurso = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_recurso):
        """Desactiva un recurso"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE RECURSO SET estado = 'inactivo' WHERE id_recurso = %s"
                cursor.execute(sql, (id_recurso,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def buscar(termino):
        """Busca recursos por nombre"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.*,
                           tr.nombre as tipo_recurso
                    FROM RECURSO r
                    LEFT JOIN TIPO_RECURSO tr ON r.id_tipo_recurso = tr.id_tipo_recurso
                    WHERE r.nombre LIKE %s
                    ORDER BY r.nombre
                """
                termino_busqueda = f"%{termino}%"
                cursor.execute(sql, (termino_busqueda,))
                return cursor.fetchall()
        finally:
            conexion.close()
