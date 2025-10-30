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
                    CONCAT(LPAD(DAY(i.fecha_registro), 2, '0'), '/', LPAD(MONTH(i.fecha_registro), 2, '0'), '/', YEAR(i.fecha_registro)) as fecha_registro,
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
            if filtros.get('paciente') and filtros['paciente'].strip():
                terminos_paciente = filtros['paciente'].strip().split()
                for termino in terminos_paciente:
                    query += " AND LOWER(CONCAT(p.nombres, ' ', p.apellidos)) LIKE LOWER(%s)"
                    params.append(f"%{termino}%")

            # Filtro por empleado
            if filtros.get('empleado') and filtros['empleado'].strip():
                terminos_empleado = filtros['empleado'].strip().split()
                for termino in terminos_empleado:
                    query += " AND LOWER(CONCAT(e.nombres, ' ', e.apellidos)) LIKE LOWER(%s)"
                    params.append(f"%{termino}%")

            # Filtro por fecha de registro
            if filtros.get('fecha_registro') and filtros['fecha_registro']:
                query += " AND DATE(i.fecha_registro) = %s"
                params.append(filtros['fecha_registro'])

            # Filtro por fecha de resolución
            if filtros.get('fecha_resolucion') and filtros['fecha_resolucion']:
                query += " AND DATE(aei.fecha_resolucion) = %s"
                params.append(filtros['fecha_resolucion'])

            # Filtro por estado
            if filtros.get('estado') and filtros['estado'].strip() and filtros['estado'] != '':
                query += " AND aei.estado_historial = %s"
                params.append(filtros['estado'].strip())

            query += " ORDER BY i.id_incidencia ASC"

            cursor.execute(query, params)
            incidencias = cursor.fetchall()

            # Formatear los datos para el frontend
            for inc in incidencias:
                inc['paciente'] = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}" if inc['paciente_nombres'] else 'No asignado'
                inc['empleado'] = f"{inc['empleado_nombres']} {inc['empleado_apellidos']}" if inc['empleado_nombres'] else 'No asignado'

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
                WHERE LOWER(CONCAT(nombres, ' ', apellidos)) LIKE LOWER(%s)
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
    def buscar_empleados(termino):
        """Busca empleados para autocompletado"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT id_empleado, nombres, apellidos
                FROM EMPLEADO
                WHERE LOWER(CONCAT(nombres, ' ', apellidos)) LIKE LOWER(%s)
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
    def actualizar(id_incidencia, descripcion, estado, observaciones):
        """Actualiza una incidencia existente"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                SET estado_historial = %s, observaciones = %s
                WHERE id_incidencia = %s
            """
            cursor.execute(query, (estado, observaciones, id_incidencia))

            # Si la descripción cambió, actualizar también la tabla INCIDENCIA
            if descripcion:
                query_desc = """
                    UPDATE INCIDENCIA
                    SET descripcion = %s
                    WHERE id_incidencia = %s
                """
                cursor.execute(query_desc, (descripcion, id_incidencia))

            # Si el estado es 'Resuelta', actualizar fecha_resolucion
            if estado == 'Resuelta':
                query_fecha = """
                    UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                    SET fecha_resolucion = NOW()
                    WHERE id_incidencia = %s
                """
                cursor.execute(query_fecha, (id_incidencia,))

            conexion.commit()
            return True

        except Exception as e:
            print(f"Error actualizando incidencia: {e}")
            return False
        finally:
            if 'conexion' in locals():
                conexion.close()
