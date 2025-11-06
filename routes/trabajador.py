from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

trabajador_bp = Blueprint('trabajador', __name__)

# Decorador para verificar que sea trabajador (empleado con rol != 1)
def trabajador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si hay sesión activa
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Verificar que sea empleado
        if session.get('tipo_usuario') != 'empleado':
            return redirect(url_for('home'))
        
        # Verificar que no sea Administrador (id_rol != 1)
        id_rol = session.get('id_rol')
        if id_rol == 1:
            return redirect(url_for('admin_panel'))
        
        # Verificar que tenga un rol válido (2, 3, 4, 5)
        if id_rol is None or id_rol not in [2, 3, 4, 5]:
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function

@trabajador_bp.route('/cuentas')
@trabajador_required
def cuentas():
    """Módulo de cuentas para trabajadores"""
    return render_template('panel_trabajador.html', subsistema='cuentas')

@trabajador_bp.route('/administracion')
@trabajador_required
def administracion():
    """Módulo de administración para trabajadores"""
    return render_template('panel_trabajador.html', subsistema='administracion')

@trabajador_bp.route('/incidencias')
@trabajador_required
def incidencias():
    """Módulo de incidencias para trabajadores"""
    return render_template('panel_trabajador.html', subsistema='incidencias')

@trabajador_bp.route('/reportes')
@trabajador_required
def reportes():
    """Módulo de reportes para trabajadores"""
    return render_template('panel_trabajador.html', subsistema='reportes')

@trabajador_bp.route('/cancelaciones')
@trabajador_required
def cancelaciones():
    """Gestión de solicitudes de cancelación de reservas"""
    return render_template('GestionarSolicitudesCancelacion.html')
