from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.incidencia import Incidencia

seguridad_bp = Blueprint('seguridad', __name__)

@seguridad_bp.route('/')
def panel():
    """Panel de Seguridad"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Verificar que el rol esté entre 1 y 5
    id_rol = session.get('id_rol')
    if id_rol is None or id_rol not in [1, 2, 3, 4, 5]:
        return redirect(url_for('home'))

    return render_template('panel.html', subsistema='seguridad')

@seguridad_bp.route('/incidencias')
def incidencias():
    """Panel de Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('panel.html', subsistema='incidencias')

@seguridad_bp.route('/incidencias/generar-incidencia')
def generar_incidencia():
    """Generar Nueva Incidencia"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('generarIncidencia.html')

@seguridad_bp.route('/incidencias/asignar-responsable')
def asignar_responsable():
    """Asignar Responsable a Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('asignarResponsable.html')

@seguridad_bp.route('/incidencias/generar-informe')
def generar_informe():
    """Generar Informe de Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('generar_informe.html')

@seguridad_bp.route('/incidencias/ocupacion-recursos')
def ocupacion_recursos():
    """Generar Reporte de Ocupación de Recursos"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('generar_ocupacion_recursos.html')

@seguridad_bp.route('/incidencias/reporte-actividad')
def reporte_actividad():
    """Generar Reporte de Actividad"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('generar_reporte_actividad.html')

@seguridad_bp.route('/incidencias/consultar-actividad')
def consultar_actividad():
    """Consultar Actividad del Sistema"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('consultar_actividad.html')

@seguridad_bp.route('/incidencias/consultar-incidencia')
def consultar_incidencia():
    """Consultar Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('consultarIncidencia.html')

# API Routes for Incidencias

@seguridad_bp.route('/api/incidencias', methods=['GET'])
def api_obtener_incidencias():
    """API para obtener todas las incidencias"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    incidencias = Incidencia.obtener_todas()
    return jsonify(incidencias)

@seguridad_bp.route('/api/incidencias/buscar', methods=['POST'])
def api_buscar_incidencias():
    """API para buscar incidencias con filtros"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    filtros = {
        'paciente': data.get('paciente', ''),
        'empleado': data.get('empleado', ''),
        'fecha_registro_desde': data.get('fecha_registro_desde', ''),
        'fecha_registro_hasta': data.get('fecha_registro_hasta', ''),
        'fecha_resolucion_desde': data.get('fecha_resolucion_desde', ''),
        'fecha_resolucion_hasta': data.get('fecha_resolucion_hasta', ''),
        'estado': data.get('estado', '')
    }

    incidencias = Incidencia.buscar(filtros)
    return jsonify(incidencias)

@seguridad_bp.route('/api/incidencias/buscar-pacientes', methods=['GET'])
def api_buscar_pacientes():
    """API para buscar pacientes (autocompletado)"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    termino = request.args.get('termino', '')
    pacientes = Incidencia.buscar_pacientes(termino)
    return jsonify(pacientes)

@seguridad_bp.route('/api/incidencias/buscar-empleados', methods=['GET'])
def api_buscar_empleados():
    """API para buscar empleados (autocompletado)"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    termino = request.args.get('termino', '')
    empleados = Incidencia.buscar_empleados(termino)
    return jsonify(empleados)
