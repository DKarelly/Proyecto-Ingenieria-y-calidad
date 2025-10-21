from flask import Blueprint, render_template, jsonify, request
from models.incidencia import Incidencia
from models.paciente import Paciente
from datetime import datetime

incidencias_bp = Blueprint('incidencias', __name__, url_prefix='/incidencias')

@incidencias_bp.route('/')
def index():
    """Ruta principal del módulo de incidencias"""
    return render_template('incidencias/index.html')

@incidencias_bp.route('/generar-informe')
def generar_informe():
    """Vista para generar informes de incidencias"""
    return render_template('incidencias/generar_informe.html')

# ============= API ENDPOINTS =============

@incidencias_bp.route('/api/pacientes', methods=['GET'])
def obtener_pacientes():
    """Retorna la lista de pacientes para el selector"""
    try:
        pacientes = Paciente.obtener_todos()
        return jsonify({
            'success': True,
            'data': pacientes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener pacientes: {str(e)}'
        }), 500

@incidencias_bp.route('/api/categorias', methods=['GET'])
def obtener_categorias():
    """Retorna las categorías de incidencias"""
    try:
        categorias = Incidencia.obtener_categorias()
        return jsonify({
            'success': True,
            'data': categorias
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener categorías: {str(e)}'
        }), 500

@incidencias_bp.route('/api/estados', methods=['GET'])
def obtener_estados():
    """Retorna los estados de incidencias"""
    try:
        estados = Incidencia.obtener_estados()
        return jsonify({
            'success': True,
            'data': estados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estados: {str(e)}'
        }), 500

@incidencias_bp.route('/api/generar-informe', methods=['POST'])
def api_generar_informe():
    """Genera un informe de incidencias según los filtros aplicados"""
    try:
        data = request.get_json()
        paciente_id = data.get('paciente_id')
        fecha = data.get('fecha')
        categoria_id = data.get('categoria_id')
        estado = data.get('estado')
        
        # Obtener todas las incidencias
        incidencias = Incidencia.obtener_todas()
        
        # Aplicar filtros si existen
        incidencias_filtradas = incidencias
        
        if fecha:
            incidencias_filtradas = [
                inc for inc in incidencias_filtradas 
                if inc['fechaRegistro'] == fecha
            ]
        
        if estado and estado != 'Todos':
            incidencias_filtradas = [
                inc for inc in incidencias_filtradas 
                if inc['estado'] == estado
            ]
        
        # Agregar información del paciente si se seleccionó uno
        paciente_info = None
        if paciente_id:
            pacientes = Paciente.obtener_todos()
            paciente_info = next((p for p in pacientes if p['id'] == int(paciente_id)), None)
        
        return jsonify({
            'success': True,
            'data': {
                'incidencias': incidencias_filtradas,
                'paciente': paciente_info,
                'filtros': {
                    'fecha': fecha,
                    'categoria': categoria_id,
                    'estado': estado
                },
                'total': len(incidencias_filtradas)
            },
            'message': f'Se encontraron {len(incidencias_filtradas)} incidencias'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar informe: {str(e)}'
        }), 500

@incidencias_bp.route('/api/incidencia/<int:id>', methods=['GET'])
def obtener_incidencia_detalle(id):
    """Retorna los detalles de una incidencia específica"""
    try:
        incidencia = Incidencia.obtener_por_id(id)
        if incidencia:
            return jsonify({
                'success': True,
                'data': incidencia
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Incidencia no encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener incidencia: {str(e)}'
        }), 500
