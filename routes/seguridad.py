from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.incidencia import Incidencia
import time

seguridad_bp = Blueprint('seguridad', __name__)

@seguridad_bp.route('/')
def panel():
    """Panel de Seguridad"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    # Verificar que el rol esté entre 1 y 5
    id_rol = session.get('id_rol')
    if id_rol is None or id_rol not in [1, 2, 3, 4, 5]:
        return redirect(url_for('home'))

    # Redirigir al dashboard principal unificado
    return redirect(url_for('admin_panel', subsistema='seguridad'))

# =======================================
# MÓDULO SEGURIDAD
# =======================================

@seguridad_bp.route('/consultar-actividad')
def consultar_actividad():
    """Consultar Actividad del Sistema"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('consultar_actividad.html')

# =======================================
# MÓDULO INCIDENCIAS
# =======================================

@seguridad_bp.route('/incidencias')
def incidencias():
    """Panel de Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    # Redirigir al dashboard principal unificado
    return redirect(url_for('admin_panel', subsistema='incidencias'))

@seguridad_bp.route('/incidencias/generar-incidencia')
def generar_incidencia():
    """Generar Nueva Incidencia"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('generarIncidencia.html')

@seguridad_bp.route('/incidencias/asignar-responsable')
def asignar_responsable():
    """Asignar Responsable a Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('asignarResponsable.html')

@seguridad_bp.route('/incidencias/consultar-incidencia')
def consultar_incidencia():
    """Consultar Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('consultarIncidencia.html')

@seguridad_bp.route('/incidencias/generar-informe')
def generar_informe():
    """Generar Informe de Incidencias"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))
    
    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))
    
    return render_template('generar_informe.html')

# =======================================
# API Routes for Incidencias
# =======================================

@seguridad_bp.route('/api/incidencias', methods=['GET'])
def api_obtener_incidencias():
    """API para obtener todas las incidencias"""
    # if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
    #     return jsonify({'error': 'No autorizado'}), 401

    incidencias = Incidencia.obtener_todas()
    return jsonify(incidencias)

@seguridad_bp.route('/api/incidencias/buscar', methods=['POST'])
def api_buscar_incidencias():
    """API para buscar incidencias con filtros"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    filtros = {
        'paciente': data.get('paciente', ''),
        'empleado': data.get('empleado', ''),
        'fecha_registro': data.get('fecha_registro', ''),
        'fecha_resolucion': data.get('fecha_resolucion', ''),
        'estado': data.get('estado', ''),
        'categoria': data.get('categoria', ''),
        'prioridad': data.get('prioridad', '')
    }

    incidencias = Incidencia.buscar(filtros)
    return jsonify(incidencias)

@seguridad_bp.route('/api/incidencias/asignar', methods=['POST'])
def api_asignar_empleado():
    """API para asignar un empleado a una incidencia"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    
    try:
        resultado = Incidencia.asignar_empleado(
            id_incidencia=data.get('id_incidencia'),
            id_empleado=data.get('id_empleado'),
            observaciones=data.get('observaciones', '')
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seguridad_bp.route('/api/incidencias/actualizar-estado', methods=['POST'])
def api_actualizar_estado():
    """API para actualizar el estado de una incidencia"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    
    try:
        resultado = Incidencia.actualizar_estado(
            id_historial=data.get('id_historial'),
            estado=data.get('estado'),
            observaciones=data.get('observaciones')
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seguridad_bp.route('/api/incidencias/buscar-pacientes', methods=['GET'])
def api_buscar_pacientes():
    """API para buscar pacientes (autocompletado)"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    termino = request.args.get('termino', '')
    pacientes = Incidencia.buscar_pacientes(termino)
    return jsonify(pacientes)

@seguridad_bp.route('/api/incidencias/buscar-empleados', methods=['GET'])
def api_buscar_empleados():
    """API para buscar empleados (autocompletado)"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    termino = request.args.get('termino', '')
    empleados = Incidencia.buscar_empleados(termino)
    return jsonify(empleados)

@seguridad_bp.route('/api/incidencias/sin-asignar', methods=['GET'])
def api_incidencias_sin_asignar():
    """API para obtener incidencias sin asignar empleado responsable"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        incidencias = Incidencia.obtener_sin_asignar()
        return jsonify(incidencias if incidencias else [])
    except Exception as e:
        print(f"Error al obtener incidencias sin asignar: {str(e)}")
        return jsonify({'error': str(e)}), 500

@seguridad_bp.route('/api/empleados', methods=['GET'])
def api_obtener_empleados():
    """API para obtener todos los empleados disponibles"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        from models.empleado import Empleado
        empleados = Empleado.obtener_todos()
        
        # Validar que empleados sea una lista
        if not isinstance(empleados, list):
            print(f"Advertencia: obtener_todos() retornó {type(empleados)} en lugar de lista")
            return jsonify([])
        
        # Agregar nombre_completo a cada empleado
        for empleado in empleados:
            if isinstance(empleado, dict):
                nombres = empleado.get('nombres', '')
                apellidos = empleado.get('apellidos', '')
                empleado['nombre_completo'] = f"{nombres} {apellidos}".strip()
        
        return jsonify(empleados)
    except Exception as e:
        print(f"Error al obtener empleados: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@seguridad_bp.route('/api/incidencias/<int:id_incidencia>/asignar', methods=['POST'])
def api_asignar_empleado_incidencia(id_incidencia):
    """API para asignar un empleado a una incidencia"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = request.get_json()
        id_empleado = data.get('id_empleado')
        estado = data.get('estado', 'En proceso')
        
        if not id_empleado:
            return jsonify({'error': 'id_empleado es requerido'}), 400

        resultado = Incidencia.asignar_empleado(id_incidencia, id_empleado, estado)
        
        if resultado.get('error'):
            return jsonify(resultado), 400
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f"Error al asignar empleado: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =======================================
# API para Consultar Actividad
# =======================================

@seguridad_bp.route('/api/actividad/estadisticas', methods=['GET'])
def api_estadisticas_actividad():
    """API para obtener estadísticas de actividad del sistema"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Obtener estadísticas generales
        estadisticas = {}

        # Total de incidencias
        cursor.execute("SELECT COUNT(*) as total FROM INCIDENCIA")
        estadisticas['total_incidencias'] = cursor.fetchone()['total']

        # Incidencias por estado
        cursor.execute("""
            SELECT aei.estado_historial, COUNT(*) as cantidad
            FROM ASIGNAR_EMPLEADO_INCIDENCIA aei
            GROUP BY aei.estado_historial
        """)
        estadisticas['por_estado'] = cursor.fetchall()

        # Incidencias del mes actual
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM INCIDENCIA
            WHERE MONTH(fecha_registro) = MONTH(CURRENT_DATE())
            AND YEAR(fecha_registro) = YEAR(CURRENT_DATE())
        """)
        estadisticas['mes_actual'] = cursor.fetchone()['total']

        # Total de reservas
        cursor.execute("SELECT COUNT(*) as total FROM RESERVA")
        estadisticas['total_reservas'] = cursor.fetchone()['total']

        # Reservas por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as cantidad
            FROM RESERVA
            GROUP BY estado
        """)
        estadisticas['reservas_por_estado'] = cursor.fetchall()

        conexion.close()
        return jsonify(estadisticas)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seguridad_bp.route('/api/actividad/reciente', methods=['GET'])
def api_actividad_reciente():
    """API para obtener actividad reciente del sistema"""
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
        return jsonify({'error': 'No autorizado'}), 401

    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        limite = request.args.get('limite', 10, type=int)

        # Obtener incidencias recientes
        cursor.execute("""
            SELECT 
                i.id_incidencia,
                i.descripcion,
                DATE_FORMAT(i.fecha_registro, '%d/%m/%Y %H:%i') as fecha,
                CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                aei.estado_historial as estado,
                'incidencia' as tipo
            FROM INCIDENCIA i
            LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
            LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
            ORDER BY i.fecha_registro DESC
            LIMIT %s
        """, (limite,))
        
        actividades = cursor.fetchall()
        conexion.close()

        return jsonify(actividades)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINTS PARA GENERAR INCIDENCIA
# ============================================================================

@seguridad_bp.route('/api/pacientes', methods=['GET'])
def api_obtener_pacientes():
    """API para obtener lista de pacientes"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        print('[API PACIENTES] Obteniendo lista de pacientes...')
        pacientes = Incidencia.obtener_pacientes()
        print(f'[API PACIENTES] Se obtuvieron {len(pacientes)} pacientes')
        
        return jsonify({
            'success': True,
            'pacientes': pacientes
        })
    except Exception as e:
        print(f'[API PACIENTES] Error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al obtener pacientes: {str(e)}'
        }), 500

@seguridad_bp.route('/api/incidencias/crear', methods=['POST'])
def api_crear_incidencia():
    """API para crear una nueva incidencia"""
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        print('[API CREAR INCIDENCIA] Datos recibidos:', data)
        
        id_paciente = data.get('id_paciente')
        descripcion = data.get('descripcion')
        categoria = data.get('categoria')
        prioridad = data.get('prioridad', 'Media')  # Valor por defecto
        id_empleado = data.get('id_empleado')  # Opcional
        
        # Validaciones
        if not id_paciente:
            return jsonify({
                'success': False,
                'message': 'Debe seleccionar un paciente'
            }), 400
        
        if not descripcion or not descripcion.strip():
            return jsonify({
                'success': False,
                'message': 'Debe ingresar una descripción'
            }), 400
        
        if not categoria:
            return jsonify({
                'success': False,
                'message': 'Debe seleccionar una categoría'
            }), 400
        
        # Crear la incidencia
        resultado = Incidencia.crear(
            descripcion=descripcion.strip(),
            id_paciente=id_paciente,
            categoria=categoria,
            prioridad=prioridad,
            id_empleado=id_empleado  # Puede ser None si no se asigna
        )
        
        print('[API CREAR INCIDENCIA] Resultado:', resultado)
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f'[API CREAR INCIDENCIA] Error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al crear incidencia: {str(e)}'
        }), 500

# =======================================
# API: CREAR REPORTE DE AUDITORÍA
# =======================================

@seguridad_bp.route('/api/reportes/crear', methods=['POST'])
def api_crear_reporte():
    """
    Crear un reporte vinculado a una auditoría
    """
    try:
        print('[API CREAR REPORTE] Iniciando creación de reporte...')
        
        # Verificar sesión
        if 'usuario_id' not in session or session.get('tipo_usuario') != 'empleado':
            return jsonify({
                'exito': False,
                'mensaje': 'No autorizado'
            }), 401
        
        id_empleado = session.get('usuario_id')
        
        # Obtener datos del formulario
        id_auditoria = request.form.get('id_auditoria')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        tipo = request.form.get('tipo')
        archivo = request.files.get('archivo')
        
        print(f'[API CREAR REPORTE] Datos recibidos: id_auditoria={id_auditoria}, nombre={nombre}, tipo={tipo}')
        
        # Validaciones
        if not all([id_auditoria, nombre, descripcion, tipo]):
            return jsonify({
                'exito': False,
                'mensaje': 'Faltan datos obligatorios'
            }), 400
        
        # Importar bd aquí para evitar importaciones circulares
        from bd import obtener_conexion_dict
        
        conexion, cursor = obtener_conexion_dict()
        
        try:
            # Verificar que la auditoría existe
            cursor.execute("SELECT id_auditoria, accion FROM AUDITORIA WHERE id_auditoria = %s", (id_auditoria,))
            auditoria = cursor.fetchone()
            
            if not auditoria:
                return jsonify({
                    'exito': False,
                    'mensaje': 'La auditoría especificada no existe'
                }), 404
            
            # Generar código para el reporte (usando id_auditoria)
            codigo = f"REP-AUD-{id_auditoria}"
            
            # Crear el nombre completo incluyendo referencia a auditoría
            nombre_completo = f"{nombre} (Auditoría #{id_auditoria})"
            
            # Insertar el reporte en la tabla REPORTE
            # Nota: La descripción incluirá el id_auditoria para mantener la relación
            query_insert = """
                INSERT INTO REPORTE (codigo, nombre, tipo, fecha_creacion, id_empleado)
                VALUES (%s, %s, %s, NOW(), %s)
            """
            
            cursor.execute(query_insert, (codigo, nombre_completo, tipo, id_empleado))
            id_reporte = cursor.lastrowid
            
            print(f'[API CREAR REPORTE] Reporte creado con ID: {id_reporte}')
            
            # Si hay archivo, guardarlo
            nombre_archivo = None
            if archivo and archivo.filename:
                import os
                from werkzeug.utils import secure_filename
                
                # Crear directorio si no existe
                upload_folder = os.path.join('static', 'uploads', 'reportes')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Generar nombre seguro para el archivo
                filename = secure_filename(archivo.filename)
                timestamp = int(time.time())
                nombre_archivo = f"{timestamp}_{filename}"
                ruta_archivo = os.path.join(upload_folder, nombre_archivo)
                
                # Guardar archivo
                archivo.save(ruta_archivo)
                print(f'[API CREAR REPORTE] Archivo guardado: {nombre_archivo}')
                
                # Intentar guardar referencia en REPORTE_ARCHIVO si la tabla existe
                try:
                    query_archivo = """
                        INSERT INTO REPORTE_ARCHIVO (id_reporte, nombre_archivo, ruta_archivo, fecha_subida)
                        VALUES (%s, %s, %s, NOW())
                    """
                    cursor.execute(query_archivo, (id_reporte, filename, nombre_archivo))
                    print(f'[API CREAR REPORTE] Archivo registrado en BD')
                except Exception as e:
                    print(f'[API CREAR REPORTE] Advertencia al guardar archivo en BD: {e}')
                    # No fallar si la tabla no existe
            
            # También registrar en AUDITORIA esta acción
            try:
                from flask import request as flask_request
                ip_address = flask_request.remote_addr
                
                query_auditoria = """
                    INSERT INTO AUDITORIA (id_empleado, accion, descripcion, tipo_evento, modulo, ip_address, fecha_registro)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(query_auditoria, (
                    id_empleado,
                    'Creación de Reporte',
                    f'Se creó el reporte "{nombre}" vinculado a la auditoría #{id_auditoria}: {descripcion}',
                    'Creación',
                    'Seguridad',
                    ip_address
                ))
            except Exception as e:
                print(f'[API CREAR REPORTE] Advertencia al registrar en auditoría: {e}')
            
            conexion.commit()
            
            return jsonify({
                'exito': True,
                'mensaje': 'Reporte registrado exitosamente',
                'id_reporte': id_reporte,
                'codigo': codigo
            }), 201
            
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()
            
    except Exception as e:
        print(f'[API CREAR REPORTE] Error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al crear el reporte: {str(e)}'
        }), 500
