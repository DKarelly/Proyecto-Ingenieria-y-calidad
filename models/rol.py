"""
Modelo para la gestión de Roles y Permisos
"""
from bd import obtener_conexion

class Rol:
    """Clase para gestionar roles del sistema"""
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los roles con sus permisos asignados"""
        conexion = obtener_conexion()
        roles = []
        
        try:
            with conexion.cursor() as cursor:
                # Obtener roles
                cursor.execute("""
                    SELECT id_rol, nombre, descripcion, estado
                    FROM ROL
                    ORDER BY nombre
                """)
                roles_data = cursor.fetchall()
                
                for rol_data in roles_data:
                    # Obtener permisos del rol
                    cursor.execute("""
                        SELECT COUNT(*) as total_permisos
                        FROM ROL_PERMISO
                        WHERE id_rol = %s
                    """, (rol_data['id_rol'],))
                    permisos_count = cursor.fetchone()['total_permisos']
                    
                    roles.append({
                        'id_rol': rol_data['id_rol'],
                        'nombre': rol_data['nombre'],
                        'descripcion': rol_data['descripcion'],
                        'estado': rol_data['estado'],
                        'total_permisos': permisos_count
                    })
        finally:
            conexion.close()
        
        return roles
    
    @staticmethod
    def obtener_por_id(id_rol):
        """Obtiene un rol específico por su ID"""
        conexion = obtener_conexion()
        rol = None
        
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT id_rol, nombre, descripcion, estado
                    FROM ROL
                    WHERE id_rol = %s
                """, (id_rol,))
                rol_data = cursor.fetchone()
                
                if rol_data:
                    rol = {
                        'id_rol': rol_data['id_rol'],
                        'nombre': rol_data['nombre'],
                        'descripcion': rol_data['descripcion'],
                        'estado': rol_data['estado']
                    }
        finally:
            conexion.close()
        
        return rol
    
    @staticmethod
    def crear(nombre, descripcion, estado='Activo'):
        """Crea un nuevo rol"""
        conexion = obtener_conexion()
        
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ROL (nombre, descripcion, estado)
                    VALUES (%s, %s, %s)
                """, (nombre, descripcion, estado))
                conexion.commit()
                return cursor.lastrowid
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()
    
    @staticmethod
    def actualizar(id_rol, nombre, descripcion, estado):
        """Actualiza un rol existente"""
        conexion = obtener_conexion()
        
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    UPDATE ROL
                    SET nombre = %s, descripcion = %s, estado = %s
                    WHERE id_rol = %s
                """, (nombre, descripcion, estado, id_rol))
                conexion.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()
    
    @staticmethod
    def eliminar(id_rol):
        """Elimina un rol (solo si no tiene empleados asignados)"""
        conexion = obtener_conexion()
        
        try:
            with conexion.cursor() as cursor:
                # Verificar si hay empleados con este rol
                cursor.execute("""
                    SELECT COUNT(*) AS total FROM EMPLEADO WHERE id_rol = %s
                """, (id_rol,))
                resultado = cursor.fetchone()
                total = resultado['total'] if isinstance(resultado, dict) else (resultado[0] if resultado else 0)
                if total > 0:
                    return False, "No se puede eliminar el rol porque tiene empleados asignados"
                
                # Eliminar permisos asociados (se eliminan automáticamente por CASCADE)
                # Eliminar el rol
                cursor.execute("DELETE FROM ROL WHERE id_rol = %s", (id_rol,))
                conexion.commit()
                return True, "Rol eliminado correctamente"
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()
    
    @staticmethod
    def obtener_permisos(id_rol):
        """Obtiene los permisos asignados a un rol"""
        conexion = obtener_conexion()
        permisos = []
        
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id_permiso, p.nombre, p.codigo, p.descripcion, p.modulo
                    FROM PERMISO p
                    INNER JOIN ROL_PERMISO rp ON p.id_permiso = rp.id_permiso
                    WHERE rp.id_rol = %s AND p.estado = 'Activo'
                    ORDER BY p.modulo, p.nombre
                """, (id_rol,))
                
                for row in cursor.fetchall():
                    permisos.append({
                        'id_permiso': row['id_permiso'],
                        'nombre': row['nombre'],
                        'codigo': row['codigo'],
                        'descripcion': row['descripcion'],
                        'modulo': row['modulo']
                    })
        finally:
            conexion.close()
        
        return permisos
    
    @staticmethod
    def asignar_permisos(id_rol, lista_permisos):
        """Asigna permisos a un rol (reemplaza los permisos existentes)"""
        conexion = obtener_conexion()
        
        try:
            with conexion.cursor() as cursor:
                # Eliminar permisos actuales
                cursor.execute("DELETE FROM ROL_PERMISO WHERE id_rol = %s", (id_rol,))
                
                # Insertar nuevos permisos
                if lista_permisos:
                    valores = [(id_rol, id_permiso) for id_permiso in lista_permisos]
                    cursor.executemany("""
                        INSERT INTO ROL_PERMISO (id_rol, id_permiso)
                        VALUES (%s, %s)
                    """, valores)
                
                conexion.commit()
                return True
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()


class Permiso:
    """Clase para gestionar permisos del sistema"""
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los permisos agrupados por módulo"""
        conexion = obtener_conexion()
        permisos = []
        
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT id_permiso, nombre, codigo, descripcion, modulo, estado
                    FROM PERMISO
                    WHERE estado = 'Activo'
                    ORDER BY modulo, nombre
                """)
                
                for row in cursor.fetchall():
                    permisos.append({
                        'id_permiso': row['id_permiso'],
                        'nombre': row['nombre'],
                        'codigo': row['codigo'],
                        'descripcion': row['descripcion'],
                        'modulo': row['modulo'],
                        'estado': row['estado']
                    })
        finally:
            conexion.close()
        
        return permisos
    
    @staticmethod
    def obtener_por_modulo():
        """Obtiene permisos agrupados por módulo"""
        permisos = Permiso.obtener_todos()
        permisos_por_modulo = {}
        
        for permiso in permisos:
            modulo = permiso['modulo']
            if modulo not in permisos_por_modulo:
                permisos_por_modulo[modulo] = []
            permisos_por_modulo[modulo].append(permiso)
        
        return permisos_por_modulo
    
    @staticmethod
    def obtener_ids_por_rol(id_rol):
        """Obtiene solo los IDs de los permisos de un rol (útil para checkboxes)"""
        conexion = obtener_conexion()
        ids_permisos = []
        
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT id_permiso
                    FROM ROL_PERMISO
                    WHERE id_rol = %s
                """, (id_rol,))
                
                ids_permisos = [row['id_permiso'] for row in cursor.fetchall()]
        finally:
            conexion.close()
        
        return ids_permisos
