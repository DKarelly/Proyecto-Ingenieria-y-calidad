from bd import obtener_conexion
from datetime import date, time, datetime

class ExamenMedico:
    """Modelo actualizado para gestión de exámenes médicos"""
    
    def __init__(self, id_examen=None, fecha_examen=None, hora_examen=None,
                 observacion=None, estado='PENDIENTE', tipo_examen='LABORATORIO',
                 indicaciones_especiales=None, resultados_pdf=None,
                 interpretacion_medica=None, id_reserva=None):
        self.id_examen = id_examen
        self.fecha_examen = fecha_examen
        self.hora_examen = hora_examen
        self.observacion = observacion
        self.estado = estado
        self.tipo_examen = tipo_examen
        self.indicaciones_especiales = indicaciones_especiales
        self.resultados_pdf = resultados_pdf
        self.interpretacion_medica = interpretacion_medica
        self.id_reserva = id_reserva

    @staticmethod
    def crear(data):
        """Crea un nuevo examen"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO EXAMEN (
                    fecha_examen, hora_examen, observacion, estado, tipo_examen,
                    indicaciones_especiales, id_reserva
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql, (
                    data.get('fecha_examen'),
                    data.get('hora_examen'),
                    data.get('observacion'),
                    'PENDIENTE',
                    data.get('tipo_examen', 'LABORATORIO'),
                    data.get('indicaciones_especiales'),
                    data.get('id_reserva')
                ))
                conexion.commit()
                return {'success': True, 'id_examen': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_examen):
        """Obtiene un examen por su ID con información completa"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT ex.*,
                           r.id_paciente,
                           r.cita_origen_id,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio,
                           prog.hora_fin,
                           CONCAT(e.nombres, ' ', e.apellidos) as profesional_solicita
                    FROM EXAMEN ex
                    INNER JOIN RESERVA r ON ex.id_reserva = r.id_reserva
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE ex.id_examen = %s
                """
                cursor.execute(sql, (id_examen,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_reserva(id_reserva):
        """Obtiene el examen asociado a una reserva"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM EXAMEN WHERE id_reserva = %s"
                cursor.execute(sql, (id_reserva,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_paciente(id_paciente):
        """Obtiene todos los exámenes de un paciente"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT ex.*,
                           r.estado as estado_reserva,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as profesional
                    FROM EXAMEN ex
                    INNER JOIN RESERVA r ON ex.id_reserva = r.id_reserva
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE r.id_paciente = %s
                    ORDER BY ex.fecha_examen DESC
                """
                cursor.execute(sql, (id_paciente,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_derivados_de_cita(id_cita):
        """Obtiene exámenes derivados de una cita específica"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT ex.*,
                           r.estado as estado_reserva,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio
                    FROM EXAMEN ex
                    INNER JOIN RESERVA r ON ex.id_reserva = r.id_reserva
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    WHERE r.cita_origen_id = %s
                    AND r.tipo_reserva = 'EXAMEN'
                    ORDER BY prog.fecha DESC
                """
                cursor.execute(sql, (id_cita,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def actualizar(id_examen, data):
        """Actualiza los datos de un examen"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                campos_permitidos = [
                    'fecha_examen', 'hora_examen', 'observacion', 'estado',
                    'tipo_examen', 'indicaciones_especiales', 'resultados_pdf',
                    'interpretacion_medica'
                ]
                
                for campo in campos_permitidos:
                    if campo in data:
                        campos.append(f"{campo} = %s")
                        valores.append(data[campo])
                
                if not campos:
                    return {'error': 'No hay campos para actualizar'}
                
                valores.append(id_examen)
                sql = f"UPDATE EXAMEN SET {', '.join(campos)} WHERE id_examen = %s"
                
                cursor.execute(sql, valores)
                conexion.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def confirmar(id_examen):
        """Confirma un examen"""
        return ExamenMedico.actualizar(id_examen, {'estado': 'CONFIRMADO'})

    @staticmethod
    def registrar_resultados(id_examen, observaciones, interpretacion=None, pdf_path=None):
        """Completa un examen registrando los resultados"""
        data = {
            'estado': 'COMPLETADO',
            'observacion': observaciones
        }
        if interpretacion:
            data['interpretacion_medica'] = interpretacion
        if pdf_path:
            data['resultados_pdf'] = pdf_path
        
        return ExamenMedico.actualizar(id_examen, data)

    @staticmethod
    def cancelar(id_examen):
        """Cancela un examen"""
        return ExamenMedico.actualizar(id_examen, {'estado': 'CANCELADO'})

    @staticmethod
    def obtener_por_estado(estado):
        """Obtiene exámenes por estado"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT ex.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio,
                           ex.tipo_examen
                    FROM EXAMEN ex
                    INNER JOIN RESERVA r ON ex.id_reserva = r.id_reserva
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    WHERE ex.estado = %s
                    ORDER BY prog.fecha, prog.hora_inicio
                """
                cursor.execute(sql, (estado,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_tipo(tipo_examen):
        """Obtiene exámenes por tipo"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT ex.*,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           prog.fecha as fecha_programada,
                           prog.hora_inicio,
                           ex.estado
                    FROM EXAMEN ex
                    INNER JOIN RESERVA r ON ex.id_reserva = r.id_reserva
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    WHERE ex.tipo_examen = %s
                    ORDER BY prog.fecha DESC
                """
                cursor.execute(sql, (tipo_examen,))
                return cursor.fetchall()
        finally:
            conexion.close()


class TipoExamen:
    """Modelo para catálogo de tipos de examen"""
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los tipos de examen activos"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """SELECT * FROM TIPO_EXAMEN 
                         WHERE estado = 'ACTIVO' 
                         ORDER BY categoria, nombre"""
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_categoria(categoria):
        """Obtiene tipos de examen por categoría"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """SELECT * FROM TIPO_EXAMEN 
                         WHERE categoria = %s AND estado = 'ACTIVO'
                         ORDER BY nombre"""
                cursor.execute(sql, (categoria,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_tipo_examen):
        """Obtiene un tipo de examen por su ID"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM TIPO_EXAMEN WHERE id_tipo_examen = %s"
                cursor.execute(sql, (id_tipo_examen,))
                return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def crear(data):
        """Crea un nuevo tipo de examen"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO TIPO_EXAMEN 
                         (categoria, nombre, descripcion, preparacion_requerida, estado)
                         VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    data.get('categoria'),
                    data.get('nombre'),
                    data.get('descripcion'),
                    data.get('preparacion_requerida'),
                    data.get('estado', 'ACTIVO')
                ))
                conexion.commit()
                return {'success': True, 'id_tipo_examen': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()


class ExamenDetalle:
    """Modelo para detalles de exámenes (múltiples tipos por examen)"""
    
    @staticmethod
    def agregar(id_examen, id_tipo_examen, observaciones=None):
        """Agrega un tipo de examen a un examen"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """INSERT INTO EXAMEN_DETALLE (id_examen, id_tipo_examen, observaciones)
                         VALUES (%s, %s, %s)"""
                cursor.execute(sql, (id_examen, id_tipo_examen, observaciones))
                conexion.commit()
                return {'success': True, 'id_detalle': cursor.lastrowid}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_examen(id_examen):
        """Obtiene todos los tipos de examen de un examen específico"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT ed.*, te.nombre, te.categoria, te.descripcion
                    FROM EXAMEN_DETALLE ed
                    INNER JOIN TIPO_EXAMEN te ON ed.id_tipo_examen = te.id_tipo_examen
                    WHERE ed.id_examen = %s
                    ORDER BY te.categoria, te.nombre
                """
                cursor.execute(sql, (id_examen,))
                return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def eliminar(id_detalle):
        """Elimina un detalle de examen"""
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM EXAMEN_DETALLE WHERE id_detalle = %s"
                cursor.execute(sql, (id_detalle,))
                conexion.commit()
                return {'success': True}
        except Exception as e:
            conexion.rollback()
            return {'error': str(e)}
        finally:
            conexion.close()
