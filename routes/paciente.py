from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from bd import obtener_conexion
from models.paciente import Paciente
from models.incidencia import Incidencia

paciente_bp = Blueprint('paciente', __name__)


# ========== HISTORIAL CLÍNICO ==========

@paciente_bp.route('/historial-clinico')
def historial_clinico():
    """Vista del historial clínico del paciente"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('HistorialClinicoPaciente.html')


@paciente_bp.route('/api/historial-clinico')
def api_historial_clinico():
    """API que retorna el historial clínico del paciente (citas completadas con diagnósticos y autorizaciones)"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        # Obtener el id_paciente del usuario
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Obtener citas completadas
            sql = """
                SELECT c.id_cita,
                       c.fecha_cita,
                       c.hora_inicio,
                       c.hora_fin,
                       c.diagnostico,
                       c.observaciones,
                       c.estado as estado_cita,
                       s.nombre as servicio,
                       e.nombres as medico_nombres,
                       e.apellidos as medico_apellidos,
                       esp.nombre as especialidad,
                       r.id_reserva
                FROM CITA c
                INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE r.id_paciente = %s
                  AND c.diagnostico IS NOT NULL
                ORDER BY c.fecha_cita DESC
            """
            cursor.execute(sql, (id_paciente,))
            historial = cursor.fetchall()
            
            # Para cada cita, obtener autorizaciones pendientes y completadas
            for cita in historial:
                id_cita = cita['id_cita']
                
                # Obtener autorizaciones asociadas a esta cita
                sql_autorizaciones = """
                    SELECT a.id_autorizacion,
                           a.tipo_procedimiento,
                           a.estado,
                           a.fecha_autorizacion,
                           a.fecha_vencimiento,
                           s.nombre as servicio_nombre,
                           s.id_servicio,
                           CONCAT(med_asig.nombres, ' ', med_asig.apellidos) as medico_asignado,
                           esp_req.nombre as especialidad_requerida,
                           a.id_reserva_generada
                    FROM AUTORIZACION_PROCEDIMIENTO a
                    INNER JOIN SERVICIO s ON a.id_servicio = s.id_servicio
                    LEFT JOIN EMPLEADO med_asig ON a.id_medico_asignado = med_asig.id_empleado
                    LEFT JOIN ESPECIALIDAD esp_req ON a.id_especialidad_requerida = esp_req.id_especialidad
                    WHERE a.id_cita = %s
                    ORDER BY a.fecha_autorizacion DESC
                """
                cursor.execute(sql_autorizaciones, (id_cita,))
                autorizaciones = cursor.fetchall()
                
                # Convertir fechas
                for aut in autorizaciones:
                    if aut.get('fecha_autorizacion'):
                        if hasattr(aut['fecha_autorizacion'], 'strftime'):
                            aut['fecha_autorizacion'] = aut['fecha_autorizacion'].strftime('%Y-%m-%d %H:%M')
                    if aut.get('fecha_vencimiento'):
                        if hasattr(aut['fecha_vencimiento'], 'strftime'):
                            aut['fecha_vencimiento'] = aut['fecha_vencimiento'].strftime('%Y-%m-%d')
                
                cita['autorizaciones'] = autorizaciones
                
                # Obtener EXÁMENES asociados a esta cita
                sql_examenes = """
                    SELECT e.id_examen,
                           e.fecha_examen,
                           e.observacion,
                           e.estado,
                           p.fecha as fecha_programacion,
                           TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio,
                           TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin,
                           s.nombre as tipo_examen,
                           emp.nombres as medico_nombres,
                           emp.apellidos as medico_apellidos
                    FROM EXAMEN e
                    INNER JOIN PROGRAMACION p ON e.id_programacion = p.id_programacion
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                    WHERE e.id_cita = %s
                    ORDER BY e.fecha_examen DESC
                """
                cursor.execute(sql_examenes, (id_cita,))
                examenes = cursor.fetchall()
                
                # Convertir fechas de exámenes
                for examen in examenes:
                    if examen.get('fecha_examen') and hasattr(examen['fecha_examen'], 'strftime'):
                        examen['fecha_examen'] = examen['fecha_examen'].strftime('%Y-%m-%d')
                    if examen.get('fecha_programacion') and hasattr(examen['fecha_programacion'], 'strftime'):
                        examen['fecha_programacion'] = examen['fecha_programacion'].strftime('%Y-%m-%d')
                
                cita['examenes'] = examenes
                
                # Obtener OPERACIONES asociadas a esta cita
                sql_operaciones = """
                    SELECT o.id_operacion,
                           o.fecha_operacion,
                           o.observacion,
                           o.estado,
                           p.fecha as fecha_programacion,
                           TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio,
                           TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin,
                           s.nombre as tipo_operacion,
                           emp.nombres as medico_nombres,
                           emp.apellidos as medico_apellidos
                    FROM OPERACION o
                    INNER JOIN PROGRAMACION p ON o.id_programacion = p.id_programacion
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                    WHERE o.id_cita = %s
                    ORDER BY o.fecha_operacion DESC
                """
                cursor.execute(sql_operaciones, (id_cita,))
                operaciones = cursor.fetchall()
                
                # Convertir fechas de operaciones
                for operacion in operaciones:
                    if operacion.get('fecha_operacion') and hasattr(operacion['fecha_operacion'], 'strftime'):
                        operacion['fecha_operacion'] = operacion['fecha_operacion'].strftime('%Y-%m-%d')
                    if operacion.get('fecha_programacion') and hasattr(operacion['fecha_programacion'], 'strftime'):
                        operacion['fecha_programacion'] = operacion['fecha_programacion'].strftime('%Y-%m-%d')
                
                cita['operaciones'] = operaciones

            return jsonify({'historial': historial})

    except Exception as e:
        return jsonify({'error': f'Error al obtener historial clínico: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@paciente_bp.route('/api/autorizacion/<int:id_autorizacion>/programaciones')
def api_programaciones_autorizacion(id_autorizacion):
    """API que retorna las programaciones disponibles para una autorización específica"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la autorización pertenece al paciente
            cursor.execute("""
                SELECT a.id_servicio, 
                       a.id_medico_asignado,
                       a.tipo_procedimiento,
                       a.estado,
                       s.nombre as servicio_nombre
                FROM AUTORIZACION_PROCEDIMIENTO a
                INNER JOIN SERVICIO s ON a.id_servicio = s.id_servicio
                WHERE a.id_autorizacion = %s AND a.id_paciente = %s
            """, (id_autorizacion, id_paciente))
            
            autorizacion = cursor.fetchone()
            
            if not autorizacion:
                return jsonify({'error': 'Autorización no encontrada'}), 404
            
            if autorizacion['estado'] != 'PENDIENTE':
                return jsonify({'error': 'Esta autorización ya ha sido utilizada o no está disponible'}), 400
            
            id_servicio = autorizacion['id_servicio']
            id_medico_asignado = autorizacion['id_medico_asignado']
            
            # Obtener programaciones disponibles
            # Si hay médico asignado, filtrar por ese médico
            # Si no hay médico asignado, mostrar todos los que ofrecen ese servicio
            
            if id_medico_asignado:
                sql_programaciones = """
                    SELECT p.id_programacion,
                           p.fecha,
                           TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                           TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                           p.estado_programacion,
                           h.id_horario,
                           e.id_empleado,
                           CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                           esp.nombre as especialidad,
                           s.nombre as servicio_nombre
                    FROM PROGRAMACION p
                    INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE p.id_servicio = %s
                      AND e.id_empleado = %s
                      AND p.estado_programacion = 'Disponible'
                      AND p.fecha >= CURDATE()
                    ORDER BY p.fecha, p.hora_inicio
                """
                cursor.execute(sql_programaciones, (id_servicio, id_medico_asignado))
            else:
                sql_programaciones = """
                    SELECT p.id_programacion,
                           p.fecha,
                           TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                           TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                           p.estado_programacion,
                           h.id_horario,
                           e.id_empleado,
                           CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                           esp.nombre as especialidad,
                           s.nombre as servicio_nombre
                    FROM PROGRAMACION p
                    INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE p.id_servicio = %s
                      AND p.estado_programacion = 'Disponible'
                      AND p.fecha >= CURDATE()
                    ORDER BY p.fecha, p.hora_inicio
                """
                cursor.execute(sql_programaciones, (id_servicio,))
            
            programaciones = cursor.fetchall()
            
            # Convertir fechas
            for prog in programaciones:
                if prog.get('fecha'):
                    if hasattr(prog['fecha'], 'strftime'):
                        prog['fecha'] = prog['fecha'].strftime('%Y-%m-%d')
            
            return jsonify({
                'programaciones': programaciones,
                'autorizacion': {
                    'id': id_autorizacion,
                    'servicio': autorizacion['servicio_nombre'],
                    'tipo': autorizacion['tipo_procedimiento']
                }
            })

    except Exception as e:
        return jsonify({'error': f'Error al obtener programaciones: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@paciente_bp.route('/api/reservar-desde-autorizacion', methods=['POST'])
def api_reservar_desde_autorizacion():
    """API para crear una reserva a partir de una autorización de procedimiento"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        data = request.get_json()
        id_autorizacion = data.get('id_autorizacion')
        id_programacion = data.get('id_programacion')

        if not id_autorizacion or not id_programacion:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # Verificar que la autorización pertenece al paciente y está pendiente
            cursor.execute("""
                SELECT id_cita, estado
                FROM AUTORIZACION_PROCEDIMIENTO
                WHERE id_autorizacion = %s AND id_paciente = %s
            """, (id_autorizacion, id_paciente))
            
            autorizacion = cursor.fetchone()
            
            if not autorizacion:
                return jsonify({'error': 'Autorización no encontrada'}), 404
            
            if autorizacion['estado'] != 'PENDIENTE':
                return jsonify({'error': 'Esta autorización ya ha sido utilizada'}), 400

            # Verificar que la programación existe y está disponible
            cursor.execute("""
                SELECT estado_programacion
                FROM PROGRAMACION
                WHERE id_programacion = %s
            """, (id_programacion,))
            
            programacion = cursor.fetchone()
            
            if not programacion:
                return jsonify({'error': 'Programación no encontrada'}), 404
            
            if programacion['estado_programacion'] != 'Disponible':
                return jsonify({'error': 'Esta programación ya no está disponible'}), 400

            # Obtener detalles de la programación para validaciones
            cursor.execute("""
                SELECT p.id_servicio, p.fecha, 
                       TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                       h.id_empleado
                FROM PROGRAMACION p
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                WHERE p.id_programacion = %s
            """, (id_programacion,))
            
            detalles_prog = cursor.fetchone()
            
            if not detalles_prog:
                return jsonify({'error': 'No se pudieron obtener detalles de la programación'}), 404
            
            id_servicio_prog = detalles_prog.get('id_servicio')
            fecha_prog = detalles_prog.get('fecha')
            hora_inicio_prog = detalles_prog.get('hora_inicio')
            hora_fin_prog = detalles_prog.get('hora_fin')
            id_empleado_prog = detalles_prog.get('id_empleado')
            
            # VALIDACIÓN 1: Verificar que el paciente no tenga ya una reserva del mismo servicio, médico y día
            sql_check_duplicado = """
                SELECT r.id_reserva
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                WHERE r.id_paciente = %s
                  AND p.id_servicio = %s
                  AND h.id_empleado = %s
                  AND p.fecha = %s
                  AND r.estado IN ('Confirmada', 'Pendiente')
                LIMIT 1
            """
            cursor.execute(sql_check_duplicado, (id_paciente, id_servicio_prog, id_empleado_prog, fecha_prog))
            reserva_duplicada = cursor.fetchone()
            
            if reserva_duplicada:
                return jsonify({
                    'error': 'Ya tienes una reserva para este mismo servicio y médico en esta fecha. No puedes agendar dos veces el mismo día.'
                }), 400
            
            # VALIDACIÓN 2: Verificar que no haya solapamiento de horarios
            sql_check_solapamiento = """
                SELECT r.id_reserva, 
                       TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                WHERE r.id_paciente = %s
                  AND p.fecha = %s
                  AND r.estado IN ('Confirmada', 'Pendiente')
                  AND (
                      (p.hora_inicio < %s AND p.hora_fin > %s) OR
                      (p.hora_inicio < %s AND p.hora_fin > %s) OR
                      (p.hora_inicio >= %s AND p.hora_fin <= %s)
                  )
                LIMIT 1
            """
            cursor.execute(sql_check_solapamiento, (
                id_paciente, fecha_prog,
                hora_fin_prog, hora_inicio_prog,
                hora_fin_prog, hora_inicio_prog,
                hora_inicio_prog, hora_fin_prog
            ))
            reserva_solapada = cursor.fetchone()
            
            if reserva_solapada:
                hora_conflicto_inicio = reserva_solapada.get('hora_inicio')
                hora_conflicto_fin = reserva_solapada.get('hora_fin')
                return jsonify({
                    'error': f'Ya tienes una reserva en este horario. Conflicto con la reserva de {hora_conflicto_inicio} a {hora_conflicto_fin}.'
                }), 400

            # Crear la reserva
            cursor.execute("""
                INSERT INTO RESERVA (id_programacion, id_paciente, fecha_reserva, estado)
                VALUES (%s, %s, NOW(), 'Pendiente')
            """, (id_programacion, id_paciente))
            
            id_reserva = cursor.lastrowid

            # Actualizar el estado de la programación
            cursor.execute("""
                UPDATE PROGRAMACION
                SET estado_programacion = 'Ocupado'
                WHERE id_programacion = %s
            """, (id_programacion,))

            # Actualizar la autorización: marcar como COMPLETADA y vincular con la reserva
            cursor.execute("""
                UPDATE AUTORIZACION_PROCEDIMIENTO
                SET estado = 'COMPLETADA',
                    fecha_uso = NOW(),
                    id_reserva_generada = %s
                WHERE id_autorizacion = %s
            """, (id_reserva, id_autorizacion))

            conexion.commit()

            return jsonify({
                'success': True,
                'id_reserva': id_reserva,
                'message': 'Reserva creada exitosamente'
            })

        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    except Exception as e:
        return jsonify({'error': f'Error al crear la reserva: {str(e)}'}), 500


@paciente_bp.route('/api/cita/<int:id_cita>/programaciones-procedimientos')
def api_programaciones_procedimientos_cita(id_cita):
    """API que retorna programaciones disponibles para procedimientos de una cita específica"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')
        tipo_procedimiento = request.args.get('tipo', 'EXAMEN')  # EXAMEN u OPERACION

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la cita pertenece al paciente
            cursor.execute("""
                SELECT c.id_cita
                FROM CITA c
                INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                WHERE c.id_cita = %s AND r.id_paciente = %s
            """, (id_cita, id_paciente))
            
            cita = cursor.fetchone()
            if not cita:
                return jsonify({'error': 'Cita no encontrada'}), 404

            # Obtener programaciones disponibles según el tipo de procedimiento
            # Para exámenes: servicios de tipo EXAMEN
            # Para operaciones: servicios de tipo OPERACION
            id_tipo_servicio = 2 if tipo_procedimiento == 'EXAMEN' else 3

            sql = """
                SELECT 
                    p.id_programacion,
                    p.fecha,
                    p.hora_inicio,
                    p.hora_fin,
                    p.estado,
                    s.nombre as servicio_nombre,
                    s.id_servicio,
                    CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                    esp.nombre as especialidad,
                    CASE 
                        WHEN r.id_paciente = %s AND p.estado = 'Ocupado' THEN 1 
                        ELSE 0 
                    END as es_reserva_propia
                FROM PROGRAMACION p
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                LEFT JOIN RESERVA r ON p.id_programacion = r.id_programacion
                WHERE s.id_tipo_servicio = %s
                  AND p.fecha >= CURDATE()
                  AND h.activo = 1
                ORDER BY p.fecha, p.hora_inicio
            """
            
            cursor.execute(sql, (id_paciente, id_tipo_servicio))
            programaciones = cursor.fetchall()

            # Convertir fechas
            for prog in programaciones:
                if prog.get('fecha'):
                    if hasattr(prog['fecha'], 'strftime'):
                        prog['fecha'] = prog['fecha'].strftime('%Y-%m-%d')
                if prog.get('hora_inicio'):
                    if hasattr(prog['hora_inicio'], 'strftime'):
                        prog['hora_inicio'] = str(prog['hora_inicio'])
                if prog.get('hora_fin'):
                    if hasattr(prog['hora_fin'], 'strftime'):
                        prog['hora_fin'] = str(prog['hora_fin'])

            cursor.close()
            conexion.close()

            return jsonify({
                'success': True,
                'programaciones': programaciones,
                'tipo_procedimiento': tipo_procedimiento
            })

    except Exception as e:
        return jsonify({'error': f'Error al obtener programaciones: {str(e)}'}), 500


@paciente_bp.route('/api/reservar-procedimiento-cita', methods=['POST'])
def api_reservar_procedimiento_cita():
    """API para reservar un procedimiento (examen u operación) desde una cita completada"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        data = request.get_json()
        id_cita = data.get('id_cita')
        id_programacion = data.get('id_programacion')
        tipo_procedimiento = data.get('tipo_procedimiento')  # 'EXAMEN' o 'OPERACION'

        if not all([id_cita, id_programacion, tipo_procedimiento]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la cita pertenece al paciente
            cursor.execute("""
                SELECT c.id_cita
                FROM CITA c
                INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                WHERE c.id_cita = %s AND r.id_paciente = %s
            """, (id_cita, id_paciente))
            
            cita = cursor.fetchone()
            if not cita:
                return jsonify({'error': 'Cita no encontrada'}), 404

            # Verificar que la programación existe y está disponible
            cursor.execute("""
                SELECT p.id_programacion, p.fecha, p.hora_inicio, p.hora_fin, 
                       p.estado, p.id_servicio, h.id_empleado
                FROM PROGRAMACION p
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                WHERE p.id_programacion = %s
            """, (id_programacion,))
            
            programacion = cursor.fetchone()
            if not programacion:
                return jsonify({'error': 'Programación no encontrada'}), 404

            if programacion['estado'] != 'Disponible':
                return jsonify({'error': 'La programación ya no está disponible'}), 400

            # Extraer datos de la programación
            id_servicio_prog = programacion['id_servicio']
            id_empleado_prog = programacion['id_empleado']
            fecha_prog = programacion['fecha']
            hora_inicio_prog = programacion['hora_inicio']
            hora_fin_prog = programacion['hora_fin']
            
            # Convertir a string si es necesario
            if hasattr(fecha_prog, 'strftime'):
                fecha_prog = fecha_prog.strftime('%Y-%m-%d')
            if hasattr(hora_inicio_prog, 'strftime'):
                hora_inicio_prog = str(hora_inicio_prog)
            if hasattr(hora_fin_prog, 'strftime'):
                hora_fin_prog = str(hora_fin_prog)

            # VALIDACIÓN 1: Verificar duplicados (mismo servicio, médico y día)
            sql_check_duplicado = """
                SELECT r.id_reserva
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                WHERE r.id_paciente = %s
                  AND p.id_servicio = %s
                  AND h.id_empleado = %s
                  AND p.fecha = %s
                  AND r.estado IN ('Confirmada', 'Pendiente')
                LIMIT 1
            """
            cursor.execute(sql_check_duplicado, (id_paciente, id_servicio_prog, id_empleado_prog, fecha_prog))
            reserva_duplicada = cursor.fetchone()
            
            if reserva_duplicada:
                return jsonify({
                    'error': 'Ya tienes una reserva para este mismo servicio y médico en esta fecha.'
                }), 400
            
            # VALIDACIÓN 2: Verificar solapamiento de horarios
            sql_check_solapamiento = """
                SELECT r.id_reserva, 
                       TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                WHERE r.id_paciente = %s
                  AND p.fecha = %s
                  AND r.estado IN ('Confirmada', 'Pendiente')
                  AND (
                      (p.hora_inicio < %s AND p.hora_fin > %s) OR
                      (p.hora_inicio < %s AND p.hora_fin > %s) OR
                      (p.hora_inicio >= %s AND p.hora_fin <= %s)
                  )
                LIMIT 1
            """
            cursor.execute(sql_check_solapamiento, (
                id_paciente, fecha_prog,
                hora_fin_prog, hora_inicio_prog,
                hora_fin_prog, hora_inicio_prog,
                hora_inicio_prog, hora_fin_prog
            ))
            reserva_solapada = cursor.fetchone()
            
            if reserva_solapada:
                hora_conflicto_inicio = reserva_solapada.get('hora_inicio')
                hora_conflicto_fin = reserva_solapada.get('hora_fin')
                return jsonify({
                    'error': f'Ya tienes una reserva en este horario. Conflicto con la reserva de {hora_conflicto_inicio} a {hora_conflicto_fin}.'
                }), 400

            # Crear la reserva
            cursor.execute("""
                INSERT INTO RESERVA (id_programacion, id_paciente, fecha_reserva, estado)
                VALUES (%s, %s, NOW(), 'Pendiente')
            """, (id_programacion, id_paciente))
            
            id_reserva = cursor.lastrowid

            # Actualizar el estado de la programación
            cursor.execute("""
                UPDATE PROGRAMACION
                SET estado = 'Ocupado'
                WHERE id_programacion = %s
            """, (id_programacion,))

            # Crear el registro correspondiente (EXAMEN u OPERACION)
            if tipo_procedimiento == 'EXAMEN':
                # Crear registro de examen
                cursor.execute("""
                    INSERT INTO EXAMEN (id_reserva, fecha_examen, estado)
                    VALUES (%s, %s, 'Pendiente')
                """, (id_reserva, fecha_prog))
            else:  # OPERACION
                # Crear registro de operación
                cursor.execute("""
                    INSERT INTO OPERACION (id_reserva, fecha_operacion, estado)
                    VALUES (%s, %s, 'Programada')
                """, (id_reserva, fecha_prog))

            conexion.commit()
            cursor.close()
            conexion.close()

            return jsonify({
                'success': True,
                'id_reserva': id_reserva,
                'message': f'{tipo_procedimiento.capitalize()} agendado exitosamente'
            })

    except Exception as e:
        if 'conexion' in locals():
            try:
                conexion.rollback()
                conexion.close()
            except:
                pass
        return jsonify({'error': f'Error al crear la reserva: {str(e)}'}), 500


# ========== INCIDENCIAS ==========

@paciente_bp.route('/incidencias/generar')
def generar_incidencia():
    """Vista para generar una nueva incidencia"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('GenerarIncidenciaPaciente.html')


@paciente_bp.route('/incidencias/historial')
def historial_incidencias():
    """Vista del historial de incidencias del paciente"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('HistorialIncidenciasPaciente.html')


@paciente_bp.route('/api/incidencias/crear', methods=['POST'])
def api_crear_incidencia():
    """API para crear una nueva incidencia"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    descripcion = data.get('descripcion', '').strip()
    categoria = data.get('categoria', None)
    prioridad = data.get('prioridad', None)

    # Validaciones
    if not descripcion:
        return jsonify({'error': 'La descripción es requerida'}), 400

    if len(descripcion) < 10:
        return jsonify({'error': 'La descripción debe tener al menos 10 caracteres'}), 400

    try:
        # Obtener el id_paciente del usuario
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        # Usar el modelo Incidencia para crear la incidencia con estado='En progreso'
        resultado = Incidencia.crear(descripcion, id_paciente, categoria, prioridad)

        if resultado['success']:
            return jsonify({
                'success': True,
                'id_incidencia': resultado['id_incidencia'],
                'message': 'Incidencia registrada exitosamente'
            }), 201
        else:
            return jsonify({'error': resultado['message']}), 500

    except Exception as e:
        return jsonify({'error': f'Error al crear incidencia: {str(e)}'}), 500


@paciente_bp.route('/api/incidencias/mis-incidencias')
def api_mis_incidencias():
    """API que retorna las incidencias del paciente"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        # Obtener incidencias del paciente usando el modelo
        # Como eliminamos ASIGNAR_EMPLEADO_INCIDENCIA, necesitamos una consulta directa
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT i.id_incidencia,
                       i.descripcion,
                       DATE_FORMAT(i.fecha_registro, '%%Y-%%m-%%d') as fecha_registro,
                       i.categoria,
                       i.prioridad,
                       i.estado,
                       DATE_FORMAT(i.fecha_resolucion, '%%Y-%%m-%%d') as fecha_resolucion
                FROM INCIDENCIA i
                WHERE i.id_paciente = %s
                ORDER BY i.fecha_registro DESC
            """
            cursor.execute(sql, (id_paciente,))
            incidencias = cursor.fetchall()

            return jsonify({'incidencias': incidencias})

    except Exception as e:
        return jsonify({'error': f'Error al obtener incidencias: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass
