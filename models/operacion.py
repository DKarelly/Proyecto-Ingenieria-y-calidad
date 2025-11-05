from bd import obtener_conexion
from datetime import date, time, datetime

class Operacion:
    def __init__(self, id_operacion=None, id_reserva=None, tipo_operacion=None,
                 quirofano=None, duracion_estimada=None, diagnostico_previo=None,
                 indicaciones_preoperatorias=None, procedimientos_realizados=None,
                 complicaciones=None, indicaciones_postoperatorias=None,
                 consentimiento_informado=False, fecha_operacion=None,
                 hora_inicio_real=None, hora_fin_real=None, estado='PENDIENTE'):
        self.id_operacion = id_operacion
        self.id_reserva = id_reserva
        self.tipo_operacion = tipo_operacion
        self.quirofano = quirofano
        self.duracion_estimada = duracion_estimada
        self.diagnostico_previo = diagnostico_previo
        self.indicaciones_preoperatorias = indicaciones_preoperatorias
        self.procedimientos_realizados = procedimientos_realizados
        self.complicaciones = complicaciones
        self.indicaciones_postoperatorias = indicaciones_postoperatorias
        self.consentimiento_informado = consentimiento_informado
        self.fecha_operacion = fecha_operacion
        self.hora_inicio_real = hora_inicio_real
        self.hora_fin_real = hora_fin_real
        self.estado = estado

    @staticmethod
    def crear(data):
        """Crea una nueva operación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO OPERACION (
                    id_reserva, tipo_operacion, quirofano, duracion_estimada,
                    diagnostico_previo, indicaciones_preoperatorias,
                    consentimiento_informado, fecha_operacion, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql, (
                    data.get('id_reserva'),
                    data.get('tipo_operacion'),
                    data.get('quirofano'),
                    data.get('duracion_estimada'),
                    data.get('diagnostico_previo'),
                    data.get('indicaciones_preoperatorias'),
                    data.get('consentimiento_informado', False),
                    data.get('fecha_operacion'),
                    'PENDIENTE'
                ))
                conexion.commit()
                return {'success': True, 'id_operacion': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_operacion):
        """Obtiene una operación por su ID con información completa"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT o.*,
                           r.id_paciente,
                           r.cita_origen_id,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio as hora_programada_inicio,
                           prog.hora_fin as hora_programada_fin,
                           CONCAT(e.nombres, ' ', e.apellidos) as cirujano_principal
                    FROM OPERACION o
                    INNER JOIN RESERVA r ON o.id_reserva = r.id_reserva
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE o.id_operacion = %s
                """
                cursor.execute(sql, (id_operacion,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_reserva(id_reserva):
        """Obtiene la operación asociada a una reserva"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM OPERACION WHERE id_reserva = %s"
                cursor.execute(sql, (id_reserva,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_paciente(id_paciente):
        """Obtiene todas las operaciones de un paciente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT o.*,
                           r.estado as estado_reserva,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as cirujano
                    FROM OPERACION o
                    INNER JOIN RESERVA r ON o.id_reserva = r.id_reserva
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE r.id_paciente = %s
                    ORDER BY o.fecha_operacion DESC
                """
                cursor.execute(sql, (id_paciente,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_derivadas_de_cita(id_cita):
        """Obtiene operaciones derivadas de una cita específica"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT o.*,
                           r.estado as estado_reserva,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio
                    FROM OPERACION o
                    INNER JOIN RESERVA r ON o.id_reserva = r.id_reserva
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    WHERE r.cita_origen_id = %s
                    AND r.tipo_reserva = 'OPERACION'
                    ORDER BY prog.fecha DESC
                """
                cursor.execute(sql, (id_cita,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_operacion, data):
        """Actualiza los datos de una operación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                campos_permitidos = [
                    'tipo_operacion', 'quirofano', 'duracion_estimada',
                    'diagnostico_previo', 'indicaciones_preoperatorias',
                    'procedimientos_realizados', 'complicaciones',
                    'indicaciones_postoperatorias', 'consentimiento_informado',
                    'fecha_operacion', 'hora_inicio_real', 'hora_fin_real', 'estado'
                ]
                
                for campo in campos_permitidos:
                    if campo in data:
                        campos.append(f"{campo} = %s")
                        valores.append(data[campo])
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_operacion)
                sql = f"UPDATE OPERACION SET {', '.join(campos)} WHERE id_operacion = %s"
                
                cursor.execute(sql, valores)
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def confirmar(id_operacion):
        """Confirma una operación"""
        return Operacion.actualizar(id_operacion, {'estado': 'CONFIRMADA'})

    @staticmethod
    def completar(id_operacion, data):
        """Completa una operación con los datos de la cirugía realizada"""
        data['estado'] = 'COMPLETADA'
        return Operacion.actualizar(id_operacion, data)

    @staticmethod
    def cancelar(id_operacion):
        """Cancela una operación"""
        return Operacion.actualizar(id_operacion, {'estado': 'CANCELADA'})

    @staticmethod
    def obtener_por_estado(estado):
        """Obtiene operaciones por estado"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT o.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as cirujano
                    FROM OPERACION o
                    INNER JOIN RESERVA r ON o.id_reserva = r.id_reserva
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE o.estado = %s
                    ORDER BY prog.fecha, prog.hora_inicio
                """
                cursor.execute(sql, (estado,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_fecha(fecha):
        """Obtiene operaciones programadas para una fecha específica"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT o.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           prog.hora_inicio,
                           prog.hora_fin,
                           CONCAT(e.nombres, ' ', e.apellidos) as cirujano,
                           o.quirofano
                    FROM OPERACION o
                    INNER JOIN RESERVA r ON o.id_reserva = r.id_reserva
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE prog.fecha = %s
                    ORDER BY prog.hora_inicio
                """
                cursor.execute(sql, (fecha,))
                return cursor.fetchall()
        finally:
            conexion.close()


class EquipoMedicoOperacion:
    """Clase para gestionar el equipo médico de una operación"""
    
    @staticmethod
    def agregar_miembro(id_operacion, id_empleado, rol, observaciones=None):
        """Agrega un miembro al equipo médico de una operación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO EQUIPO_MEDICO_OPERACION 
                         (id_operacion, id_empleado, rol_en_operacion, observaciones)
                         VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (id_operacion, id_empleado, rol, observaciones))
                conexion.commit()
                return {'success': True, 'id_equipo': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_equipo(id_operacion):
        """Obtiene todos los miembros del equipo médico de una operación"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT em.*,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                           esp.nombre as especialidad
                    FROM EQUIPO_MEDICO_OPERACION em
                    INNER JOIN EMPLEADO e ON em.id_empleado = e.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE em.id_operacion = %s
                    ORDER BY 
                        CASE em.rol_en_operacion
                            WHEN 'CIRUJANO_PRINCIPAL' THEN 1
                            WHEN 'CIRUJANO_ASISTENTE' THEN 2
                            WHEN 'ANESTESIOLOGO' THEN 3
                            WHEN 'ENFERMERA' THEN 4
                            ELSE 5
                        END
                """
                cursor.execute(sql, (id_operacion,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def eliminar_miembro(id_equipo):
        """Elimina un miembro del equipo médico"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM EQUIPO_MEDICO_OPERACION WHERE id_equipo = %s"
                cursor.execute(sql, (id_equipo,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()
