from flask import Flask, render_template, session, redirect, url_for, g, request
from models.usuario import Usuario
from routes.usuarios import usuarios_bp
from routes.cuentas import cuentas_bp
from routes.admin import admin_bp
from routes.trabajador import trabajador_bp
from routes.reservas import reservas_bp
from routes.notificaciones import notificaciones_bp
from routes.reportes import reportes_bp
from routes.seguridad import seguridad_bp
from routes.farmacia import farmacia_bp
from routes.paciente import paciente_bp

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
app.register_blueprint(trabajador_bp, url_prefix='/trabajador')
app.register_blueprint(reservas_bp, url_prefix='/reservas')
app.register_blueprint(notificaciones_bp, url_prefix='/notificaciones')
app.register_blueprint(reportes_bp, url_prefix='/reportes')
app.register_blueprint(seguridad_bp, url_prefix='/seguridad')
app.register_blueprint(farmacia_bp, url_prefix='/farmacia')
app.register_blueprint(paciente_bp, url_prefix='/paciente')


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/doctores")
def lista_doctores():
    """Página que muestra la lista de doctores agrupados por especialidad"""
    import bd
    from collections import defaultdict
    
    conexion = bd.obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Consultar todos los médicos (id_rol = 2) activos con sus especialidades
            sql = """
                SELECT 
                    e.id_empleado,
                    e.nombres,
                    e.apellidos,
                    e.documento_identidad,
                    e.fotoPerfil,
                    esp.nombre as especialidad,
                    u.telefono
                FROM EMPLEADO e
                INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE e.id_rol = 2 
                  AND e.estado = 'activo' 
                  AND u.estado = 'activo'
                ORDER BY esp.nombre, e.apellidos, e.nombres
            """
            cursor.execute(sql)
            doctores = cursor.fetchall()
            
            # Agrupar doctores por especialidad
            doctores_por_especialidad = defaultdict(list)
            for doctor in doctores:
                especialidad = doctor['especialidad'] or 'Medicina General'
                doctores_por_especialidad[especialidad].append(doctor)
            
            # Convertir defaultdict a dict normal para el template
            doctores_por_especialidad = dict(doctores_por_especialidad)
            
    finally:
        conexion.close()
    
    return render_template('lista_doctores.html', doctores_por_especialidad=doctores_por_especialidad)


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
    """Panel de administración - Solo para Administradores (id_rol=1)"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Verificar que el rol sea Administrador (id_rol=1)
    id_rol = session.get('id_rol')
    if id_rol != 1:
        # Si no es administrador pero es empleado, redirigir al panel de trabajador
        return redirect(url_for('trabajador_panel'))

    return render_template('panel.html')

@app.route("/trabajador/panel")
def trabajador_panel():
    """Panel de trabajador - Para empleados con roles diferentes a Administrador (id_rol != 1)"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Verificar que el rol NO sea Administrador (id_rol != 1)
    id_rol = session.get('id_rol')
    if id_rol == 1:
        # Si es administrador, redirigir al panel de admin
        return redirect(url_for('admin_panel'))

    # Verificar que tenga un rol válido (2, 3, 4, 5)
    if id_rol is None or id_rol not in [2, 3, 4, 5]:
        return redirect(url_for('home'))

    return render_template('panel_trabajador.html')

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
