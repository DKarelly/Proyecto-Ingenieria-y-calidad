from flask import Flask, render_template, session, redirect, url_for
from routes.usuarios import usuarios_bp
from routes.cuentas import cuentas_bp
from routes.admin import admin_bp
from routes.reservas import reservas_bp
from routes.notificaciones import notificaciones_bp
from routes.reportes import reportes_bp
from routes.seguridad import seguridad_bp

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura_aqui_12345'  # Cambia esto por una clave segura

# Registrar blueprints
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(cuentas_bp, url_prefix='/cuentas')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(reservas_bp, url_prefix='/reservas')
app.register_blueprint(notificaciones_bp, url_prefix='/notificaciones')
app.register_blueprint(reportes_bp, url_prefix='/reportes')
app.register_blueprint(seguridad_bp, url_prefix='/seguridad')

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/admin/panel")
def admin_panel():
    """Panel de administración - Solo para empleados con rol administrador"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    # Verificar que sea administrador (opcional, dependiendo de tus roles)
    # if session.get('rol') != 'Administrador':
    #     return redirect(url_for('home'))
    
    return render_template('panel.html')

@app.route("/logout")
def logout():
    """Cerrar sesión y limpiar datos"""
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
