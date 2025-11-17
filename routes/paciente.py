from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from bd import obtener_conexion
from models.paciente import Paciente

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
    """API que retorna el historial clínico del paciente (citas completadas con diagnósticos)"""
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
                       esp.nombre as especialidad
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

            return jsonify({'historial': historial})

    except Exception as e:
        return jsonify({'error': f'Error al obtener historial clínico: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


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

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            from datetime import datetime
            fecha_actual = datetime.now().date()

            sql = """
                INSERT INTO INCIDENCIA (descripcion, fecha_registro, id_paciente, categoria, prioridad)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (descripcion, fecha_actual, id_paciente, categoria, prioridad))
            conexion.commit()
            id_incidencia = cursor.lastrowid

        return jsonify({
            'success': True,
            'id_incidencia': id_incidencia,
            'message': 'Incidencia registrada exitosamente'
        }), 201

    except Exception as e:
        if conexion:
            conexion.rollback()
        return jsonify({'error': f'Error al crear incidencia: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


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

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT i.id_incidencia,
                       i.descripcion,
                       i.fecha_registro,
                       i.categoria,
                       i.prioridad,
                       a.estado_historial as estado_resolucion,
                       a.fecha_resolucion,
                       a.observaciones as observaciones_resolucion,
                       CONCAT(e.nombres, ' ', e.apellidos) as empleado_asignado
                FROM INCIDENCIA i
                LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA a ON i.id_incidencia = a.id_incidencia
                LEFT JOIN EMPLEADO e ON a.id_empleado = e.id_empleado
                WHERE i.id_paciente = %s
                ORDER BY i.fecha_registro DESC
            """
            cursor.execute(sql, (id_paciente,))
            incidencias = cursor.fetchall()
            
            # Convertir fechas a string para serialización JSON
            for incidencia in incidencias:
                if incidencia.get('fecha_registro'):
                    incidencia['fecha_registro'] = incidencia['fecha_registro'].strftime('%Y-%m-%d %H:%M:%S')
                if incidencia.get('fecha_resolucion'):
                    incidencia['fecha_resolucion'] = incidencia['fecha_resolucion'].strftime('%Y-%m-%d %H:%M:%S')

            return jsonify({'incidencias': incidencias})

    except Exception as e:
        return jsonify({'error': f'Error al obtener incidencias: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


# ========== AUTORIZACIONES DE EXÁMENES Y OPERACIONES ==========

@paciente_bp.route('/autorizaciones')
def autorizaciones():
    """Vista de autorizaciones médicas del paciente"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('AutorizacionesPaciente.html')


@paciente_bp.route('/api/autorizaciones-pendientes')
def api_autorizaciones_pendientes():
    """API que retorna las autorizaciones pendientes del paciente"""
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
            # Obtener autorizaciones de exámenes pendientes
            sql_examenes = """
                SELECT ae.id_autorizacion_examen,
                       ae.id_cita,
                       ae.estado,
                       ae.fecha_autorizacion,
                       ae.observaciones,
                       s.nombre as servicio_nombre,
                       s.descripcion as servicio_descripcion,
                       e.nombres as medico_nombres,
                       e.apellidos as medico_apellidos,
                       c.fecha_cita
                FROM AUTORIZACION_EXAMEN ae
                INNER JOIN SERVICIO s ON ae.id_servicio = s.id_servicio
                INNER JOIN EMPLEADO e ON ae.id_empleado_autoriza = e.id_empleado
                INNER JOIN CITA c ON ae.id_cita = c.id_cita
                WHERE ae.id_paciente = %s
                  AND ae.estado = 'Pendiente'
                ORDER BY ae.fecha_autorizacion DESC
            """
            cursor.execute(sql_examenes, (id_paciente,))
            autorizaciones_examenes = cursor.fetchall()

            # Obtener autorizaciones de operaciones pendientes
            sql_operaciones = """
                SELECT ao.id_autorizacion_operacion,
                       ao.id_cita,
                       ao.estado,
                       ao.fecha_autorizacion,
                       ao.observaciones,
                       ao.es_derivacion,
                       s.nombre as servicio_nombre,
                       s.descripcion as servicio_descripcion,
                       e1.nombres as medico_autoriza_nombres,
                       e1.apellidos as medico_autoriza_apellidos,
                       e2.nombres as medico_asignado_nombres,
                       e2.apellidos as medico_asignado_apellidos,
                       c.fecha_cita
                FROM AUTORIZACION_OPERACION ao
                INNER JOIN SERVICIO s ON ao.id_servicio = s.id_servicio
                INNER JOIN EMPLEADO e1 ON ao.id_empleado_autoriza = e1.id_empleado
                LEFT JOIN EMPLEADO e2 ON ao.id_empleado_asignado = e2.id_empleado
                INNER JOIN CITA c ON ao.id_cita = c.id_cita
                WHERE ao.id_paciente = %s
                  AND ao.estado = 'Pendiente'
                ORDER BY ao.fecha_autorizacion DESC
            """
            cursor.execute(sql_operaciones, (id_paciente,))
            autorizaciones_operaciones = cursor.fetchall()

            # Convertir fechas a string para serialización JSON
            for auth in autorizaciones_examenes:
                if auth.get('fecha_autorizacion'):
                    auth['fecha_autorizacion'] = auth['fecha_autorizacion'].strftime('%Y-%m-%d %H:%M:%S')
                if auth.get('fecha_cita'):
                    auth['fecha_cita'] = auth['fecha_cita'].strftime('%Y-%m-%d')

            for auth in autorizaciones_operaciones:
                if auth.get('fecha_autorizacion'):
                    auth['fecha_autorizacion'] = auth['fecha_autorizacion'].strftime('%Y-%m-%d %H:%M:%S')
                if auth.get('fecha_cita'):
                    auth['fecha_cita'] = auth['fecha_cita'].strftime('%Y-%m-%d')

            return jsonify({
                'autorizaciones_examenes': autorizaciones_examenes,
                'autorizaciones_operaciones': autorizaciones_operaciones
            })

    except Exception as e:
        return jsonify({'error': f'Error al obtener autorizaciones: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass
