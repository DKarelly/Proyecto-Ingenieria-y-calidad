from flask import Blueprint, render_template, session, redirect, url_for, jsonify
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
    
    return render_template('panel.html', subsistema='notificaciones')

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
                AND fecha_envio >= CURDATE()
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
        with conexion.cursor() as cursor:
            sql = """
                SELECT id_notificacion, titulo, mensaje, fecha_envio, hora_envio, tipo
                FROM NOTIFICACION
                WHERE id_paciente = %s
                ORDER BY fecha_envio DESC, hora_envio DESC
                LIMIT 10
            """
            cursor.execute(sql, (id_paciente,))
            notificaciones = cursor.fetchall()

            return jsonify({'notificaciones': notificaciones})

    except Exception as e:
        return jsonify({'error': str(e), 'notificaciones': []}), 500
    finally:
        try:
            conexion.close()
        except:
            pass


@notificaciones_bp.route('/historial')
def historial():
    """Vista del historial completo de notificaciones para pacientes"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'paciente':
        return redirect(url_for('home'))

    return render_template('HistorialNotificaciones.html')
