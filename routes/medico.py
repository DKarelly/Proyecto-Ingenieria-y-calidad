"""
Rutas para el módulo de médicos
Gestiona el panel médico y sus funcionalidades
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from functools import wraps
from datetime import datetime, date, timedelta
from bd import obtener_conexion
from models.autorizacion_procedimiento import AutorizacionProcedimiento
from models.empleado import Empleado
from models.servicio import Servicio
from models.notificacion import Notificacion

# Crear el Blueprint
medico_bp = Blueprint('medico', __name__, url_prefix='/medico')

# Funciones auxiliares para obtener datos
def obtener_estadisticas_medico(id_empleado):
    """
    Obtiene las estadísticas del médico con una sola consulta optimizada
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # OPTIMIZACIÓN: Una sola consulta con SUBQUERYs en SELECT para todas las estadísticas
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) 
                 FROM CITA c
                 INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                 INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                 INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                 WHERE h.id_empleado = %s AND c.fecha_cita = CURDATE()) as citas_hoy,
                
                (SELECT COUNT(*) 
                 FROM CITA c
                 INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                 INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                 INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                 WHERE h.id_empleado = %s AND c.fecha_cita = CURDATE() AND c.estado = 'Pendiente') as citas_pendientes,
                
                (SELECT COUNT(*) 
                 FROM CITA c
                 INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                 INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                 INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                 WHERE h.id_empleado = %s AND c.fecha_cita = CURDATE() AND c.estado = 'Completada') as citas_completadas,
                
                (SELECT COUNT(DISTINCT r.id_paciente)
                 FROM CITA c
                 INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                 INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                 INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                 WHERE h.id_empleado = %s AND YEARWEEK(c.fecha_cita, 1) = YEARWEEK(CURDATE(), 1)) as pacientes_semana,
                
                (SELECT COUNT(*) 
                 FROM CITA c
                 INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
                 INNER JOIN PROGRAMACION p ON r.id_programacion = p.id_programacion
                 INNER JOIN HORARIO h ON p.id_horario = h.id_horario
                 WHERE h.id_empleado = %s AND c.estado = 'Pendiente') as diagnosticos_pendientes
        """, (id_empleado, id_empleado, id_empleado, id_empleado, id_empleado))
        
        result = cursor.fetchone()
        
        return {
            'citas_hoy': result['citas_hoy'],
            'citas_pendientes': result['citas_pendientes'],
            'citas_completadas': result['citas_completadas'],
            'pacientes_semana': result['pacientes_semana'],
            'diagnosticos_pendientes': result['diagnosticos_pendientes']
        }
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
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
    Obtiene las citas del día actual del médico (OPTIMIZADO)
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # OPTIMIZACIÓN: Usar STRAIGHT_JOIN para forzar orden óptimo de JOINs
        cursor.execute("""
            SELECT STRAIGHT_JOIN
                c.id_cita,
                c.estado,
                c.hora_inicio,
                c.hora_fin,
                p.nombres,
                p.apellidos,
                s.nombre as tipo_servicio
            FROM HORARIO h
            INNER JOIN PROGRAMACION prog ON h.id_horario = prog.id_horario
            INNER JOIN RESERVA r ON prog.id_programacion = r.id_programacion
            INNER JOIN CITA c ON r.id_reserva = c.id_reserva
            INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
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


def obtener_horarios_medico(id_empleado, offset_semana=0):
    """
    Obtiene los horarios del médico (OPTIMIZADO - índice en id_empleado, activo, fecha)
    offset_semana: número de semanas a avanzar (+) o retroceder (-) desde la semana actual
    """
    from datetime import datetime, timedelta
    
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener fecha de inicio de la semana (Lunes) con offset
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=offset_semana)
        fin_semana = inicio_semana + timedelta(days=6)
        
        # OPTIMIZACIÓN: Query más simple, filtrado directo por índice
        cursor.execute("""
            SELECT fecha, hora_inicio, hora_fin
            FROM HORARIO
            WHERE id_empleado = %s 
            AND activo = 1
            AND fecha BETWEEN %s AND %s
            ORDER BY fecha, hora_inicio
        """, (id_empleado, inicio_semana.date(), fin_semana.date()))
        
        horarios = cursor.fetchall()
        
        # OPTIMIZACIÓN: Organizar horarios por día de la semana
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
        
        # OPTIMIZACIÓN: Pre-calcular horas min/max aquí en lugar del template
        hora_min = 23
        hora_max = 0
        for dia_data in horarios_por_dia.values():
            for bloque in dia_data['bloques']:
                if bloque['hora_inicio'].hour < hora_min:
                    hora_min = bloque['hora_inicio'].hour
                if bloque['hora_fin'].hour > hora_max:
                    hora_max = bloque['hora_fin'].hour
        
        return {
            'horarios': horarios_por_dia,
            'hora_min': hora_min if horarios_por_dia else 8,
            'hora_max': hora_max if horarios_por_dia else 18
        }
        
    except Exception as e:
        print(f"Error al obtener horarios: {e}")
        return {'horarios': {}, 'hora_min': 8, 'hora_max': 18}
    finally:
        if conexion:
            conexion.close()


def obtener_citas_semana(id_empleado, offset_semana=0):
    """
    Obtiene las citas del médico para la semana (OPTIMIZADO)
    offset_semana: número de semanas a avanzar (+) o retroceder (-) desde la semana actual
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener fecha de inicio de la semana (Lunes) con offset
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=offset_semana)
        fin_semana = inicio_semana + timedelta(days=6)
        
        # OPTIMIZACIÓN: Iniciar desde HORARIO (tabla más pequeña filtrada por id_empleado)
        cursor.execute("""
            SELECT STRAIGHT_JOIN
                c.id_cita,
                c.fecha_cita,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                p.nombres,
                p.apellidos,
                s.nombre as tipo_servicio
            FROM HORARIO h
            INNER JOIN PROGRAMACION prog ON h.id_horario = prog.id_horario
            INNER JOIN RESERVA r ON prog.id_programacion = r.id_programacion
            INNER JOIN CITA c ON r.id_reserva = c.id_reserva
            INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            WHERE h.id_empleado = %s
            AND c.fecha_cita BETWEEN %s AND %s
            AND c.estado != 'Cancelada'
            ORDER BY c.fecha_cita, c.hora_inicio
        """, (id_empleado, inicio_semana.date(), fin_semana.date()))
        
        citas = cursor.fetchall()
        
        # OPTIMIZACIÓN: Pre-calcular y organizar citas con información completa
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
            
            # OPTIMIZACIÓN: Pre-calcular toda la info de la cita aquí
            duracion_minutos = (hora_fin.hour - hora_inicio.hour) * 60 + (hora_fin.minute - hora_inicio.minute)
            altura_px = max(1, int((duracion_minutos / 60) * 80))  # Pre-calcular altura en píxeles
            offset_minutos = hora_inicio.minute
            offset_px = int((offset_minutos / 60) * 80) if offset_minutos > 0 else 0
            
            # Solo agregar en la hora de inicio (más eficiente)
            clave = f"{dia_semana}_{hora_inicio.hour}"
            
            if clave not in citas_calendario:
                citas_calendario[clave] = []
            
            # Color según estado (pre-calculado)
            if cita['estado'] == 'Pendiente':
                color = '#f59e0b'
            elif cita['estado'] == 'Confirmada':
                color = '#3b82f6'
            else:
                color = '#10b981'
            
            citas_calendario[clave].append({
                'id': cita['id_cita'],
                'paciente': f"{cita['nombres']} {cita['apellidos']}",
                'hora_inicio_str': hora_inicio.strftime('%H:%M'),
                'hora_fin_str': hora_fin.strftime('%H:%M'),
                'tipo': cita['tipo_servicio'] if cita['tipo_servicio'] else 'Consulta',
                'estado': cita['estado'],
                'altura': altura_px,
                'offset': offset_px,
                'color': color
            })
        
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
    Obtiene pacientes únicos del médico (OPTIMIZADO)
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # OPTIMIZACIÓN: Empezar desde HORARIO filtrado, usar STRAIGHT_JOIN
        cursor.execute("""
            SELECT STRAIGHT_JOIN
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad,
                p.fecha_nacimiento,
                MAX(c.fecha_cita) as ultima_cita,
                COUNT(DISTINCT c.id_cita) as total_citas
            FROM HORARIO h
            INNER JOIN PROGRAMACION prog ON h.id_horario = prog.id_horario
            INNER JOIN RESERVA r ON prog.id_programacion = r.id_programacion
            INNER JOIN CITA c ON r.id_reserva = c.id_reserva
            INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            WHERE h.id_empleado = %s
            GROUP BY p.id_paciente, p.nombres, p.apellidos, 
                     p.documento_identidad, p.fecha_nacimiento
            ORDER BY ultima_cita DESC
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


def obtener_notificaciones_medico(id_empleado):
    """
    Obtiene las notificaciones del médico desde la tabla NOTIFICACION
    """
    try:
        print(f"🔍 [DEBUG obtener_notificaciones_medico] id_empleado: {id_empleado}")
        
        # Obtener id_usuario del empleado
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
        empleado = cursor.fetchone()
        conexion.close()
        
        print(f"🔍 [DEBUG obtener_notificaciones_medico] Empleado encontrado: {empleado}")
        
        if not empleado or not empleado.get('id_usuario'):
            print(f"⚠️ [DEBUG obtener_notificaciones_medico] No se encontró id_usuario para empleado {id_empleado}")
            return []
        
        id_usuario = empleado['id_usuario']
        print(f"🔍 [DEBUG obtener_notificaciones_medico] id_usuario: {id_usuario}")
        
        # Obtener notificaciones usando el modelo
        notificaciones = Notificacion.obtener_por_usuario(id_usuario)
        print(f"🔍 [DEBUG obtener_notificaciones_medico] Notificaciones obtenidas: {len(notificaciones) if notificaciones else 0}")
        
        if notificaciones:
            print(f"🔍 [DEBUG obtener_notificaciones_medico] Primera notificación: {notificaciones[0] if notificaciones else 'N/A'}")
        
        # Formatear notificaciones para el template
        notificaciones_formateadas = []
        for n in notificaciones:
            fecha_envio = n.get('fecha_envio')
            hora_envio = n.get('hora_envio')
            
            # Formatear fecha
            if fecha_envio:
                if isinstance(fecha_envio, str):
                    fecha_str = fecha_envio
                else:
                    fecha_str = fecha_envio.strftime('%Y-%m-%d')
            else:
                fecha_str = None
            
            # Formatear hora
            hora_str = None
            if hora_envio:
                if isinstance(hora_envio, str):
                    hora_str = hora_envio[:5] if len(hora_envio) >= 5 else hora_envio
                elif isinstance(hora_envio, timedelta):
                    # Convertir timedelta a formato HH:MM
                    total_seconds = int(hora_envio.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    hora_str = f"{hours:02d}:{minutes:02d}"
                elif hasattr(hora_envio, 'strftime'):
                    hora_str = hora_envio.strftime('%H:%M')
                else:
                    hora_str = str(hora_envio)[:5]
            
            notificaciones_formateadas.append({
                'id_notificacion': n.get('id_notificacion'),
                'titulo': n.get('titulo'),
                'mensaje': n.get('mensaje'),
                'tipo': n.get('tipo'),
                'fecha_envio': fecha_str,
                'hora_envio': hora_str,
                'leida': bool(n.get('leida')),
                'fecha_leida': n.get('fecha_leida').strftime('%Y-%m-%d %H:%M:%S') if n.get('fecha_leida') and hasattr(n.get('fecha_leida'), 'strftime') else (str(n.get('fecha_leida')) if n.get('fecha_leida') else None),
                'id_reserva': n.get('id_reserva'),
                'estado_reserva': n.get('estado_reserva')
            })
        
        return notificaciones_formateadas
    except Exception as e:
        print(f"Error obteniendo notificaciones del médico: {e}")
        import traceback
        traceback.print_exc()
        return []


def obtener_citas_pendientes_diagnostico(id_empleado):
    """
    Obtiene citas pendientes de diagnóstico (OPTIMIZADO)
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # OPTIMIZACIÓN: STRAIGHT_JOIN desde HORARIO, índice compuesto en (id_empleado, estado)
        cursor.execute("""
            SELECT STRAIGHT_JOIN
                c.id_cita,
                c.fecha_cita,
                c.hora_inicio,
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad,
                s.nombre as tipo_servicio
            FROM HORARIO h
            INNER JOIN PROGRAMACION prog ON h.id_horario = prog.id_horario
            INNER JOIN RESERVA r ON prog.id_programacion = r.id_programacion
            INNER JOIN CITA c ON r.id_reserva = c.id_reserva
            INNER JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            WHERE h.id_empleado = %s
            AND c.estado = 'Pendiente'
            ORDER BY c.fecha_cita DESC, c.hora_inicio DESC
            LIMIT 50
        """, (id_empleado,))
        
        citas = cursor.fetchall()
        
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
    Ruta principal del panel médico (OPTIMIZADO - carga solo datos necesarios)
    """
    subsistema = request.args.get('subsistema', None)
    id_empleado = session.get('id_empleado')

    # Información del médico desde la sesión (sin query)
    usuario = {
        'id': session.get('usuario_id'),
        'nombre': session.get('nombre_usuario'),
        'email': session.get('email_usuario'),
        'rol': session.get('rol', 'Médico'),
        'id_empleado': id_empleado
    }

    # Obtener offset de semana desde los parámetros de la URL
    offset_semana = request.args.get('offset_semana', 0, type=int)
    
    # Calcular fechas de la semana para mostrar en el header
    hoy = datetime.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=offset_semana)
    fin_semana = inicio_semana + timedelta(days=6)
    
    # OPTIMIZACIÓN: Cargar solo los datos necesarios según el subsistema
    if subsistema == 'agenda':
        # Solo agenda: estadísticas + citas hoy + horarios + citas semana
        stats = obtener_estadisticas_medico(id_empleado)
        citas_hoy = obtener_citas_hoy(id_empleado)
        horarios_medico = obtener_horarios_medico(id_empleado, offset_semana)
        citas_semana = obtener_citas_semana(id_empleado, offset_semana)
        mis_pacientes = []
        citas_pendientes = []
        
    elif subsistema == 'pacientes':
        # Solo pacientes: estadísticas + mis pacientes
        stats = obtener_estadisticas_medico(id_empleado)
        citas_hoy = []
        horarios_medico = []
        citas_semana = {}
        mis_pacientes = obtener_mis_pacientes(id_empleado)
        citas_pendientes = []
        
    elif subsistema == 'diagnosticos':
        # Solo diagnósticos: estadísticas + citas pendientes
        stats = obtener_estadisticas_medico(id_empleado)
        citas_hoy = []
        horarios_medico = []
        citas_semana = {}
        mis_pacientes = []
        citas_pendientes = obtener_citas_pendientes_diagnostico(id_empleado)
        
    elif subsistema == 'notificaciones':
        # Solo notificaciones: estadísticas básicas + notificaciones
        stats = obtener_estadisticas_medico(id_empleado)
        citas_hoy = []
        horarios_medico = []
        citas_semana = {}
        mis_pacientes = []
        citas_pendientes = []
        print(f"🔍 [DEBUG panel] Cargando notificaciones para subsistema 'notificaciones'")
        notificaciones = obtener_notificaciones_medico(id_empleado)
        print(f"🔍 [DEBUG panel] Notificaciones obtenidas: {len(notificaciones) if notificaciones else 0}")
        
    else:
        # Dashboard: estadísticas + citas hoy solamente
        stats = obtener_estadisticas_medico(id_empleado)
        citas_hoy = obtener_citas_hoy(id_empleado)
        horarios_medico = []
        citas_semana = {}
        mis_pacientes = []
        citas_pendientes = []
        notificaciones = []
    
            # Obtener contador de notificaciones no leídas para el badge
    notificaciones_no_leidas = 0
    if subsistema != 'notificaciones':
        try:
            # Obtener id_usuario del empleado
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_usuario FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
            empleado = cursor.fetchone()
            print(f"🔍 [DEBUG panel] Empleado para badge: {empleado}")
            
            if empleado and empleado.get('id_usuario'):
                id_usuario = empleado['id_usuario']
                print(f"🔍 [DEBUG panel] Contando notificaciones no leídas para id_usuario: {id_usuario}")
                
                try:
                    cursor.execute("""
                        SELECT COUNT(*) as total
                        FROM NOTIFICACION
                        WHERE id_usuario = %s AND (leida = FALSE OR leida = 0 OR leida IS NULL)
                    """, (id_usuario,))
                    result = cursor.fetchone()
                    notificaciones_no_leidas = result['total'] if result else 0
                    print(f"🔍 [DEBUG panel] Notificaciones no leídas: {notificaciones_no_leidas}")
                except Exception as e:
                    print(f"❌ [DEBUG panel] Error contando notificaciones: {e}")
                    # Si falla porque no existe el campo, intentar verificar si existe
                    error_str = str(e).lower()
                    if 'id_usuario' in error_str or 'unknown column' in error_str:
                        print(f"⚠️ Campo id_usuario no existe en NOTIFICACION")
                    else:
                        import traceback
                        traceback.print_exc()
            conexion.close()
        except Exception as e:
            print(f"❌ Error obteniendo contador de notificaciones: {e}")
            import traceback
            traceback.print_exc()
            notificaciones_no_leidas = 0

    return render_template(
        'panel_medico.html',
        subsistema=subsistema,
        usuario=usuario,
        stats=stats,
        citas_hoy=citas_hoy,
        horarios_medico=horarios_medico,
        citas_semana=citas_semana,
        mis_pacientes=mis_pacientes,
        citas_pendientes=citas_pendientes,
        notificaciones=notificaciones if subsistema == 'notificaciones' else [],
        notificaciones_no_leidas=notificaciones_no_leidas,
        offset_semana=offset_semana,
        inicio_semana=inicio_semana,
        fin_semana=fin_semana
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
        
        # Obtener autorizaciones (exámenes y operaciones) del paciente
        cursor.execute("""
            SELECT 
                ap.id_autorizacion,
                ap.id_tipo_servicio,
                CASE 
                    WHEN ap.id_tipo_servicio = 4 THEN 'EXAMEN'
                    WHEN ap.id_tipo_servicio = 2 THEN 'OPERACION'
                    ELSE 'OTRO'
                END as tipo_procedimiento,
                s.nombre as servicio_nombre,
                ap.fecha_autorizacion,
                ap.fecha_vencimiento,
                ap.fecha_uso,
                CONCAT(med.nombres, ' ', med.apellidos) as medico_autoriza,
                CONCAT(med_asig.nombres, ' ', med_asig.apellidos) as medico_asignado,
                esp.nombre as especialidad_requerida,
                c.fecha_cita,
                c.diagnostico as diagnostico_cita,
                CASE 
                    WHEN ap.fecha_uso IS NOT NULL THEN 'COMPLETADO'
                    WHEN ap.fecha_vencimiento < NOW() THEN 'VENCIDO'
                    ELSE 'PENDIENTE'
                END as estado_autorizacion
            FROM AUTORIZACION_PROCEDIMIENTO ap
            INNER JOIN SERVICIO s ON ap.id_servicio = s.id_servicio
            INNER JOIN EMPLEADO med ON ap.id_medico_autoriza = med.id_empleado
            LEFT JOIN EMPLEADO med_asig ON ap.id_medico_asignado = med_asig.id_empleado
            LEFT JOIN ESPECIALIDAD esp ON ap.id_especialidad_requerida = esp.id_especialidad
            LEFT JOIN CITA c ON ap.id_cita = c.id_cita
            WHERE ap.id_paciente = %s
            ORDER BY ap.fecha_autorizacion DESC
        """, (id_paciente,))
        
        autorizaciones = cursor.fetchall()
        
        # Separar en exámenes y operaciones
        examenes = []
        operaciones = []
        
        for aut in autorizaciones:
            fecha_aut = aut['fecha_autorizacion'].strftime('%d/%m/%Y') if aut['fecha_autorizacion'] else 'N/A'
            fecha_venc = aut['fecha_vencimiento'].strftime('%d/%m/%Y') if aut['fecha_vencimiento'] else 'N/A'
            fecha_uso = aut['fecha_uso'].strftime('%d/%m/%Y') if aut['fecha_uso'] else None
            
            item = {
                'id': aut['id_autorizacion'],
                'servicio': aut['servicio_nombre'],
                'fecha_autorizacion': fecha_aut,
                'fecha_vencimiento': fecha_venc,
                'fecha_uso': fecha_uso,
                'medico_autoriza': aut['medico_autoriza'],
                'medico_asignado': aut['medico_asignado'] if aut['medico_asignado'] else None,
                'especialidad': aut['especialidad_requerida'] if aut['especialidad_requerida'] else None,
                'estado': aut['estado_autorizacion']
            }
            
            if aut['id_tipo_servicio'] == 4:
                examenes.append(item)
            elif aut['id_tipo_servicio'] == 2:
                operaciones.append(item)
        
        return jsonify({
            'success': True,
            'paciente': {
                'nombre': nombre_completo,
                'dni': paciente['documento_identidad'],
                'edad': edad
            },
            'historial': historial_formateado,
            'examenes': examenes,
            'operaciones': operaciones
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
    Guarda un diagnóstico para una cita y la marca como completada.
    También puede autorizar exámenes u operaciones si se solicita.
    Validaciones:
    - Solo se puede registrar a partir de la hora de inicio de la cita
    - Fecha límite: hasta las 23:59:59 del mismo día de la cita
    - Se puede omitir validación temporal con parámetro 'omitir_validacion_tiempo'
    """
    conexion = None
    try:
        id_cita = request.form.get('id_cita')
        id_paciente = request.form.get('id_paciente')
        diagnostico = request.form.get('diagnostico')
        observaciones = request.form.get('observaciones', '')
        es_modificacion = request.form.get('es_modificacion') == 'true'
        omitir_validacion_tiempo = request.form.get('omitir_validacion_tiempo') == 'true'
        
        # Datos de autorización de procedimientos
        autorizar_examen = request.form.get('autorizar_examen') == 'true'
        autorizar_operacion = request.form.get('autorizar_operacion') == 'true'
        
        if not id_cita or not diagnostico or not id_paciente:
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Validación temporal: obtener fecha y hora de la cita (usar nombres correctos de columnas)
        # La tabla CITA tiene: fecha_cita, hora_inicio, hora_fin
        # Se usan alias para mantener el resto del código sin cambios
        cursor.execute("""
            SELECT fecha_cita AS fecha, hora_inicio AS hora, estado, diagnostico AS diagnostico_existente
            FROM CITA 
            WHERE id_cita = %s
        """, (id_cita,))
        
        cita = cursor.fetchone()
        if not cita:
            return jsonify({'success': False, 'message': 'Cita no encontrada'}), 404
        
        # Si la cita está cancelada, no permitir registro
        if cita['estado'] == 'Cancelada':
            return jsonify({'success': False, 'message': 'No se puede registrar diagnóstico para una cita cancelada'}), 400
        
        from datetime import datetime, time, timedelta
        
        # Combinar fecha y hora de la cita
        fecha_cita = cita['fecha']
        hora_cita = cita['hora']
        
        if isinstance(hora_cita, timedelta):
            hora_inicio = (datetime.min + hora_cita).time()
        elif isinstance(hora_cita, time):
            hora_inicio = hora_cita
        else:
            hora_inicio = datetime.strptime(str(hora_cita), '%H:%M:%S').time()
        
        fecha_hora_cita = datetime.combine(fecha_cita, hora_inicio)
        fecha_limite = datetime.combine(fecha_cita, time(23, 59, 59))
        ahora = datetime.now()
        
        # VALIDACIÓN 1: Solo si es registro nuevo (no modificación) y no se omite validación
        if not es_modificacion and not omitir_validacion_tiempo:
            # No permitir registro antes de que inicie la cita
            if ahora < fecha_hora_cita:
                hora_formatted = hora_inicio.strftime('%H:%M')
                return jsonify({
                    'success': False, 
                    'message': f'Esta cita aún no ha iniciado. Podrá registrar el diagnóstico a partir de las {hora_formatted}'
                }), 400
            
            # No permitir registro después de la fecha límite (medianoche del día de la cita)
            if ahora > fecha_limite:
                return jsonify({
                    'success': False, 
                    'message': 'El plazo para registrar el diagnóstico ha expirado. Solo se permite el mismo día de la cita.'
                }), 400
        
        # VALIDACIÓN 2: Si es modificación, verificar que sea el mismo médico
        if es_modificacion:
            cursor.execute("""
                SELECT id_empleado FROM CITA WHERE id_cita = %s
            """, (id_cita,))
            cita_medico = cursor.fetchone()
            id_empleado_actual = session.get('id_empleado')
            
            if cita_medico and cita_medico['id_empleado'] != id_empleado_actual:
                return jsonify({
                    'success': False,
                    'message': 'Solo el médico que registró el diagnóstico puede modificarlo'
                }), 403
        
        # Si es modificación, guardar historial del diagnóstico anterior
        if es_modificacion and cita['diagnostico_existente']:
            try:
                cursor.execute("""
                    INSERT INTO historial_diagnosticos 
                    (id_cita, diagnostico_anterior, observaciones_anterior, fecha_modificacion, id_medico_modifica)
                    VALUES (%s, %s, %s, NOW(), %s)
                """, (id_cita, cita['diagnostico_existente'], cita.get('observaciones'), session.get('id_empleado')))
            except Exception as e:
                # Si la tabla no existe, continuar sin guardar historial
                print(f"Advertencia: No se pudo guardar en historial_diagnosticos: {e}")
        
        # Actualizar la cita con el diagnóstico y cambiar estado a Completada
        cursor.execute("""
            UPDATE CITA 
            SET diagnostico = %s, 
                observaciones = %s, 
                estado = 'Completada'
            WHERE id_cita = %s
        """, (diagnostico, observaciones, id_cita))
        
        id_empleado = session.get('id_empleado')
        
        # Procesar autorizaciones si se solicitaron
        autorizaciones_creadas = []
        
        if autorizar_examen:
            # Soportar múltiples exámenes (hasta 3)
            cantidad_examenes = request.form.get('cantidad_examenes', '0')
            examenes_ids = []
            
            # Obtener exámenes del nuevo formato (múltiples)
            for i in range(int(cantidad_examenes) if cantidad_examenes else 0):
                examen_id = request.form.get(f'examenes[{i}]')
                if examen_id:
                    examenes_ids.append(examen_id)
            
            # Fallback al formato antiguo (un solo examen)
            if not examenes_ids:
                id_servicio_examen = request.form.get('id_servicio_examen')
                if id_servicio_examen:
                    examenes_ids.append(id_servicio_examen)
            
            print(f"🔍 [DEBUG] Autorizar exámenes: {len(examenes_ids)} examen(es)")
            
            examenes_creados = 0
            for id_servicio_examen in examenes_ids:
                if id_servicio_examen:
                    # Para exámenes, el médico que autoriza es el mismo que lo realiza
                    datos_examen = {
                        'id_cita': int(id_cita),
                        'id_paciente': int(id_paciente),
                        'id_medico_autoriza': int(id_empleado),
                        'tipo_procedimiento': 'EXAMEN',
                        'id_servicio': int(id_servicio_examen),
                        'id_especialidad_requerida': None,
                        'id_medico_asignado': int(id_empleado)  # El mismo médico realiza el examen
                    }
                    print(f"🔍 [DEBUG] Datos para crear autorización de examen: {datos_examen}")
                    
                    resultado = AutorizacionProcedimiento.crear(datos_examen, cursor_externo=cursor)
                    print(f"🔍 [DEBUG] Resultado crear examen: {resultado}")
                    
                    if resultado.get('success'):
                        examenes_creados += 1
                        print(f"✅ [DEBUG] Autorización de examen creada con ID: {resultado.get('id_autorizacion')}")
                    else:
                        print(f"❌ Error al crear autorización de examen: {resultado.get('error')}")
            
            if examenes_creados > 0:
                autorizaciones_creadas.append(f'{examenes_creados} examen(es)')
        
        if autorizar_operacion:
            id_servicio_operacion = request.form.get('id_servicio_operacion')
            id_medico_derivar = request.form.get('id_medico_derivar_operacion')
            
            # Convertir valores vacíos a None
            id_medico_derivar = int(id_medico_derivar) if id_medico_derivar and id_medico_derivar != '' else None
            
            if id_servicio_operacion:
                # Validación: Si NO se deriva, el médico logueado DEBE poder operar
                if not id_medico_derivar:
                    # Verificar que el médico tenga la especialidad requerida para el servicio
                    cursor.execute("""
                        SELECT s.id_especialidad as especialidad_servicio,
                               e.id_especialidad as especialidad_medico
                        FROM SERVICIO s
                        INNER JOIN EMPLEADO e ON e.id_empleado = %s
                        WHERE s.id_servicio = %s 
                        AND s.id_tipo_servicio = 2
                    """, (id_empleado, id_servicio_operacion))
                    
                    resultado_validacion = cursor.fetchone()
                    
                    if not resultado_validacion:
                        # Hacer commit antes de cerrar para guardar el diagnóstico
                        conexion.commit()
                        conexion.close()
                        return jsonify({
                            'success': False, 
                            'message': 'Servicio de operación no encontrado.'
                        }), 404
                    
                    # Verificar que las especialidades coincidan
                    puede_operar = (resultado_validacion['especialidad_servicio'] == 
                                   resultado_validacion['especialidad_medico'])
                    
                    if not puede_operar:
                        # Hacer commit antes de cerrar para guardar el diagnóstico
                        conexion.commit()
                        conexion.close()
                        return jsonify({
                            'success': False, 
                            'message': 'Usted no está autorizado para realizar esta operación. Debe derivar a otro médico de la especialidad requerida.'
                        }), 403
                    
                    # Si puede operar, asignarla a sí mismo
                    id_medico_asignado = id_empleado
                else:
                    # Si se deriva, asignarla al médico seleccionado
                    id_medico_asignado = id_medico_derivar
                
                # Obtener la especialidad requerida del servicio de operación
                cursor.execute("""
                    SELECT id_especialidad FROM SERVICIO WHERE id_servicio = %s
                """, (id_servicio_operacion,))
                
                servicio_result = cursor.fetchone()
                id_especialidad_req = servicio_result['id_especialidad'] if servicio_result else None
                
                datos_operacion = {
                    'id_cita': int(id_cita),
                    'id_paciente': int(id_paciente),
                    'id_medico_autoriza': int(id_empleado),
                    'tipo_procedimiento': 'OPERACION',
                    'id_servicio': int(id_servicio_operacion),
                    'id_especialidad_requerida': int(id_especialidad_req) if id_especialidad_req else None,
                    'id_medico_asignado': int(id_medico_asignado) if id_medico_asignado else None
                }
                print(f"🔍 [DEBUG] Datos para crear autorización de operación: {datos_operacion}")
                
                resultado = AutorizacionProcedimiento.crear(datos_operacion, cursor_externo=cursor)
                print(f"🔍 [DEBUG] Resultado crear operación: {resultado}")
                
                if resultado.get('success'):
                    autorizaciones_creadas.append('operación')
                    print(f"✅ [DEBUG] Autorización de operación creada con ID: {resultado.get('id_autorizacion')}")
                    
                    # NOTIFICACIÓN: Enviar notificación al médico derivado (si aplica)
                    if id_medico_derivar and id_medico_derivar != id_empleado:
                        try:
                            # Obtener información del médico que autoriza y del servicio
                            cursor.execute("""
                                SELECT 
                                    CONCAT(e.nombres, ' ', e.apellidos) as nombre_medico_autoriza,
                                    CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                                    s.nombre as nombre_servicio,
                                    u.id_usuario as id_usuario_derivado
                                FROM EMPLEADO e
                                CROSS JOIN PACIENTE p
                                CROSS JOIN SERVICIO s
                                INNER JOIN EMPLEADO e2 ON e2.id_empleado = %s
                                INNER JOIN USUARIO u ON e2.id_usuario = u.id_usuario
                                WHERE e.id_empleado = %s
                                AND p.id_paciente = %s
                                AND s.id_servicio = %s
                            """, (id_medico_derivar, id_empleado, id_paciente, id_servicio_operacion))
                            
                            info_notif = cursor.fetchone()
                            
                            if info_notif and info_notif['id_usuario_derivado']:
                                titulo_notif = "Nueva Operación Derivada"
                                mensaje_notif = f"""
                                <div style="margin: 15px 0;">
                                    <p style="margin: 10px 0; font-size: 15px; color: #374151;">
                                        El Dr./Dra. <strong>{info_notif['nombre_medico_autoriza']}</strong> le ha derivado una operación.
                                    </p>
                                    <div style="background-color: #f9fafb; border-left: 4px solid #ef4444; padding: 15px; margin: 15px 0; border-radius: 4px;">
                                        <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>🏥 Operación:</strong> {info_notif['nombre_servicio']}</p>
                                        <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>👤 Paciente:</strong> {info_notif['nombre_paciente']}</p>
                                        <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>📋 ID Autorización:</strong> {resultado.get('id_autorizacion')}</p>
                                    </div>
                                    <p style="margin: 10px 0; font-size: 14px; color: #6b7280;">
                                        Por favor, revise su agenda para programar la operación correspondiente.
                                    </p>
                                </div>
                                """
                                
                                result_notif = Notificacion.crear_para_medico(
                                    titulo=titulo_notif,
                                    mensaje=mensaje_notif,
                                    tipo='derivacion_operacion',
                                    id_usuario=info_notif['id_usuario_derivado']
                                )
                                
                                if result_notif.get('success'):
                                    print(f"✅ [DEBUG] Notificación enviada al médico derivado (ID usuario: {info_notif['id_usuario_derivado']})")
                                else:
                                    print(f"⚠️ [DEBUG] Error al enviar notificación: {result_notif.get('error')}")
                            else:
                                print(f"⚠️ [DEBUG] No se pudo obtener id_usuario del médico derivado")
                                
                        except Exception as notif_error:
                            # No hacer fallar todo si la notificación falla
                            print(f"⚠️ [DEBUG] Error al enviar notificación de derivación: {notif_error}")
                else:
                    print(f"❌ Error al crear autorización de operación: {resultado.get('error')}")
        
        conexion.commit()
        
        if es_modificacion:
            mensaje = 'Diagnóstico modificado exitosamente. Los cambios han sido registrados.'
        else:
            mensaje = 'Diagnóstico guardado exitosamente. La cita ha sido marcada como completada.'
        
        if autorizaciones_creadas:
            mensaje += f' Se autorizaron: {", ".join(autorizaciones_creadas)}.'
        
        return jsonify({'success': True, 'message': mensaje})

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
@medico_bp.route('/api/obtener_diagnostico/<int:id_cita>')
@medico_required
def api_obtener_diagnostico(id_cita):
    """
    Retorna el diagnóstico de una cita específica para permitir su modificación
    """
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        cursor.execute("""
            SELECT diagnostico, observaciones, estado, id_empleado
            FROM CITA 
            WHERE id_cita = %s
        """, (id_cita,))
        
        cita = cursor.fetchone()
        conexion.close()
        
        if not cita:
            return jsonify({'success': False, 'message': 'Cita no encontrada'}), 404
        
        # Verificar que el médico que intenta modificar sea el mismo que registró
        if cita['id_empleado'] != session.get('id_empleado'):
            return jsonify({
                'success': False, 
                'message': 'Solo el médico que registró el diagnóstico puede modificarlo'
            }), 403
        
        return jsonify({
            'success': True,
            'diagnostico': cita['diagnostico'],
            'observaciones': cita['observaciones'],
            'estado': cita['estado']
        })
        
    except Exception as e:
        print(f"Error al obtener diagnóstico: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

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


@medico_bp.route('/api/obtener_especialidades', methods=['GET'])
@medico_required
def obtener_especialidades():
    """
    Obtiene todas las especialidades médicas disponibles
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        cursor.execute("""
            SELECT id_especialidad, nombre, descripcion
            FROM ESPECIALIDAD
            WHERE estado = 'activo'
            ORDER BY nombre
        """)
        
        especialidades = cursor.fetchall()
        
        return jsonify({'success': True, 'especialidades': especialidades})
        
    except Exception as e:
        print(f"Error al obtener especialidades: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conexion:
            conexion.close()


@medico_bp.route('/api/obtener_medicos_por_especialidad/<int:id_especialidad>', methods=['GET'])
@medico_required
def obtener_medicos_por_especialidad(id_especialidad):
    """
    Obtiene médicos que pueden realizar procedimientos de una especialidad específica
    """
    try:
        medicos = AutorizacionProcedimiento.obtener_medicos_por_especialidad(id_especialidad)
        return jsonify({'success': True, 'medicos': medicos})
        
    except Exception as e:
        print(f"Error al obtener médicos: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@medico_bp.route('/api/obtener_servicios_por_especialidad/<int:id_especialidad>', methods=['GET'])
@medico_required
def obtener_servicios_por_especialidad(id_especialidad):
    """
    Obtiene servicios (operaciones) disponibles para una especialidad
    """
    try:
        servicios = Servicio.obtener_por_especialidad(id_especialidad)
        return jsonify({'success': True, 'servicios': servicios})
        
    except Exception as e:
        print(f"Error al obtener servicios: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@medico_bp.route('/api/obtener_servicios_examen', methods=['GET'])
@medico_required
def obtener_servicios_examen():
    """
    Obtiene servicios de tipo EXAMEN de la especialidad del médico logueado
    El médico solo puede autorizar exámenes de su especialidad
    """
    try:
        id_empleado = session.get('id_empleado')
        
        # Obtener especialidad del médico logueado
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_especialidad FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
        result = cursor.fetchone()
        conexion.close()
        
        id_especialidad_medico = result['id_especialidad'] if result else None
        
        # Obtener solo exámenes de la especialidad del médico
        servicios = AutorizacionProcedimiento.obtener_servicios_examen(id_especialidad_medico)
        return jsonify({'success': True, 'servicios': servicios})
        
    except Exception as e:
        print(f"Error al obtener servicios de examen: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@medico_bp.route('/api/obtener_servicios_operacion', methods=['GET'])
@medico_required
def obtener_servicios_operacion():
    """
    Obtiene servicios de tipo OPERACION que el médico actual puede realizar o derivar
    """
    try:
        id_empleado = session.get('id_empleado')
        
        # Obtener especialidad del médico
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_especialidad FROM EMPLEADO WHERE id_empleado = %s", (id_empleado,))
        result = cursor.fetchone()
        conexion.close()
        
        id_especialidad_medico = result['id_especialidad'] if result else None
        
        servicios = AutorizacionProcedimiento.obtener_servicios_operacion(id_especialidad_medico)
        return jsonify({'success': True, 'servicios': servicios})
        
    except Exception as e:
        print(f"Error al obtener servicios de operación: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@medico_bp.route('/api/obtener_medicos_mi_especialidad', methods=['GET'])
@medico_required
def obtener_medicos_mi_especialidad():
    """
    Obtiene médicos de la misma especialidad del médico logueado
    Se usa para derivar operaciones sin mostrar selector de especialidad
    """
    try:
        id_empleado = session.get('id_empleado')
        
        # Obtener especialidad del médico logueado
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id_especialidad, nombres, apellidos 
            FROM EMPLEADO 
            WHERE id_empleado = %s
        """, (id_empleado,))
        result = cursor.fetchone()
        
        if not result:
            conexion.close()
            return jsonify({'success': False, 'message': 'Médico no encontrado'}), 404
        
        id_especialidad_medico = result['id_especialidad']
        medico_actual_nombre = f"{result['nombres']} {result['apellidos']}"
        
        # Obtener otros médicos de la misma especialidad
        medicos = AutorizacionProcedimiento.obtener_medicos_por_especialidad(id_especialidad_medico)
        
        # Filtrar para excluir el médico actual
        medicos_filtrados = [m for m in medicos if m['id_empleado'] != id_empleado]
        
        conexion.close()
        return jsonify({
            'success': True, 
            'medicos': medicos_filtrados,
            'especialidad_nombre': medicos[0]['especialidad'] if medicos else 'N/A'
        })
        
    except Exception as e:
        print(f"Error al obtener médicos de mi especialidad: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@medico_bp.route('/api/verificar_autorizaciones/<int:id_paciente>', methods=['GET'])
def verificar_autorizaciones(id_paciente):
    """
    Verifica si un paciente tiene autorizaciones pendientes (para habilitar botones)
    Ruta pública para que el paciente pueda verificar sus autorizaciones
    """
    try:
        permisos = AutorizacionProcedimiento.obtener_pendientes_por_paciente(id_paciente)
        return jsonify({'success': True, 'permisos': permisos})
        
    except Exception as e:
        print(f"Error al verificar autorizaciones: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@medico_bp.route('/api/obtener_autorizaciones_cita/<int:id_cita>', methods=['GET'])
@medico_required
def obtener_autorizaciones_cita(id_cita):
    """
    Obtiene las autorizaciones asociadas a una cita específica
    """
    try:
        autorizaciones = AutorizacionProcedimiento.obtener_por_cita(id_cita)
        return jsonify({'success': True, 'autorizaciones': autorizaciones})
        
    except Exception as e:
        print(f"Error al obtener autorizaciones: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@medico_bp.route('/api/notificaciones-recientes', methods=['GET'])
@medico_required
def api_notificaciones_recientes():
    """
    Obtiene las notificaciones más recientes del médico para mostrar en el header
    """
    try:
        id_empleado = session.get('id_empleado')
        notificaciones = obtener_notificaciones_medico(id_empleado)
        
        # Solo las 5 más recientes
        notificaciones_recientes = notificaciones[:5] if notificaciones else []
        
        return jsonify({
            'success': True,
            'notificaciones': notificaciones_recientes
        })
        
    except Exception as e:
        print(f"Error al obtener notificaciones recientes: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


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


@medico_bp.route('/api/auto_completar_citas_sin_diagnostico', methods=['POST'])
@medico_required
def auto_completar_citas_sin_diagnostico():
    """
    Auto-completa citas que no recibieron diagnóstico en su día correspondiente.
    Marca las citas como 'Completada' con observación indicando que no se registró diagnóstico.
    IMPORTANTE: No crea autorizaciones ni procedimientos.
    
    Puede ser llamado:
    - Manualmente por el médico
    - Por un scheduler/cron job al final del día
    """
    conexion = None
    try:
        id_empleado = session.get('id_empleado')
        fecha_objetivo = request.json.get('fecha') if request.json else None
        
        # Si no se especifica fecha, usar ayer (para citas del día anterior)
        if fecha_objetivo:
            fecha_citas = datetime.strptime(fecha_objetivo, '%Y-%m-%d').date()
        else:
            fecha_citas = (datetime.now() - timedelta(days=1)).date()
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Obtener citas del médico sin diagnóstico de la fecha especificada
        # Estados que indican que la cita debió haberse atendido: Pendiente, Confirmada
        # NOTA: id_paciente está en RESERVA, no en CITA
        cursor.execute("""
            SELECT 
                c.id_cita, 
                r.id_paciente,
                c.fecha_cita,
                c.hora_inicio,
                CONCAT(p.nombres, ' ', p.apellidos) as paciente
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION pr ON r.id_programacion = pr.id_programacion
            INNER JOIN HORARIO h ON pr.id_horario = h.id_horario
            LEFT JOIN PACIENTE p ON r.id_paciente = p.id_paciente
            WHERE h.id_empleado = %s 
            AND c.fecha_cita = %s
            AND c.estado IN ('Pendiente', 'Confirmada')
            AND (c.diagnostico IS NULL OR c.diagnostico = '')
        """, (id_empleado, fecha_citas))
        
        citas_sin_diagnostico = cursor.fetchall()
        
        if not citas_sin_diagnostico:
            return jsonify({
                'success': True, 
                'message': f'No hay citas sin diagnóstico para el {fecha_citas.strftime("%d/%m/%Y")}',
                'citas_actualizadas': 0
            })
        
        # Marcar cada cita como completada con observación de no registro
        citas_actualizadas = []
        for cita in citas_sin_diagnostico:
            cursor.execute("""
                UPDATE CITA 
                SET estado = 'Completada',
                    diagnostico = '[No registrado]',
                    observaciones = 'Diagnóstico no registrado por el médico durante la cita. Auto-completado por el sistema.'
                WHERE id_cita = %s
            """, (cita['id_cita'],))
            
            citas_actualizadas.append({
                'id_cita': cita['id_cita'],
                'paciente': cita['paciente'],
                'fecha': cita['fecha_cita'].strftime('%d/%m/%Y') if cita['fecha_cita'] else 'N/A'
            })
        
        conexion.commit()
        
        return jsonify({
            'success': True,
            'message': f'Se auto-completaron {len(citas_actualizadas)} cita(s) sin diagnóstico del {fecha_citas.strftime("%d/%m/%Y")}',
            'citas_actualizadas': len(citas_actualizadas),
            'detalle': citas_actualizadas
        })
        
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al auto-completar citas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conexion:
            conexion.close()


@medico_bp.route('/api/citas_sin_diagnostico_pendientes', methods=['GET'])
@medico_required
def obtener_citas_sin_diagnostico_pendientes():
    """
    Obtiene el conteo de citas pasadas sin diagnóstico para mostrar alerta al médico.
    """
    conexion = None
    try:
        id_empleado = session.get('id_empleado')
        hoy = datetime.now().date()
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Contar citas de días anteriores sin diagnóstico
        # NOTA: id_paciente está en RESERVA, no en CITA
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM CITA c
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            INNER JOIN PROGRAMACION pr ON r.id_programacion = pr.id_programacion
            INNER JOIN HORARIO h ON pr.id_horario = h.id_horario
            WHERE h.id_empleado = %s 
            AND c.fecha_cita < %s
            AND c.estado IN ('Pendiente', 'Confirmada')
            AND (c.diagnostico IS NULL OR c.diagnostico = '')
        """, (id_empleado, hoy))
        
        resultado = cursor.fetchone()
        total = resultado['total'] if resultado else 0
        
        return jsonify({
            'success': True,
            'citas_pendientes': total
        })
        
    except Exception as e:
        print(f"Error al obtener citas sin diagnóstico: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conexion:
            conexion.close()
