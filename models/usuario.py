from bd import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

class Usuario:
    def __init__(self, id_usuario=None, contrasena=None, correo=None, 
                 telefono=None, estado='Activo', fecha_creacion=None):
        self.id_usuario = id_usuario
        self.contrasena = contrasena
        self.correo = correo
        self.telefono = telefono
        self.estado = estado
        self.fecha_creacion = fecha_creacion

    @staticmethod
    def crear_usuario(contrasena, correo, telefono=None):
        """Crea un nuevo usuario en la base de datos"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Hash de la contraseña
                contrasena_hash = generate_password_hash(contrasena)
                
                print(f'[DEBUG Usuario.crear_usuario] Insertando usuario: correo={correo}, telefono={telefono}')
                
                sql = """INSERT INTO USUARIO (correo, contrasena, telefono, estado, fecha_creacion) 
                         VALUES (%s, %s, %s, %s, %s)"""
                # Guardar cuenta nueva con estado 'Activo' (mayúscula) por requerimiento
                cursor.execute(sql, (correo, contrasena_hash, telefono, 'Activo', date.today()))
                conexion.commit()
                
                id_insertado = cursor.lastrowid
                print(f'[DEBUG Usuario.crear_usuario] Usuario insertado con ID: {id_insertado}')
                
                return {'success': True, 'id_usuario': id_insertado}
        except Exception as e:
            conexion.rollback()
            print(f'[DEBUG Usuario.crear_usuario] ERROR: {str(e)}')
            import traceback
            traceback.print_exc()
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
                           p.id_paciente,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad as documento_paciente,
                           e.id_empleado,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           e.documento_identidad as documento_empleado,
                           r.nombre as rol_empleado,
                           CASE 
                               WHEN p.id_paciente IS NOT NULL THEN 'paciente'
                               WHEN e.id_empleado IS NOT NULL THEN 'empleado'
                               ELSE NULL
                           END as tipo_usuario
                    FROM USUARIO u
                    LEFT JOIN PACIENTE p ON u.id_usuario = p.id_usuario
                    LEFT JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
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
                           p.id_paciente,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad as documento_paciente,
                           CASE 
                               WHEN p.sexo = 'M' THEN 'Masculino'
                               WHEN p.sexo = 'F' THEN 'Femenino'
                               ELSE p.sexo
                           END as sexo_paciente,
                           p.fecha_nacimiento,
                           p.id_distrito as id_distrito_paciente,
                           e.id_empleado,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           e.documento_identidad as documento_empleado,
                           CASE 
                               WHEN e.sexo = 'M' THEN 'Masculino'
                               WHEN e.sexo = 'F' THEN 'Femenino'
                               ELSE e.sexo
                           END as sexo_empleado,
                           e.fecha_nacimiento as fecha_nacimiento_empleado,
                           e.id_distrito as id_distrito_empleado,
                           r.nombre as rol_empleado,
                           r.id_rol,
                           esp.nombre as especialidad_empleado,
                           esp.id_especialidad,
                           -- Información de ubicación
                           dist.nombre as distrito,
                           prov.nombre as provincia,
                           dept.nombre as departamento,
                           CASE 
                               WHEN p.id_paciente IS NOT NULL THEN 'paciente'
                               WHEN e.id_empleado IS NOT NULL THEN 'empleado'
                               ELSE NULL
                           END as tipo_usuario
                    FROM USUARIO u
                    LEFT JOIN PACIENTE p ON u.id_usuario = p.id_usuario
                    LEFT JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    -- Join para ubicación de pacientes
                    LEFT JOIN DISTRITO dist ON (p.id_distrito = dist.id_distrito OR e.id_distrito = dist.id_distrito)
                    LEFT JOIN PROVINCIA prov ON dist.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dept ON prov.id_departamento = dept.id_departamento
                    WHERE u.id_usuario = %s
                """
                cursor.execute(sql, (id_usuario,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_correo(correo):
        """Obtiene un usuario por su correo electrónico"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT u.*, 
                           p.id_paciente,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           e.id_empleado,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           r.nombre as rol_empleado,
                           r.id_rol,
                           CASE 
                               WHEN p.id_paciente IS NOT NULL THEN 'paciente'
                               WHEN e.id_empleado IS NOT NULL THEN 'empleado'
                               ELSE NULL
                           END as tipo_usuario
                    FROM USUARIO u
                    LEFT JOIN PACIENTE p ON u.id_usuario = p.id_usuario
                    LEFT JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    WHERE u.correo = %s
                """
                cursor.execute(sql, (correo,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_usuario, correo=None, telefono=None, estado=None, contrasena=None):
        """Actualiza un usuario existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                if correo:
                    campos.append("correo = %s")
                    valores.append(correo)
                
                if telefono:
                    campos.append("telefono = %s")
                    valores.append(telefono)
                
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
    def cambiar_contrasena(id_usuario, contrasena_actual, contrasena_nueva):
        """Cambia la contraseña de un usuario verificando la contraseña actual"""
        from werkzeug.security import check_password_hash, generate_password_hash
        
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener contraseña actual
                sql = "SELECT contrasena FROM USUARIO WHERE id_usuario = %s"
                cursor.execute(sql, (id_usuario,))
                usuario = cursor.fetchone()
                
                if not usuario:
                    return {'error': 'Usuario no encontrado'}
                    
                # Verificar contraseña actual
                if not check_password_hash(usuario['contrasena'], contrasena_actual):
                    return {'error': 'La contraseña actual es incorrecta'}
                    
                # Validar nueva contraseña
                if len(contrasena_nueva) < 8:
                    return {'error': 'La nueva contraseña debe tener al menos 8 caracteres'}
                    
                import re
                if not re.search(r'[A-Z]', contrasena_nueva):
                    return {'error': 'La nueva contraseña debe tener al menos una mayúscula'}
                    
                if not re.search(r'[a-z]', contrasena_nueva):
                    return {'error': 'La nueva contraseña debe tener al menos una minúscula'}
                    
                if not re.search(r'\d', contrasena_nueva):
                    return {'error': 'La nueva contraseña debe tener al menos un número'}
                
                # Actualizar contraseña
                contrasena_hash = generate_password_hash(contrasena_nueva)
                sql = "UPDATE USUARIO SET contrasena = %s WHERE id_usuario = %s"
                cursor.execute(sql, (contrasena_hash, id_usuario))
                conexion.commit()
                
                return {
                    'success': True,
                    'message': 'Contraseña actualizada exitosamente'
                }
                
        except Exception as e:
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def verificar_contrasena(contrasena_hash, contrasena_ingresada):
        """Verifica si la contraseña ingresada coincide con el hash"""
        return check_password_hash(contrasena_hash, contrasena_ingresada)

    @staticmethod
    def login(correo, contrasena):
        """Realiza el login de un usuario"""
        usuario = Usuario.obtener_por_correo(correo)
        
        if not usuario:
            return {'error': 'Usuario no encontrado'}
        
        # Aceptar variantes de mayúsculas/minúsculas en el campo estado
        if not usuario['estado'] or usuario['estado'].lower() != 'activo':
            return {'error': 'Usuario inactivo'}
        
        if not Usuario.verificar_contrasena(usuario['contrasena'], contrasena):
            return {'error': 'Contraseña incorrecta'}
        
        # Determinar el nombre según el tipo de usuario
        nombre = None
        if usuario['tipo_usuario'] == 'paciente':
            nombre = usuario.get('nombre_paciente')
        elif usuario['tipo_usuario'] == 'empleado':
            nombre = usuario.get('nombre_empleado')

        # Si no se encontró nombre, intentar obtenerlo directamente de las tablas
        if not nombre:
            if usuario['tipo_usuario'] == 'paciente' and usuario.get('id_paciente'):
                from models.paciente import Paciente
                paciente = Paciente.obtener_por_id(usuario['id_paciente'])
                if paciente:
                    nombre = f"{paciente['nombres']} {paciente['apellidos']}"
            elif usuario['tipo_usuario'] == 'empleado' and usuario.get('id_empleado'):
                from models.empleado import Empleado
                empleado = Empleado.obtener_por_id(usuario['id_empleado'])
                if empleado:
                    nombre = f"{empleado['nombres']} {empleado['apellidos']}"

        return {
            'success': True,
            'usuario': {
                'id_usuario': usuario['id_usuario'],
                'correo': usuario['correo'],
                'telefono': usuario['telefono'],
                'tipo_usuario': usuario['tipo_usuario'],
                'nombre': nombre,
                'rol': usuario.get('rol_empleado'),
                'id_rol': usuario.get('id_rol'),
                'id_paciente': usuario.get('id_paciente'),
                'id_empleado': usuario.get('id_empleado')
            }
        }

