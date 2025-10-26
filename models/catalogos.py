from bd import obtener_conexion

class Especialidad:
    @staticmethod
    def obtener_todas():
        """Obtiene todas las especialidades"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM ESPECIALIDAD WHERE estado = 'activo' ORDER BY nombre"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_especialidad):
        """Obtiene una especialidad por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM ESPECIALIDAD WHERE id_especialidad = %s"
                cursor.execute(sql, (id_especialidad,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def crear(nombre, descripcion):
        """Crea una nueva especialidad"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO ESPECIALIDAD (nombre, estado, descripcion) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nombre, 'activo', descripcion))
                conexion.commit()
                return {'success': True, 'id_especialidad': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

class Rol:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los roles"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM ROL WHERE estado = 'activo' ORDER BY nombre"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_rol):
        """Obtiene un rol por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM ROL WHERE id_rol = %s"
                cursor.execute(sql, (id_rol,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def crear(nombre):
        """Crea un nuevo rol"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO ROL (nombre, estado) VALUES (%s, %s)"
                cursor.execute(sql, (nombre, 'activo'))
                conexion.commit()
                return {'success': True, 'id_rol': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

class Categoria:
    @staticmethod
    def obtener_todas():
        """Obtiene todas las categorías"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM CATEGORIA ORDER BY nombre"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_categoria):
        """Obtiene una categoría por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM CATEGORIA WHERE id_categoria = %s"
                cursor.execute(sql, (id_categoria,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def crear(nombre, descripcion):
        """Crea una nueva categoría"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO CATEGORIA (nombre, descripcion) VALUES (%s, %s)"
                cursor.execute(sql, (nombre, descripcion))
                conexion.commit()
                return {'success': True, 'id_categoria': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

class TipoServicio:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los tipos de servicio"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM TIPO_SERVICIO ORDER BY nombre"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_tipo_servicio):
        """Obtiene un tipo de servicio por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM TIPO_SERVICIO WHERE id_tipo_servicio = %s"
                cursor.execute(sql, (id_tipo_servicio,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def crear(nombre, descripcion):
        """Crea un nuevo tipo de servicio"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO TIPO_SERVICIO (nombre, descripcion) VALUES (%s, %s)"
                cursor.execute(sql, (nombre, descripcion))
                conexion.commit()
                return {'success': True, 'id_tipo_servicio': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()
