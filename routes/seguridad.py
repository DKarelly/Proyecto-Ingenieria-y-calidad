# Módulo de Seguridad - Auditoría, Respaldos, Roles y Permisos
from flask import Blueprint, render_template, request, jsonify
from models.registro_actividad import RegistroActividad
from models.empleado import Empleado

seguridad_bp = Blueprint('seguridad', __name__, url_prefix='/seguridad')

@seguridad_bp.route('/consultar-actividad')
def consultar_actividad():
    """Renderiza la página de consulta de actividad"""
    return render_template('seguridad/consultar_actividad.html')

@seguridad_bp.route('/api/registros', methods=['GET'])
def obtener_registros():
    """API para obtener registros de actividad con filtros"""
    try:
        # Obtener parámetros de filtrado
        empleado = request.args.get('empleado', '')
        fecha = request.args.get('fecha', '')
        horario = request.args.get('horario', '')
        
        filtros = {
            'empleado': empleado,
            'fecha': fecha,
            'horario': horario
        }
        
        # Buscar registros aplicando filtros
        registros = RegistroActividad.buscar_registros(filtros)
        
        return jsonify({
            'success': True,
            'data': registros
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@seguridad_bp.route('/api/empleados', methods=['GET'])
def obtener_empleados():
    """API para obtener lista de empleados"""
    try:
        empleados = Empleado.listar_empleados()
        return jsonify({
            'success': True,
            'data': empleados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@seguridad_bp.route('/api/exportar-registros', methods=['POST'])
def exportar_registros():
    """API para exportar registros en PDF o Excel"""
    try:
        formato = request.json.get('formato', 'pdf')
        # TODO: Implementar exportación real
        return jsonify({
            'success': True,
            'message': f'Registros exportados en formato {formato}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
