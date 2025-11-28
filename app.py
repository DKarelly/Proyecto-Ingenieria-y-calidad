from flask import Flask, render_template, session, redirect, url_for, g, request, send_from_directory, flash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta_super_segura_aqui_12345')

# OPTIMIZACIÓN: Deshabilitar caché en desarrollo
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 if app.debug else 31536000

# OPTIMIZACIÓN: Servir archivos estáticos directamente sin pasar por before_request
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir archivos estáticos optimizados"""
    return send_from_directory('static', filename, max_age=0 if app.debug else 31536000)

# Ruta para favicon
@app.route('/favicon.ico')
def favicon():
    """Servir el favicon con transparencia"""
    response = send_from_directory('static/images', 'FaviconN.png', mimetype='image/png')
    # Headers para asegurar que el navegador respete la transparencia y actualice el caché
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Inicializar pool de conexiones al arrancar la aplicación
# Esto mejora el rendimiento al reutilizar conexiones
from bd import inicializar_pool
inicializar_pool()

# Ejecutar actualización automática de estados de reservas al iniciar
# Esto marca como Completadas o Inasistidas las citas que ya pasaron
try:
    from utils.actualizar_estados_reservas import ejecutar_actualizacion_completa
    ejecutar_actualizacion_completa()
except Exception as e:
    print(f"Advertencia: No se pudo ejecutar actualización de estados: {e}")

# Registrar blueprints con lazy loading - se importan solo cuando se necesitan
# Esto reduce el tiempo de inicio de la aplicación
def registrar_blueprints():
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
    from routes.medico import medico_bp
    from routes.recepcionista import recepcionista_bp

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
    app.register_blueprint(medico_bp, url_prefix='/medico')
    app.register_blueprint(recepcionista_bp)

# Registrar blueprints
registrar_blueprints()

@app.route("/")
def home():
    return render_template('home.html')

# Cargar información del usuario completo en `g.user` antes de cada petición
@app.before_request
def load_logged_in_user():
    # OPTIMIZACIÓN: No procesar archivos estáticos
    if request.path.startswith('/static/'):
        return
    
    user_id = session.get('usuario_id')
    if user_id is None:
        g.user = None
    else:
        try:
            # Lazy loading del modelo Usuario - se importa solo cuando es necesario
            from models.usuario import Usuario
            # Obtener el usuario completo desde el modelo
            g.user = Usuario.obtener_por_id(user_id)
        except Exception:
            # En caso de error (DB, etc.) no romper la app; dejar sin usuario
            g.user = None

# SEGURIDAD: Timeout de sesión diferenciado por rol
# Pacientes: 15 minutos de inactividad
# Otros roles: Sin restricción de timeout
@app.before_request
def check_patient_session_timeout():
    """
    Verifica el timeout de sesión para pacientes.
    Si un paciente está inactivo por más de 15 minutos, cierra su sesión automáticamente.
    Para otros roles (empleados, médicos, etc.), no aplica restricción.
    """
    # OPTIMIZACIÓN: No procesar archivos estáticos ni rutas de login/logout
    if request.path.startswith('/static/'):
        return
    
    # Excluir rutas de login y logout para evitar bucles de redirección
    if request.path in ['/usuarios/login', '/usuarios/logout', '/logout', '/']:
        return
    
    # Solo aplicar timeout a pacientes
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario != 'paciente':
        return  # No aplicar timeout a empleados, médicos, etc.
    
    # Verificar si hay timestamp de última actividad
    last_activity_str = session.get('last_activity')
    
    if last_activity_str is None:
        # Si no hay timestamp, inicializarlo (primera petición después del login)
        # Esto puede pasar si el usuario ya tenía sesión antes de implementar esta funcionalidad
        session['last_activity'] = datetime.now().isoformat()
        return
    
    try:
        # Convertir el timestamp string a datetime
        last_activity = datetime.fromisoformat(last_activity_str)
        now = datetime.now()
        
        # Calcular tiempo de inactividad
        inactivity_time = now - last_activity
        
        # Timeout: 15 minutos
        timeout_duration = timedelta(minutes=15)
        
        # Si el tiempo de inactividad supera el timeout, cerrar sesión
        if inactivity_time > timeout_duration:
            # Limpiar sesión
            session.clear()
            # Redirigir al login con mensaje
            flash('Su sesión ha expirado por seguridad. Por favor, inicie sesión nuevamente.', 'warning')
            return redirect(url_for('usuarios.login'))
        
        # Si está activo, actualizar el timestamp (Rolling Window)
        # Esto reinicia el contador de 15 minutos con cada petición
        session['last_activity'] = now.isoformat()
        
    except (ValueError, TypeError) as e:
        # Si hay error al parsear el timestamp, reinicializarlo
        # Esto es resistente a fallos como se solicitó
        session['last_activity'] = datetime.now().isoformat()


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
    """Panel de administración - Solo para administradores (rol 1)"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Verificar que el rol sea Administrador (rol 1)
    id_rol = session.get('id_rol')
    if id_rol != 1:
        # Si no es administrador, redirigir según su rol
        if id_rol == 2:  # Médico
            return redirect(url_for('medico.panel'))
        elif id_rol == 3:  # Recepcionista
            return redirect(url_for('recepcionista.panel'))
        elif id_rol == 4:  # Farmacéutico
            return redirect(url_for('farmacia.panel'))
        else:  # Otros empleados (incluyendo Laboratorista rol 5)
            return redirect(url_for('trabajador.panel'))

    # Leer el subsistema desde el querystring para resaltar la sección y mostrar su contenido
    subsistema = request.args.get('subsistema')
    # Panel único principal
    return render_template('panel.html', subsistema=subsistema)

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
    app.run(debug=True, threaded=True)
