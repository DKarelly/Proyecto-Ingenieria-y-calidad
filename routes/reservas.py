from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.empleado import Empleado
from models.servicio import Servicio
from models.catalogos import TipoServicio
from models.horario import Horario
from models.paciente import Paciente
from models.reserva import Reserva
from bd import obtener_conexion

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/')
def panel():
    """Panel de Reservas"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('panel.html', subsistema='reservas')

@reservas_bp.route('/consultar-servicio-medico')
def consultar_servicio_medico():
    """Consultar Servicio por Médico"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Obtener solo médicos (empleados con roles de médico y especialidad asignada)
    medicos = Empleado.obtener_medicos()

    return render_template('ConsultarServicioPorMédico.html', medicos=medicos)


@reservas_bp.route('/api/servicios-por-medico/<int:id_empleado>')
def api_servicios_por_medico(id_empleado):
    """Retorna servicios disponibles para el médico (por su especialidad)."""
    # Obtener empleado
    empleado = Empleado.obtener_por_id(id_empleado)
    if not empleado:
        return jsonify({'error': 'Empleado no encontrado'}), 404

    # Verificar que el empleado sea médico (roles 2 o 3)
    id_rol = empleado.get('id_rol')
    if id_rol not in [2, 3]:
        return jsonify({'error': 'El empleado no es un médico'}), 400

    id_especialidad = empleado.get('id_especialidad')
    if not id_especialidad:
        return jsonify({'error': 'El médico no tiene especialidad asignada'}), 400

    servicios = Servicio.obtener_por_especialidad(id_especialidad)
    return jsonify({'servicios': servicios})

@reservas_bp.route('/consultar-disponibilidad')
def consultar_disponibilidad():
    """Consultar Disponibilidad"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    # Pasar lista de servicios y médicos al template
    servicios = Servicio.obtener_todos()
    medicos = Empleado.obtener_medicos()
    return render_template('consultarDisponibilidad.html', servicios=servicios, medicos=medicos)


@reservas_bp.route('/api/horarios-disponibles')
def api_horarios_disponibles():
    """Retorna horarios disponibles para una fecha y (opcional) empleado o servicio.

    Parámetros GET:
    - fecha: YYYY-MM-DD (requerido)
    - id_empleado: int (opcional)
    - id_servicio: int (opcional)
    """
    fecha = request.args.get('fecha')
    id_empleado = request.args.get('id_empleado')
    id_servicio = request.args.get('id_servicio')

    resultados = []

    # Helper: filtrar horarios por estado 'disponible' y fecha >= hoy cuando fecha no es provista
    from datetime import date
    hoy = date.today()

    def filtrar_horarios_lista(lista):
        out = []
        for h in lista:
            try:
                fecha_h = h.get('fecha')
                if isinstance(fecha_h, str):
                    fecha_h_obj = date.fromisoformat(fecha_h)
                else:
                    fecha_h_obj = fecha_h
            except Exception:
                fecha_h_obj = None

            # Cuando no se pasa 'fecha', devolvemos horarios con fecha >= hoy y estado 'disponible'
            if h.get('estado') == 'disponible' and (fecha is None and (fecha_h_obj is None or fecha_h_obj >= hoy) or (fecha and str(h.get('fecha')) == fecha)):
                out.append(h)
        return out

    # Si se indica id_empleado, consultar directamente (fecha opcional)
    if id_empleado:
        if fecha:
            horarios = Horario.obtener_disponibles(fecha, id_empleado)
            resultados = horarios or []
        else:
            horarios = Horario.obtener_por_empleado(id_empleado)
            resultados = filtrar_horarios_lista(horarios)

    elif id_servicio:
        # Si se indica servicio, obtener su especialidad y buscar empleados
        servicio = Servicio.obtener_por_id(int(id_servicio))
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404
        id_especialidad = servicio.get('id_especialidad')
        if not id_especialidad:
            return jsonify({'error': 'Servicio no tiene especialidad asociada'}), 400
        empleados = Empleado.obtener_por_especialidad(id_especialidad)
        horarios_agr = []
        for emp in empleados:
            emp_id = emp.get('id_empleado')
            if fecha:
                h = Horario.obtener_disponibles(fecha, emp_id)
                h = h or []
                # añadir campos de empleado
                for hh in h:
                    hh['empleado_id'] = emp_id
                    hh['empleado_nombre'] = emp.get('nombres') + ' ' + (emp.get('apellidos') or '')
                horarios_agr.extend(h)
            else:
                h = Horario.obtener_por_empleado(emp_id)
                h_fil = filtrar_horarios_lista(h or [])
                for hh in h_fil:
                    hh['empleado_id'] = emp_id
                    hh['empleado_nombre'] = emp.get('nombres') + ' ' + (emp.get('apellidos') or '')
                horarios_agr.extend(h_fil)
        resultados = horarios_agr

    else:
        # Sin filtro por empleado ni servicio: devolver próximos disponibles
        if fecha:
            resultados = Horario.obtener_disponibles(fecha)
        else:
            todos = Horario.obtener_todos()
            resultados = filtrar_horarios_lista(todos or [])

    return jsonify({'horarios': resultados})

@reservas_bp.route('/consultar-servicio-tipo')
def consultar_servicio_tipo():
    """Consultar Servicio por Tipo"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    tipos = TipoServicio.obtener_todos()
    return render_template('ConsultarServicioPorTipo.html', tipos=tipos)


@reservas_bp.route('/api/servicios-por-tipo/<int:id_tipo>')
def api_servicios_por_tipo(id_tipo):
    """Retorna servicios para un tipo de servicio"""
    tipo = TipoServicio.obtener_por_id(id_tipo)
    if not tipo:
        return jsonify({'error': 'Tipo de servicio no encontrado'}), 404

    servicios = Servicio.obtener_por_tipo(id_tipo)
    return jsonify({'servicios': servicios})

@reservas_bp.route('/generar-reserva')
def generar_reserva():
    """Generar Nueva Reserva"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    servicios = Servicio.obtener_todos()
    medicos = Empleado.obtener_medicos()
    return render_template('GenerarReserva.html', servicios=servicios, medicos=medicos)


@reservas_bp.route('/api/paciente-por-dni')
def api_paciente_por_dni():
    dni = request.args.get('dni')
    if not dni:
        return jsonify({'error': 'Parámetro dni requerido'}), 400
    paciente = Paciente.obtener_por_documento(dni)
    if not paciente:
        return jsonify({'paciente': None})
    return jsonify({'paciente': paciente})


@reservas_bp.route('/api/reservas-por-paciente')
def api_reservas_por_paciente():
    """Devuelve reservas de un paciente por id_paciente (GET param)
    Parámetros: id_paciente (requerido)
    """
    id_paciente = request.args.get('id_paciente')
    if not id_paciente:
        return jsonify({'error': 'Parámetro id_paciente requerido'}), 400
    try:
        reservas = Reserva.obtener_por_paciente(int(id_paciente))
        return jsonify({'reservas': reservas})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reservas_bp.route('/api/reprogramar-reserva', methods=['POST'])
def api_reprogramar_reserva():
    """Reprograma una reserva existente a un nuevo horario.

    Body JSON: { id_reserva: int, id_horario: int }
    """
    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    id_horario = data.get('id_horario')

    if not id_reserva:
        return jsonify({'error': 'id_reserva es requerido'}), 400
    if not id_horario:
        return jsonify({'error': 'id_horario es requerido'}), 400

    conexion = None
    try:
        # Obtener reserva actual
        reserva = Reserva.obtener_por_id(int(id_reserva))
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404

        # Obtener horario seleccionado
        horario = Horario.obtener_por_id(int(id_horario))
        if not horario:
            return jsonify({'error': 'Horario no encontrado'}), 404

        fecha = horario.get('fecha')
        hora_inicio = horario.get('hora_inicio')
        hora_fin = horario.get('hora_fin')
        id_servicio = reserva.get('id_servicio') or reserva.get('id_servicio')

        # Crear nueva programacion y actualizar la reserva para apuntar a ella
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Insertar nueva PROGRAMACION
            sql_ins = """INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario)
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql_ins, (fecha, hora_inicio, hora_fin, 'disponible', id_servicio, id_horario))
            conexion.commit()
            nuevo_id_programacion = cursor.lastrowid

            # Marcar programacion anterior como 'reprogramada' (si existe)
            id_programacion_ant = reserva.get('id_programacion')
            if id_programacion_ant:
                try:
                    cursor.execute("UPDATE PROGRAMACION SET estado = %s WHERE id_programacion = %s", ('reprogramada', id_programacion_ant))
                    conexion.commit()
                except Exception:
                    conexion.rollback()

            # Actualizar reserva
            res = Reserva.reprogramar(int(id_reserva), int(nuevo_id_programacion))
            if res.get('error'):
                conexion.rollback()
                return jsonify({'error': res.get('error')}), 500

        return jsonify({'success': True, 'id_programacion': nuevo_id_programacion})

    except Exception as e:
        if conexion:
            conexion.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conexion:
            conexion.close()


@reservas_bp.route('/api/crear-reserva', methods=['POST'])
def api_crear_reserva():
    data = request.get_json() or {}
    id_paciente = data.get('id_paciente')
    id_horario = data.get('id_horario')
    id_servicio = data.get('id_servicio')

    if not id_paciente:
        return jsonify({'error': 'id_paciente es requerido'}), 400
    if not id_servicio:
        return jsonify({'error': 'id_servicio es requerido'}), 400

    # Si nos proporcionan id_horario, crear una programación vinculada
    conexion = None
    try:
        if id_horario:
            horario = Horario.obtener_por_id(int(id_horario))
            if not horario:
                return jsonify({'error': 'Horario no encontrado'}), 404
            fecha = horario.get('fecha')
            hora_inicio = horario.get('hora_inicio')
            hora_fin = horario.get('hora_fin')
            # Insertar PROGRAMACION
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                sql = """INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario)
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (fecha, hora_inicio, hora_fin, 'disponible', id_servicio, id_horario))
                conexion.commit()
                id_programacion = cursor.lastrowid
        else:
            return jsonify({'error': 'id_horario es requerido por ahora'}), 400

        # Crear reserva con tipo = 1 (por defecto)
        res = Reserva.crear(1, int(id_paciente), int(id_programacion))
        if res.get('error'):
            return jsonify({'error': res['error']}), 500
        return jsonify({'success': True, 'id_reserva': res.get('id_reserva')}), 201

    except Exception as e:
        if conexion:
            conexion.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conexion:
            conexion.close()

@reservas_bp.route('/reporte-servicios')
def reporte_servicios():
    """Reporte de Servicios"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    servicios = Servicio.obtener_todos()
    return render_template('reporteDeServicios.html', servicios=servicios)


@reservas_bp.route('/api/reporte-servicios')
def api_reporte_servicios():
    """API: devuelve reporte de servicios filtrado por servicio y/o fecha (YYYY-MM-DD)

    Parámetros GET:
    - id_servicio: int (opcional)
    - fecha: YYYY-MM-DD (opcional)
    """
    id_servicio = request.args.get('id_servicio')
    fecha = request.args.get('fecha')

    try:
        conn = obtener_conexion()
        with conn.cursor() as cursor:
            sql = """
            SELECT P.id_programacion, P.fecha, P.hora_inicio, P.hora_fin, P.estado as programacion_estado,
                   R.id_reserva, R.id_paciente,
                   PAC.nombres as paciente_nombres, PAC.apellidos as paciente_apellidos,
                   S.id_servicio, S.nombre as servicio_nombre,
                   E.id_empleado, E.nombres as empleado_nombres, E.apellidos as empleado_apellidos
            FROM PROGRAMACION P
            LEFT JOIN RESERVA R ON R.id_programacion = P.id_programacion
            LEFT JOIN PACIENTE PAC ON R.id_paciente = PAC.id_paciente
            LEFT JOIN SERVICIO S ON P.id_servicio = S.id_servicio
            LEFT JOIN EMPLEADO E ON P.id_horario IS NOT NULL AND E.id_empleado = P.id_horario -- fallback, will try to join via HORARIO later
            """

            # The schema stores relation between PROGRAMACION and HORARIO via id_horario
            # We'll join HORARIO to obtain empleado if available
            sql = sql + "\nLEFT JOIN HORARIO H ON P.id_horario = H.id_horario"

            where_clauses = []
            params = []
            if id_servicio:
                where_clauses.append('P.id_servicio = %s')
                params.append(int(id_servicio))
            if fecha:
                where_clauses.append('P.fecha = %s')
                params.append(fecha)

            if where_clauses:
                sql = sql + '\nWHERE ' + ' AND '.join(where_clauses)

            sql = sql + '\nORDER BY P.fecha DESC, P.hora_inicio'

            cursor.execute(sql, params)
            rows = cursor.fetchall()

        # Transform rows into JSON-able list
        resultados = []
        for r in rows:
            empleado_nombre = None
            if r.get('empleado_nombres'):
                empleado_nombre = (r.get('empleado_nombres') or '') + ' ' + (r.get('empleado_apellidos') or '')
            else:
                # try empleado from HORARIO (H.id_empleado)
                # some rows may include H.id_empleado as 'id_empleado' from the join
                if r.get('id_empleado'):
                    empleado_nombre = ''  # placeholder; detailed join may be improved if needed

            resultados.append({
                'id_programacion': r.get('id_programacion'),
                'fecha': str(r.get('fecha')),
                'hora_inicio': str(r.get('hora_inicio')),
                'hora_fin': str(r.get('hora_fin')),
                'programacion_estado': r.get('programacion_estado'),
                'id_reserva': r.get('id_reserva'),
                'id_paciente': r.get('id_paciente'),
                'paciente': (r.get('paciente_nombres') or '') + ' ' + (r.get('paciente_apellidos') or ''),
                'id_servicio': r.get('id_servicio'),
                'servicio': r.get('servicio_nombre'),
                'empleado': empleado_nombre
            })

        return jsonify({'report': resultados})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@reservas_bp.route('/reprogramar-reserva')
def reprogramar_reserva():
    """Reprogramar Reserva"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('ReprogramarReserva.html')

@reservas_bp.route('/gestionar-cancelaciones')
def gestionar_cancelaciones():
    """Gestionar Cancelaciones"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('GestionarCancelaciones.html')


@reservas_bp.route('/api/reservas-activas')
def api_reservas_activas():
    """Obtiene todas las reservas activas (no canceladas)
    Parámetros GET opcionales:
    - dni: documento de identidad del paciente para filtrar
    """
    # Verificar autenticación
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    dni = request.args.get('dni', '').strip()

    # Validar formato de DNI si se proporciona
    if dni:
        if not dni.isdigit() or len(dni) != 8:
            return jsonify({'error': 'DNI inválido. Debe contener 8 dígitos'}), 400

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            if dni:
                # Buscar reservas por DNI del paciente
                sql = """
                    SELECT r.id_reserva,
                           r.estado,
                           r.fecha_registro,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           s.nombre as servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE r.estado != 'cancelada'
                    AND p.documento_identidad = %s
                    ORDER BY prog.fecha DESC, prog.hora_inicio DESC
                """
                cursor.execute(sql, (dni,))
            else:
                # Obtener todas las reservas activas
                sql = """
                    SELECT r.id_reserva,
                           r.estado,
                           r.fecha_registro,
                           CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                           p.documento_identidad,
                           prog.fecha as fecha_cita,
                           prog.hora_inicio,
                           prog.hora_fin,
                           s.nombre as servicio,
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado
                    FROM RESERVA r
                    INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                    INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                    INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                    INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                    INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    WHERE r.estado != 'cancelada'
                    ORDER BY prog.fecha DESC, prog.hora_inicio DESC
                """
                cursor.execute(sql)

            reservas = cursor.fetchall()

            # Convertir a formato JSON
            resultado = []
            for reserva in reservas:
                resultado.append({
                    'id_reserva': reserva.get('id_reserva'),
                    'estado': reserva.get('estado'),
                    'nombre_paciente': reserva.get('nombre_paciente'),
                    'documento_identidad': reserva.get('documento_identidad'),
                    'fecha_cita': str(reserva.get('fecha_cita')),
                    'hora_inicio': str(reserva.get('hora_inicio')),
                    'hora_fin': str(reserva.get('hora_fin')),
                    'servicio': reserva.get('servicio'),
                    'nombre_empleado': reserva.get('nombre_empleado')
                })

            return jsonify({'reservas': resultado})

    except Exception as e:
        return jsonify({'error': f'Error al obtener reservas: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/cancelar-reserva', methods=['POST'])
def api_cancelar_reserva():
    """Cancela una reserva específica
    Body JSON: { id_reserva: int, motivo: str }
    """
    # Verificar autenticación
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    motivo = data.get('motivo', '').strip()

    # Validaciones
    if not id_reserva:
        return jsonify({'error': 'id_reserva es requerido'}), 400

    try:
        id_reserva = int(id_reserva)
    except (ValueError, TypeError):
        return jsonify({'error': 'id_reserva debe ser un número válido'}), 400

    if not motivo:
        return jsonify({'error': 'El motivo de cancelación es requerido'}), 400

    if len(motivo) < 10:
        return jsonify({'error': 'El motivo debe tener al menos 10 caracteres'}), 400

    if len(motivo) > 500:
        return jsonify({'error': 'El motivo no puede exceder 500 caracteres'}), 400

    try:
        # Verificar que la reserva existe y está activa
        reserva = Reserva.obtener_por_id(id_reserva)
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404

        if reserva.get('estado') == 'cancelada':
            return jsonify({'error': 'La reserva ya está cancelada'}), 400

        if reserva.get('estado') == 'completada':
            return jsonify({'error': 'No se puede cancelar una reserva completada'}), 400

        # Cancelar la reserva
        resultado = Reserva.cancelar(id_reserva, motivo)

        if resultado.get('error'):
            return jsonify({'error': resultado['error']}), 500

        # Log de auditoría (opcional - puedes implementar una tabla de auditoría)
        # AuditLog.crear('cancelacion_reserva', session['usuario_id'], id_reserva, motivo)

        return jsonify({
            'success': True,
            'message': 'Reserva cancelada exitosamente',
            'id_reserva': id_reserva
        })

    except Exception as e:
        return jsonify({'error': f'Error al cancelar reserva: {str(e)}'}), 500


# ========== RUTAS PARA PACIENTES ==========

@reservas_bp.route('/paciente/nueva-cita')
def paciente_nueva_cita():
    """Vista para que pacientes registren nuevas citas"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('RegistrarCitaPaciente.html')


@reservas_bp.route('/api/servicios-activos')
def api_servicios_activos():
    """Retorna todos los servicios activos disponibles para pacientes"""
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT s.id_servicio, s.nombre, s.descripcion, e.nombre as especialidad
                FROM SERVICIO s
                LEFT JOIN ESPECIALIDAD e ON s.id_especialidad = e.id_especialidad
                WHERE s.estado = 'activo'
                ORDER BY s.nombre
            """
            cursor.execute(sql)
            servicios = cursor.fetchall()

            return jsonify({'servicios': servicios})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/medicos-por-servicio/<int:id_servicio>')
def api_medicos_por_servicio(id_servicio):
    """Retorna médicos disponibles para un servicio específico"""
    try:
        # Obtener servicio para saber la especialidad
        servicio = Servicio.obtener_por_id(id_servicio)
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404

        id_especialidad = servicio.get('id_especialidad')
        if not id_especialidad:
            return jsonify({'error': 'Servicio sin especialidad asignada'}), 400

        # Obtener médicos de esa especialidad
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT e.id_empleado, e.nombres, e.apellidos, esp.nombre as especialidad
                FROM EMPLEADO e
                INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE e.id_especialidad = %s
                AND e.estado = 'activo'
                AND e.id_rol IN (2, 3)
                ORDER BY e.apellidos, e.nombres
            """
            cursor.execute(sql, (id_especialidad,))
            medicos = cursor.fetchall()

            return jsonify({'medicos': medicos})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/medico/<int:id_medico>')
def api_medico(id_medico):
    """Retorna información detallada de un médico incluyendo un servicio que puede ofrecer"""
    try:
        # Obtener empleado
        empleado = Empleado.obtener_por_id(id_medico)
        if not empleado:
            return jsonify({'error': 'Médico no encontrado'}), 404

        # Verificar que sea médico
        id_rol = empleado.get('id_rol')
        if id_rol not in [2, 3]:
            return jsonify({'error': 'El empleado no es un médico'}), 400

        # Obtener un servicio de la especialidad del médico
        id_especialidad = empleado.get('id_especialidad')
        servicio = None
        servicio_nombre = None
        id_servicio = None
        
        if id_especialidad:
            servicios = Servicio.obtener_por_especialidad(id_especialidad)
            if servicios and len(servicios) > 0:
                servicio = servicios[0]
                id_servicio = servicio.get('id_servicio')
                servicio_nombre = servicio.get('nombre')

        # Construir respuesta
        respuesta = {
            'id_empleado': empleado.get('id_empleado'),
            'nombres': empleado.get('nombres'),
            'apellidos': empleado.get('apellidos'),
            'id_servicio': id_servicio,
            'servicio_nombre': servicio_nombre,
            'especialidad': empleado.get('especialidad')
        }

        return jsonify(respuesta)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reservas_bp.route('/paciente/crear-reserva', methods=['POST'])
def paciente_crear_reserva():
    """Crea una nueva reserva para un paciente autenticado"""
    # Verificar autenticación
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_servicio = data.get('id_servicio')
    id_horario = data.get('id_horario')

    # Validaciones
    if not id_servicio:
        return jsonify({'error': 'Servicio es requerido'}), 400

    if not id_horario:
        return jsonify({'error': 'Horario es requerido'}), 400

    try:
        # Obtener el id_paciente asociado al usuario actual
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        # Verificar que el horario existe y está disponible
        horario = Horario.obtener_por_id(int(id_horario))
        if not horario:
            return jsonify({'error': 'Horario no encontrado'}), 404

        if horario.get('disponibilidad') != 'Disponible':
            return jsonify({'error': 'El horario seleccionado ya no está disponible'}), 400

        # Obtener datos del horario
        fecha = horario.get('fecha')
        hora_inicio = horario.get('hora_inicio')
        hora_fin = horario.get('hora_fin')

        # Crear programación
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql_prog = """
                INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_prog, (fecha, hora_inicio, hora_fin, 'disponible', id_servicio, id_horario))
            conexion.commit()
            id_programacion = cursor.lastrowid

            # Crear reserva (tipo 1 = reserva normal)
            from datetime import datetime
            fecha_actual = datetime.now().date()
            hora_actual = datetime.now().time()

            sql_reserva = """
                INSERT INTO RESERVA (fecha_registro, hora_registro, tipo, estado, id_paciente, id_programacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_reserva, (fecha_actual, hora_actual, 1, 'activa', id_paciente, id_programacion))
            conexion.commit()
            id_reserva = cursor.lastrowid

            # Actualizar disponibilidad del horario
            sql_update_horario = """
                UPDATE HORARIO SET disponibilidad = 'Ocupado' WHERE id_horario = %s
            """
            cursor.execute(sql_update_horario, (id_horario,))
            conexion.commit()

        return jsonify({
            'success': True,
            'id_reserva': id_reserva,
            'message': 'Cita agendada exitosamente'
        }), 201

    except Exception as e:
        if conexion:
            conexion.rollback()
        return jsonify({'error': f'Error al crear reserva: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/paciente/historial')
def paciente_historial_reservas():
    """Vista del historial de reservas del paciente"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('HistorialReservasPaciente.html')


@reservas_bp.route('/api/paciente/mis-reservas')
def api_paciente_mis_reservas():
    """API que retorna todas las reservas del paciente autenticado"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        # Obtener el id_paciente del usuario
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT r.id_reserva,
                       r.fecha_registro,
                       r.estado as estado_reserva,
                       p.fecha as fecha_cita,
                       p.hora_inicio,
                       p.hora_fin,
                       s.nombre as servicio,
                       e.nombres as medico_nombres,
                       e.apellidos as medico_apellidos,
                       esp.nombre as especialidad
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE r.id_paciente = %s
                ORDER BY p.fecha DESC, p.hora_inicio DESC
            """
            cursor.execute(sql, (id_paciente,))
            reservas = cursor.fetchall()

            return jsonify({'reservas': reservas})

    except Exception as e:
        return jsonify({'error': f'Error al obtener reservas: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass
