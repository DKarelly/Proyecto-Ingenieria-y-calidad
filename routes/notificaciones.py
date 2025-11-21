from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
import datetime
from models.notificacion import Notificacion
from bd import obtener_conexion

notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/')
def panel():
    """Panel de Notificaciones"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    # Redirigir al dashboard principal unificado
    return redirect(url_for('admin_panel', subsistema='notificaciones'))

@notificaciones_bp.route('/gestionar-confirmacion-reserva')
def gestionar_confirmacion_reserva():
    """Gestionar Confirmación de Reserva"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('GestionarConfirmacióndeCitas.html')

@notificaciones_bp.route('/gestionar-recordatorio-reserva')
def gestionar_recordatorio_reserva():
    """Gestionar Recordatorio Reserva"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('GestionarRecordatorios.html')

@notificaciones_bp.route('/gestionar-recordatorio-cambios')
def gestionar_recordatorio_cambios():
    """Gestionar Recordatorio de Cambios"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('gestionarRecordatoriosDeCambios.html')


# ========== APIs PARA PACIENTES ==========

@notificaciones_bp.route('/api/no-leidas-count')
def api_no_leidas_count():
    """Retorna el número de notificaciones no leídas del usuario"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado', 'count': 0}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'count': 0})

    try:
        # Obtener id_paciente desde la sesión o desde la BD
        id_paciente = session.get('id_paciente')
        
        if not id_paciente:
            # Si no está en sesión, buscar en la BD usando id_usuario
            conexion = obtener_conexion()
            if not conexion:
                return jsonify({'error': 'Error de conexión', 'count': 0}), 500
            
            with conexion.cursor() as cursor:
                cursor.execute("SELECT id_paciente FROM PACIENTE WHERE id_usuario = %s", (session['usuario_id'],))
                resultado = cursor.fetchone()
                if resultado:
                    id_paciente = resultado['id_paciente']
                else:
                    return jsonify({'count': 0})
            conexion.close()
        
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({'error': 'Error de conexión', 'count': 0}), 500
            
        with conexion.cursor() as cursor:
            # La tabla NOTIFICACION tiene id_paciente, fecha_envio, hora_envio
            sql = """
                SELECT COUNT(*) as count
                FROM NOTIFICACION
                WHERE id_paciente = %s 
                AND fecha_envio <= CURDATE()
            """
            cursor.execute(sql, (id_paciente,))
            resultado = cursor.fetchone()

            count = resultado['count'] if resultado else 0
            return jsonify({'count': count})

    except Exception as e:
        print(f"Error en api_no_leidas_count: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'count': 0}), 500
    finally:
        try:
            if conexion:
                conexion.close()
        except:
            pass


@notificaciones_bp.route('/api/recientes')
def api_recientes():
    """Retorna las notificaciones más recientes del usuario (últimas 10)"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'notificaciones': []})

    try:
        # Obtener id_paciente
        id_paciente = session.get('id_paciente')
        
        if not id_paciente:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT id_paciente FROM PACIENTE WHERE id_usuario = %s", (session['usuario_id'],))
                resultado = cursor.fetchone()
                if resultado:
                    id_paciente = resultado['id_paciente']
                else:
                    return jsonify({'notificaciones': []})
            conexion.close()
        
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({'error': 'Error al obtener conexión', 'notificaciones': []}), 500
        with conexion.cursor() as cursor:
            # Selección unificada:
            # - Mostrar siempre notificaciones inmediatas (tipo != 'recordatorio')
            # - Mostrar recordatorios sólo si fecha_envio <= CURDATE()
            # - Incluir estado de reserva para colorear según estado
            sql = """
                SELECT n.id_notificacion, n.titulo, n.mensaje, n.fecha_envio, n.hora_envio, n.tipo, 
                       COALESCE(n.leida, FALSE) as leida, n.fecha_leida, n.id_reserva,
                       r.estado as estado_reserva
                FROM NOTIFICACION n
                LEFT JOIN RESERVA r ON n.id_reserva = r.id_reserva
                WHERE n.id_paciente = %s
                AND (n.tipo != 'recordatorio' OR n.fecha_envio <= CURDATE())
                ORDER BY 
                    CASE WHEN n.leida = FALSE THEN 0 ELSE 1 END,
                    n.fecha_envio DESC, 
                    n.hora_envio DESC
                LIMIT 50
            """
            cursor.execute(sql, (id_paciente,))
            rows = cursor.fetchall()

            # Normalize fields for the frontend (fecha_creacion ISO and leida flag default false)
            notificaciones = []
            for r in rows:
                fecha = r.get('fecha_envio')
                hora = r.get('hora_envio')

                # Normalizar fecha y hora a strings JSON-serializables
                fecha_str = None
                hora_str = None

                try:
                    if isinstance(fecha, datetime.date):
                        fecha_str = fecha.isoformat()
                    elif fecha is not None:
                        fecha_str = str(fecha)
                except Exception:
                    fecha_str = str(fecha)

                try:
                    # PyMySQL returns TIME as datetime.timedelta in some configs
                    if isinstance(hora, datetime.timedelta):
                        total_seconds = int(hora.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        hora_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                    elif isinstance(hora, datetime.time):
                        hora_str = hora.isoformat()
                    elif hora is not None:
                        hora_str = str(hora)
                except Exception:
                    hora_str = str(hora)

                fecha_creacion = None
                if fecha_str and hora_str:
                    fecha_creacion = f"{fecha_str} {hora_str}"
                elif fecha_str:
                    fecha_creacion = fecha_str

                notificaciones.append({
                    'id_notificacion': r.get('id_notificacion'),
                    'titulo': r.get('titulo'),
                    'mensaje': r.get('mensaje'),
                    'tipo': r.get('tipo'),
                    'fecha_envio': fecha_str,
                    'hora_envio': hora_str,
                    'fecha_creacion': fecha_creacion,
                    'leida': bool(r.get('leida', False)),
                    'estado_reserva': r.get('estado_reserva'),  # Incluir estado para colorear
                    'id_reserva': r.get('id_reserva')  # Incluir id_reserva para redirección
                })

            # Additionally return a total count (total available notifications up to today)
            try:
                count_sql = """
                    SELECT COUNT(*) as total
                    FROM NOTIFICACION
                    WHERE id_paciente = %s
                    AND (tipo != 'recordatorio' OR fecha_envio <= CURDATE())
                """
                cursor.execute(count_sql, (id_paciente,))
                total_row = cursor.fetchone()
                total = total_row.get('total') if total_row else len(notificaciones)
            except Exception:
                total = len(notificaciones)

            return jsonify({'notificaciones': notificaciones, 'total': total})

    except Exception as e:
        # Log full traceback to help debugging in development
        print(f"Error en api_recientes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'notificaciones': []}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@notificaciones_bp.route('/api/marcar-leida/<int:id_notificacion>', methods=['POST'])
def api_marcar_leida(id_notificacion):
    """Marca una notificación como leída"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        # Verificar que la notificación pertenece al paciente actual
        id_paciente = session.get('id_paciente')
        if not id_paciente:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT id_paciente FROM PACIENTE WHERE id_usuario = %s", (session['usuario_id'],))
                resultado = cursor.fetchone()
                if resultado:
                    id_paciente = resultado['id_paciente']
                else:
                    return jsonify({'error': 'Paciente no encontrado'}), 404
            conexion.close()

        # Verificar propiedad de la notificación
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_paciente FROM NOTIFICACION WHERE id_notificacion = %s", (id_notificacion,))
            notif = cursor.fetchone()
            if not notif:
                return jsonify({'error': 'Notificación no encontrada'}), 404
            if notif['id_paciente'] != id_paciente:
                return jsonify({'error': 'No autorizado'}), 403
        conexion.close()

        # Marcar como leída
        resultado = Notificacion.marcar_como_leida(id_notificacion)
        if 'error' in resultado:
            return jsonify({'error': resultado['error']}), 500
        
        return jsonify({'success': True, 'message': 'Notificación marcada como leída'})

    except Exception as e:
        print(f"Error en api_marcar_leida: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@notificaciones_bp.route('/api/marcar-todas-leidas', methods=['POST'])
def api_marcar_todas_leidas():
    """Marca todas las notificaciones del paciente como leídas"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    if session.get('tipo_usuario') != 'paciente':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        # Obtener id_paciente
        id_paciente = session.get('id_paciente')
        if not id_paciente:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT id_paciente FROM PACIENTE WHERE id_usuario = %s", (session['usuario_id'],))
                resultado = cursor.fetchone()
                if resultado:
                    id_paciente = resultado['id_paciente']
                else:
                    return jsonify({'error': 'Paciente no encontrado'}), 404
            conexion.close()

        # Marcar todas como leídas
        resultado = Notificacion.marcar_todas_como_leidas(id_paciente)
        if 'error' in resultado:
            return jsonify({'error': resultado['error']}), 500
        
        return jsonify({
            'success': True, 
            'message': f"{resultado.get('count', 0)} notificaciones marcadas como leídas"
        })

    except Exception as e:
        print(f"Error en api_marcar_todas_leidas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@notificaciones_bp.route('/historial')
def historial():
    """Vista del historial completo de notificaciones para pacientes con paginación"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    # Obtener id_paciente desde la sesión o consultando la BD
    id_paciente = session.get('id_paciente')
    try:
        if not id_paciente:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT id_paciente FROM PACIENTE WHERE id_usuario = %s", (session['usuario_id'],))
                resultado = cursor.fetchone()
                if resultado:
                    id_paciente = resultado['id_paciente']
            try:
                conexion.close()
            except:
                pass

        # Paginación
        pagina = int(request.args.get('pagina', 1))
        por_pagina = 10
        
        # Si aún no hay id_paciente, mostrar vacío
        if not id_paciente:
            notificaciones = []
            total = 0
        else:
            # Obtener todas las notificaciones para contar
            todas_notificaciones = Notificacion.obtener_por_paciente(id_paciente)
            total = len(todas_notificaciones)
            
            # Aplicar paginación
            inicio = (pagina - 1) * por_pagina
            fin = inicio + por_pagina
            notificaciones = todas_notificaciones[inicio:fin]
            
            # Calcular total de páginas
            total_paginas = (total + por_pagina - 1) // por_pagina

    except Exception as e:
        print(f"Error cargando historial de notificaciones: {e}")
        notificaciones = []
        total = 0
        total_paginas = 0
        pagina = 1

    return render_template('HistorialNotificaciones.html', 
                         notificaciones=notificaciones,
                         pagina_actual=pagina,
                         total_paginas=total_paginas,
                         total_notificaciones=total)
