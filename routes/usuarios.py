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
        
        # Redirigir según el tipo de usuario
        if usuario['tipo_usuario'] == 'empleado':
            # Si es empleado, verificar su rol
            id_rol = usuario.get('id_rol')
            if id_rol == 1:  # Administrador
                return redirect(url_for('admin.panel'))
            else:  # Otros empleados (médico, recepcionista, farmacéutico, laboratorista)
                return redirect(url_for('trabajador.panel'))
        else:  # Paciente
            return redirect(url_for('usuarios.perfil'))
    
    return render_template('home.html')

@usuarios_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('usuarios.login'))

@usuarios_bp.route('/recuperar-contrasena', methods=['GET'])
def recuperar_contrasena_vista():
    """Página para iniciar recuperación de contraseña"""
    # Algunos sistemas de archivos tienen nombres con caracteres especiales
    # El template se llama recuperarContraseña.html
    try:
        return render_template('recuperarContraseña.html')
    except Exception:
        # Fallback por si el nombre del archivo difiere en acentos
        return render_template('recuperarContrasena.html')

@usuarios_bp.route('/perfil')
@login_required
def perfil():
    """Página de perfil del usuario - Versión Simple"""
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    return render_template('perfil.html', usuario=usuario)

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

@usuarios_bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Permite al usuario logueado editar SU propio perfil (correo, teléfono y contraseña)."""
    from datetime import datetime, timedelta
    
    id_usuario = session['usuario_id']
    usuario = Usuario.obtener_por_id(id_usuario)

    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios.perfil'))

    # Calcular fecha máxima permitida (18 años atrás)
    fecha_maxima = datetime.now() - timedelta(days=18*365.25)
    max_fecha = fecha_maxima.strftime('%Y-%m-%d')

    if request.method == 'POST':
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        id_distrito = request.form.get('id_distrito')

        # Actualizar datos básicos del usuario (correo, telefono)
        resultado = Usuario.actualizar(
            id_usuario=id_usuario,
            correo=correo if correo else None,
            telefono=telefono if telefono else None
        )

        if 'error' in resultado:
            flash(f'Error al actualizar perfil: {resultado["error"]}', 'danger')
            return render_template('editarPerfil.html', usuario=usuario)

        # Refrescar datos de sesión si cambió correo/telefono
        if correo:
            session['correo'] = correo
        if telefono:
            session['telefono'] = telefono

        # Actualizar nombres y ubicación según tipo de usuario
        try:
            sexo = request.form.get('sexo')
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            
            # Validar edad mínima (18 años) si se proporciona fecha de nacimiento
            if fecha_nacimiento:
                from datetime import datetime, timedelta
                fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                edad_minima = datetime.now() - timedelta(days=18*365.25)
                if fecha_nac > edad_minima:
                    flash('Debes ser mayor de 18 años', 'danger')
                    return render_template('editarPerfil.html', usuario=usuario)
            
            if usuario['tipo_usuario'] == 'paciente' and usuario.get('id_paciente'):
                from models.paciente import Paciente
                
                Paciente.actualizar(
                    id_paciente=usuario['id_paciente'],
                    nombres=nombres if nombres else None,
                    apellidos=apellidos if apellidos else None,
                    sexo=sexo if sexo else None,
                    fecha_nacimiento=fecha_nacimiento if fecha_nacimiento else None,
                    id_distrito=int(id_distrito) if id_distrito else None
                )
            elif usuario['tipo_usuario'] == 'empleado' and usuario.get('id_empleado'):
                from models.empleado import Empleado
                
                Empleado.actualizar(
                    id_empleado=usuario['id_empleado'],
                    nombres=nombres if nombres else None,
                    apellidos=apellidos if apellidos else None,
                    sexo=sexo if sexo else None,
                    fecha_nacimiento=fecha_nacimiento if fecha_nacimiento else None,
                    id_distrito=int(id_distrito) if id_distrito else None
                )
        except Exception as e:
            flash(f'Error al actualizar datos de perfil: {str(e)}', 'danger')
            return render_template('editarPerfil.html', usuario=usuario)

        # Actualizar nombre en sesión si se envió
        if nombres or apellidos:
            nombre_sesion = f"{nombres or ''} {apellidos or ''}".strip()
            if nombre_sesion:
                session['nombre_usuario'] = nombre_sesion

        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('usuarios.perfil'))

    return render_template('editarPerfil.html', usuario=usuario, max_fecha=max_fecha)

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

@usuarios_bp.route('/api/send-email', methods=['POST'])
def api_send_email():
    """API: Enviar email genérico"""
    import smtplib
    from email.message import EmailMessage
    import os

    data = request.get_json()
    to_email = data.get('to')
    subject = data.get('subject', 'Mensaje del Sistema Medico')
    body = data.get('body', '')

    if not to_email or not body:
        return jsonify({'error': 'Los campos "to" y "body" son requeridos'}), 400

    try:
        # Configuración SMTP - usar variables de entorno para mayor seguridad
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')

        if not sender_email or not sender_password:
            return jsonify({'error': 'Configuración SMTP no encontrada. Verifica las variables de entorno.'}), 500

        # Crear mensaje
        msg = EmailMessage()
        msg.set_charset('utf-8')
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)

        # Enviar email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg, sender_email, to_email)
        server.quit()

        return jsonify({'success': True, 'message': 'Email enviado exitosamente'})

    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de autenticación SMTP: {e}")
        return jsonify({'error': 'Error de autenticación. Verifica las credenciales SMTP.'}), 500
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': f'Error al enviar email: {str(e)}'}), 500

@usuarios_bp.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """API: Enviar código de recuperación de contraseña"""
    import random
    import string
    from bd import obtener_conexion

    data = request.get_json()
    correo = data.get('correo')

    if not correo:
        return jsonify({'error': 'El correo electrónico es requerido'}), 400

    # Verificar si el usuario existe
    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s AND estado = 'activo'", (correo,))
            usuario = cursor.fetchone()

            # Para evitar enumeración de correos, siempre respondemos éxito;
            # si el usuario no existe, no generamos código ni enviamos email.
            if not usuario:
                return jsonify({'success': True, 'message': 'Si el correo existe, se enviará un código de recuperación.'})

            # Generar código de recuperación
            codigo = ''.join(random.choices(string.digits, k=6))

            # Guardar código en la base de datos (crear tabla temporal si no existe)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS RECUPERACION_CONTRASENA (
                    id_recuperacion INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL,
                    codigo VARCHAR(6) NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usado BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
                )
            """)

            # Eliminar códigos anteriores para este usuario
            cursor.execute("DELETE FROM RECUPERACION_CONTRASENA WHERE id_usuario = %s", (usuario['id_usuario'],))

            # Insertar nuevo código
            cursor.execute("""
                INSERT INTO RECUPERACION_CONTRASENA (id_usuario, codigo)
                VALUES (%s, %s)
            """, (usuario['id_usuario'], codigo))

            conexion.commit()

            # MOSTRAR CÓDIGO EN CONSOLA PARA DESARROLLO
            print("="*60)
            print(f"CÓDIGO DE RECUPERACIÓN GENERADO")
            print(f"Email: {correo}")
            print(f"Código: {codigo}")
            print("="*60)

            # Enviar email usando la API de envío de emails
            email_data = {
                'to': correo,
                'subject': 'Codigo de recuperacion de contrasena - Sistema Medico',
                'body': f"""
Hola,

Has solicitado recuperar tu contrasena. Tu codigo de recuperacion es:

{codigo}

Este codigo expirara en 15 minutos.

Si no solicitaste este cambio, ignora este mensaje.

Atentamente,
Sistema de Gestion Medica
                """.strip()
            }

            # Hacer petición interna a la API de envío de emails
            from flask import current_app
            with current_app.test_client() as client:
                response = client.post('/usuarios/api/send-email',
                                     json=email_data,
                                     content_type='application/json')
                email_result = response.get_json()

                if email_result.get('success'):
                    return jsonify({'success': True, 'message': 'Código enviado exitosamente'})
                else:
                    # Si falla el envío, mostrar el código en consola para desarrollo
                    print(f"Código de recuperación para {correo}: {codigo}")
                    return jsonify({'success': True, 'message': 'Código generado (revisa la consola)'})

    except Exception as e:
        if conexion:
            try:
                conexion.rollback()
            except:
                pass
        print(f"Error en forgot-password: {str(e)}")
        return jsonify({'error': 'Error al procesar la solicitud de recuperación de contraseña'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass

@usuarios_bp.route('/api/verify-code', methods=['POST'])
def api_verify_code():
    """API: Verificar código de recuperación de contraseña"""
    from bd import obtener_conexion

    data = request.get_json()
    correo = data.get('correo')
    codigo = data.get('codigo')

    if not correo or not codigo:
        return jsonify({'error': 'Correo y código son requeridos'}), 400

    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Obtener usuario por correo
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s AND estado = 'activo'", (correo,))
            usuario = cursor.fetchone()
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404

            # Validar código no usado y con vigencia de 15 minutos
            cursor.execute(
                """
                SELECT id_recuperacion
                FROM RECUPERACION_CONTRASENA
                WHERE id_usuario = %s
                  AND codigo = %s
                  AND usado = FALSE
                  AND TIMESTAMPDIFF(MINUTE, fecha_creacion, NOW()) <= 15
                ORDER BY id_recuperacion DESC
                LIMIT 1
                """,
                (usuario['id_usuario'], codigo)
            )
            rec = cursor.fetchone()
            if not rec:
                return jsonify({'valid': False, 'error': 'Código inválido o expirado'}), 400

            return jsonify({'valid': True})
    except Exception as e:
        print(f"Error en verify-code: {str(e)}")
        return jsonify({'error': 'Error al verificar el código'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass

@usuarios_bp.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """API: Restablecer contraseña usando código de recuperación"""
    from bd import obtener_conexion

    data = request.get_json()
    correo = data.get('correo')
    codigo = data.get('codigo')
    nueva_contrasena = data.get('nueva_contrasena')

    if not correo or not codigo or not nueva_contrasena:
        return jsonify({'error': 'Correo, código y nueva contraseña son requeridos'}), 400

    if len(nueva_contrasena) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Obtener usuario por correo
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s AND estado = 'activo'", (correo,))
            usuario = cursor.fetchone()
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404

            # Validar código vigente y no usado
            cursor.execute(
                """
                SELECT id_recuperacion
                FROM RECUPERACION_CONTRASENA
                WHERE id_usuario = %s
                  AND codigo = %s
                  AND usado = FALSE
                  AND TIMESTAMPDIFF(MINUTE, fecha_creacion, NOW()) <= 15
                ORDER BY id_recuperacion DESC
                LIMIT 1
                """,
                (usuario['id_usuario'], codigo)
            )
            rec = cursor.fetchone()
            if not rec:
                return jsonify({'error': 'Código inválido o expirado'}), 400

            # Actualizar contraseña
            resultado = Usuario.actualizar(id_usuario=usuario['id_usuario'], contrasena=nueva_contrasena)
            if 'error' in resultado:
                return jsonify({'error': 'No se pudo actualizar la contraseña'}), 500

            # Marcar código como usado y limpiar otros códigos antiguos
            cursor.execute(
                "UPDATE RECUPERACION_CONTRASENA SET usado = TRUE WHERE id_recuperacion = %s",
                (rec['id_recuperacion'],)
            )
            cursor.execute(
                "DELETE FROM RECUPERACION_CONTRASENA WHERE id_usuario = %s AND usado = FALSE",
                (usuario['id_usuario'],)
            )
            conexion.commit()

            return jsonify({'success': True, 'message': 'Contraseña actualizada exitosamente'})
    except Exception as e:
        if conexion:
            try:
                conexion.rollback()
            except:
                pass
        print(f"Error en reset-password: {str(e)}")
        return jsonify({'error': 'Error al restablecer la contraseña'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@usuarios_bp.route('/medicos')
def lista_medicos():
    """Página que muestra todos los médicos (id_rol=2) organizados por especialidad"""
    import bd
    
    try:
        conexion = bd.obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener todas las especialidades activas
        cursor.execute("""
            SELECT id_especialidad, nombre, descripcion
            FROM ESPECIALIDAD
            WHERE estado = 'activo'
            ORDER BY nombre
        """)
        especialidades = cursor.fetchall()
        
        # Para cada especialidad, obtener sus médicos
        for especialidad in especialidades:
            cursor.execute("""
                SELECT 
                    e.id_empleado,
                    e.nombres,
                    e.apellidos,
                    e.documento_identidad,
                    e.sexo,
                    e.fotoPerfil,
                    e.id_especialidad
                FROM EMPLEADO e
                WHERE e.id_rol = 2 
                AND e.estado = 'Activo'
                AND e.id_especialidad = %s
                ORDER BY e.apellidos, e.nombres
            """, (especialidad['id_especialidad'],))
            
            especialidad['medicos'] = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return render_template('lista_medicos.html', especialidades=especialidades)
        
    except Exception as e:
        print(f"Error al cargar lista de médicos: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar la lista de médicos', 'danger')
        return redirect(url_for('home'))


@usuarios_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    """Cambiar contraseña del usuario logueado"""
    if request.method == 'POST':
        contrasena_actual = request.form.get('contrasena_actual')
        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        
        # Validaciones
        if not all([contrasena_actual, nueva_contrasena, confirmar_contrasena]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('cambiarContrasena.html')
        
        if nueva_contrasena != confirmar_contrasena:
            flash('La nueva contraseña y su confirmación no coinciden', 'error')
            return render_template('cambiarContrasena.html')
        
        if len(nueva_contrasena) < 8:
            flash('La nueva contraseña debe tener al menos 8 caracteres', 'error')
            return render_template('cambiarContrasena.html')
        
        # Validar que la nueva contraseña tenga mayúsculas, minúsculas y números
        import re
        if not re.search(r'[A-Z]', nueva_contrasena):
            flash('La nueva contraseña debe contener al menos una mayúscula', 'error')
            return render_template('cambiarContrasena.html')
        
        if not re.search(r'[a-z]', nueva_contrasena):
            flash('La nueva contraseña debe contener al menos una minúscula', 'error')
            return render_template('cambiarContrasena.html')
        
        if not re.search(r'\d', nueva_contrasena):
            flash('La nueva contraseña debe contener al menos un número', 'error')
            return render_template('cambiarContrasena.html')
        
        # Verificar contraseña actual
        usuario = Usuario.obtener_por_id(session['usuario_id'])
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('usuarios.logout'))
        
        from werkzeug.security import check_password_hash
        if not check_password_hash(usuario['contrasena'], contrasena_actual):
            flash('La contraseña actual es incorrecta', 'error')
            return render_template('cambiarContrasena.html')
        
        # Actualizar contraseña
        resultado = Usuario.actualizar(id_usuario=session['usuario_id'], contrasena=nueva_contrasena)
        
        if 'error' in resultado:
            flash('Error al cambiar la contraseña: ' + resultado['error'], 'error')
            return render_template('cambiarContrasena.html')
        
        flash('Contraseña cambiada exitosamente', 'success')
        return redirect(url_for('cuentas.consultar_perfil'))
    
    # GET
    return render_template('cambiarContrasena.html')
