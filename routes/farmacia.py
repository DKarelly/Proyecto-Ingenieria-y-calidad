from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.farmacia import Medicamento, DetalleMedicamento
from bd import obtener_conexion
from datetime import date

farmacia_bp = Blueprint('farmacia', __name__, url_prefix='/farmacia')

@farmacia_bp.before_request
def check_session():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios.login'))
    if session.get('id_rol') not in [1, 4]:  # 1 = admin, 4 = farmacia
        return redirect(url_for('home'))

@farmacia_bp.route('/')
def farmacia():
    return render_template('panel.html', subsistema='farmacia')

@farmacia_bp.route('/gestionar-recepcion-medicamentos')
def gestionar_recepcion_medicamentos():
    # Pasar la fecha actual para el formulario
    return render_template('gestionarRecepcionMedicamentos.html', current_date=date.today().isoformat())

@farmacia_bp.route('/gestionar-entrega-medicamentos')
def gestionar_entrega_medicamentos():
    return render_template('gestionarEntregaMedicamentos.html')

# Medicamentos - API
@farmacia_bp.route('/api/medicamentos', methods=['GET'])
def api_listar_medicamentos():
    medicamentos = Medicamento.listar()
    return jsonify(medicamentos), 200

@farmacia_bp.route('/api/medicamentos/crear', methods=['POST'])
def api_crear_medicamento():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '')
    stock = data.get('stock')
    fecha_vencimiento = data.get('fecha_vencimiento')

    if not nombre or stock is None or not fecha_vencimiento:
        return jsonify({'error': 'Campos requeridos: nombre, stock, fecha_vencimiento'}), 400

    try:
        res = Medicamento.crear(nombre, descripcion, int(stock), fecha_vencimiento)
        return jsonify(res), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/medicamentos/<int:id_medicamento>/actualizar', methods=['PUT'])
def api_actualizar_medicamento(id_medicamento):
    data = request.get_json() or {}
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '')
    stock = data.get('stock')
    fecha_vencimiento = data.get('fecha_vencimiento')

    if not nombre or stock is None or not fecha_vencimiento:
        return jsonify({'error': 'Campos requeridos: nombre, stock, fecha_vencimiento'}), 400

    try:
        res = Medicamento.actualizar(id_medicamento, nombre, descripcion, int(stock), fecha_vencimiento)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/medicamentos/<int:id_medicamento>/eliminar', methods=['DELETE'])
def api_eliminar_medicamento(id_medicamento):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM MEDICAMENTO WHERE id_medicamento = %s", (id_medicamento,))
            conexion.commit()
            return jsonify({'deleted_rows': cursor.rowcount}), 200
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Entregas - API
@farmacia_bp.route('/api/entregas', methods=['GET'])
def api_listar_entregas():
    try:
        entregas = DetalleMedicamento.listar_entregas()
        return jsonify(entregas), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@farmacia_bp.route('/api/entregas/registrar', methods=['POST'])
def api_registrar_entrega():
    data = request.get_json() or {}
    id_empleado = data.get('id_empleado')
    id_paciente = data.get('id_paciente')
    id_medicamento = data.get('id_medicamento')
    cantidad = data.get('cantidad')

    if not all([id_empleado, id_paciente, id_medicamento, cantidad]):
        return jsonify({'error': 'Campos requeridos: id_empleado, id_paciente, id_medicamento, cantidad'}), 400

    try:
        resultado = DetalleMedicamento.registrar_entrega(int(id_empleado), int(id_paciente), int(id_medicamento), int(cantidad))
        if resultado.get('error'):
            return jsonify(resultado), 400
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500