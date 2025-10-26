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
        correo = request.form.get('correo')
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
        session['correo'] = usuario['correo']
        session['telefono'] = usuario['telefono']
        session['tipo_usuario'] = usuario['tipo_usuario']
        session['nombre_usuario'] = usuario['nombre']
        session['rol'] = usuario.get('rol')
        session['id_rol'] = usuario.get('id_rol')
        session['id_paciente'] = usuario.get('id_paciente')
        session['id_empleado'] = usuario.get('id_empleado')
        
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
    """Crea un nuevo usuario (paciente o empleado)"""
    if request.method == 'POST':
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        tipo_usuario = request.form.get('tipo_usuario')
        
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
        
        # Crear usuario primero
        resultado_usuario = Usuario.crear_usuario(
            contrasena=contrasena,
            correo=correo,
            telefono=telefono
        )
        
        if 'error' in resultado_usuario:
            flash(f'Error al crear usuario: {resultado_usuario["error"]}', 'danger')
            return render_template('crearcuentaPaciente.html')
        
        id_usuario = resultado_usuario['id_usuario']
        
        # Ahora crear el paciente o empleado
        if tipo_usuario == 'paciente':
            from models.paciente import Paciente
            nombres = request.form.get('nombres')
            apellidos = request.form.get('apellidos')
            documento = request.form.get('documento_identidad')
            sexo = request.form.get('sexo')
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            id_distrito = request.form.get('id_distrito')
            
            resultado = Paciente.crear(nombres, apellidos, documento, sexo, 
                                      fecha_nacimiento, id_usuario, id_distrito)
        else:  # empleado
            from models.empleado import Empleado
            nombres = request.form.get('nombres')
            apellidos = request.form.get('apellidos')
            documento = request.form.get('documento_identidad')
            sexo = request.form.get('sexo')
            id_rol = request.form.get('id_rol')
            id_distrito = request.form.get('id_distrito')
            id_especialidad = request.form.get('id_especialidad')
            
            resultado = Empleado.crear(nombres, apellidos, documento, sexo, 
                                      id_usuario, id_rol, id_distrito, id_especialidad)
        
        if 'error' in resultado:
            flash(f'Error al crear {tipo_usuario}: {resultado["error"]}', 'danger')
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
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        estado = request.form.get('estado')
        nueva_contrasena = request.form.get('nueva_contrasena')
        
        # Actualizar usuario
        resultado = Usuario.actualizar(
            id_usuario=id_usuario,
            correo=correo,
            telefono=telefono,
            estado=estado,
            contrasena=nueva_contrasena if nueva_contrasena else None
        )
        
        if 'error' in resultado:
            flash(f'Error al actualizar usuario: {resultado["error"]}', 'danger')
        else:
            # Actualizar paciente o empleado si corresponde
            if usuario['tipo_usuario'] == 'paciente':
                from models.paciente import Paciente
                nombres = request.form.get('nombres')
                apellidos = request.form.get('apellidos')
                documento = request.form.get('documento_identidad')
                sexo = request.form.get('sexo')
                fecha_nacimiento = request.form.get('fecha_nacimiento')
                id_distrito = request.form.get('id_distrito')
                
                Paciente.actualizar(usuario['id_paciente'], nombres, apellidos, 
                                   documento, sexo, fecha_nacimiento, id_distrito)
            elif usuario['tipo_usuario'] == 'empleado':
                from models.empleado import Empleado
                nombres = request.form.get('nombres')
                apellidos = request.form.get('apellidos')
                documento = request.form.get('documento_identidad')
                sexo = request.form.get('sexo')
                id_rol = request.form.get('id_rol')
                id_distrito = request.form.get('id_distrito')
                id_especialidad = request.form.get('id_especialidad')
                estado_empleado = request.form.get('estado_empleado')
                
                Empleado.actualizar(usuario['id_empleado'], nombres, apellidos, 
                                   documento, sexo, estado_empleado, id_rol, 
                                   id_distrito, id_especialidad)
            
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
    correo = data.get('correo')
    contrasena = data.get('contrasena')
    
    if not correo or not contrasena:
        return jsonify({'error': 'Debe completar todos los campos'}), 400
    
    resultado = Usuario.login(correo, contrasena)
    
    if 'error' in resultado:
        return jsonify({'error': resultado['error']}), 401
    
    # Guardar en sesión también
    usuario = resultado['usuario']
    session['usuario_id'] = usuario['id_usuario']
    session['correo'] = usuario['correo']
    session['telefono'] = usuario['telefono']
    session['tipo_usuario'] = usuario['tipo_usuario']
    session['nombre_usuario'] = usuario['nombre']
    session['rol'] = usuario.get('rol')
    session['id_rol'] = usuario.get('id_rol')
    session['id_paciente'] = usuario.get('id_paciente')
    session['id_empleado'] = usuario.get('id_empleado')
    
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
            'correo': session.get('correo'),
            'telefono': session.get('telefono'),
            'tipo_usuario': session.get('tipo_usuario'),
            'rol': session.get('rol'),
            'id_rol': session.get('id_rol'),
            'id_paciente': session.get('id_paciente'),
            'id_empleado': session.get('id_empleado')
        }
    })

@usuarios_bp.route('/api/register', methods=['POST'])
def api_register():
    """API: Registrar nuevo paciente y crear su usuario"""
    from models.paciente import Paciente
    from models.usuario import Usuario
    from bd import obtener_conexion
    from werkzeug.security import generate_password_hash
    from datetime import date
    
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['nombres', 'apellidos', 'documento_identidad', 'correo', 'contrasena']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Obtener el ID de distrito
    id_distrito = data.get('id_distrito')
    if not id_distrito:
        return jsonify({'error': 'Debe seleccionar un distrito'}), 400
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el documento ya existe
            cursor.execute("SELECT id_paciente FROM PACIENTE WHERE documento_identidad = %s", 
                         (data['documento_identidad'],))
            if cursor.fetchone():
                return jsonify({'error': 'El documento de identidad ya está registrado'}), 400
            
            # Verificar si el correo ya existe
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s", 
                         (data['correo'],))
            if cursor.fetchone():
                return jsonify({'error': 'El correo electrónico ya está registrado'}), 400
            
            # Crear el usuario primero
            contrasena_hash = generate_password_hash(data['contrasena'])
            
            sql_usuario = """
                INSERT INTO USUARIO (correo, contrasena, telefono, estado, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (
                data['correo'],
                contrasena_hash,
                data.get('telefono'),
                'activo',
                date.today()
            ))
            
            id_usuario = cursor.lastrowid
            
            # Crear el paciente
            sql_paciente = """
                INSERT INTO PACIENTE (nombres, apellidos, documento_identidad, sexo,
                                    fecha_nacimiento, id_usuario, id_distrito)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_paciente, (
                data['nombres'],
                data['apellidos'],
                data['documento_identidad'],
                data.get('sexo'),
                data.get('fecha_nacimiento'),
                id_usuario,
                id_distrito
            ))
            
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
