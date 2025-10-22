from flask import Blueprint, render_template, session, redirect, url_for

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/')
def panel():
    """Panel de Reportes"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('panel.html', subsistema='reportes')

@reportes_bp.route('/consultar-por-categoria')
def consultar_por_categoria():
    """Consultar Reportes por Categoría"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('consultar_por_categoria.html')