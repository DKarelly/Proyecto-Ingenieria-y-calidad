from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.empleado import Empleado
from models.servicio import Servicio
from models.catalogos import TipoServicio
from models.horario import Horario
from models.paciente import Paciente
from models.reserva import Reserva
from models.programacion import Programacion
from bd import obtener_conexion
from datetime import date, datetime, timedelta, time
from models.notificacion import Notificacion
import time as time_module
from utils.email_service import (
    enviar_email_reserva_creada,
    enviar_email_reserva_creada_medico,
    enviar_email_cancelacion_aprobada,
    enviar_email_cancelacion_medico,
    enviar_email_reprogramacion_aprobada,
    enviar_email_reprogramacion_medico,
    enviar_email_confirmacion_reserva,
    enviar_email_recordatorio_24h,
    enviar_email_recordatorio_2h
)

reservas_bp = Blueprint('reservas', __name__)

# Variable global para controlar la frecuencia de actualización
_ultima_actualizacion_horarios = None
_intervalo_actualizacion = 300  # 5 minutos en segundos

def actualizar_horarios_vencidos():
    """
    Actualiza automáticamente el estado de las programaciones a 'Ocupado' o 'Bloqueado'
    cuando la fecha ya ha pasado.
    
    Esta función se ejecuta automáticamente antes de consultar horarios,
    pero solo si han pasado al menos 5 minutos desde la última actualización.
    
    Nota: La tabla HORARIO ahora usa 'activo' (bool) en lugar de 'estado'.
    """
    global _ultima_actualizacion_horarios
    
    # Verificar si necesitamos actualizar (evitar llamadas frecuentes)
    tiempo_actual = time_module.time()
    if _ultima_actualizacion_horarios is not None:
        if (tiempo_actual - _ultima_actualizacion_horarios) < _intervalo_actualizacion:
            return 0  # No actualizar todavía
    
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Establecer un timeout corto para evitar bloqueos largos
        cursor.execute("SET SESSION innodb_lock_wait_timeout = 2")
        
        fecha_actual = date.today()
        
        # Actualizar programaciones cuya fecha ya pasó y siguen como Disponible
        query = """
            UPDATE PROGRAMACION 
            SET estado = 'Ocupado'
            WHERE fecha < %s 
            AND estado = 'Disponible'
        """
        
        cursor.execute(query, (fecha_actual,))
        registros_actualizados = cursor.rowcount
        conn.commit()
        
        # Actualizar el timestamp de última actualización
        _ultima_actualizacion_horarios = tiempo_actual
        
        if registros_actualizados > 0:
            print(f"✓ Se actualizaron {registros_actualizados} programaciones vencidas")
        
        return registros_actualizados
        
    except Exception as e:
        # Silenciar errores de timeout para no interrumpir las consultas
        if "Lock wait timeout" in str(e):
            print(f"⚠ Timeout al actualizar horarios vencidos (se omitirá por ahora)")
        else:
            print(f"Error al actualizar horarios vencidos: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return 0
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

@reservas_bp.route('/')
def panel():
    """Panel de Reservas"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    # Redirigir al dashboard principal unificado
    return redirect(url_for('admin_panel', subsistema='reservas'))

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
    
    # Actualizar horarios vencidos antes de mostrar la página
    actualizar_horarios_vencidos()
    
    # Pasar lista de servicios y médicos al template
    servicios = Servicio.obtener_todos()
    medicos = Empleado.obtener_medicos()
    return render_template('consultarDisponibilidad.html', servicios=servicios, medicos=medicos)


@reservas_bp.route('/listar-reservas')
def listar_reservas():
    """Listar Reservas con filtros"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Obtener datos para los filtros
    servicios = Servicio.obtener_todos()
    tipos_servicio = TipoServicio.obtener_todos()
    medicos = Empleado.obtener_medicos()
    
    # Estados de reserva
    estados = ['Confirmada', 'Completada', 'Cancelada', 'Inasistida']
    
    return render_template('listarReservas.html', 
                         servicios=servicios, 
                         tipos_servicio=tipos_servicio,
                         medicos=medicos,
                         estados=estados)


@reservas_bp.route('/api/listar-reservas')
def api_listar_reservas():
    """
    API para listar reservas con filtros
    
    Parámetros GET opcionales:
    - fecha_desde: YYYY-MM-DD
    - fecha_hasta: YYYY-MM-DD
    - id_servicio: int
    - id_tipo_servicio: int
    - id_empleado: int
    - id_paciente: int
    - dni_paciente: str
    - estado: str (Confirmada, Completada, Cancelada, Inasistida)
    """
    try:
        # Obtener parámetros de filtro
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        id_servicio = request.args.get('id_servicio')
        id_tipo_servicio = request.args.get('id_tipo_servicio')
        id_empleado = request.args.get('id_empleado')
        id_paciente = request.args.get('id_paciente')
        dni_paciente = request.args.get('dni_paciente')
        estado = request.args.get('estado')
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Construir query base
            sql = """
                SELECT 
                    r.id_reserva,
                    r.estado as estado_reserva,
                    r.fecha_registro,
                    r.hora_registro,
                    p.fecha as fecha_programacion,
                    TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                    TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                    pac.id_paciente,
                    CONCAT(pac.nombres, ' ', pac.apellidos) as paciente_nombre,
                    pac.documento_identidad as paciente_dni,
                    s.id_servicio,
                    s.nombre as servicio_nombre,
                    ts.nombre as tipo_servicio,
                    e.id_empleado,
                    CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                    esp.nombre as especialidad
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE 1=1
            """
            
            params = []
            
            # Aplicar filtros
            if fecha_desde:
                sql += " AND p.fecha >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                sql += " AND p.fecha <= %s"
                params.append(fecha_hasta)
            
            if id_servicio:
                sql += " AND s.id_servicio = %s"
                params.append(int(id_servicio))
            
            if id_tipo_servicio:
                sql += " AND ts.id_tipo_servicio = %s"
                params.append(int(id_tipo_servicio))
            
            if id_empleado:
                sql += " AND e.id_empleado = %s"
                params.append(int(id_empleado))
            
            if id_paciente:
                sql += " AND pac.id_paciente = %s"
                params.append(int(id_paciente))
            
            if dni_paciente:
                sql += " AND pac.documento_identidad = %s"
                params.append(dni_paciente)
            
            if estado:
                sql += " AND r.estado = %s"
                params.append(estado)
            
            sql += " ORDER BY p.fecha DESC, p.hora_inicio DESC, r.fecha_registro DESC"
            
            cursor.execute(sql, params)
            reservas = cursor.fetchall()
            
            # Convertir fechas a string
            for reserva in reservas:
                if reserva.get('fecha_registro'):
                    reserva['fecha_registro'] = reserva['fecha_registro'].strftime('%Y-%m-%d')
                if reserva.get('fecha_programacion'):
                    reserva['fecha_programacion'] = reserva['fecha_programacion'].strftime('%Y-%m-%d')
                if reserva.get('hora_registro'):
                    if isinstance(reserva['hora_registro'], timedelta):
                        total_seconds = int(reserva['hora_registro'].total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        reserva['hora_registro'] = f"{hours:02d}:{minutes:02d}"
                    else:
                        reserva['hora_registro'] = str(reserva['hora_registro'])[:5]
            
            return jsonify({
                'reservas': reservas,
                'total': len(reservas)
            })
            
    except Exception as e:
        print(f"[API] Error al listar reservas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al listar reservas: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/detalle-reserva/<int:id_reserva>')
def api_detalle_reserva(id_reserva):
    """
    API para obtener el detalle completo de una reserva
    Incluye información de CITA, EXAMEN u OPERACION según corresponda
    """
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Obtener información básica de la reserva
            sql = """
                SELECT 
                    r.id_reserva,
                    r.estado as estado_reserva,
                    r.fecha_registro,
                    r.hora_registro,
                    p.fecha as fecha_programacion,
                    TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                    TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                    pac.id_paciente,
                    CONCAT(pac.nombres, ' ', pac.apellidos) as paciente_nombre,
                    pac.documento_identidad as paciente_dni,
                    s.id_servicio,
                    s.nombre as servicio_nombre,
                    ts.nombre as tipo_servicio,
                    e.id_empleado,
                    CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                    esp.nombre as especialidad
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                LEFT JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE r.id_reserva = %s
            """
            cursor.execute(sql, (id_reserva,))
            reserva = cursor.fetchone()
            
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada'}), 404
            
            # Convertir fechas
            if reserva.get('fecha_registro'):
                reserva['fecha_registro'] = reserva['fecha_registro'].strftime('%Y-%m-%d')
            if reserva.get('fecha_programacion'):
                reserva['fecha_programacion'] = reserva['fecha_programacion'].strftime('%Y-%m-%d')
            if reserva.get('hora_registro'):
                if isinstance(reserva['hora_registro'], timedelta):
                    total_seconds = int(reserva['hora_registro'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    reserva['hora_registro'] = f"{hours:02d}:{minutes:02d}"
                else:
                    reserva['hora_registro'] = str(reserva['hora_registro'])[:5]
            
            # Buscar información específica según el tipo de servicio
            tipo_servicio = reserva.get('tipo_servicio', '').lower()
            
            # Buscar CITA
            cursor.execute("""
                SELECT id_cita, fecha_cita, TIME_FORMAT(hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(hora_fin, '%%H:%%i') as hora_fin, diagnostico, 
                       observaciones, estado
                FROM CITA
                WHERE id_reserva = %s
            """, (id_reserva,))
            cita = cursor.fetchone()
            if cita and cita.get('fecha_cita'):
                cita['fecha_cita'] = cita['fecha_cita'].strftime('%Y-%m-%d')
                reserva['cita'] = cita
            
            # Buscar EXAMEN
            try:
                cursor.execute("""
                    SELECT id_examen, fecha_examen, 
                           TIME_FORMAT(hora_inicio, '%%H:%%i') as hora_inicio,
                           observacion, estado
                    FROM EXAMEN
                    WHERE id_reserva = %s
                """, (id_reserva,))
                examen = cursor.fetchone()
                if examen and examen.get('fecha_examen'):
                    examen['fecha_examen'] = examen['fecha_examen'].strftime('%Y-%m-%d')
                    reserva['examen'] = examen
            except Exception as e:
                # Si falla (columna hora_inicio no existe), intentar sin ella
                print(f"[DEBUG] Error al buscar examen con hora: {e}")
                try:
                    cursor.execute("""
                        SELECT id_examen, fecha_examen, observacion, estado
                        FROM EXAMEN
                        WHERE id_reserva = %s
                    """, (id_reserva,))
                    examen = cursor.fetchone()
                    if examen:
                        if examen.get('fecha_examen'):
                            examen['fecha_examen'] = examen['fecha_examen'].strftime('%Y-%m-%d')
                        examen['hora_inicio'] = 'No disponible'
                        reserva['examen'] = examen
                except Exception as e2:
                    print(f"[DEBUG] Error al buscar examen sin hora: {e2}")
            
            # Buscar OPERACION con recursos
            try:
                cursor.execute("""
                    SELECT o.id_operacion, o.fecha_operacion, 
                           TIME_FORMAT(o.hora_inicio, '%%H:%%i') as hora_inicio,
                           TIME_FORMAT(o.hora_fin, '%%H:%%i') as hora_fin, 
                           o.observaciones
                    FROM OPERACION o
                    WHERE o.id_reserva = %s
                """, (id_reserva,))
                operacion = cursor.fetchone()
                if operacion:
                    if operacion.get('fecha_operacion'):
                        operacion['fecha_operacion'] = operacion['fecha_operacion'].strftime('%Y-%m-%d')
                    
                    # Obtener recursos de la operación
                    cursor.execute("""
                        SELECT r.id_recurso, r.nombre, r.descripcion
                        FROM OPERACION_RECURSO or1
                        INNER JOIN RECURSO r ON or1.id_recurso = r.id_recurso
                        WHERE or1.id_operacion = %s
                    """, (operacion['id_operacion'],))
                    recursos = cursor.fetchall()
                    operacion['recursos'] = recursos
                    reserva['operacion'] = operacion
            except Exception as e:
                print(f"[DEBUG] Error al buscar operación: {e}")
            
            return jsonify(reserva)
            
    except Exception as e:
        print(f"[API] Error al obtener detalle de reserva: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener detalle: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/cancelar-reserva/<int:id_reserva>', methods=['POST'])
def api_cancelar_reserva(id_reserva):
    """
    API para cancelar una reserva
    Actualiza el estado de la reserva a 'Cancelada' y la programación a 'Disponible'
    """
    try:
        # Obtener motivo de cancelación del request (opcional)
        # Usar silent=True para evitar error si no hay JSON body
        data = request.get_json(silent=True) or {}
        motivo = data.get('motivo', 'Cancelación solicitada por el usuario')
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la reserva existe y está en estado Confirmada
            cursor.execute("""
                SELECT r.estado, r.id_programacion
                FROM RESERVA r
                WHERE r.id_reserva = %s
            """, (id_reserva,))
            reserva = cursor.fetchone()
            
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada'}), 404
            
            if reserva['estado'] == 'Cancelada':
                return jsonify({'error': 'La reserva ya está cancelada'}), 400
            
            if reserva['estado'] in ['Completada', 'Inasistida']:
                return jsonify({'error': f'No se puede cancelar una reserva en estado {reserva["estado"]}'}), 400
            
            # Actualizar estado de la reserva
            hora_actual = datetime.now().time()
            
            cursor.execute("""
                UPDATE RESERVA 
                SET estado = 'Cancelada',
                    fecha_cancelada = %s,
                    motivo_cancelacion = %s
                WHERE id_reserva = %s
            """, (hora_actual, motivo, id_reserva))
            
            # Liberar la programación
            cursor.execute("""
                UPDATE PROGRAMACION
                SET estado = 'Disponible'
                WHERE id_programacion = %s
            """, (reserva['id_programacion'],))
            
            conexion.commit()
            
            # Enviar notificación al paciente
            try:
                cursor.execute("""
                    SELECT id_paciente FROM RESERVA WHERE id_reserva = %s
                """, (id_reserva,))
                paciente_data = cursor.fetchone()
                if paciente_data:
                    Notificacion.crear(
                        paciente_data['id_paciente'],
                        'reserva_cancelada',
                        f'Su reserva #{id_reserva} ha sido cancelada.',
                        f'/paciente/mis-reservas'
                    )
            except Exception as e:
                print(f"Error al crear notificación: {e}")
            
            return jsonify({'message': 'Reserva cancelada exitosamente'})
            
    except Exception as e:
        print(f"[API] Error al cancelar reserva: {e}")
        import traceback
        traceback.print_exc()
        try:
            conexion.rollback()
        except:
            pass
        return jsonify({'error': f'Error al cancelar reserva: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/horarios-semana/<int:id_empleado>')
def api_horarios_semana(id_empleado):
    """
    Retorna los horarios de una semana para un médico específico
    Agrupa por fecha y muestra si está disponible o no
    
    Parámetros GET opcionales:
    - fecha_inicio: YYYY-MM-DD (fecha desde la cual buscar la semana)
    """
    try:
        from datetime import date, timedelta, datetime
        
        # Obtener fecha de inicio si se proporciona
        fecha_param = request.args.get('fecha_inicio')
        hoy = date.today()
        
        if fecha_param:
            try:
                fecha_inicio = datetime.strptime(fecha_param, '%Y-%m-%d').date()
                
                # Validar que no sea una fecha anterior a hoy
                if fecha_inicio < hoy:
                    return jsonify({
                        'error': 'No se pueden buscar horarios de fechas pasadas',
                        'fecha_minima': hoy.strftime('%Y-%m-%d')
                    }), 400
                
                # Calcular inicio de semana desde la fecha proporcionada (lunes de esa semana)
                inicio_semana = fecha_inicio - timedelta(days=fecha_inicio.weekday())
                
                # Si el lunes calculado es anterior a hoy, usar hoy como inicio
                if inicio_semana < hoy:
                    inicio_semana = hoy
                    
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        else:
            # Si no se proporciona fecha, usar la semana actual desde hoy
            inicio_semana = hoy
        
        # Fin de semana: 7 días después del inicio
        fin_semana = inicio_semana + timedelta(days=6)
        
        print(f"[API] Horarios para médico {id_empleado} desde {inicio_semana} hasta {fin_semana}")
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    h.id_horario,
                    h.fecha,
                    TIME_FORMAT(h.hora_inicio, '%%H:%%i') as hora_inicio,
                    TIME_FORMAT(h.hora_fin, '%%H:%%i') as hora_fin,
                    h.activo,
                    COALESCE(p.estado, 'Disponible') as estado_programacion,
                    CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                    esp.nombre as especialidad
                FROM HORARIO h
                INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                LEFT JOIN PROGRAMACION p ON p.id_horario = h.id_horario 
                    AND p.fecha = h.fecha 
                    AND p.hora_inicio = h.hora_inicio
                WHERE h.id_empleado = %s
                  AND h.fecha BETWEEN %s AND %s
                  AND h.activo = 1
                ORDER BY h.fecha, h.hora_inicio
            """
            cursor.execute(sql, (id_empleado, inicio_semana, fin_semana))
            horarios = cursor.fetchall()
            
            print(f"[API] Horarios encontrados: {len(horarios)}")
            
            # Convertir fechas a string
            for horario in horarios:
                if horario.get('fecha'):
                    horario['fecha'] = horario['fecha'].strftime('%Y-%m-%d')
                    # Agregar día de la semana
                    fecha_obj = date.fromisoformat(horario['fecha'])
                    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                    horario['dia_semana'] = dias_semana[fecha_obj.weekday()]
                
                # Marcar si es disponible (verificar estado de programación)
                estado_prog = horario.get('estado_programacion', 'Disponible')
                horario['disponible'] = estado_prog == 'Disponible'
            
            return jsonify({
                'horarios': horarios,
                'inicio_semana': inicio_semana.strftime('%Y-%m-%d'),
                'fin_semana': fin_semana.strftime('%Y-%m-%d'),
                'total': len(horarios)
            })

    except Exception as e:
        print(f"[API] Error al obtener horarios: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener horarios: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


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
            if h.get('estado') == 'Disponible' and (fecha is None and (fecha_h_obj is None or fecha_h_obj >= hoy) or (fecha and str(h.get('fecha')) == fecha)):
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

@reservas_bp.route('/api/buscar-horarios-disponibles')
def api_buscar_horarios_disponibles():
    """Búsqueda dinámica de horarios (Disponibles y Ocupados) con filtros opcionales.
    Muestra programaciones de la semana actual por defecto.
    
    Parámetros GET (todos opcionales):
    - id_servicio: int
    - id_tipo_servicio: int (1=Cita, 4=Examen, etc.)
    - id_empleado: int  
    - fecha: YYYY-MM-DD (si no se proporciona, muestra semana actual)
    """
    from datetime import date, timedelta
    
    # Actualizar automáticamente los horarios vencidos antes de consultar
    actualizar_horarios_vencidos()
    
    id_servicio = request.args.get('id_servicio', '').strip()
    id_tipo_servicio = request.args.get('id_tipo_servicio', '').strip()
    id_empleado = request.args.get('id_empleado', '').strip()
    fecha = request.args.get('fecha', '').strip()
    
    # Validar y limpiar parámetros - filtrar valores inválidos
    if id_servicio in ['', 'undefined', 'null', 'None']:
        id_servicio = None
    if id_tipo_servicio in ['', 'undefined', 'null', 'None']:
        id_tipo_servicio = None
    if id_empleado in ['', 'undefined', 'null', 'None']:
        id_servicio = None
    if id_empleado in ['', 'undefined', 'null', 'None']:
        id_empleado = None
    if fecha in ['', 'undefined', 'null', 'None']:
        fecha = None
    
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Calcular rango de la semana (lunes a domingo)
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
        fin_semana = inicio_semana + timedelta(days=6)  # Domingo de esta semana
        
        # Query: buscar TODAS las PROGRAMACIONES (Disponible y Ocupado)
        query = """
            SELECT 
                p.id_programacion,
                p.id_horario,
                p.id_servicio,
                h.id_empleado,
                p.fecha,
                TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                p.estado as estado_programacion,
                CONCAT(e.nombres, ' ', e.apellidos) as profesional,
                es.nombre as especialidad,
                s.nombre as servicio_nombre
            FROM PROGRAMACION p
            INNER JOIN HORARIO h ON p.id_horario = h.id_horario
            INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
            LEFT JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
            LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
            WHERE h.activo = 1
                AND p.fecha >= %s
                AND p.fecha <= %s
        """
        
        params = [inicio_semana, fin_semana]
        
        # Filtro por servicio específico
        if id_servicio:
            query += " AND p.id_servicio = %s"
            params.append(int(id_servicio))
        
        # Filtro por tipo de servicio (1=Cita, 4=Examen, etc.)
        if id_tipo_servicio:
            query += " AND s.id_tipo_servicio = %s"
            params.append(int(id_tipo_servicio))
        
        # Filtro por empleado
        if id_empleado:
            query += " AND h.id_empleado = %s"
            params.append(int(id_empleado))
        
        # Filtro por fecha específica (sobrescribe el rango semanal)
        if fecha:
            query = query.replace("AND p.fecha >= %s", "AND p.fecha = %s")
            query = query.replace("AND p.fecha <= %s", "")
            params = [fecha] + params[2:]  # Reemplazar los dos primeros parámetros
        
        # Ordenar por fecha, hora y empleado
        query += " ORDER BY p.fecha ASC, p.hora_inicio ASC, e.nombres ASC"
        
        cursor.execute(query, params)
        horarios = cursor.fetchall()
        
        # Convertir fechas a string y agregar info adicional
        for h in horarios:
            if h.get('fecha'):
                h['fecha'] = h['fecha'].strftime('%Y-%m-%d')
        
        return jsonify({
            'horarios': horarios,
            'inicio_semana': inicio_semana.strftime('%Y-%m-%d'),
            'fin_semana': fin_semana.strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        print(f"Error en búsqueda de horarios: {str(e)}")
        return jsonify({'error': str(e), 'horarios': []}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@reservas_bp.route('/api/buscar-horarios-disponibles-completo')
def api_buscar_horarios_disponibles_completo():
    """Búsqueda completa de horarios con todos los filtros.
    
    Parámetros GET (todos opcionales):
    - id_empleado: int
    - disponibilidad: string (Disponible, Ocupado, Bloqueado)
    - fecha_desde: YYYY-MM-DD
    - fecha_hasta: YYYY-MM-DD
    - rol: string
    """
    # Actualizar automáticamente los horarios vencidos antes de consultar
    actualizar_horarios_vencidos()
    
    id_empleado = request.args.get('id_empleado')
    disponibilidad = request.args.get('disponibilidad')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    rol = request.args.get('rol')
    
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Construir query según el filtro de disponibilidad
        params = []
        
        # Para Ocupado y Bloqueado: buscar directamente en PROGRAMACION
        # ya que estas programaciones pueden no coincidir exactamente con un HORARIO
        if disponibilidad in ['Ocupado', 'Bloqueado']:
            query = """
                SELECT 
                    p.id_horario,
                    COALESCE(h.id_empleado, 0) as id_empleado,
                    p.fecha,
                    TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                    TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                    p.estado as disponibilidad,
                    COALESCE(h.activo, 1) as activo,
                    CONCAT(COALESCE(e.nombres, 'N/A'), ' ', COALESCE(e.apellidos, '')) as profesional,
                    COALESCE(es.nombre, '-') as especialidad,
                    COALESCE(r.nombre, '-') as rol,
                    p.id_programacion
                FROM PROGRAMACION p
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
                LEFT JOIN ROL r ON e.id_rol = r.id_rol
                WHERE p.estado = %s
            """
            params.append(disponibilidad)
            
            # Filtros adicionales
            if id_empleado:
                query += " AND h.id_empleado = %s"
                params.append(int(id_empleado))
            
            if fecha_desde:
                query += " AND p.fecha >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND p.fecha <= %s"
                params.append(fecha_hasta)
            
            if rol:
                query += " AND r.nombre = %s"
                params.append(rol)
            
            query += " ORDER BY p.id_programacion ASC"
        
        else:
            # Para Disponible o sin filtro: buscar desde HORARIO
            query = """
                SELECT 
                    h.id_horario,
                    h.id_empleado,
                    h.fecha,
                    TIME_FORMAT(h.hora_inicio, '%%H:%%i') as hora_inicio,
                    TIME_FORMAT(h.hora_fin, '%%H:%%i') as hora_fin,
                    COALESCE(p.estado, 'Disponible') as disponibilidad,
                    h.activo,
                    CONCAT(e.nombres, ' ', e.apellidos) as profesional,
                    COALESCE(es.nombre, '-') as especialidad,
                    r.nombre as rol,
                    p.id_programacion
                FROM HORARIO h
                INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
                LEFT JOIN ROL r ON e.id_rol = r.id_rol
                LEFT JOIN PROGRAMACION p ON p.id_horario = h.id_horario 
                    AND p.fecha = h.fecha 
                    AND p.hora_inicio = h.hora_inicio
                WHERE h.activo = 1
            """
            
            # Filtros adicionales
            if id_empleado:
                query += " AND h.id_empleado = %s"
                params.append(int(id_empleado))
            
            if disponibilidad == 'Disponible':
                query += " AND COALESCE(p.estado, 'Disponible') = 'Disponible'"
            
            if fecha_desde:
                query += " AND h.fecha >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND h.fecha <= %s"
                params.append(fecha_hasta)
            
            if rol:
                query += " AND r.nombre = %s"
                params.append(rol)
            
            query += " ORDER BY h.id_horario ASC"
        
        print(f"\n[DEBUG api_buscar_horarios_disponibles_completo]")
        print(f"  Filtro disponibilidad: '{disponibilidad}'")
        print(f"  Estrategia: {'Buscar en PROGRAMACION directamente' if disponibilidad in ['Ocupado', 'Bloqueado'] else 'Buscar en HORARIO con LEFT JOIN'}")
        print(f"  Parámetros: {params}")
        print(f"\n[DEBUG] Query completa:")
        print(query)
        print()
        
        cursor.execute(query, params)
        horarios = cursor.fetchall()
        
        print(f"  Registros encontrados: {len(horarios)}")
        if horarios and len(horarios) > 0:
            print(f"  Primeros 3 registros:")
            for h in horarios[:3]:
                print(f"    - id_horario={h.get('id_horario')}, disponibilidad={h.get('disponibilidad')}, fecha={h.get('fecha')}")
        
        # Convertir fechas a string
        for h in horarios:
            if h.get('fecha'):
                h['fecha'] = h['fecha'].strftime('%Y-%m-%d')
        
        return jsonify({'horarios': horarios})
        
    except Exception as e:
        print(f"Error en búsqueda completa de horarios: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'horarios': []}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@reservas_bp.route('/api/reservas-por-programacion')
def api_reservas_por_programacion():
    """Obtiene las reservas asociadas a una programación específica.
    
    Parámetros GET:
    - id_horario: int (requerido)
    - fecha: YYYY-MM-DD (requerido)
    - hora_inicio: HH:MM (requerido)
    """
    id_horario = request.args.get('id_horario')
    fecha = request.args.get('fecha')
    hora_inicio = request.args.get('hora_inicio')
    
    if not id_horario or not fecha or not hora_inicio:
        return jsonify({'error': 'Parámetros id_horario, fecha y hora_inicio son requeridos'}), 400
    
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Buscar la programación primero
        query_programacion = """
            SELECT 
                p.id_programacion,
                p.id_horario,
                p.fecha,
                TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                p.estado,
                p.cupo_disponible,
                CONCAT(e.nombres, ' ', e.apellidos) as profesional,
                COALESCE(es.nombre, '-') as especialidad
            FROM PROGRAMACION p
            INNER JOIN HORARIO h ON p.id_horario = h.id_horario
            INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
            LEFT JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
            WHERE p.id_horario = %s 
                AND p.fecha = %s 
                AND TIME_FORMAT(p.hora_inicio, '%%H:%%i') = %s
        """
        
        cursor.execute(query_programacion, (id_horario, fecha, hora_inicio))
        programacion = cursor.fetchone()
        
        if not programacion:
            return jsonify({'error': 'Programación no encontrada', 'reservas': []}), 404
        
        # Convertir fecha a string
        if programacion.get('fecha'):
            programacion['fecha'] = programacion['fecha'].strftime('%Y-%m-%d')
        
        # Buscar reservas asociadas a esta programación
        query_reservas = """
            SELECT 
                r.id_reserva,
                r.id_paciente,
                CONCAT(pac.nombres, ' ', pac.apellidos) as paciente,
                pac.documento,
                r.estado as estado_reserva,
                DATE_FORMAT(r.fecha_registro, '%%Y-%%m-%%d %%H:%%i:%%s') as fecha_registro,
                r.motivo_consulta,
                r.observaciones,
                s.nombre as servicio
            FROM RESERVA r
            INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
            LEFT JOIN SERVICIO s ON r.id_servicio = s.id_servicio
            WHERE r.id_programacion = %s
            ORDER BY r.fecha_registro DESC
        """
        
        cursor.execute(query_reservas, (programacion['id_programacion'],))
        reservas = cursor.fetchall()
        
        return jsonify({
            'programacion': programacion,
            'reservas': reservas,
            'total_reservas': len(reservas)
        })
        
    except Exception as e:
        print(f"Error al obtener reservas de programación: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'reservas': []}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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
    """Generar Nueva Reserva - Para empleados y pacientes"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    # Si es paciente, renderizar el formulario de paciente
    if session.get('tipo_usuario') == 'paciente':
        return render_template('RegistrarCitaPaciente.html')
    
    # Si es empleado, renderizar el formulario de empleado
    if session.get('tipo_usuario') == 'empleado':
        servicios = Servicio.obtener_todos()
        medicos = Empleado.obtener_medicos()
        programaciones = Programacion.obtener_todos()
        
        # Obtener tipos de servicio excluyendo Farmacia
        tipos_servicio = TipoServicio.obtener_todos()
        # Filtrar para excluir Farmacia (nombre puede ser 'Farmacia' o similar)
        tipos_servicio_filtrados = [t for t in tipos_servicio if t.get('nombre', '').lower() != 'farmacia']
        
        return render_template('GenerarReserva.html', 
                             servicios=servicios, 
                             medicos=medicos, 
                             programaciones=programaciones,
                             tipos_servicio=tipos_servicio_filtrados)
    
    # Si no es ni empleado ni paciente, redirigir al home
    return redirect(url_for('home'))


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
        
        # Serializar para JSON (convertir datetime y timedelta)
        reservas_serializadas = []
        for r in reservas:
            r_dict = dict(r)
            
            # Convertir fecha_registro y fecha_cita
            for fecha_key in ['fecha_registro', 'fecha_cita']:
                if r_dict.get(fecha_key) and hasattr(r_dict[fecha_key], 'isoformat'):
                    r_dict[fecha_key] = r_dict[fecha_key].isoformat()
            
            # Convertir timedelta a HH:MM para hora_registro, hora_inicio, hora_fin
            for hora_key in ['hora_registro', 'hora_inicio', 'hora_fin']:
                if r_dict.get(hora_key):
                    if isinstance(r_dict[hora_key], timedelta):
                        total_seconds = int(r_dict[hora_key].total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        r_dict[hora_key] = f"{hours:02d}:{minutes:02d}"
                    else:
                        r_dict[hora_key] = str(r_dict[hora_key])[:5]
            
            reservas_serializadas.append(r_dict)
        
        return jsonify({'reservas': reservas_serializadas})
    except Exception as e:
        print(f"[API reservas-por-paciente] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@reservas_bp.route('/api/reprogramar-reserva', methods=['POST'])
def api_reprogramar_reserva_old():
    """Reprograma una reserva existente a un nuevo horario (versión antigua).

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
            cursor.execute(sql_ins, (fecha, hora_inicio, hora_fin, 'Disponible', id_servicio, id_horario))
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

        # Crear notificación para el paciente sobre la reprogramación
        try:
            id_paciente = reserva.get('id_paciente')
            estado_actual = reserva.get('estado', 'Confirmada')
            
            # Notificación inmediata de reprogramación
            try:
                Notificacion.crear('Reserva Reprogramada', f'Su reserva fue reprogramada para {fecha} a las {hora_inicio}', 'reprogramacion', id_paciente, id_reserva)
            except Exception as e:
                print(f"Error creando notificación reprogramacion inmediata: {e}")
            
            # Notificación del estado actual
            try:
                Notificacion.crear_notificacion_estado_reserva(id_paciente, id_reserva, estado_actual)
            except Exception as e:
                print(f"Error creando notificación de estado tras reprogramación: {e}")
            
            # Programar recordatorio en la nueva fecha
            try:
                Notificacion.crear_recordatorio_cita(id_paciente, id_reserva, fecha, hora_inicio)
            except Exception as e:
                print(f"Error programando recordatorio tras reprogramacion: {e}")
        except Exception as e:
            print(f"Error procesando notificaciones tras reprogramacion: {e}")

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
    id_programacion = data.get('id_programacion')
    id_servicio = data.get('id_servicio')

    if not id_paciente:
        return jsonify({'error': 'id_paciente es requerido'}), 400
    if not id_programacion:
        return jsonify({'error': 'id_programacion es requerido'}), 400
    if not id_servicio:
        return jsonify({'error': 'id_servicio es requerido'}), 400

    conexion = None
    try:
        # Verificar que la programación existe y está disponible
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.id_programacion, p.fecha, p.hora_inicio, p.hora_fin, p.estado
                FROM PROGRAMACION p
                WHERE p.id_programacion = %s
            """, (id_programacion,))
            programacion = cursor.fetchone()
            
            if not programacion:
                return jsonify({'error': 'Programación no encontrada'}), 404
            
            if programacion.get('estado') != 'Disponible':
                return jsonify({'error': 'Esta programación ya no está disponible'}), 400
            
            fecha = programacion.get('fecha')
            hora_inicio = programacion.get('hora_inicio')
            hora_fin = programacion.get('hora_fin')
            
            # Actualizar estado de PROGRAMACION a 'Ocupado'
            cursor.execute("""
                UPDATE PROGRAMACION 
                SET estado = 'Ocupado' 
                WHERE id_programacion = %s
            """, (id_programacion,))
            conexion.commit()

        # Crear reserva con tipo = 1 (por defecto)
        res = Reserva.crear(1, int(id_paciente), int(id_programacion))
        if res.get('error'):
            # Revertir estado de programación
            with conexion.cursor() as cursor:
                cursor.execute("""
                    UPDATE PROGRAMACION 
                    SET estado = 'Disponible' 
                    WHERE id_programacion = %s
                """, (id_programacion,))
                conexion.commit()
            return jsonify({'error': res['error']}), 500
        
        id_reserva = res.get('id_reserva')
        
        # Determinar el tipo de servicio y crear el registro correspondiente
        conexion_tipo = obtener_conexion()
        try:
            with conexion_tipo.cursor() as cursor:
                # Obtener el tipo de servicio
                cursor.execute("""
                    SELECT ts.nombre 
                    FROM SERVICIO s 
                    INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio 
                    WHERE s.id_servicio = %s
                """, (id_servicio,))
                tipo_servicio_data = cursor.fetchone()
                tipo_servicio_nombre = tipo_servicio_data.get('nombre', '').lower() if tipo_servicio_data else ''
                
                # Crear registro según el tipo de servicio
                if 'consulta' in tipo_servicio_nombre or 'cita' in tipo_servicio_nombre:
                    # Crear CITA
                    cursor.execute("""
                        INSERT INTO CITA (fecha_cita, hora_inicio, hora_fin, estado, id_reserva)
                        VALUES (%s, %s, %s, 'Pendiente', %s)
                    """, (fecha, hora_inicio, hora_fin, id_reserva))
                    print(f"✓ CITA creada para reserva {id_reserva}")
                    
                elif 'examen' in tipo_servicio_nombre or 'diagnóstico' in tipo_servicio_nombre or 'diagnostico' in tipo_servicio_nombre:
                    # Crear EXAMEN
                    cursor.execute("""
                        INSERT INTO EXAMEN (fecha_examen, hora_inicio, estado, id_reserva)
                        VALUES (%s, %s, 'Pendiente', %s)
                    """, (fecha, hora_inicio, id_reserva))
                    print(f"✓ EXAMEN creado para reserva {id_reserva}")
                    
                elif 'quirúrgico' in tipo_servicio_nombre or 'quirurgico' in tipo_servicio_nombre or 'operación' in tipo_servicio_nombre or 'operacion' in tipo_servicio_nombre:
                    # Crear OPERACION
                    cursor.execute("""
                        INSERT INTO OPERACION (fecha_operacion, hora_inicio, hora_fin, id_reserva)
                        VALUES (%s, %s, %s, %s)
                    """, (fecha, hora_inicio, hora_fin, id_reserva))
                    print(f"✓ OPERACION creada para reserva {id_reserva}")
                else:
                    print(f"⚠ Tipo de servicio '{tipo_servicio_nombre}' no reconocido para crear registro específico")
                
                conexion_tipo.commit()
        except Exception as e:
            print(f"Error creando registro de tipo específico: {e}")
            conexion_tipo.rollback()
        finally:
            conexion_tipo.close()
        
        # Obtener el estado de la reserva recién creada (normalmente será 'Confirmada')
        conexion_notif = obtener_conexion()
        try:
            with conexion_notif.cursor() as cursor:
                cursor.execute("SELECT estado FROM RESERVA WHERE id_reserva = %s", (id_reserva,))
                reserva_data = cursor.fetchone()
                estado_reserva = reserva_data.get('estado', 'Confirmada') if reserva_data else 'Confirmada'
        except Exception as e:
            print(f"Error obteniendo estado de reserva: {e}")
            estado_reserva = 'Confirmada'
        finally:
            try:
                conexion_notif.close()
            except:
                pass
        
        # Crear notificaciones
        try:
            # 1. Notificación de confirmación de creación
            Notificacion.crear_confirmacion_reserva(id_paciente, id_reserva)
        except Exception as e:
            print(f"Error creando notificación de confirmación (API): {e}")
        
        try:
            # 2. Notificación del estado actual de la reserva
            Notificacion.crear_notificacion_estado_reserva(id_paciente, id_reserva, estado_reserva)
        except Exception as e:
            print(f"Error creando notificación de estado (API): {e}")
        
        try:
            # 3. Programar recordatorio para la fecha de la cita (se mostrará 24h antes)
            Notificacion.crear_recordatorio_cita(id_paciente, id_reserva, fecha, hora_inicio)
        except Exception as e:
            print(f"Error programando recordatorio de cita (API): {e}")
        
        # Enviar EMAILS de confirmación de reserva
        try:
            with obtener_conexion() as conexion_email:
                with conexion_email.cursor() as cursor:
                    # Obtener información completa de la reserva
                    cursor.execute("""
                        SELECT 
                            r.id_reserva,
                            p.fecha,
                            TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio,
                            TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin,
                            COALESCE(serv.nombre, 'Consulta Médica') as servicio,
                            CONCAT(pac.nombres, ' ', pac.apellidos) as nombre_paciente,
                            pac.correo as paciente_email,
                            CONCAT(emp.nombres, ' ', emp.apellidos) as nombre_medico,
                            emp.correo as medico_email,
                            esp.nombre as especialidad
                        FROM RESERVA r
                        INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                        LEFT JOIN SERVICIO serv ON prog.id_servicio = serv.id_servicio
                        INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                        LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                        LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                        LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                        WHERE r.id_reserva = %s
                    """, (id_reserva,))
                    info_email = cursor.fetchone()
                    
                    if info_email:
                        fecha_formateada = info_email['fecha'].strftime('%d de %B de %Y') if isinstance(info_email['fecha'], (date, datetime)) else str(info_email['fecha'])
                        
                        # Email al paciente
                        if info_email.get('paciente_email'):
                            resultado = enviar_email_reserva_creada(
                                paciente_email=info_email['paciente_email'],
                                paciente_nombre=info_email['nombre_paciente'],
                                fecha=fecha_formateada,
                                hora_inicio=info_email['hora_inicio'],
                                hora_fin=info_email['hora_fin'],
                                medico_nombre=info_email['nombre_medico'] or 'Por asignar',
                                especialidad=info_email['especialidad'] or 'General',
                                servicio=info_email['servicio'],
                                id_reserva=info_email['id_reserva']
                            )
                            if resultado['success']:
                                print(f"📧✅ Email de confirmación enviado al paciente: {info_email['paciente_email']}")
                            else:
                                print(f"📧⚠️ No se pudo enviar email al paciente: {resultado['message']}")
                        
                        # Email al médico
                        if info_email.get('medico_email') and info_email.get('nombre_medico'):
                            resultado = enviar_email_reserva_creada_medico(
                                medico_email=info_email['medico_email'],
                                medico_nombre=info_email['nombre_medico'],
                                paciente_nombre=info_email['nombre_paciente'],
                                fecha=fecha_formateada,
                                hora_inicio=info_email['hora_inicio'],
                                hora_fin=info_email['hora_fin'],
                                servicio=info_email['servicio'],
                                id_reserva=info_email['id_reserva']
                            )
                            if resultado['success']:
                                print(f"📧✅ Email de notificación enviado al médico: {info_email['medico_email']}")
                            else:
                                print(f"📧⚠️ No se pudo enviar email al médico: {resultado['message']}")
                    
        except Exception as e:
            print(f"❌ Error enviando emails de confirmación: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({'success': True, 'id_reserva': id_reserva}), 201

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

@reservas_bp.route('/solicitudes-cancelacion')
def solicitudes_cancelacion():
    """Gestionar Solicitudes de Cancelación"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    # Permitir acceso a trabajadores, administradores y empleados
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario not in ['empleado', 'trabajador', 'administrador']:
        return redirect(url_for('home'))
    
    return render_template('Cancelar.html')

@reservas_bp.route('/gestionar-cancelaciones')
def gestionar_cancelaciones():
    """Gestionar Cancelaciones"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Obtener lista de médicos para el filtro
    try:
        from models.empleado import Empleado
        medicos = Empleado.obtener_empleados_rol('Medico')
    except Exception as e:
        print(f"Error al obtener médicos: {e}")
        medicos = []

    return render_template('GestionarCancelaciones.html', medicos=medicos)


@reservas_bp.route('/api/solicitudes-reprogramacion')
def api_solicitudes_reprogramacion():
    """API para obtener solicitudes de reprogramación pendientes"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    s.id_solicitud,
                    s.id_reserva,
                    s.estado as estado_solicitud,
                    s.motivo,
                    s.fecha_solicitud,
                    r.estado as estado_reserva,
                    CONCAT(pac.nombres, ' ', pac.apellidos) as paciente_nombre,
                    pac.documento_identidad as paciente_dni,
                    p_actual.fecha as fecha_actual,
                    TIME_FORMAT(p_actual.hora_inicio, '%H:%i') as hora_inicio_actual,
                    TIME_FORMAT(p_actual.hora_fin, '%H:%i') as hora_fin_actual,
                    srv.nombre as servicio_nombre,
                    CONCAT(emp.nombres, ' ', emp.apellidos) as medico_nombre,
                    esp.nombre as especialidad,
                    (SELECT COUNT(*) FROM SOLICITUD s2 
                     WHERE s2.id_reserva = s.id_reserva 
                     AND s2.estado = 'Aprobada') as num_reprogramaciones
                FROM SOLICITUD s
                INNER JOIN RESERVA r ON s.id_reserva = r.id_reserva
                INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                INNER JOIN PROGRAMACION p_actual ON r.id_programacion = p_actual.id_programacion
                INNER JOIN SERVICIO srv ON p_actual.id_servicio = srv.id_servicio
                LEFT JOIN HORARIO h ON p_actual.id_horario = h.id_horario
                LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                WHERE s.estado = 'Pendiente'
                AND s.nueva_programacion_id IS NOT NULL
                ORDER BY s.fecha_solicitud DESC
            """
            cursor.execute(sql)
            solicitudes = cursor.fetchall()
            
            print(f"📊 Total de solicitudes de REPROGRAMACIÓN encontradas: {len(solicitudes)}")
            
            # Formatear fechas
            for sol in solicitudes:
                if sol.get('fecha_solicitud'):
                    sol['fecha_solicitud'] = sol['fecha_solicitud'].strftime('%Y-%m-%d %H:%M:%S')
                if sol.get('fecha_actual'):
                    sol['fecha_actual'] = sol['fecha_actual'].strftime('%Y-%m-%d')
            
            return jsonify({'solicitudes': solicitudes})
            
    except Exception as e:
        print(f"[API] Error al obtener solicitudes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener solicitudes: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/estadisticas-reprogramacion')
def api_estadisticas_reprogramacion():
    """API para obtener estadísticas de solicitudes de reprogramación"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        from datetime import date
        hoy = date.today()
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Contar solicitudes pendientes de REPROGRAMACIÓN
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM SOLICITUD
                WHERE estado = 'Pendiente'
                AND nueva_programacion_id IS NOT NULL
            """)
            pendientes = cursor.fetchone()['total']
            
            # Contar reprogramadas hoy (solicitudes aprobadas de REPROGRAMACIÓN)
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM SOLICITUD
                WHERE estado = 'Aprobada'
                AND DATE(fecha_respuesta) = %s
                AND nueva_programacion_id IS NOT NULL
            """, (hoy,))
            reprogramadas_hoy = cursor.fetchone()['total']
            
            return jsonify({
                'pendientes': pendientes,
                'reprogramadas_hoy': reprogramadas_hoy
            })
            
    except Exception as e:
        print(f"[API] Error al obtener estadísticas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/aprobar-reprogramacion', methods=['POST'])
def api_aprobar_reprogramacion():
    """API para aprobar una solicitud de reprogramación"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    data = request.get_json()
    id_solicitud = data.get('id_solicitud')
    nueva_programacion_id = data.get('nueva_programacion_id')
    respuesta = data.get('respuesta', 'Solicitud aprobada')
    
    if not id_solicitud or not nueva_programacion_id:
        return jsonify({'error': 'Faltan parámetros requeridos'}), 400
    
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la solicitud existe y está pendiente
            cursor.execute("""
                SELECT s.*, r.id_programacion as programacion_anterior
                FROM SOLICITUD s
                INNER JOIN RESERVA r ON s.id_reserva = r.id_reserva
                WHERE s.id_solicitud = %s AND s.estado = 'Pendiente'
            """, (id_solicitud,))
            solicitud = cursor.fetchone()
            
            if not solicitud:
                return jsonify({'error': 'Solicitud no encontrada o ya procesada'}), 404
            
            # Contar reprogramaciones aprobadas para esta reserva
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM SOLICITUD
                WHERE id_reserva = %s AND estado = 'Aprobada'
            """, (solicitud['id_reserva'],))
            result = cursor.fetchone()
            num_reprogramaciones = result['total'] if result else 0
            
            # Validar máximo 2 reprogramaciones
            if num_reprogramaciones >= 2:
                return jsonify({'error': 'Esta reserva ya ha sido reprogramada el máximo de veces permitido (2)'}), 400
            
            # Verificar que la nueva programación está disponible
            cursor.execute("""
                SELECT estado FROM PROGRAMACION
                WHERE id_programacion = %s
            """, (nueva_programacion_id,))
            prog = cursor.fetchone()
            
            if not prog:
                return jsonify({'error': 'Programación no encontrada'}), 404
            
            if prog['estado'] != 'Disponible':
                return jsonify({'error': 'La programación seleccionada no está disponible'}), 400
            
            # Actualizar la solicitud
            cursor.execute("""
                UPDATE SOLICITUD
                SET estado = 'Aprobada',
                    nueva_programacion_id = %s,
                    respuesta = %s,
                    fecha_respuesta = NOW()
                WHERE id_solicitud = %s
            """, (nueva_programacion_id, respuesta, id_solicitud))
            
            # Actualizar la reserva con la nueva programación
            cursor.execute("""
                UPDATE RESERVA
                SET id_programacion = %s
                WHERE id_reserva = %s
            """, (nueva_programacion_id, solicitud['id_reserva']))
            
            # Liberar la programación anterior
            cursor.execute("""
                UPDATE PROGRAMACION
                SET estado = 'Disponible'
                WHERE id_programacion = %s
            """, (solicitud['programacion_anterior'],))
            
            # Ocupar la nueva programación
            cursor.execute("""
                UPDATE PROGRAMACION
                SET estado = 'Ocupado'
                WHERE id_programacion = %s
            """, (nueva_programacion_id,))
            
            conexion.commit()
            
            # Obtener información completa para notificaciones y emails
            try:
                cursor.execute("""
                    SELECT 
                        r.id_paciente,
                        r.id_reserva,
                        p_ant.fecha as fecha_anterior,
                        TIME_FORMAT(p_ant.hora_inicio, '%H:%i') as hora_inicio_anterior,
                        TIME_FORMAT(p_ant.hora_fin, '%H:%i') as hora_fin_anterior,
                        p_nueva.fecha as fecha_nueva,
                        TIME_FORMAT(p_nueva.hora_inicio, '%H:%i') as hora_inicio_nueva,
                        TIME_FORMAT(p_nueva.hora_fin, '%H:%i') as hora_fin_nueva,
                        COALESCE(serv.nombre, 'Consulta Médica') as servicio,
                        CONCAT(pac.nombres, ' ', pac.apellidos) as nombre_paciente,
                        pac.correo as paciente_email,
                        CONCAT(emp.nombres, ' ', emp.apellidos) as nombre_medico,
                        emp.correo as medico_email,
                        esp.nombre as especialidad,
                        s.motivo as motivo_reprogramacion
                    FROM RESERVA r
                    INNER JOIN PROGRAMACION p_nueva ON r.id_programacion = p_nueva.id_programacion
                    INNER JOIN PROGRAMACION p_ant ON p_ant.id_programacion = %s
                    LEFT JOIN SERVICIO serv ON p_nueva.id_servicio = serv.id_servicio
                    INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                    LEFT JOIN HORARIO h ON p_nueva.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO emp ON h.id_empleado = emp.id_empleado
                    LEFT JOIN ESPECIALIDAD esp ON emp.id_especialidad = esp.id_especialidad
                    INNER JOIN SOLICITUD s ON s.id_reserva = r.id_reserva AND s.id_solicitud = %s
                    WHERE r.id_reserva = %s
                """, (solicitud['programacion_anterior'], id_solicitud, solicitud['id_reserva']))
                info = cursor.fetchone()
                
                if info:
                    # Crear notificación en el sistema
                    Notificacion.crear(
                        info['id_paciente'],
                        'reprogramacion_aprobada',
                        f'Su solicitud de reprogramación para la reserva #{info["id_reserva"]} ha sido aprobada. Nueva fecha: {info["fecha_nueva"]} a las {info["hora_inicio_nueva"]}.',
                        f'/paciente/mis-reservas'
                    )
                    print(f"✅ Notificación de reprogramación enviada al paciente")
                    
                    # Enviar EMAIL al paciente
                    if info.get('paciente_email'):
                        fecha_ant_format = info['fecha_anterior'].strftime('%d de %B de %Y') if isinstance(info['fecha_anterior'], (date, datetime)) else str(info['fecha_anterior'])
                        fecha_nueva_format = info['fecha_nueva'].strftime('%d de %B de %Y') if isinstance(info['fecha_nueva'], (date, datetime)) else str(info['fecha_nueva'])
                        
                        resultado = enviar_email_reprogramacion_aprobada(
                            paciente_email=info['paciente_email'],
                            paciente_nombre=info['nombre_paciente'],
                            fecha_anterior=fecha_ant_format,
                            hora_inicio_anterior=info['hora_inicio_anterior'],
                            hora_fin_anterior=info['hora_fin_anterior'],
                            fecha_nueva=fecha_nueva_format,
                            hora_inicio_nueva=info['hora_inicio_nueva'],
                            hora_fin_nueva=info['hora_fin_nueva'],
                            medico_nombre=info['nombre_medico'] or 'Por asignar',
                            especialidad=info['especialidad'] or 'General',
                            servicio=info['servicio'],
                            motivo_reprogramacion=info['motivo_reprogramacion'],
                            comentario_admin=respuesta if respuesta and respuesta != 'Solicitud aprobada' else None
                        )
                        if resultado['success']:
                            print(f"📧✅ Email de reprogramación enviado al paciente: {info['paciente_email']}")
                        else:
                            print(f"📧⚠️ No se pudo enviar email al paciente: {resultado['message']}")
                    
                    # Enviar EMAIL al médico
                    if info.get('medico_email') and info.get('nombre_medico'):
                        fecha_ant_format = info['fecha_anterior'].strftime('%d de %B de %Y') if isinstance(info['fecha_anterior'], (date, datetime)) else str(info['fecha_anterior'])
                        fecha_nueva_format = info['fecha_nueva'].strftime('%d de %B de %Y') if isinstance(info['fecha_nueva'], (date, datetime)) else str(info['fecha_nueva'])
                        
                        resultado = enviar_email_reprogramacion_medico(
                            medico_email=info['medico_email'],
                            medico_nombre=info['nombre_medico'],
                            paciente_nombre=info['nombre_paciente'],
                            fecha_anterior=fecha_ant_format,
                            hora_inicio_anterior=info['hora_inicio_anterior'],
                            hora_fin_anterior=info['hora_fin_anterior'],
                            fecha_nueva=fecha_nueva_format,
                            hora_inicio_nueva=info['hora_inicio_nueva'],
                            hora_fin_nueva=info['hora_fin_nueva'],
                            servicio=info['servicio'],
                            motivo_reprogramacion=info['motivo_reprogramacion']
                        )
                        if resultado['success']:
                            print(f"📧✅ Email de reprogramación enviado al médico: {info['medico_email']}")
                        else:
                            print(f"📧⚠️ No se pudo enviar email al médico: {resultado['message']}")
                
            except Exception as e:
                print(f"❌ Error enviando notificaciones/emails de reprogramación: {e}")
                import traceback
                traceback.print_exc()
            
            # Enviar notificación al paciente (código antiguo - ya incluido arriba)
            try:
                cursor.execute("""
                    SELECT id_paciente FROM RESERVA WHERE id_reserva = %s
                """, (solicitud['id_reserva'],))
                paciente_data = cursor.fetchone()
                if paciente_data:
                    pass  # Ya se envió arriba con más información
            except Exception as e:
                print(f"Error en verificación de paciente: {e}")
            
            return jsonify({'message': 'Reprogramación aprobada exitosamente. Se enviaron notificaciones y emails.'})
            
    except Exception as e:
        print(f"[API] Error al aprobar reprogramación: {e}")
        import traceback
        traceback.print_exc()
        try:
            conexion.rollback()
        except:
            pass
        return jsonify({'error': f'Error al aprobar reprogramación: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/rechazar-reprogramacion', methods=['POST'])
def api_rechazar_reprogramacion():
    """API para rechazar una solicitud de reprogramación"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    data = request.get_json()
    id_solicitud = data.get('id_solicitud')
    respuesta = data.get('respuesta', 'Solicitud rechazada')
    
    if not id_solicitud:
        return jsonify({'error': 'Falta id_solicitud'}), 400
    
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la solicitud existe y está pendiente
            cursor.execute("""
                SELECT s.*, r.id_paciente
                FROM SOLICITUD s
                INNER JOIN RESERVA r ON s.id_reserva = r.id_reserva
                WHERE s.id_solicitud = %s AND s.estado = 'Pendiente'
            """, (id_solicitud,))
            solicitud = cursor.fetchone()
            
            if not solicitud:
                return jsonify({'error': 'Solicitud no encontrada o ya procesada'}), 404
            
            # Actualizar la solicitud
            cursor.execute("""
                UPDATE SOLICITUD
                SET estado = 'Rechazada',
                    respuesta = %s,
                    fecha_respuesta = NOW()
                WHERE id_solicitud = %s
            """, (respuesta, id_solicitud))
            
            conexion.commit()
            
            # Enviar notificación al paciente
            try:
                from models.notificacion import Notificacion
                Notificacion.crear(
                    solicitud['id_paciente'],
                    'reprogramacion_rechazada',
                    f'Su solicitud de reprogramación para la reserva #{solicitud["id_reserva"]} ha sido rechazada. Motivo: {respuesta}',
                    f'/paciente/mis-reservas'
                )
            except Exception as e:
                print(f"Error al crear notificación: {e}")
            
            return jsonify({'message': 'Solicitud rechazada'})
            
    except Exception as e:
        print(f"[API] Error al rechazar solicitud: {e}")
        import traceback
        traceback.print_exc()
        try:
            conexion.rollback()
        except:
            pass
        return jsonify({'error': f'Error al rechazar solicitud: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/reservas-activas')
def api_reservas_activas():
    """Obtiene todas las reservas con estado 'Confirmada' (listas para gestionar cancelaciones)
    Parámetros GET opcionales:
    - dni: documento de identidad del paciente
    - nombre: nombre o apellido del paciente
    - id_empleado: ID del médico
    """
    # Verificar autenticación
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    dni = request.args.get('dni', '').strip()
    nombre = request.args.get('nombre', '').strip()
    id_empleado = request.args.get('id_empleado', '').strip()

    # Validar formato de DNI si se proporciona
    if dni and (not dni.isdigit() or len(dni) != 8):
        return jsonify({'error': 'DNI inválido. Debe contener 8 dígitos'}), 400

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Query base para obtener reservas confirmadas
            sql_base = """
                SELECT r.id_reserva,
                       r.estado,
                       DATE_FORMAT(r.fecha_registro, '%%Y-%%m-%%d') as fecha_registro,
                       r.id_programacion,
                       CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                       p.documento_identidad,
                       DATE_FORMAT(prog.fecha, '%%Y-%%m-%%d') as fecha_cita,
                       TIME_FORMAT(prog.hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(prog.hora_fin, '%%H:%%i') as hora_fin,
                       s.nombre as servicio,
                       CONCAT(e.nombres, ' ', e.apellidos) as nombre_empleado,
                       COALESCE(es.nombre, '-') as especialidad,
                       h.id_empleado
                FROM RESERVA r
                INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
                INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                LEFT JOIN HORARIO h ON prog.id_horario = h.id_horario
                LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
                WHERE r.estado = 'Confirmada'
            """
            
            params = []
            
            if dni:
                sql_base += " AND p.documento_identidad = %s"
                params.append(dni)
            
            if nombre:
                sql_base += " AND (LOWER(p.nombres) LIKE %s OR LOWER(p.apellidos) LIKE %s)"
                nombre_like = f"%{nombre.lower()}%"
                params.append(nombre_like)
                params.append(nombre_like)
            
            if id_empleado:
                sql_base += " AND h.id_empleado = %s"
                params.append(int(id_empleado))
            
            sql_base += " ORDER BY prog.fecha ASC, prog.hora_inicio ASC"
            
            if params:
                cursor.execute(sql_base, tuple(params))
            else:
                cursor.execute(sql_base)

            reservas = cursor.fetchall()

            # Convertir a formato JSON
            resultado = []
            for reserva in reservas:
                resultado.append({
                    'id_reserva': reserva.get('id_reserva'),
                    'estado': reserva.get('estado'),
                    'nombre_paciente': reserva.get('nombre_paciente'),
                    'documento_identidad': reserva.get('documento_identidad'),
                    'fecha_cita': reserva.get('fecha_cita'),
                    'hora_inicio': reserva.get('hora_inicio'),
                    'hora_fin': reserva.get('hora_fin'),
                    'servicio': reserva.get('servicio'),
                    'nombre_empleado': reserva.get('nombre_empleado') or 'N/A',
                    'especialidad': reserva.get('especialidad'),
                    'id_programacion': reserva.get('id_programacion'),
                    'fecha_registro': reserva.get('fecha_registro')
                })

            return jsonify({'reservas': resultado})

    except Exception as e:
        print(f"Error al obtener reservas activas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener reservas: {str(e)}'}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


# NOTA: La función api_cancelar_reserva fue reemplazada por una versión mejorada
# en la línea ~435 que utiliza parámetros de ruta en lugar de JSON body
# Nueva ruta: /api/cancelar-reserva/<int:id_reserva>


# ========== RUTAS PARA PACIENTES ==========

@reservas_bp.route('/paciente/nueva-cita')
def paciente_nueva_cita():
    """Vista para que pacientes registren nuevas citas"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('RegistrarCitaPaciente.html')


@reservas_bp.route('/paciente/nuevo-examen')
def paciente_nuevo_examen():
    """Vista para que pacientes registren nuevos exámenes"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('RegistrarExamenPaciente.html')


@reservas_bp.route('/api/servicios-examen')
def api_servicios_examen():
    """Retorna todos los servicios de tipo Examen (tipo_servicio = 4)"""
    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT s.id_servicio, s.nombre, s.descripcion, s.id_especialidad,
                       e.nombre as nombre_especialidad
                FROM SERVICIO s
                LEFT JOIN ESPECIALIDAD e ON s.id_especialidad = e.id_especialidad
                WHERE s.id_tipo_servicio = 4 
                AND s.estado = 'Activo'
                ORDER BY 
                    CASE WHEN s.id_especialidad IS NULL THEN 0 ELSE 1 END,
                    s.nombre
            """
            cursor.execute(sql)
            servicios = cursor.fetchall()
            
            servicios_lista = []
            for servicio in servicios:
                servicios_lista.append({
                    'id_servicio': servicio['id_servicio'],
                    'nombre': servicio['nombre'],
                    'descripcion': servicio['descripcion'],
                    'id_especialidad': servicio['id_especialidad'],
                    'nombre_especialidad': servicio['nombre_especialidad']
                })
            
            return jsonify({
                'success': True,
                'servicios': servicios_lista
            })
            
    except Exception as e:
        print(f"[API servicios-examen] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error al obtener servicios de examen'}), 500
    finally:
        if conexion:
            conexion.close()


@reservas_bp.route('/api/especialidades-publicas')
def api_especialidades_publicas():
    """Retorna todas las especialidades activas (endpoint público para pacientes)"""
    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT id_especialidad, nombre, descripcion
                FROM ESPECIALIDAD 
                WHERE estado = 'activo'
                ORDER BY nombre
            """
            cursor.execute(sql)
            especialidades = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'especialidades': especialidades
            })
            
    except Exception as e:
        print(f"[API especialidades-publicas] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error al obtener especialidades'}), 500
    finally:
        if conexion:
            conexion.close()


@reservas_bp.route('/api/horarios-disponibles-examen')
def api_horarios_disponibles_examen():
    """Retorna fechas y horas disponibles para exámenes (sin restricción de empleado/especialidad)"""
    conexion = None
    try:
        fecha_str = request.args.get('fecha')
        
        if not fecha_str:
            return jsonify({'error': 'Fecha es requerida'}), 400
        
        # Validar formato de fecha
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        # Validar que la fecha no sea en el pasado
        if fecha_obj < datetime.now().date():
            return jsonify({'error': 'No se pueden agendar exámenes en fechas pasadas'}), 400
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Buscar horarios disponibles en esa fecha (de cualquier empleado)
            # Para exámenes, usamos horarios activos sin programación ocupada
            sql = """
                SELECT DISTINCT h.hora_inicio, h.hora_fin, h.id_horario
                FROM HORARIO h
                LEFT JOIN PROGRAMACION p ON p.id_horario = h.id_horario 
                    AND p.fecha = h.fecha 
                    AND p.hora_inicio = h.hora_inicio
                WHERE h.fecha = %s
                AND h.activo = 1
                AND (p.estado IS NULL OR p.estado = 'Disponible')
                ORDER BY h.hora_inicio
            """
            cursor.execute(sql, (fecha_str,))
            horarios = cursor.fetchall()
            
            if not horarios:
                return jsonify({
                    'success': True,
                    'horarios': [],
                    'mensaje': 'No hay horarios disponibles para esta fecha'
                })
            
            horarios_lista = []
            for horario in horarios:
                hora_inicio = horario['hora_inicio']
                hora_fin = horario['hora_fin']
                
                # Convertir a string si es necesario
                if isinstance(hora_inicio, timedelta):
                    total_seconds = int(hora_inicio.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    hora_inicio_str = f"{hours:02d}:{minutes:02d}"
                else:
                    hora_inicio_str = str(hora_inicio)[:5]
                
                if isinstance(hora_fin, timedelta):
                    total_seconds = int(hora_fin.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    hora_fin_str = f"{hours:02d}:{minutes:02d}"
                else:
                    hora_fin_str = str(hora_fin)[:5]
                
                horarios_lista.append({
                    'hora_inicio': hora_inicio_str,
                    'hora_fin': hora_fin_str
                })
            
            return jsonify({
                'success': True,
                'horarios': horarios_lista
            })
            
    except Exception as e:
        print(f"[API horarios-disponibles-examen] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error al obtener horarios disponibles'}), 500
    finally:
        if conexion:
            conexion.close()


@reservas_bp.route('/api/especialidades-activas')
def api_especialidades_activas():
    """Retorna todas las especialidades activas"""
    try:
        print("[API] Iniciando consulta de especialidades...")
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Buscar especialidades activas (con LIKE para ser case-insensitive)
            sql = """
                SELECT id_especialidad, nombre, estado, descripcion
                FROM ESPECIALIDAD
                WHERE estado = 'Activo'
                ORDER BY nombre
            """
            print(f"[API] Ejecutando SQL: {sql}")
            cursor.execute(sql)
            especialidades = cursor.fetchall()
            print(f"[API] Especialidades encontradas con filtro: {len(especialidades)}")
            
            # Si no hay especialidades activas, devolver todas
            if not especialidades or len(especialidades) == 0:
                print("[API] No se encontraron especialidades activas, buscando todas...")
                sql_all = """
                    SELECT id_especialidad, nombre, estado, descripcion
                    FROM ESPECIALIDAD
                    ORDER BY nombre
                """
                cursor.execute(sql_all)
                especialidades = cursor.fetchall()
                print(f"[API] Total especialidades sin filtro: {len(especialidades)}")

            print(f"[API] Retornando {len(especialidades)} especialidades")
            return jsonify({
                'especialidades': especialidades,
                'total': len(especialidades) if especialidades else 0
            })

    except Exception as e:
        print(f"[API] Error al obtener especialidades: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'especialidades': []}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


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
                WHERE s.estado = 'Activo'
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


@reservas_bp.route('/api/empleados-todos')
def api_empleados_todos():
    """Retorna TODOS los empleados activos con sus roles."""
    try:
        print(f"[API] Obteniendo todos los empleados activos")
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    e.id_empleado,
                    e.nombres,
                    e.apellidos,
                    e.documento_identidad,
                    e.sexo,
                    e.estado,
                    e.fotoPerfil,
                    COALESCE(esp.nombre, '-') as especialidad,
                    e.id_especialidad,
                    r.nombre as rol,
                    e.id_rol
                FROM EMPLEADO e
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                LEFT JOIN ROL r ON e.id_rol = r.id_rol
                WHERE e.estado = 'Activo'
                ORDER BY e.id_empleado ASC
            """
            cursor.execute(sql)
            
            empleados = cursor.fetchall()
            print(f"[API] Empleados encontrados: {len(empleados)}")

            return jsonify({
                'empleados': empleados,
                'total': len(empleados)
            })

    except Exception as e:
        print(f"[API] Error al obtener empleados: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'empleados': []}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/medicos-por-especialidad/<int:id_especialidad>')
def api_medicos_por_especialidad(id_especialidad):
    """Retorna médicos disponibles (id_rol=2) para una especialidad específica.
    Si id_especialidad es 0, retorna todos los médicos activos."""
    try:
        print(f"[API] Buscando médicos para especialidad ID: {id_especialidad}")
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            if id_especialidad == 0:
                # Retornar todos los médicos activos
                sql = """
                    SELECT 
                        e.id_empleado,
                        e.nombres,
                        e.apellidos,
                        e.documento_identidad,
                        e.sexo,
                        e.estado,
                        e.fotoPerfil,
                        COALESCE(esp.nombre, 'General') as especialidad,
                        e.id_especialidad
                    FROM EMPLEADO e
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE e.id_rol = 2 
                      AND e.estado = 'Activo'
                    ORDER BY e.id_empleado ASC
                """
                cursor.execute(sql)
            else:
                # Filtrar por especialidad específica
                sql = """
                    SELECT 
                        e.id_empleado,
                        e.nombres,
                        e.apellidos,
                        e.documento_identidad,
                        e.sexo,
                        e.estado,
                        e.fotoPerfil,
                        esp.nombre as especialidad,
                        esp.id_especialidad
                    FROM EMPLEADO e
                    INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE e.id_rol = 2 
                      AND e.id_especialidad = %s
                      AND e.estado = 'Activo'
                    ORDER BY e.nombres, e.apellidos
                """
                print(f"[API] Ejecutando SQL con id_especialidad={id_especialidad}")
                cursor.execute(sql, (id_especialidad,))
            
            medicos = cursor.fetchall()
            print(f"[API] Médicos encontrados: {len(medicos)}")
            
            for medico in medicos:
                print(f"[API] - {medico.get('nombres')} {medico.get('apellidos')} (ID: {medico.get('id_empleado')})")

            return jsonify({
                'medicos': medicos,
                'total': len(medicos)
            })

    except Exception as e:
        print(f"[API] Error al obtener médicos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'medicos': []}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@reservas_bp.route('/api/medicos-por-servicio/<int:id_servicio>')
def api_medicos_por_servicio(id_servicio):
    """Retorna médicos disponibles para un servicio específico"""
    conexion = None
    try:
        print(f"[API medicos-por-servicio] Buscando médicos para servicio ID: {id_servicio}")
        
        # Obtener servicio para verificar si existe
        servicio = Servicio.obtener_por_id(id_servicio)
        if not servicio:
            print(f"[API medicos-por-servicio] ERROR: Servicio {id_servicio} no encontrado")
            return jsonify({'error': 'Servicio no encontrado'}), 404

        id_especialidad = servicio.get('id_especialidad')
        print(f"[API medicos-por-servicio] Especialidad del servicio: {id_especialidad}")
        
        # Obtener médicos
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Si tiene especialidad, filtrar solo médicos de esa especialidad
            if id_especialidad:
                sql = """
                    SELECT e.id_empleado, 
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_completo,
                           esp.nombre as especialidad
                    FROM EMPLEADO e
                    INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE e.id_especialidad = %s
                    AND e.estado = 'Activo'
                    AND e.id_rol IN (2, 3)
                    ORDER BY e.apellidos, e.nombres
                """
                cursor.execute(sql, (id_especialidad,))
            else:
                # Sin especialidad: mostrar solo médicos generales (sin especialidad asignada)
                sql = """
                    SELECT e.id_empleado, 
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_completo,
                           'Médico General' as especialidad
                    FROM EMPLEADO e
                    WHERE e.id_especialidad IS NULL
                    AND e.estado = 'Activo'
                    AND e.id_rol IN (2, 3)
                    ORDER BY e.apellidos, e.nombres
                """
                cursor.execute(sql)
            
            medicos = cursor.fetchall()
            
            print(f"[API medicos-por-servicio] Médicos encontrados: {len(medicos)}")
            for medico in medicos:
                print(f"  - ID: {medico['id_empleado']}, Nombre: {medico.get('nombre_completo', 'N/A')}")

            return jsonify({
                'success': True,
                'medicos': medicos,
                'total': len(medicos)
            })

    except Exception as e:
        print(f"[API medicos-por-servicio] EXCEPCIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'medicos': []
        }), 500
    finally:
        if conexion:
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
    id_servicio = data.get('id_servicio')  # Opcional para reserva de CITA
    id_programacion = data.get('id_programacion')

    # Validaciones
    if not id_programacion:
        return jsonify({'error': 'Programación es requerida'}), 400

    try:
        # Obtener el id_paciente asociado al usuario actual
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        # Verificar que la programación existe y está disponible
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar estado de la programación
            sql_check = """
                SELECT p.*, h.id_empleado, h.activo
                FROM PROGRAMACION p
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                WHERE p.id_programacion = %s
            """
            cursor.execute(sql_check, (int(id_programacion),))
            programacion = cursor.fetchone()
            
            if not programacion:
                return jsonify({'error': 'Programación no encontrada'}), 404
            
            if programacion['estado'] != 'Disponible':
                return jsonify({'error': 'La programación ya no está disponible'}), 400
            
            if not programacion['activo']:
                return jsonify({'error': 'El horario asociado no está activo'}), 400

            # Actualizar estado de PROGRAMACION de 'Disponible' a 'Ocupado'
            sql_update = """
                UPDATE PROGRAMACION 
                SET estado = 'Ocupado'
                WHERE id_programacion = %s AND estado = 'Disponible'
            """
            cursor.execute(sql_update, (int(id_programacion),))
            
            if cursor.rowcount == 0:
                conexion.rollback()
                return jsonify({'error': 'No se pudo reservar. La programación ya no está disponible'}), 400
            
            conexion.commit()

            # Crear reserva (tipo 1 = reserva normal)
            from datetime import datetime
            fecha_actual = datetime.now().date()
            hora_actual = datetime.now().time()

            sql_reserva = """
                INSERT INTO RESERVA (fecha_registro, hora_registro, tipo, estado, id_paciente, id_programacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_reserva, (fecha_actual, hora_actual, 1, 'Confirmada', id_paciente, id_programacion))
            conexion.commit()
            id_reserva = cursor.lastrowid

            # Obtener el tipo de servicio para determinar si es CITA, EXAMEN u OPERACION
            id_servicio_prog = programacion.get('id_servicio')
            tipo_servicio_nombre = None
            
            if id_servicio_prog:
                cursor.execute("""
                    SELECT ts.nombre 
                    FROM SERVICIO s
                    INNER JOIN TIPO_SERVICIO ts ON s.id_tipo_servicio = ts.id_tipo_servicio
                    WHERE s.id_servicio = %s
                """, (id_servicio_prog,))
                tipo_data = cursor.fetchone()
                tipo_servicio_nombre = tipo_data.get('nombre', '').lower() if tipo_data else ''

            # Crear registro específico según el tipo de servicio
            fecha_prog = programacion['fecha']
            hora_inicio_prog = programacion['hora_inicio']
            hora_fin_prog = programacion['hora_fin']

            if tipo_servicio_nombre and ('consulta' in tipo_servicio_nombre or 'cita' in tipo_servicio_nombre):
                # Crear CITA
                cursor.execute("""
                    INSERT INTO CITA (fecha_cita, hora_inicio, hora_fin, estado, id_reserva)
                    VALUES (%s, %s, %s, 'Pendiente', %s)
                """, (fecha_prog, hora_inicio_prog, hora_fin_prog, id_reserva))
                print(f"✓ CITA creada para reserva {id_reserva}")
                
            elif tipo_servicio_nombre and ('examen' in tipo_servicio_nombre or 'diagnóstico' in tipo_servicio_nombre or 'diagnostico' in tipo_servicio_nombre):
                # Crear EXAMEN con todos los campos requeridos
                cursor.execute("""
                    INSERT INTO EXAMEN (fecha_examen, hora_inicio, hora_fin, estado, id_reserva)
                    VALUES (%s, %s, %s, 'Pendiente', %s)
                """, (fecha_prog, hora_inicio_prog, hora_fin_prog, id_reserva))
                print(f"✓ EXAMEN creado para reserva {id_reserva}")
                
            elif tipo_servicio_nombre and ('quirúrgico' in tipo_servicio_nombre or 'quirurgico' in tipo_servicio_nombre or 'operación' in tipo_servicio_nombre or 'operacion' in tipo_servicio_nombre):
                # Crear OPERACION
                cursor.execute("""
                    INSERT INTO OPERACION (fecha_operacion, hora_inicio, hora_fin, id_reserva)
                    VALUES (%s, %s, %s, %s)
                """, (fecha_prog, hora_inicio_prog, hora_fin_prog, id_reserva))
                print(f"✓ OPERACION creada para reserva {id_reserva}")
            else:
                print(f"⚠ No se creó registro específico. Tipo: '{tipo_servicio_nombre}'")
            
            conexion.commit()

        tipo_reserva = 'servicio' if id_servicio else 'cita'

        # Crear notificaciones para el paciente
        try:
            # 1. Notificación de confirmación de creación
            Notificacion.crear_confirmacion_reserva(id_paciente, id_reserva)
        except Exception as e:
            print(f"Error creando notificación de confirmación: {e}")
        
        try:
            # 2. Notificación del estado actual de la reserva (Confirmada)
            Notificacion.crear_notificacion_estado_reserva(id_paciente, id_reserva, 'Confirmada')
        except Exception as e:
            print(f"Error creando notificación de estado: {e}")

        # 3. Programar recordatorio para la fecha/hora de la cita
        try:
            # Obtener fecha y hora de la programación
            fecha_cita = programacion['fecha']
            hora_inicio_cita = programacion['hora_inicio']
            Notificacion.crear_recordatorio_cita(id_paciente, id_reserva, fecha_cita, hora_inicio_cita)
        except Exception as e:
            print(f"Error programando recordatorio de cita: {e}")

        return jsonify({
            'success': True,
            'id_reserva': id_reserva,
            'tipo': tipo_reserva,
            'message': f'{"Servicio reservado" if id_servicio else "Cita agendada"} exitosamente'
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
    """API que retorna todas las reservas del paciente autenticado con sus relaciones"""
    print("\n[API mis-reservas] Inicio de solicitud")
    
    if 'usuario_id' not in session:
        print("[API mis-reservas] Error: No autenticado")
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        print("[API mis-reservas] Error: No es paciente")
        return jsonify({'error': 'Acceso no autorizado'}), 403

    conexion = None
    try:
        usuario_id = session.get('usuario_id')
        print(f"[API mis-reservas] Usuario ID: {usuario_id}")
        
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            print("[API mis-reservas] Error: Paciente no encontrado")
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')
        print(f"[API mis-reservas] Paciente ID: {id_paciente}")

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Obtener todas las reservas del paciente
            sql_reservas = """
                SELECT r.id_reserva,
                       r.fecha_registro,
                       r.hora_registro,
                       r.tipo,
                       r.estado as estado_reserva,
                       r.motivo_cancelacion,
                       p.id_servicio,
                       p.fecha as fecha_programacion,
                       TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                       COALESCE(s.nombre, 'Consulta Médica') as servicio,
                       e.nombres as medico_nombres,
                       e.apellidos as medico_apellidos,
                       esp.nombre as especialidad
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE r.id_paciente = %s
                ORDER BY r.fecha_registro DESC, r.hora_registro DESC
            """
            cursor.execute(sql_reservas, (id_paciente,))
            reservas = cursor.fetchall()
            
            print(f"[API mis-reservas] Encontradas {len(reservas)} reservas")
            
            # Debug: mostrar id_servicio de cada reserva
            for r in reservas:
                print(f"[API mis-reservas] Reserva {r['id_reserva']}: id_servicio={r.get('id_servicio')}, servicio={r.get('servicio')}")
            
            # Para cada reserva, obtener sus CITAS, EXAMENES y OPERACIONES relacionadas
            for reserva in reservas:
                id_reserva = reserva['id_reserva']
                
                # Obtener CITAS relacionadas
                sql_citas = """
                    SELECT c.id_cita,
                           c.fecha_cita,
                           TIME_FORMAT(c.hora_inicio, '%%H:%%i') as hora_inicio,
                           TIME_FORMAT(c.hora_fin, '%%H:%%i') as hora_fin,
                           c.diagnostico,
                           c.observaciones,
                           c.estado
                    FROM CITA c
                    WHERE c.id_reserva = %s
                """
                cursor.execute(sql_citas, (id_reserva,))
                citas = cursor.fetchall()
                
                # Convertir fechas de citas
                for cita in citas:
                    if cita.get('fecha_cita') and hasattr(cita['fecha_cita'], 'strftime'):
                        cita['fecha_cita'] = cita['fecha_cita'].strftime('%Y-%m-%d')
                
                reserva['citas'] = citas
                
                # Obtener EXAMENES relacionados
                sql_examenes = """
                    SELECT e.id_examen,
                           e.fecha_examen,
                           e.observacion,
                           e.estado,
                           s.nombre as nombre_servicio,
                           TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                           TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin
                    FROM EXAMEN e
                    LEFT JOIN RESERVA r ON e.id_reserva = r.id_reserva
                    LEFT JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                    LEFT JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    WHERE e.id_reserva = %s
                """
                cursor.execute(sql_examenes, (id_reserva,))
                examenes = cursor.fetchall()
                
                # Convertir fechas de examenes
                for examen in examenes:
                    if examen.get('fecha_examen') and hasattr(examen['fecha_examen'], 'strftime'):
                        examen['fecha_examen'] = examen['fecha_examen'].strftime('%Y-%m-%d')
                
                reserva['examenes'] = examenes
                
                # Obtener OPERACIONES relacionadas (solo las NO completadas - sin hora_fin)
                sql_operaciones = """
                    SELECT o.id_operacion,
                           o.fecha_operacion,
                           TIME_FORMAT(o.hora_inicio, '%%H:%%i') as hora_inicio,
                           TIME_FORMAT(o.hora_fin, '%%H:%%i') as hora_fin,
                           o.observaciones,
                           CONCAT(emp.nombres, ' ', emp.apellidos) as medico,
                           c.id_cita
                    FROM OPERACION o
                    LEFT JOIN EMPLEADO emp ON o.id_empleado = emp.id_empleado
                    LEFT JOIN CITA c ON o.id_cita = c.id_cita
                    WHERE o.id_reserva = %s AND (o.hora_fin IS NULL OR o.observaciones IS NULL)
                """
                cursor.execute(sql_operaciones, (id_reserva,))
                operaciones = cursor.fetchall()
                
                # Convertir fechas de operaciones
                for operacion in operaciones:
                    if operacion.get('fecha_operacion') and hasattr(operacion['fecha_operacion'], 'strftime'):
                        operacion['fecha_operacion'] = operacion['fecha_operacion'].strftime('%Y-%m-%d')
                
                reserva['operaciones'] = operaciones
                
                # Convertir fechas de la reserva
                if reserva.get('fecha_registro'):
                    if hasattr(reserva['fecha_registro'], 'strftime'):
                        reserva['fecha_registro'] = reserva['fecha_registro'].strftime('%Y-%m-%d')
                    else:
                        reserva['fecha_registro'] = str(reserva['fecha_registro'])
                
                if reserva.get('hora_registro'):
                    if hasattr(reserva['hora_registro'], 'strftime'):
                        reserva['hora_registro'] = reserva['hora_registro'].strftime('%H:%M:%S')
                    else:
                        reserva['hora_registro'] = str(reserva['hora_registro'])
                
                if reserva.get('fecha_programacion'):
                    if hasattr(reserva['fecha_programacion'], 'strftime'):
                        reserva['fecha_programacion'] = reserva['fecha_programacion'].strftime('%Y-%m-%d')
                    else:
                        reserva['fecha_programacion'] = str(reserva['fecha_programacion'])

            print(f"[API mis-reservas] Retornando {len(reservas)} reservas completas")
            return jsonify({'reservas': reservas})

    except Exception as e:
        print(f"[API mis-reservas] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener reservas: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
                print("[API mis-reservas] Conexión cerrada")
            except:
                pass


@reservas_bp.route('/historial-clinico')
def historial_clinico():
    """Vista del historial clínico (citas completadas con diagnóstico)"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('HistorialClinicoPaciente.html')


@reservas_bp.route('/api/paciente/historial-clinico')
def api_paciente_historial_clinico():
    """API que retorna el historial clínico (citas completadas con diagnóstico)"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    conexion = None
    try:
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Solo citas completadas con diagnóstico
            sql = """
                SELECT c.id_cita,
                       c.fecha_cita,
                       TIME_FORMAT(c.hora_inicio, '%%H:%%i') as hora_inicio,
                       c.diagnostico,
                       c.observaciones,
                       c.estado,
                       e.nombres as medico_nombres,
                       e.apellidos as medico_apellidos,
                       esp.nombre as especialidad,
                       r.id_reserva,
                       (SELECT COUNT(*) FROM EXAMEN ex WHERE ex.id_reserva = r.id_reserva) as total_examenes
                FROM CITA c
                INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE r.id_paciente = %s
                  AND LOWER(c.estado) = 'Completada'
                  AND c.diagnostico IS NOT NULL
                  AND c.diagnostico != ''
                ORDER BY c.fecha_cita DESC
            """
            cursor.execute(sql, (id_paciente,))
            historial = cursor.fetchall()
            
            # Convertir fechas y obtener exámenes asociados
            for cita in historial:
                if cita.get('fecha_cita'):
                    if hasattr(cita['fecha_cita'], 'strftime'):
                        cita['fecha_cita'] = cita['fecha_cita'].strftime('%Y-%m-%d')
                    else:
                        cita['fecha_cita'] = str(cita['fecha_cita'])
                
                # Obtener detalles de exámenes asociados
                id_reserva = cita.get('id_reserva')
                if id_reserva:
                    sql_examenes = """
                        SELECT e.id_examen,
                               e.fecha_examen,
                               e.observacion,
                               e.estado,
                               'Examen Médico' as tipo_examen,
                               TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                               TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin
                        FROM EXAMEN e
                        LEFT JOIN RESERVA r ON e.id_reserva = r.id_reserva
                        LEFT JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                        WHERE e.id_reserva = %s
                        ORDER BY e.fecha_examen DESC
                    """
                    cursor.execute(sql_examenes, (id_reserva,))
                    examenes = cursor.fetchall()
                    
                    # Convertir fechas de exámenes
                    for examen in examenes:
                        if examen.get('fecha_examen'):
                            if hasattr(examen['fecha_examen'], 'strftime'):
                                examen['fecha_examen'] = examen['fecha_examen'].strftime('%Y-%m-%d')
                            else:
                                examen['fecha_examen'] = str(examen['fecha_examen'])
                    
                    cita['examenes'] = examenes
                    
                    # Obtener operaciones asociadas (si la tabla OPERACION existe)
                    try:
                        sql_operaciones = """
                            SELECT o.id_operacion,
                                   o.fecha_operacion,
                                   TIME_FORMAT(o.hora_operacion, '%%H:%%i') as hora_operacion,
                                   o.descripcion,
                                   o.estado,
                                   o.tipo_operacion
                            FROM OPERACION o
                            WHERE o.id_reserva = %s
                            ORDER BY o.fecha_operacion DESC, o.hora_operacion DESC
                        """
                        cursor.execute(sql_operaciones, (id_reserva,))
                        operaciones = cursor.fetchall()
                        
                        # Convertir fechas de operaciones
                        for operacion in operaciones:
                            if operacion.get('fecha_operacion'):
                                if hasattr(operacion['fecha_operacion'], 'strftime'):
                                    operacion['fecha_operacion'] = operacion['fecha_operacion'].strftime('%Y-%m-%d')
                                else:
                                    operacion['fecha_operacion'] = str(operacion['fecha_operacion'])
                        
                        cita['operaciones'] = operaciones
                    except:
                        # Si la tabla OPERACION no existe, devolver lista vacía
                        cita['operaciones'] = []
                else:
                    cita['examenes'] = []
                    cita['operaciones'] = []

            return jsonify({'historial': historial})

    except Exception as e:
        print(f"[API historial-clinico] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener historial clínico: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@reservas_bp.route('/operaciones')
def operaciones():
    """Vista de gestión de operaciones"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('GestionOperaciones.html')


@reservas_bp.route('/examenes')
def examenes():
    """Vista de gestión de exámenes"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('GestionExamenes.html')


@reservas_bp.route('/api/paciente/examenes')
def api_paciente_examenes():
    """API que retorna todos los exámenes del paciente autenticado"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    conexion = None
    try:
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)

        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT e.id_examen,
                       e.fecha_examen,
                       e.observacion,
                       e.estado,
                       r.id_reserva,
                       'Examen Médico' as tipo_examen,
                       TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin
                FROM EXAMEN e
                INNER JOIN RESERVA r ON e.id_reserva = r.id_reserva
                LEFT JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                WHERE r.id_paciente = %s
                ORDER BY e.fecha_examen DESC
            """
            cursor.execute(sql, (id_paciente,))
            examenes = cursor.fetchall()
            
            # Convertir fechas
            for examen in examenes:
                if examen.get('fecha_examen'):
                    if hasattr(examen['fecha_examen'], 'strftime'):
                        examen['fecha_examen'] = examen['fecha_examen'].strftime('%Y-%m-%d')
                    else:
                        examen['fecha_examen'] = str(examen['fecha_examen'])

            return jsonify({'examenes': examenes})

    except Exception as e:
        print(f"[API examenes] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener exámenes: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


# ========== RUTAS PARA GENERACIÓN DE EXÁMENES Y OPERACIONES ==========

@reservas_bp.route('/examenes/generar')
def examenes_generar():
    """Vista para generar un nuevo examen"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('GenerarExamen.html')


@reservas_bp.route('/operaciones/generar')
def operaciones_generar():
    """Vista para generar una nueva operación"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('GenerarOperacion.html')


@reservas_bp.route('/api/examenes/crear', methods=['POST'])
def api_crear_examen():
    """API para crear un nuevo examen (crea automáticamente la reserva y programación)"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_servicio = data.get('id_servicio')
    fecha_examen = data.get('fecha_examen')
    hora_inicio = data.get('hora_inicio')
    estado = data.get('estado', 'Confirmada')
    observacion = data.get('observacion', '')

    # Validaciones
    if not id_servicio:
        return jsonify({'error': 'ID de servicio es requerido'}), 400
    
    if not fecha_examen:
        return jsonify({'error': 'Fecha del examen es requerida'}), 400
    
    if not hora_inicio:
        return jsonify({'error': 'Hora del examen es requerida'}), 400

    conexion = None
    try:
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)
        
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # 1. Buscar un horario activo para esa fecha y hora sin programación ocupada
            sql_horario = """
                SELECT h.id_horario 
                FROM HORARIO h
                LEFT JOIN PROGRAMACION p ON p.id_horario = h.id_horario 
                    AND p.fecha = h.fecha 
                    AND p.hora_inicio <= %s 
                    AND p.hora_fin >= %s
                WHERE h.fecha = %s 
                AND h.hora_inicio <= %s 
                AND h.hora_fin >= %s
                AND h.activo = 1
                AND (p.estado IS NULL OR p.estado = 'Disponible')
                LIMIT 1
            """
            cursor.execute(sql_horario, (hora_inicio, hora_inicio, fecha_examen, hora_inicio, hora_inicio))
            horario = cursor.fetchone()
            
            if not horario:
                return jsonify({'error': 'No hay horarios disponibles para la fecha y hora seleccionada'}), 400
            
            id_horario = horario['id_horario']
            
            # 2. Crear una PROGRAMACION para el examen
            sql_programacion = """
                INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario)
                VALUES (%s, %s, %s, 'Activo', %s, %s)
            """
            # Asumimos 1 hora de duración para exámenes
            from datetime import datetime, timedelta
            hora_obj = datetime.strptime(hora_inicio, '%H:%M')
            hora_fin_obj = hora_obj + timedelta(hours=1)
            hora_fin = hora_fin_obj.strftime('%H:%M')
            
            cursor.execute(sql_programacion, (fecha_examen, hora_inicio, hora_fin, id_servicio, id_horario))
            id_programacion = cursor.lastrowid
            
            # 3. Crear la RESERVA
            from datetime import datetime
            fecha_registro = datetime.now().date()
            hora_registro = datetime.now().time()
            
            sql_reserva = """
                INSERT INTO RESERVA (fecha_registro, hora_registro, tipo, estado, id_paciente, id_programacion)
                VALUES (%s, %s, 3, 'Confirmada', %s, %s)
            """
            cursor.execute(sql_reserva, (fecha_registro, hora_registro, id_paciente, id_programacion))
            id_reserva = cursor.lastrowid

            # 4. Crear el EXAMEN
            sql_examen = """
                INSERT INTO EXAMEN (fecha_examen, hora_inicio, observacion, estado, id_reserva)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_examen, (fecha_examen, hora_inicio, observacion, estado, id_reserva))
            id_examen = cursor.lastrowid
            
            # 5. Commit de toda la transacción
            conexion.commit()

            return jsonify({
                'success': True,
                'id_examen': id_examen,
                'id_reserva': id_reserva,
                'message': 'Examen agendado exitosamente'
            }), 201

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API crear-examen] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al agendar examen: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@reservas_bp.route('/api/operaciones/crear', methods=['POST'])
def api_crear_operacion():
    """API para crear una nueva operación"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    id_cita = data.get('id_cita')
    fecha_operacion = data.get('fecha_operacion')
    hora_inicio = data.get('hora_inicio')
    observaciones_tipo = data.get('observaciones', '')

    # Validaciones
    if not id_reserva:
        return jsonify({'error': 'ID de reserva es requerido'}), 400
    
    if not id_cita:
        return jsonify({'error': 'ID de cita es requerido'}), 400
    
    if not fecha_operacion:
        return jsonify({'error': 'Fecha de operación es requerida'}), 400
    
    if not hora_inicio:
        return jsonify({'error': 'Hora de inicio es requerida'}), 400
    
    if not observaciones_tipo:
        return jsonify({'error': 'Observaciones iniciales son requeridas'}), 400

    conexion = None
    try:
        # Verificar que la reserva pertenece al paciente autenticado
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)
        
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la reserva pertenece al paciente
            sql_verificar = """
                SELECT id_reserva FROM RESERVA WHERE id_reserva = %s AND id_paciente = %s
            """
            cursor.execute(sql_verificar, (id_reserva, id_paciente))
            reserva = cursor.fetchone()
            
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada o no autorizada'}), 404

            # Obtener el id_empleado (médico) de la CITA
            sql_medico = """
                SELECT 
                    c.id_cita,
                    p.id_horario,
                    h.id_empleado
                FROM CITA c
                INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                WHERE c.id_cita = %s AND c.id_reserva = %s
            """
            cursor.execute(sql_medico, (id_cita, id_reserva))
            cita_info = cursor.fetchone()
            
            if not cita_info:
                return jsonify({'error': 'Cita no encontrada o no relacionada con la reserva'}), 404
            
            id_empleado = cita_info['id_empleado']
            
            if not id_empleado:
                return jsonify({'error': 'No se pudo determinar el médico responsable de la cita'}), 400

            # Insertar la nueva operación (sin hora_fin ni observaciones finales - las completa el médico)
            sql_insert = """
                INSERT INTO OPERACION (fecha_operacion, hora_inicio, hora_fin, observaciones, id_reserva, id_empleado, id_cita)
                VALUES (%s, %s, NULL, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (fecha_operacion, hora_inicio, observaciones_tipo, id_reserva, id_empleado, id_cita))
            conexion.commit()
            
            id_operacion = cursor.lastrowid

            return jsonify({
                'success': True,
                'id_operacion': id_operacion,
                'id_empleado': id_empleado,
                'message': 'Operación programada exitosamente'
            }), 201

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API crear-operacion] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al crear operación: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@reservas_bp.route('/api/horarios-disponibles-reprogramacion', methods=['POST'])
def api_horarios_disponibles_reprogramacion():
    """API para obtener horarios disponibles del mismo médico y servicio para reprogramar"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    # Permitir tanto pacientes como empleados (admin) para reprogramar
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario not in ['paciente', 'empleado']:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    fecha = data.get('fecha')
    
    print(f"[API horarios-reprogramacion] Tipo usuario: {tipo_usuario}, Datos: id_reserva={id_reserva}, fecha={fecha}")

    if not id_reserva or not fecha:
        error_msg = f'Faltan datos requeridos: id_reserva={id_reserva}, fecha={fecha}'
        print(f"[API horarios-reprogramacion] ERROR: {error_msg}")
        return jsonify({'error': error_msg}), 400

    conexion = None
    try:
        usuario_id = session.get('usuario_id')
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Obtener datos de la reserva actual: paciente, médico, servicio, tipo de servicio
            sql_get_reserva = """
                SELECT 
                    r.id_paciente, 
                    r.id_reserva,
                    r.id_programacion,
                    prog.id_servicio,
                    prog.id_horario as id_horario_actual,
                    h.id_empleado,
                    h.hora_inicio as hora_actual_inicio,
                    h.hora_fin as hora_actual_fin,
                    s.nombre as servicio_nombre,
                    ts.nombre as tipo_servicio
                FROM RESERVA r
                INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
                INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                INNER JOIN TIPO_SERVICIO ts ON s.id_tiposervicio = ts.id_tiposervicio
                WHERE r.id_reserva = %s
            """
            cursor.execute(sql_get_reserva, (id_reserva,))
            reserva_info = cursor.fetchone()
            
            if not reserva_info:
                return jsonify({'error': 'Reserva no encontrada'}), 404
            
            id_paciente = reserva_info['id_paciente']
            id_empleado = reserva_info['id_empleado']
            id_servicio = reserva_info['id_servicio']
            tipo_servicio = reserva_info['tipo_servicio']
            hora_actual_inicio = reserva_info['hora_actual_inicio']
            hora_actual_fin = reserva_info['hora_actual_fin']
            
            print(f"[API horarios-reprogramacion] Médico: {id_empleado}, Servicio: {id_servicio}, Tipo: {tipo_servicio}")
            
            # Para pacientes, validar que la reserva sea suya
            if tipo_usuario == 'paciente':
                paciente = Paciente.obtener_por_usuario(usuario_id)
                if not paciente or paciente.get('id_paciente') != id_paciente:
                    return jsonify({'error': 'No tienes permiso para acceder a esta reserva'}), 403
            
            # Convertir timedelta a time si es necesario
            if isinstance(hora_actual_inicio, timedelta):
                total_seconds = int(hora_actual_inicio.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                hora_actual_inicio = time(hours, minutes)
            
            if isinstance(hora_actual_fin, timedelta):
                total_seconds = int(hora_actual_fin.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                hora_actual_fin = time(hours, minutes)
            
            print(f"[API horarios-reprogramacion] Hora actual: {hora_actual_inicio} - {hora_actual_fin}")

            # Buscar programaciones disponibles del MISMO médico y MISMO tipo de servicio (CITA, EXAMEN, OPERACION)
            sql_horarios = """
                SELECT DISTINCT
                    prog.id_programacion,
                    prog.id_horario,
                    prog.fecha,
                    TIME_FORMAT(prog.hora_inicio, '%%H:%%i') as hora_inicio,
                    TIME_FORMAT(prog.hora_fin, '%%H:%%i') as hora_fin,
                    prog.estado,
                    s.nombre as servicio_nombre,
                    CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre
                FROM PROGRAMACION prog
                INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
                INNER JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
                INNER JOIN TIPO_SERVICIO ts ON s.id_tiposervicio = ts.id_tiposervicio
                INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                WHERE prog.fecha = %s
                AND h.id_empleado = %s
                AND ts.nombre = %s
                AND prog.estado = 'Disponible'
                AND h.activo = 1
                AND NOT (prog.hora_inicio = %s AND prog.hora_fin = %s)
                ORDER BY prog.hora_inicio ASC
            """
            cursor.execute(sql_horarios, (fecha, id_empleado, tipo_servicio, hora_actual_inicio, hora_actual_fin))
            
            horarios = cursor.fetchall()
            print(f"[API horarios-reprogramacion] Encontradas {len(horarios)} programaciones disponibles del mismo médico y tipo de servicio")

            horarios_disponibles = []
            for horario in horarios:
                horarios_disponibles.append({
                    'id_programacion': horario['id_programacion'],
                    'hora': horario['hora_inicio'],
                    'hora_inicio': horario['hora_inicio'],
                    'hora_fin': horario['hora_fin'],
                    'servicio': horario['servicio_nombre'],
                    'medico': horario['medico_nombre']
                })

            return jsonify({
                'success': True,
                'horarios': horarios_disponibles,
                'hora_actual': hora_actual_inicio.strftime('%H:%M') if hasattr(hora_actual_inicio, 'strftime') else str(hora_actual_inicio),
                'medico': reserva_info.get('medico_nombre', 'N/A'),
                'tipo_servicio': tipo_servicio
            }), 200

    except Exception as e:
        print(f"[API horarios-reprogramacion] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener horarios: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@reservas_bp.route('/api/reprogramar', methods=['POST'])
def api_reprogramar_reserva():
    """API para reprogramar una reserva cambiando su horario"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    # Permitir tanto pacientes como empleados (admin) para reprogramar
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario not in ['paciente', 'empleado']:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    nueva_fecha = data.get('nueva_fecha')
    nueva_hora = data.get('nueva_hora')
    id_servicio = data.get('id_servicio')  # Opcional ahora

    # Validar solo los campos esenciales
    if not all([id_reserva, nueva_fecha, nueva_hora]):
        return jsonify({'error': 'Faltan datos requeridos (id_reserva, nueva_fecha, nueva_hora)'}), 400
    
    print(f"[API reprogramar] Tipo usuario: {tipo_usuario}, Datos: id_reserva={id_reserva}, fecha={nueva_fecha}, hora={nueva_hora}, id_servicio={id_servicio}")

    conexion = None
    try:
        usuario_id = session.get('usuario_id')
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Primero obtener el id_paciente de la reserva
            sql_get_reserva = """
                SELECT r.id_paciente, r.id_reserva
                FROM RESERVA r
                WHERE r.id_reserva = %s
            """
            cursor.execute(sql_get_reserva, (id_reserva,))
            reserva_info = cursor.fetchone()
            
            if not reserva_info:
                return jsonify({'error': 'Reserva no encontrada'}), 404
            
            id_paciente = reserva_info['id_paciente']
            
            # Para pacientes, validar que la reserva sea suya
            if tipo_usuario == 'paciente':
                paciente = Paciente.obtener_por_usuario(usuario_id)
                if not paciente or paciente.get('id_paciente') != id_paciente:
                    return jsonify({'error': 'No tienes permiso para acceder a esta reserva'}), 403
        
            # Obtener la reserva actual y su id_servicio si no se proporcionó
            sql_verificar = """
                SELECT r.id_reserva, r.id_programacion, r.tipo, p.id_servicio
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                WHERE r.id_reserva = %s AND r.id_paciente = %s
            """
            cursor.execute(sql_verificar, (id_reserva, id_paciente))
            reserva = cursor.fetchone()
            
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada'}), 404
            
            id_programacion_actual = reserva['id_programacion']
            tipo_reserva = reserva['tipo']
            
            # Si no se proporcionó id_servicio, usar el de la programación actual
            if not id_servicio:
                id_servicio = reserva.get('id_servicio')
                print(f"[API reprogramar] Usando id_servicio de la reserva actual: {id_servicio}")

            sql_horario = """
                SELECT h.id_horario 
                FROM HORARIO h
                LEFT JOIN PROGRAMACION p ON p.id_horario = h.id_horario 
                    AND p.fecha = h.fecha 
                    AND p.hora_inicio <= %s 
                    AND p.hora_fin >= %s
                WHERE h.fecha = %s 
                AND h.hora_inicio <= %s 
                AND h.hora_fin >= %s
                AND h.activo = 1
                AND (p.estado IS NULL OR p.estado = 'Disponible')
                LIMIT 1
            """
            cursor.execute(sql_horario, (nueva_hora, nueva_hora, nueva_fecha, nueva_hora, nueva_hora))
            horario_nuevo = cursor.fetchone()
            
            if not horario_nuevo:
                return jsonify({'error': 'Horario no disponible'}), 400
            
            id_horario_nuevo = horario_nuevo['id_horario']

            from datetime import datetime, timedelta
            hora_obj = datetime.strptime(nueva_hora, '%H:%M')
            hora_fin_obj = hora_obj + timedelta(hours=1)
            hora_fin = hora_fin_obj.strftime('%H:%M')

            sql_nueva_prog = """
                INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario)
                VALUES (%s, %s, %s, 'Activo', %s, %s)
            """
            cursor.execute(sql_nueva_prog, (nueva_fecha, nueva_hora, hora_fin, id_servicio, id_horario_nuevo))
            id_programacion_nueva = cursor.lastrowid

            sql_actualizar = """
                UPDATE RESERVA 
                SET id_programacion = %s,
                    estado = 'Confirmada',
                    motivo_cancelacion = NULL
                WHERE id_reserva = %s
            """
            cursor.execute(sql_actualizar, (id_programacion_nueva, id_reserva))

            # Actualizar la tabla específica según el tipo de reserva
            # hora_fin ya fue calculado arriba
            if tipo_reserva == 1:
                sql_actualizar_cita = """
                    UPDATE CITA 
                    SET fecha_cita = %s, hora_inicio = %s, hora_fin = %s 
                    WHERE id_reserva = %s
                """
                cursor.execute(sql_actualizar_cita, (nueva_fecha, nueva_hora, hora_fin, id_reserva))
            elif tipo_reserva == 3:
                sql_actualizar_examen = """
                    UPDATE EXAMEN 
                    SET fecha_examen = %s, hora_inicio = %s 
                    WHERE id_reserva = %s
                """
                cursor.execute(sql_actualizar_examen, (nueva_fecha, nueva_hora, id_reserva))
            elif tipo_reserva == 2:
                sql_actualizar_operacion = """
                    UPDATE OPERACION 
                    SET fecha_operacion = %s, hora_inicio = %s, hora_fin = %s 
                    WHERE id_reserva = %s
                """
                cursor.execute(sql_actualizar_operacion, (nueva_fecha, nueva_hora, hora_fin, id_reserva))

            conexion.commit()

            return jsonify({
                'success': True,
                'message': 'Reserva reprogramada exitosamente'
            }), 200

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API reprogramar] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al reprogramar: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@reservas_bp.route('/api/solicitar-cancelacion', methods=['POST'])
def api_solicitar_cancelacion():
    """API para solicitar la cancelación de una reserva"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    motivo = data.get('motivo', '')

    if not id_reserva:
        return jsonify({'error': 'ID de reserva es requerido'}), 400

    if not motivo or len(motivo.strip()) < 10:
        return jsonify({'error': 'Debe proporcionar un motivo válido (mínimo 10 caracteres)'}), 400

    conexion = None
    try:
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)
        
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        id_paciente = paciente.get('id_paciente')

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la reserva existe y pertenece al paciente
            sql_verificar = """
                SELECT id_reserva, estado 
                FROM RESERVA 
                WHERE id_reserva = %s AND id_paciente = %s
            """
            cursor.execute(sql_verificar, (id_reserva, id_paciente))
            reserva = cursor.fetchone()
            
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada'}), 404
            
            if reserva['estado'] == 'Cancelada':
                return jsonify({'error': 'Esta reserva ya está cancelada'}), 400
            
            if reserva['estado'] == 'Completada':
                return jsonify({'error': 'No se puede cancelar una reserva completada'}), 400
            
            # Verificar si ya existe una solicitud pendiente en la tabla SOLICITUD
            sql_verificar_solicitud = """
                SELECT COUNT(*) as count 
                FROM SOLICITUD 
                WHERE id_reserva = %s AND estado = 'Pendiente'
            """
            cursor.execute(sql_verificar_solicitud, (id_reserva,))
            result = cursor.fetchone()
            
            if result and result['count'] > 0:
                return jsonify({'error': 'Ya existe una solicitud de cancelación pendiente para esta reserva'}), 400

            # Crear solicitud en la tabla SOLICITUD
            sql_insertar_solicitud = """
                INSERT INTO SOLICITUD (id_reserva, estado, motivo, fecha_solicitud)
                VALUES (%s, 'Pendiente', %s, NOW())
            """
            cursor.execute(sql_insertar_solicitud, (id_reserva, motivo))
            conexion.commit()

            return jsonify({
                'success': True,
                'message': 'Solicitud de cancelación enviada. Un trabajador la revisará pronto.'
            }), 200

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API solicitar-cancelacion] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al solicitar cancelación: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


# ==================== ENDPOINTS PARA TRABAJADORES ====================

@reservas_bp.route('/api/trabajador/solicitudes-cancelacion')
def api_trabajador_solicitudes_cancelacion():
    """API para obtener todas las solicitudes de cancelación (para trabajadores, empleados y administradores)"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    # Verificar que sea trabajador, empleado o admin
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario not in ['trabajador', 'administrador', 'empleado']:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    s.id_solicitud,
                    s.id_reserva,
                    s.estado as estado,
                    s.motivo,
                    s.respuesta,
                    s.fecha_solicitud,
                    s.fecha_respuesta,
                    r.fecha_registro,
                    r.estado as estado_reserva,
                    r.tipo,
                    p.fecha as fecha_programacion,
                    TIME_FORMAT(p.hora_inicio, '%H:%i') as hora_inicio,
                    TIME_FORMAT(p.hora_fin, '%H:%i') as hora_fin,
                    COALESCE(serv.nombre, 'Consulta Médica') as servicio,
                    esp.nombre as especialidad,
                    pac.nombres as paciente_nombres,
                    pac.apellidos as paciente_apellidos,
                    pac.documento_identidad as paciente_dni
                FROM SOLICITUD s
                INNER JOIN RESERVA r ON s.id_reserva = r.id_reserva
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                LEFT JOIN SERVICIO serv ON p.id_servicio = serv.id_servicio
                INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE s.nueva_programacion_id IS NULL
                ORDER BY 
                    CASE s.estado
                        WHEN 'Pendiente' THEN 1
                        WHEN 'Aprobada' THEN 2
                        WHEN 'Rechazada' THEN 3
                    END,
                    s.fecha_solicitud DESC
            """
            cursor.execute(sql)
            solicitudes = cursor.fetchall()

            print(f"📊 Total de solicitudes de cancelación encontradas: {len(solicitudes)}")
            
            # Convertir fechas
            for solicitud in solicitudes:
                if solicitud.get('fecha_programacion') and hasattr(solicitud['fecha_programacion'], 'strftime'):
                    solicitud['fecha_programacion'] = solicitud['fecha_programacion'].strftime('%Y-%m-%d')
                if solicitud.get('fecha_solicitud') and hasattr(solicitud['fecha_solicitud'], 'strftime'):
                    solicitud['fecha_solicitud'] = solicitud['fecha_solicitud'].strftime('%Y-%m-%d %H:%M:%S')
                if solicitud.get('fecha_respuesta') and hasattr(solicitud['fecha_respuesta'], 'strftime'):
                    solicitud['fecha_respuesta'] = solicitud['fecha_respuesta'].strftime('%Y-%m-%d %H:%M:%S')

            return jsonify({
                'success': True,
                'solicitudes': solicitudes
            }), 200

    except Exception as e:
        print(f"[API trabajador-solicitudes] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener solicitudes: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@reservas_bp.route('/api/trabajador/procesar-cancelacion', methods=['POST'])
def api_trabajador_procesar_cancelacion():
    """API para aprobar o rechazar una solicitud de cancelación"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario not in ['trabajador', 'administrador', 'empleado']:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    estado = data.get('estado')  # 'Aprobada' o 'Rechazada'

    if not id_reserva:
        return jsonify({'error': 'Falta id_reserva'}), 400

    if estado not in ['Aprobada', 'Rechazada']:
        return jsonify({'error': 'Estado inválido'}), 400

    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Buscar la solicitud pendiente para esta reserva
            cursor.execute("""
                SELECT s.id_solicitud, s.motivo, r.id_paciente
                FROM SOLICITUD s
                INNER JOIN RESERVA r ON s.id_reserva = r.id_reserva
                WHERE s.id_reserva = %s 
                AND s.estado = 'Pendiente'
                AND s.motivo IS NOT NULL
                AND s.nueva_programacion_id IS NULL
                ORDER BY s.fecha_solicitud DESC
                LIMIT 1
            """, (id_reserva,))
            
            solicitud = cursor.fetchone()
            
            if not solicitud:
                return jsonify({'error': 'No se encontró solicitud de cancelación pendiente'}), 404
            
            id_solicitud = solicitud['id_solicitud']
            id_paciente = solicitud['id_paciente']
            
            # Actualizar estado de la solicitud
            cursor.execute("""
                UPDATE SOLICITUD
                SET estado = %s,
                    fecha_respuesta = NOW()
                WHERE id_solicitud = %s
            """, (estado, id_solicitud))
            
            # Si se aprueba, actualizar estado de la reserva y liberar programación
            if estado == 'Aprobada':
                # Obtener información de la reserva para emails
                sql_info_reserva = """
                    SELECT 
                        r.id_reserva,
                        r.id_programacion,
                        r.id_paciente,
                        CONCAT(pac.nombres, ' ', pac.apellidos) as paciente_nombre,
                        pac.documento_identidad as paciente_dni,
                        u.correo as paciente_correo,
                        p.fecha as fecha_programacion,
                        TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                        TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                        s.nombre as servicio,
                        s.id_tipo_servicio as tipo,
                        CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                        u_medico.correo as medico_correo,
                        esp.nombre as especialidad
                    FROM RESERVA r
                    INNER JOIN PACIENTE pac ON r.id_paciente = pac.id_paciente
                    INNER JOIN USUARIO u ON pac.id_usuario = u.id_usuario
                    INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                    INNER JOIN SERVICIO s ON p.id_servicio = s.id_servicio
                    LEFT JOIN HORARIO h ON p.id_horario = h.id_horario
                    LEFT JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                    LEFT JOIN USUARIO u_medico ON e.id_usuario = u_medico.id_usuario
                    LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                    WHERE r.id_reserva = %s
                """
                cursor.execute(sql_info_reserva, (id_reserva,))
                info_reserva = cursor.fetchone()
                
                # Actualizar estado de la reserva a Cancelada
                cursor.execute("""
                    UPDATE RESERVA
                    SET estado = 'Cancelada',
                        motivo_cancelacion = (SELECT motivo FROM SOLICITUD WHERE id_solicitud = %s)
                    WHERE id_reserva = %s
                """, (id_solicitud, id_reserva))
                
                # Liberar la programación
                id_programacion = info_reserva['id_programacion']
                cursor.execute("""
                    UPDATE PROGRAMACION
                    SET estado = 'Disponible'
                    WHERE id_programacion = %s
                """, (id_programacion,))
                
                conexion.commit()
                
                # Enviar emails de cancelación
                try:
                    # Email al paciente
                    enviar_email_cancelacion_aprobada(
                        destinatario=info_reserva['paciente_correo'],
                        paciente_nombre=info_reserva['paciente_nombre'],
                        servicio=info_reserva['servicio'],
                        fecha=info_reserva['fecha_programacion'].strftime('%d/%m/%Y'),
                        hora=info_reserva['hora_inicio']
                    )
                    
                    # Email al médico (si existe)
                    if info_reserva.get('medico_correo'):
                        enviar_email_cancelacion_medico(
                            destinatario=info_reserva['medico_correo'],
                            medico_nombre=info_reserva['medico_nombre'],
                            paciente_nombre=info_reserva['paciente_nombre'],
                            servicio=info_reserva['servicio'],
                            fecha=info_reserva['fecha_programacion'].strftime('%d/%m/%Y'),
                            hora=info_reserva['hora_inicio']
                        )
                except Exception as e:
                    print(f"❌ Error enviando emails de cancelación: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Crear notificación para el paciente
                try:
                    Notificacion.crear_cancelacion_aprobada(id_paciente, id_reserva)
                except Exception as e:
                    print(f"Error creando notificación: {e}")
                
                return jsonify({'success': True, 'message': 'Cancelación aprobada exitosamente'})
            else:
                # Solo actualizar la solicitud como rechazada
                conexion.commit()
                
                # Crear notificación para el paciente
                try:
                    Notificacion.crear_cancelacion_rechazada(id_paciente, id_reserva)
                except Exception as e:
                    print(f"Error creando notificación: {e}")
                
                return jsonify({'success': True, 'message': 'Solicitud de cancelación rechazada'})
            
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API procesar-cancelacion] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al procesar solicitud: {str(e)}'}), 500
    finally:
        if conexion:
            conexion.close()

# ========== ENDPOINTS PARA PACIENTES: SOLICITUDES DE REPROGRAMACIÓN Y CANCELACIÓN ==========

@reservas_bp.route('/api/solicitar-reprogramacion', methods=['POST'])
def api_solicitar_reprogramacion_paciente():
    """API para que los pacientes soliciten reprogramación de una reserva"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    data = request.get_json()
    id_reserva = data.get('id_reserva')
    motivo = data.get('motivo', '').strip()
    
    if not id_reserva:
        return jsonify({'error': 'Falta id_reserva'}), 400
    
    if len(motivo) < 20:
        return jsonify({'error': 'El motivo debe tener al menos 20 caracteres'}), 400
    
    conexion = None
    try:
        # Obtener id_paciente del usuario actual
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        id_paciente = paciente.get('id_paciente')
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la reserva pertenece al paciente y está activa
            cursor.execute("""
                SELECT r.*, p.fecha as fecha_programacion
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                WHERE r.id_reserva = %s AND r.id_paciente = %s
            """, (id_reserva, id_paciente))
            reserva = cursor.fetchone()
            
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada o no te pertenece'}), 404
            
            if reserva['estado'] != 'Confirmada':
                return jsonify({'error': f'No puedes solicitar reprogramación de una reserva con estado {reserva["estado"]}'}), 400
            
            # Validar que la reserva es al menos 2 días en el futuro
            fecha_reserva = reserva['fecha_programacion']
            hoy = date.today()
            dias_diferencia = (fecha_reserva - hoy).days
            
            if dias_diferencia < 2:
                return jsonify({'error': 'Las solicitudes de reprogramación deben realizarse con al menos 2 días de anticipación'}), 400
            
            # Verificar si ya existe una solicitud pendiente
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM SOLICITUD
                WHERE id_reserva = %s AND estado = 'Pendiente'
            """, (id_reserva,))
            pendientes = cursor.fetchone()
            
            if pendientes and pendientes['total'] > 0:
                return jsonify({'error': 'Ya existe una solicitud de reprogramación pendiente para esta reserva'}), 400
            
            # Crear la solicitud
            cursor.execute("""
                INSERT INTO SOLICITUD (id_reserva, motivo, estado, fecha_solicitud)
                VALUES (%s, %s, 'Pendiente', NOW())
            """, (id_reserva, motivo))
            conexion.commit()
            id_solicitud = cursor.lastrowid
            
            # Crear notificación para el paciente
            try:
                Notificacion.crear(
                    'Solicitud de Reprogramación Enviada',
                    f'Tu solicitud de reprogramación para la reserva #{id_reserva} ha sido enviada. Recibirás una respuesta en las próximas 24-48 horas.',
                    'confirmacion',
                    id_paciente,
                    id_reserva
                )
            except Exception as e:
                print(f"Error creando notificación: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Solicitud de reprogramación enviada exitosamente',
                'id_solicitud': id_solicitud
            }), 201
            
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API solicitar-reprogramacion] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al enviar solicitud: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass


@reservas_bp.route('/api/solicitar-cancelacion', methods=['POST'])
def api_solicitar_cancelacion_paciente():
    """API para que los pacientes soliciten cancelación de una reserva"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    data = request.get_json()
    id_reserva = data.get('id_reserva')
    motivo = data.get('motivo', '').strip()
    
    if not id_reserva:
        return jsonify({'error': 'Falta id_reserva'}), 400
    
    if len(motivo) < 20:
        return jsonify({'error': 'El motivo debe tener al menos 20 caracteres'}), 400
    
    conexion = None
    try:
        # Obtener id_paciente del usuario actual
        usuario_id = session.get('usuario_id')
        paciente = Paciente.obtener_por_usuario(usuario_id)
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        id_paciente = paciente.get('id_paciente')
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar que la reserva pertenece al paciente y está activa
            cursor.execute("""
                SELECT r.*, p.fecha as fecha_programacion
                FROM RESERVA r
                INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                WHERE r.id_reserva = %s AND r.id_paciente = %s
            """, (id_reserva, id_paciente))
            reserva = cursor.fetchone()
            
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada o no te pertenece'}), 404
            
            if reserva['estado'] != 'Confirmada':
                return jsonify({'error': f'No puedes solicitar cancelación de una reserva con estado {reserva["estado"]}'}), 400
            
            # Validar que la reserva es al menos 2 días en el futuro
            fecha_reserva = reserva['fecha_programacion']
            hoy = date.today()
            dias_diferencia = (fecha_reserva - hoy).days
            
            if dias_diferencia < 2:
                return jsonify({'error': 'Las solicitudes de cancelación deben realizarse con al menos 2 días de anticipación'}), 400
            
            # Verificar si ya existe una solicitud pendiente
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM SOLICITUD
                WHERE id_reserva = %s AND estado = 'Pendiente'
            """, (id_reserva,))
            pendientes = cursor.fetchone()
            
            if pendientes and pendientes['total'] > 0:
                return jsonify({'error': 'Ya existe una solicitud de cancelación pendiente para esta reserva'}), 400
            
            # Crear la solicitud
            cursor.execute("""
                INSERT INTO SOLICITUD (id_reserva, motivo, estado, fecha_solicitud)
                VALUES (%s, %s, 'Pendiente', NOW())
            """, (id_reserva, motivo))
            conexion.commit()
            id_solicitud = cursor.lastrowid
            
            # Crear notificación para el paciente
            try:
                Notificacion.crear(
                    'Solicitud de Cancelación Enviada',
                    f'Tu solicitud de cancelación para la reserva #{id_reserva} ha sido enviada. Recibirás una respuesta en las próximas 24-48 horas.',
                    'cancelacion',
                    id_paciente,
                    id_reserva
                )
            except Exception as e:
                print(f"Error creando notificación: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Solicitud de cancelación enviada exitosamente',
                'id_solicitud': id_solicitud
            }), 201
            
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API solicitar-cancelacion] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al enviar solicitud: {str(e)}'}), 500
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass

