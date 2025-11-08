"""
Rutas para el módulo de médicos
Gestiona el panel médico y sus funcionalidades
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from functools import wraps
from datetime import datetime, date
from bd import obtener_conexion

# Crear el Blueprint
medico_bp = Blueprint('medico', __name__, url_prefix='/medico')

# Funciones auxiliares para obtener datos
def obtener_estadisticas_medico(id_empleado):
    """
    Obtiene las estadísticas del médico desde la base de datos
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener el id_horario del médico
        cursor.execute("""
            SELECT id_horario FROM HORARIO 
            WHERE id_empleado = %s
        """, (id_empleado,))
        horarios = cursor.fetchall()
        horarios_ids = [h['id_horario'] for h in horarios]
        
        if not horarios_ids:
            return {
                'citas_hoy': 0,
                'citas_pendientes': 0,
                'citas_completadas': 0,
                'pacientes_semana': 0,
                'diagnosticos_pendientes': 0
            }
        
        # Citas de hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM RESERVA r
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            WHERE p.fecha = CURDATE()
            AND p.id_horario IN ({})
        """.format(','.join(['%s'] * len(horarios_ids))), horarios_ids)
        citas_hoy = cursor.fetchone()['total']
        
        # Citas pendientes hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM RESERVA r
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            WHERE p.fecha = CURDATE()
            AND r.estado = 'Pendiente'
            AND p.id_horario IN ({})
        """.format(','.join(['%s'] * len(horarios_ids))), horarios_ids)
        citas_pendientes = cursor.fetchone()['total']
        
        # Citas completadas hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM RESERVA r
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            WHERE p.fecha = CURDATE()
            AND r.estado = 'Completada'
            AND p.id_horario IN ({})
        """.format(','.join(['%s'] * len(horarios_ids))), horarios_ids)
        citas_completadas = cursor.fetchone()['total']
        
        # Pacientes atendidos esta semana
        cursor.execute("""
            SELECT COUNT(DISTINCT r.id_paciente) as total
            FROM RESERVA r
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            WHERE YEARWEEK(p.fecha, 1) = YEARWEEK(CURDATE(), 1)
            AND p.id_horario IN ({})
        """.format(','.join(['%s'] * len(horarios_ids))), horarios_ids)
        pacientes_semana = cursor.fetchone()['total']
        
        # Diagnósticos pendientes (reservas confirmadas o en proceso)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM RESERVA r
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            WHERE r.estado IN ('Confirmada', 'En proceso')
            AND p.id_horario IN ({})
        """.format(','.join(['%s'] * len(horarios_ids))), horarios_ids)
        diagnosticos_pendientes = cursor.fetchone()['total']
        
        return {
            'citas_hoy': citas_hoy,
            'citas_pendientes': citas_pendientes,
            'citas_completadas': citas_completadas,
            'pacientes_semana': pacientes_semana,
            'diagnosticos_pendientes': diagnosticos_pendientes
        }
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {
            'citas_hoy': 0,
            'citas_pendientes': 0,
            'citas_completadas': 0,
            'pacientes_semana': 0,
            'diagnosticos_pendientes': 0
        }
    finally:
        if conexion:
            conexion.close()


def obtener_citas_hoy(id_empleado):
    """
    Obtiene las citas del día actual del médico
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener el id_horario del médico
        cursor.execute("""
            SELECT id_horario FROM HORARIO 
            WHERE id_empleado = %s
        """, (id_empleado,))
        horarios = cursor.fetchall()
        horarios_ids = [h['id_horario'] for h in horarios]
        
        if not horarios_ids:
            return []
        
        # Obtener citas de hoy con información del paciente
        cursor.execute("""
            SELECT 
                r.id_reserva,
                r.estado,
                r.tipo,
                p.fecha,
                p.hora_inicio,
                p.hora_fin,
                pac.nombre1 as nombre_paciente,
                pac.apellido_paterno,
                pac.apellido_materno,
                s.nombre as tipo_servicio
            FROM RESERVA r
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
            LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
            WHERE p.fecha = CURDATE()
            AND p.id_horario IN ({})
            ORDER BY p.hora_inicio
        """.format(','.join(['%s'] * len(horarios_ids))), horarios_ids)
        
        citas = cursor.fetchall()
        
        # Formatear los datos
        citas_formateadas = []
        for cita in citas:
            # Formatear hora
            hora = cita['hora_inicio'].strftime('%I:%M %p') if cita['hora_inicio'] else 'N/A'
            
            # Nombre completo del paciente
            nombre_completo = f"{cita['nombre_paciente']} {cita['apellido_paterno']}"
            if cita['apellido_materno']:
                nombre_completo += f" {cita['apellido_materno']}"
            
            # Tipo de servicio o consulta
            tipo_consulta = cita['tipo_servicio'] if cita['tipo_servicio'] else 'Consulta General'
            
            citas_formateadas.append({
                'id': cita['id_reserva'],
                'paciente': nombre_completo,
                'hora': hora,
                'tipo': tipo_consulta,
                'estado': cita['estado']
            })
        
        return citas_formateadas
        
    except Exception as e:
        print(f"Error al obtener citas de hoy: {e}")
        return []
    finally:
        if conexion:
            conexion.close()


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
    id_empleado = session.get('id_empleado')

    # Obtener información del médico desde la sesión
    usuario = {
        'id': session.get('usuario_id'),
        'nombre': session.get('nombre_usuario'),
        'email': session.get('email_usuario'),
        'rol': session.get('rol', 'Médico'),
        'id_empleado': id_empleado
    }

    # Obtener estadísticas del médico
    stats = obtener_estadisticas_medico(id_empleado)
    
    # Obtener citas de hoy
    citas_hoy = obtener_citas_hoy(id_empleado)

    return render_template(
        'panel_medico.html',
        subsistema=subsistema,
        usuario=usuario,
        stats=stats,
        citas_hoy=citas_hoy
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
