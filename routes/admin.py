from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.servicio import Servicio
from models.catalogos import TipoServicio, TipoRecurso
from models.recurso import Recurso
from models.horario import Horario
from models.empleado import Empleado
from models.agenda import Agenda
from models.programacion import Programacion
from models.bloqueoHorario import BloqueoHorario

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def panel():
    """Panel de Administración y Gestión"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Restringir acceso: solo Administrador (rol 1) puede ver el panel de administración
    id_rol = session.get('id_rol')
    if id_rol != 1:
        # Redirigir según el rol del empleado
        if id_rol == 2:  # Médico
            return redirect(url_for('medico.panel'))
        else:            # Otros empleados (recepción, farmacia, etc.)
            return redirect(url_for('trabajador.panel'))

    # Redirigir al dashboard canónico /admin/panel
    subsistema = request.args.get('subsistema')
    return redirect(url_for('admin_panel', subsistema=subsistema))

@admin_bp.route('/consultar-agenda-medica')
def consultar_agenda_medica():
    """Consultar Agenda Médica"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('consultaAgendaMedica.html')

@admin_bp.route('/consultar-incidencia')
def consultar_incidencia():
    """Consultar Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('consultarIncidencia.html')

@admin_bp.route('/gestionar-bloqueo-horarios')
def gestionar_bloqueo_horarios():
    """Gestionar Bloqueo de Horarios"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestionarBloqueo.html')

@admin_bp.route('/gestionar-catalogo-servicios')
def gestionar_catalogo_servicios():
    """Gestionar Catálogo de Servicios"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestionCatalogoServicio.html')

@admin_bp.route('/gestionar-programacion')
def gestionar_programacion():
    """Gestionar programación"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestionprogramacion.html')

@admin_bp.route('/gestionar-horarios-laborales')
def gestionar_horarios_laborales():
    """Gestionar Horarios Laborales"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestionHorariosLaborables.html')

@admin_bp.route('/gestionar-recursos-fisicos')
def gestionar_recursos_fisicos():
    """Gestionar Recursos Físicos"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestionRecursosFisicos.html')

# API Routes for Gestion Catalogo Servicios

@admin_bp.route('/api/servicios', methods=['GET'])
def api_obtener_servicios():
    """API para obtener todos los servicios o filtrados por tipo"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    tipo_servicio = request.args.get('tipo_servicio')
    if tipo_servicio:
        servicios = Servicio.obtener_por_tipo(int(tipo_servicio))
    else:
        servicios = Servicio.obtener_todos()
    return jsonify(servicios)

@admin_bp.route('/api/tipos-servicio', methods=['GET'])
def api_obtener_tipos_servicio():
    """API para obtener tipos de servicio"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    tipos = TipoServicio.obtener_todos()
    return jsonify(tipos)

@admin_bp.route('/api/especialidades', methods=['GET'])
def api_obtener_especialidades():
    """API para obtener especialidades"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    from models.catalogos import Especialidad
    especialidades = Especialidad.obtener_todas()
    return jsonify(especialidades)

@admin_bp.route('/api/servicios/buscar', methods=['POST'])
def api_buscar_servicios():
    """API para buscar servicios con filtros"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    tipo_servicio = data.get('tipo_servicio', '')
    especialidad = data.get('especialidad', '')
    termino = data.get('termino', '')

    if tipo_servicio and especialidad and termino:
        # Buscar por tipo, especialidad y término
        servicios = Servicio.buscar(termino)
        servicios_filtrados = [s for s in servicios if str(s['id_tipo_servicio']) == tipo_servicio and str(s.get('id_especialidad', '')) == especialidad]
    elif tipo_servicio and especialidad:
        # Buscar por tipo y especialidad
        servicios = Servicio.obtener_por_tipo(int(tipo_servicio))
        servicios_filtrados = [s for s in servicios if str(s.get('id_especialidad', '')) == especialidad]
    elif tipo_servicio and termino:
        # Buscar por tipo y término
        servicios = Servicio.buscar(termino)
        servicios_filtrados = [s for s in servicios if str(s['id_tipo_servicio']) == tipo_servicio]
    elif especialidad and termino:
        # Buscar por especialidad y término
        servicios = Servicio.buscar(termino)
        servicios_filtrados = [s for s in servicios if str(s.get('id_especialidad', '')) == especialidad]
    elif tipo_servicio:
        # Buscar por tipo
        servicios_filtrados = Servicio.obtener_por_tipo(int(tipo_servicio))
    elif especialidad:
        # Buscar por especialidad
        servicios_filtrados = Servicio.obtener_por_especialidad(int(especialidad))
    elif termino:
        # Buscar por término
        servicios_filtrados = Servicio.buscar(termino)
    else:
        # Todos los servicios
        servicios_filtrados = Servicio.obtener_todos()

    return jsonify(servicios_filtrados)

@admin_bp.route('/api/servicios', methods=['POST'])
def api_crear_servicio():
    """API para crear un nuevo servicio"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    estado = data.get('estado')
    id_tipo_servicio = data.get('id_tipo_servicio')
    id_especialidad = data.get('id_especialidad')

    if not nombre or not descripcion or not estado or not id_tipo_servicio:
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    resultado = Servicio.crear(nombre, descripcion, id_tipo_servicio, id_especialidad)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Servicio creado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/servicios/<int:id_servicio>', methods=['PUT'])
def api_actualizar_servicio(id_servicio):
    """API para actualizar un servicio"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    estado = data.get('estado')
    id_tipo_servicio = data.get('id_tipo_servicio')
    id_especialidad = data.get('id_especialidad')

    resultado = Servicio.actualizar(id_servicio, nombre=nombre, descripcion=descripcion, estado=estado, id_tipo_servicio=id_tipo_servicio, id_especialidad=id_especialidad)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Servicio actualizado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/servicios/<int:id_servicio>', methods=['GET'])
def api_obtener_servicio(id_servicio):
    """API para obtener un servicio específico"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    servicio = Servicio.obtener_por_id(id_servicio)
    if servicio:
        return jsonify(servicio)
    else:
        return jsonify({'error': 'Servicio no encontrado'}), 404

@admin_bp.route('/api/servicios/<int:id_servicio>', methods=['DELETE'])
def api_eliminar_servicio(id_servicio):
    """API para eliminar (desactivar) un servicio"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    resultado = Servicio.eliminar(id_servicio)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Servicio desactivado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

# API Routes for Gestion Recursos Fisicos

@admin_bp.route('/api/recursos', methods=['GET'])
def api_obtener_recursos():
    """API para obtener todos los recursos"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    recursos = Recurso.obtener_todos()
    return jsonify(recursos)

@admin_bp.route('/api/tipos-recurso', methods=['GET'])
def api_obtener_tipos_recurso():
    """API para obtener tipos de recurso"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    tipos = TipoRecurso.obtener_todos()
    return jsonify(tipos)

@admin_bp.route('/api/recursos/buscar', methods=['POST'])
def api_buscar_recursos():
    """API para buscar recursos con filtros"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    tipo_recurso = data.get('tipo_recurso', '')
    termino = data.get('termino', '')

    if tipo_recurso and termino:
        # Buscar por tipo y término
        recursos = Recurso.buscar(termino)
        recursos_filtrados = [r for r in recursos if str(r['id_tipo_recurso']) == tipo_recurso]
    elif tipo_recurso:
        # Buscar por tipo
        recursos_filtrados = Recurso.obtener_por_tipo(int(tipo_recurso))
    elif termino:
        # Buscar por término
        recursos_filtrados = Recurso.buscar(termino)
    else:
        # Todos los recursos
        recursos_filtrados = Recurso.obtener_todos()

    return jsonify(recursos_filtrados)

@admin_bp.route('/api/recursos', methods=['POST'])
def api_crear_recurso():
    """API para crear un nuevo recurso"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    nombre = data.get('nombre')
    estado = data.get('estado')
    id_tipo_recurso = data.get('id_tipo_recurso')

    if not nombre or not estado or not id_tipo_recurso:
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    resultado = Recurso.crear(nombre, id_tipo_recurso)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Recurso creado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/recursos/<int:id_recurso>', methods=['PUT'])
def api_actualizar_recurso(id_recurso):
    """API para actualizar un recurso"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    nombre = data.get('nombre')
    estado = data.get('estado')
    id_tipo_recurso = data.get('id_tipo_recurso')

    resultado = Recurso.actualizar(id_recurso, nombre=nombre, estado=estado, id_tipo_recurso=id_tipo_recurso)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Recurso actualizado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/recursos/<int:id_recurso>', methods=['GET'])
def api_obtener_recurso(id_recurso):
    """API para obtener un recurso específico"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    recurso = Recurso.obtener_por_id(id_recurso)
    if recurso:
        return jsonify(recurso)
    else:
        return jsonify({'error': 'Recurso no encontrado'}), 404

@admin_bp.route('/api/recursos/<int:id_recurso>', methods=['DELETE'])
def api_eliminar_recurso(id_recurso):
    """API para eliminar (desactivar) un recurso"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    resultado = Recurso.eliminar(id_recurso)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Recurso desactivado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

# API Routes for Gestion Horarios Laborales

@admin_bp.route('/api/horarios', methods=['GET'])
def api_obtener_horarios():
    """API para obtener todos los horarios"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    horarios = Horario.obtener_todos()

    # Convertir objetos datetime a strings para JSON serialization
    for horario in horarios:
        if 'hora_inicio' in horario and horario['hora_inicio']:
            horario['hora_inicio'] = str(horario['hora_inicio'])
        if 'hora_fin' in horario and horario['hora_fin']:
            horario['hora_fin'] = str(horario['hora_fin'])
        if 'fecha' in horario and horario['fecha']:
            horario['fecha'] = horario['fecha'].isoformat()

    return jsonify(horarios)

@admin_bp.route('/api/empleados', methods=['GET'])
def api_obtener_empleados():
    """API para obtener todos los empleados"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    empleados = Empleado.obtener_todos()
    return jsonify(empleados)

@admin_bp.route('/api/empleados/buscar', methods=['GET'])
def api_buscar_empleados():
    """API para buscar empleados por término"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    termino = request.args.get('termino', '')

    if termino:
        empleados = Empleado.buscar(termino)
    else:
        empleados = Empleado.obtener_todos()

    return jsonify(empleados)

@admin_bp.route('/api/horarios/buscar', methods=['POST'])
def api_buscar_horarios():
    """API para buscar horarios por fecha"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    fecha = data.get('fecha', '')

    if fecha:
        # Buscar por fecha
        horarios_filtrados = Horario.obtener_por_fecha(fecha)
    else:
        # Todos los horarios
        horarios_filtrados = Horario.obtener_todos()

    # Convertir objetos datetime a strings para JSON serialization
    for horario in horarios_filtrados:
        if 'hora_inicio' in horario and horario['hora_inicio']:
            horario['hora_inicio'] = str(horario['hora_inicio'])
        if 'hora_fin' in horario and horario['hora_fin']:
            horario['hora_fin'] = str(horario['hora_fin'])
        if 'fecha' in horario and horario['fecha']:
            horario['fecha'] = horario['fecha'].isoformat()

    return jsonify(horarios_filtrados)

@admin_bp.route('/api/horarios', methods=['POST'])
def api_crear_horario():
    """API para crear un nuevo horario"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    id_empleado = data.get('id_empleado')
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    activo = data.get('activo', 1)

    if not id_empleado or not fecha or not hora_inicio or not hora_fin:
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    resultado = Horario.crear(id_empleado, fecha, hora_inicio, hora_fin, activo)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Horario creado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/horarios/<int:id_horario>', methods=['PUT'])
def api_actualizar_horario(id_horario):
    """API para actualizar un horario"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    activo = data.get('activo', 1)

    resultado = Horario.actualizar(id_horario, fecha=fecha, hora_inicio=hora_inicio,
                                  hora_fin=hora_fin, activo=activo)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Horario actualizado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/horarios/<int:id_horario>', methods=['GET'])
def api_obtener_horario(id_horario):
    """API para obtener un horario específico"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    horario = Horario.obtener_por_id(id_horario)
    if horario:
        # Convertir objetos datetime a strings para JSON serialization
        if 'hora_inicio' in horario and horario['hora_inicio']:
            horario['hora_inicio'] = str(horario['hora_inicio'])
        if 'hora_fin' in horario and horario['hora_fin']:
            horario['hora_fin'] = str(horario['hora_fin'])
        if 'fecha' in horario and horario['fecha']:
            horario['fecha'] = horario['fecha'].isoformat()
        return jsonify(horario)
    else:
        return jsonify({'error': 'Horario no encontrado'}), 404

@admin_bp.route('/api/horarios/<int:id_horario>', methods=['DELETE'])
def api_eliminar_horario(id_horario):
    """API para eliminar (desactivar) un horario"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    # Cambiar estado a inactivo en lugar de eliminar
    resultado = Horario.actualizar_estado(id_horario, 0)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Horario dado de baja exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

# API Routes for Consultar Agenda Medica

@admin_bp.route('/api/empleados/buscar-agenda', methods=['GET'])
def api_buscar_empleados_agenda():
    """API para obtener empleados para agenda (autocomplete)"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    empleados = Empleado.obtener_todos()
    empleados_activos = [e for e in empleados if e.get('estado', '') == 'Activo']
    return jsonify(empleados_activos)

@admin_bp.route('/api/servicios/buscar-agenda', methods=['GET'])
def api_buscar_servicios_agenda():
    """API para obtener servicios activos para agenda"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    servicios = Servicio.obtener_todos()
    servicios_activos = [s for s in servicios if s.get('estado', '') == 'Activo']
    return jsonify(servicios_activos)

@admin_bp.route('/api/agenda/consultar', methods=['POST'])
def api_consultar_agenda():
    """API para consultar la agenda médica con filtros"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    id_empleado = data.get('id_empleado')
    fecha = data.get('fecha')
    id_servicio = data.get('id_servicio')

    # Convertir a int si no son None
    if id_empleado:
        id_empleado = int(id_empleado)
    if id_servicio:
        id_servicio = int(id_servicio)

    agenda = Agenda.consultar_agenda(id_empleado=id_empleado, fecha=fecha, id_servicio=id_servicio)
    return jsonify(agenda)

# API Routes for Gestion Programacion

@admin_bp.route('/api/programaciones', methods=['GET'])
def api_obtener_programaciones():
    """API para obtener todas las programaciones o filtradas por parámetros"""
    # Temporarily commented out for testing
    # if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
    #     return jsonify({'error': 'No autorizado'}), 401

    # Obtener parámetros de consulta
    fecha = request.args.get('fecha', '')
    tipo_servicio = request.args.get('tipo_servicio', '')
    servicio = request.args.get('servicio', '')
    estado = request.args.get('estado', '')
    id_empleado = request.args.get('id_empleado', '')

    # Convertir a int si no están vacíos
    id_tipo_servicio = int(tipo_servicio) if tipo_servicio else None
    id_servicio = int(servicio) if servicio else None
    id_empleado_int = int(id_empleado) if id_empleado else None

    if fecha or id_tipo_servicio or id_servicio or estado or id_empleado_int:
        # Usar búsqueda con filtros
        programaciones = Programacion.buscar_por_filtros(fecha=fecha, id_tipo_servicio=id_tipo_servicio, id_servicio=id_servicio, estado=estado, id_empleado=id_empleado_int)
    else:
        # Obtener todas las programaciones
        programaciones = Programacion.obtener_todos()

    # Convertir objetos datetime a strings para JSON serialization
    for prog in programaciones:
        if 'hora_inicio' in prog and prog['hora_inicio']:
            if hasattr(prog['hora_inicio'], 'total_seconds'):
                # Es timedelta
                total_seconds = int(prog['hora_inicio'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                prog['hora_inicio'] = f"{hours:02d}:{minutes:02d}"
            else:
                prog['hora_inicio'] = str(prog['hora_inicio'])
        if 'hora_fin' in prog and prog['hora_fin']:
            if hasattr(prog['hora_fin'], 'total_seconds'):
                # Es timedelta
                total_seconds = int(prog['hora_fin'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                prog['hora_fin'] = f"{hours:02d}:{minutes:02d}"
            else:
                prog['hora_fin'] = str(prog['hora_fin'])
        if 'fecha' in prog and prog['fecha']:
            prog['fecha'] = prog['fecha'].isoformat()

    return jsonify(programaciones)

@admin_bp.route('/api/programaciones/buscar', methods=['POST'])
def api_buscar_programaciones():
    """API para buscar programaciones con filtros"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    fecha = data.get('fecha', '')
    id_empleado = data.get('id_empleado', '')
    estado = data.get('estado', '')
    id_servicio = data.get('id_servicio', '')

    # Convertir a int si no están vacíos
    if id_empleado:
        id_empleado = int(id_empleado)
    if id_servicio:
        id_servicio = int(id_servicio)

    programaciones_filtradas = Programacion.buscar_por_filtros(fecha=fecha, id_empleado=id_empleado, estado=estado, id_servicio=id_servicio)

    # Convertir objetos datetime a strings para JSON serialization
    for prog in programaciones_filtradas:
        if 'hora_inicio' in prog and prog['hora_inicio']:
            if hasattr(prog['hora_inicio'], 'total_seconds'):
                # Es timedelta
                total_seconds = int(prog['hora_inicio'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                prog['hora_inicio'] = f"{hours:02d}:{minutes:02d}"
            else:
                prog['hora_inicio'] = str(prog['hora_inicio'])
        if 'hora_fin' in prog and prog['hora_fin']:
            if hasattr(prog['hora_fin'], 'total_seconds'):
                # Es timedelta
                total_seconds = int(prog['hora_fin'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                prog['hora_fin'] = f"{hours:02d}:{minutes:02d}"
            else:
                prog['hora_fin'] = str(prog['hora_fin'])
        if 'fecha' in prog and prog['fecha']:
            prog['fecha'] = prog['fecha'].isoformat()

    return jsonify(programaciones_filtradas)

@admin_bp.route('/api/programaciones', methods=['POST'])
def api_crear_programacion():
    """API para crear una nueva programación"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    id_servicio = data.get('id_servicio')
    id_horario = data.get('id_horario')
    estado = data.get('estado', 'Disponible')

    if not fecha or not hora_inicio or not hora_fin or not id_servicio or not id_horario:
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    resultado = Programacion.crear(fecha, hora_inicio, hora_fin, id_servicio, id_horario, estado)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Programación creada exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/programaciones/<int:id_programacion>', methods=['PUT'])
def api_actualizar_programacion(id_programacion):
    """API para actualizar una programación"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    id_servicio = data.get('id_servicio')
    id_horario = data.get('id_horario')
    estado = data.get('estado')

    resultado = Programacion.actualizar(id_programacion, fecha=fecha, hora_inicio=hora_inicio,
                                       hora_fin=hora_fin, id_servicio=id_servicio,
                                       id_horario=id_horario, estado=estado)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Programación actualizada exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/programaciones/<int:id_programacion>', methods=['GET'])
def api_obtener_programacion(id_programacion):
    """API para obtener una programación específica"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    programacion = Programacion.obtener_por_id(id_programacion)
    if programacion:
        # Convertir objetos datetime a strings para JSON serialization
        if 'hora_inicio' in programacion and programacion['hora_inicio']:
            if hasattr(programacion['hora_inicio'], 'total_seconds'):
                # Es timedelta
                total_seconds = int(programacion['hora_inicio'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                programacion['hora_inicio'] = f"{hours:02d}:{minutes:02d}"
            else:
                programacion['hora_inicio'] = str(programacion['hora_inicio'])
        if 'hora_fin' in programacion and programacion['hora_fin']:
            if hasattr(programacion['hora_fin'], 'total_seconds'):
                # Es timedelta
                total_seconds = int(programacion['hora_fin'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                programacion['hora_fin'] = f"{hours:02d}:{minutes:02d}"
            else:
                programacion['hora_fin'] = str(programacion['hora_fin'])
        if 'fecha' in programacion and programacion['fecha']:
            programacion['fecha'] = programacion['fecha'].isoformat()
        return jsonify(programacion)
    else:
        return jsonify({'error': 'Programación no encontrada'}), 404

@admin_bp.route('/api/programaciones/<int:id_programacion>', methods=['DELETE'])
def api_eliminar_programacion(id_programacion):
    """API para eliminar una programación"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    resultado = Programacion.eliminar(id_programacion)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Programación eliminada exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/horarios/empleados/<int:id_empleado>', methods=['GET'])
def api_obtener_horarios_por_empleado(id_empleado):
    """API para obtener horarios de un empleado específico"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    horarios = Horario.obtener_por_empleado(id_empleado)

    # Convertir objetos datetime a strings para JSON serialization
    for horario in horarios:
        if 'hora_inicio' in horario and horario['hora_inicio']:
            horario['hora_inicio'] = str(horario['hora_inicio'])
        if 'hora_fin' in horario and horario['hora_fin']:
            horario['hora_fin'] = str(horario['hora_fin'])
        if 'fecha' in horario and horario['fecha']:
            horario['fecha'] = horario['fecha'].isoformat()

    return jsonify(horarios)

# API Routes for Gestion Bloqueo Horarios

@admin_bp.route('/api/bloqueos', methods=['GET'])
def api_obtener_bloqueos():
    """API para obtener todos los bloqueos o filtrados por parámetros"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    # Obtener parámetros de consulta
    fecha = request.args.get('fecha', '')
    id_programacion = request.args.get('id_programacion', '')
    estado = request.args.get('estado', '')

    # Convertir a int si no están vacíos
    id_programacion_int = int(id_programacion) if id_programacion else None

    if fecha or id_programacion_int or estado:
        # Usar búsqueda con filtros
        bloqueos = BloqueoHorario.buscar_por_filtros(fecha=fecha, id_programacion=id_programacion_int, estado=estado)
    else:
        # Obtener todos los bloqueos
        bloqueos = BloqueoHorario.obtener_todos()

    # Convertir objetos datetime a strings para JSON serialization
    for bloqueo in bloqueos:
        if 'hora_inicio' in bloqueo and bloqueo['hora_inicio']:
            bloqueo['hora_inicio'] = str(bloqueo['hora_inicio'])
        if 'hora_fin' in bloqueo and bloqueo['hora_fin']:
            bloqueo['hora_fin'] = str(bloqueo['hora_fin'])
        if 'fecha' in bloqueo and bloqueo['fecha']:
            bloqueo['fecha'] = bloqueo['fecha'].isoformat()
        if 'fecha_programacion' in bloqueo and bloqueo['fecha_programacion']:
            bloqueo['fecha_programacion'] = bloqueo['fecha_programacion'].isoformat()
        if 'hora_inicio_programacion' in bloqueo and bloqueo['hora_inicio_programacion']:
            bloqueo['hora_inicio_programacion'] = str(bloqueo['hora_inicio_programacion'])
        if 'hora_fin_programacion' in bloqueo and bloqueo['hora_fin_programacion']:
            bloqueo['hora_fin_programacion'] = str(bloqueo['hora_fin_programacion'])

    return jsonify(bloqueos)

@admin_bp.route('/api/bloqueos', methods=['POST'])
def api_crear_bloqueo():
    """API para crear un nuevo bloqueo"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    motivo = data.get('motivo')
    estado = data.get('estado')
    id_programacion = data.get('id_programacion')

    if not fecha or not hora_inicio or not hora_fin or not motivo or not estado:
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    resultado = BloqueoHorario.crear(fecha, hora_inicio, hora_fin, motivo, estado, id_programacion)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Bloqueo creado exitosamente', 'id_bloqueo': resultado['id_bloqueo']})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/bloqueos/<int:id_bloqueo>', methods=['PUT'])
def api_actualizar_bloqueo(id_bloqueo):
    """API para actualizar un bloqueo"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    motivo = data.get('motivo')
    estado = data.get('estado')
    id_programacion = data.get('id_programacion')

    resultado = BloqueoHorario.actualizar(id_bloqueo, fecha=fecha, hora_inicio=hora_inicio,
                                         hora_fin=hora_fin, motivo=motivo, estado=estado,
                                         id_programacion=id_programacion)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Bloqueo actualizado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500

@admin_bp.route('/api/bloqueos/<int:id_bloqueo>', methods=['GET'])
def api_obtener_bloqueo(id_bloqueo):
    """API para obtener un bloqueo específico"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    bloqueo = BloqueoHorario.obtener_por_id(id_bloqueo)
    if bloqueo:
        # Convertir objetos datetime a strings para JSON serialization
        if 'hora_inicio' in bloqueo and bloqueo['hora_inicio']:
            bloqueo['hora_inicio'] = str(bloqueo['hora_inicio'])
        if 'hora_fin' in bloqueo and bloqueo['hora_fin']:
            bloqueo['hora_fin'] = str(bloqueo['hora_fin'])
        if 'fecha' in bloqueo and bloqueo['fecha']:
            bloqueo['fecha'] = bloqueo['fecha'].isoformat()
        if 'fecha_programacion' in bloqueo and bloqueo['fecha_programacion']:
            bloqueo['fecha_programacion'] = bloqueo['fecha_programacion'].isoformat()
        if 'hora_inicio_programacion' in bloqueo and bloqueo['hora_inicio_programacion']:
            bloqueo['hora_inicio_programacion'] = str(bloqueo['hora_inicio_programacion'])
        if 'hora_fin_programacion' in bloqueo and bloqueo['hora_fin_programacion']:
            bloqueo['hora_fin_programacion'] = str(bloqueo['hora_fin_programacion'])
        return jsonify(bloqueo)
    else:
        return jsonify({'error': 'Bloqueo no encontrado'}), 404

@admin_bp.route('/api/bloqueos/<int:id_bloqueo>', methods=['DELETE'])
def api_eliminar_bloqueo(id_bloqueo):
    """API para eliminar un bloqueo"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    resultado = BloqueoHorario.eliminar(id_bloqueo)
    if 'success' in resultado:
        return jsonify({'success': True, 'message': 'Bloqueo eliminado exitosamente'})
    else:
        return jsonify({'success': False, 'message': resultado.get('error', 'Error desconocido')}), 500
