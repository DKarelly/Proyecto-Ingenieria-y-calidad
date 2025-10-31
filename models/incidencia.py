from bd import obtener_conexion

class Incidencia:
    @staticmethod
    def obtener_todas():
        """Obtiene todas las incidencias con información relacionada"""
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
                    aei.estado_historial as estado,
                    aei.fecha_resolucion,
                    e.nombres as empleado_nombres,
                    e.apellidos as empleado_apellidos,
                    aei.observaciones
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
                LEFT JOIN EMPLEADO e ON aei.id_empleado = e.id_empleado
                ORDER BY i.id_incidencia ASC
            """

            cursor.execute(query)
            incidencias = cursor.fetchall()

            # Formatear los datos para el frontend
            for inc in incidencias:
                inc['paciente'] = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}" if inc['paciente_nombres'] else 'No asignado'
                inc['empleado'] = f"{inc['empleado_nombres']} {inc['empleado_apellidos']}" if inc['empleado_nombres'] else 'No asignado'
                inc['prioridad'] = 'Media'  # Por defecto, se puede agregar campo en BD después
                inc['categoria'] = 'General'  # Por defecto, se puede agregar campo en BD después

            return incidencias

        except Exception as e:
            print(f"Error obteniendo incidencias: {e}")
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def buscar(filtros):
        """Busca incidencias con filtros aplicados"""
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
                    aei.estado_historial as estado,
                    aei.fecha_resolucion,
                    e.nombres as empleado_nombres,
                    e.apellidos as empleado_apellidos,
                    aei.observaciones
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
                LEFT JOIN EMPLEADO e ON aei.id_empleado = e.id_empleado
                WHERE 1=1
            """

            params = []

            # Filtro por paciente
            if filtros.get('paciente'):
                query += " AND (CONCAT(p.nombres, ' ', p.apellidos) LIKE %s)"
                params.append(f"%{filtros['paciente']}%")

            # Filtro por empleado
            if filtros.get('empleado'):
                query += " AND (CONCAT(e.nombres, ' ', e.apellidos) LIKE %s)"
                params.append(f"%{filtros['empleado']}%")

            # Filtro por fecha de registro
            if filtros.get('fecha_registro_desde'):
                query += " AND i.fecha_registro >= %s"
                params.append(filtros['fecha_registro_desde'])

            if filtros.get('fecha_registro_hasta'):
                query += " AND i.fecha_registro <= %s"
                params.append(filtros['fecha_registro_hasta'])

            # Filtro por fecha de resolución
            if filtros.get('fecha_resolucion_desde'):
                query += " AND aei.fecha_resolucion >= %s"
                params.append(filtros['fecha_resolucion_desde'])

            if filtros.get('fecha_resolucion_hasta'):
                query += " AND aei.fecha_resolucion <= %s"
                params.append(filtros['fecha_resolucion_hasta'])

            # Filtro por estado
            if filtros.get('estado') and filtros['estado'] != '':
                query += " AND aei.estado_historial = %s"
                params.append(filtros['estado'])

            query += " ORDER BY i.id_incidencia ASC"

            cursor.execute(query, params)
            incidencias = cursor.fetchall()

            # Formatear los datos para el frontend
            for inc in incidencias:
                inc['paciente'] = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}" if inc['paciente_nombres'] else 'No asignado'
                inc['empleado'] = f"{inc['empleado_nombres']} {inc['empleado_apellidos']}" if inc['empleado_nombres'] else 'No asignado'
                inc['prioridad'] = 'Media'  # Por defecto
                inc['categoria'] = 'General'  # Por defecto

            return incidencias

        except Exception as e:
            print(f"Error buscando incidencias: {e}")
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def buscar_pacientes(termino):
        """Busca pacientes para autocompletado"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT id_paciente, nombres, apellidos
                FROM PACIENTE
                WHERE CONCAT(nombres, ' ', apellidos) LIKE %s
                LIMIT 10
            """

            cursor.execute(query, (f"%{termino}%",))
            pacientes = cursor.fetchall()

            # Formatear para autocompletado
            for p in pacientes:
                p['nombre_completo'] = f"{p['nombres']} {p['apellidos']}"

            return pacientes

        except Exception as e:
            print(f"Error buscando pacientes: {e}")
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
    def buscar_empleados(termino):
        """Busca empleados para autocompletado"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT id_empleado, nombres, apellidos
                FROM EMPLEADO
                WHERE CONCAT(nombres, ' ', apellidos) LIKE %s
                LIMIT 10
            """

            cursor.execute(query, (f"%{termino}%",))
            empleados = cursor.fetchall()

            # Formatear para autocompletado
            for e in empleados:
                e['nombre_completo'] = f"{e['nombres']} {e['apellidos']}"

            return empleados

        except Exception as e:
            print(f"Error buscando empleados: {e}")
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def crear(descripcion, id_paciente, categoria=None, id_empleado=None):
        """Crea una nueva incidencia"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Insertar la incidencia
            query = """
                INSERT INTO INCIDENCIA (descripcion, id_paciente, fecha_registro, categoria)
                VALUES (%s, %s, NOW(), %s)
            """

            cursor.execute(query, (descripcion, id_paciente, categoria))
            conexion.commit()

            id_incidencia = cursor.lastrowid

            # Si se proporciona un empleado, crear la asignación automática
            if id_empleado:
                query_asignar = """
                    INSERT INTO ASIGNAR_EMPLEADO_INCIDENCIA 
                    (id_incidencia, id_empleado, estado_historial, observaciones)
                    VALUES (%s, %s, 'Abierta', 'Incidencia creada')
                """
                cursor.execute(query_asignar, (id_incidencia, id_empleado))
                conexion.commit()

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
    def asignar_empleado(id_incidencia, id_empleado, observaciones=''):
        """Asigna un empleado a una incidencia"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Verificar si ya existe una asignación
            query_check = """
                SELECT id_historial FROM ASIGNAR_EMPLEADO_INCIDENCIA
                WHERE id_incidencia = %s
            """
            cursor.execute(query_check, (id_incidencia,))
            asignacion_existente = cursor.fetchone()

            if asignacion_existente:
                # Actualizar asignación existente
                query_update = """
                    UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                    SET id_empleado = %s, 
                        observaciones = %s,
                        estado_historial = 'Asignada'
                    WHERE id_incidencia = %s
                """
                cursor.execute(query_update, (id_empleado, observaciones, id_incidencia))
            else:
                # Crear nueva asignación
                query_insert = """
                    INSERT INTO ASIGNAR_EMPLEADO_INCIDENCIA 
                    (id_incidencia, id_empleado, estado_historial, observaciones)
                    VALUES (%s, %s, 'Asignada', %s)
                """
                cursor.execute(query_insert, (id_incidencia, id_empleado, observaciones))

            conexion.commit()

            return {
                'success': True,
                'message': 'Empleado asignado exitosamente'
            }

        except Exception as e:
            print(f"Error asignando empleado: {e}")
            if 'conexion' in locals():
                conexion.rollback()
            return {
                'success': False,
                'message': f'Error al asignar empleado: {str(e)}'
            }
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def actualizar_estado(id_historial, estado, observaciones):
        """Actualiza el estado de una asignación de incidencia"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Si el estado es "Resuelta", establecer fecha de resolución
            if estado == 'Resuelta':
                query = """
                    UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                    SET estado_historial = %s,
                        observaciones = %s,
                        fecha_resolucion = NOW()
                    WHERE id_historial = %s
                """
            else:
                query = """
                    UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                    SET estado_historial = %s,
                        observaciones = %s
                    WHERE id_historial = %s
                """

            cursor.execute(query, (estado, observaciones, id_historial))
            conexion.commit()

            return {
                'success': True,
                'message': 'Estado actualizado exitosamente'
            }

        except Exception as e:
            print(f"Error actualizando estado: {e}")
            if 'conexion' in locals():
                conexion.rollback()
            return {
                'success': False,
                'message': f'Error al actualizar estado: {str(e)}'
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
                    aei.id_historial,
                    aei.estado_historial as estado,
                    DATE_FORMAT(aei.fecha_resolucion, '%d/%m/%Y %H:%i') as fecha_resolucion,
                    aei.id_empleado,
                    e.nombres as empleado_nombres,
                    e.apellidos as empleado_apellidos,
                    aei.observaciones
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
                LEFT JOIN EMPLEADO e ON aei.id_empleado = e.id_empleado
                WHERE i.id_incidencia = %s
            """

            cursor.execute(query, (id_incidencia,))
            incidencia = cursor.fetchone()

            if incidencia:
                incidencia['paciente'] = f"{incidencia['paciente_nombres']} {incidencia['paciente_apellidos']}" if incidencia['paciente_nombres'] else 'No asignado'
                incidencia['empleado'] = f"{incidencia['empleado_nombres']} {incidencia['empleado_apellidos']}" if incidencia['empleado_nombres'] else 'No asignado'

            return incidencia

        except Exception as e:
            print(f"Error obteniendo incidencia: {e}")
            return None
        finally:
            if 'conexion' in locals():
                conexion.close()
