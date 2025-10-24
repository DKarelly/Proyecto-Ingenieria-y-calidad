from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def panel():
    """Panel de Administración y Gestión"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('panel.html', subsistema='administracion')

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