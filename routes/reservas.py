from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.empleado import Empleado
from models.servicio import Servicio
from models.catalogos import TipoServicio
from models.horario import Horario
from models.paciente import Paciente
from models.reserva import Reserva
from models.programacion import Programacion
from bd import obtener_conexion
from datetime import date
from models.notificacion import Notificacion

reservas_bp = Blueprint('reservas', __name__)

def actualizar_horarios_vencidos():
    """
    Actualiza automáticamente el estado de los horarios a 'Completado' 
    cuando la fecha del horario ya ha pasado (fecha < fecha actual).
    
    Esta función se ejecuta automáticamente antes de consultar horarios
    para mantener los estados actualizados.
    """
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        fecha_actual = date.today()
        
        # Actualizar horarios cuya fecha ya pasó y no están en estado Completado
        query = """
            UPDATE HORARIO 
            SET estado = 'Completado'
            WHERE fecha < %s 
            AND estado != 'Completado'
        """
        
        cursor.execute(query, (fecha_actual,))
        registros_actualizados = cursor.rowcount
        conn.commit()
        
        if registros_actualizados > 0:
            print(f"✓ Se actualizaron {registros_actualizados} horarios a estado 'Completado'")
        
        return registros_actualizados
        
    except Exception as e:
        print(f"Error al actualizar horarios vencidos: {str(e)}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
                    h.estado,
                    h.disponibilidad,
                    CONCAT(e.nombres, ' ', e.apellidos) as medico_nombre,
                    esp.nombre as especialidad
                FROM HORARIO h
                INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
                LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
                WHERE h.id_empleado = %s
                  AND h.fecha BETWEEN %s AND %s
                  AND LOWER(h.estado) = 'activo'
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
                
                # Marcar si es disponible (verificar campo disponibilidad o estado)
                disponibilidad = horario.get('disponibilidad', '').lower()
                horario['disponible'] = disponibilidad == 'disponible'
            
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

@reservas_bp.route('/api/buscar-horarios-disponibles')
def api_buscar_horarios_disponibles():
    """Búsqueda dinámica de horarios disponibles con filtros opcionales.
    
    Parámetros GET (todos opcionales):
    - id_servicio: int
    - id_empleado: int  
    - fecha: YYYY-MM-DD
    """
    # Actualizar automáticamente los horarios vencidos antes de consultar
    actualizar_horarios_vencidos()
    
    id_servicio = request.args.get('id_servicio')
    id_empleado = request.args.get('id_empleado')
    fecha = request.args.get('fecha')
    
    conn = None
    cursor = None
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Query base
        query = """
            SELECT 
                h.id_horario,
                h.id_empleado,
                h.fecha,
                TIME_FORMAT(h.hora_inicio, '%%H:%%i') as hora_inicio,
                TIME_FORMAT(h.hora_fin, '%%H:%%i') as hora_fin,
                h.disponibilidad,
                h.estado,
                CONCAT(e.nombres, ' ', e.apellidos) as profesional,
                es.nombre as especialidad
            FROM HORARIO h
            INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
            LEFT JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
            WHERE LOWER(h.disponibilidad) = 'disponible'
                AND LOWER(h.estado) = 'activo'
        """
        
        params = []
        
        # Filtro por servicio (buscar empleados de la especialidad del servicio)
        if id_servicio:
            query += """
                AND e.id_especialidad = (
                    SELECT id_especialidad 
                    FROM SERVICIO 
                    WHERE id_servicio = %s
                )
            """
            params.append(int(id_servicio))
        
        # Filtro por empleado
        if id_empleado:
            query += " AND h.id_empleado = %s"
            params.append(int(id_empleado))
        
        # Filtro por fecha
        if fecha:
            query += " AND h.fecha = %s"
            params.append(fecha)
        # Si NO hay fecha, mostrar TODOS los horarios (sin filtro de fecha)
        
        # Ordenar por ID de horario
        query += " ORDER BY h.id_horario ASC"
        
        cursor.execute(query, params)
        horarios = cursor.fetchall()
        
        # Convertir fechas a string
        for h in horarios:
            if h.get('fecha'):
                h['fecha'] = h['fecha'].strftime('%Y-%m-%d')
        
        return jsonify({'horarios': horarios})
        
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
    - disponibilidad: string (Disponible, Ocupado, Completado)
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
        
        # Query base - NO filtrar por disponibilidad ni estado en WHERE inicial
        query = """
            SELECT 
                h.id_horario,
                h.id_empleado,
                h.fecha,
                TIME_FORMAT(h.hora_inicio, '%%H:%%i') as hora_inicio,
                TIME_FORMAT(h.hora_fin, '%%H:%%i') as hora_fin,
                h.disponibilidad,
                h.estado,
                CONCAT(e.nombres, ' ', e.apellidos) as profesional,
                COALESCE(es.nombre, '-') as especialidad,
                r.nombre as rol
            FROM HORARIO h
            INNER JOIN EMPLEADO e ON h.id_empleado = e.id_empleado
            LEFT JOIN ESPECIALIDAD es ON e.id_especialidad = es.id_especialidad
            LEFT JOIN ROL r ON e.id_rol = r.id_rol
            WHERE 1=1
        """
        
        params = []
        
        # Filtro por empleado
        if id_empleado:
            query += " AND h.id_empleado = %s"
            params.append(int(id_empleado))
        
        # Filtro por disponibilidad
        if disponibilidad:
            query += " AND LOWER(h.disponibilidad) = LOWER(%s)"
            params.append(disponibilidad)
        
        # Filtro por rango de fechas
        if fecha_desde:
            query += " AND h.fecha >= %s"
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND h.fecha <= %s"
            params.append(fecha_hasta)
        
        # Filtro por rol del empleado
        if rol:
            query += " AND r.nombre = %s"
            params.append(rol)
        
        # Ordenar por ID de horario
        query += " ORDER BY h.id_horario ASC"
        
        cursor.execute(query, params)
        horarios = cursor.fetchall()
        
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
        return render_template('GenerarReserva.html', servicios=servicios, medicos=medicos, programaciones=programaciones)
    
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

        # Crear notificación para el paciente sobre la reprogramación
        try:
            id_paciente = reserva.get('id_paciente')
            estado_actual = reserva.get('estado', 'Pendiente')
            
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
        
        id_reserva = res.get('id_reserva')
        
        # Obtener el estado de la reserva recién creada (normalmente será 'Pendiente')
        conexion_notif = obtener_conexion()
        try:
            with conexion_notif.cursor() as cursor:
                cursor.execute("SELECT estado FROM RESERVA WHERE id_reserva = %s", (id_reserva,))
                reserva_data = cursor.fetchone()
                estado_reserva = reserva_data.get('estado', 'Pendiente') if reserva_data else 'Pendiente'
        except Exception as e:
            print(f"Error obteniendo estado de reserva: {e}")
            estado_reserva = 'Pendiente'
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
                WHERE LOWER(estado) = 'activo'
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
                WHERE LOWER(e.estado) = 'activo'
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
                      AND LOWER(e.estado) = 'activo'
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
                      AND LOWER(e.estado) = 'activo'
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
    id_servicio = data.get('id_servicio')  # Opcional para reserva de CITA
    id_horario = data.get('id_horario')

    # Validaciones
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
            # Si NO hay id_servicio, es una reserva de CITA (id_servicio NULL)
            # Si SÍ hay id_servicio, es una reserva de SERVICIO
            if id_servicio:
                sql_prog = """
                    INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin, estado, id_servicio, id_horario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_prog, (fecha, hora_inicio, hora_fin, 'disponible', id_servicio, id_horario))
            else:
                # Reserva de CITA - sin servicio
                sql_prog = """
                    INSERT INTO PROGRAMACION (fecha, hora_inicio, hora_fin, estado, id_horario)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_prog, (fecha, hora_inicio, hora_fin, 'disponible', id_horario))
            
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
            cursor.execute(sql_reserva, (fecha_actual, hora_actual, 1, 'Pendiente', id_paciente, id_programacion))
            conexion.commit()
            id_reserva = cursor.lastrowid

            # Actualizar disponibilidad del horario
            sql_update_horario = """
                UPDATE HORARIO SET disponibilidad = 'Ocupado' WHERE id_horario = %s
            """
            cursor.execute(sql_update_horario, (id_horario,))
            conexion.commit()

        tipo_reserva = 'servicio' if id_servicio else 'cita'

        # Crear notificaciones para el paciente
        try:
            # 1. Notificación de confirmación de creación
            Notificacion.crear_confirmacion_reserva(id_paciente, id_reserva)
        except Exception as e:
            print(f"Error creando notificación de confirmación: {e}")
        
        try:
            # 2. Notificación del estado actual de la reserva (Pendiente)
            Notificacion.crear_notificacion_estado_reserva(id_paciente, id_reserva, 'Pendiente')
        except Exception as e:
            print(f"Error creando notificación de estado: {e}")

        # 3. Programar recordatorio para la fecha/hora de la cita
        try:
            Notificacion.crear_recordatorio_cita(id_paciente, id_reserva, fecha, hora_inicio)
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
    """API que retorna todas las reservas del paciente autenticado"""
    print("\n[API mis-reservas] Inicio de solicitud")
    
    if 'usuario_id' not in session:
        print("[API mis-reservas] Error: No autenticado")
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        print("[API mis-reservas] Error: No es paciente")
        return jsonify({'error': 'Acceso no autorizado'}), 403

    conexion = None
    try:
        # Obtener el id_paciente del usuario
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
            sql = """
                SELECT r.id_reserva,
                       r.fecha_registro,
                       r.hora_registro,
                       r.tipo,
                       r.estado as estado_reserva,
                       p.fecha as fecha_cita,
                       TIME_FORMAT(p.hora_inicio, '%%H:%%i') as hora_inicio,
                       TIME_FORMAT(p.hora_fin, '%%H:%%i') as hora_fin,
                       COALESCE(s.nombre, 'Cita Médica') as servicio,
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
                ORDER BY p.fecha DESC, p.hora_inicio DESC
            """
            print(f"[API mis-reservas] Ejecutando SQL para paciente {id_paciente}")
            cursor.execute(sql, (id_paciente,))
            reservas = cursor.fetchall()
            
            print(f"[API mis-reservas] Encontradas {len(reservas)} reservas")
            
            # Convertir fechas a string
            for i, reserva in enumerate(reservas):
                try:
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
                    
                    if reserva.get('fecha_cita'):
                        if hasattr(reserva['fecha_cita'], 'strftime'):
                            reserva['fecha_cita'] = reserva['fecha_cita'].strftime('%Y-%m-%d')
                        else:
                            reserva['fecha_cita'] = str(reserva['fecha_cita'])
                except Exception as e:
                    print(f"[API mis-reservas] Error procesando reserva {i}: {str(e)}")
                    raise

            print(f"[API mis-reservas] Retornando {len(reservas)} reservas")
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
                  AND LOWER(c.estado) = 'completada'
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
                               TIME_FORMAT(e.hora_examen, '%%H:%%i') as hora_examen,
                               e.observacion,
                               e.estado,
                               'Examen Médico' as tipo_examen
                        FROM EXAMEN e
                        WHERE e.id_reserva = %s
                        ORDER BY e.fecha_examen DESC, e.hora_examen DESC
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
                       TIME_FORMAT(e.hora_examen, '%%H:%%i') as hora_examen,
                       e.observacion,
                       e.estado,
                       r.id_reserva,
                       'Examen Médico' as tipo_examen
                FROM EXAMEN e
                INNER JOIN RESERVA r ON e.id_reserva = r.id_reserva
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
    """API para crear un nuevo examen"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.get_json() or {}
    id_reserva = data.get('id_reserva')
    fecha_examen = data.get('fecha_examen')
    hora_examen = data.get('hora_examen')
    estado = data.get('estado', 'Pendiente')
    observacion = data.get('observacion', '')

    # Validaciones
    if not id_reserva:
        return jsonify({'error': 'ID de reserva es requerido'}), 400
    
    if not fecha_examen:
        return jsonify({'error': 'Fecha del examen es requerida'}), 400
    
    if not hora_examen:
        return jsonify({'error': 'Hora del examen es requerida'}), 400

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

            # Insertar el nuevo examen
            sql_insert = """
                INSERT INTO EXAMEN (fecha_examen, hora_examen, observacion, estado, id_reserva)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (fecha_examen, hora_examen, observacion, estado, id_reserva))
            conexion.commit()
            
            id_examen = cursor.lastrowid

            return jsonify({
                'success': True,
                'id_examen': id_examen,
                'message': 'Examen creado exitosamente'
            }), 201

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"[API crear-examen] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al crear examen: {str(e)}'}), 500
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
    tipo_operacion = data.get('tipo_operacion')
    fecha_operacion = data.get('fecha_operacion')
    hora_operacion = data.get('hora_operacion')
    estado = data.get('estado', 'Programada')
    descripcion = data.get('descripcion', '')

    # Validaciones
    if not id_reserva:
        return jsonify({'error': 'ID de reserva es requerido'}), 400
    
    if not tipo_operacion:
        return jsonify({'error': 'Tipo de operación es requerido'}), 400
    
    if not fecha_operacion:
        return jsonify({'error': 'Fecha de operación es requerida'}), 400
    
    if not hora_operacion:
        return jsonify({'error': 'Hora de operación es requerida'}), 400
    
    if not descripcion:
        return jsonify({'error': 'Descripción es requerida'}), 400

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

            # Insertar la nueva operación
            sql_insert = """
                INSERT INTO OPERACION (tipo_operacion, fecha_operacion, hora_operacion, descripcion, estado, id_reserva)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (tipo_operacion, fecha_operacion, hora_operacion, descripcion, estado, id_reserva))
            conexion.commit()
            
            id_operacion = cursor.lastrowid

            return jsonify({
                'success': True,
                'id_operacion': id_operacion,
                'message': 'Operación creada exitosamente'
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
