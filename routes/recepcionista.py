"""
Rutas para el módulo de recepcionista
Gestiona el panel recepcionista y sus funcionalidades
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from functools import wraps
from datetime import datetime, date
from bd import obtener_conexion

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

        # Verificar si el usuario es recepcionista (id_rol = 3)
        if session.get('id_rol') != 3:
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('home'))

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
    usuario = {
        'id': session.get('usuario_id'),
        'nombre': 'Recepcionista',  # Valor por defecto
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
            else:
                # Si no se encuentra un nombre válido, mantener 'Recepcionista' y agregar mensaje de debug
                usuario['mensaje_debug'] = 'No se pudo obtener el nombre del empleado. Verifica que el empleado tenga nombres y apellidos en la base de datos.'
        except Exception as e:
            print(f"Error obteniendo nombre del empleado: {e}")
            usuario['mensaje_debug'] = f'Error al consultar la base de datos: {str(e)}'
        finally:
            if 'conexion' in locals():
                conexion.close()
    else:
        usuario['mensaje_debug'] = 'No hay id_empleado en la sesión. El usuario no está asociado a un empleado.'

    # Temporal: Forzar mensaje de debug para testing
    usuario['mensaje_debug'] = 'Mensaje de debug de prueba para verificar la visualización.'

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
    API: Busca pacientes por nombre o DNI para autocompletado
    """
    try:
        query = request.args.get('q', '').strip()

        if len(query) < 2:
            return jsonify([])

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Buscar pacientes que coincidan con el término de búsqueda
        cursor.execute("""
            SELECT
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad as dni
            FROM PACIENTE p
            INNER JOIN USUARIO u ON p.id_usuario = u.id_usuario
            WHERE u.estado = 'activo'
            AND (
                CONCAT(p.nombres, ' ', p.apellidos) LIKE %s
                OR p.documento_identidad LIKE %s
            )
            ORDER BY p.apellidos, p.nombres
            LIMIT 10
        """, (f'%{query}%', f'%{query}%'))

        pacientes = cursor.fetchall()

        return jsonify(pacientes)

    except Exception as e:
        print(f"Error al buscar pacientes: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'conexion' in locals() and conexion:
            conexion.close()


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
        # Obtener datos del formulario
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        documento_identidad = request.form.get('dni')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        direccion = request.form.get('direccion')

        # Validaciones básicas
        if not all([nombres, apellidos, documento_identidad, fecha_nacimiento, telefono, email]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

        # Obtener id_distrito (por defecto, asumimos uno genérico o el primero)
        # En una implementación real, esto vendría de un select de ubicación
        id_distrito = 1  # Valor por defecto

        # Importar modelos necesarios
        from models.paciente import Paciente
        from models.usuario import Usuario

        # Crear usuario primero
        resultado_usuario = Usuario.crear_usuario(
            contrasena='123456',  # Contraseña temporal
            correo=email,
            telefono=telefono
        )

        if 'error' in resultado_usuario:
            return jsonify({'success': False, 'message': resultado_usuario['error']}), 400

        id_usuario = resultado_usuario['id_usuario']

        # Crear paciente
        resultado_paciente = Paciente.crear(
            nombres=nombres,
            apellidos=apellidos,
            documento=documento_identidad,
            sexo=request.form.get('sexo', 'M'),
            fecha_nacimiento=fecha_nacimiento,
            id_usuario=id_usuario,
            id_distrito=id_distrito
        )

        if 'error' in resultado_paciente:
            # Si falla la creación del paciente, eliminar el usuario creado
            Usuario.eliminar(id_usuario)
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
            except ValueError:
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
    API: Genera una nueva incidencia
    """
    try:
        tipo_incidencia = request.form.get('tipo_incidencia')
        descripcion = request.form.get('descripcion')
        prioridad = request.form.get('prioridad')
        id_paciente = request.form.get('id_paciente')  # Opcional

        # Validaciones
        if not all([tipo_incidencia, descripcion, prioridad]):
            return jsonify({'success': False, 'message': 'Tipo de incidencia, descripción y prioridad son requeridos'}), 400

        # Obtener ID del empleado recepcionista
        id_empleado = session.get('id_empleado')
        if not id_empleado:
            return jsonify({'success': False, 'message': 'No se pudo identificar al empleado'}), 400

        # Usar el modelo Incidencia para crear la incidencia
        from models.incidencia import Incidencia
        resultado = Incidencia.crear(descripcion, id_paciente, tipo_incidencia, prioridad)

        if resultado['success']:
            return jsonify({'success': True, 'message': 'Incidencia generada exitosamente'})
        else:
            return jsonify({'success': False, 'message': resultado['message']}), 500

    except Exception as e:
        print(f"Error al generar incidencia: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


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
