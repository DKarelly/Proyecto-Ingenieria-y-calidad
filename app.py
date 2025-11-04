from flask import Flask, render_template, session, redirect, url_for, g, request
from models.usuario import Usuario
from routes.usuarios import usuarios_bp
from routes.cuentas import cuentas_bp
from routes.admin import admin_bp
from routes.reservas import reservas_bp
from routes.notificaciones import notificaciones_bp
from routes.reportes import reportes_bp
from routes.seguridad import seguridad_bp
from routes.farmacia import farmacia_bp
from routes.paciente import paciente_bp
from routes.trabajador import trabajador_bp

import os
from dotenv import load_dotenv
#noaseaeaeaeass
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
app.register_blueprint(farmacia_bp, url_prefix='/farmacia')
app.register_blueprint(paciente_bp, url_prefix='/paciente')
app.register_blueprint(trabajador_bp, url_prefix='/trabajador')

@app.route("/")
def home():
    return render_template('home.html')

# Cargar información del usuario completo en `g.user` antes de cada petición
@app.before_request
def load_logged_in_user():
    user_id = session.get('usuario_id')
    if user_id is None:
        g.user = None
    else:
        try:
            # Obtener el usuario completo desde el modelo
            g.user = Usuario.obtener_por_id(user_id)
        except Exception:
            # En caso de error (DB, etc.) no romper la app; dejar sin usuario
            g.user = None


def is_auth():
    return g.get('user') is not None


@app.context_processor
def inject_globals():
    # Inyecta is_auth y user en todas las plantillas.
    # También inyectamos `usuario` por compatibilidad con templates existentes.
    return {
        'is_auth': is_auth(),
        'user': g.get('user'),
        'usuario': g.get('user')
    }

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
