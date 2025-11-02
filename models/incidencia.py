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
                    i.categoria,
                    i.prioridad,
                    aei.estado_historial as estado,
                    aei.fecha_resolucion,
                    e.nombres as empleado_nombres,
                    e.apellidos as empleado_apellidos,
                    aei.observaciones
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
                LEFT JOIN EMPLEADO e ON aei.id_empleado = e.id_empleado
                ORDER BY i.id_incidencia DESC
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
                    i.categoria,
                    i.prioridad,
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

            # Filtro por categoría
            if filtros.get('categoria') and filtros['categoria'].strip() and filtros['categoria'] != '':
                query += " AND i.categoria = %s"
                params.append(filtros['categoria'].strip())

            # Filtro por prioridad
            if filtros.get('prioridad') and filtros['prioridad'].strip() and filtros['prioridad'] != '':
                query += " AND i.prioridad = %s"
                params.append(filtros['prioridad'].strip())

            query += " ORDER BY i.id_incidencia DESC"

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

    @staticmethod
    def actualizar_completa(id_incidencia, descripcion, estado, prioridad, categoria, observaciones):
        """Actualiza una incidencia con todos sus campos"""
        conexion = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Actualizar tabla INCIDENCIA (descripción, prioridad, categoría)
            if descripcion or prioridad or categoria:
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

                if updates_incidencia:
                    query_incidencia = f"""
                        UPDATE INCIDENCIA
                        SET {', '.join(updates_incidencia)}
                        WHERE id_incidencia = %s
                    """
                    params_incidencia.append(id_incidencia)
                    cursor.execute(query_incidencia, params_incidencia)

            # Actualizar tabla ASIGNAR_EMPLEADO_INCIDENCIA (estado, observaciones)
            if estado or observaciones:
                updates_asignacion = []
                params_asignacion = []

                if estado:
                    updates_asignacion.append("estado_historial = %s")
                    params_asignacion.append(estado)

                if observaciones is not None:  # Permitir string vacío
                    updates_asignacion.append("observaciones = %s")
                    params_asignacion.append(observaciones)

                # Si el estado es 'Resuelta' o 'Cerrada', actualizar fecha_resolucion
                if estado in ['Resuelta', 'Cerrada']:
                    updates_asignacion.append("fecha_resolucion = COALESCE(fecha_resolucion, NOW())")

                if updates_asignacion:
                    query_asignacion = f"""
                        UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                        SET {', '.join(updates_asignacion)}
                        WHERE id_incidencia = %s
                    """
                    params_asignacion.append(id_incidencia)
                    cursor.execute(query_asignacion, params_asignacion)

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
    def resolver_incidencia(id_incidencia, comentario=''):
        """Marca una incidencia como resuelta"""
        conexion = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Verificar que la incidencia existe y tiene asignación
            cursor.execute("""
                SELECT id_historial FROM ASIGNAR_EMPLEADO_INCIDENCIA
                WHERE id_incidencia = %s
            """, (id_incidencia,))

            asignacion = cursor.fetchone()

            if not asignacion:
                # Si no hay asignación, no se puede resolver
                print(f"No se puede resolver la incidencia {id_incidencia}: no tiene empleado asignado")
                return False

            # Actualizar el estado a 'Resuelta' y agregar comentario a observaciones
            observaciones_actuales = ""
            cursor.execute("""
                SELECT observaciones FROM ASIGNAR_EMPLEADO_INCIDENCIA
                WHERE id_incidencia = %s
            """, (id_incidencia,))

            resultado = cursor.fetchone()
            if resultado and resultado['observaciones']:
                observaciones_actuales = resultado['observaciones']

            # Agregar el comentario de resolución
            if comentario:
                if observaciones_actuales:
                    observaciones_nuevas = f"{observaciones_actuales}\n\n[RESOLUCIÓN]: {comentario}"
                else:
                    observaciones_nuevas = f"[RESOLUCIÓN]: {comentario}"
            else:
                observaciones_nuevas = observaciones_actuales if observaciones_actuales else "Incidencia resuelta"

            # Actualizar estado y fecha de resolución
            query = """
                UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                SET estado_historial = 'Resuelta',
                    fecha_resolucion = NOW(),
                    observaciones = %s
                WHERE id_incidencia = %s
            """
            cursor.execute(query, (observaciones_nuevas, id_incidencia))

            conexion.commit()
            return True

        except Exception as e:
            print(f"Error resolviendo incidencia: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def crear(id_paciente, descripcion, categoria, prioridad):
        """Crea una nueva incidencia"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                INSERT INTO INCIDENCIA (descripcion, fecha_registro, id_paciente, categoria, prioridad)
                VALUES (%s, CURDATE(), %s, %s, %s)
            """
            cursor.execute(query, (descripcion, id_paciente, categoria, prioridad))
            conexion.commit()

            return cursor.lastrowid

        except Exception as e:
            print(f"Error creando incidencia: {e}")
            return None
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def asignar_empleado(id_incidencia, id_empleado, observaciones=''):
        """Asigna un empleado a una incidencia"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                INSERT INTO ASIGNAR_EMPLEADO_INCIDENCIA
                (id_incidencia, id_empleado, observaciones, estado_historial, fecha_resolucion)
                VALUES (%s, %s, %s, 'Abierta', NULL)
            """
            cursor.execute(query, (id_incidencia, id_empleado, observaciones))
            conexion.commit()
            return True

        except Exception as e:
            print(f"Error asignando empleado: {e}")
            return False
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def actualizar_asignacion(id_incidencia, id_empleado, estado, prioridad):
        """Actualiza la asignación de una incidencia"""
        conexion = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Verificar que la incidencia existe
            query_incidencia = "SELECT id_incidencia FROM INCIDENCIA WHERE id_incidencia = %s"
            cursor.execute(query_incidencia, (id_incidencia,))
            if not cursor.fetchone():
                print(f"Incidencia {id_incidencia} no encontrada")
                return False

            # Verificar que el empleado existe
            query_empleado = "SELECT id_empleado FROM EMPLEADO WHERE id_empleado = %s"
            cursor.execute(query_empleado, (id_empleado,))
            if not cursor.fetchone():
                print(f"Empleado {id_empleado} no encontrado")
                return False

            # Verificar si ya existe asignación
            query_check = """
                SELECT id_historial FROM ASIGNAR_EMPLEADO_INCIDENCIA
                WHERE id_incidencia = %s
            """
            cursor.execute(query_check, (id_incidencia,))
            asignacion = cursor.fetchone()

            if asignacion:
                # Actualizar asignación existente
                query = """
                    UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                    SET id_empleado = %s, estado_historial = %s
                    WHERE id_incidencia = %s
                """
                cursor.execute(query, (id_empleado, estado, id_incidencia))

                # Si el estado es 'Resuelta' o 'Cerrada', actualizar fecha de resolución
                if estado in ['Resuelta', 'Cerrada']:
                    query_fecha = """
                        UPDATE ASIGNAR_EMPLEADO_INCIDENCIA
                        SET fecha_resolucion = COALESCE(fecha_resolucion, NOW())
                        WHERE id_incidencia = %s
                    """
                    cursor.execute(query_fecha, (id_incidencia,))
            else:
                # Crear nueva asignación
                query = """
                    INSERT INTO ASIGNAR_EMPLEADO_INCIDENCIA
                    (id_incidencia, id_empleado, estado_historial, observaciones, fecha_resolucion)
                    VALUES (%s, %s, %s, '', NULL)
                """
                cursor.execute(query, (id_incidencia, id_empleado, estado))

            # Actualizar prioridad en la tabla INCIDENCIA
            if prioridad:
                query_prioridad = """
                    UPDATE INCIDENCIA
                    SET prioridad = %s
                    WHERE id_incidencia = %s
                """
                cursor.execute(query_prioridad, (prioridad, id_incidencia))

            conexion.commit()
            return True

        except Exception as e:
            print(f"Error actualizando asignación: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_sin_asignar():
        """Obtiene incidencias que NO tienen un empleado asignado"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT
                    i.id_incidencia,
                    COALESCE(i.descripcion, 'Sin descripción') as descripcion,
                    DATE_FORMAT(i.fecha_registro, '%d/%m/%Y') as fecha_registro,
                    COALESCE(p.nombres, '') as paciente_nombres,
                    COALESCE(p.apellidos, '') as paciente_apellidos,
                    COALESCE(i.categoria, 'Sin categoría') as categoria,
                    COALESCE(i.prioridad, 'Media') as prioridad,
                    'Sin asignar' as estado
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
                WHERE aei.id_historial IS NULL OR aei.id_empleado IS NULL
                ORDER BY i.fecha_registro DESC
            """

            cursor.execute(query)
            incidencias = cursor.fetchall()

            for inc in incidencias:
                paciente_nombre = f"{inc['paciente_nombres']} {inc['paciente_apellidos']}".strip()
                inc['paciente'] = paciente_nombre if paciente_nombre else 'No asignado'
                inc['responsable_actual'] = None

                # Asegurar que todos los campos tengan valores por defecto
                if not inc.get('descripcion'):
                    inc['descripcion'] = 'Sin descripción'
                if not inc.get('categoria'):
                    inc['categoria'] = 'Sin categoría'
                if not inc.get('prioridad'):
                    inc['prioridad'] = 'Media'

            return incidencias

        except Exception as e:
            print(f"Error obteniendo incidencias sin asignar: {e}")
            return []
        finally:
            if 'conexion' in locals():
                conexion.close()

    @staticmethod
    def obtener_empleados_disponibles():
        """Obtiene la lista de empleados disponibles activos"""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            query = """
                SELECT 
                    id_empleado, 
                    COALESCE(nombres, '') as nombres,
                    COALESCE(apellidos, '') as apellidos
                FROM EMPLEADO
                WHERE estado = 'Activo'
                ORDER BY nombres, apellidos
            """
            cursor.execute(query)
            empleados = cursor.fetchall()

            # Procesar nombres y generar nombre_completo
            for emp in empleados:
                nombres = emp.get('nombres', '').strip() if emp.get('nombres') else ''
                apellidos = emp.get('apellidos', '').strip() if emp.get('apellidos') else ''
                
                nombre_completo = f"{nombres} {apellidos}".strip()
                if not nombre_completo:
                    emp['nombre_completo'] = f"Empleado #{emp['id_empleado']}"
                else:
                    emp['nombre_completo'] = nombre_completo

            return empleados

        except Exception as e:
            print(f"Error obteniendo empleados: {e}")
            return []
        finally:
            if 'conexion' in locals():
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
                    aei.estado_historial as estado,
                    DATE_FORMAT(aei.fecha_resolucion, '%d/%m/%Y') as fecha_resolucion,
                    aei.observaciones
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
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
                query += " AND aei.estado_historial = %s"
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
