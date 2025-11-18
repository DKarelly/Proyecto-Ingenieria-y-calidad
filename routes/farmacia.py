from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.farmacia import Medicamento, DetalleMedicamento, Paciente, Empleado
import datetime

farmacia_bp = Blueprint('farmacia', __name__)

# Rutas de vistas
@farmacia_bp.route('/')
def index():
    if 'id_rol' not in session or session['id_rol'] not in [1, 4]:
        return redirect(url_for('usuarios.login'))
    # Redirigir al dashboard principal unificado
    return redirect(url_for('admin_panel', subsistema='farmacia'))

@farmacia_bp.route('/panel')
def panel():
    """Panel específico de farmacia para farmacéuticos (rol 4)"""
    if 'id_rol' not in session or session['id_rol'] not in [1, 4]:
        return redirect(url_for('usuarios.login'))

    # Estadísticas rápidas
    stats = {
        'medicamentos_recibidos': 0,
        'medicamentos_entregados': 0,
        'alertas_vencimiento': 0
    }

    # Medicamentos recibidos hoy
    try:
        hoy = datetime.date.today()
        medicamentos_hoy = Medicamento.obtener_recibidos_hoy()
        stats['medicamentos_recibidos'] = len(medicamentos_hoy) if medicamentos_hoy else 0
    except Exception as e:
        print(f"Error obteniendo medicamentos recibidos hoy: {e}")
        stats['medicamentos_recibidos'] = 0

    # Medicamentos entregados hoy
    try:
        entregas_hoy = DetalleMedicamento.listar_entregas()
        # Filtrar entregas de hoy
        hoy_str = datetime.date.today().strftime('%Y-%m-%d')
        entregas_hoy_filtradas = [e for e in entregas_hoy if isinstance(e.get('fecha_entrega'), str) and e.get('fecha_entrega') == hoy_str]
        stats['medicamentos_entregados'] = len(entregas_hoy_filtradas)
    except Exception as e:
        print(f"Error obteniendo medicamentos entregados hoy: {e}")
        stats['medicamentos_entregados'] = 0

    # Alertas de vencimiento (próximos 30 días)
    try:
        alertas = Medicamento.obtener_por_vencer(30)
        stats['alertas_vencimiento'] = len(alertas) if alertas else 0
    except Exception as e:
        print(f"Error obteniendo alertas de vencimiento: {e}")
        stats['alertas_vencimiento'] = 0

    # Medicamentos recientes (últimos 5)
    medicamentos_recientes = []
    try:
        medicamentos_recientes = Medicamento.obtener_recientes(5)
    except Exception as e:
        print(f"Error obteniendo medicamentos recientes: {e}")

    # Medicamentos por vencer (próximos 30 días, máximo 5)
    medicamentos_por_vencer = []
    try:
        medicamentos_por_vencer = Medicamento.obtener_por_vencer(30, limite=5)
        # Las fechas ya vienen en formato '%d/%m/%Y' del modelo, no necesitamos parsear
    except Exception as e:
        print(f"Error obteniendo medicamentos por vencer: {e}")

    # Ingresos recientes (última semana)
    ingresos_recientes = []
    try:
        ingresos_recientes = Medicamento.obtener_ingresos_recientes()
    except Exception as e:
        print(f"Error obteniendo ingresos recientes: {e}")

    # Entregas recientes
    entregas_recientes = []
    try:
        entregas_recientes = DetalleMedicamento.listar_entregas()[:5]  # Últimas 5 entregas
        # Parsear fechas de string a datetime para el template
        for entrega in entregas_recientes:
            if 'fecha_entrega' in entrega and isinstance(entrega['fecha_entrega'], str):
                try:
                    entrega['fecha_entrega'] = datetime.datetime.strptime(entrega['fecha_entrega'], '%Y-%m-%d')
                except ValueError:
                    pass  # Mantener como string si no se puede parsear
    except Exception as e:
        print(f"Error obteniendo entregas recientes: {e}")

    # Inventario completo
    inventario = []
    try:
        inventario = Medicamento.listar_con_detalles()
        # Las fechas ya vienen en formato '%d/%m/%Y' del modelo, no necesitamos parsear
    except Exception as e:
        print(f"Error obteniendo inventario: {e}")

    # Medicamentos vencidos
    medicamentos_vencidos = []
    try:
        medicamentos_vencidos = Medicamento.obtener_vencidos()
        # Las fechas ya vienen en formato '%d/%m/%Y' del modelo, no necesitamos parsear
    except Exception as e:
        print(f"Error obteniendo medicamentos vencidos: {e}")

    # Medicamentos con stock bajo
    medicamentos_stock_bajo = []
    try:
        medicamentos_stock_bajo = Medicamento.obtener_stock_bajo()
        # Las fechas ya vienen en formato '%d/%m/%Y' del modelo, no necesitamos parsear
    except Exception as e:
        print(f"Error obteniendo medicamentos con stock bajo: {e}")

    # Dummy data for testing if methods return empty
    if not medicamentos_recientes:
        medicamentos_recientes = [
            {'nombre': 'Paracetamol', 'stock': 100, 'cantidad': 100},
            {'nombre': 'Ibuprofeno', 'stock': 50, 'cantidad': 50}
        ]
    if not ingresos_recientes:
        ingresos_recientes = [
            {'nombre': 'Paracetamol', 'descripcion': 'Analgésico', 'cantidad': 100, 'fecha_vencimiento': '01/01/2026', 'fecha_ingreso': '01/11/2025'},
            {'nombre': 'Ibuprofeno', 'descripcion': 'Antiinflamatorio', 'cantidad': 50, 'fecha_vencimiento': '01/01/2026', 'fecha_ingreso': '01/11/2025'}
        ]

    # Determinar subsistema desde query params
    subsistema = request.args.get('subsistema')

    return render_template('panel_farmacia.html',
                         subsistema=subsistema,
                         stats=stats,
                         medicamentos_recientes=medicamentos_recientes,
                         medicamentos_por_vencer=medicamentos_por_vencer,
                         ingresos_recientes=ingresos_recientes,
                         entregas_recientes=entregas_recientes,
                         inventario=inventario,
                         medicamentos_vencidos=medicamentos_vencidos,
                         medicamentos_stock_bajo=medicamentos_stock_bajo,
                         datetime=datetime)

@farmacia_bp.route('/gestionar-medicamentos')
def gestionar_medicamentos():
    if 'id_rol' not in session or session['id_rol'] not in [1, 4]:
        return redirect(url_for('usuarios.login'))
    return render_template('gestionarMedicamentos.html')

@farmacia_bp.route('/gestionar-entrega-medicamentos')
def gestionar_entrega_medicamentos():
    if 'id_rol' not in session or session['id_rol'] not in [1, 4]:
        return redirect(url_for('usuarios.login'))
    return render_template('gestionarEntregaMedicamentos.html')

@farmacia_bp.route('/gestionar-recepcion-medicamentos')
def gestionar_recepcion_medicamentos():
    if 'id_rol' not in session or session['id_rol'] not in [1, 4]:
        return redirect(url_for('usuarios.login'))
    return render_template('gestionarRecepcionMedicamentos.html')

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
        print(f"DEBUG API: Datos recibidos: {datos}")

        # Obtener id_empleado de la sesión
        id_empleado = session.get('id_empleado')
        if not id_empleado:
            return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401

        # Mapear las claves del frontend a las esperadas
        id_paciente = datos.get('id_paciente_entrega')
        id_medicamento = datos.get('id_medicamento_entrega')
        cantidad = datos.get('cantidad_entrega')

        # Validar que todos los datos estén presentes y no sean 'undefined'
        if not id_paciente or id_paciente == 'undefined' or not id_medicamento or id_medicamento == 'undefined' or not cantidad:
            return jsonify({'success': False, 'message': 'Debe seleccionar un paciente y un medicamento válidos'}), 400

        try:
            cantidad = int(cantidad)
        except ValueError:
            return jsonify({'success': False, 'message': 'Cantidad debe ser un número'}), 400

        resultado = DetalleMedicamento.registrar_entrega(
            id_empleado,
            id_paciente,
            id_medicamento,
            cantidad
        )
        print(f"DEBUG API: Resultado del modelo: {resultado}")
        if 'error' in resultado:
            return jsonify({'success': False, 'message': resultado['error']}), 400
        return jsonify({'success': True, 'message': 'Entrega registrada exitosamente', 'data': resultado}), 201
    except Exception as e:
        print(f"DEBUG API: Error en API: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

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

# API Endpoint para registrar ingreso de medicamentos (usado por el formulario)
@farmacia_bp.route('/api/ingreso', methods=['POST'])
def api_registrar_ingreso():
    try:
        datos = request.json
        resultado = Medicamento.crear(
            datos['nombre_medicamento'],
            datos['descripcion'] or '',
            int(datos['stock']),
            datos['fecha_vencimiento']
        )
        if 'error' in resultado:
            return jsonify({'success': False, 'message': resultado['error']}), 400
        return jsonify({'success': True, 'message': 'Ingreso registrado exitosamente', 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API Endpoint para obtener medicamentos disponibles para entrega
@farmacia_bp.route('/api/medicamentos/disponibles', methods=['GET'])
def api_medicamentos_disponibles():
    try:
        medicamentos = Medicamento.listar()
        # Filtrar solo medicamentos con stock > 0
        disponibles = [med for med in medicamentos if med.get('stock', 0) > 0]
        return jsonify(disponibles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoint para buscar pacientes (usado por el formulario de entrega)
@farmacia_bp.route('/api/pacientes/entrega', methods=['GET'])
def api_buscar_pacientes_entrega():
    try:
        busqueda = request.args.get('busqueda', '')
        if len(busqueda) < 2:
            return jsonify([])
        resultados = Paciente.buscar(busqueda)
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoint para buscar medicamentos (usado por el formulario de entrega)
@farmacia_bp.route('/api/medicamentos/entrega', methods=['GET'])
def api_buscar_medicamentos_entrega():
    try:
        busqueda = request.args.get('busqueda', '')
        if len(busqueda) < 2:
            return jsonify([])
        resultados = Medicamento.buscar(busqueda)
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoint para retirar medicamentos vencidos
@farmacia_bp.route('/api/medicamento/<int:id>/retirar', methods=['POST'])
def api_retirar_medicamento(id):
    try:
        resultado = Medicamento.retirar(id)
        if 'error' in resultado:
            return jsonify({'success': False, 'message': resultado['error']}), 400
        return jsonify({'success': True, 'message': resultado['message']})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
