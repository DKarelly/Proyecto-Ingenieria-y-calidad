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
                 estado='PENDIENTE', fecha_autorizacion=None):
        self.id_autorizacion = id_autorizacion
        self.id_cita = id_cita
        self.id_paciente = id_paciente
        self.id_medico_autoriza = id_medico_autoriza
        self.tipo_procedimiento = tipo_procedimiento  # 'EXAMEN' o 'OPERACION'
        self.id_servicio = id_servicio
        self.id_especialidad_requerida = id_especialidad_requerida
        self.id_medico_asignado = id_medico_asignado
        self.estado = estado  # 'PENDIENTE', 'APROBADA', 'RECHAZADA', 'COMPLETADA'
        self.fecha_autorizacion = fecha_autorizacion

    @staticmethod
    def crear(data):
        """Crea una nueva autorización de procedimiento"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO AUTORIZACION_PROCEDIMIENTO (
                    id_cita, id_paciente, id_medico_autoriza, tipo_procedimiento,
                    id_servicio, id_especialidad_requerida, id_medico_asignado, 
                    estado, fecha_autorizacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql, (
                    data.get('id_cita'),
                    data.get('id_paciente'),
                    data.get('id_medico_autoriza'),
                    data.get('tipo_procedimiento'),
                    data.get('id_servicio'),
                    data.get('id_especialidad_requerida'),
                    data.get('id_medico_asignado'),
                    'PENDIENTE',
                    datetime.now()
                ))
                conexion.commit()
                return {'success': True, 'id_autorizacion': cursor.lastrowid}
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
        """Obtiene autorizaciones pendientes de un paciente para habilitar botones"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT tipo_procedimiento, COUNT(*) as cantidad
                    FROM AUTORIZACION_PROCEDIMIENTO
                    WHERE id_paciente = %s 
                    AND estado = 'PENDIENTE'
                    GROUP BY tipo_procedimiento
                """
                cursor.execute(sql, (id_paciente,))
                result = cursor.fetchall()
                
                # Convertir a diccionario para fácil acceso
                permisos = {
                    'examen': False,
                    'operacion': False
                }
                
                for row in result:
                    if row['tipo_procedimiento'] == 'EXAMEN' and row['cantidad'] > 0:
                        permisos['examen'] = True
                    elif row['tipo_procedimiento'] == 'OPERACION' and row['cantidad'] > 0:
                        permisos['operacion'] = True
                
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
    def actualizar(id_autorizacion, data):
        """Actualiza una autorización existente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                campos_permitidos = [
                    'id_medico_asignado', 'id_servicio', 'estado', 'id_especialidad_requerida'
                ]
                
                for campo in campos_permitidos:
                    if campo in data:
                        campos.append(f"{campo} = %s")
                        valores.append(data[campo])
                
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
    def asignar_medico(id_autorizacion, id_medico):
        """Asigna un médico a una autorización"""
        return AutorizacionProcedimiento.actualizar(id_autorizacion, {'id_medico_asignado': id_medico})

    @staticmethod
    def obtener_servicios_examen():
        """Obtiene todos los servicios de tipo EXAMEN (id_tipo_servicio = 4)"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
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
