from flask import Blueprint, render_template, session, redirect, url_for

notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/')
def panel():
    """Panel de Notificaciones"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    # Redirigir al dashboard principal unificado
    return redirect(url_for('admin_panel', subsistema='notificaciones'))

@notificaciones_bp.route('/gestionar-confirmacion-reserva')
def gestionar_confirmacion_reserva():
    """Gestionar Confirmación de Reserva"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('GestionarConfirmacióndeCitas.html')

@notificaciones_bp.route('/gestionar-recordatorio-reserva')
def gestionar_recordatorio_reserva():
    """Gestionar Recordatorio Reserva"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('GestionarRecordatorios.html')
