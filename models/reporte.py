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
    def crear(id_categoria, tipo, descripcion, contenido_json=None, id_empleado=None, 
              id_servicio=None, id_recurso=None):
        """Crea un nuevo reporte"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Generar código único
                codigo = Reporte.generar_codigo()
                
                # Insertar reporte con todas las columnas
                sql = """INSERT INTO REPORTE (codigo, nombre, tipo, descripcion, contenido_json, 
                         estado, fecha_creacion, id_categoria, id_empleado, id_servicio, id_recurso) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    codigo, 
                    descripcion[:100] if descripcion else tipo,  # nombre: primeros 100 chars de descripcion
                    tipo, 
                    descripcion,
                    contenido_json,
                    'Pendiente',
                    datetime.now(),
                    id_categoria, 
                    id_empleado, 
                    id_servicio, 
                    id_recurso
                ))
                
                conexion.commit()
                return {
                    'success': True, 
                    'id_reporte': cursor.lastrowid,
                    'codigo': codigo,
                    'message': 'Reporte creado exitosamente'
                }
        except Exception as e:
            conexion.rollback()
            return {'success': False, 'error': str(e)}
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
            # Validar y convertir id_reporte a entero
            try:
                id_reporte = int(id_reporte) if id_reporte else None
                if not id_reporte:
                    return None
            except (ValueError, TypeError):
                print(f"Error: id_reporte inválido: {id_reporte}")
                return None
            
            with conexion.cursor() as cursor:
                sql = """
                    SELECT r.id_reporte,
                           r.codigo,
                           r.nombre,
                           r.tipo,
                           r.descripcion,
                           r.estado,
                           r.fecha_creacion,
                           r.id_categoria,
                           r.id_empleado,
                           r.id_servicio,
                           r.id_recurso,
                           c.nombre as categoria,
                           c.descripcion as descripcion_categoria,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
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

    @staticmethod
    def agregar_archivo(id_reporte, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes):
        """Agrega un archivo adjunto a un reporte"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO REPORTE_ARCHIVO 
                         (id_reporte, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes)
                         VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (id_reporte, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes))
                conexion.commit()
                return {'success': True, 'id_archivo': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_archivos(id_reporte):
        """Obtiene todos los archivos adjuntos de un reporte"""
        conexion = obtener_conexion()
        try:
            # Validar y convertir id_reporte a entero
            try:
                id_reporte = int(id_reporte) if id_reporte else None
                if not id_reporte:
                    return []
            except (ValueError, TypeError) as e:
                print(f"Error: id_reporte inválido: {id_reporte}, error: {e}")
                return []
            
            with conexion.cursor() as cursor:
                sql = """SELECT id_archivo, nombre_archivo, ruta_archivo, tipo_archivo, 
                         CAST(tamano_bytes AS SIGNED) as tamano_bytes, 
                         DATE_FORMAT(fecha_subida, '%%d/%%m/%%Y %%H:%%i') as fecha_subida
                         FROM REPORTE_ARCHIVO 
                         WHERE id_reporte = %s
                         ORDER BY fecha_subida DESC"""
                cursor.execute(sql, (id_reporte,))
                resultados = cursor.fetchall()
                return resultados if resultados else []
        except Exception as e:
            print(f"Error en obtener_archivos (id_reporte={id_reporte}): {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            conexion.close()

    @staticmethod
    def eliminar_archivo(id_archivo):
        """Elimina un archivo adjunto"""
        conexion = obtener_conexion()
        try:
            # Validar y convertir id_archivo a entero
            try:
                id_archivo = int(id_archivo) if id_archivo else None
                if not id_archivo:
                    return False
            except (ValueError, TypeError):
                print(f"Error: id_archivo inválido: {id_archivo}")
                return False
            
            with conexion.cursor() as cursor:
                # Primero obtener la ruta del archivo
                cursor.execute("SELECT ruta_archivo FROM REPORTE_ARCHIVO WHERE id_archivo = %s", (id_archivo,))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Eliminar el registro de la BD
                    cursor.execute("DELETE FROM REPORTE_ARCHIVO WHERE id_archivo = %s", (id_archivo,))
                    conexion.commit()
                    return {'success': True, 'ruta_archivo': resultado['ruta_archivo']}
                return {'success': False, 'error': 'Archivo no encontrado'}
        except Exception as e:
            conexion.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conexion.close()
            conexion.close()

    @staticmethod
    def buscar_reportes(filtros):
        """Busca reportes con filtros en tiempo real"""
        print(f"[MODELO] buscar_reportes llamado con: {filtros}")
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Query optimizada para MySQL con subconsulta para contar archivos
                sql = """
                    SELECT r.id_reporte,
                           r.codigo,
                           r.nombre,
                           r.tipo,
                           r.descripcion,
                           r.contenido_json,
                           r.estado,
                           r.fecha_creacion,
                           r.id_categoria,
                           r.id_empleado,
                           r.id_servicio,
                           r.id_recurso,
                           c.nombre as categoria,
                           CONCAT(e.nombres, ' ', e.apellidos) as empleado,
                           s.nombre as servicio,
                           DATE_FORMAT(r.fecha_creacion, '%%d/%%m/%%Y %%H:%%i') as fecha_formateada,
                           COALESCE((SELECT COUNT(*) FROM REPORTE_ARCHIVO ra WHERE ra.id_reporte = r.id_reporte), 0) as num_archivos
                    FROM REPORTE r
                    LEFT JOIN CATEGORIA c ON r.id_categoria = c.id_categoria
                    LEFT JOIN EMPLEADO e ON r.id_empleado = e.id_empleado
                    LEFT JOIN SERVICIO s ON r.id_servicio = s.id_servicio
                    WHERE 1=1
                """
                
                params = []
                
                # Filtro por texto (busca en código, nombre, tipo)
                if filtros.get('busqueda'):
                    sql += " AND (r.codigo LIKE %s OR r.nombre LIKE %s OR r.tipo LIKE %s)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])
                
                # Filtro por categoría (asegurar que sea entero o None)
                if filtros.get('id_categoria'):
                    try:
                        id_cat = int(filtros['id_categoria']) if filtros['id_categoria'] else None
                        if id_cat:
                            sql += " AND r.id_categoria = %s"
                            params.append(id_cat)
                    except (ValueError, TypeError):
                        pass  # Ignorar si no se puede convertir a entero
                
                # Filtro por tipo
                if filtros.get('tipo'):
                    sql += " AND r.tipo = %s"
                    params.append(str(filtros['tipo']))
                
                # Filtro por rango de fechas
                if filtros.get('fecha_inicio'):
                    sql += " AND DATE(r.fecha_creacion) >= %s"
                    params.append(str(filtros['fecha_inicio']))
                
                if filtros.get('fecha_fin'):
                    sql += " AND DATE(r.fecha_creacion) <= %s"
                    params.append(str(filtros['fecha_fin']))
                
                sql += " ORDER BY r.fecha_creacion DESC"
                
                # Límite de resultados para búsqueda en tiempo real
                limite = 50  # Valor por defecto
                if filtros.get('limite'):
                    try:
                        limite = int(filtros['limite'])
                    except (ValueError, TypeError):
                        limite = 50
                
                # Añadir límite como parámetro
                sql += " LIMIT %s"
                params.append(limite)
                
                print(f"[MODELO] SQL final: {sql}")
                print(f"[MODELO] Params: {params}")
                print(f"[MODELO] Tipos de params: {[type(p).__name__ for p in params]}")
                
                # Ejecutar la consulta
                cursor.execute(sql, tuple(params))
                    
                return cursor.fetchall()
        finally:
            conexion.close()
