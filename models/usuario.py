from bd import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario:
    def __init__(self, id_usuario=None, contrasena=None, correo_electronico=None, 
                 fecha_creacion=None, ultimo_acceso=None, estado='activo', 
                 tipo_usuario=None, id_paciente=None, id_empleado=None):
        self.id_usuario = id_usuario
        self.contrasena = contrasena
        self.correo_electronico = correo_electronico
        self.fecha_creacion = fecha_creacion
        self.ultimo_acceso = ultimo_acceso
        self.estado = estado
        self.tipo_usuario = tipo_usuario
        self.id_paciente = id_paciente
        self.id_empleado = id_empleado

    @staticmethod
    def crear_usuario(contrasena, correo_electronico, tipo_usuario, id_paciente=None, id_empleado=None):
        """Crea un nuevo usuario en la base de datos"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Hash de la contraseña
                contrasena_hash = generate_password_hash(contrasena)
                
                # Validar que solo tenga id_paciente o id_empleado según el tipo
                if tipo_usuario == 'paciente' and id_paciente is None:
                    return {'error': 'Debe proporcionar id_paciente para tipo paciente'}
                if tipo_usuario == 'empleado' and id_empleado is None:
                    return {'error': 'Debe proporcionar id_empleado para tipo empleado'}
                
                sql = """INSERT INTO USUARIO (contrasena, correo_electronico, tipo_usuario, 
                         id_paciente, id_empleado) VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (contrasena_hash, correo_electronico, tipo_usuario, 
                                   id_paciente, id_empleado))
                conexion.commit()
                return {'success': True, 'id_usuario': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los usuarios con información de paciente o empleado"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT u.*, 
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           r.nombre as rol_empleado
                    FROM USUARIO u
                    LEFT JOIN PACIENTE p ON u.id_paciente = p.id_paciente
                    LEFT JOIN EMPLEADO e ON u.id_empleado = e.id_empleado
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    ORDER BY u.fecha_creacion DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_usuario):
        """Obtiene un usuario por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT u.*, 
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad as documento_paciente,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           e.documento as documento_empleado,
                           r.nombre as rol_empleado
                    FROM USUARIO u
                    LEFT JOIN PACIENTE p ON u.id_paciente = p.id_paciente
                    LEFT JOIN EMPLEADO e ON u.id_empleado = e.id_empleado
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    WHERE u.id_usuario = %s
                """
                cursor.execute(sql, (id_usuario,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_correo(correo_electronico):
        """Obtiene un usuario por su correo electrónico"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT u.*, 
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           r.nombre as rol_empleado
                    FROM USUARIO u
                    LEFT JOIN PACIENTE p ON u.id_paciente = p.id_paciente
                    LEFT JOIN EMPLEADO e ON u.id_empleado = e.id_empleado
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    WHERE u.correo_electronico = %s
                """
                cursor.execute(sql, (correo_electronico,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_usuario, correo_electronico=None, estado=None, contrasena=None):
        """Actualiza un usuario existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                if correo_electronico:
                    campos.append("correo_electronico = %s")
                    valores.append(correo_electronico)
                
                if estado:
                    campos.append("estado = %s")
                    valores.append(estado)
                
                if contrasena:
                    campos.append("contrasena = %s")
                    valores.append(generate_password_hash(contrasena))
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_usuario)
                sql = f"UPDATE USUARIO SET {', '.join(campos)} WHERE id_usuario = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def actualizar_ultimo_acceso(id_usuario):
        """Actualiza la fecha de último acceso del usuario"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE USUARIO SET ultimo_acceso = %s WHERE id_usuario = %s"
                cursor.execute(sql, (datetime.now(), id_usuario))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_usuario):
        """Elimina un usuario (cambio de estado a inactivo)"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE USUARIO SET estado = 'inactivo' WHERE id_usuario = %s"
                cursor.execute(sql, (id_usuario,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def verificar_contrasena(contrasena_hash, contrasena_ingresada):
        """Verifica si la contraseña ingresada coincide con el hash"""
        return check_password_hash(contrasena_hash, contrasena_ingresada)

    @staticmethod
    def login(correo_electronico, contrasena):
        """Realiza el login de un usuario"""
        usuario = Usuario.obtener_por_correo(correo_electronico)
        
        if not usuario:
            return {'error': 'Usuario no encontrado'}
        
        if usuario['estado'] != 'activo':
            return {'error': 'Usuario inactivo'}
        
        if not Usuario.verificar_contrasena(usuario['contrasena'], contrasena):
            return {'error': 'Contraseña incorrecta'}
        
        # Actualizar último acceso
        Usuario.actualizar_ultimo_acceso(usuario['id_usuario'])
        
        return {
            'success': True,
            'usuario': {
                'id_usuario': usuario['id_usuario'],
                'correo_electronico': usuario['correo_electronico'],
                'tipo_usuario': usuario['tipo_usuario'],
                'nombre': usuario['nombre_paciente'] if usuario['tipo_usuario'] == 'paciente' else usuario['nombre_empleado'],
                'rol': usuario.get('rol_empleado')
            }
        }
