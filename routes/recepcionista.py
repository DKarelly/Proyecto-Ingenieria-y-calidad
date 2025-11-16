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
                (SELECT COUNT(*) FROM RESERVA WHERE DATE(fecha_creacion) = CURDATE()) as reservas_hoy,
                (SELECT COUNT(*) FROM PACIENTE WHERE DATE(fecha_creacion) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)) as pacientes_registrados,
                (SELECT COUNT(*) FROM INCIDENCIA WHERE estado = 'abierta') as incidencias_pendientes
        """)

        result = cursor.fetchone()

        return {
            'reservas_hoy': result['reservas_hoy'] or 0,
            'pacientes_registrados': result['pacientes_registrados'] or 0,
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
                id_incidencia,
                titulo,
                descripcion,
                severidad,
                estado,
                fecha_creacion
            FROM INCIDENCIA
            ORDER BY fecha_creacion DESC
            LIMIT 5
        """)

        incidencias = cursor.fetchall()

        # Formatear fechas
        for incidencia in incidencias:
            if isinstance(incidencia['fecha_creacion'], str):
                incidencia['fecha_creacion'] = datetime.strptime(incidencia['fecha_creacion'], '%Y-%m-%d %H:%M:%S')
            elif hasattr(incidencia['fecha_creacion'], 'strftime'):
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
                p.documento_identidad,
                p.sexo,
                u.telefono,
                u.correo
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
    Obtiene todas las incidencias
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_incidencia,
                titulo,
                descripcion,
                tipo_incidencia,
                severidad,
                estado,
                fecha_creacion
            FROM INCIDENCIA
            ORDER BY fecha_creacion DESC
        """)

        incidencias = cursor.fetchall()
        return incidencias

    except Exception as e:
        print(f"Error al obtener incidencias: {e}")
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
        'nombre': session.get('nombre_usuario'),
        'email': session.get('email_usuario'),
        'rol': session.get('rol', 'Recepcionista'),
        'id_empleado': session.get('id_empleado')
    }

    # Obtener estadísticas para el dashboard
    stats = obtener_estadisticas_recepcionista()

    return render_template('panel_recepcionista.html',
                         subsistema=subsistema,
                         accion=accion,
                         usuario=usuario,
                         stats=stats)


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
    API: Lista todas las incidencias
    """
    incidencias = obtener_incidencias()
    return jsonify(incidencias)


@recepcionista_bp.route('/incidencias/generar', methods=['POST'])
@recepcionista_required
def api_incidencias_generar():
    """
    API: Genera una nueva incidencia
    """
    try:
        tipo_incidencia = request.form.get('tipo_incidencia')
        severidad = request.form.get('severidad')
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')

        # Validaciones
        if not all([tipo_incidencia, severidad, titulo, descripcion]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

        # Obtener ID del empleado recepcionista
        id_empleado = session.get('id_empleado')
        if not id_empleado:
            return jsonify({'success': False, 'message': 'No se pudo identificar al empleado'}), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Insertar incidencia
        cursor.execute("""
            INSERT INTO INCIDENCIA (
                titulo, descripcion, tipo_incidencia, severidad,
                estado, id_empleado_reporta, fecha_creacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            titulo, descripcion, tipo_incidencia, severidad,
            'abierta', id_empleado, datetime.now()
        ))

        conexion.commit()

        return jsonify({'success': True, 'message': 'Incidencia generada exitosamente'})

    except Exception as e:
        if 'conexion' in locals() and conexion:
            conexion.rollback()
        print(f"Error al generar incidencia: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500
    finally:
        if 'conexion' in locals() and conexion:
            conexion.close()


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
