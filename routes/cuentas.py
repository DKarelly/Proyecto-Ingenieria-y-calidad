from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from models.empleado import Empleado
from models.usuario import Usuario
from models.paciente import Paciente

cuentas_bp = Blueprint('cuentas', __name__)

@cuentas_bp.route('/')
def panel():
    """Panel de Cuentas y Autenticación - Redirige al dashboard principal"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    # Redirigir al dashboard principal con subsistema cuentas
    return redirect(url_for('admin_panel', subsistema='cuentas'))

@cuentas_bp.route('/consultar-lista-usuarios')
def consultar_lista_usuarios():
    """Consultar Lista de Usuarios"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Obtener todos los usuarios del sistema
    import bd
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Consulta para obtener usuarios (tanto empleados como pacientes)
        query = """
            SELECT
                u.id_usuario as id,
                COALESCE(e.nombres, p.nombres) as nombre,
                COALESCE(e.apellidos, p.apellidos) as apellido,
                u.correo as email,
                COALESCE(e.fecha_nacimiento, p.fecha_nacimiento) as fecha_nacimiento,
                CASE
                    WHEN e.id_empleado IS NOT NULL THEN COALESCE(r.nombre, 'Empleado')
                    WHEN p.id_paciente IS NOT NULL THEN 'Paciente'
                    ELSE 'Usuario'
                END as rol,
                CASE
                    WHEN u.estado = 'Activo' THEN TRUE
                    ELSE FALSE
                END as activo
            FROM USUARIO u
            LEFT JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
            LEFT JOIN PACIENTE p ON u.id_usuario = p.id_usuario
            LEFT JOIN ROL r ON e.id_rol = r.id_rol
            ORDER BY u.id_usuario DESC
        """

        cursor.execute(query)
        resultados = cursor.fetchall()

        # Convertir resultados a lista de diccionarios
        usuarios = []
        for row in resultados:
            usuarios.append({
                'id': row['id'],
                'nombre': row['nombre'],
                'apellido': row['apellido'],
                'email': row['email'],
                'fecha_nacimiento': row['fecha_nacimiento'].strftime('%d/%m/%Y') if row.get('fecha_nacimiento') else 'N/A',
                'rol': row['rol'],
                'activo': row['activo']
            })

        cursor.close()
        conexion.close()

        return render_template('consultarlistadeUsuario.html', usuarios=usuarios)

    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        cursor.close()
        conexion.close()
        return render_template('consultarlistadeUsuario.html', usuarios=[])

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
            # Normalizar sexo: solo 'Masculino'/'Femenino'
            sexo_val = resultado.get('sexo')
            if sexo_val in (None, ''):
                sexo_paciente = 'No especificado'
            elif sexo_val == 'Masculino':
                sexo_paciente = 'Masculino'
            elif sexo_val == 'Femenino':
                sexo_paciente = 'Femenino'
            else:
                sexo_paciente = sexo_val

            usuario = {
                'tipo_usuario': 'paciente',
                'id_usuario': resultado['id_usuario'],
                'correo': resultado['correo'],
                'telefono': resultado['telefono'],
                'estado': resultado['estado'],
                'fecha_creacion': resultado['fecha_creacion'],
                'nombre_paciente': f"{resultado['nombres']} {resultado['apellidos']}",
                'documento_paciente': resultado['documento_identidad'],
                'sexo_paciente': sexo_paciente,
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
            # Normalizar sexo de empleado similar a pacientes
            sexo_val = resultado.get('sexo')
            if sexo_val in (None, ''):
                sexo_empleado = 'No especificado'
            elif sexo_val == 'Masculino':
                sexo_empleado = 'Masculino'
            elif sexo_val == 'Femenino':
                sexo_empleado = 'Femenino'
            else:
                sexo_empleado = sexo_val

            usuario = {
                'tipo_usuario': 'empleado',
                'id_usuario': resultado['id_usuario'],
                'correo': resultado['correo'],
                'telefono': resultado['telefono'],
                'estado': resultado['estado'],
                'fecha_creacion': resultado['fecha_creacion'],
                'nombre_empleado': f"{resultado['nombres']} {resultado['apellidos']}",
                'documento_empleado': resultado['documento_identidad'],
                'sexo_empleado': sexo_empleado,
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

@cuentas_bp.route('/ver-perfil-empleado/<int:id_empleado>')
def ver_perfil_empleado(id_empleado):
    """Ver Perfil de un Empleado específico"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    import bd
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()
    
    # Obtener información completa del empleado
    query = """
        SELECT 
            u.id_usuario,
            u.correo,
            u.telefono,
            u.estado,
            u.fecha_creacion,
            e.id_empleado,
            e.nombres,
            e.apellidos,
            e.documento_identidad,
            e.sexo,
            e.fecha_nacimiento,
            r.nombre as rol,
            esp.nombre as especialidad,
            d.nombre as distrito,
            prov.nombre as provincia,
            dep.nombre as departamento
        FROM EMPLEADO e
        INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
        LEFT JOIN ROL r ON e.id_rol = r.id_rol
        LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
        LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
        LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
        LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
        WHERE e.id_empleado = %s
    """
    cursor.execute(query, (id_empleado,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not resultado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('cuentas.gestionar_cuentas_internas'))
    
    # Normalizar sexo
    sexo_val = resultado.get('sexo')
    if sexo_val in (None, ''):
        sexo_empleado = 'No especificado'
    elif sexo_val.upper() == 'M' or sexo_val == 'Masculino':
        sexo_empleado = 'Masculino'
    elif sexo_val.upper() == 'F' or sexo_val == 'Femenino':
        sexo_empleado = 'Femenino'
    else:
        sexo_empleado = sexo_val

    usuario = {
        'tipo_usuario': 'empleado',
        'id_usuario': resultado['id_usuario'],
        'id_empleado': resultado['id_empleado'],
        'correo': resultado['correo'],
        'telefono': resultado['telefono'],
        'estado': resultado['estado'],
        'fecha_creacion': resultado['fecha_creacion'],
        'nombre_empleado': f"{resultado['nombres']} {resultado['apellidos']}",
        'documento_empleado': resultado['documento_identidad'],
        'sexo_empleado': sexo_empleado,
        'fecha_nacimiento': resultado.get('fecha_nacimiento'),
        'rol_empleado': resultado['rol'],
        'especialidad_empleado': resultado['especialidad'],
        'distrito': resultado['distrito'],
        'provincia': resultado['provincia'],
        'departamento': resultado['departamento'],
        'origen': 'gestion_usuarios'  # Indicar que viene de gestión de usuarios
    }
    
    return render_template('consultarperfil.html', usuario=usuario)

@cuentas_bp.route('/ver-perfil-paciente/<int:id_paciente>')
def ver_perfil_paciente(id_paciente):
    """Ver Perfil de un Paciente específico"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    import bd
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()
    
    # Obtener información completa del paciente
    query = """
        SELECT 
            u.id_usuario,
            u.correo,
            u.telefono,
            u.estado,
            u.fecha_creacion,
            p.id_paciente,
            p.nombres,
            p.apellidos,
            p.documento_identidad,
            p.sexo,
            p.fecha_nacimiento,
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
        flash('Paciente no encontrado', 'error')
        return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='pacientes'))
    
    # Normalizar sexo
    sexo_val = resultado.get('sexo')
    if sexo_val in (None, ''):
        sexo_paciente = 'No especificado'
    elif sexo_val.upper() == 'M' or sexo_val == 'Masculino':
        sexo_paciente = 'Masculino'
    elif sexo_val.upper() == 'F' or sexo_val == 'Femenino':
        sexo_paciente = 'Femenino'
    else:
        sexo_paciente = sexo_val

    # Normalizar estado (asegurar que sea 'activo' o 'inactivo' en minúsculas)
    estado_val = resultado.get('estado')
    if estado_val:
        # Convertir a string y luego a minúsculas
        estado_str = str(estado_val).strip().lower()
        # Verificar si es 'activo' (puede venir como 'Activo', 'ACTIVO', 'activo', etc.)
        if estado_str == 'Activo':
            estado_normalizado = 'activo'
        else:
            estado_normalizado = 'inactivo'
    else:
        estado_normalizado = 'inactivo'

    usuario = {
        'tipo_usuario': 'paciente',
        'id_usuario': resultado['id_usuario'],
        'id_paciente': resultado['id_paciente'],
        'correo': resultado['correo'],
        'telefono': resultado['telefono'],
        'estado': estado_normalizado,
        'fecha_creacion': resultado['fecha_creacion'],
        'nombre_paciente': f"{resultado['nombres']} {resultado['apellidos']}",
        'documento_paciente': resultado['documento_identidad'],
        'sexo_paciente': sexo_paciente,
        'fecha_nacimiento': resultado['fecha_nacimiento'],
        'distrito': resultado['distrito'],
        'provincia': resultado['provincia'],
        'departamento': resultado['departamento'],
        'origen': 'gestion_usuarios'  # Indicar que viene de gestión de usuarios
    }
    
    return render_template('consultarperfil.html', usuario=usuario)

@cuentas_bp.route('/registrar-cuenta-paciente', methods=['GET', 'POST'])
def registrar_cuenta_paciente():
    """Registrar Cuenta de Paciente"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombres = request.form.get('nombres', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            tipo_documento = request.form.get('tipo-documento', '').strip()
            documento = request.form.get('documento-identidad', '').strip()
            sexo = request.form.get('sexo', '').strip()
            telefono = request.form.get('telefono', '').strip()
            fecha_nacimiento = request.form.get('fecha-nacimiento', '').strip()
            email = request.form.get('email', '').strip()
            id_distrito = request.form.get('distrito', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm-password', '')
            
            # Verificar si es una petición AJAX
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json'
            
            # Validar campos requeridos
            if not all([nombres, apellidos, tipo_documento, documento, sexo, telefono, fecha_nacimiento, email, id_distrito, password]):
                if is_ajax:
                    return jsonify({
                        'success': False,
                        'error': 'Todos los campos marcados con (*) son obligatorios'
                    }), 400
                flash('Todos los campos marcados con (*) son obligatorios', 'error')
                return redirect(url_for('cuentas.registrar_cuenta_paciente'))
            
            def error_response(message):
                if is_ajax:
                    return jsonify({'success': False, 'error': message}), 400
                flash(message, 'error')
                return redirect(url_for('cuentas.registrar_cuenta_paciente'))
            
            # Validar tipo de documento
            tipos_validos = ['DNI', 'CE', 'PASAPORTE']
            if tipo_documento not in tipos_validos:
                return error_response('Tipo de documento inválido')
            
            # Validar documento según tipo
            if tipo_documento == 'DNI':
                if len(documento) != 8 or not documento.isdigit():
                    return error_response('El DNI debe tener exactamente 8 dígitos')
            elif tipo_documento == 'CE':
                if len(documento) < 9 or len(documento) > 12 or not documento.isdigit():
                    return error_response('El Carnet de Extranjería debe tener entre 9 y 12 dígitos')
            elif tipo_documento == 'PASAPORTE':
                if len(documento) < 6 or len(documento) > 15:
                    return error_response('El Pasaporte debe tener entre 6 y 15 caracteres')
                if not documento.replace(' ', '').replace('-', '').isalnum():
                    return error_response('El Pasaporte solo puede contener letras y números')
            
            # Validar teléfono (9 dígitos)
            if len(telefono) != 9 or not telefono.isdigit():
                return error_response('El teléfono debe tener exactamente 9 dígitos')
            
            # Validar contraseñas
            if password != confirm_password:
                return error_response('Las contraseñas no coinciden')
            
            if len(password) < 6:
                return error_response('La contraseña debe tener al menos 6 caracteres')
            
            # Verificar si el correo ya existe
            usuario_existente = Usuario.obtener_por_correo(email)
            if usuario_existente:
                return error_response('El correo electrónico ya está registrado')
            
            # Verificar si el documento ya existe
            from models.paciente import Paciente
            paciente_existente = Paciente.obtener_por_documento(documento)
            if paciente_existente:
                return error_response('El documento de identidad ya está registrado')
            
            # Crear usuario primero
            resultado_usuario = Usuario.crear_usuario(
                contrasena=password,
                correo=email,
                telefono=telefono
            )
            
            if 'error' in resultado_usuario:
                if is_ajax:
                    return jsonify({
                        'success': False,
                        'error': f'Error al crear usuario: {resultado_usuario["error"]}'
                    }), 400
                flash(f'Error al crear usuario: {resultado_usuario["error"]}', 'error')
                return redirect(url_for('cuentas.registrar_cuenta_paciente'))
            
            id_usuario = resultado_usuario['id_usuario']
            
            # Guardar sexo como palabra completa ('Masculino'/'Femenino')
            if sexo in ('Masculino', 'Femenino'):
                sexo_db = sexo
            else:
                # En caso de valores inesperados, normalizar por primera letra
                sexo_db = 'Masculino' if sexo and sexo.upper().startswith('M') else 'Femenino'
            
            # Crear paciente
            resultado_paciente = Paciente.crear(
                nombres=nombres,
                apellidos=apellidos,
                documento_identidad=documento,
                sexo=sexo_db,
                fecha_nacimiento=fecha_nacimiento,
                id_usuario=id_usuario,
                id_distrito=int(id_distrito)
            )
            
            if 'error' in resultado_paciente:
                # Si falla, eliminar el usuario creado
                Usuario.eliminar(id_usuario)
                return jsonify({
                    'success': False,
                    'error': f'Error al crear paciente: {resultado_paciente["error"]}'
                }), 400
            
            return jsonify({
                'success': True,
                'message': f'Cuenta de paciente {nombres} {apellidos} creada exitosamente',
                'paciente': {
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'documento': documento
                }
            }), 200
            
        except Exception as e:
            # Verificar si es AJAX
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json'
            if is_ajax:
                return jsonify({
                    'success': False,
                    'error': f'Error al procesar la solicitud: {str(e)}'
                }), 500
            flash(f'Error al procesar la solicitud: {str(e)}', 'error')
            return redirect(url_for('cuentas.registrar_cuenta_paciente'))
    
    return render_template('crearcuentaPaciente.html')

@cuentas_bp.route('/gestionar-cuentas-internas', methods=['GET', 'POST'])
def gestionar_cuentas_internas():
    """Gestionar Cuentas Internas - Empleados y Pacientes con Tabs"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    # Obtener tab activo (por defecto: empleados)
    tab_activo = request.args.get('tab', 'empleados')

    # Si es POST, crear nuevo empleado
    if request.method == 'POST':
        # Función auxiliar para manejar errores
        def handle_error(error_msg):
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('cuentas.gestionar_cuentas_internas'))
        
        try:
            print('[DEBUG] ========== INICIO REGISTRO EMPLEADO ==========')
            
            # Detectar si es JSON o FormData
            if request.is_json:
                data = request.get_json()
                accion = data.get('accion')
                
                # Si es petición AJAX para crear empleado
                if accion == 'crear_empleado':
                    print('[DEBUG] Procesando petición JSON para crear empleado')
                    nombres = data.get('nombres', '').strip()
                    apellidos = data.get('apellidos', '').strip()
                    tipo_documento = data.get('tipo_documento', '').strip()
                    documento = data.get('documento_identidad', '').strip()
                    telefono = data.get('telefono', '').strip()
                    email = data.get('correo', '').strip()
                    password = data.get('password', '')
                    id_rol = data.get('id_rol')
                    id_especialidad = data.get('id_especialidad')
                    sexo = data.get('sexo', '')
                    fecha_nacimiento = data.get('fecha_nacimiento', '').strip()
                    confirm_password = password  # En JSON ya se validó en frontend
                    
                    # Validar tipo de documento si viene
                    if tipo_documento:
                        tipos_validos = ['DNI', 'CE', 'PASAPORTE']
                        if tipo_documento not in tipos_validos:
                            return handle_error('Tipo de documento inválido')
                        
                        # Validar documento según tipo
                        if tipo_documento == 'DNI':
                            if len(documento) != 8 or not documento.isdigit():
                                return handle_error('El DNI debe tener exactamente 8 dígitos')
                        elif tipo_documento == 'CE':
                            if len(documento) < 9 or len(documento) > 12 or not documento.isdigit():
                                return handle_error('El Carnet de Extranjería debe tener entre 9 y 12 dígitos')
                        elif tipo_documento == 'PASAPORTE':
                            if len(documento) < 6 or len(documento) > 15:
                                return handle_error('El Pasaporte debe tener entre 6 y 15 caracteres')
                            if not documento.replace(' ', '').replace('-', '').isalnum():
                                return handle_error('El Pasaporte solo puede contener letras y números')
                else:
                    return jsonify({'success': False, 'error': 'Acción no reconocida'}), 400
            else:
                # FormData tradicional
                print('[DEBUG] Procesando FormData tradicional')
                nombres = request.form.get('nombres', '').strip()
                apellidos = request.form.get('apellidos', '').strip()
                tipo_documento = request.form.get('tipo-documento', '').strip()  # También puede venir por FormData
                documento = request.form.get('documento', '').strip()
                telefono = request.form.get('telefono', '').strip()
                email = request.form.get('email', '').strip()
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm-password', '')
                id_rol = request.form.get('rol')
                id_especialidad = request.form.get('especialidad')
                sexo = request.form.get('sexo', '')
                fecha_nacimiento = request.form.get('nacimiento', '').strip()
            
            print(f'[DEBUG] Datos recibidos: nombres={nombres}, apellidos={apellidos}, doc={documento}, email={email}, rol={id_rol}')

            # ===== VALIDACIONES BACKEND =====

            # Validar campos requeridos
            if not all([nombres, apellidos, documento, sexo, telefono, fecha_nacimiento, email, password, id_rol]):
                print('[DEBUG] ERROR: Falta algún campo requerido')
                error_msg = 'Todos los campos son obligatorios'
                if request.is_json:
                    return jsonify({'success': False, 'error': error_msg}), 400
                flash(error_msg, 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))

            # Validar longitud de nombres
            if len(nombres) < 2 or len(nombres) > 60:
                print(f'[DEBUG] ERROR: Nombres inválidos (longitud: {len(nombres)})')
                return handle_error('El nombre debe tener entre 2 y 60 caracteres')

            # Validar longitud de apellidos
            if len(apellidos) < 2 or len(apellidos) > 60:
                return handle_error('Los apellidos deben tener entre 2 y 60 caracteres')

            # Validar documento según tipo
            # Si no hay tipo_documento especificado, asumir DNI (compatibilidad)
            if not tipo_documento:
                if not documento.isdigit() or len(documento) != 8:
                    return handle_error('El documento debe contener exactamente 8 dígitos')
            # Si hay tipo_documento, ya se validó arriba en la sección JSON

            # Validar sexo
            if sexo not in ['Masculino', 'Femenino']:
                return handle_error('Debe seleccionar un sexo válido')

            # Validar teléfono (solo números, exactamente 9 dígitos)
            if not telefono.isdigit() or len(telefono) != 9:
                return handle_error('El teléfono debe contener exactamente 9 dígitos')

            # Validar email
            import re
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, email) or len(email) > 120:
                return handle_error('El formato del correo electrónico no es válido')

            # Validar contraseñas (solo si es FormData, en JSON ya se validó)
            if not request.is_json and password != confirm_password:
                return handle_error('Las contraseñas no coinciden')

            if len(password) < 8 or len(password) > 64:
                return handle_error('La contraseña debe tener entre 8 y 64 caracteres')

            # Validar que la contraseña tenga letras y números
            if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
                return handle_error('La contraseña debe incluir al menos una letra y un número')

            # Validar que la contraseña tenga al menos una mayúscula
            if not re.search(r'[A-Z]', password):
                return handle_error('La contraseña debe incluir al menos una letra mayúscula')

            # Validar fecha de nacimiento (mayor de 18 años)
            from datetime import datetime, timedelta
            try:
                fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                edad_minima = datetime.now() - timedelta(days=18*365.25)
                if fecha_nac > edad_minima:
                    return handle_error('El empleado debe ser mayor de 18 años')
            except ValueError:
                return handle_error('Fecha de nacimiento no válida')

            # Verificar si el correo ya existe
            from models.usuario import Usuario
            usuario_existente = Usuario.obtener_por_correo(email)
            if usuario_existente:
                print(f'[DEBUG] ERROR: Correo ya existe: {email}')
                return handle_error('El correo electrónico ya está registrado')

            # Verificar si el documento ya existe
            empleado_existente = Empleado.obtener_por_documento(documento)
            if empleado_existente:
                print(f'[DEBUG] ERROR: Documento ya existe: {documento}')
                return handle_error('El documento de identidad ya está registrado')

            print('[DEBUG] Validaciones pasadas, creando usuario...')
            # Crear usuario usando el método correcto
            resultado_usuario = Usuario.crear_usuario(
                contrasena=password,
                correo=email,
                telefono=telefono
            )

            print(f'[DEBUG] Resultado crear_usuario: {resultado_usuario}')
            
            if 'error' in resultado_usuario:
                print(f'[DEBUG] ERROR al crear usuario: {resultado_usuario["error"]}')
                return handle_error(f'Error al crear usuario: {resultado_usuario["error"]}')

            id_usuario = resultado_usuario['id_usuario']
            print(f'[DEBUG] Usuario creado con ID: {id_usuario}')

            # Obtener ubicación (distrito)
            # El formulario envía departamento/provincia/distrito; guardamos el id de distrito
            if request.is_json:
                id_distrito = data.get('id_distrito')
            else:
                id_distrito = request.form.get('distrito')
            try:
                id_distrito = int(id_distrito) if id_distrito not in (None, '', 'undefined') else None
            except (ValueError, TypeError):
                id_distrito = None

            # Obtener especialidad si el rol es médico
            if request.is_json:
                id_especialidad = data.get('id_especialidad')
            else:
                id_especialidad = request.form.get('especialidad')
            try:
                id_especialidad = int(id_especialidad) if id_especialidad not in (None, '', 'undefined') else None
            except (ValueError, TypeError):
                id_especialidad = None

            # Log para depuración (se puede eliminar en producción)
            print('[DEBUG] Registro empleado - datos recibidos:', {
                'nombres': nombres,
                'apellidos': apellidos,
                'documento': documento,
                'sexo': sexo,
                'telefono': telefono,
                'fecha_nacimiento': fecha_nacimiento,
                'email': email,
                'id_rol': id_rol,
                'id_distrito': id_distrito,
                'id_especialidad': id_especialidad
            })

            # Crear empleado
            print('[DEBUG] Llamando a Empleado.crear...')
            resultado_empleado = Empleado.crear(
                nombres=nombres,
                apellidos=apellidos,
                documento_identidad=documento,
                sexo=sexo,
                id_usuario=id_usuario,
                id_rol=int(id_rol) if id_rol not in (None, '', 'undefined') else None,
                id_distrito=id_distrito,
                id_especialidad=id_especialidad,
                fecha_nacimiento=fecha_nacimiento
            )
            
            print(f'[DEBUG] Resultado Empleado.crear: {resultado_empleado}')

            if 'error' in resultado_empleado:
                # Si falla, eliminar el usuario creado
                print(f'[DEBUG] ERROR al crear empleado: {resultado_empleado["error"]}, eliminando usuario {id_usuario}')
                Usuario.eliminar(id_usuario)
                error_msg = f'Error al crear empleado: {resultado_empleado["error"]}'
                
                if request.is_json:
                    return jsonify({'success': False, 'error': error_msg}), 400
                else:
                    flash(error_msg, 'error')
                    return redirect(url_for('cuentas.gestionar_cuentas_internas'))

            print(f'[DEBUG] ========== Empleado creado exitosamente con ID: {resultado_empleado.get("id_empleado")} ==========')
            
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                print('[DEBUG] Retornando respuesta JSON')
                response = jsonify({
                    'success': True, 
                    'message': 'Empleado registrado exitosamente',
                    'id_empleado': resultado_empleado.get("id_empleado")
                })
                response.headers['Content-Type'] = 'application/json'
                return response, 200
            else:
                flash('Empleado registrado exitosamente', 'success')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))

        except Exception as e:
            print(f'[DEBUG] ========== EXCEPCIÓN EN REGISTRO: {str(e)} ==========')
            import traceback
            traceback.print_exc()
            error_msg = f'Error al procesar la solicitud: {str(e)}'
            
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))
    
    # GET - Listar o buscar empleados y pacientes
    termino_busqueda = request.args.get('q', '').strip()
    
    # EMPLEADOS
    if termino_busqueda:
        empleados = Empleado.buscar(termino_busqueda)
    else:
        empleados = Empleado.obtener_todos()
    
    # PACIENTES
    from models.paciente import Paciente
    if termino_busqueda:
        pacientes = Paciente.buscar(termino_busqueda)
    else:
        pacientes = Paciente.obtener_todos()
    
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
                         pacientes=pacientes,
                         roles=roles,
                         termino_busqueda=termino_busqueda,
                         tab_activo=tab_activo)

@cuentas_bp.route('/api/empleados', methods=['GET'])
def api_obtener_empleados():
    """API para obtener empleados en formato JSON para paginación dinámica"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return jsonify([]), 401

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return jsonify([]), 401
    
    try:
        empleados = Empleado.obtener_todos()
        
        # Convertir a lista de diccionarios para JSON
        empleados_json = []
        for emp in empleados:
            # Usar estado_usuario si está disponible, sino estado del empleado, sino 'activo' por defecto
            estado_usuario = emp.get('estado_usuario') or emp.get('estado') or 'activo'
            empleados_json.append({
                'id_empleado': emp.get('id_empleado'),
                'nombres': emp.get('nombres'),
                'apellidos': emp.get('apellidos'),
                'documento_identidad': emp.get('documento_identidad'),
                'correo': emp.get('correo'),
                'telefono': emp.get('telefono'),
                'rol': emp.get('rol'),
                'estado': estado_usuario,
                'estado_usuario': estado_usuario  # Incluir explícitamente para el filtro
            })
        
        return jsonify(empleados_json)
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return jsonify([]), 500


@cuentas_bp.route('/api/pacientes', methods=['GET'])
def api_obtener_pacientes():
    """API para obtener pacientes en formato JSON para paginación dinámica"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return jsonify([]), 401

    # Verificar que sea empleado (solo empleados pueden ver pacientes)
    if session.get('tipo_usuario') != 'empleado':
        return jsonify([]), 401
    
    try:
        pacientes = Paciente.obtener_todos()
        
        # Convertir a lista de diccionarios para JSON
        pacientes_json = []
        for pac in pacientes:
            # Usar estado_usuario si está disponible, sino estado del paciente, sino 'activo' por defecto
            estado = pac.get('estado_usuario') or pac.get('estado') or 'activo'
            pacientes_json.append({
                'id_paciente': pac.get('id_paciente'),
                'nombres': pac.get('nombres'),
                'apellidos': pac.get('apellidos'),
                'documento_identidad': pac.get('documento_identidad'),
                'correo': pac.get('correo'),
                'telefono': pac.get('telefono'),
                'estado': estado,
                'estado_usuario': estado
            })
        
        return jsonify(pacientes_json)
    except Exception as e:
        print(f"Error al obtener pacientes: {e}")
        return jsonify([]), 500


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
            fecha_nacimiento = request.form.get('nacimiento', '').strip()
            id_distrito = request.form.get('distrito')  # Obtener distrito
            id_especialidad = request.form.get('especialidad')  # Obtener especialidad
            estado = request.form.get('estado', 'activo')  # Obtener estado

            # Validar campos requeridos
            if not all([nombres, apellidos, documento, telefono, email, id_rol]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('cuentas.editar_empleado', id_empleado=id_empleado))

            # Obtener empleado actual
            empleado = Empleado.obtener_por_id(id_empleado)
            if not empleado:
                flash('Empleado no encontrado', 'error')
                return redirect(url_for('cuentas.gestionar_cuentas_internas'))

            # Procesar id_distrito
            if id_distrito:
                try:
                    id_distrito = int(id_distrito)
                except (ValueError, TypeError):
                    id_distrito = None
            else:
                id_distrito = None

            # Procesar id_especialidad
            if id_especialidad:
                try:
                    id_especialidad = int(id_especialidad)
                except (ValueError, TypeError):
                    id_especialidad = None
            else:
                id_especialidad = None

            # Procesar fecha_nacimiento (si viene vacía dejar None)
            if fecha_nacimiento == '':
                fecha_nacimiento = None

            # Actualizar empleado
            resultado_empleado = Empleado.actualizar(
                id_empleado=id_empleado,
                nombres=nombres,
                apellidos=apellidos,
                documento_identidad=documento,
                sexo=sexo,
                estado=estado,
                id_rol=id_rol,
                id_distrito=id_distrito,
                id_especialidad=id_especialidad,  # Incluir especialidad en actualización
                fecha_nacimiento=fecha_nacimiento
            )

            if 'error' in resultado_empleado:
                flash(f'Error al actualizar empleado: {resultado_empleado["error"]}', 'error')
                return redirect(url_for('cuentas.editar_empleado', id_empleado=id_empleado))

            # Actualizar usuario (teléfono, correo y estado)
            from models.usuario import Usuario
            resultado_usuario = Usuario.actualizar(
                id_usuario=empleado['id_usuario'],
                correo=email,
                telefono=telefono,
                estado=estado
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
    
    # Asegurar que fecha_nacimiento venga en formato YYYY-MM-DD para el input[type=date]
    try:
        if empleado.get('fecha_nacimiento'):
            fn = empleado['fecha_nacimiento']
            # Si es date/datetime, formatear; si ya es string, dejarlo
            try:
                empleado['fecha_nacimiento'] = fn.strftime('%Y-%m-%d')
            except Exception:
                empleado['fecha_nacimiento'] = str(fn)
    except Exception:
        # ignorar si empleado no es un dict o no tiene la clave
        pass

    return render_template('editarEmpleado.html', 
                         empleado=empleado,
                         roles=roles,
                         departamentos=departamentos,
                         provincias=provincias,
                         distritos=distritos)

@cuentas_bp.route('/eliminar-empleado/<int:id_empleado>', methods=['GET', 'POST'])
def eliminar_empleado(id_empleado):
    """Eliminar (desactivar) un empleado"""
    # Verificar sesión
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        flash('No autorizado', 'error')
        return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='empleados'))
    
    try:
        resultado = Empleado.eliminar(id_empleado)
        
        if 'error' in resultado:
            flash(f'Error: {resultado["error"]}', 'error')
            return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='empleados'))
        
        flash('Empleado eliminado correctamente', 'success')
        return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='empleados'))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='empleados'))

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

# ==================== API ENDPOINTS PARA ROLES Y PERMISOS ====================

@cuentas_bp.route('/api/roles', methods=['GET'])
def api_obtener_roles():
    """API: Obtener todos los roles"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from models.rol import Rol
        roles = Rol.obtener_todos()
        return jsonify({'success': True, 'roles': roles})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cuentas_bp.route('/api/roles', methods=['POST'])
def api_crear_rol():
    """API: Crear un nuevo rol"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from models.rol import Rol
        data = request.get_json()
        
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not nombre:
            return jsonify({'success': False, 'message': 'El nombre del rol es obligatorio'}), 400
        
        id_rol = Rol.crear(nombre, descripcion)
        return jsonify({'success': True, 'message': 'Rol creado correctamente', 'id_rol': id_rol})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cuentas_bp.route('/api/roles/<int:id_rol>', methods=['PUT'])
def api_actualizar_rol(id_rol):
    """API: Actualizar un rol existente"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from models.rol import Rol
        data = request.get_json()
        
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        estado = data.get('estado', 'Activo')
        
        if not nombre:
            return jsonify({'success': False, 'message': 'El nombre del rol es obligatorio'}), 400
        
        actualizado = Rol.actualizar(id_rol, nombre, descripcion, estado)
        
        if actualizado:
            return jsonify({'success': True, 'message': 'Rol actualizado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Rol no encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cuentas_bp.route('/api/roles/<int:id_rol>', methods=['DELETE'])
def api_eliminar_rol(id_rol):
    """API: Eliminar un rol"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from models.rol import Rol
        exito, mensaje = Rol.eliminar(id_rol)
        
        if exito:
            return jsonify({'success': True, 'message': mensaje})
        else:
            return jsonify({'success': False, 'message': mensaje}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cuentas_bp.route('/api/permisos', methods=['GET'])
def api_obtener_permisos():
    """API: Obtener todos los permisos agrupados por módulo"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from models.rol import Permiso
        permisos = Permiso.obtener_por_modulo()
        return jsonify({'success': True, 'permisos': permisos})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cuentas_bp.route('/api/roles/<int:id_rol>/permisos', methods=['GET'])
def api_obtener_permisos_rol(id_rol):
    """API: Obtener permisos de un rol específico"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from models.rol import Permiso
        permisos_ids = Permiso.obtener_ids_por_rol(id_rol)
        return jsonify({'success': True, 'permisos_ids': permisos_ids})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cuentas_bp.route('/api/roles/<int:id_rol>/permisos', methods=['POST'])
def api_asignar_permisos_rol(id_rol):
    """API: Asignar permisos a un rol"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from models.rol import Rol
        data = request.get_json()
        permisos = data.get('permisos', [])
        
        Rol.asignar_permisos(id_rol, permisos)
        return jsonify({'success': True, 'message': 'Permisos asignados correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
            u.estado,
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
        'estado': resultado['estado'] or 'Activo',
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
        estado = request.form.get('estado', 'Activo')  # Obtener estado del formulario
        
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
            # Actualizar usuario (incluyendo estado)
            Usuario.actualizar(
                id_usuario=paciente['id_usuario'],
                correo=correo,
                telefono=telefono,
                estado=estado
            )
            flash('Paciente actualizado exitosamente', 'success')
        else:
            flash(f'Error al actualizar: {resultado["error"]}', 'danger')
        
        return redirect(url_for('cuentas.gestionar_datos_pacientes'))
    
    return render_template('editarPaciente.html', paciente=paciente)

@cuentas_bp.route('/eliminar-paciente/<int:id_paciente>', methods=['GET', 'POST'])
def eliminar_paciente(id_paciente):
    """Eliminar (desactivar) Paciente"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        flash('No autorizado', 'error')
        return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='pacientes'))
    
    from models.paciente import Paciente
    
    try:
        resultado = Paciente.eliminar(id_paciente)
        
        if 'error' in resultado:
            flash(f'Error: {resultado["error"]}', 'error')
            return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='pacientes'))
        
        flash('Paciente eliminado exitosamente', 'success')
        return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='pacientes'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('cuentas.gestionar_cuentas_internas', tab='pacientes'))

@cuentas_bp.route('/recuperar-contrasena')
def recuperar_contrasena():
    """Recuperar Contraseña"""
    return render_template('recuperarContraseña.html')

@cuentas_bp.route('/api/especialidades', methods=['GET'])
def api_obtener_especialidades():
    """API: Obtiene todas las especialidades activas"""
    from bd import obtener_conexion

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_especialidad, nombre FROM ESPECIALIDAD WHERE estado = 'Activo' ORDER BY nombre")
            especialidades = cursor.fetchall()
            return jsonify(especialidades)
    finally:
        conexion.close()

@cuentas_bp.route('/api/usuario/<int:usuario_id>', methods=['GET'])
def api_obtener_detalle_usuario(usuario_id):
    """API: Obtiene información detallada de un usuario específico"""
    # Verificar si hay sesión activa
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    # Verificar que sea empleado
    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 403

    import bd
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Consulta para obtener información completa del usuario
        query = """
            SELECT
                u.id_usuario,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_creacion,
                COALESCE(e.nombres, p.nombres) as nombres,
                COALESCE(e.apellidos, p.apellidos) as apellidos,
                COALESCE(e.documento_identidad, p.documento_identidad) as documento_identidad,
                COALESCE(e.sexo, p.sexo) as sexo,
                CASE
                    WHEN e.id_empleado IS NOT NULL THEN 'Empleado'
                    WHEN p.id_paciente IS NOT NULL THEN 'Paciente'
                    ELSE 'Usuario'
                END as tipo_usuario,
                r.nombre as rol,
                esp.nombre as especialidad,
                COALESCE(e.fecha_nacimiento, p.fecha_nacimiento) as fecha_nacimiento,
                d.nombre as distrito,
                prov.nombre as provincia,
                dep.nombre as departamento
            FROM USUARIO u
            LEFT JOIN EMPLEADO e ON u.id_usuario = e.id_usuario
            LEFT JOIN PACIENTE p ON u.id_usuario = p.id_usuario
            LEFT JOIN ROL r ON e.id_rol = r.id_rol
            LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
            LEFT JOIN DISTRITO d ON COALESCE(e.id_distrito, p.id_distrito) = d.id_distrito
            LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
            LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
            WHERE u.id_usuario = %s
        """

        cursor.execute(query, (usuario_id,))
        resultado = cursor.fetchone()

        if not resultado:
            cursor.close()
            conexion.close()
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Formatear la respuesta
        usuario = {
            'id_usuario': resultado['id_usuario'],
            'correo': resultado['correo'],
            'telefono': resultado['telefono'] or 'No especificado',
            'estado': resultado['estado'],
            'fecha_creacion': resultado['fecha_creacion'].strftime('%d/%m/%Y') if resultado['fecha_creacion'] else 'No disponible',
            'nombres': resultado['nombres'],
            'apellidos': resultado['apellidos'],
            'documento_identidad': resultado['documento_identidad'] or 'No especificado',
            # Normalizar valor de sexo para la API: solo 'Masculino'/'Femenino'
            'sexo': (
                'Masculino' if (resultado['sexo'] and resultado['sexo'] == 'Masculino')
                else 'Femenino' if (resultado['sexo'] and resultado['sexo'] == 'Femenino')
                else 'No especificado'
            ),
            'tipo_usuario': resultado['tipo_usuario'],
            'rol': resultado['rol'] or 'N/A',
            'especialidad': resultado['especialidad'] or 'N/A',
            'fecha_nacimiento': resultado['fecha_nacimiento'].strftime('%d/%m/%Y') if resultado['fecha_nacimiento'] else 'N/A',
            'distrito': resultado['distrito'] or 'No especificado',
            'provincia': resultado['provincia'] or 'No especificado',
            'departamento': resultado['departamento'] or 'No especificado'
        }

        cursor.close()
        conexion.close()

        return jsonify(usuario)

    except Exception as e:
        print(f"Error al obtener detalle de usuario: {e}")
        cursor.close()
        conexion.close()
        return jsonify({'error': 'Error al obtener información del usuario'}), 500

@cuentas_bp.route('/modificar-datos-cuenta', methods=['GET', 'POST'])
def modificar_datos_cuenta():
    """Modificar Datos de Cuenta del Usuario Logueado"""
    # Verificar sesión
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('home'))

    usuario_id = session.get('usuario_id')
    tipo_usuario = session.get('tipo_usuario')

    # Solo empleados pueden modificar sus datos desde esta ruta
    if tipo_usuario != 'empleado':
        flash('No tiene permisos para acceder a esta página', 'error')
        return redirect(url_for('home'))

    import bd

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombres = request.form.get('nombres', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            documento = request.form.get('documento', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            sexo = request.form.get('sexo', 'M')
            id_rol = request.form.get('rol')
            id_distrito = request.form.get('distrito')
            id_especialidad = request.form.get('especialidad')

            # Validar campos requeridos
            if not all([nombres, apellidos, documento, telefono, email, id_rol]):
                flash('Todos los campos marcados son requeridos', 'error')
                return redirect(url_for('cuentas.modificar_datos_cuenta'))

            # Obtener empleado actual
            empleado = Empleado.obtener_por_usuario(usuario_id)
            if not empleado:
                flash('Empleado no encontrado', 'error')
                return redirect(url_for('home'))

            # Verificar si el correo ya está en uso por otro usuario
            if email != empleado['correo']:
                usuario_existente = Usuario.obtener_por_correo(email)
                if usuario_existente and usuario_existente['id_usuario'] != usuario_id:
                    flash('El correo electrónico ya está registrado por otro usuario', 'error')
                    return redirect(url_for('cuentas.modificar_datos_cuenta'))

            # Verificar si el documento ya está en uso por otro empleado
            if documento != empleado['documento_identidad']:
                empleado_existente = Empleado.obtener_por_documento(documento)
                if empleado_existente and empleado_existente['id_empleado'] != empleado['id_empleado']:
                    flash('El documento de identidad ya está registrado por otro empleado', 'error')
                    return redirect(url_for('cuentas.modificar_datos_cuenta'))

            # Procesar id_distrito
            if id_distrito:
                try:
                    id_distrito = int(id_distrito)
                except (ValueError, TypeError):
                    id_distrito = None
            else:
                id_distrito = None

            # Procesar id_especialidad
            if id_especialidad:
                try:
                    id_especialidad = int(id_especialidad)
                except (ValueError, TypeError):
                    id_especialidad = None
            else:
                id_especialidad = None

            # Actualizar empleado
            resultado_empleado = Empleado.actualizar(
                id_empleado=empleado['id_empleado'],
                nombres=nombres,
                apellidos=apellidos,
                documento_identidad=documento,
                sexo=sexo,
                id_rol=id_rol,
                id_distrito=id_distrito,
                id_especialidad=id_especialidad
            )

            if 'error' in resultado_empleado:
                flash(f'Error al actualizar empleado: {resultado_empleado["error"]}', 'error')
                return redirect(url_for('cuentas.modificar_datos_cuenta'))

            # Actualizar usuario (correo y teléfono)
            params_usuario = {
                'id_usuario': usuario_id,
                'correo': email,
                'telefono': telefono
            }

            resultado_usuario = Usuario.actualizar(**params_usuario)

            if 'error' in resultado_usuario:
                flash(f'Error al actualizar datos de contacto: {resultado_usuario["error"]}', 'error')
                return redirect(url_for('cuentas.modificar_datos_cuenta'))

            flash('Datos actualizados exitosamente', 'success')
            return redirect(url_for('cuentas.modificar_datos_cuenta'))

        except Exception as e:
            flash(f'Error al procesar la solicitud: {str(e)}', 'error')
            return redirect(url_for('cuentas.modificar_datos_cuenta'))

    # GET - Cargar datos actuales del usuario
    conexion = bd.obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Obtener datos completos del empleado
        query = """
            SELECT
                e.id_empleado,
                e.nombres,
                e.apellidos,
                e.documento_identidad,
                e.sexo,
                e.id_rol,
                e.id_especialidad,
                e.id_distrito,
                u.correo,
                u.telefono,
                r.nombre as rol,
                esp.nombre as especialidad,
                d.nombre as distrito,
                d.id_distrito,
                prov.nombre as provincia,
                prov.id_provincia,
                dep.nombre as departamento,
                dep.id_departamento
            FROM EMPLEADO e
            INNER JOIN USUARIO u ON e.id_usuario = u.id_usuario
            LEFT JOIN ROL r ON e.id_rol = r.id_rol
            LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
            LEFT JOIN DISTRITO d ON e.id_distrito = d.id_distrito
            LEFT JOIN PROVINCIA prov ON d.id_provincia = prov.id_provincia
            LEFT JOIN DEPARTAMENTO dep ON prov.id_departamento = dep.id_departamento
            WHERE e.id_usuario = %s
        """
        cursor.execute(query, (usuario_id,))
        empleado = cursor.fetchone()

        if not empleado:
            flash('No se encontraron datos del empleado', 'error')
            cursor.close()
            conexion.close()
            return redirect(url_for('home'))

        # Obtener roles para el select
        cursor.execute("SELECT id_rol, nombre FROM ROL WHERE estado = 'activo' ORDER BY nombre")
        roles = cursor.fetchall()

        # Obtener departamentos
        cursor.execute("SELECT id_departamento, nombre FROM DEPARTAMENTO ORDER BY nombre")
        departamentos = cursor.fetchall()

        # Obtener provincias
        cursor.execute("SELECT id_provincia, nombre, id_departamento FROM PROVINCIA ORDER BY nombre")
        provincias = cursor.fetchall()

        # Obtener distritos
        cursor.execute("SELECT id_distrito, nombre, id_provincia FROM DISTRITO ORDER BY nombre")
        distritos = cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()

    return render_template('modificarDatosCuenta.html',
                         empleado=empleado,
                         roles=roles,
                         departamentos=departamentos,
                         provincias=provincias,
                         distritos=distritos)
