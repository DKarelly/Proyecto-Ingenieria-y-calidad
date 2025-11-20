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
