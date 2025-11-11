"""
Rutas para el módulo de médicos
Gestiona el panel médico y sus funcionalidades
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from functools import wraps
from datetime import datetime, date, timedelta
from bd import obtener_conexion

# Crear el Blueprint
medico_bp = Blueprint('medico', __name__, url_prefix='/medico')

# Funciones auxiliares para obtener datos
def obtener_estadisticas_medico(id_empleado):
    """
    Obtiene las estadísticas del médico desde la base de datos
    Navega a través de CITA -> RESERVA -> PROGRAMACION -> HORARIO -> EMPLEADO
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Citas de hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            INNER JOIN HORARIO h ON p.id_horario = h.id_horario
            WHERE h.id_empleado = %s
            AND c.fecha_cita = CURDATE()
        """, (id_empleado,))
        citas_hoy = cursor.fetchone()['total']
        
        # Citas pendientes hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            INNER JOIN HORARIO h ON p.id_horario = h.id_horario
            WHERE h.id_empleado = %s
            AND c.fecha_cita = CURDATE()
            AND c.estado = 'Pendiente'
        """, (id_empleado,))
        citas_pendientes = cursor.fetchone()['total']
        
        # Citas completadas hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            INNER JOIN HORARIO h ON p.id_horario = h.id_horario
            WHERE h.id_empleado = %s
            AND c.fecha_cita = CURDATE()
            AND c.estado = 'Completada'
        """, (id_empleado,))
        citas_completadas = cursor.fetchone()['total']
        
        # Pacientes atendidos esta semana
        cursor.execute("""
            SELECT COUNT(DISTINCT r.id_paciente) as total
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            INNER JOIN HORARIO h ON p.id_horario = h.id_horario
            WHERE h.id_empleado = %s
            AND YEARWEEK(c.fecha_cita, 1) = YEARWEEK(CURDATE(), 1)
        """, (id_empleado,))
        pacientes_semana = cursor.fetchone()['total']
        
        # Diagnósticos pendientes (citas sin diagnóstico)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
            INNER JOIN HORARIO h ON p.id_horario = h.id_horario
            WHERE h.id_empleado = %s
            AND c.estado = 'Pendiente'
        """, (id_empleado,))
        diagnosticos_pendientes = cursor.fetchone()['total']
        
        return {
            'citas_hoy': citas_hoy,
            'citas_pendientes': citas_pendientes,
            'citas_completadas': citas_completadas,
            'pacientes_semana': pacientes_semana,
            'diagnosticos_pendientes': diagnosticos_pendientes
        }
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        import traceback
        traceback.print_exc()
        return {
            'citas_hoy': 0,
            'citas_pendientes': 0,
            'citas_completadas': 0,
            'pacientes_semana': 0,
            'diagnosticos_pendientes': 0
        }
    finally:
        if conexion:
            conexion.close()


def obtener_citas_hoy(id_empleado):
    """
    Obtiene las citas del día actual del médico
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener citas de hoy con información del paciente
        cursor.execute("""
            SELECT 
                c.id_cita,
                c.estado,
                c.fecha_cita,
                c.hora_inicio,
                c.hora_fin,
                p.nombres,
                p.apellidos,
                s.nombre as tipo_servicio
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
            INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            WHERE h.id_empleado = %s
            AND c.fecha_cita = CURDATE()
            ORDER BY c.hora_inicio
        """, (id_empleado,))
        
        citas = cursor.fetchall()
        
        # Formatear los datos
        citas_formateadas = []
        for cita in citas:
            # Formatear hora de inicio
            if cita['hora_inicio']:
                if isinstance(cita['hora_inicio'], str):
                    hora_obj = datetime.strptime(cita['hora_inicio'], '%H:%M:%S').time()
                elif isinstance(cita['hora_inicio'], timedelta):
                    # Convertir timedelta a time
                    hora_obj = (datetime.min + cita['hora_inicio']).time()
                else:
                    hora_obj = cita['hora_inicio']
                hora = hora_obj.strftime('%H:%M')
            else:
                hora = 'N/A'
            
            # Nombre completo del paciente
            nombre_completo = f"{cita['nombres']} {cita['apellidos']}"
            
            # Tipo de servicio
            tipo_consulta = cita['tipo_servicio'] if cita['tipo_servicio'] else 'Consulta General'
            
            citas_formateadas.append({
                'id': cita['id_cita'],
                'paciente': nombre_completo,
                'hora': hora,
                'hora_inicio': cita['hora_inicio'],
                'hora_fin': cita['hora_fin'],
                'tipo': tipo_consulta,
                'estado': cita['estado']
            })
        
        return citas_formateadas
        
    except Exception as e:
        print(f"Error al obtener citas de hoy: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conexion:
            conexion.close()


def obtener_horarios_medico(id_empleado):
    """
    Obtiene los horarios del médico desde la tabla HORARIO organizados por día de la semana
    """
    from datetime import datetime, timedelta
    
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener fecha de inicio de la semana actual (Lunes)
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        
        print(f"DEBUG - ID Empleado: {id_empleado}")
        print(f"DEBUG - Semana actual: {inicio_semana.date()} a {fin_semana.date()}")
        
        cursor.execute("""
            SELECT fecha, hora_inicio, hora_fin, activo
            FROM HORARIO
            WHERE id_empleado = %s 
            AND activo = 1
            AND fecha BETWEEN %s AND %s
            ORDER BY fecha, hora_inicio
        """, (id_empleado, inicio_semana.date(), fin_semana.date()))
        
        horarios = cursor.fetchall()
        print(f"DEBUG - Horarios encontrados: {len(horarios)}")
        print(f"DEBUG - Datos horarios: {horarios[:3] if horarios else 'Ninguno'}")
        
        # Organizar horarios por día de la semana
        horarios_por_dia = {}
        for horario in horarios:
            # Obtener valores del diccionario
            fecha_raw = horario['fecha']
            hora_inicio_raw = horario['hora_inicio']
            hora_fin_raw = horario['hora_fin']
            
            # Convertir fecha a objeto date si es necesario
            if isinstance(fecha_raw, str):
                from datetime import datetime as dt
                fecha = dt.strptime(fecha_raw, '%Y-%m-%d').date()
            else:
                fecha = fecha_raw
            
            # Convertir timedelta a time si es necesario
            if isinstance(hora_inicio_raw, timedelta):
                hora_inicio = (datetime.min + hora_inicio_raw).time()
            else:
                hora_inicio = hora_inicio_raw
                
            if isinstance(hora_fin_raw, timedelta):
                hora_fin = (datetime.min + hora_fin_raw).time()
            else:
                hora_fin = hora_fin_raw
            
            dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
            
            if dia_semana not in horarios_por_dia:
                horarios_por_dia[dia_semana] = {
                    'fecha': fecha,
                    'bloques': []
                }
            
            horarios_por_dia[dia_semana]['bloques'].append({
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin
            })
        
        print(f"DEBUG - Horarios organizados: {horarios_por_dia}")
        return horarios_por_dia
        
    except Exception as e:
        print(f"Error al obtener horarios: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        if conexion:
            conexion.close()


def obtener_citas_semana(id_empleado):
    """
    Obtiene las citas/reservas del médico para la semana actual
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener fecha de inicio de la semana actual (Lunes)
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        
        cursor.execute("""
            SELECT 
                c.id_cita,
                c.fecha_cita,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                p.nombres,
                p.apellidos,
                s.nombre as tipo_servicio
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
            INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            WHERE h.id_empleado = %s
            AND c.fecha_cita BETWEEN %s AND %s
            AND c.estado != 'Cancelada'
            ORDER BY c.fecha_cita, c.hora_inicio
        """, (id_empleado, inicio_semana.date(), fin_semana.date()))
        
        citas = cursor.fetchall()
        
        # Organizar citas por día y hora - CADA CITA SE COLOCA EN TODAS LAS HORAS QUE OCUPA
        citas_calendario = {}
        for cita in citas:
            fecha = cita['fecha_cita']
            dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
            
            # Convertir hora_inicio de timedelta a time
            if isinstance(cita['hora_inicio'], timedelta):
                hora_inicio = (datetime.min + cita['hora_inicio']).time()
            else:
                hora_inicio = cita['hora_inicio']
            
            # Convertir hora_fin de timedelta a time
            if isinstance(cita['hora_fin'], timedelta):
                hora_fin = (datetime.min + cita['hora_fin']).time()
            else:
                hora_fin = cita['hora_fin']
            
            # Calcular duración en horas (redondeado hacia arriba)
            hora_inicio_num = hora_inicio.hour + hora_inicio.minute / 60
            hora_fin_num = hora_fin.hour + hora_fin.minute / 60
            duracion_horas = hora_fin_num - hora_inicio_num
            
            # Agregar la cita a TODAS las horas que ocupa
            hora_actual = hora_inicio.hour
            hora_final = hora_fin.hour
            
            # Si la cita termina a las XX:00 exactas, no incluir esa hora
            if hora_fin.minute == 0:
                hora_final = hora_fin.hour - 1
            
            while hora_actual <= hora_final:
                clave = f"{dia_semana}_{hora_actual}"
                
                if clave not in citas_calendario:
                    citas_calendario[clave] = []
                
                # Solo agregar una vez por hora (evitar duplicados)
                cita_info = {
                    'id': cita['id_cita'],
                    'paciente': f"{cita['nombres']} {cita['apellidos']}",
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'duracion_horas': duracion_horas,
                    'tipo': cita['tipo_servicio'] if cita['tipo_servicio'] else 'Consulta',
                    'estado': cita['estado'],
                    'es_hora_inicio': (hora_actual == hora_inicio.hour)  # Marcar si es la primera hora
                }
                
                # Verificar si esta cita ya está en esta hora (evitar duplicados)
                ya_existe = any(c['id'] == cita_info['id'] for c in citas_calendario[clave])
                if not ya_existe:
                    citas_calendario[clave].append(cita_info)
                
                hora_actual += 1
        
        return citas_calendario
        
    except Exception as e:
        print(f"Error al obtener citas de la semana: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        if conexion:
            conexion.close()


def obtener_mis_pacientes(id_empleado):
    """
    Obtiene la lista de pacientes únicos que han tenido citas con este médico
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        cursor.execute("""
            SELECT DISTINCT
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad,
                p.fecha_nacimiento,
                MAX(c.fecha_cita) as ultima_cita,
                COUNT(c.id_cita) as total_citas
            FROM PACIENTE p
            INNER JOIN RESERVA r ON p.id_paciente = r.id_paciente
            INNER JOIN CITA c ON r.id_reserva = c.id_reserva
            INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
            INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
            WHERE h.id_empleado = %s
            GROUP BY p.id_paciente, p.nombres, p.apellidos, 
                     p.documento_identidad, p.fecha_nacimiento
            ORDER BY MAX(c.fecha_cita) DESC
        """, (id_empleado,))
        
        pacientes = cursor.fetchall()
        
        # Calcular edad
        from datetime import datetime
        pacientes_formateados = []
        for p in pacientes:
            edad = 'N/A'
            if p['fecha_nacimiento']:
                hoy = datetime.now().date()
                if isinstance(p['fecha_nacimiento'], str):
                    fecha_nac = datetime.strptime(p['fecha_nacimiento'], '%Y-%m-%d').date()
                else:
                    fecha_nac = p['fecha_nacimiento']
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            
            nombre_completo = f"{p['nombres']} {p['apellidos']}"
                
            pacientes_formateados.append({
                'id_paciente': p['id_paciente'],
                'nombre_completo': nombre_completo,
                'dni': p['documento_identidad'],
                'edad': edad,
                'ultima_cita': p['ultima_cita'],
                'total_citas': p['total_citas']
            })
        
        return pacientes_formateados
        
    except Exception as e:
        print(f"Error al obtener pacientes: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conexion:
            conexion.close()


def obtener_citas_pendientes_diagnostico(id_empleado):
    """
    Obtiene las citas pendientes que necesitan diagnóstico
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        print(f"DEBUG - Buscando citas pendientes para empleado: {id_empleado}")
        
        cursor.execute("""
            SELECT 
                c.id_cita,
                c.fecha_cita,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad,
                s.nombre as tipo_servicio
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
            INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            WHERE h.id_empleado = %s
            AND c.estado = 'Pendiente'
            ORDER BY c.fecha_cita DESC, c.hora_inicio DESC
        """, (id_empleado,))
        
        citas = cursor.fetchall()
        print(f"DEBUG - Citas pendientes encontradas: {len(citas)}")
        
        citas_formateadas = []
        for cita in citas:
            nombre_completo = f"{cita['nombres']} {cita['apellidos']}"
            
            # Formatear hora de inicio - manejar timedelta
            if cita['hora_inicio']:
                if isinstance(cita['hora_inicio'], str):
                    hora_obj = datetime.strptime(cita['hora_inicio'], '%H:%M:%S').time()
                elif isinstance(cita['hora_inicio'], timedelta):
                    # Convertir timedelta a time
                    hora_obj = (datetime.min + cita['hora_inicio']).time()
                else:
                    hora_obj = cita['hora_inicio']
                hora = hora_obj.strftime('%H:%M')
            else:
                hora = 'N/A'
            
            # Formatear fecha
            if isinstance(cita['fecha_cita'], str):
                fecha_obj = datetime.strptime(cita['fecha_cita'], '%Y-%m-%d').date()
            else:
                fecha_obj = cita['fecha_cita']
                
            citas_formateadas.append({
                'id_cita': cita['id_cita'],
                'id_paciente': cita['id_paciente'],
                'paciente': nombre_completo,
                'dni': cita['documento_identidad'],
                'fecha': fecha_obj,
                'hora': hora,
                'tipo': cita['tipo_servicio'] if cita['tipo_servicio'] else 'Consulta General'
            })
        
        print(f"DEBUG - Citas formateadas: {len(citas_formateadas)}")
        return citas_formateadas
        
    except Exception as e:
        print(f"Error al obtener citas pendientes: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conexion:
            conexion.close()


def obtener_historial_paciente(id_paciente, id_empleado):
    """
    Obtiene el historial completo de citas de un paciente con el médico
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        cursor.execute("""
            SELECT 
                c.id_cita,
                c.fecha_cita,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                c.diagnostico,
                c.observaciones
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION prog ON r.id_programacion = prog.id_programacion
            INNER JOIN HORARIO h ON prog.id_horario = h.id_horario
            WHERE r.id_paciente = %s
            AND h.id_empleado = %s
            ORDER BY c.fecha_cita DESC, c.hora_inicio DESC
        """, (id_paciente, id_empleado))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []
    finally:
        if conexion:
            conexion.close()


# Decorador para verificar que el usuario es médico
def medico_required(f):
    """
    Decorador que verifica si el usuario está autenticado y tiene rol de médico (id_rol = 2)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está autenticado
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('cuentas.login'))

        # Verificar si el usuario es médico (id_rol = 2)
        if session.get('id_rol') != 2:
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function


@medico_bp.route('/')
@medico_bp.route('/panel')
@medico_required
def panel():
    """
    Ruta principal del panel médico
    Muestra el dashboard o el subsistema solicitado
    """
    subsistema = request.args.get('subsistema', None)
    id_empleado = session.get('id_empleado')

    # Obtener información del médico desde la sesión
    usuario = {
        'id': session.get('usuario_id'),
        'nombre': session.get('nombre_usuario'),
        'email': session.get('email_usuario'),
        'rol': session.get('rol', 'Médico'),
        'id_empleado': id_empleado
    }

    # Obtener estadísticas del médico
    stats = obtener_estadisticas_medico(id_empleado)
    
    # Obtener citas de hoy
    citas_hoy = obtener_citas_hoy(id_empleado)
    
    # Datos adicionales según el subsistema
    horarios_medico = []
    citas_semana = {}
    mis_pacientes = []
    citas_pendientes = []
    
    if subsistema == 'agenda':
        horarios_medico = obtener_horarios_medico(id_empleado)
        citas_semana = obtener_citas_semana(id_empleado)
    elif subsistema == 'pacientes':
        mis_pacientes = obtener_mis_pacientes(id_empleado)
    elif subsistema == 'diagnosticos':
        citas_pendientes = obtener_citas_pendientes_diagnostico(id_empleado)

    return render_template(
        'panel_medico.html',
        subsistema=subsistema,
        usuario=usuario,
        stats=stats,
        citas_hoy=citas_hoy,
        horarios_medico=horarios_medico,
        citas_semana=citas_semana,
        mis_pacientes=mis_pacientes,
        citas_pendientes=citas_pendientes
    )


@medico_bp.route('/dashboard')
@medico_required
def dashboard():
    """
    Dashboard principal del médico con estadísticas y resumen
    """
    # Aquí se obtendrían las estadísticas desde la base de datos
    stats = {
        'citas_hoy': 8,
        'citas_pendientes': 2,
        'citas_completadas': 6,
        'pacientes_semana': 24,
        'diagnosticos_pendientes': 5,
        'calificacion_promedio': 4.9
    }

    return render_template(
        'panel_medico.html',
        subsistema=None,
        stats=stats
    )


@medico_bp.route('/agenda')
@medico_required
def agenda():
    """
    Vista de agenda médica con calendario de citas
    """
    fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))

    # Aquí se obtendrían las citas desde la base de datos
    # Por ahora retornamos datos de ejemplo

    return render_template(
        'panel_medico.html',
        subsistema='agenda',
        fecha=fecha
    )


@medico_bp.route('/pacientes')
@medico_required
def pacientes():
    """
    Lista de pacientes del médico
    """
    id_empleado = session.get('id_empleado')
    busqueda = request.args.get('q', '')

    mis_pacientes = obtener_mis_pacientes(id_empleado)

    return render_template(
        'panel_medico.html',
        subsistema='pacientes',
        busqueda=busqueda,
        mis_pacientes=mis_pacientes
    )


@medico_bp.route('/historial_paciente/<int:id_paciente>')
@medico_required
def historial_paciente(id_paciente):
    """
    Obtiene el historial de un paciente específico
    """
    id_empleado = session.get('id_empleado')
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener datos del paciente
        cursor.execute("""
            SELECT 
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad,
                p.fecha_nacimiento
            FROM PACIENTE p
            WHERE p.id_paciente = %s
        """, (id_paciente,))
        
        paciente = cursor.fetchone()
        
        if not paciente:
            return jsonify({'success': False, 'message': 'Paciente no encontrado'}), 404
        
        # Calcular edad
        from datetime import datetime
        edad = 'N/A'
        if paciente['fecha_nacimiento']:
            hoy = datetime.now().date()
            if isinstance(paciente['fecha_nacimiento'], str):
                fecha_nac = datetime.strptime(paciente['fecha_nacimiento'], '%Y-%m-%d').date()
            else:
                fecha_nac = paciente['fecha_nacimiento']
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        
        nombre_completo = f"{paciente['nombres']} {paciente['apellidos']}"
        
        # Obtener historial de citas
        historial = obtener_historial_paciente(id_paciente, id_empleado)
        
        # Formatear historial
        historial_formateado = []
        for cita in historial:
            if cita['hora_inicio']:
                if isinstance(cita['hora_inicio'], str):
                    hora_obj = datetime.strptime(cita['hora_inicio'], '%H:%M:%S').time()
                elif isinstance(cita['hora_inicio'], timedelta):
                    # Convertir timedelta a time
                    hora_obj = (datetime.min + cita['hora_inicio']).time()
                else:
                    hora_obj = cita['hora_inicio']
                hora = hora_obj.strftime('%H:%M')
            else:
                hora = 'N/A'
                
            historial_formateado.append({
                'id_cita': cita['id_cita'],
                'fecha': cita['fecha_cita'].strftime('%d/%m/%Y') if cita['fecha_cita'] else 'N/A',
                'hora': hora,
                'estado': cita['estado'],
                'diagnostico': cita['diagnostico'] if cita['diagnostico'] else '',
                'observaciones': cita['observaciones'] if cita['observaciones'] else ''
            })
        
        return jsonify({
            'success': True,
            'paciente': {
                'nombre': nombre_completo,
                'dni': paciente['documento_identidad'],
                'edad': edad
            },
            'historial': historial_formateado
        })
        
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conexion:
            conexion.close()


@medico_bp.route('/paciente/<int:paciente_id>')
@medico_required
def ver_paciente(paciente_id):
    """
    Ver detalles completos de un paciente específico
    """
    # Aquí se obtendría la información completa del paciente
    # incluyendo historial médico, diagnósticos, etc.

    return render_template(
        'medico_detalle_paciente.html',
        paciente_id=paciente_id
    )


@medico_bp.route('/diagnosticos')
@medico_bp.route('/diagnosticos/nuevo')
@medico_required
def diagnosticos():
    """
    Formulario para registrar diagnósticos
    """
    return render_template(
        'panel_medico.html',
        subsistema='diagnosticos'
    )


@medico_bp.route('/diagnosticos/guardar', methods=['POST'])
@medico_required
def guardar_diagnostico():
    """
    Guarda un diagnóstico para una cita y la marca como completada
    """
    conexion = None
    try:
        id_cita = request.form.get('id_cita')
        diagnostico = request.form.get('diagnostico')
        observaciones = request.form.get('observaciones', '')
        
        if not id_cita or not diagnostico:
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Actualizar la cita con el diagnóstico y cambiar estado a Completada
        cursor.execute("""
            UPDATE CITA 
            SET diagnostico = %s, 
                observaciones = %s, 
                estado = 'Completada'
            WHERE id_cita = %s
        """, (diagnostico, observaciones, id_cita))
        
        conexion.commit()
        
        return jsonify({'success': True, 'message': 'Diagnóstico guardado exitosamente'})

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al guardar diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error al guardar: {str(e)}'}), 500
    finally:
        if conexion:
            conexion.close()


@medico_bp.route('/historial')
@medico_required
def historial():
    """
    Vista de historial médico de pacientes
    """
    return render_template(
        'panel_medico.html',
        subsistema='historial'
    )


@medico_bp.route('/recetas')
@medico_required
def recetas():
    """
    Gestión de recetas médicas
    """
    return render_template(
        'panel_medico.html',
        subsistema='recetas'
    )


@medico_bp.route('/recetas/nueva', methods=['POST'])
@medico_required
def nueva_receta():
    """
    Crea una nueva receta médica
    """
    try:
        paciente_id = request.form.get('paciente_id')
        medicamentos = request.form.get('medicamentos')
        dosis = request.form.get('dosis')
        duracion = request.form.get('duracion')
        indicaciones = request.form.get('indicaciones')
        medico_id = session.get('id_empleado')

        # Aquí se guardaría en la base de datos

        flash('Receta generada exitosamente', 'success')
        return redirect(url_for('medico.recetas'))

    except Exception as e:
        flash(f'Error al generar la receta: {str(e)}', 'danger')
        return redirect(url_for('medico.recetas'))


@medico_bp.route('/reportes')
@medico_required
def reportes():
    """
    Generación de reportes médicos
    """
    return render_template(
        'panel_medico.html',
        subsistema='reportes'
    )


@medico_bp.route('/notificaciones')
@medico_required
def notificaciones():
    """
    Centro de notificaciones del médico
    """
    return render_template(
        'panel_medico.html',
        subsistema='notificaciones'
    )


# API Endpoints para consultas AJAX
@medico_bp.route('/api/citas-hoy')
@medico_required
def api_citas_hoy():
    """
    Retorna las citas del día actual en formato JSON
    """
    medico_id = session.get('id_empleado')

    # Aquí se obtendrían las citas desde la base de datos
    citas = [
        {
            'id': 1,
            'paciente': 'Juan Pérez García',
            'hora': '10:00 AM',
            'tipo': 'Consulta General',
            'estado': 'pendiente'
        },
        {
            'id': 2,
            'paciente': 'María García López',
            'hora': '09:30 AM',
            'tipo': 'Control de Presión',
            'estado': 'completada'
        }
    ]

    return jsonify({'success': True, 'citas': citas})


@medico_bp.route('/api/estadisticas')
@medico_required
def api_estadisticas():
    """
    Retorna estadísticas del médico en formato JSON
    """
    medico_id = session.get('id_empleado')

    # Aquí se calcularían las estadísticas desde la base de datos
    stats = {
        'citas_hoy': 8,
        'citas_semana': 24,
        'pacientes_activos': 156,
        'diagnosticos_mes': 42,
        'calificacion': 4.9
    }

    return jsonify({'success': True, 'estadisticas': stats})


@medico_bp.route('/api/buscar-paciente')
@medico_required
def api_buscar_paciente():
    """
    Busca pacientes por nombre o DNI
    """
    query = request.args.get('q', '')
    medico_id = session.get('id_empleado')

    # Aquí se buscarían los pacientes en la base de datos
    pacientes = []

    return jsonify({'success': True, 'pacientes': pacientes})


# Manejo de errores específico para el módulo médico
@medico_bp.errorhandler(404)
def medico_not_found(error):
    """
    Maneja errores 404 en el módulo médico
    """
    flash('La página solicitada no existe', 'warning')
    return redirect(url_for('medico.panel'))


@medico_bp.errorhandler(500)
def medico_server_error(error):
    """
    Maneja errores 500 en el módulo médico
    """
    flash('Ha ocurrido un error en el servidor. Por favor, intenta nuevamente', 'danger')
    return redirect(url_for('medico.panel'))
