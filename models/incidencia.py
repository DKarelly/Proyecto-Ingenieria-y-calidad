from bd import obtener_conexion

class Incidencia:
    @staticmethod
    def obtener_todas():
        """Obtiene todas las incidencias con información relacionada"""
        print("[DEBUG] obtener_todas() called")
        try:
            import pymysql.cursors
            print("[DEBUG] Importing pymysql.cursors")
            conexion = obtener_conexion()
            print(f"[DEBUG] Connection obtained: {conexion}")
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            print("[DEBUG] Cursor created with DictCursor")

            query = """
                SELECT
                    i.id_incidencia,
                    i.descripcion,
                    i.categoria,
                    i.prioridad,
                    i.estado,
                    DATE_FORMAT(i.fecha_registro, '%d/%m/%Y') as fecha_registro,
                    DATE_FORMAT(i.fecha_resolucion, '%d/%m/%Y') as fecha_resolucion,
                    p.nombres as paciente_nombres,
                    p.apellidos as paciente_apellidos
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                ORDER BY i.id_incidencia DESC
            """
            print(f"[DEBUG] Query: {query}")

            cursor.execute(query)
            print("[DEBUG] Query executed")
            incidencias = cursor.fetchall()
            print(f"[DEBUG] Raw incidencias: {incidencias}")
            print(f"[DEBUG] Number of incidencias: {len(incidencias)}")

            # Formatear los datos para el frontend
            for inc in incidencias:
                inc['paciente'] = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}" if inc['paciente_nombres'] else 'No asignado'

            print(f"[DEBUG] Formatted incidencias: {incidencias}")
            return incidencias

        except Exception as e:
            print(f"Error obteniendo incidencias: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()
                print("[DEBUG] Connection closed")

    @staticmethod
    def obtener_pendientes():
        """Obtiene solo las incidencias con estado 'En progreso'"""
        try:
            import pymysql.cursors
            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            query = """
                SELECT
                    i.id_incidencia,
                    i.descripcion,
                    i.categoria,
                    i.prioridad,
                    i.estado,
                    DATE_FORMAT(i.fecha_registro, '%d/%m/%Y') as fecha_registro,
                    DATE_FORMAT(i.fecha_resolucion, '%d/%m/%Y') as fecha_resolucion,
                    p.nombres as paciente_nombres,
                    p.apellidos as paciente_apellidos
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                WHERE i.estado = 'En progreso'
                ORDER BY i.id_incidencia DESC
            """

            cursor.execute(query)
            incidencias = cursor.fetchall()

            # Formatear los datos para el frontend
            for inc in incidencias:
                inc['paciente'] = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}" if inc['paciente_nombres'] else 'No asignado'

            return incidencias

        except Exception as e:
            print(f"Error obteniendo incidencias pendientes: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def buscar(filtros):
        """Busca incidencias con filtros aplicados"""
        try:
            import pymysql.cursors
            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            query = """
                SELECT
                    i.id_incidencia,
                    i.descripcion,
                    DATE_FORMAT(i.fecha_registro, '%%d/%%m/%%Y') as fecha_registro,
                    DATE_FORMAT(i.fecha_resolucion, '%%d/%%m/%%Y') as fecha_resolucion,
                    p.nombres as paciente_nombres,
                    p.apellidos as paciente_apellidos,
                    i.categoria,
                    i.prioridad,
                    i.estado
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                WHERE 1=1
            """

            params = []

            # Filtro por paciente (mejorado para buscar por nombre completo o partes)
            if filtros.get('paciente') and filtros['paciente'].strip():
                termino_paciente = filtros['paciente'].strip()
                # Buscar que el nombre O apellido O nombre completo contenga el término (búsqueda más flexible)
                # Buscar en nombres O apellidos O nombre completo concatenado
                query += " AND (LOWER(p.nombres) LIKE LOWER(%s) OR LOWER(p.apellidos) LIKE LOWER(%s) OR LOWER(CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, ''))) LIKE LOWER(%s))"
                params.append(f"%{termino_paciente}%")
                params.append(f"%{termino_paciente}%")
                params.append(f"%{termino_paciente}%")
                print(f"[BUSCAR] Filtrando por paciente: '{termino_paciente}'")

            # Filtro por fecha de registro
            if filtros.get('fecha_registro') and filtros['fecha_registro']:
                query += " AND DATE(i.fecha_registro) = %s"
                params.append(filtros['fecha_registro'])

            # Filtro por categoría
            if filtros.get('categoria') and filtros['categoria'].strip() and filtros['categoria'] != '':
                query += " AND i.categoria = %s"
                params.append(filtros['categoria'].strip())

            # Filtro por prioridad
            if filtros.get('prioridad') and filtros['prioridad'].strip() and filtros['prioridad'] != '':
                query += " AND i.prioridad = %s"
                params.append(filtros['prioridad'].strip())

            # Filtro por estado
            # Si se busca por paciente, mostrar TODOS los estados (sin filtrar)
            # Si NO se busca por paciente, por defecto mostrar solo "En progreso"
            if not filtros.get('paciente') or not filtros['paciente'].strip():
                # Si no hay búsqueda por paciente, filtrar por "En progreso" por defecto
                query += " AND i.estado = 'En progreso'"
            elif filtros.get('estado') and filtros['estado'].strip() and filtros['estado'] != '':
                # Si hay búsqueda por paciente pero también hay un estado específico seleccionado, usarlo
                query += " AND i.estado = %s"
                params.append(filtros['estado'].strip())
            # Si hay búsqueda por paciente pero NO hay estado seleccionado, NO filtrar por estado (mostrar todos)

            query += " ORDER BY i.id_incidencia DESC"

            print(f"[BUSCAR] Query SQL: {query}")
            print(f"[BUSCAR] Params: {params}")
            
            cursor.execute(query, params)
            incidencias = cursor.fetchall()

            print(f"[BUSCAR] Incidencias encontradas: {len(incidencias)}")

            # Formatear los datos para el frontend
            for inc in incidencias:
                inc['paciente'] = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}" if inc['paciente_nombres'] else 'No asignado'

            print(f"[BUSCAR] Incidencias formateadas: {len(incidencias)}")
            return incidencias

        except Exception as e:
            print(f"Error buscando incidencias: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def buscar_pacientes(termino):
        """Busca pacientes para autocompletado"""
        try:
            import pymysql.cursors
            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            query = """
                SELECT 
                    id_paciente,
                    CONCAT(nombres, ' ', apellidos) as nombre_completo,
                    documento_identidad as dni
                FROM PACIENTE
                WHERE LOWER(CONCAT(nombres, ' ', apellidos)) LIKE LOWER(%s)
                   OR documento_identidad LIKE %s
                ORDER BY nombres, apellidos
                LIMIT 10
            """

            cursor.execute(query, (f"%{termino}%", f"%{termino}%"))
            pacientes = cursor.fetchall()

            return pacientes

        except Exception as e:
            print(f"Error buscando pacientes: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()
    
    @staticmethod
    def obtener_pacientes():
        """Obtiene todos los pacientes activos para selección"""
        try:
            import pymysql.cursors
            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            query = """
                SELECT id_paciente, nombres, apellidos, documento_identidad as dni
                FROM PACIENTE
                ORDER BY nombres, apellidos
            """

            cursor.execute(query)
            pacientes = cursor.fetchall()
            
            print(f"[MODELO INCIDENCIA] Pacientes obtenidos: {len(pacientes)}")

            return pacientes

        except Exception as e:
            print(f"Error obteniendo pacientes: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()



    @staticmethod
    def crear(descripcion, id_paciente, categoria=None, prioridad=None):
        """Crea una nueva incidencia"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Insertar la incidencia
            query = """
                INSERT INTO INCIDENCIA (descripcion, id_paciente, fecha_registro, categoria, prioridad, estado)
                VALUES (%s, %s, NOW(), %s, %s, 'En progreso')
            """

            cursor.execute(query, (descripcion, id_paciente, categoria, prioridad))
            conexion.commit()

            id_incidencia = cursor.lastrowid

            return {
                'success': True,
                'message': 'Incidencia creada exitosamente',
                'id_incidencia': id_incidencia
            }

        except Exception as e:
            print(f"Error creando incidencia: {e}")
            if 'conexion' in locals():
                conexion.rollback()
            return {
                'success': False,
                'message': f'Error al crear incidencia: {str(e)}'
            }
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def actualizar(id_incidencia, descripcion=None, categoria=None, prioridad=None, estado=None):
        """Actualiza una incidencia existente"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Actualizar tabla INCIDENCIA
            updates_incidencia = []
            params_incidencia = []

            if descripcion is not None:
                updates_incidencia.append("descripcion = %s")
                params_incidencia.append(descripcion)

            if categoria is not None:
                updates_incidencia.append("categoria = %s")
                params_incidencia.append(categoria)

            if prioridad is not None:
                updates_incidencia.append("prioridad = %s")
                params_incidencia.append(prioridad)

            if estado is not None:
                updates_incidencia.append("estado = %s")
                params_incidencia.append(estado)
                
                # Si el estado se cambia a 'Resuelta', establecer fecha_resolucion
                if estado == 'Resuelta':
                    updates_incidencia.append("fecha_resolucion = NOW()")

            if updates_incidencia:
                params_incidencia.append(id_incidencia)
                query_incidencia = f"""
                    UPDATE INCIDENCIA
                    SET {', '.join(updates_incidencia)}
                    WHERE id_incidencia = %s
                """
                cursor.execute(query_incidencia, params_incidencia)

            conexion.commit()

            return {
                'success': True,
                'message': 'Incidencia actualizada exitosamente'
            }

        except Exception as e:
            print(f"Error actualizando incidencia: {e}")
            if 'conexion' in locals():
                conexion.rollback()
            return {
                'success': False,
                'message': f'Error al actualizar incidencia: {str(e)}'
            }
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def obtener_por_id(id_incidencia):
        """Obtiene una incidencia específica por su ID"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    i.id_incidencia,
                    i.descripcion,
                    DATE_FORMAT(i.fecha_registro, '%d/%m/%Y %H:%i') as fecha_registro,
                    i.id_paciente,
                    p.nombres as paciente_nombres,
                    p.apellidos as paciente_apellidos,
                    i.estado
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                WHERE i.id_incidencia = %s
            """

            cursor.execute(query, (id_incidencia,))
            incidencia = cursor.fetchone()

            if incidencia:
                incidencia['paciente'] = f"{incidencia['paciente_nombres']} {incidencia['paciente_apellidos']}" if incidencia['paciente_nombres'] else 'No asignado'

            return incidencia

        except Exception as e:
            print(f"Error obteniendo incidencia: {e}")
            return None
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def actualizar_completa(id_incidencia, descripcion, estado, prioridad, categoria):
        """Actualiza una incidencia con todos sus campos"""
        conexion = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Actualizar tabla INCIDENCIA (descripción, prioridad, categoría, estado)
            updates_incidencia = []
            params_incidencia = []

            if descripcion:
                updates_incidencia.append("descripcion = %s")
                params_incidencia.append(descripcion)

            if prioridad:
                updates_incidencia.append("prioridad = %s")
                params_incidencia.append(prioridad)

            if categoria:
                updates_incidencia.append("categoria = %s")
                params_incidencia.append(categoria)

            if estado:
                updates_incidencia.append("estado = %s")
                params_incidencia.append(estado)

            if updates_incidencia:
                query_incidencia = f"""
                    UPDATE INCIDENCIA
                    SET {', '.join(updates_incidencia)}
                    WHERE id_incidencia = %s
                """
                params_incidencia.append(id_incidencia)
                cursor.execute(query_incidencia, params_incidencia)

            conexion.commit()
            return True

        except Exception as e:
            print(f"Error actualizando incidencia completa: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()









    @staticmethod
    def generar_informe(filtros):
        """Genera un informe de incidencias con filtros"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    i.id_incidencia,
                    i.descripcion,
                    DATE_FORMAT(i.fecha_registro, '%d/%m/%Y') as fecha_registro,
                    p.nombres as paciente_nombres,
                    p.apellidos as paciente_apellidos,
                    i.categoria,
                    i.prioridad,
                    i.estado
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                WHERE 1=1
            """

            params = []

            if filtros.get('paciente'):
                query += " AND i.id_paciente = %s"
                params.append(filtros['paciente'])

            if filtros.get('fecha'):
                query += " AND DATE(i.fecha_registro) = %s"
                params.append(filtros['fecha'])

            if filtros.get('categoria'):
                query += " AND i.categoria = %s"
                params.append(filtros['categoria'])

            if filtros.get('estado'):
                query += " AND i.estado = %s"
                params.append(filtros['estado'])

            query += " ORDER BY i.fecha_registro DESC"

            cursor.execute(query, params)
            incidencias = cursor.fetchall()

            for inc in incidencias:
                inc['paciente'] = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}" if inc['paciente_nombres'] else 'No asignado'

            return incidencias

        except Exception as e:
            print(f"Error generando informe: {e}")
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()
