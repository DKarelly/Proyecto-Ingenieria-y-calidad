from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, send_file
from models.reporte import Reporte, ArchivoReporte
from models.catalogos import Categoria
from werkzeug.utils import secure_filename
import os
from datetime import datetime

reportes_bp = Blueprint('reportes', __name__)

# Configuración de archivos
UPLOAD_FOLDER = 'uploads/reportes'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@reportes_bp.route('/')
def panel():
    """Panel de Reportes"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('panel.html', subsistema='reportes')

@reportes_bp.route('/consultar-por-categoria')
def consultar_por_categoria():
    """Consultar Reportes por Categoría"""
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    if session.get('tipo_usuario') != 'empleado':
        return redirect(url_for('home'))

    return render_template('consultar_por_categoria.html')

# ============================================
# ENDPOINTS API REST
# ============================================

@reportes_bp.route('/api/reportes/categorias', methods=['GET'])
def obtener_categorias():
    """Obtiene todas las categorías para reportes"""
    try:
        categorias = Categoria.obtener_todas()
        return jsonify(categorias)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/buscar', methods=['POST'])
def buscar_reportes():
    """Busca reportes según filtros"""
    try:
        filtros = request.get_json() or {}
        reportes = Reporte.buscar(filtros)
        return jsonify(reportes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/<int:id_reporte>', methods=['GET'])
def obtener_reporte(id_reporte):
    """Obtiene un reporte por su ID con sus archivos"""
    try:
        reporte = Reporte.obtener_por_id(id_reporte)
        if not reporte:
            return jsonify({'error': 'Reporte no encontrado'}), 404

        # Obtener archivos adjuntos
        archivos = ArchivoReporte.obtener_por_reporte(id_reporte)

        # Convertir a diccionario y agregar archivos
        reporte_dict = dict(reporte)
        reporte_dict['archivos'] = archivos

        return jsonify(reporte_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/crear', methods=['POST'])
def crear_reporte():
    """Crea un nuevo reporte"""
    try:
        datos = request.get_json()

        # Validar datos requeridos
        if not datos.get('id_categoria'):
            return jsonify({'error': 'La categoría es requerida'}), 400

        # Obtener ID del empleado de la sesión
        id_empleado = session.get('usuario_id')
        if not id_empleado:
            return jsonify({'error': 'Usuario no autenticado'}), 401

        # Generar código si no se proporcionó
        codigo = datos.get('codigo') or Reporte.generar_codigo()

        # Crear el reporte
        resultado = Reporte.crear(
            codigo=codigo,
            nombre=datos.get('nombre', f"Reporte {datetime.now().strftime('%Y%m%d')}"),
            tipo=datos.get('tipo', 'General'),
            id_categoria=datos['id_categoria'],
            id_empleado=id_empleado,
            descripcion=datos.get('descripcion'),
            id_servicio=datos.get('id_servicio'),
            id_recurso=datos.get('id_recurso'),
            estado=datos.get('estado', 'Completado')
        )

        if 'error' in resultado:
            return jsonify(resultado), 500

        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/<int:id_reporte>/subir-archivo', methods=['POST'])
def subir_archivo(id_reporte):
    """Sube un archivo adjunto a un reporte"""
    try:
        # Verificar que el reporte existe
        reporte = Reporte.obtener_por_id(id_reporte)
        if not reporte:
            return jsonify({'error': 'Reporte no encontrado'}), 404

        # Verificar que se envió un archivo
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400

        archivo = request.files['archivo']

        if archivo.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400

        if not allowed_file(archivo.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400

        # Crear directorio si no existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Generar nombre seguro para el archivo
        filename = secure_filename(archivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_unico = f"{id_reporte}_{timestamp}_{filename}"
        ruta_archivo = os.path.join(UPLOAD_FOLDER, nombre_unico)

        # Guardar el archivo
        archivo.save(ruta_archivo)

        # Obtener información del archivo
        tamano_bytes = os.path.getsize(ruta_archivo)
        tipo_mime = archivo.content_type or 'application/octet-stream'

        # Registrar en la base de datos
        resultado = ArchivoReporte.crear(
            id_reporte=id_reporte,
            nombre_archivo=filename,
            ruta_archivo=ruta_archivo,
            tamano_bytes=tamano_bytes,
            tipo_mime=tipo_mime
        )

        if 'error' in resultado:
            # Eliminar archivo si falla el registro
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            return jsonify(resultado), 500

        return jsonify({
            'success': True,
            'id_archivo': resultado['id_archivo'],
            'nombre_archivo': filename,
            'tamano_bytes': tamano_bytes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/descargar-archivo/<int:id_archivo>', methods=['GET'])
def descargar_archivo(id_archivo):
    """Descarga un archivo adjunto"""
    try:
        archivo = ArchivoReporte.obtener_por_id(id_archivo)
        if not archivo:
            return jsonify({'error': 'Archivo no encontrado'}), 404

        ruta_archivo = archivo['ruta_archivo']
        if not os.path.exists(ruta_archivo):
            return jsonify({'error': 'Archivo físico no encontrado'}), 404

        return send_file(
            ruta_archivo,
            as_attachment=True,
            download_name=archivo['nombre_archivo'],
            mimetype=archivo.get('tipo_archivo', 'application/octet-stream')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/eliminar-archivo/<int:id_archivo>', methods=['DELETE'])
def eliminar_archivo(id_archivo):
    """Elimina un archivo adjunto"""
    try:
        # Obtener información del archivo
        archivo = ArchivoReporte.obtener_por_id(id_archivo)
        if not archivo:
            return jsonify({'error': 'Archivo no encontrado'}), 404

        # Eliminar archivo físico
        ruta_archivo = archivo['ruta_archivo']
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

        # Eliminar registro de la base de datos
        resultado = ArchivoReporte.eliminar(id_archivo)

        if 'error' in resultado:
            return jsonify(resultado), 500

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/<int:id_reporte>/eliminar', methods=['DELETE'])
def eliminar_reporte(id_reporte):
    """Elimina un reporte y sus archivos asociados"""
    try:
        # Obtener archivos del reporte
        archivos = ArchivoReporte.obtener_por_reporte(id_reporte)

        # Eliminar archivos físicos y registros
        for archivo in archivos:
            ruta_archivo = archivo['ruta_archivo']
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            ArchivoReporte.eliminar(archivo['id_archivo'])

        # Eliminar el reporte
        resultado = Reporte.eliminar(id_reporte)

        if 'error' in resultado:
            return jsonify(resultado), 500

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/<int:id_reporte>/descargar', methods=['GET'])
def descargar_reporte(id_reporte):
    """Descarga un reporte en formato PDF o Excel"""
    try:
        formato = request.args.get('formato', 'pdf')

        reporte = Reporte.obtener_por_id(id_reporte)
        if not reporte:
            return jsonify({'error': 'Reporte no encontrado'}), 404

        # Por ahora, retornar un mensaje indicando que se requiere implementación
        return jsonify({
            'message': 'Funcionalidad de exportación en desarrollo',
            'reporte': dict(reporte),
            'formato': formato
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/api/reportes/exportar', methods=['GET'])
def exportar_reportes():
    """Exporta múltiples reportes en formato PDF o Excel"""
    try:
        formato = request.args.get('formato', 'pdf')

        # Obtener filtros de la query string
        filtros = {
            'id_categoria': request.args.get('id_categoria'),
            'tipo': request.args.get('tipo'),
            'fecha_inicio': request.args.get('fecha_inicio'),
            'fecha_fin': request.args.get('fecha_fin')
        }

        # Filtrar valores None
        filtros = {k: v for k, v in filtros.items() if v}

        reportes = Reporte.buscar(filtros)

        # Por ahora, retornar un mensaje indicando que se requiere implementación
        return jsonify({
            'message': 'Funcionalidad de exportación en desarrollo',
            'total_reportes': len(reportes),
            'formato': formato
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500