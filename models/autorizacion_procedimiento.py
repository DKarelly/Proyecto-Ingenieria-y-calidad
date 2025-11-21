"""
Modelo para gestionar autorizaciones de procedimientos médicos (exámenes y operaciones)
desde las citas médicas
"""

from bd import obtener_conexion
from datetime import datetime

class AutorizacionProcedimiento:
    """
    Gestiona las autorizaciones que un médico otorga a un paciente durante una cita
    para realizar exámenes u operaciones
    """
    
    def __init__(self, id_autorizacion=None, id_cita=None, id_paciente=None,
                 id_medico_autoriza=None, tipo_procedimiento=None, 
                 id_servicio=None, id_especialidad_requerida=None, id_medico_asignado=None,
                 estado='PENDIENTE', fecha_autorizacion=None, fecha_vencimiento=None,
                 fecha_uso=None, id_reserva_generada=None):
        self.id_autorizacion = id_autorizacion
        self.id_cita = id_cita
        self.id_paciente = id_paciente
        self.id_medico_autoriza = id_medico_autoriza
        self.tipo_procedimiento = tipo_procedimiento  # 'EXAMEN' o 'OPERACION'
        self.id_servicio = id_servicio
        self.id_especialidad_requerida = id_especialidad_requerida
        self.id_medico_asignado = id_medico_asignado
        self.estado = estado  # 'PENDIENTE', 'APROBADA', 'RECHAZADA', 'COMPLETADA', 'VENCIDA'
        self.fecha_autorizacion = fecha_autorizacion
        self.fecha_vencimiento = fecha_vencimiento  # Nueva: fecha límite de uso
        self.fecha_uso = fecha_uso  # Nueva: cuándo fue utilizada
        self.id_reserva_generada = id_reserva_generada  # Nueva: vínculo con reserva/procedimiento

    @staticmethod
    def crear(data):
        """
        Crea una nueva autorización de procedimiento con fecha de vencimiento automática (7 días)
        Envía notificaciones automáticas al paciente y al médico asignado (Puntos 5.1 y 5.2)
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                from datetime import timedelta
                fecha_actual = datetime.now()
                fecha_vencimiento = fecha_actual + timedelta(days=7)  # Vence en 7 días
                
                sql = """INSERT INTO AUTORIZACION_PROCEDIMIENTO (
                    id_cita, id_paciente, id_medico_autoriza, tipo_procedimiento,
                    id_servicio, id_especialidad_requerida, id_medico_asignado, 
                    estado, fecha_autorizacion, fecha_vencimiento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql, (
                    data.get('id_cita'),
                    data.get('id_paciente'),
                    data.get('id_medico_autoriza'),
                    data.get('tipo_procedimiento'),
                    data.get('id_servicio'),
                    data.get('id_especialidad_requerida'),
                    data.get('id_medico_asignado'),
                    'PENDIENTE',
                    fecha_actual,
                    fecha_vencimiento
                ))
                id_autorizacion = cursor.lastrowid
                conexion.commit()
                
                # Enviar notificaciones automáticas
                try:
                    from utils.notificaciones_autorizaciones import (
                        crear_notificacion_autorizacion_paciente,
                        crear_notificacion_autorizacion_medico
                    )
                    
                    # Obtener datos adicionales para las notificaciones
                    cursor.execute("""
                        SELECT s.nombre as nombre_servicio,
                               CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                               u.correo as correo_paciente
                        FROM SERVICIO s
                        INNER JOIN PACIENTE p ON p.id_paciente = %s
                        INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                        WHERE s.id_servicio = %s
                    """, (data.get('id_paciente'), data.get('id_servicio')))
                    info = cursor.fetchone()
                    
                    if info:
                        # Notificación al paciente
                        crear_notificacion_autorizacion_paciente(
                            data.get('id_paciente'),
                            id_autorizacion,
                            data.get('tipo_procedimiento'),
                            info['nombre_servicio'],
                            fecha_vencimiento
                        )
                        
                        # Notificación al médico asignado (si existe)
                        if data.get('id_medico_asignado'):
                            crear_notificacion_autorizacion_medico(
                                data.get('id_medico_asignado'),
                                id_autorizacion,
                                data.get('tipo_procedimiento'),
                                info['nombre_paciente'],
                                info['nombre_servicio']
                            )
                except Exception as notif_error:
                    # No fallar la creación si las notificaciones fallan
                    print(f"Error al enviar notificaciones: {notif_error}")
                
                return {'success': True, 'id_autorizacion': id_autorizacion, 'fecha_vencimiento': fecha_vencimiento}
        except Exception as e:
            conexion.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_autorizacion):
        """Obtiene una autorización por su ID con información completa"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT a.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           CONCAT(med_aut.nombres, ' ', med_aut.apellidos) as medico_autoriza,
                           esp_aut.nombre as especialidad_autoriza,
                           CONCAT(med_asig.nombres, ' ', med_asig.apellidos) as medico_asignado,
                           esp_req.nombre as especialidad_requerida,
                           s.nombre as servicio_nombre,
                           c.fecha_cita,
                           c.diagnostico
                    FROM AUTORIZACION_PROCEDIMIENTO a
                    INNER JOIN PACIENTE p ON a.id_paciente = p.id_paciente
                    INNER JOIN EMPLEADO med_aut ON a.id_medico_autoriza = med_aut.id_empleado
                    INNER JOIN SERVICIO s ON a.id_servicio = s.id_servicio
                    LEFT JOIN ESPECIALIDAD esp_aut ON med_aut.id_especialidad = esp_aut.id_especialidad
                    LEFT JOIN EMPLEADO med_asig ON a.id_medico_asignado = med_asig.id_empleado
                    LEFT JOIN ESPECIALIDAD esp_req ON a.id_especialidad_requerida = esp_req.id_especialidad
                    INNER JOIN CITA c ON a.id_cita = c.id_cita
                    WHERE a.id_autorizacion = %s
                """
                cursor.execute(sql, (id_autorizacion,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_paciente(id_paciente, tipo_procedimiento=None):
        """Obtiene todas las autorizaciones de un paciente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                if tipo_procedimiento:
                    sql = """
                        SELECT a.*,
                               CONCAT(med_aut.nombres, ' ', med_aut.apellidos) as medico_autoriza,
                               esp_req.nombre as especialidad_requerida,
                               c.fecha_cita,
                               c.diagnostico
                        FROM AUTORIZACION_PROCEDIMIENTO a
                        INNER JOIN EMPLEADO med_aut ON a.id_medico_autoriza = med_aut.id_empleado
                        LEFT JOIN ESPECIALIDAD esp_req ON a.id_especialidad_requerida = esp_req.id_especialidad
                        INNER JOIN CITA c ON a.id_cita = c.id_cita
                        WHERE a.id_paciente = %s AND a.tipo_procedimiento = %s
                        ORDER BY a.fecha_autorizacion DESC
                    """
                    cursor.execute(sql, (id_paciente, tipo_procedimiento))
                else:
                    sql = """
                        SELECT a.*,
                               CONCAT(med_aut.nombres, ' ', med_aut.apellidos) as medico_autoriza,
                               esp_req.nombre as especialidad_requerida,
                               c.fecha_cita,
                               c.diagnostico
                        FROM AUTORIZACION_PROCEDIMIENTO a
                        INNER JOIN EMPLEADO med_aut ON a.id_medico_autoriza = med_aut.id_empleado
                        LEFT JOIN ESPECIALIDAD esp_req ON a.id_especialidad_requerida = esp_req.id_especialidad
                        INNER JOIN CITA c ON a.id_cita = c.id_cita
                        WHERE a.id_paciente = %s
                        ORDER BY a.fecha_autorizacion DESC
                    """
                    cursor.execute(sql, (id_paciente,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_cita(id_cita):
        """Obtiene autorizaciones asociadas a una cita"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT a.*,
                           esp_req.nombre as especialidad_requerida,
                           CONCAT(med_asig.nombres, ' ', med_asig.apellidos) as medico_asignado
                    FROM AUTORIZACION_PROCEDIMIENTO a
                    LEFT JOIN ESPECIALIDAD esp_req ON a.id_especialidad_requerida = esp_req.id_especialidad
                    LEFT JOIN EMPLEADO med_asig ON a.id_medico_asignado = med_asig.id_empleado
                    WHERE a.id_cita = %s
                    ORDER BY a.tipo_procedimiento, a.fecha_autorizacion DESC
                """
                cursor.execute(sql, (id_cita,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_pendientes_por_paciente(id_paciente):
        """
        Obtiene autorizaciones pendientes y activas de un paciente para habilitar botones
        Excluye autorizaciones vencidas o ya utilizadas
        
        Una autorización está pendiente si:
        - No tiene fecha_uso (no ha sido utilizada)
        - No tiene id_reserva_generada (no se ha generado reserva)
        - No está vencida (fecha_vencimiento es NULL o es futura)
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT tipo_procedimiento, COUNT(*) as cantidad,
                           MIN(fecha_vencimiento) as proxima_vencimiento
                    FROM AUTORIZACION_PROCEDIMIENTO
                    WHERE id_paciente = %s 
                    AND fecha_uso IS NULL
                    AND (fecha_vencimiento IS NULL OR fecha_vencimiento > NOW())
                    AND id_reserva_generada IS NULL
                    GROUP BY tipo_procedimiento
                """
                cursor.execute(sql, (id_paciente,))
                result = cursor.fetchall()
                
                # Convertir a diccionario para fácil acceso
                permisos = {
                    'examen': False,
                    'operacion': False,
                    'tiene_autorizaciones': False,
                    'detalles': []
                }
                
                for row in result:
                    if row['tipo_procedimiento'] == 'EXAMEN' and row['cantidad'] > 0:
                        permisos['examen'] = True
                        permisos['tiene_autorizaciones'] = True
                        permisos['detalles'].append({
                            'tipo': 'EXAMEN',
                            'cantidad': row['cantidad'],
                            'proxima_vencimiento': row['proxima_vencimiento']
                        })
                    elif row['tipo_procedimiento'] == 'OPERACION' and row['cantidad'] > 0:
                        permisos['operacion'] = True
                        permisos['tiene_autorizaciones'] = True
                        permisos['detalles'].append({
                            'tipo': 'OPERACION',
                            'cantidad': row['cantidad'],
                            'proxima_vencimiento': row['proxima_vencimiento']
                        })
                
                return permisos
        finally:
            conexion.close()

    @staticmethod
    def obtener_medicos_por_especialidad(id_especialidad):
        """Obtiene médicos que pueden realizar procedimientos de una especialidad específica"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT e.id_empleado,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_completo,
                           e.nombres,
                           e.apellidos,
                           esp.nombre as especialidad,
                           u.correo,
                           u.telefono
                    FROM EMPLEADO e
                    INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE e.id_especialidad = %s
                    AND e.id_rol = 2
                    AND e.estado = 'activo'
                    AND u.estado = 'activo'
                    ORDER BY e.apellidos, e.nombres
                """
                cursor.execute(sql, (id_especialidad,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_autorizacion, data, id_usuario_modifica=None):
        """Actualiza una autorización existente con auditoría de cambios"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Si se proporciona usuario, registrar cambios en auditoría
                if id_usuario_modifica:
                    # Obtener valores actuales
                    cursor.execute("SELECT * FROM AUTORIZACION_PROCEDIMIENTO WHERE id_autorizacion = %s", (id_autorizacion,))
                    valores_anteriores = cursor.fetchone()
                
                campos = []
                valores = []
                
                campos_permitidos = [
                    'id_medico_asignado', 'id_servicio', 'estado', 'id_especialidad_requerida',
                    'fecha_vencimiento'
                ]
                
                for campo in campos_permitidos:
                    if campo in data:
                        campos.append(f"{campo} = %s")
                        valores.append(data[campo])
                        
                        # Registrar en auditoría si hay usuario
                        if id_usuario_modifica and valores_anteriores:
                            valor_anterior = valores_anteriores.get(campo)
                            valor_nuevo = data[campo]
                            if valor_anterior != valor_nuevo:
                                AutorizacionProcedimiento._registrar_auditoria(
                                    id_autorizacion, campo, valor_anterior, valor_nuevo, 
                                    id_usuario_modifica, data.get('observaciones_auditoria')
                                )
                
                if not campos:
                    return {'success': False, 'error': 'No hay campos para actualizar'}
                
                valores.append(id_autorizacion)
                sql = f"UPDATE AUTORIZACION_PROCEDIMIENTO SET {', '.join(campos)} WHERE id_autorizacion = %s"
                
                cursor.execute(sql, valores)
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def _registrar_auditoria(id_autorizacion, campo, valor_anterior, valor_nuevo, id_usuario, observaciones=None):
        """Registra un cambio en la tabla de auditoría"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO AUTORIZACION_PROCEDIMIENTO_AUDITORIA 
                        (id_autorizacion, campo_modificado, valor_anterior, valor_nuevo, 
                         id_usuario_modifica, observaciones)
                        VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    id_autorizacion, campo, str(valor_anterior), str(valor_nuevo),
                    id_usuario, observaciones
                ))
                conexion.commit()
        except Exception as e:
            print(f"Error al registrar auditoría: {e}")
        finally:
            conexion.close()

    @staticmethod
    def editar_pendiente(id_autorizacion, data, id_usuario_modifica):
        """
        Edita una autorización SOLO si está en estado PENDIENTE
        Punto 1.2 del documento: Modificación de Autorizaciones
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Verificar que está en PENDIENTE
                cursor.execute(
                    "SELECT estado FROM AUTORIZACION_PROCEDIMIENTO WHERE id_autorizacion = %s",
                    (id_autorizacion,)
                )
                resultado = cursor.fetchone()
                
                if not resultado:
                    return {'success': False, 'error': 'Autorización no encontrada'}
                
                if resultado['estado'] != 'PENDIENTE':
                    return {
                        'success': False, 
                        'error': f'No se puede editar. La autorización está en estado: {resultado["estado"]}'
                    }
                
                # Proceder con la actualización usando auditoría
                return AutorizacionProcedimiento.actualizar(id_autorizacion, data, id_usuario_modifica)
        finally:
            conexion.close()

    @staticmethod
    def aprobar(id_autorizacion):
        """Aprueba una autorización"""
        return AutorizacionProcedimiento.actualizar(id_autorizacion, {'estado': 'APROBADA'})

    @staticmethod
    def rechazar(id_autorizacion):
        """Rechaza una autorización"""
        return AutorizacionProcedimiento.actualizar(id_autorizacion, {'estado': 'RECHAZADA'})

    @staticmethod
    def completar(id_autorizacion):
        """Marca una autorización como completada (procedimiento realizado)"""
        return AutorizacionProcedimiento.actualizar(id_autorizacion, {'estado': 'COMPLETADA'})

    @staticmethod
    def asignar_medico(id_autorizacion, id_medico, validar_especialidad=True):
        """
        Asigna un médico a una autorización con validación y notificación
        Punto 2.1 del documento: Validación de Especialidad del Médico
        Punto 5.2 del documento: Notificación al Médico Asignado
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                if validar_especialidad:
                    # Verificar que el médico tenga la especialidad requerida
                    sql = """
                        SELECT a.id_especialidad_requerida, a.tipo_procedimiento, a.id_paciente,
                               a.id_servicio, e.id_especialidad as especialidad_medico
                        FROM AUTORIZACION_PROCEDIMIENTO a
                        INNER JOIN EMPLEADO e ON e.id_empleado = %s
                        WHERE a.id_autorizacion = %s
                    """
                    cursor.execute(sql, (id_medico, id_autorizacion))
                    result = cursor.fetchone()
                    
                    if not result:
                        return {'success': False, 'error': 'Autorización o médico no encontrado'}
                    
                    if result['id_especialidad_requerida'] and result['especialidad_medico']:
                        if result['id_especialidad_requerida'] != result['especialidad_medico']:
                            return {
                                'success': False, 
                                'error': 'El médico no tiene la especialidad requerida para este procedimiento',
                                'requiere_confirmacion': True
                            }
                
                # Actualizar la asignación
                update_result = AutorizacionProcedimiento.actualizar(id_autorizacion, {'id_medico_asignado': id_medico})
                
                if update_result.get('success'):
                    # Enviar notificación al médico asignado
                    try:
                        from utils.notificaciones_autorizaciones import crear_notificacion_autorizacion_medico
                        
                        # Obtener datos para la notificación
                        cursor.execute("""
                            SELECT a.tipo_procedimiento,
                                   CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                                   s.nombre as nombre_servicio
                            FROM AUTORIZACION_PROCEDIMIENTO a
                            INNER JOIN PACIENTE p ON a.id_paciente = p.id_paciente
                            INNER JOIN SERVICIO s ON a.id_servicio = s.id_servicio
                            WHERE a.id_autorizacion = %s
                        """, (id_autorizacion,))
                        info = cursor.fetchone()
                        
                        if info:
                            crear_notificacion_autorizacion_medico(
                                id_medico,
                                id_autorizacion,
                                info['tipo_procedimiento'],
                                info['nombre_paciente'],
                                info['nombre_servicio']
                            )
                    except Exception as notif_error:
                        print(f"Error al enviar notificación a médico: {notif_error}")
                
                return update_result
        finally:
            conexion.close()

    @staticmethod
    def consumir_autorizacion(id_autorizacion, id_reserva):
        """
        Marca una autorización como utilizada y la vincula con la reserva/procedimiento generado
        Punto 1.3 del documento: Consumo de Autorizaciones
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Verificar que no haya sido usada antes
                cursor.execute(
                    "SELECT id_reserva_generada, estado FROM AUTORIZACION_PROCEDIMIENTO WHERE id_autorizacion = %s",
                    (id_autorizacion,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return {'success': False, 'error': 'Autorización no encontrada'}
                
                if result['id_reserva_generada']:
                    return {'success': False, 'error': 'Esta autorización ya fue utilizada'}
                
                if result['estado'] == 'VENCIDA':
                    return {'success': False, 'error': 'Esta autorización está vencida'}
                
                # Marcar como usada
                sql = """UPDATE AUTORIZACION_PROCEDIMIENTO 
                        SET id_reserva_generada = %s, fecha_uso = %s, estado = 'COMPLETADA'
                        WHERE id_autorizacion = %s"""
                cursor.execute(sql, (id_reserva, datetime.now(), id_autorizacion))
                conexion.commit()
                
                return {'success': True, 'mensaje': 'Autorización consumida exitosamente'}
        except Exception as e:
            conexion.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def marcar_vencidas():
        """
        Marca como VENCIDAS las autorizaciones que superaron su fecha de vencimiento
        Punto 1.1 del documento: Vencimiento de Autorizaciones
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """UPDATE AUTORIZACION_PROCEDIMIENTO 
                        SET estado = 'VENCIDA'
                        WHERE estado = 'PENDIENTE'
                        AND fecha_vencimiento < NOW()
                        AND id_reserva_generada IS NULL"""
                cursor.execute(sql)
                conexion.commit()
                return {'success': True, 'autorizaciones_vencidas': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_vencer(dias=2):
        """Obtiene autorizaciones que están por vencer en X días"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT a.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           u.correo as correo_paciente,
                           u.telefono as telefono_paciente,
                           DATEDIFF(a.fecha_vencimiento, NOW()) as dias_restantes
                    FROM AUTORIZACION_PROCEDIMIENTO a
                    INNER JOIN PACIENTE p ON a.id_paciente = p.id_paciente
                    INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                    WHERE a.estado = 'PENDIENTE'
                    AND a.fecha_vencimiento BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s DAY)
                    AND a.id_reserva_generada IS NULL
                    ORDER BY a.fecha_vencimiento ASC
                """
                cursor.execute(sql, (dias,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_servicios_examen(id_especialidad_medico=None):
        """
        Obtiene servicios de tipo EXAMEN (id_tipo_servicio = 4)
        Si se proporciona id_especialidad_medico, filtra exámenes de esa especialidad
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                if id_especialidad_medico:
                    # Mostrar solo exámenes de la especialidad del médico
                    sql = """
                        SELECT s.id_servicio, s.nombre, s.descripcion, s.id_especialidad,
                               e.nombre as nombre_especialidad
                        FROM SERVICIO s
                        LEFT JOIN ESPECIALIDAD e ON s.id_especialidad = e.id_especialidad
                        WHERE s.id_tipo_servicio = 4 
                        AND s.estado = 'activo'
                        AND (s.id_especialidad = %s OR s.id_especialidad IS NULL)
                        ORDER BY s.nombre
                    """
                    cursor.execute(sql, (id_especialidad_medico,))
                else:
                    # Sin especialidad: mostrar todos los exámenes
                    sql = """
                        SELECT s.id_servicio, s.nombre, s.descripcion, s.id_especialidad,
                               e.nombre as nombre_especialidad
                        FROM SERVICIO s
                        LEFT JOIN ESPECIALIDAD e ON s.id_especialidad = e.id_especialidad
                        WHERE s.id_tipo_servicio = 4 
                        AND s.estado = 'activo'
                        ORDER BY s.nombre
                    """
                    cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_servicios_operacion(id_especialidad_medico=None):
        """
        Obtiene servicios de tipo OPERACION (id_tipo_servicio = 2)
        Si se proporciona id_especialidad_medico, incluye:
        - Operaciones de la misma especialidad del médico
        - Operaciones sin especialidad específica
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                if id_especialidad_medico:
                    sql = """
                        SELECT s.id_servicio, s.nombre, s.descripcion, s.id_especialidad,
                               e.nombre as nombre_especialidad
                        FROM SERVICIO s
                        LEFT JOIN ESPECIALIDAD e ON s.id_especialidad = e.id_especialidad
                        WHERE s.id_tipo_servicio = 2 
                        AND s.estado = 'activo'
                        AND (s.id_especialidad = %s OR s.id_especialidad IS NULL)
                        ORDER BY 
                            CASE WHEN s.id_especialidad = %s THEN 0 ELSE 1 END,
                            s.nombre
                    """
                    cursor.execute(sql, (id_especialidad_medico, id_especialidad_medico))
                else:
                    sql = """
                        SELECT s.id_servicio, s.nombre, s.descripcion, s.id_especialidad,
                               e.nombre as nombre_especialidad
                        FROM SERVICIO s
                        LEFT JOIN ESPECIALIDAD e ON s.id_especialidad = e.id_especialidad
                        WHERE s.id_tipo_servicio = 2 
                        AND s.estado = 'activo'
                        ORDER BY s.nombre
                    """
                    cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()
