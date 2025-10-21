# Módulo de Reportes - Generación de reportes operativos y estadísticos
from flask import Blueprint, render_template, request, jsonify
from models.reporte import Reporte
from models.categoria import Categoria
from models.empleado import Empleado

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/consultar-por-categoria')
def consultar_por_categoria():
    """Renderiza la página de consulta de reportes por categoría"""
    return render_template('reportes/consultar_por_categoria.html')

@reportes_bp.route('/api/categorias', methods=['GET'])
def obtener_categorias():
    """API para obtener lista de categorías"""
    try:
        categorias = Categoria.listar_categorias()
        return jsonify({
            'success': True,
            'data': categorias
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@reportes_bp.route('/api/reportes', methods=['GET'])
def obtener_reportes():
    """API para obtener reportes con filtros"""
    try:
        categoria = request.args.get('categoria', '')
        fecha = request.args.get('fecha', '')
        
        # Buscar reportes aplicando filtros
        reportes = Reporte.buscar_reportes_por_categoria(categoria, fecha)
        
        return jsonify({
            'success': True,
            'data': reportes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@reportes_bp.route('/api/generar-reporte', methods=['POST'])
def generar_reporte():
    """API para generar un nuevo reporte"""
    try:
        data = request.json
        categoria = data.get('categoria')
        id_usuario = data.get('idUsuario', 1)
        nombre_empleado = data.get('nombreEmpleado', 'Sistema')
        
        if not categoria:
            return jsonify({
                'success': False,
                'message': 'Debe seleccionar una categoría'
            }), 400
        
        # Generar reporte
        nuevo_reporte = Reporte.generar_reporte(categoria, id_usuario, nombre_empleado)
        
        return jsonify({
            'success': True,
            'message': 'Reporte generado exitosamente',
            'data': nuevo_reporte
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@reportes_bp.route('/api/historial', methods=['GET'])
def obtener_historial():
    """API para obtener historial de reportes por categoría"""
    try:
        historial = Reporte.historial_reportes_por_categoria()
        return jsonify({
            'success': True,
            'data': historial
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@reportes_bp.route('/generar-reporte-actividad')
def generar_reporte_actividad():
    """Renderiza la página de generar reporte de actividad"""
    return render_template('reportes/generar_reporte_actividad.html')

@reportes_bp.route('/api/generar-actividad', methods=['POST'])
def generar_actividad():
    """API para generar reporte de actividad por empleado y fecha"""
    try:
        data = request.json
        id_empleado = data.get('idEmpleado')
        fecha = data.get('fecha')
        
        if not id_empleado or not fecha:
            return jsonify({
                'success': False,
                'message': 'Debe proporcionar empleado y fecha'
            }), 400
        
        # Generar reporte de actividad con recursos simulados
        recursos = []
        tipos_recursos = ['Consultorio', 'Equipo Médico', 'Laboratorio', 'Sala de Rayos X', 'Ambulancia']
        estados = ['Disponible', 'En Uso', 'Mantenimiento', 'Disponible', 'En Uso']
        
        for i in range(1, 11):  # Generar 10 recursos
            recursos.append({
                'idRecurso': i,
                'nombreRecurso': f'{tipos_recursos[i % len(tipos_recursos)]} {i}',
                'tipo': tipos_recursos[i % len(tipos_recursos)],
                'estado': estados[i % len(estados)],
                'descripcion': f'Recurso {tipos_recursos[i % len(tipos_recursos)]} asignado',
                'uso': f'{60 + (i * 5)}%'
            })
        
        return jsonify({
            'success': True,
            'message': 'Reporte de actividad generado',
            'data': {
                'recursos': recursos,
                'total': len(recursos),
                'idEmpleado': id_empleado,
                'fecha': fecha
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@reportes_bp.route('/generar-ocupacion-recursos')
def generar_ocupacion_recursos():
    """Renderiza la página de generar reporte de ocupación de recursos"""
    return render_template('reportes/generar_ocupacion_recursos.html')

@reportes_bp.route('/api/tipos-recurso', methods=['GET'])
def obtener_tipos_recurso():
    """API para obtener tipos de recursos"""
    try:
        from models.tipo_recurso import TipoRecurso
        tipos = TipoRecurso.listar_tipos_recurso()
        return jsonify({
            'success': True,
            'data': tipos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@reportes_bp.route('/api/recursos', methods=['GET'])
def obtener_recursos():
    """API para obtener recursos con filtros"""
    try:
        from models.recurso import Recurso
        
        tipo_recurso = request.args.get('tipoRecurso', '')
        nombre = request.args.get('nombre', '')
        
        if tipo_recurso:
            recursos = Recurso.buscar_por_tipo(tipo_recurso)
        elif nombre:
            recursos = Recurso.buscar_por_nombre(nombre)
        else:
            recursos = Recurso.listar_recursos()
        
        return jsonify({
            'success': True,
            'data': recursos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@reportes_bp.route('/api/generar-ocupacion', methods=['POST'])
def generar_ocupacion():
    """API para generar reporte de ocupación de recursos"""
    try:
        from models.reporte_ocupacion import ReporteOcupacion
        
        data = request.json
        tipo_recurso_id = data.get('tipoRecurso')
        
        # Generar reporte de ocupación
        reportes = ReporteOcupacion.generar_reporte_ocupacion(tipo_recurso_id)
        
        return jsonify({
            'success': True,
            'message': 'Reporte de ocupación generado exitosamente',
            'data': {
                'reportes': reportes,
                'total': len(reportes)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
