from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request, send_file
from models.reporte import Reporte
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import bd
import pymysql.cursors

reportes_bp = Blueprint("reportes", __name__)

# Configuración de uploads
UPLOAD_FOLDER = 'uploads/reportes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}

def obtener_conexion_dict():
    """Helper para obtener conexión con DictCursor"""
    conexion = bd.obtener_conexion()
    return conexion, conexion.cursor(pymysql.cursors.DictCursor)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Asegura que la carpeta de uploads exista"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@reportes_bp.route("/")
def panel():
    if "usuario_id" not in session:
        return redirect(url_for("home"))
    if session.get("tipo_usuario") != "empleado":
        return redirect(url_for("home"))
    return render_template("panel.html", subsistema="reportes")

@reportes_bp.route("/consultar-por-categoria")
def consultar_por_categoria():
    if "usuario_id" not in session:
        return redirect(url_for("home"))
    if session.get("tipo_usuario") != "empleado":
        return redirect(url_for("home"))
    return render_template("consultar_por_categoria.html")

@reportes_bp.route("/generar-reporte-actividad")
def generar_reporte_actividad():
    if "usuario_id" not in session:
        return redirect(url_for("home"))
    if session.get("tipo_usuario") != "empleado":
        return redirect(url_for("home"))
    return render_template("generar_reporte_actividad.html")

@reportes_bp.route("/ocupacion-recursos")
def ocupacion_recursos():
    if "usuario_id" not in session:
        return redirect(url_for("home"))
    if session.get("tipo_usuario") != "empleado":
        return redirect(url_for("home"))
    return render_template("generar_ocupacion_recursos.html")

@reportes_bp.route("/api/reportes", methods=["GET"])
def api_obtener_reportes():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    try:
        reportes = Reporte.obtener_todos()
        return jsonify(reportes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/por-categoria", methods=["POST"])
def api_reportes_por_categoria():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    id_categoria = data.get("id_categoria")
    try:
        reportes = Reporte.obtener_por_categoria(id_categoria)
        return jsonify(reportes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/crear", methods=["POST"])
def api_crear_reporte():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    try:
        resultado = Reporte.crear(
            id_categoria=data.get("id_categoria"),
            tipo=data.get("tipo"),
            descripcion=data.get("descripcion"),
            contenido_json=data.get("contenido_json"),
            id_empleado=session.get("id_empleado")
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/por-tipo", methods=["POST"])
def api_reportes_por_tipo():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    tipo = data.get("tipo")
    try:
        reportes = Reporte.obtener_por_tipo(tipo)
        return jsonify(reportes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/por-empleado", methods=["POST"])
def api_reportes_por_empleado():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    id_empleado = data.get("id_empleado")
    try:
        reportes = Reporte.obtener_por_empleado(id_empleado)
        return jsonify(reportes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/por-fechas", methods=["POST"])
def api_reportes_por_fechas():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")
    try:
        reportes = Reporte.obtener_por_fechas(fecha_inicio, fecha_fin)
        return jsonify(reportes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/categorias", methods=["GET"])
def api_obtener_categorias():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    try:
        conexion, cursor = obtener_conexion_dict()
        cursor.execute("""
            SELECT id_categoria, nombre, descripcion
            FROM CATEGORIA
            ORDER BY nombre
        """)
        categorias = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/empleados", methods=["GET"])
def api_obtener_empleados():
    """API para obtener empleados - filtra solo médicos (id_rol = 2) si se especifica"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    try:
        # Verificar si se solicita solo médicos
        solo_medicos = request.args.get('solo_medicos', 'false').lower() == 'true'
        formato = request.args.get('formato', 'array')  # 'array' o 'object'
        
        conexion, cursor = obtener_conexion_dict()
        
        sql = """
            SELECT 
                e.id_empleado, 
                e.nombres, 
                e.apellidos, 
                COALESCE(esp.nombre, 'Sin especialidad') as especialidad,
                r.nombre as rol
            FROM EMPLEADO e
            LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
            LEFT JOIN ROL r ON e.id_rol = r.id_rol
            WHERE e.estado = 'Activo'
        """
        
        if solo_medicos:
            sql += " AND e.id_rol = 2"
            print(f"[API EMPLEADOS] Filtrando solo médicos (id_rol = 2)")
        
        sql += " ORDER BY e.nombres, e.apellidos"
        
        cursor.execute(sql)
        empleados = cursor.fetchall()
        
        print(f"[API EMPLEADOS] Total empleados retornados: {len(empleados)}")
        
        cursor.close()
        conexion.close()
        
        # Devolver en formato solicitado
        if formato == 'object':
            return jsonify({
                'success': True,
                'empleados': empleados
            })
        else:
            return jsonify(empleados)
        
    except Exception as e:
        print(f"[API EMPLEADOS] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@reportes_bp.route("/api/tipos-recursos", methods=["GET"])
def api_obtener_tipos_recursos():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    try:
        conexion, cursor = obtener_conexion_dict()
        cursor.execute("""
            SELECT id_tipo_recurso, nombre, descripcion
            FROM TIPO_RECURSO
            ORDER BY nombre
        """)
        tipos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(tipos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/auditoria", methods=["POST"])
def api_obtener_auditoria():
    """API para obtener registros de auditoría con filtros"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    try:
        data = request.get_json() or {}
        
        id_empleado = data.get('id_empleado')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        modulo = data.get('modulo')
        tipo_evento = data.get('tipo_evento')
        limite = data.get('limite', 50)
        
        print(f"[API AUDITORIA] Filtros recibidos: empleado={id_empleado}, fechas={fecha_inicio} a {fecha_fin}, tipo={tipo_evento}, limite={limite}")
        
        conexion, cursor = obtener_conexion_dict()
        
        sql = """
            SELECT 
                a.id_auditoria,
                a.accion,
                a.modulo,
                a.tipo_evento,
                a.descripcion,
                CONCAT(COALESCE(e.nombres, ''), ' ', COALESCE(e.apellidos, '')) as empleado,
                a.fecha_registro,
                a.ip_address
            FROM AUDITORIA a
            LEFT JOIN EMPLEADO e ON a.id_empleado = e.id_empleado
            WHERE 1=1
        """
        params = []
        
        if id_empleado:
            sql += " AND a.id_empleado = %s"
            params.append(id_empleado)
        
        if fecha_inicio:
            sql += " AND DATE(a.fecha_registro) >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            sql += " AND DATE(a.fecha_registro) <= %s"
            params.append(fecha_fin)
        
        if modulo:
            sql += " AND a.modulo = %s"
            params.append(modulo)
        
        if tipo_evento:
            sql += " AND a.tipo_evento = %s"
            params.append(tipo_evento)
        
        sql += " ORDER BY a.fecha_registro DESC LIMIT %s"
        params.append(limite)
        
        print(f"[API AUDITORIA] SQL: {sql}")
        print(f"[API AUDITORIA] Params: {params}")
        
        cursor.execute(sql, tuple(params))
        actividades = cursor.fetchall()
        
        print(f"[API AUDITORIA] Registros encontrados: {len(actividades)}")
        
        # Formatear las fechas en Python
        for actividad in actividades:
            if actividad.get('fecha_registro'):
                actividad['fecha_formateada'] = actividad['fecha_registro'].strftime('%d/%m/%Y %H:%M:%S')
        
        if len(actividades) > 0:
            print(f"[API AUDITORIA] Primer registro: {actividades[0]}")
        
        cursor.close()
        conexion.close()
        
        return jsonify(actividades)
    except Exception as e:
        print(f"[API AUDITORIA] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/recursos-ocupacion", methods=["POST"])
def api_recursos_ocupacion():
    """API para obtener recursos con su ocupación desde la tabla RECURSO"""
    print("[API RECURSOS-OCUPACION] Iniciando endpoint...")
    
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        print("[API RECURSOS-OCUPACION] Usuario no autorizado")
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        data = request.get_json() or {}
        print(f"[API RECURSOS-OCUPACION] Datos recibidos: {data}")
        
        id_tipo_recurso = data.get('id_tipo_recurso')
        limite = data.get('limite', 100)
        
        print(f"[API RECURSOS-OCUPACION] Filtros - tipo: {id_tipo_recurso}, limite: {limite}")
        
        conexion, cursor = obtener_conexion_dict()
        print("[API RECURSOS-OCUPACION] Conexión establecida con DictCursor")
        
        # Query simplificado - la tabla OPERACION_RECURSO no tiene fecha_operacion
        # Solo listamos recursos con conteo de operaciones
        sql = """
            SELECT 
                r.id_recurso,
                r.nombre,
                COALESCE(tr.nombre, 'Sin tipo') as tipo_recurso,
                COALESCE(r.estado, 'Activo') as estado,
                r.id_tipo_recurso,
                COALESCE(
                    (SELECT COUNT(*) 
                     FROM OPERACION_RECURSO ore
                     WHERE ore.id_recurso = r.id_recurso
                    ), 0
                ) as operaciones_mes
            FROM RECURSO r
            LEFT JOIN TIPO_RECURSO tr ON r.id_tipo_recurso = tr.id_tipo_recurso
            WHERE 1=1
        """
        params = []
        
        if id_tipo_recurso:
            sql += " AND r.id_tipo_recurso = %s"
            params.append(id_tipo_recurso)
            print(f"[API RECURSOS-OCUPACION] Filtrando por tipo: {id_tipo_recurso}")
        
        sql += " ORDER BY r.nombre LIMIT %s"
        params.append(limite)
        
        print(f"[API RECURSOS-OCUPACION] Ejecutando query...")
        
        cursor.execute(sql, tuple(params))
            
        recursos = cursor.fetchall()
        
        print(f"[API RECURSOS-OCUPACION] Recursos obtenidos: {len(recursos)}")
        if recursos:
            print(f"[API RECURSOS-OCUPACION] Primer recurso: {recursos[0]}")
        
        cursor.close()
        conexion.close()
        
        print(f"[API RECURSOS-OCUPACION] Retornando {len(recursos)} recursos")
        return jsonify(recursos)
        
    except Exception as e:
        print(f"[API RECURSOS-OCUPACION] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/recursos-por-tipo/<int:id_tipo>", methods=["GET"])
def api_recursos_por_tipo(id_tipo):
    """API para obtener recursos filtrados por tipo (dropdown cascada)"""
    print(f"[API RECURSOS-POR-TIPO] Obteniendo recursos del tipo: {id_tipo}")
    
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        print("[API RECURSOS-POR-TIPO] Usuario no autorizado")
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        conexion, cursor = obtener_conexion_dict()
        print("[API RECURSOS-POR-TIPO] Conexión establecida")
        
        sql = """
            SELECT 
                id_recurso,
                nombre,
                estado
            FROM RECURSO
            WHERE id_tipo_recurso = %s
            AND (estado = 'Activo' OR estado = 'Disponible')
            ORDER BY nombre
        """
        
        cursor.execute(sql, (id_tipo,))
        recursos = cursor.fetchall()
        
        print(f"[API RECURSOS-POR-TIPO] Recursos encontrados: {len(recursos)}")
        
        cursor.close()
        conexion.close()
        
        return jsonify(recursos)
        
    except Exception as e:
        print(f"[API RECURSOS-POR-TIPO] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/recursos/<int:id_recurso>/detalle", methods=["GET"])
def api_detalle_recurso(id_recurso):
    """API para obtener detalle de uso de un recurso con información de empleados"""
    print(f"[API DETALLE-RECURSO] Obteniendo detalle del recurso: {id_recurso}")
    
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        print("[API DETALLE-RECURSO] Usuario no autorizado")
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        conexion, cursor = obtener_conexion_dict()
        print("[API DETALLE-RECURSO] Conexión establecida")
        
        # Query actualizado: RESERVA → CITA → OPERACION → OPERACION_RECURSO
        # Obtiene información completa desde la cita programada
        sql = """
            SELECT 
                ore.id_operacion_recurso,
                ore.id_operacion,
                o.fecha_operacion,
                o.hora_inicio,
                o.hora_fin,
                o.observaciones as observaciones_operacion,
                c.id_cita,
                c.fecha_cita,
                c.diagnostico,
                c.observaciones as observaciones_cita,
                c.estado as estado_cita,
                CONCAT(COALESCE(p.nombres, ''), ' ', COALESCE(p.apellidos, '')) as paciente,
                p.id_paciente,
                p.documento_identidad as dni_paciente,
                CONCAT(COALESCE(e.nombres, ''), ' ', COALESCE(e.apellidos, '')) as medico,
                e.id_empleado,
                COALESCE(esp.nombre, 'Sin especialidad') as especialidad_medico,
                r.nombre as recurso,
                tr.nombre as tipo_recurso,
                COALESCE(s.nombre, 'Sin servicio') as servicio,
                res.estado as estado_reserva,
                res.tipo as tipo_reserva,
                DATE_FORMAT(o.fecha_operacion, '%%d/%%m/%%Y') as fecha_formateada,
                TIME_FORMAT(o.hora_inicio, '%%H:%%i') as hora_inicio_formateada,
                TIME_FORMAT(o.hora_fin, '%%H:%%i') as hora_fin_formateada
            FROM OPERACION_RECURSO ore
            INNER JOIN OPERACION o ON ore.id_operacion = o.id_operacion
            INNER JOIN RECURSO r ON ore.id_recurso = r.id_recurso
            INNER JOIN TIPO_RECURSO tr ON r.id_tipo_recurso = tr.id_tipo_recurso
            LEFT JOIN CITA c ON o.id_cita = c.id_cita
            LEFT JOIN RESERVA res ON c.id_reserva = res.id_reserva
            LEFT JOIN PACIENTE p ON res.id_paciente = p.id_paciente
            LEFT JOIN EMPLEADO e ON o.id_empleado = e.id_empleado
            LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
            LEFT JOIN PROGRAMACION prog ON res.id_programacion = prog.id_programacion
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            WHERE ore.id_recurso = %s
            ORDER BY o.fecha_operacion DESC, o.hora_inicio DESC
            LIMIT 100
        """
        
        cursor.execute(sql, (id_recurso,))
        usos = cursor.fetchall()
        
        print(f"[API DETALLE-RECURSO] Usos encontrados: {len(usos)}")
        
        # Convertir timedelta y datetime a strings para serialización JSON
        for uso in usos:
            # Convertir hora_inicio y hora_fin (timedelta) a strings
            if uso.get('hora_inicio') and hasattr(uso['hora_inicio'], 'total_seconds'):
                total_seconds = int(uso['hora_inicio'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                uso['hora_inicio'] = f"{hours:02d}:{minutes:02d}"
            
            if uso.get('hora_fin') and hasattr(uso['hora_fin'], 'total_seconds'):
                total_seconds = int(uso['hora_fin'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                uso['hora_fin'] = f"{hours:02d}:{minutes:02d}"
            
            # Convertir fecha_operacion (date) a string
            if uso.get('fecha_operacion') and hasattr(uso['fecha_operacion'], 'strftime'):
                uso['fecha_operacion'] = uso['fecha_operacion'].strftime('%Y-%m-%d')
        
        cursor.close()
        conexion.close()
        
        return jsonify(usos)
        
    except Exception as e:
        print(f"[API DETALLE-RECURSO] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============ MÓDULOS Y TIPOS DE EVENTO (para auditoría) ============

@reportes_bp.route("/api/modulos", methods=["GET"])
def api_obtener_modulos():
    """API para obtener módulos únicos de auditoría"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT DISTINCT modulo as nombre
            FROM AUDITORIA
            ORDER BY modulo
        """)
        modulos = cursor.fetchall()
        conexion.close()
        return jsonify(modulos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/tipos-evento", methods=["GET"])
def api_obtener_tipos_evento():
    """API para obtener tipos de evento únicos de auditoría"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT DISTINCT tipo_evento as nombre
            FROM AUDITORIA
            ORDER BY tipo_evento
        """)
        tipos = cursor.fetchall()
        conexion.close()
        return jsonify(tipos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/actividad", methods=["POST"])
def api_reporte_actividad():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")
    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        reporte = {}
        
        # Reservas en el período
        cursor.execute("""
            SELECT COUNT(*) as total, estado, COUNT(*) as cantidad
            FROM RESERVA
            WHERE fecha_reserva BETWEEN %s AND %s
            GROUP BY estado
        """, (fecha_inicio, fecha_fin))
        reporte["reservas"] = cursor.fetchall()
        
        # Incidencias en el período
        cursor.execute("""
            SELECT COUNT(*) as total, aei.estado_historial, COUNT(*) as cantidad
            FROM INCIDENCIA i
            LEFT JOIN ASIGNAR_EMPLEADO_INCIDENCIA aei ON i.id_incidencia = aei.id_incidencia
            WHERE i.fecha_registro BETWEEN %s AND %s
            GROUP BY aei.estado_historial
        """, (fecha_inicio, fecha_fin))
        reporte["incidencias"] = cursor.fetchall()
        
        # Servicios más solicitados
        cursor.execute("""
            SELECT s.nombre as servicio, COUNT(*) as cantidad
            FROM RESERVA r
            INNER JOIN SERVICIO s ON r.id_servicio = s.id_servicio
            WHERE r.fecha_reserva BETWEEN %s AND %s
            GROUP BY s.id_servicio
            ORDER BY cantidad DESC
            LIMIT 10
        """, (fecha_inicio, fecha_fin))
        reporte["servicios_populares"] = cursor.fetchall()
        
        # Empleados más activos
        cursor.execute("""
            SELECT CONCAT(e.nombres, ' ', e.apellidos) as empleado, COUNT(*) as reservas_atendidas
            FROM RESERVA r
            INNER JOIN EMPLEADO e ON r.id_empleado = e.id_empleado
            WHERE r.fecha_reserva BETWEEN %s AND %s
            GROUP BY e.id_empleado
            ORDER BY reservas_atendidas DESC
            LIMIT 10
        """, (fecha_inicio, fecha_fin))
        reporte["empleados_activos"] = cursor.fetchall()
        
        conexion.close()
        return jsonify(reporte)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/reportes/ocupacion-recursos", methods=["POST"])
def api_ocupacion_recursos():
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")
    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Ocupación de recursos por tipo
        cursor.execute("""
            SELECT rf.nombre_recurso, rf.tipo_recurso, COUNT(r.id_reserva) as veces_usado, rf.estado as estado_actual
            FROM RECURSO_FISICO rf
            LEFT JOIN RESERVA r ON rf.id_recurso = r.id_recurso AND r.fecha_reserva BETWEEN %s AND %s
            GROUP BY rf.id_recurso
            ORDER BY veces_usado DESC
        """, (fecha_inicio, fecha_fin))
        recursos = cursor.fetchall()
        
        # Estadísticas generales
        cursor.execute("""
            SELECT tipo_recurso, COUNT(*) as total_recursos,
                   SUM(CASE WHEN estado = 'Disponible' THEN 1 ELSE 0 END) as disponibles,
                   SUM(CASE WHEN estado = 'Ocupado' THEN 1 ELSE 0 END) as ocupados,
                   SUM(CASE WHEN estado = 'Mantenimiento' THEN 1 ELSE 0 END) as en_mantenimiento
            FROM RECURSO_FISICO
            GROUP BY tipo_recurso
        """)
        estadisticas = cursor.fetchall()
        
        conexion.close()
        return jsonify({"recursos": recursos, "estadisticas": estadisticas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =======================================
# API para Búsqueda en Tiempo Real
# =======================================

@reportes_bp.route("/api/reportes/buscar", methods=["POST"])
def api_buscar_reportes():
    """API para búsqueda de reportes en tiempo real"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.get_json() or {}
    
    # Limpiar y validar los filtros
    filtros = {
        'busqueda': str(data.get('busqueda', '')).strip(),
        'id_categoria': None,
        'tipo': None,
        'fecha_inicio': None,
        'fecha_fin': None,
        'limite': 50
    }
    
    # Validar id_categoria
    if data.get('id_categoria'):
        try:
            filtros['id_categoria'] = int(data.get('id_categoria'))
        except (ValueError, TypeError):
            pass  # Mantener como None si no es válido
    
    # Validar tipo
    if data.get('tipo') and str(data.get('tipo')).strip():
        filtros['tipo'] = str(data.get('tipo')).strip()
    
    # Validar fechas
    if data.get('fecha_inicio') and str(data.get('fecha_inicio')).strip():
        filtros['fecha_inicio'] = str(data.get('fecha_inicio')).strip()
    
    if data.get('fecha_fin') and str(data.get('fecha_fin')).strip():
        filtros['fecha_fin'] = str(data.get('fecha_fin')).strip()
    
    # Validar límite
    if data.get('limite'):
        try:
            filtros['limite'] = int(data.get('limite'))
        except (ValueError, TypeError):
            filtros['limite'] = 50
    
    try:
        print(f"[API BUSCAR] Filtros enviados: {filtros}")
        reportes = Reporte.buscar_reportes(filtros)
        return jsonify(reportes)
    except Exception as e:
        print(f"Error en api_buscar_reportes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =======================================
# API para Detalle de Reporte
# =======================================

@reportes_bp.route("/api/reportes/<int:id_reporte>", methods=["GET"])
def api_detalle_reporte(id_reporte):
    """API para obtener detalle completo de un reporte"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        reporte = Reporte.obtener_por_id(id_reporte)
        if reporte:
            # Convertir datetime a string si existe
            if 'fecha_creacion' in reporte and reporte['fecha_creacion']:
                if isinstance(reporte['fecha_creacion'], datetime):
                    reporte['fecha_creacion'] = reporte['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Obtener archivos adjuntos
            archivos = Reporte.obtener_archivos(id_reporte)
            reporte['archivos'] = archivos
            return jsonify(reporte)
        return jsonify({"error": "Reporte no encontrado"}), 404
    except Exception as e:
        print(f"Error en api_detalle_reporte: {e}")
        return jsonify({"error": str(e)}), 500

# =======================================
# API para Subir Archivos
# =======================================

@reportes_bp.route("/api/reportes/<int:id_reporte>/subir-archivo", methods=["POST"])
def api_subir_archivo(id_reporte):
    """API para subir archivos adjuntos a un reporte"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    if 'archivo' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400
    
    archivo = request.files['archivo']
    
    if archivo.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400
    
    if archivo and allowed_file(archivo.filename):
        try:
            ensure_upload_folder()
            
            # Generar nombre único
            filename = secure_filename(archivo.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            nombre_unico = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, nombre_unico)
            
            # Guardar archivo
            archivo.save(filepath)
            
            # Obtener información del archivo
            tamano = os.path.getsize(filepath)
            tipo = archivo.content_type
            
            # Registrar en BD
            resultado = Reporte.agregar_archivo(
                id_reporte=id_reporte,
                nombre_archivo=filename,
                ruta_archivo=filepath,
                tipo_archivo=tipo,
                tamano_bytes=tamano
            )
            
            if resultado['success']:
                return jsonify({
                    'success': True,
                    'message': 'Archivo subido exitosamente',
                    'archivo': {
                        'id_archivo': resultado['id_archivo'],
                        'nombre': filename,
                        'tamano': tamano
                    }
                })
            else:
                # Si falla el registro en BD, eliminar archivo
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({"error": resultado.get('error', 'Error al guardar archivo')}), 500
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Tipo de archivo no permitido"}), 400

# =======================================
# API para Descargar Archivo
# =======================================

@reportes_bp.route("/api/reportes/descargar-archivo/<int:id_archivo>", methods=["GET"])
def api_descargar_archivo(id_archivo):
    """API para descargar un archivo adjunto"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        import pymysql.cursors
        conexion = bd.obtener_conexion()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT nombre_archivo, ruta_archivo, tipo_archivo
            FROM REPORTE_ARCHIVO
            WHERE id_archivo = %s
        """, (id_archivo,))
        
        archivo_info = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if archivo_info and os.path.exists(archivo_info['ruta_archivo']):
            return send_file(
                archivo_info['ruta_archivo'],
                as_attachment=True,
                download_name=archivo_info['nombre_archivo'],
                mimetype=archivo_info['tipo_archivo']
            )
        
        return jsonify({"error": "Archivo no encontrado"}), 404
    except Exception as e:
        print(f"Error al descargar archivo: {e}")
        return jsonify({"error": str(e)}), 500

# =======================================
# API para Eliminar Archivo
# =======================================

@reportes_bp.route("/api/reportes/eliminar-archivo/<int:id_archivo>", methods=["DELETE"])
def api_eliminar_archivo(id_archivo):
    """API para eliminar un archivo adjunto"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        resultado = Reporte.eliminar_archivo(id_archivo)
        
        if resultado['success']:
            # Eliminar archivo físico si existe
            if 'ruta_archivo' in resultado and os.path.exists(resultado['ruta_archivo']):
                os.remove(resultado['ruta_archivo'])
            
            return jsonify({"success": True, "message": "Archivo eliminado exitosamente"})
        
        return jsonify({"error": resultado.get('error', 'Error al eliminar archivo')}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =======================================
# API para Eliminar Reporte
# =======================================

@reportes_bp.route("/api/reportes/<int:id_reporte>/eliminar", methods=["DELETE"])
def api_eliminar_reporte(id_reporte):
    """API para eliminar un reporte completo"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        # Primero obtener los archivos asociados para eliminarlos
        archivos = Reporte.obtener_archivos(id_reporte)
        
        # Eliminar archivos físicos
        for archivo in archivos:
            if archivo.get('ruta_archivo') and os.path.exists(archivo['ruta_archivo']):
                try:
                    os.remove(archivo['ruta_archivo'])
                except Exception as e:
                    print(f"Error eliminando archivo físico: {e}")
        
        # Eliminar reporte de la base de datos (esto también eliminará los registros de archivos por CASCADE)
        resultado = Reporte.eliminar(id_reporte)
        
        if resultado.get('success'):
            return jsonify({"success": True, "message": "Reporte eliminado exitosamente"})
        
        return jsonify({"error": resultado.get('error', 'Error al eliminar reporte')}), 500
    except Exception as e:
        print(f"Error en api_eliminar_reporte: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =======================================
# API para Descargar Reporte (PDF/Excel)
# =======================================

@reportes_bp.route("/api/reportes/<int:id_reporte>/descargar", methods=["GET"])
def api_descargar_reporte(id_reporte):
    """API para descargar el reporte completo en PDF o Excel"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    formato = request.args.get('formato', 'pdf')  # pdf o excel
    
    try:
        reporte = Reporte.obtener_por_id(id_reporte)
        
        if not reporte:
            return jsonify({"error": "Reporte no encontrado"}), 404
        
        if formato == 'pdf':
            # Aquí implementarías la generación del PDF
            # Por ahora retornamos los datos JSON
            return jsonify({
                "mensaje": "Generación de PDF en desarrollo",
                "reporte": reporte
            })
        elif formato == 'excel':
            # Aquí implementarías la generación del Excel
            return jsonify({
                "mensaje": "Generación de Excel en desarrollo",
                "reporte": reporte
            })
        else:
            return jsonify({"error": "Formato no soportado"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =======================================
# API para Auditoría (Detalle y Archivos)
# =======================================

@reportes_bp.route("/api/auditoria/<int:id_auditoria>", methods=["GET"])
def api_detalle_auditoria(id_auditoria):
    """API para obtener detalle de un registro de auditoría"""
    print(f"[API DETALLE AUDITORIA] Obteniendo detalle de auditoria ID: {id_auditoria}")
    
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        conexion, cursor = obtener_conexion_dict()
        
        sql = """
            SELECT 
                a.id_auditoria,
                a.accion,
                a.modulo,
                a.tipo_evento,
                a.descripcion,
                CONCAT(COALESCE(e.nombres, ''), ' ', COALESCE(e.apellidos, '')) as empleado,
                a.fecha_registro,
                a.ip_address
            FROM AUDITORIA a
            LEFT JOIN EMPLEADO e ON a.id_empleado = e.id_empleado
            WHERE a.id_auditoria = %s
        """
        cursor.execute(sql, (id_auditoria,))
        actividad = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if actividad:
            # Formatear fecha en Python
            if actividad.get('fecha_registro'):
                actividad['fecha_formateada'] = actividad['fecha_registro'].strftime('%d/%m/%Y %H:%M:%S')
            print(f"[API DETALLE AUDITORIA] Actividad encontrada: {actividad}")
            return jsonify(actividad)
        
        print(f"[API DETALLE AUDITORIA] Actividad no encontrada")
        return jsonify({"error": "Registro no encontrado"}), 404
        
    except Exception as e:
        print(f"[API DETALLE AUDITORIA] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/auditoria/<int:id_auditoria>", methods=["DELETE"])
def api_eliminar_auditoria(id_auditoria):
    """API para eliminar un registro de auditoría"""
    print(f"[API ELIMINAR AUDITORIA] Eliminando auditoria ID: {id_auditoria}")
    
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    try:
        conexion, cursor = obtener_conexion_dict()
        
        # Verificar que existe el registro
        cursor.execute("SELECT id_auditoria FROM AUDITORIA WHERE id_auditoria = %s", (id_auditoria,))
        if not cursor.fetchone():
            cursor.close()
            conexion.close()
            return jsonify({"exito": False, "mensaje": "Registro no encontrado"}), 404
        
        # Eliminar el registro
        cursor.execute("DELETE FROM AUDITORIA WHERE id_auditoria = %s", (id_auditoria,))
        conexion.commit()
        
        cursor.close()
        conexion.close()
        
        print(f"[API ELIMINAR AUDITORIA] Registro eliminado exitosamente")
        return jsonify({"exito": True, "mensaje": "Registro eliminado exitosamente"})
        
    except Exception as e:
        print(f"[API ELIMINAR AUDITORIA] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"exito": False, "mensaje": str(e)}), 500

@reportes_bp.route("/api/auditoria/<int:id_auditoria>/archivos", methods=["GET"])
def api_archivos_auditoria(id_auditoria):
    """API para obtener archivos de un registro de auditoría"""
    print(f"[API ARCHIVOS AUDITORIA] Obteniendo archivos de auditoria ID: {id_auditoria}")
    
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        conexion, cursor = obtener_conexion_dict()
        
        # Intentar obtener archivos si la tabla/columna existe
        sql = """
            SELECT id_archivo, nombre_archivo, ruta_archivo, tipo_archivo, 
                   tamano_bytes, fecha_subida
            FROM REPORTE_ARCHIVO 
            WHERE id_reporte = %s
            ORDER BY fecha_subida DESC
        """
        cursor.execute(sql, (id_auditoria,))
        archivos = cursor.fetchall()
        
        # Formatear fechas en Python
        for archivo in archivos:
            if archivo.get('fecha_subida'):
                archivo['fecha_subida'] = archivo['fecha_subida'].strftime('%d/%m/%Y %H:%M')
        
        cursor.close()
        conexion.close()
        
        print(f"[API ARCHIVOS AUDITORIA] Archivos encontrados: {len(archivos)}")
        return jsonify(archivos if archivos else [])
        
    except Exception as e:
        # Si hay error (tabla no existe, columna no existe, etc), devolver array vacío
        print(f"[API ARCHIVOS AUDITORIA] No se pudieron obtener archivos: {e}")
        return jsonify([])

@reportes_bp.route("/api/auditoria/descargar-archivo/<int:id_archivo>", methods=["GET"])
def api_descargar_archivo_auditoria(id_archivo):
    """API para descargar un archivo de auditoría"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT ruta_archivo, nombre_archivo FROM AUDITORIA_ARCHIVO WHERE id_archivo = %s", (id_archivo,))
        archivo = cursor.fetchone()
        conexion.close()
        
        if archivo and os.path.exists(archivo['ruta_archivo']):
            return send_file(archivo['ruta_archivo'], as_attachment=True, download_name=archivo['nombre_archivo'])
        
        return jsonify({"error": "Archivo no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/auditoria/exportar", methods=["GET"])
def api_exportar_auditoria():
    """API para exportar auditoría a PDF"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    # Obtener filtros
    id_empleado = request.args.get('id_empleado')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    tipo_evento = request.args.get('tipo_evento')
    
    # Por ahora retornar mensaje
    return jsonify({
        "mensaje": "Exportación a PDF en desarrollo",
        "filtros": {
            "id_empleado": id_empleado,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "tipo_evento": tipo_evento
        }
    })

# =======================================
# API para Recursos (Detalle y Archivos)
# =======================================

@reportes_bp.route("/api/recursos/<int:id_recurso>/archivos", methods=["GET"])
def api_archivos_recurso(id_recurso):
    """API para obtener archivos de un recurso"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        sql = """
            SELECT id_archivo, nombre_archivo, ruta_archivo, tipo_archivo, 
                   tamano_bytes, DATE_FORMAT(fecha_subida, '%d/%m/%Y %H:%i') as fecha_subida
            FROM RECURSO_ARCHIVO 
            WHERE id_recurso = %s
            ORDER BY fecha_subida DESC
        """
        cursor.execute(sql, (id_recurso,))
        archivos = cursor.fetchall()
        conexion.close()
        
        return jsonify(archivos)
    except Exception as e:
        print(f"Error en api_archivos_recurso: {e}")
        return jsonify([])

@reportes_bp.route("/api/recursos/descargar-archivo/<int:id_archivo>", methods=["GET"])
def api_descargar_archivo_recurso(id_archivo):
    """API para descargar un archivo de recurso"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        from bd import obtener_conexion
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT ruta_archivo, nombre_archivo FROM RECURSO_ARCHIVO WHERE id_archivo = %s", (id_archivo,))
        archivo = cursor.fetchone()
        conexion.close()
        
        if archivo and os.path.exists(archivo['ruta_archivo']):
            return send_file(archivo['ruta_archivo'], as_attachment=True, download_name=archivo['nombre_archivo'])
        
        return jsonify({"error": "Archivo no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/recursos-ocupacion/exportar", methods=["GET"])
def api_exportar_recursos():
    """API para exportar recursos a PDF"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    # Obtener filtros
    id_tipo_recurso = request.args.get('id_tipo_recurso')
    
    # Por ahora retornar mensaje
    return jsonify({
        "mensaje": "Exportación a PDF en desarrollo",
        "filtros": {
            "id_tipo_recurso": id_tipo_recurso
        }
    })

@reportes_bp.route("/api/auditoria/generar", methods=["POST"])
def api_generar_reporte_auditoria():
    """API para generar un nuevo registro de auditoría con archivo adjunto"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        # Obtener datos del formulario
        id_empleado = request.form.get('id_empleado')
        accion = request.form.get('accion')
        descripcion = request.form.get('descripcion', '')
        
        if not id_empleado or not accion or not descripcion:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        
        # Obtener IP del cliente
        ip_address = request.remote_addr
        
        # Obtener conexión a la base de datos
        import pymysql.cursors
        conexion = bd.obtener_conexion()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        # Insertar registro de auditoría (fecha_registro se genera automáticamente)
        sql_insert = """
            INSERT INTO AUDITORIA (id_empleado, accion, descripcion, tipo_evento, modulo, ip_address, fecha_registro)
            VALUES (%s, %s, %s, 'Registro Manual', 'Reportes', %s, NOW())
        """
        cursor.execute(sql_insert, (id_empleado, accion, descripcion, ip_address))
        id_auditoria = cursor.lastrowid
        
        # Manejar archivo adjunto si existe
        archivo_guardado = None
        if 'archivo' in request.files:
            archivo = request.files['archivo']
            if archivo and archivo.filename:
                try:
                    # Crear directorio si no existe
                    UPLOAD_FOLDER = os.path.join('static', 'uploads', 'auditoria')
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    # Generar nombre único
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = secure_filename(archivo.filename)
                    nombre_unico = f"audit_{timestamp}_{filename}"
                    filepath = os.path.join(UPLOAD_FOLDER, nombre_unico)
                    
                    # Guardar archivo
                    archivo.save(filepath)
                    tamano = os.path.getsize(filepath)
                    
                    # Intentar insertar en REPORTE_ARCHIVO (usando id_auditoria como id_reporte)
                    try:
                        sql_archivo = """
                            INSERT INTO REPORTE_ARCHIVO (id_reporte, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes, fecha_subida)
                            VALUES (%s, %s, %s, %s, %s, NOW())
                        """
                        cursor.execute(sql_archivo, (id_auditoria, filename, nombre_unico, archivo.content_type, tamano))
                        print(f'[GENERAR AUDITORIA] Archivo guardado: {nombre_unico}')
                    except Exception as e:
                        print(f'[GENERAR AUDITORIA] No se pudo guardar referencia en BD: {e}')
                        # No fallar si la tabla no existe
                    
                    archivo_guardado = {
                        'nombre': filename,
                        'ruta': filepath,
                        'tipo': archivo.content_type,
                        'tamano': tamano
                    }
                except Exception as e:
                    print(f'[GENERAR AUDITORIA] Error al guardar archivo: {e}')
                    # No fallar si hay error con el archivo
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return jsonify({
            "success": True,
            "mensaje": "Registro de auditoría creado exitosamente",
            "id_auditoria": id_auditoria,
            "archivo_adjunto": archivo_guardado is not None
        })
        
    except Exception as e:
        print(f"Error al generar registro de auditoría: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/recursos-ocupacion/generar", methods=["POST"])
def api_generar_reporte_recursos():
    """API para vincular una operación existente (desde RESERVA) con un recurso"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        # Obtener datos del formulario
        id_operacion = request.form.get('id_operacion')  # ID de operación existente
        id_recurso = request.form.get('id_recurso')
        observaciones = request.form.get('observaciones', '').strip()
        
        print(f"[VINCULAR OPERACION-RECURSO] Datos recibidos:")
        print(f"  - id_operacion: {id_operacion}")
        print(f"  - id_recurso: {id_recurso}")
        print(f"  - observaciones: {observaciones[:50] if observaciones else 'Sin observaciones'}...")
        
        # Validaciones
        if not id_operacion:
            return jsonify({"error": "Debe seleccionar una operación"}), 400
        if not id_recurso:
            return jsonify({"error": "Debe seleccionar un recurso"}), 400
        
        # Obtener conexión a la base de datos con DictCursor
        conexion, cursor = obtener_conexion_dict()
        
        # Verificar que la operación existe y tiene cita
        cursor.execute("""
            SELECT o.id_operacion, o.id_cita, c.id_reserva, r.id_paciente
            FROM OPERACION o
            INNER JOIN CITA c ON o.id_cita = c.id_cita
            INNER JOIN RESERVA r ON c.id_reserva = r.id_reserva
            WHERE o.id_operacion = %s
        """, (id_operacion,))
        
        operacion = cursor.fetchone()
        
        if not operacion:
            cursor.close()
            conexion.close()
            return jsonify({"error": "La operación no existe o no tiene cita/reserva asociada"}), 400
        
        print(f"[VINCULAR OPERACION-RECURSO] Operación válida encontrada")
        
        # Actualizar observaciones de la operación si se proporcionaron
        if observaciones:
            print(f"[VINCULAR OPERACION-RECURSO] Actualizando observaciones de la operación...")
            cursor.execute("""
                UPDATE OPERACION 
                SET observaciones = %s
                WHERE id_operacion = %s
            """, (observaciones, id_operacion))
            print(f"[VINCULAR OPERACION-RECURSO] Observaciones actualizadas")
        
        # Verificar si ya existe el vínculo
        cursor.execute("""
            SELECT id_operacion_recurso 
            FROM OPERACION_RECURSO 
            WHERE id_operacion = %s AND id_recurso = %s
        """, (id_operacion, id_recurso))
        
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return jsonify({"error": "Esta operación ya está vinculada a este recurso"}), 400
        
        # Crear el vínculo OPERACION_RECURSO
        sql_operacion_recurso = """
            INSERT INTO OPERACION_RECURSO 
            (id_operacion, id_recurso)
            VALUES (%s, %s)
        """
        print(f"[VINCULAR OPERACION-RECURSO] Creando vínculo...")
        
        cursor.execute(sql_operacion_recurso, (id_operacion, id_recurso))
        
        conexion.commit()
        print(f"[VINCULAR OPERACION-RECURSO] Vínculo creado exitosamente")
        
        cursor.close()
        conexion.close()
        
        return jsonify({
            "success": True,
            "mensaje": "Operación vinculada al recurso exitosamente"
        })
        
    except Exception as e:
        print(f"[VINCULAR OPERACION-RECURSO] ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar hacer rollback si la conexión existe
        try:
            if 'conexion' in locals():
                conexion.rollback()
                print(f"[VINCULAR OPERACION-RECURSO] Rollback realizado")
        except:
            pass
            
        return jsonify({"error": str(e)}), 500
        
    except Exception as e:
        print(f"Error al generar reporte de recursos: {e}")
        return jsonify({"error": str(e)}), 500

# ============ ENDPOINTS AUXILIARES ============

@reportes_bp.route("/api/operaciones-disponibles", methods=["GET"])
def api_operaciones_disponibles():
    """API para obtener operaciones desde CITA que pueden vincularse a recursos"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        conexion, cursor = obtener_conexion_dict()
        
        # Obtener operaciones que tienen CITA con RESERVA
        sql = """
            SELECT 
                o.id_operacion,
                DATE_FORMAT(o.fecha_operacion, '%d/%m/%Y') as fecha,
                TIME_FORMAT(o.hora_inicio, '%H:%i') as hora_inicio,
                TIME_FORMAT(o.hora_fin, '%H:%i') as hora_fin,
                c.id_cita,
                c.diagnostico,
                c.estado as estado_cita,
                CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                p.documento_identidad as dni_paciente,
                CONCAT(e.nombres, ' ', e.apellidos) as medico,
                COALESCE(esp.nombre, 'Sin especialidad') as especialidad,
                COALESCE(s.nombre, 'Sin servicio') as servicio,
                o.observaciones,
                res.estado as estado_reserva
            FROM OPERACION o
            INNER JOIN CITA c ON o.id_cita = c.id_cita
            INNER JOIN RESERVA res ON c.id_reserva = res.id_reserva
            INNER JOIN PACIENTE p ON res.id_paciente = p.id_paciente
            LEFT JOIN EMPLEADO e ON o.id_empleado = e.id_empleado
            LEFT JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
            LEFT JOIN PROGRAMACION prog ON res.id_programacion = prog.id_programacion
            LEFT JOIN SERVICIO s ON prog.id_servicio = s.id_servicio
            WHERE c.id_cita IS NOT NULL
            ORDER BY o.fecha_operacion DESC, o.hora_inicio DESC
            LIMIT 100
        """
        
        cursor.execute(sql)
        operaciones = cursor.fetchall()
        
        print(f"[API OPERACIONES-DISPONIBLES] Operaciones encontradas: {len(operaciones)}")
        
        cursor.close()
        conexion.close()
        
        return jsonify(operaciones)
        
    except Exception as e:
        print(f"[API OPERACIONES-DISPONIBLES] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@reportes_bp.route("/api/pacientes", methods=["GET"])
def api_obtener_pacientes():
    """API para obtener la lista de pacientes para búsquedas"""
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        conexion = bd.obtener_conexion()
        cursor = conexion.cursor()
        
        sql = """
            SELECT 
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad,
                p.sexo,
                p.fecha_nacimiento
            FROM PACIENTE p
            ORDER BY p.apellidos, p.nombres
        """
        
        cursor.execute(sql)
        pacientes = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return jsonify(pacientes)
        
    except Exception as e:
        print(f"Error al obtener pacientes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
