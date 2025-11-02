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
    # if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
    #     return jsonify({'error': 'No autorizado'}), 401

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
        'fecha_registro': data.get('fecha_registro', ''),
        'fecha_resolucion': data.get('fecha_resolucion', ''),
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

@seguridad_bp.route('/api/incidencias/<int:id_incidencia>', methods=['PUT'])
def api_actualizar_incidencia(id_incidencia):
    """API para actualizar una incidencia"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = request.get_json()
        descripcion = data.get('descripcion', '')
        estado = data.get('estado', '')
        prioridad = data.get('prioridad', '')
        categoria = data.get('categoria', '')
        observaciones = data.get('observaciones', '')

        if not estado:
            return jsonify({'error': 'El estado es requerido'}), 400

        # Validar prioridad si se proporciona
        if prioridad:
            prioridades_validas = ['Baja', 'Media', 'Alta']
            if prioridad not in prioridades_validas:
                return jsonify({'error': 'Prioridad inválida'}), 400

        # Validar categoría si se proporciona
        if categoria:
            categorias_validas = ['Hardware', 'Software', 'Equipamiento Médico', 'Infraestructura', 'Insumos', 'Otro']
            if categoria not in categorias_validas:
                return jsonify({'error': 'Categoría inválida'}), 400

        exito = Incidencia.actualizar_completa(
            id_incidencia,
            descripcion,
            estado,
            prioridad,
            categoria,
            observaciones
        )

        if exito:
            return jsonify({'mensaje': 'Incidencia actualizada exitosamente'})
        else:
            return jsonify({'error': 'Error al actualizar la incidencia'}), 500
    except Exception as e:
        print(f"Error en api_actualizar_incidencia: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@seguridad_bp.route('/api/incidencias/<int:id_incidencia>/resolver', methods=['POST'])
def api_resolver_incidencia(id_incidencia):
    """API para marcar una incidencia como resuelta"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = request.get_json()
        comentario = data.get('comentario', '')

        # Marcar como resuelta
        exito = Incidencia.resolver_incidencia(id_incidencia, comentario)

        if exito:
            return jsonify({'mensaje': 'Incidencia resuelta exitosamente'})
        else:
            return jsonify({'error': 'Error al resolver la incidencia'}), 500
    except Exception as e:
        print(f"Error en api_resolver_incidencia: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@seguridad_bp.route('/incidencias/generar-incidencia', methods=['POST'])
def crear_incidencia():
    """Crear Nueva Incidencia"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    descripcion = request.form.get('descripcion')
    categoria = request.form.get('categoria')
    prioridad = request.form.get('prioridad', 'Media')
    id_paciente = request.form.get('paciente')  # Obtener del formulario
    
    if not id_paciente:
        id_paciente = session.get('id_paciente')  # Fallback a sesión si existe

    if not descripcion or not categoria or not id_paciente:
        return jsonify({'error': 'Descripción, categoría y paciente son requeridos'}), 400

    id_incidencia = Incidencia.crear(id_paciente, descripcion, categoria, prioridad)

    if id_incidencia:
        return redirect(url_for('seguridad.incidencias'))
    else:
        return jsonify({'error': 'Error al crear la incidencia'}), 500

@seguridad_bp.route('/api/incidencias/sin-asignar', methods=['GET'])
def api_incidencias_sin_asignar():
    """API para obtener incidencias sin asignar"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    incidencias = Incidencia.obtener_sin_asignar()
    return jsonify(incidencias)

@seguridad_bp.route('/api/empleados', methods=['GET'])
def api_obtener_empleados():
    """API para obtener empleados disponibles"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    empleados = Incidencia.obtener_empleados_disponibles()
    return jsonify(empleados)

@seguridad_bp.route('/api/incidencias/<int:id_incidencia>/asignar', methods=['POST'])
def api_asignar_empleado_incidencia(id_incidencia):
    """API para asignar empleado a incidencia"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = request.get_json()

        # Validar que se recibieron datos
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400

        id_empleado = data.get('id_empleado')
        prioridad = data.get('prioridad', 'Media')
        
        # Al asignar un empleado, el estado siempre es "En proceso"
        estado = 'En proceso'

        # Validaciones de entrada
        if not id_empleado:
            return jsonify({'error': 'El empleado es requerido'}), 400

        # Validar que id_empleado sea un número
        try:
            id_empleado = int(id_empleado)
        except (ValueError, TypeError):
            return jsonify({'error': 'ID de empleado inválido'}), 400

        # Validar que id_incidencia sea válido
        if id_incidencia <= 0:
            return jsonify({'error': 'ID de incidencia inválido'}), 400

        # Validar prioridad
        prioridades_validas = ['Baja', 'Media', 'Alta']
        if prioridad not in prioridades_validas:
            return jsonify({'error': f'Prioridad inválida. Debe ser una de: {", ".join(prioridades_validas)}'}), 400

        # Verificar que la incidencia existe
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT id_incidencia FROM INCIDENCIA WHERE id_incidencia = %s", (id_incidencia,))
        incidencia = cursor.fetchone()

        if not incidencia:
            conexion.close()
            return jsonify({'error': 'La incidencia no existe'}), 404

        # Verificar que el empleado existe
        cursor.execute("SELECT id_empleado, nombres, apellidos FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
        empleado = cursor.fetchone()

        if not empleado:
            conexion.close()
            return jsonify({'error': 'El empleado no existe'}), 404

        conexion.close()

        # Actualizar la asignación
        exito = Incidencia.actualizar_asignacion(id_incidencia, id_empleado, estado, prioridad)

        if exito:
            return jsonify({
                'mensaje': 'Empleado asignado exitosamente',
                'empleado': f"{empleado['nombres']} {empleado['apellidos']}",
                'estado': estado,
                'prioridad': prioridad
            }), 200
        else:
            return jsonify({'error': 'Error al asignar empleado. Por favor, intente nuevamente.'}), 500

    except Exception as e:
        print(f"Error en api_asignar_empleado_incidencia: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@seguridad_bp.route('/api/incidencias/informe', methods=['POST'])
def api_generar_informe():
    """API para generar informe de incidencias"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    filtros = {
        'paciente': data.get('paciente', ''),
        'fecha': data.get('fecha', ''),
        'categoria': data.get('categoria', ''),
        'estado': data.get('estado', '')
    }

    incidencias = Incidencia.generar_informe(filtros)
    return jsonify(incidencias)

@seguridad_bp.route('/api/pacientes', methods=['GET'])
def api_obtener_pacientes():
    """API para obtener todos los pacientes"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    from bd import obtener_conexion
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "SELECT id_paciente, nombres, apellidos FROM PACIENTE ORDER BY nombres"
        cursor.execute(query)
        pacientes = cursor.fetchall()

        for p in pacientes:
            p['nombre_completo'] = f"{p['nombres']} {p['apellidos']}"

        return jsonify(pacientes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conexion' in locals():
            conexion.close()
