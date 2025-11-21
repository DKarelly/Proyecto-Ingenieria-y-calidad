from bd import obtener_conexion
from datetime import date

class Paciente:
    def __init__(self, id_paciente=None, nombres=None, apellidos=None, 
                 documento_identidad=None, sexo=None, fecha_nacimiento=None,
                 id_usuario=None, id_distrito=None):
        self.id_paciente = id_paciente
        self.nombres = nombres
        self.apellidos = apellidos
        self.documento_identidad = documento_identidad
        self.sexo = sexo
        self.fecha_nacimiento = fecha_nacimiento
        self.id_usuario = id_usuario
        self.id_distrito = id_distrito

    @staticmethod
    def crear(nombres, apellidos, documento_identidad, sexo, fecha_nacimiento, 
              id_usuario, id_distrito):
        """Crea un nuevo paciente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO PACIENTE (nombres, apellidos, documento_identidad, 
                         sexo, fecha_nacimiento, id_usuario, id_distrito) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (nombres, apellidos, documento_identidad, 
                                   sexo, fecha_nacimiento, id_usuario, id_distrito))
                conexion.commit()
                return {'success': True, 'id_paciente': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            # Detectar error de duplicación de DNI
            error_msg = str(e)
            if '1062' in error_msg and 'documento_identidad' in error_msg:
                return {'error': f'El documento de identidad {documento_identidad} ya está registrado en el sistema'}
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    @staticmethod
    def obtener_todos():
        """Obtiene todos los pacientes activos"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*, 
                           u.correo, u.telefono, u.estado,
                           d.nombre as distrito, 
                           prov.nombre as provincia,
                           dep.nombre as departamento
                    FROM PACIENTE p
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    LEFT JOIN DISTRITO d ON p.id_distrito = d.id_distrito
                    LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
                    WHERE u.estado = 'activo'
                    ORDER BY p.apellidos, p.nombres
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_paciente):
        """Obtiene un paciente por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*, 
                           u.correo, u.telefono, u.estado as estado_usuario,
                           d.nombre as distrito, d.id_distrito,
                           prov.nombre as provincia, prov.id_provincia,
                           dep.nombre as departamento, dep.id_departamento
                    FROM PACIENTE p
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    LEFT JOIN DISTRITO d ON p.id_distrito = d.id_distrito
                    LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
                    WHERE p.id_paciente = %s
                """
                cursor.execute(sql, (id_paciente,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_documento(documento_identidad):
        """Obtiene un paciente por su documento"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*, 
                           u.correo, u.telefono, u.estado as estado_usuario
                    FROM PACIENTE p
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    WHERE p.documento_identidad = %s
                """
                cursor.execute(sql, (documento_identidad,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_usuario(id_usuario):
        """Obtiene un paciente por su ID de usuario"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*, 
                           u.correo, u.telefono, u.estado as estado_usuario,
                           d.nombre as distrito,
                           prov.nombre as provincia,
                           dep.nombre as departamento
                    FROM PACIENTE p
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    LEFT JOIN DISTRITO d ON p.id_distrito = d.id_distrito
                    LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
                    WHERE p.id_usuario = %s
                """
                cursor.execute(sql, (id_usuario,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_paciente, nombres=None, apellidos=None, documento_identidad=None,
                  sexo=None, fecha_nacimiento=None, id_distrito=None):
        """Actualiza un paciente existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                if nombres:
                    campos.append("nombres = %s")
                    valores.append(nombres)
                
                if apellidos:
                    campos.append("apellidos = %s")
                    valores.append(apellidos)
                
                if documento_identidad:
                    campos.append("documento_identidad = %s")
                    valores.append(documento_identidad)
                
                if sexo:
                    campos.append("sexo = %s")
                    valores.append(sexo)
                
                if fecha_nacimiento:
                    campos.append("fecha_nacimiento = %s")
                    valores.append(fecha_nacimiento)
                
                if id_distrito:
                    campos.append("id_distrito = %s")
                    valores.append(id_distrito)
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_paciente)
                sql = f"UPDATE PACIENTE SET {', '.join(campos)} WHERE id_paciente = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_paciente):
        """Elimina un paciente (desactiva su usuario asociado)"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Primero obtener el id_usuario
                cursor.execute("SELECT id_usuario FROM PACIENTE WHERE id_paciente = %s", (id_paciente,))
                resultado = cursor.fetchone()
                
                if not resultado:
                    return {'error': 'Paciente no encontrado'}
                
                # resultado es un diccionario (DictCursor), acceder por clave
                id_usuario = resultado['id_usuario']
                
                # Desactivar el usuario
                cursor.execute("UPDATE USUARIO SET estado = 'Inactivo' WHERE id_usuario = %s", 
                             (id_usuario,))
                
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def buscar(termino):
        """Busca pacientes activos por nombre, apellido, correo o documento"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.*, 
                           u.correo, u.telefono,
                           d.nombre as distrito
                    FROM PACIENTE p
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    LEFT JOIN DISTRITO d ON p.id_distrito = d.id_distrito
                    WHERE u.estado = 'activo'
                      AND (p.nombres LIKE %s 
                           OR p.apellidos LIKE %s 
                           OR p.documento_identidad LIKE %s
                           OR u.correo LIKE %s)
                    ORDER BY p.apellidos, p.nombres
                """
                termino_busqueda = f"%{termino}%"
                cursor.execute(sql, (termino_busqueda, termino_busqueda, termino_busqueda, termino_busqueda))
                return cursor.fetchall()
        finally:
            conexion.close()
