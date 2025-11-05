from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.farmacia import Medicamento, DetalleMedicamento, Paciente, Empleado
from datetime import datetime

farmacia_bp = Blueprint('farmacia', __name__)

# Rutas de vistas
@farmacia_bp.route('/')
def index():
    if 'id_rol' not in session or session['id_rol'] not in [1, 5]:
        return redirect(url_for('usuarios.login'))
    return render_template('panel.html', subsistema='farmacia')

@farmacia_bp.route('/gestionar-medicamentos')
def gestionar_medicamentos():
    if 'id_rol' not in session or session['id_rol'] not in [1, 5]:
        return redirect(url_for('usuarios.login'))
    return render_template('gestionarMedicamentos.html')

@farmacia_bp.route('/gestionar-entrega-medicamentos')
def gestionar_entrega_medicamentos():
    if 'id_rol' not in session or session['id_rol'] not in [1, 5]:
        return redirect(url_for('usuarios.login'))
    return render_template('gestionarEntregaMedicamentos.html')

# API Endpoints para Medicamentos
@farmacia_bp.route('/api/medicamentos', methods=['GET'])
def api_listar_medicamentos():
    try:
        medicamentos = Medicamento.listar()
        return jsonify(medicamentos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/medicamentos', methods=['POST'])
def api_crear_medicamento():
    try:
        datos = request.json
        resultado = Medicamento.crear(
            datos['nombre'],
            datos['descripcion'],
            datos['stock'],
            datos['fecha_vencimiento']
        )
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/medicamentos/<int:id_medicamento>', methods=['GET'])
def api_obtener_medicamento(id_medicamento):
    try:
        medicamento = Medicamento.obtener_por_id(id_medicamento)
        if medicamento:
            return jsonify(medicamento)
        return jsonify({'error': 'Medicamento no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/medicamentos/<int:id_medicamento>', methods=['PUT'])
def api_actualizar_medicamento(id_medicamento):
    try:
        datos = request.json
        resultado = Medicamento.actualizar(
            id_medicamento,
            datos['nombre'],
            datos['descripcion'],
            datos['stock'],
            datos['fecha_vencimiento']
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/medicamentos/buscar', methods=['GET'])
def api_buscar_medicamentos():
    try:
        termino = request.args.get('termino', '')
        resultados = Medicamento.buscar(termino)
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoints para Entrega de Medicamentos
@farmacia_bp.route('/api/entregas', methods=['GET'])
def api_listar_entregas():
    try:
        entregas = DetalleMedicamento.listar_entregas()
        return jsonify(entregas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/entregas/<int:id_detalle>', methods=['GET'])
def api_obtener_entrega(id_detalle):
    try:
        entrega = DetalleMedicamento.obtener_entrega_por_id(id_detalle)
        if entrega:
            return jsonify(entrega)
        return jsonify({'error': 'Entrega no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/entregas/<int:id_detalle>', methods=['PUT'])
def api_actualizar_entrega(id_detalle):
    try:
        datos = request.json
        resultado = DetalleMedicamento.actualizar_entrega(
            id_detalle,
            datos['id_empleado'],
            datos['id_paciente'],
            datos['id_medicamento'],
            datos['cantidad']
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/entregas', methods=['POST'])
def api_registrar_entrega():
    try:
        datos = request.json
        resultado = DetalleMedicamento.registrar_entrega(
            datos['id_empleado'],
            datos['id_paciente'],
            datos['id_medicamento'],
            datos['cantidad']
        )
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoints para búsqueda de Pacientes y Empleados
@farmacia_bp.route('/api/pacientes/buscar', methods=['GET'])
def api_buscar_pacientes():
    try:
        termino = request.args.get('termino', '')
        resultados = Paciente.buscar(termino)
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/empleados/buscar', methods=['GET'])
def api_buscar_empleados():
    try:
        termino = request.args.get('termino', '')
        resultados = Empleado.buscar(termino)
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500