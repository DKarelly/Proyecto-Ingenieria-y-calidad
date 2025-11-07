"""
Rutas para el módulo de médicos
Gestiona el panel médico y sus funcionalidades
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from functools import wraps
from datetime import datetime

# Crear el Blueprint
medico_bp = Blueprint('medico', __name__, url_prefix='/medico')

# Decorador para verificar que el usuario es médico
def medico_required(f):
    """
    Decorador que verifica si el usuario está autenticado y tiene rol de médico (id_rol = 2)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está autenticado
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('cuentas.login'))

        # Verificar si el usuario es médico (id_rol = 2)
        if session.get('id_rol') != 2:
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function


@medico_bp.route('/')
@medico_bp.route('/panel')
@medico_required
def panel():
    """
    Ruta principal del panel médico
    Muestra el dashboard o el subsistema solicitado
    """
    subsistema = request.args.get('subsistema', None)

    # Obtener información del médico desde la sesión
    usuario = {
        'id': session.get('usuario_id'),
        'nombre': session.get('nombre_usuario'),
        'email': session.get('email_usuario'),
        'rol': session.get('rol', 'Médico'),
        'id_empleado': session.get('id_empleado')
    }

    return render_template(
        'panel_medico.html',
        subsistema=subsistema,
        usuario=usuario
    )


@medico_bp.route('/dashboard')
@medico_required
def dashboard():
    """
    Dashboard principal del médico con estadísticas y resumen
    """
    # Aquí se obtendrían las estadísticas desde la base de datos
    stats = {
        'citas_hoy': 8,
        'citas_pendientes': 2,
        'citas_completadas': 6,
        'pacientes_semana': 24,
        'diagnosticos_pendientes': 5,
        'calificacion_promedio': 4.9
    }

    return render_template(
        'panel_medico.html',
        subsistema=None,
        stats=stats
    )


@medico_bp.route('/agenda')
@medico_required
def agenda():
    """
    Vista de agenda médica con calendario de citas
    """
    fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))

    # Aquí se obtendrían las citas desde la base de datos
    # Por ahora retornamos datos de ejemplo

    return render_template(
        'panel_medico.html',
        subsistema='agenda',
        fecha=fecha
    )


@medico_bp.route('/pacientes')
@medico_required
def pacientes():
    """
    Lista de pacientes del médico
    """
    busqueda = request.args.get('q', '')

    # Aquí se obtendrían los pacientes desde la base de datos
    # Filtrados por el médico actual

    return render_template(
        'panel_medico.html',
        subsistema='pacientes',
        busqueda=busqueda
    )


@medico_bp.route('/paciente/<int:paciente_id>')
@medico_required
def ver_paciente(paciente_id):
    """
    Ver detalles completos de un paciente específico
    """
    # Aquí se obtendría la información completa del paciente
    # incluyendo historial médico, diagnósticos, etc.

    return render_template(
        'medico_detalle_paciente.html',
        paciente_id=paciente_id
    )


@medico_bp.route('/diagnosticos')
@medico_bp.route('/diagnosticos/nuevo')
@medico_required
def diagnosticos():
    """
    Formulario para registrar diagnósticos
    """
    return render_template(
        'panel_medico.html',
        subsistema='diagnosticos'
    )


@medico_bp.route('/diagnosticos/guardar', methods=['POST'])
@medico_required
def guardar_diagnostico():
    """
    Guarda un nuevo diagnóstico en la base de datos
    """
    try:
        # Obtener datos del formulario
        paciente_id = request.form.get('paciente_id')
        fecha_consulta = request.form.get('fecha_consulta')
        tipo_consulta = request.form.get('tipo_consulta')
        sintomas = request.form.get('sintomas')
        diagnostico = request.form.get('diagnostico')
        tratamiento = request.form.get('tratamiento')
        observaciones = request.form.get('observaciones')
        medico_id = session.get('id_empleado')

        # Aquí se guardaría en la base de datos
        # Por ahora solo retornamos éxito

        flash('Diagnóstico registrado exitosamente', 'success')
        return redirect(url_for('medico.diagnosticos'))

    except Exception as e:
        flash(f'Error al guardar el diagnóstico: {str(e)}', 'danger')
        return redirect(url_for('medico.diagnosticos'))


@medico_bp.route('/historial')
@medico_required
def historial():
    """
    Vista de historial médico de pacientes
    """
    return render_template(
        'panel_medico.html',
        subsistema='historial'
    )


@medico_bp.route('/recetas')
@medico_required
def recetas():
    """
    Gestión de recetas médicas
    """
    return render_template(
        'panel_medico.html',
        subsistema='recetas'
    )


@medico_bp.route('/recetas/nueva', methods=['POST'])
@medico_required
def nueva_receta():
    """
    Crea una nueva receta médica
    """
    try:
        paciente_id = request.form.get('paciente_id')
        medicamentos = request.form.get('medicamentos')
        dosis = request.form.get('dosis')
        duracion = request.form.get('duracion')
        indicaciones = request.form.get('indicaciones')
        medico_id = session.get('id_empleado')

        # Aquí se guardaría en la base de datos

        flash('Receta generada exitosamente', 'success')
        return redirect(url_for('medico.recetas'))

    except Exception as e:
        flash(f'Error al generar la receta: {str(e)}', 'danger')
        return redirect(url_for('medico.recetas'))


@medico_bp.route('/reportes')
@medico_required
def reportes():
    """
    Generación de reportes médicos
    """
    return render_template(
        'panel_medico.html',
        subsistema='reportes'
    )


@medico_bp.route('/notificaciones')
@medico_required
def notificaciones():
    """
    Centro de notificaciones del médico
    """
    return render_template(
        'panel_medico.html',
        subsistema='notificaciones'
    )


# API Endpoints para consultas AJAX
@medico_bp.route('/api/citas-hoy')
@medico_required
def api_citas_hoy():
    """
    Retorna las citas del día actual en formato JSON
    """
    medico_id = session.get('id_empleado')

    # Aquí se obtendrían las citas desde la base de datos
    citas = [
        {
            'id': 1,
            'paciente': 'Juan Pérez García',
            'hora': '10:00 AM',
            'tipo': 'Consulta General',
            'estado': 'pendiente'
        },
        {
            'id': 2,
            'paciente': 'María García López',
            'hora': '09:30 AM',
            'tipo': 'Control de Presión',
            'estado': 'completada'
        }
    ]

    return jsonify({'success': True, 'citas': citas})


@medico_bp.route('/api/estadisticas')
@medico_required
def api_estadisticas():
    """
    Retorna estadísticas del médico en formato JSON
    """
    medico_id = session.get('id_empleado')

    # Aquí se calcularían las estadísticas desde la base de datos
    stats = {
        'citas_hoy': 8,
        'citas_semana': 24,
        'pacientes_activos': 156,
        'diagnosticos_mes': 42,
        'calificacion': 4.9
    }

    return jsonify({'success': True, 'estadisticas': stats})


@medico_bp.route('/api/buscar-paciente')
@medico_required
def api_buscar_paciente():
    """
    Busca pacientes por nombre o DNI
    """
    query = request.args.get('q', '')
    medico_id = session.get('id_empleado')

    # Aquí se buscarían los pacientes en la base de datos
    pacientes = []

    return jsonify({'success': True, 'pacientes': pacientes})


# Manejo de errores específico para el módulo médico
@medico_bp.errorhandler(404)
def medico_not_found(error):
    """
    Maneja errores 404 en el módulo médico
    """
    flash('La página solicitada no existe', 'warning')
    return redirect(url_for('medico.panel'))


@medico_bp.errorhandler(500)
def medico_server_error(error):
    """
    Maneja errores 500 en el módulo médico
    """
    flash('Ha ocurrido un error en el servidor. Por favor, intenta nuevamente', 'danger')
    return redirect(url_for('medico.panel'))
