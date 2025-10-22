from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.usuario import Usuario
from functools import wraps

usuarios_bp = Blueprint('usuarios', __name__)

# Decorador para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar que sea empleado
def empleado_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tipo_usuario' not in session or session['tipo_usuario'] != 'empleado':
            flash('No tiene permisos para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.perfil'))
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if request.method == 'POST':
        correo = request.form.get('correo_electronico')
        contrasena = request.form.get('contrasena')
        
        if not correo or not contrasena:
            flash('Debe completar todos los campos', 'warning')
            return render_template('home.html')
        
        resultado = Usuario.login(correo, contrasena)
        
        if 'error' in resultado:
            flash(resultado['error'], 'danger')
            return render_template('home.html')
        
        # Guardar datos en sesión
        usuario = resultado['usuario']
        session['usuario_id'] = usuario['id_usuario']
        session['correo_electronico'] = usuario['correo_electronico']
        session['tipo_usuario'] = usuario['tipo_usuario']
        session['nombre_usuario'] = usuario['nombre']
        session['rol'] = usuario.get('rol')
        
        flash(f'Bienvenido {usuario["nombre"]}', 'success')
        return redirect(url_for('usuarios.perfil'))
    
    return render_template('home.html')

@usuarios_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('usuarios.login'))

@usuarios_bp.route('/perfil')
@login_required
def perfil():
    """Página de perfil del usuario"""
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    return render_template('consultarperfil.html', usuario=usuario)

@usuarios_bp.route('/listar')
@login_required
@empleado_required
def listar():
    """Lista todos los usuarios (solo para empleados)"""
    usuarios = Usuario.obtener_todos()
    return render_template('consultarlistadeUsuario.html', usuarios=usuarios)

@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@empleado_required
def crear():
    """Crea un nuevo usuario"""
    if request.method == 'POST':
        correo = request.form.get('correo_electronico')
        contrasena = request.form.get('contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        tipo_usuario = request.form.get('tipo_usuario')
        id_paciente = request.form.get('id_paciente')
        id_empleado = request.form.get('id_empleado')
        
        # Validaciones
        if not all([correo, contrasena, confirmar_contrasena, tipo_usuario]):
            flash('Debe completar todos los campos obligatorios', 'warning')
            return render_template('crearcuentaPaciente.html')
        
        if contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'warning')
            return render_template('crearcuentaPaciente.html')
        
        if len(contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'warning')
            return render_template('crearcuentaPaciente.html')
        
        # Crear usuario
        resultado = Usuario.crear_usuario(
            contrasena=contrasena,
            correo_electronico=correo,
            tipo_usuario=tipo_usuario,
            id_paciente=int(id_paciente) if id_paciente else None,
            id_empleado=int(id_empleado) if id_empleado else None
        )
        
        if 'error' in resultado:
            flash(f'Error al crear usuario: {resultado["error"]}', 'danger')
            return render_template('crearcuentaPaciente.html')
        
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('usuarios.listar'))
    
    return render_template('crearcuentaPaciente.html')

@usuarios_bp.route('/editar/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
@empleado_required
def editar(id_usuario):
    """Edita un usuario existente"""
    usuario = Usuario.obtener_por_id(id_usuario)
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios.listar'))
    
    if request.method == 'POST':
        correo = request.form.get('correo_electronico')
        estado = request.form.get('estado')
        nueva_contrasena = request.form.get('nueva_contrasena')
        
        resultado = Usuario.actualizar(
            id_usuario=id_usuario,
            correo_electronico=correo,
            estado=estado,
            contrasena=nueva_contrasena if nueva_contrasena else None
        )
        
        if 'error' in resultado:
            flash(f'Error al actualizar usuario: {resultado["error"]}', 'danger')
        else:
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.listar'))
    
    return render_template('modificarDatosCuenta.html', usuario=usuario)

@usuarios_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    """Permite al usuario cambiar su contraseña"""
    if request.method == 'POST':
        contrasena_actual = request.form.get('contrasena_actual')
        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        
        if not all([contrasena_actual, nueva_contrasena, confirmar_contrasena]):
            flash('Debe completar todos los campos', 'warning')
            return render_template('recuperarContraseña.html')
        
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas nuevas no coinciden', 'warning')
            return render_template('recuperarContraseña.html')
        
        # Verificar contraseña actual
        usuario = Usuario.obtener_por_id(session['usuario_id'])
        if not Usuario.verificar_contrasena(usuario['contrasena'], contrasena_actual):
            flash('Contraseña actual incorrecta', 'danger')
            return render_template('recuperarContraseña.html')
        
        # Actualizar contraseña
        resultado = Usuario.actualizar(
            id_usuario=session['usuario_id'],
            contrasena=nueva_contrasena
        )
        
        if 'error' in resultado:
            flash(f'Error al cambiar contraseña: {resultado["error"]}', 'danger')
        else:
            flash('Contraseña cambiada exitosamente', 'success')
            return redirect(url_for('usuarios.perfil'))
    
    return render_template('recuperarContraseña.html')

@usuarios_bp.route('/eliminar/<int:id_usuario>', methods=['POST'])
@login_required
@empleado_required
def eliminar(id_usuario):
    """Elimina (desactiva) un usuario"""
    resultado = Usuario.eliminar(id_usuario)
    
    if 'error' in resultado:
        flash(f'Error al eliminar usuario: {resultado["error"]}', 'danger')
    else:
        flash('Usuario desactivado exitosamente', 'success')
    
    return redirect(url_for('usuarios.listar'))

# API endpoints
@usuarios_bp.route('/api/login', methods=['POST'])
def api_login():
    """API: Login de usuario"""
    data = request.get_json()
    correo = data.get('correo_electronico')
    contrasena = data.get('contrasena')
    
    if not correo or not contrasena:
        return jsonify({'error': 'Debe completar todos los campos'}), 400
    
    resultado = Usuario.login(correo, contrasena)
    
    if 'error' in resultado:
        return jsonify({'error': resultado['error']}), 401
    
    # Guardar en sesión también
    usuario = resultado['usuario']
    session['usuario_id'] = usuario['id_usuario']
    session['correo_electronico'] = usuario['correo_electronico']
    session['tipo_usuario'] = usuario['tipo_usuario']
    session['nombre_usuario'] = usuario['nombre']
    session['rol'] = usuario.get('rol')
    
    return jsonify(resultado)

@usuarios_bp.route('/api/session', methods=['GET'])
def api_get_session():
    """API: Obtener información de la sesión actual"""
    if 'usuario_id' not in session:
        return jsonify({'logged_in': False})
    
    return jsonify({
        'logged_in': True,
        'usuario': {
            'id_usuario': session.get('usuario_id'),
            'nombre': session.get('nombre_usuario'),
            'correo_electronico': session.get('correo_electronico'),
            'tipo_usuario': session.get('tipo_usuario'),
            'rol': session.get('rol')
        }
    })

@usuarios_bp.route('/api/register', methods=['POST'])
def api_register():
    """API: Registrar nuevo paciente y crear su usuario"""
    from bd import obtener_conexion
    from werkzeug.security import generate_password_hash
    
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['nombres', 'apellidos', 'documento_identidad', 'correo', 'contrasena']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Obtener los IDs de ubicación
    id_departamento = data.get('id_departamento')
    id_provincia = data.get('id_provincia')
    id_distrito = data.get('id_distrito')
    
    if not all([id_departamento, id_provincia, id_distrito]):
        return jsonify({'error': 'Debe seleccionar departamento, provincia y distrito'}), 400
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el documento ya existe
            cursor.execute("SELECT id_paciente FROM PACIENTE WHERE documento_identidad = %s", 
                         (data['documento_identidad'],))
            if cursor.fetchone():
                return jsonify({'error': 'El documento de identidad ya está registrado'}), 400
            
            # Verificar si el correo ya existe
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo_electronico = %s", 
                         (data['correo'],))
            if cursor.fetchone():
                return jsonify({'error': 'El correo electrónico ya está registrado'}), 400
            
            # Insertar el paciente
            sql_paciente = """
                INSERT INTO PACIENTE (nombres, apellidos, documento_identidad, telefono, 
                                    correo, fecha_nacimiento, id_departamento, id_provincia, id_distrito)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_paciente, (
                data['nombres'],
                data['apellidos'],
                data['documento_identidad'],
                data.get('telefono'),
                data['correo'],
                data.get('fecha_nacimiento'),
                id_departamento,
                id_provincia,
                id_distrito
            ))
            
            id_paciente = cursor.lastrowid
            
            # Crear el usuario directamente aquí (sin llamar a otra función que abre otra conexión)
            contrasena_hash = generate_password_hash(data['contrasena'])
            sql_usuario = """
                INSERT INTO USUARIO (contrasena, correo_electronico, tipo_usuario, id_paciente)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (contrasena_hash, data['correo'], 'paciente', id_paciente))
            
            conexion.commit()
            return jsonify({'success': True, 'message': 'Registro exitoso'})
            
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': f'Error en el registro: {str(e)}'}), 500
    finally:
        conexion.close()

@usuarios_bp.route('/api/usuarios', methods=['GET'])
@login_required
@empleado_required
def api_obtener_usuarios():
    """API: Obtiene todos los usuarios"""
    usuarios = Usuario.obtener_todos()
    return jsonify(usuarios)

@usuarios_bp.route('/api/usuarios/<int:id_usuario>', methods=['GET'])
@login_required
def api_obtener_usuario(id_usuario):
    """API: Obtiene un usuario por ID"""
    # Solo empleados pueden ver otros usuarios
    if session['tipo_usuario'] != 'empleado' and session['usuario_id'] != id_usuario:
        return jsonify({'error': 'No autorizado'}), 403
    
    usuario = Usuario.obtener_por_id(id_usuario)
    if usuario:
        return jsonify(usuario)
    return jsonify({'error': 'Usuario no encontrado'}), 404

@usuarios_bp.route('/api/departamentos', methods=['GET'])
def api_obtener_departamentos():
    """API: Obtiene todos los departamentos"""
    from bd import obtener_conexion
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_departamento, nombre FROM DEPARTAMENTO ORDER BY nombre")
            departamentos = cursor.fetchall()
            return jsonify(departamentos)
    finally:
        conexion.close()

@usuarios_bp.route('/api/provincias/<int:id_departamento>', methods=['GET'])
def api_obtener_provincias(id_departamento):
    """API: Obtiene provincias por departamento"""
    from bd import obtener_conexion
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id_provincia, nombre FROM PROVINCIA WHERE id_departamento = %s ORDER BY nombre",
                (id_departamento,)
            )
            provincias = cursor.fetchall()
            return jsonify(provincias)
    finally:
        conexion.close()

@usuarios_bp.route('/api/distritos/<int:id_provincia>', methods=['GET'])
def api_obtener_distritos(id_provincia):
    """API: Obtiene distritos por provincia"""
    from bd import obtener_conexion
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id_distrito, nombre FROM DISTRITO WHERE id_provincia = %s ORDER BY nombre",
                (id_provincia,)
            )
            distritos = cursor.fetchall()
            return jsonify(distritos)
    finally:
        conexion.close()
