from bd import obtener_conexion

class Empleado:
    def __init__(self, id_empleado=None, nombres=None, apellidos=None,
                 documento_identidad=None, sexo=None, estado='activo',
                 id_usuario=None, id_rol=None, id_distrito=None, id_especialidad=None):
        self.id_empleado = id_empleado
        self.nombres = nombres
        self.apellidos = apellidos
        self.documento_identidad = documento_identidad
        self.sexo = sexo
        self.estado = estado
        self.id_usuario = id_usuario
        self.id_rol = id_rol
        self.id_distrito = id_distrito
        self.id_especialidad = id_especialidad

    @staticmethod
    def crear(nombres, apellidos, documento_identidad, sexo, id_usuario, 
              id_rol, id_distrito=None, id_especialidad=None, fecha_nacimiento=None):
        """Crea un nuevo empleado"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                print(f'[DEBUG Empleado.crear] Insertando empleado: nombres={nombres}, apellidos={apellidos}, doc={documento_identidad}, id_usuario={id_usuario}, id_rol={id_rol}, id_distrito={id_distrito}, id_especialidad={id_especialidad}')
                
                # Insert including fecha_nacimiento (column added to table)
                sql = """INSERT INTO EMPLEADO (nombres, apellidos, fecha_nacimiento, documento_identidad, 
                         sexo, estado, id_usuario, id_rol, id_distrito, id_especialidad) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (nombres, apellidos, fecha_nacimiento, documento_identidad, sexo, 
                                   'activo', id_usuario, id_rol, id_distrito, id_especialidad))
                conexion.commit()
                
                id_insertado = cursor.lastrowid
                print(f'[DEBUG Empleado.crear] Empleado insertado con ID: {id_insertado}')
                
                return {'success': True, 'id_empleado': id_insertado}
        except Exception as e:
            conexion.rollback()
            print(f'[DEBUG Empleado.crear] ERROR: {str(e)}')
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los empleados activos"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*, 
                           u.correo, u.telefono, u.estado as estado_usuario,
                           r.nombre as rol,
                           esp.nombre as especialidad,
                           d.nombre as distrito,
                           prov.nombre as provincia,
                           dep.nombre as departamento
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
                    LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
                    WHERE u.estado = 'activo'
                    ORDER BY e.apellidos, e.nombres
                """
                cursor.execute(sql)
                resultado = cursor.fetchall()
                # Asegurar que siempre retorna una lista
                return resultado if resultado else []
        except Exception as e:
            print(f"Error en obtener_todos: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_empleado):
        """Obtiene un empleado por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*, 
                           u.correo, u.telefono, u.estado as estado_usuario,
                           r.nombre as rol, r.estado as estado_rol,
                           esp.nombre as especialidad, esp.descripcion as descripcion_especialidad,
                           d.nombre as distrito, d.id_distrito,
                           prov.nombre as provincia, prov.id_provincia,
                           dep.nombre as departamento, dep.id_departamento
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
                    LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
                    WHERE e.id_empleado = %s
                """
                cursor.execute(sql, (id_empleado,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_usuario(id_usuario):
        """Obtiene un empleado por su ID de usuario"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*, 
                           u.correo, u.telefono, u.estado as estado_usuario,
                           r.nombre as rol,
                           esp.nombre as especialidad,
                           d.nombre as distrito
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
                    WHERE e.id_usuario = %s
                """
                cursor.execute(sql, (id_usuario,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_documento(documento_identidad):
        """Obtiene un empleado por su documento"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*, 
                           u.correo, u.telefono,
                           r.nombre as rol
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    WHERE e.documento_identidad = %s
                """
                cursor.execute(sql, (documento_identidad,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_especialidad(id_especialidad):
        """Obtiene empleados por especialidad"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*, 
                           u.correo, u.telefono,
                           r.nombre as rol,
                           esp.nombre as especialidad
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE e.id_especialidad = %s AND e.estado = 'activo'
                    ORDER BY e.apellidos, e.nombres
                """
                cursor.execute(sql, (id_especialidad,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_rol(id_rol):
        """Obtiene empleados por rol"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*, 
                           u.correo, u.telefono,
                           r.nombre as rol,
                           esp.nombre as especialidad
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE e.id_rol = %s AND e.estado = 'activo'
                    ORDER BY e.apellidos, e.nombres
                """
                cursor.execute(sql, (id_rol,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_empleado, nombres=None, apellidos=None, documento_identidad=None,
                  sexo=None, estado=None, id_rol=None, id_distrito=None, id_especialidad=None,
                  fecha_nacimiento=None):
        """Actualiza un empleado existente"""
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

                # Fecha de nacimiento (aceptar None explícito para eliminar)
                if fecha_nacimiento is not None:
                    campos.append("fecha_nacimiento = %s")
                    valores.append(fecha_nacimiento)
                
                if estado:
                    campos.append("estado = %s")
                    valores.append(estado)
                
                if id_rol:
                    campos.append("id_rol = %s")
                    valores.append(id_rol)
                
                if id_distrito:
                    campos.append("id_distrito = %s")
                    valores.append(id_distrito)
                
                if id_especialidad is not None:  # Permite None explícito
                    campos.append("id_especialidad = %s")
                    valores.append(id_especialidad)
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_empleado)
                sql = f"UPDATE EMPLEADO SET {', '.join(campos)} WHERE id_empleado = %s"
                cursor.execute(sql, tuple(valores))
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_empleado):
        """Desactiva un empleado (cambia estado a inactivo)"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Primero obtener el id_usuario
                cursor.execute("SELECT id_usuario FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
                empleado = cursor.fetchone()
                
                if not empleado:
                    return {'error': 'Empleado no encontrado'}
                
                # Desactivar el empleado
                cursor.execute("UPDATE EMPLEADO SET estado = 'inactivo' WHERE id_empleado = %s", 
                             (id_empleado,))
                
                # Desactivar el usuario
                cursor.execute("UPDATE USUARIO SET estado = 'inactivo' WHERE id_usuario = %s", 
                             (empleado['id_usuario'],))
                
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_medicos():
        """Obtiene solo empleados que son médicos (roles 2 y 3) y tienen especialidad asignada"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*,
                           u.correo, u.telefono, u.estado as estado_usuario,
                           r.nombre as rol,
                           esp.nombre as especialidad,
                           d.nombre as distrito,
                           prov.nombre as provincia,
                           dep.nombre as departamento
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
                    LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
                    WHERE e.id_rol IN (2)
                      AND e.id_especialidad IS NOT NULL
                      AND e.estado = 'activo'
                    ORDER BY e.apellidos, e.nombres
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def buscar(termino):
        """Busca empleados activos por nombre, apellido, correo o documento"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.*,
                           u.correo, u.telefono,
                           r.nombre as rol,
                           esp.nombre as especialidad,
                           d.nombre as distrito,
                           prov.nombre as provincia,
                           dep.nombre as departamento
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    LEFT JOIN ROL r ON e.id_rol = r.id_rol
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
                    LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
                    LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
                    WHERE (e.nombres LIKE %s
                       OR e.apellidos LIKE %s
                       OR e.documento_identidad LIKE %s
                       OR u.correo LIKE %s
                       OR r.nombre LIKE %s)
                    AND u.estado = 'activo'
                    ORDER BY e.apellidos, e.nombres
                """
                termino_busqueda = f"%{termino}%"
                cursor.execute(sql, (termino_busqueda, termino_busqueda, termino_busqueda, 
                                   termino_busqueda, termino_busqueda))
                return cursor.fetchall()
        finally:
            conexion.close()
