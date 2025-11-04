from flask import Blueprint, render_template, session, redirect, url_for

farmacia_bp = Blueprint('farmacia', __name__, url_prefix='/farmacia')

@farmacia_bp.before_request
def check_session():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios.login'))
    if session.get('id_rol') not in [1, 4]:  # 1 = admin, 4 = farmacia
        return redirect(url_for('home'))

@farmacia_bp.route('/')
def farmacia():
    return render_template('panel.html', subsistema='farmacia')

@farmacia_bp.route('/gestionar-recepcion-medicamentos')
def gestionar_recepcion_medicamentos():
    return render_template('gestionarRecepcionMedicamentos.html')

@farmacia_bp.route('/gestionar-entrega-medicamentos')
def gestionar_entrega_medicamentos():
    return render_template('gestionarEntregaMedicamentos.html')
