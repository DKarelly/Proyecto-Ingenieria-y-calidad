from flask import Flask, render_template, session, redirect, url_for
from routes.usuarios import usuarios_bp
from routes.cuentas import cuentas_bp
from routes.admin import admin_bp
from routes.reservas import reservas_bp
from routes.notificaciones import notificaciones_bp
from routes.reportes import reportes_bp
from routes.seguridad import seguridad_bp
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta_super_segura_aqui_12345')

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
    """Panel de administración - Solo para empleados con roles 1 a 5"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Verificar que el rol esté entre 1 y 5
    id_rol = session.get('id_rol')
    if id_rol is None or id_rol not in [1, 2, 3, 4, 5]:
        return redirect(url_for('home'))

    return render_template('panel.html')

@app.route("/perfil")
def perfil():
    """Página de perfil del usuario"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Importar el modelo Usuario para obtener datos
    from models.usuario import Usuario
    usuario = Usuario.obtener_por_id(session['usuario_id'])

    if not usuario:
        session.clear()
        return redirect(url_for('home'))

    return render_template('consultarperfil.html', usuario=usuario)

@app.route("/logout")
def logout():
    """Cerrar sesión y limpiar datos"""
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
