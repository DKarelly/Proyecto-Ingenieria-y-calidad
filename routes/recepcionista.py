"""
Rutas para el módulo de recepcionista
Gestiona el panel recepcionista y sus funcionalidades
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from functools import wraps
from datetime import datetime, date
from bd import obtener_conexion
import pymysql.cursors

# Crear el Blueprint
recepcionista_bp = Blueprint('recepcionista', __name__, url_prefix='/recepcionista')

# Funciones auxiliares para obtener datos
def obtener_estadisticas_recepcionista():
    """
    Obtiene las estadísticas del recepcionista
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Estadísticas básicas del recepcionista
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM RESERVA WHERE DATE(fecha_registro) = CURDATE()) as reservas_hoy,
                (SELECT COUNT(*) FROM PACIENTE) as pacientes_totales,
                (SELECT COUNT(*) FROM INCIDENCIA WHERE estado = 'En progreso') as incidencias_pendientes
        """)

        result = cursor.fetchone()

        return {
            'reservas_hoy': result['reservas_hoy'] or 0,
            'pacientes_registrados': result['pacientes_totales'] or 0,
            'incidencias_pendientes': result['incidencias_pendientes'] or 0
        }

    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {
            'reservas_hoy': 0,
            'pacientes_registrados': 0,
            'incidencias_pendientes': 0
        }
    finally:
        if conexion:
            conexion.close()


def obtener_incidencias_recientes():
    """
    Obtiene las incidencias recientes para el dashboard
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                i.id_incidencia,
                i.descripcion,
                i.categoria,
                i.prioridad,
                i.estado,
                i.fecha_registro,
                i.id_paciente,
                CONCAT(p.nombres, ' ', p.apellidos) AS nombrepaciente
            FROM INCIDENCIA i
            LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
            ORDER BY fecha_registro DESC
            LIMIT 5;
        """)

        incidencias = cursor.fetchall()

        # Formatear fechas
        for incidencia in incidencias:
            if isinstance(incidencia['fecha_registro'], str):
                incidencia['fecha_registro'] = datetime.strptime(incidencia['fecha_registro'], '%Y-%m-%d %H:%M:%S')
            elif hasattr(incidencia['fecha_registro'], 'strftime'):
                pass  # Ya es datetime

        return incidencias

    except Exception as e:
        print(f"Error al obtener incidencias recientes: {e}")
        return []
    finally:
        if conexion:
            conexion.close()


def obtener_pacientes():
    """
    Obtiene la lista de pacientes para el recepcionista
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad as dni,
                p.sexo,
                u.telefono,
                u.correo as email
            FROM PACIENTE p
            INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
            WHERE u.estado = 'activo'
            ORDER BY p.apellidos, p.nombres
        """)

        pacientes = cursor.fetchall()
        return pacientes

    except Exception as e:
        print(f"Error al obtener pacientes: {e}")
        return []
    finally:
        if conexion:
            conexion.close()


def obtener_incidencias():
    """
    Obtiene todas las incidencias con información del paciente
    """
    conexion = None
    try:
        import pymysql.cursors
        conexion = obtener_conexion()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT
                i.id_incidencia,
                i.descripcion,
                i.categoria,
                i.prioridad,
                i.estado,
                DATE_FORMAT(i.fecha_registro, '%Y-%m-%d %H:%i:%s') as fecha_registro,
                DATE_FORMAT(i.fecha_resolucion, '%Y-%m-%d') as fecha_resolucion,
                i.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad as dni
            FROM INCIDENCIA i
            LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
            ORDER BY i.fecha_registro DESC
        """)

        incidencias = cursor.fetchall()

        # Formatear los datos para incluir nombre completo del paciente
        for incidencia in incidencias:
            if incidencia['nombres'] and incidencia['apellidos']:
                incidencia['paciente_nombre'] = f"{incidencia['nombres']} {incidencia['apellidos']}"
            else:
                incidencia['paciente_nombre'] = 'No asignado'

        return incidencias

    except Exception as e:
        print(f"Error al obtener incidencias: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conexion:
            conexion.close()


def obtener_reservas():
    """
    Obtiene todas las reservas con información del paciente y servicio
    """
    conexion = None
    try:
        import pymysql.cursors
        conexion = obtener_conexion()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.estado,
                r.fecha_registro,
                r.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad as dni,
                prog.fecha as fecha_reserva,
                prog.hora_inicio as hora_reserva,
                s.nombre as servicio_nombre,
                s.descripcion as servicio_descripcion,
                emp.nombres as medico_nombres,
                emp.apellidos as medico_apellidos,
                esp.nombre as especialidad
            FROM RESERVA r
            LEFT JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            LEFT JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
            LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
            LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
            ORDER BY prog.fecha DESC, prog.hora_inicio DESC
        """)

        reservas = cursor.fetchall()

        # Formatear los datos para incluir nombre completo del paciente y médico
        for reserva in reservas:
            if reserva['nombres'] and reserva['apellidos']:
                reserva['paciente_nombre'] = f"{reserva['nombres']} {reserva['apellidos']}"
            else:
                reserva['paciente_nombre'] = 'No asignado'

            if reserva['medico_nombres'] and reserva['medico_apellidos']:
                reserva['medico_nombre'] = f"Dr. {reserva['medico_nombres']} {reserva['medico_apellidos']}"
            else:
                reserva['medico_nombre'] = 'Médico no asignado'

            # Formatear fecha
            if reserva['fecha_reserva']:
                if isinstance(reserva['fecha_reserva'], str):
                    reserva['fecha_formateada'] = datetime.strptime(reserva['fecha_reserva'], '%Y-%m-%d').strftime('%d/%m/%Y')
                else:
                    reserva['fecha_formateada'] = reserva['fecha_reserva'].strftime('%d/%m/%Y')
                    reserva['fecha_reserva'] = reserva['fecha_reserva'].strftime('%Y-%m-%d')
            else:
                reserva['fecha_formateada'] = 'Fecha no disponible'

            # Formatear hora (convertir timedelta a string)
            if reserva['hora_reserva']:
                # Convertir timedelta a formato HH:MM:SS
                total_seconds = int(reserva['hora_reserva'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                reserva['hora_formateada'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                reserva['hora_reserva'] = reserva['hora_formateada']
            else:
                reserva['hora_formateada'] = 'Hora no disponible'
                reserva['hora_reserva'] = None

        return reservas

    except Exception as e:
        print(f"Error al obtener reservas: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conexion:
            conexion.close()


# Decorador para verificar que sea recepcionista
def recepcionista_required(f):
    """
    Decorador que verifica si el usuario está autenticado y tiene rol de recepcionista (id_rol = 3)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está autenticado
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('usuarios.login'))

        # Obtener id_rol de la sesión
        id_rol = session.get('id_rol')
        
        # Debug: imprimir información de la sesión
        print(f"🔍 [DEBUG recepcionista_required] id_rol en sesión: {id_rol}, tipo: {type(id_rol)}")
        print(f"🔍 [DEBUG recepcionista_required] usuario_id: {session.get('usuario_id')}")
        print(f"🔍 [DEBUG recepcionista_required] tipo_usuario: {session.get('tipo_usuario')}")
        print(f"🔍 [DEBUG recepcionista_required] rol: {session.get('rol')}")
        
        # Si no hay id_rol en sesión, intentar obtenerlo de la base de datos
        if id_rol is None:
            try:
                id_empleado = session.get('id_empleado')
                if id_empleado:
                    conexion = obtener_conexion()
                    cursor = conexion.cursor()
                    cursor.execute("SELECT id_rol FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
                    empleado = cursor.fetchone()
                    if empleado:
                        id_rol = empleado['id_rol']
                        session['id_rol'] = id_rol
                        print(f"🔍 [DEBUG recepcionista_required] id_rol obtenido de BD: {id_rol}")
                    conexion.close()
            except Exception as e:
                print(f"❌ [DEBUG recepcionista_required] Error obteniendo id_rol: {e}")

        # Verificar si el usuario es recepcionista (id_rol = 3)
        # Convertir a int para comparación segura
        id_rol_int = int(id_rol) if id_rol is not None else None
        if id_rol_int != 3:
            print(f"❌ [DEBUG recepcionista_required] Acceso denegado. id_rol: {id_rol_int}, esperado: 3")
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('home'))

        print(f"✅ [DEBUG recepcionista_required] Acceso permitido para recepcionista")
        return f(*args, **kwargs)
    return decorated_function


@recepcionista_bp.route('/')
@recepcionista_bp.route('/panel')
@recepcionista_required
def panel():
    """
    Panel principal del recepcionista
    """
    subsistema = request.args.get('subsistema')
    accion = request.args.get('accion')

    # Información del recepcionista desde la sesión
    # Usar session.nombre_usuario como valor inicial (se establece en login)
    nombre_usuario = session.get('nombre_usuario', 'Recepcionista')
    usuario = {
        'id': session.get('usuario_id'),
        'nombre': nombre_usuario,  # Valor inicial desde sesión
        'email': session.get('email_usuario'),
        'rol': session.get('rol', 'Recepcionista'),
        'id_empleado': session.get('id_empleado')
    }

    # Si tenemos id_empleado, obtener el nombre completo del empleado
    if usuario.get('id_empleado'):
        try:
            import pymysql.cursors
            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT CONCAT(COALESCE(nombres, ''), ' ', COALESCE(apellidos, '')) as nombre_completo
                FROM EMPLEADO
                WHERE id_empleado = %s
            """, (usuario['id_empleado'],))
            empleado = cursor.fetchone()
            if empleado and empleado['nombre_completo'] and empleado['nombre_completo'].strip() and empleado['nombre_completo'].strip() != '0':
                usuario['nombre'] = empleado['nombre_completo'].strip()
            # Si no se encuentra un nombre válido, ya tenemos el nombre_usuario de la sesión como respaldo
        except Exception as e:
            print(f"Error obteniendo nombre del empleado: {e}")
            # Si hay error, mantener el nombre_usuario de la sesión
        finally:
            if 'conexion' in locals():
                conexion.close()

    # Obtener estadísticas para el dashboard
    stats = obtener_estadisticas_recepcionista()

    # Obtener incidencias recientes para el dashboard si estamos en la vista principal
    if not subsistema:
        incidencias_recientes = obtener_incidencias_recientes()
    else:
        incidencias_recientes = []

    return render_template('panel_recepcionista.html',
                         subsistema=subsistema,
                         accion=accion,
                         usuario=usuario,
                         stats=stats,
                         incidencias_recientes=incidencias_recientes)


# API Endpoints para el dashboard
@recepcionista_bp.route('/dashboard/stats')
@recepcionista_required
def api_dashboard_stats():
    """
    API: Retorna estadísticas del dashboard del recepcionista
    """
    stats = obtener_estadisticas_recepcionista()
    return jsonify(stats)


@recepcionista_bp.route('/incidencias/recientes')
@recepcionista_required
def api_incidencias_recientes():
    """
    API: Retorna incidencias recientes para el dashboard
    """
    incidencias = obtener_incidencias_recientes()
    return jsonify(incidencias)


# Gestión de Pacientes
@recepcionista_bp.route('/pacientes/listar')
@recepcionista_required
def api_pacientes_listar():
    """
    API: Lista todos los pacientes
    """
    pacientes = obtener_pacientes()
    return jsonify(pacientes)


@recepcionista_bp.route('/pacientes/buscar')
@recepcionista_required
def api_pacientes_buscar():
    """
    API: Busca pacientes por nombre o DNI, devuelve datos completos para la tabla
    """
    try:
        query = request.args.get('q', '').strip()

        conexion = obtener_conexion()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # Si hay query, buscar pacientes filtrados; si no, devolver todos
        if query and len(query) >= 1:
            # Buscar pacientes que coincidan con el término de búsqueda
            # Optimizado: búsqueda más rápida usando índices si están disponibles
            cursor.execute("""
                SELECT
                    p.id_paciente,
                    p.nombres,
                    p.apellidos,
                    p.documento_identidad as dni,
                    u.telefono,
                    u.correo as email
                FROM PACIENTE p
                INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                WHERE u.estado = 'activo'
                AND (
                    p.nombres LIKE %s
                    OR p.apellidos LIKE %s
                    OR CONCAT(p.nombres, ' ', p.apellidos) LIKE %s
                    OR p.documento_identidad LIKE %s
                )
                ORDER BY p.apellidos, p.nombres
                LIMIT 100
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            # Si no hay query o es muy corta, devolver todos los pacientes
            cursor.execute("""
                SELECT
                    p.id_paciente,
                    p.nombres,
                    p.apellidos,
                    p.documento_identidad as dni,
                    u.telefono,
                    u.correo as email
                FROM PACIENTE p
                INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
                WHERE u.estado = 'activo'
                ORDER BY p.apellidos, p.nombres
                LIMIT 100
            """)

        pacientes = cursor.fetchall()

        # Asegurar que todos los valores None se conviertan a None (JSON null)
        # y que los campos estén presentes incluso si son None
        pacientes_formateados = []
        for paciente in pacientes:
            paciente_dict = {
                'id_paciente': paciente.get('id_paciente'),
                'nombres': paciente.get('nombres') or '',
                'apellidos': paciente.get('apellidos') or '',
                'dni': paciente.get('dni') or '',
                'telefono': paciente.get('telefono') or '',
                'email': paciente.get('email') or ''
            }
            pacientes_formateados.append(paciente_dict)

        return jsonify(pacientes_formateados)

    except Exception as e:
        print(f"Error al buscar pacientes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'conexion' in locals() and conexion:
            try:
                conexion.close()
            except Exception as e:
                print(f"Error cerrando conexión: {e}")


@recepcionista_bp.route('/pacientes/<int:id_paciente>')
@recepcionista_required
def api_paciente_detalles(id_paciente):
    """
    API: Obtiene detalles completos de un paciente por ID
    """
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad as dni,
                p.sexo,
                DATE_FORMAT(p.fecha_nacimiento, '%d/%m/%Y') as fecha_nacimiento,
                u.telefono,
                u.correo as email,
                d.nombre as departamento,
                pr.nombre as provincia,
                di.nombre as distrito
            FROM PACIENTE p
            INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
            LEFT JOIN DISTRITO di ON p.id_distrito = di.id_distrito
            LEFT JOIN PROVINCIA pr ON di.id_provincia = pr.id_provincia
            LEFT JOIN DEPARTAMENTO d ON pr.id_departamento = d.id_departamento
            WHERE p.id_paciente = %s AND u.estado = 'activo'
        """, (id_paciente,))

        paciente = cursor.fetchone()

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        return jsonify(paciente)

    except Exception as e:
        print(f"Error al obtener detalles del paciente: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'conexion' in locals() and conexion:
            conexion.close()


@recepcionista_bp.route('/pacientes/registrar', methods=['POST'])
@recepcionista_required
def api_pacientes_registrar():
    """
    API: Registra un nuevo paciente
    """
    try:
        # Obtener datos del formulario (usando los nombres correctos del formulario)
        nombres = request.form.get('nombres', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        tipo_documento = request.form.get('tipo-documento', '').strip()
        documento_identidad = request.form.get('documento-identidad', '').strip()
        sexo = request.form.get('sexo', '').strip()
        fecha_nacimiento = request.form.get('fecha-nacimiento', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        id_distrito = request.form.get('distrito', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm-password', '').strip()

        # Validaciones básicas - verificar que todos los campos requeridos estén presentes
        campos_requeridos = {
            'nombres': nombres,
            'apellidos': apellidos,
            'tipo-documento': tipo_documento,
            'documento-identidad': documento_identidad,
            'sexo': sexo,
            'fecha-nacimiento': fecha_nacimiento,
            'telefono': telefono,
            'email': email,
            'distrito': id_distrito,
            'password': password
        }

        # Verificar campos faltantes
        campos_faltantes = [campo for campo, valor in campos_requeridos.items() if not valor]
        if campos_faltantes:
            return jsonify({
                'success': False, 
                'message': f'Faltan campos requeridos: {", ".join(campos_faltantes)}'
            }), 400

        # Validar tipo de documento
        tipos_validos = ['DNI', 'CE', 'PASAPORTE']
        if tipo_documento not in tipos_validos:
            return jsonify({'success': False, 'message': 'Tipo de documento inválido'}), 400

        # Validar documento según tipo
        if tipo_documento == 'DNI':
            if len(documento_identidad) != 8 or not documento_identidad.isdigit():
                return jsonify({'success': False, 'message': 'El DNI debe tener exactamente 8 dígitos'}), 400
        elif tipo_documento == 'CE':
            if len(documento_identidad) < 9 or len(documento_identidad) > 12 or not documento_identidad.isdigit():
                return jsonify({'success': False, 'message': 'El Carnet de Extranjería debe tener entre 9 y 12 dígitos'}), 400
        elif tipo_documento == 'PASAPORTE':
            if len(documento_identidad) < 6 or len(documento_identidad) > 15:
                return jsonify({'success': False, 'message': 'El Pasaporte debe tener entre 6 y 15 caracteres'}), 400
            if not documento_identidad.replace(' ', '').replace('-', '').isalnum():
                return jsonify({'success': False, 'message': 'El Pasaporte solo puede contener letras y números'}), 400

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'}), 400

        # Validar longitud mínima de contraseña
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'La contraseña debe tener al menos 6 caracteres'}), 400

        # Validar que id_distrito sea un número válido
        try:
            id_distrito = int(id_distrito)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Distrito inválido'}), 400

        # VALIDACIONES DE UNICIDAD: Verificar que correo, teléfono y DNI no existan
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            
            # 1. Validar que el correo no exista
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s", (email,))
            if cursor.fetchone():
                conexion.close()
                return jsonify({'success': False, 'message': f'El correo electrónico {email} ya está registrado en el sistema'}), 400
            
            # 2. Validar que el teléfono no exista (si se proporciona)
            if telefono:
                cursor.execute("SELECT id_usuario FROM USUARIO WHERE telefono = %s AND telefono IS NOT NULL AND telefono != ''", (telefono,))
                if cursor.fetchone():
                    conexion.close()
                    return jsonify({'success': False, 'message': f'El teléfono {telefono} ya está registrado en el sistema'}), 400
            
            # 3. Validar que el DNI no exista (ni en PACIENTE ni en EMPLEADO)
            # Primero verificar en PACIENTE
            cursor.execute("SELECT id_paciente FROM PACIENTE WHERE documento_identidad = %s", (documento_identidad,))
            if cursor.fetchone():
                conexion.close()
                return jsonify({'success': False, 'message': f'El documento de identidad {documento_identidad} ya está registrado en el sistema'}), 400
            
            # También verificar en EMPLEADO
            from models.empleado import Empleado
            empleado_existente = Empleado.obtener_por_documento(documento_identidad)
            if empleado_existente:
                conexion.close()
                return jsonify({'success': False, 'message': f'El documento de identidad {documento_identidad} ya está registrado en el sistema'}), 400
            
            conexion.close()
        except Exception as e:
            if conexion:
                conexion.close()
            print(f"Error en validaciones de unicidad: {e}")
            return jsonify({'success': False, 'message': 'Error al validar datos únicos'}), 500

        # Importar modelos necesarios
        from models.paciente import Paciente
        from models.usuario import Usuario

        # Crear usuario primero con la contraseña proporcionada
        resultado_usuario = Usuario.crear_usuario(
            contrasena=password,
            correo=email,
            telefono=telefono
        )

        if 'error' in resultado_usuario:
            return jsonify({'success': False, 'message': resultado_usuario['error']}), 400

        id_usuario = resultado_usuario['id_usuario']

        # Convertir fecha de formato YYYY-MM-DD a formato necesario
        # La fecha viene en formato YYYY-MM-DD del input type="date"
        try:
            from datetime import datetime
            fecha_nacimiento_obj = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            fecha_nacimiento_formato = fecha_nacimiento_obj.strftime('%Y-%m-%d')
        except ValueError:
            # Si falla, intentar otros formatos comunes
            try:
                fecha_nacimiento_obj = datetime.strptime(fecha_nacimiento, '%d/%m/%Y')
                fecha_nacimiento_formato = fecha_nacimiento_obj.strftime('%Y-%m-%d')
            except ValueError:
                return jsonify({'success': False, 'message': 'Formato de fecha inválido'}), 400

        # Crear paciente
        resultado_paciente = Paciente.crear(
            nombres=nombres,
            apellidos=apellidos,
            documento_identidad=documento_identidad,
            sexo=sexo,
            fecha_nacimiento=fecha_nacimiento_formato,
            id_usuario=id_usuario,
            id_distrito=id_distrito
        )

        if 'error' in resultado_paciente:
            # Si falla la creación del paciente, eliminar el usuario creado
            try:
                Usuario.eliminar(id_usuario)
            except:
                pass
            return jsonify({'success': False, 'message': resultado_paciente['error']}), 400

        return jsonify({'success': True, 'message': 'Paciente registrado exitosamente'})

    except Exception as e:
        print(f"Error al registrar paciente: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


# Gestión de Incidencias
@recepcionista_bp.route('/incidencias/listar')
@recepcionista_required
def api_incidencias_listar():
    """
    API: Lista todas las incidencias, con filtro opcional por paciente
    """
    try:
        q = request.args.get('q', '').strip()
        id_paciente = request.args.get('id_paciente', '').strip()

        # Si hay búsqueda por texto, hacer consulta filtrada en SQL
        if q:
            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            cursor.execute("""
                SELECT
                    i.id_incidencia,
                    i.descripcion,
                    i.categoria,
                    i.prioridad,
                    i.estado,
                    DATE_FORMAT(i.fecha_registro, '%Y-%m-%d %H:%i:%s') as fecha_registro,
                    DATE_FORMAT(i.fecha_resolucion, '%Y-%m-%d') as fecha_resolucion,
                    i.id_paciente,
                    p.nombres,
                    p.apellidos,
                    p.documento_identidad as dni
                FROM INCIDENCIA i
                LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                WHERE CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, '')) LIKE %s
                   OR COALESCE(p.documento_identidad, '') LIKE %s
                ORDER BY i.fecha_registro DESC
            """, (f'%{q}%', f'%{q}%'))

            incidencias = cursor.fetchall()

            # Formatear los datos para incluir nombre completo del paciente
            for incidencia in incidencias:
                if incidencia['nombres'] and incidencia['apellidos']:
                    incidencia['paciente_nombre'] = f"{incidencia['nombres']} {incidencia['apellidos']}"
                else:
                    incidencia['paciente_nombre'] = 'No asignado'

            conexion.close()
        # Si hay filtro por ID de paciente específico
        elif id_paciente:
            try:
                id_paciente_int = int(id_paciente)
                if id_paciente_int <= 0:
                    raise ValueError('ID de paciente debe ser mayor a 0')
                    
                conexion = obtener_conexion()
                cursor = conexion.cursor(pymysql.cursors.DictCursor)

                cursor.execute("""
                    SELECT
                        i.id_incidencia,
                        i.descripcion,
                        i.categoria,
                        i.prioridad,
                        i.estado,
                        DATE_FORMAT(i.fecha_registro, '%Y-%m-%d %H:%i:%s') as fecha_registro,
                        DATE_FORMAT(i.fecha_resolucion, '%Y-%m-%d') as fecha_resolucion,
                        i.id_paciente,
                        p.nombres,
                        p.apellidos,
                        p.documento_identidad as dni
                    FROM INCIDENCIA i
                    LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
                    WHERE i.id_paciente = %s
                    ORDER BY i.fecha_registro DESC
                """, (id_paciente_int,))

                incidencias = cursor.fetchall()

                # Formatear los datos para incluir nombre completo del paciente
                for incidencia in incidencias:
                    if incidencia['nombres'] and incidencia['apellidos']:
                        incidencia['paciente_nombre'] = f"{incidencia['nombres']} {incidencia['apellidos']}"
                    else:
                        incidencia['paciente_nombre'] = 'No asignado'

                conexion.close()
            except (ValueError, TypeError) as e:
                print(f"Error al procesar ID de paciente: {e}")
                return jsonify({'error': 'ID de paciente inválido'}), 400
        # Si no hay filtros, obtener todas las incidencias
        else:
            incidencias = obtener_incidencias()

        return jsonify({'incidencias': incidencias})
    except Exception as e:
        print(f"Error al listar incidencias: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor al cargar incidencias'}), 500


@recepcionista_bp.route('/incidencias/generar', methods=['POST'])
@recepcionista_required
def api_incidencias_generar():
    """
    API: Genera una nueva incidencia con protección contra XSS y DDoS
    """
    try:
        tipo_incidencia = request.form.get('tipo_incidencia')
        descripcion = request.form.get('descripcion')
        prioridad = request.form.get('prioridad')
        id_paciente = request.form.get('id_paciente')  # Opcional

        # Validaciones básicas
        if not all([tipo_incidencia, descripcion, prioridad]):
            return jsonify({'success': False, 'message': 'Tipo de incidencia, descripción y prioridad son requeridos'}), 400

        # Obtener ID del empleado recepcionista para rate limiting
        id_empleado = session.get('id_empleado')
        if not id_empleado:
            return jsonify({'success': False, 'message': 'No se pudo identificar al empleado'}), 400
        
        # Usar IP + ID de empleado como identificador para rate limiting
        identificador = f"{request.remote_addr}_{id_empleado}"

        # Usar el modelo Incidencia para crear la incidencia (con sanitización y rate limiting)
        from models.incidencia import Incidencia
        resultado = Incidencia.crear(
            descripcion=descripcion, 
            id_paciente=id_paciente, 
            categoria=tipo_incidencia, 
            prioridad=prioridad,
            identificador_usuario=identificador
        )

        if resultado.get('rate_limited'):
            return jsonify({'success': False, 'message': resultado['message']}), 429  # Too Many Requests
        
        if resultado['success']:
            return jsonify({'success': True, 'message': 'Incidencia generada exitosamente'})
        else:
            return jsonify({'success': False, 'message': resultado['message']}), 500

    except Exception as e:
        print(f"Error al generar incidencia: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


# Gestión de Reservas
@recepcionista_bp.route('/reservas/listar')
@recepcionista_required
def api_reservas_listar():
    """
    API: Lista todas las reservas, con filtro opcional por paciente o estado
    """
    try:
        q = request.args.get('q', '').strip()
        estado = request.args.get('estado', '').strip()
        id_paciente = request.args.get('id_paciente', '').strip()

        # Si hay búsqueda por texto, hacer consulta filtrada en SQL
        if q:
            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            cursor.execute("""
                SELECT
                    r.id_reserva,
                    r.estado,
                    r.fecha_registro,
                    r.id_paciente,
                    p.nombres,
                    p.apellidos,
                    p.documento_identidad as dni,
                    prog.fecha as fecha_reserva,
                    prog.hora_inicio as hora_reserva,
                    s.nombre as servicio_nombre,
                    s.descripcion as servicio_descripcion,
                    emp.nombres as medico_nombres,
                    emp.apellidos as medico_apellidos,
                    esp.nombre as especialidad
                FROM RESERVA r
                LEFT JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                LEFT JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                WHERE CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, '')) LIKE %s
                   OR COALESCE(p.documento_identidad, '') LIKE %s
                   OR COALESCE(s.nombre, '') LIKE %s
                ORDER BY prog.fecha DESC, prog.hora_inicio DESC
            """, (f'%{q}%', f'%{q}%', f'%{q}%'))

            reservas = cursor.fetchall()
            conexion.close()
        # Si hay filtro por estado
        elif estado:
            estados_validos = ['pendiente', 'confirmada', 'cancelada', 'completada']
            if estado not in estados_validos:
                return jsonify({'error': 'Estado inválido'}), 400

            conexion = obtener_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            cursor.execute("""
                SELECT
                    r.id_reserva,
                    r.estado,
                    r.fecha_registro,
                    r.id_paciente,
                    p.nombres,
                    p.apellidos,
                    p.documento_identidad as dni,
                    prog.fecha as fecha_reserva,
                    prog.hora_inicio as hora_reserva,
                    s.nombre as servicio_nombre,
                    s.descripcion as servicio_descripcion,
                    emp.nombres as medico_nombres,
                    emp.apellidos as medico_apellidos,
                    esp.nombre as especialidad
                FROM RESERVA r
                LEFT JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                LEFT JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                WHERE r.estado = %s
                ORDER BY prog.fecha DESC, prog.hora_inicio DESC
            """, (estado,))

            reservas = cursor.fetchall()
            conexion.close()
        # Si hay filtro por ID de paciente específico
        elif id_paciente:
            try:
                id_paciente_int = int(id_paciente)
                if id_paciente_int <= 0:
                    raise ValueError('ID de paciente debe ser mayor a 0')

                conexion = obtener_conexion()
                cursor = conexion.cursor(pymysql.cursors.DictCursor)

                cursor.execute("""
                    SELECT
                        r.id_reserva,
                        r.estado,
                        r.fecha_registro,
                        r.id_paciente,
                        p.nombres,
                        p.apellidos,
                        p.documento_identidad as dni,
                        prog.fecha as fecha_reserva,
                        prog.hora_inicio as hora_reserva,
                        s.nombre as servicio_nombre,
                        s.descripcion as servicio_descripcion,
                        emp.nombres as medico_nombres,
                        emp.apellidos as medico_apellidos,
                        esp.nombre as especialidad
                    FROM RESERVA r
                    LEFT JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    LEFT JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                    WHERE r.id_paciente = %s
                    ORDER BY prog.fecha DESC, prog.hora_inicio DESC
                """, (id_paciente_int,))

                reservas = cursor.fetchall()
                conexion.close()
            except (ValueError, TypeError) as e:
                print(f"Error al procesar ID de paciente: {e}")
                return jsonify({'error': 'ID de paciente inválido'}), 400
        # Si no hay filtros, obtener todas las reservas
        else:
            reservas = obtener_reservas()

        # Formatear los datos para incluir nombre completo del paciente y médico
        for reserva in reservas:
            if reserva['nombres'] and reserva['apellidos']:
                reserva['paciente_nombre'] = f"{reserva['nombres']} {reserva['apellidos']}"
            else:
                reserva['paciente_nombre'] = 'No asignado'

            if reserva['medico_nombres'] and reserva['medico_apellidos']:
                reserva['medico_nombre'] = f"Dr. {reserva['medico_nombres']} {reserva['medico_apellidos']}"
            else:
                reserva['medico_nombre'] = 'Médico no asignado'

            # Formatear fecha
            if reserva['fecha_reserva']:
                if isinstance(reserva['fecha_reserva'], str):
                    reserva['fecha_formateada'] = datetime.strptime(reserva['fecha_reserva'], '%Y-%m-%d').strftime('%d/%m/%Y')
                else:
                    reserva['fecha_formateada'] = reserva['fecha_reserva'].strftime('%d/%m/%Y')
                    reserva['fecha_reserva'] = reserva['fecha_reserva'].strftime('%Y-%m-%d')
            else:
                reserva['fecha_formateada'] = 'Fecha no disponible'

            # Formatear hora (convertir timedelta a string)
            if reserva['hora_reserva']:
                # Si ya es string, no hacer nada
                if isinstance(reserva['hora_reserva'], str):
                    reserva['hora_formateada'] = reserva['hora_reserva']
                else:
                    # Convertir timedelta a formato HH:MM:SS
                    total_seconds = int(reserva['hora_reserva'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    reserva['hora_formateada'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    reserva['hora_reserva'] = reserva['hora_formateada']
            else:
                reserva['hora_formateada'] = 'Hora no disponible'
                reserva['hora_reserva'] = None

        return jsonify({'reservas': reservas})
    except Exception as e:
        print(f"Error al listar reservas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor al cargar reservas'}), 500


# API Endpoints para ubicaciones (departamentos, provincias, distritos)
@recepcionista_bp.route('/api/departamentos', methods=['GET'])
@recepcionista_required
def api_obtener_departamentos():
    """API: Obtiene todos los departamentos"""
    from bd import obtener_conexion
    import pymysql.cursors

    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT id_departamento, nombre FROM DEPARTAMENTO ORDER BY nombre")
            departamentos = cursor.fetchall()
            return jsonify(departamentos)
    finally:
        conexion.close()


@recepcionista_bp.route('/api/provincias/<int:id_departamento>', methods=['GET'])
@recepcionista_required
def api_obtener_provincias(id_departamento):
    """API: Obtiene provincias por departamento"""
    from bd import obtener_conexion
    import pymysql.cursors

    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT id_provincia, nombre FROM PROVINCIA WHERE id_departamento = %s ORDER BY nombre",
                (id_departamento,)
            )
            provincias = cursor.fetchall()
            return jsonify(provincias)
    finally:
        conexion.close()


@recepcionista_bp.route('/api/distritos/<int:id_provincia>', methods=['GET'])
@recepcionista_required
def api_obtener_distritos(id_provincia):
    """API: Obtiene distritos por provincia"""
    from bd import obtener_conexion
    import pymysql.cursors

    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT id_distrito, nombre FROM DISTRITO WHERE id_provincia = %s ORDER BY nombre",
                (id_provincia,)
            )
            distritos = cursor.fetchall()
            return jsonify(distritos)
    finally:
        conexion.close()


# API Endpoint de bienvenida con logging
@recepcionista_bp.route('/api/welcome', methods=['GET'])
@recepcionista_required
def api_welcome():
    """API: Endpoint de bienvenida que registra metadata de la solicitud"""
    # Log de metadata de la solicitud
    print(f"Request received: {request.method} {request.path}")

    # Retornar mensaje de bienvenida
    return jsonify({'message': 'Welcome to the Flask API Service!'})


# Manejo de errores específico para el módulo recepcionista
@recepcionista_bp.errorhandler(404)
def recepcionista_not_found(error):
    """
    Maneja errores 404 en el módulo recepcionista
    """
    flash('La página solicitada no existe', 'warning')
    return redirect(url_for('recepcionista.panel'))


@recepcionista_bp.errorhandler(500)
def recepcionista_server_error(error):
    """
    Maneja errores 500 en el módulo recepcionista
    """
    flash('Ha ocurrido un error en el servidor. Por favor, intenta nuevamente', 'danger')
    return redirect(url_for('recepcionista.panel'))
