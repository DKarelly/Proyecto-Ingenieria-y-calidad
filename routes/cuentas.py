from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from werkzeug.security import generate_password_hash
from models.empleado import Empleado
from models.usuario import Usuario

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
    """Consultar Perfil del Usuario Logueado"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('home'))
    
    import bd
    from models.paciente import Paciente
    from models.empleado import Empleado
    
    usuario_id = session.get('usuario_id')
    tipo_usuario = session.get('tipo_usuario')
    
    # Obtener información del usuario
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()
    
    if tipo_usuario == 'paciente':
        # Consulta para paciente
        query = """
            SELECT 
                u.id_usuario,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_creacion,
                p.nombres,
                p.apellidos,
                p.documento_identidad,
                p.sexo,
                p.fecha_nacimiento,
                d.nombre as distrito,
                prov.nombre as provincia,
                dep.nombre as departamento
            FROM USUARIO u
            INNER JOIN PACIENTE p ON u.id_usuario = p.id_usuario
            LEFT JOIN DISTRITO d ON p.id_distrito = d.id_distrito
            LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
            LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
            WHERE u.id_usuario = %s
        """
        cursor.execute(query, (usuario_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            usuario = {
                'tipo_usuario': 'paciente',
                'id_usuario': resultado['id_usuario'],
                'correo': resultado['correo'],
                'telefono': resultado['telefono'],
                'estado': resultado['estado'],
                'fecha_creacion': resultado['fecha_creacion'],
                'nombre_paciente': f"{resultado['nombres']} {resultado['apellidos']}",
                'documento_paciente': resultado['documento_identidad'],
                'sexo_paciente': 'Masculino' if resultado['sexo'] == 'M' else 'Femenino',
                'fecha_nacimiento': resultado['fecha_nacimiento'],
                'distrito': resultado['distrito'],
                'provincia': resultado['provincia'],
                'departamento': resultado['departamento']
            }
        else:
            usuario = None
            
    else:  # empleado
        # Consulta para empleado
        query = """
            SELECT 
                u.id_usuario,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_creacion,
                e.nombres,
                e.apellidos,
                e.documento_identidad,
                e.sexo,
                r.nombre as rol,
                esp.nombre as especialidad,
                d.nombre as distrito,
                prov.nombre as provincia,
                dep.nombre as departamento
            FROM USUARIO u
            INNER JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
            LEFT JOIN ROL r ON e.id_rol = r.id_rol
            LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
            LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
            LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
            LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
            WHERE u.id_usuario = %s
        """
        cursor.execute(query, (usuario_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            usuario = {
                'tipo_usuario': 'empleado',
                'id_usuario': resultado['id_usuario'],
                'correo': resultado['correo'],
                'telefono': resultado['telefono'],
                'estado': resultado['estado'],
                'fecha_creacion': resultado['fecha_creacion'],
                'nombre_empleado': f"{resultado['nombres']} {resultado['apellidos']}",
                'documento_empleado': resultado['documento_identidad'],
                'sexo_empleado': 'Masculino' if resultado['sexo'] == 'M' else 'Femenino',
                'rol_empleado': resultado['rol'],
                'especialidad_empleado': resultado['especialidad'],
                'distrito': resultado['distrito'],
                'provincia': resultado['provincia'],
                'departamento': resultado['departamento']
            }
        else:
            usuario = None
    
    cursor.close()
    conexion.close()
    
    return render_template('consultarperfil.html', usuario=usuario)

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

@cuentas_bp.route('/gestionar-cuentas-internas', methods=['GET', 'POST'])
def gestionar_cuentas_internas():
    """Gestionar Cuentas Internas - Listar, Crear, Buscar Empleados"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    # Si es POST, crear nuevo empleado
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombres = request.form.get('nombres', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            documento = request.form.get('documento', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            id_rol = request.form.get('rol')
            sexo = request.form.get('sexo', 'M')  # Por defecto M
            
            # Validar campos requeridos
            if not all([nombres, apellidos, documento, telefono, email, password, id_rol]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
            # Verificar si el correo ya existe
            from models.usuario import Usuario
            usuario_existente = Usuario.obtener_por_correo(email)
            if usuario_existente:
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
            # Verificar si el documento ya existe
            empleado_existente = Empleado.obtener_por_documento(documento)
            if empleado_existente:
                flash('El documento de identidad ya está registrado', 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
            # Hashear la contraseña
            password_hash = generate_password_hash(password)
            
            # Crear usuario
            resultado_usuario = Usuario.crear(email, password_hash, telefono)
            
            if 'error' in resultado_usuario:
                flash(f'Error al crear usuario: {resultado_usuario["error"]}', 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
            id_usuario = resultado_usuario['id_usuario']
            
            # Obtener ubicación (distrito) - opcional
            id_distrito = None
            from bd import obtener_conexion
            distrito_nombre = request.form.get('distrito', '').strip()
            if distrito_nombre:
                conexion = obtener_conexion()
                try:
                    with conexion.cursor() as cursor:
                        cursor.execute("SELECT id_distrito FROM DISTRITO WHERE nombre LIKE %s LIMIT 1", 
                                     (f"%{distrito_nombre}%",))
                        distrito = cursor.fetchone()
                        if distrito:
                            id_distrito = distrito['id_distrito']
                finally:
                    conexion.close()
            
            # Crear empleado
            resultado_empleado = Empleado.crear(
                nombres=nombres,
                apellidos=apellidos,
                documento_identidad=documento,
                sexo=sexo,
                id_usuario=id_usuario,
                id_rol=id_rol,
                id_distrito=id_distrito,
                id_especialidad=None
            )
            
            if 'error' in resultado_empleado:
                # Si falla, eliminar el usuario creado
                Usuario.eliminar(id_usuario)
                flash(f'Error al crear empleado: {resultado_empleado["error"]}', 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
            flash('Empleado registrado exitosamente', 'success')
            return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
        except Exception as e:
            flash(f'Error al procesar la solicitud: {str(e)}', 'error')
            return redirect(url_for('cuentas.gestionar_cuentas_internas'))
    
    # GET - Listar o buscar empleados
    termino_busqueda = request.args.get('q', '').strip()
    
    if termino_busqueda:
        empleados = Empleado.buscar(termino_busqueda)
    else:
        empleados = Empleado.obtener_todos()
    
    # Obtener roles para el formulario
    from bd import obtener_conexion
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_rol, nombre FROM ROL WHERE estado = 'activo' ORDER BY nombre")
            roles = cursor.fetchall()
    finally:
        conexion.close()
    
    return render_template('gestionarCuentasInternas.html', 
                         empleados=empleados,
                         roles=roles,
                         termino_busqueda=termino_busqueda)

@cuentas_bp.route('/editar-empleado/<int:id_empleado>', methods=['GET', 'POST'])
def editar_empleado(id_empleado):
    """Editar un empleado existente"""
    # Verificar sesión
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombres = request.form.get('nombres', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            documento = request.form.get('documento', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            id_rol = request.form.get('rol')
            sexo = request.form.get('sexo', 'M')
            
            # Validar campos requeridos
            if not all([nombres, apellidos, documento, telefono, email, id_rol]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('cuentas.editar_empleado', id_empleado=id_empleado))
            
            # Obtener empleado actual
            empleado = Empleado.obtener_por_id(id_empleado)
            if not empleado:
                flash('Empleado no encontrado', 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
            # Actualizar empleado
            resultado_empleado = Empleado.actualizar(
                id_empleado=id_empleado,
                nombres=nombres,
                apellidos=apellidos,
                documento_identidad=documento,
                sexo=sexo,
                id_rol=id_rol
            )
            
            if 'error' in resultado_empleado:
                flash(f'Error al actualizar empleado: {resultado_empleado["error"]}', 'error')
                return redirect(url_for('cuentas.editar_empleado', id_empleado=id_empleado))
            
            # Actualizar usuario (teléfono y correo)
            from models.usuario import Usuario
            resultado_usuario = Usuario.actualizar(
                id_usuario=empleado['id_usuario'],
                correo=email,
                telefono=telefono
            )
            
            if 'error' in resultado_usuario:
                flash(f'Error al actualizar datos de contacto: {resultado_usuario["error"]}', 'error')
                return redirect(url_for('cuentas.editar_empleado', id_empleado=id_empleado))
            
            flash('Empleado actualizado exitosamente', 'success')
            return redirect(url_for('cuentas.gestionar_cuentas_internas'))
            
        except Exception as e:
            flash(f'Error al procesar la solicitud: {str(e)}', 'error')
            return redirect(url_for('cuentas.editar_empleado', id_empleado=id_empleado))
    
    # GET - Mostrar formulario de edición
    empleado = Empleado.obtener_por_id(id_empleado)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('cuentas.gestionar_cuentas_internas'))
    
    # Obtener roles
    from bd import obtener_conexion
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_rol, nombre FROM ROL WHERE estado = 'activo' ORDER BY nombre")
            roles = cursor.fetchall()
            
            # Obtener departamentos, provincias, distritos
            cursor.execute("SELECT id_departamento, nombre FROM DEPARTAMENTO ORDER BY nombre")
            departamentos = cursor.fetchall()
            
            cursor.execute("SELECT id_provincia, nombre, id_departamento FROM PROVINCIA ORDER BY nombre")
            provincias = cursor.fetchall()
            
            cursor.execute("SELECT id_distrito, nombre, id_provincia FROM DISTRITO ORDER BY nombre")
            distritos = cursor.fetchall()
    finally:
        conexion.close()
    
    return render_template('editarEmpleado.html', 
                         empleado=empleado,
                         roles=roles,
                         departamentos=departamentos,
                         provincias=provincias,
                         distritos=distritos)

@cuentas_bp.route('/eliminar-empleado/<int:id_empleado>', methods=['POST'])
def eliminar_empleado(id_empleado):
    """Eliminar (desactivar) un empleado"""
    # Verificar sesión
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        resultado = Empleado.eliminar(id_empleado)
        
        if 'error' in resultado:
            return jsonify({'success': False, 'message': resultado['error']}), 400
        
        return jsonify({'success': True, 'message': 'Empleado eliminado correctamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
    
    # Obtener pacientes con búsqueda opcional
    from models.paciente import Paciente
    q = request.args.get('q', '')
    
    if q:
        pacientes = Paciente.buscar(q)
    else:
        pacientes = Paciente.obtener_todos()
    
    return render_template('gestiondeDatosPacientes.html', pacientes=pacientes, query=q)

@cuentas_bp.route('/editar-paciente/<int:id_paciente>', methods=['GET', 'POST'])
def editar_paciente(id_paciente):
    """Editar Paciente"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    from models.paciente import Paciente
    from models.usuario import Usuario
    import bd
    
    # Obtener datos completos del paciente con ubicación
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()
    
    query = """
        SELECT 
            p.id_paciente,
            p.id_usuario,
            p.nombres,
            p.apellidos,
            p.documento_identidad,
            p.sexo,
            p.fecha_nacimiento,
            u.correo,
            u.telefono,
            p.id_distrito,
            d.nombre as distrito,
            prov.nombre as provincia,
            dep.nombre as departamento
        FROM PACIENTE p
        INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
        LEFT JOIN DISTRITO d ON p.id_distrito = d.id_distrito
        LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
        LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
        WHERE p.id_paciente = %s
    """
    
    cursor.execute(query, (id_paciente,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not resultado:
        flash('Paciente no encontrado', 'danger')
        return redirect(url_for('cuentas.gestionar_datos_pacientes'))
    
    # resultado es un diccionario (DictCursor)
    paciente = {
        'id_paciente': resultado['id_paciente'],
        'id_usuario': resultado['id_usuario'],
        'nombres': resultado['nombres'],
        'apellidos': resultado['apellidos'],
        'documento_identidad': resultado['documento_identidad'],
        'sexo': resultado['sexo'],
        'fecha_nacimiento': resultado['fecha_nacimiento'],
        'correo': resultado['correo'],
        'telefono': resultado['telefono'],
        'id_ubicacion': resultado['id_distrito'] or 0,
        'distrito': resultado['distrito'] or '',
        'provincia': resultado['provincia'] or '',
        'departamento': resultado['departamento'] or ''
    }
    
    if request.method == 'POST':
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        documento = request.form.get('documento_identidad')
        sexo = request.form.get('sexo')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        id_distrito = request.form.get('id_ubicacion')  # El formulario lo envía como id_ubicacion
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        
        # Actualizar paciente
        resultado = Paciente.actualizar(
            id_paciente=id_paciente,
            nombres=nombres,
            apellidos=apellidos,
            documento_identidad=documento,
            sexo=sexo,
            fecha_nacimiento=fecha_nacimiento if fecha_nacimiento else None,
            id_distrito=int(id_distrito) if id_distrito else None
        )
        
        if 'error' not in resultado:
            # Actualizar usuario
            Usuario.actualizar(
                id_usuario=paciente['id_usuario'],
                correo=correo,
                telefono=telefono
            )
            flash('Paciente actualizado exitosamente', 'success')
        else:
            flash(f'Error al actualizar: {resultado["error"]}', 'danger')
        
        return redirect(url_for('cuentas.gestionar_datos_pacientes'))
    
    return render_template('editarPaciente.html', paciente=paciente)

@cuentas_bp.route('/eliminar-paciente/<int:id_paciente>', methods=['POST'])
def eliminar_paciente(id_paciente):
    """Eliminar (desactivar) Paciente"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 403
    
    from models.paciente import Paciente
    
    resultado = Paciente.eliminar(id_paciente)
    
    if 'error' in resultado:
        return jsonify({'error': resultado['error']}), 500
    
    return jsonify({'success': True, 'message': 'Paciente eliminado exitosamente'})

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
