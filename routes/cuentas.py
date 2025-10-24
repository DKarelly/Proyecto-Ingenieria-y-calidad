from flask import Blueprint, render_template, session, redirect, url_for

cuentas_bp = Blueprint('cuentas', __name__)

@cuentas_bp.route('/')
def panel():
    """Panel de Cuentas y Autenticación"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('panel.html', subsistema='cuentas')

@cuentas_bp.route('/consultar-lista-usuarios')
def consultar_lista_usuarios():
    """Consultar Lista de Usuarios"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('consultarlistadeUsuario.html')

@cuentas_bp.route('/consultar-perfil')
def consultar_perfil():
    """Consultar Perfil"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('consultarperfil.html')

@cuentas_bp.route('/registrar-cuenta-paciente')
def registrar_cuenta_paciente():
    """Registrar Cuenta de Paciente"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('crearcuentaPaciente.html')

@cuentas_bp.route('/gestionar-cuentas-internas')
def gestionar_cuentas_internas():
    """Gestionar Cuentas Internas"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestionarCuentasInternas.html')

@cuentas_bp.route('/gestionar-roles-permisos')
def gestionar_roles_permisos():
    """Gestión de Roles y Permisos"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestionarRolesPermisos.html')

@cuentas_bp.route('/gestionar-datos-pacientes')
def gestionar_datos_pacientes():
    """Gestión de Datos del Paciente"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('gestiondeDatosPacientes.html')

@cuentas_bp.route('/recuperar-contrasena')
def recuperar_contrasena():
    """Recuperar Contraseña"""
    return render_template('recuperarContraseña.html')

@cuentas_bp.route('/modificar-datos-cuenta')
@cuentas_bp.route('/modificar-datos-cuenta/<int:id_empleado>')
def modificar_datos_cuenta(id_empleado=None):
    """Modificar Datos de Cuenta"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return redirect('/usuarios/login')
    return render_template('modificarDatosCuenta.html')
