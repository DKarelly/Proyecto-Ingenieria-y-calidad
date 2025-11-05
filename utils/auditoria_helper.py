"""
Helper para registro de auditoría del sistema
Adaptado a la estructura real de la tabla AUDITORIA
"""
import json
import logging
from datetime import datetime
from flask import session, request
from bd import obtener_conexion

class AuditoriaHelper:
    """
    Clase para gestionar el registro de auditoría
    
    Estructura de tabla AUDITORIA:
    - id_auditoria: int AI PK
    - id_usuario: int
    - id_empleado: int
    - accion: varchar(100)
    - modulo: varchar(50)
    - tipo_evento: varchar(50)
    - descripcion: text
    - ip_address: varchar(45)
    - fecha_registro: datetime (automático)
    - detalles_json: text (JSON con información adicional)
    """
    
    # Tipos de eventos
    LOGIN = 'Login'
    LOGOUT = 'Logout'
    CREACION = 'Creación'
    MODIFICACION = 'Modificación'
    ELIMINACION = 'Eliminación'
    CONSULTA = 'Consulta'
    INCIDENCIA = 'Incidencia'
    ERROR = 'Error'
    
    @staticmethod
    def _obtener_ip_cliente():
        """Obtiene la IP del cliente"""
        try:
            if request:
                # Verificar si viene de un proxy
                if request.headers.get('X-Forwarded-For'):
                    return request.headers.get('X-Forwarded-For').split(',')[0].strip()
                elif request.headers.get('X-Real-IP'):
                    return request.headers.get('X-Real-IP')
                else:
                    return request.remote_addr
            return 'N/A'
        except:
            return 'N/A'
    
    @staticmethod
    def _formatear_cambios(valores_anteriores, valores_nuevos):
        """Formatea los cambios para la descripción"""
        if not valores_anteriores or not valores_nuevos:
            return ''
        
        cambios = []
        for campo in valores_nuevos:
            valor_anterior = valores_anteriores.get(campo, 'N/A')
            valor_nuevo = valores_nuevos.get(campo, 'N/A')
            
            if valor_anterior != valor_nuevo:
                cambios.append(f"  - {campo}: '{valor_anterior}' → '{valor_nuevo}'")
        
        return '\n'.join(cambios) if cambios else ''
    
    @staticmethod
    def registrar(tipo_evento, modulo, accion, descripcion='', id_usuario=None, 
                  detalles_json=None, exitoso=True):
        """
        Registra una operación en la tabla de auditoría
        
        Estructura de tabla AUDITORIA:
        - id_auditoria: int AI PK
        - id_usuario: int
        - id_empleado: int
        - accion: varchar(100)
        - modulo: varchar(50)
        - tipo_evento: varchar(50)
        - descripcion: text
        - ip_address: varchar(45)
        - fecha_registro: (timestamp automático)
        - detalles_json: text (para valores anteriores/nuevos)
        
        Args:
            tipo_evento (str): Tipo de evento (Login, Creación, Modificación, etc.)
            modulo (str): Módulo del sistema afectado
            accion (str): Descripción breve de la acción (max 100 caracteres)
            descripcion (str): Descripción detallada
            id_usuario (int): ID del usuario que realizó la acción (si aplica)
            detalles_json (dict): Detalles adicionales en formato JSON (valores anteriores/nuevos, etc.)
            exitoso (bool): Si la operación fue exitosa
            
        Returns:
            int: ID del registro de auditoría creado, o None si falló
        """
        try:
            # Obtener ID de usuario de la sesión si no se proporciona
            if id_usuario is None and 'usuario_id' in session:
                id_usuario = session.get('usuario_id')
            
            # Obtener ID de empleado si es un empleado
            id_empleado = None
            if session.get('tipo_usuario') == 'empleado':
                id_empleado = session.get('id_empleado')
            
            # Obtener IP del cliente
            ip_address = AuditoriaHelper._obtener_ip_cliente()
            
            # Preparar descripción completa
            desc_completa = descripcion
            
            # Agregar estado de la operación a la descripción
            if not exitoso:
                desc_completa = f"[FALLIDO] {desc_completa}"
            
            # Limitar longitud de acción a 100 caracteres
            accion_truncada = accion[:100] if len(accion) > 100 else accion
            
            # Convertir detalles a JSON si existen
            detalles_json_str = json.dumps(detalles_json, ensure_ascii=False) if detalles_json else None
            
            # Insertar en base de datos según estructura real
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            sql = """
                INSERT INTO AUDITORIA 
                (id_usuario, id_empleado, accion, modulo, tipo_evento, descripcion, 
                 ip_address, detalles_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                id_usuario,
                id_empleado,
                accion_truncada,
                modulo,
                tipo_evento,
                desc_completa,
                ip_address,
                detalles_json_str
            ))
            
            id_auditoria = cursor.lastrowid
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            logging.info(f"Auditoría registrada: {tipo_evento} - {modulo} - {accion_truncada}")
            
            return id_auditoria
            
        except Exception as e:
            logging.error(f"Error al registrar auditoría: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # ========== MÉTODOS ESPECÍFICOS ==========
    
    @staticmethod
    def registrar_login(id_usuario, tipo_usuario, exitoso=True, razon=''):
        """Registra un intento de inicio de sesión"""
        accion = f"Inicio de sesión {tipo_usuario}"
        descripcion = f"Usuario ID {id_usuario} {'exitoso' if exitoso else 'fallido'}"
        
        if razon:
            descripcion += f" - Razón: {razon}"
        
        detalles = {
            'id_usuario': id_usuario,
            'tipo_usuario': tipo_usuario,
            'navegador': request.user_agent.string if request else None,
            'razon': razon
        }
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.LOGIN,
            modulo='Autenticación',
            accion=accion,
            descripcion=descripcion,
            id_usuario=id_usuario,
            detalles_json=detalles,
            exitoso=exitoso
        )
    
    @staticmethod
    def registrar_logout(id_usuario, tipo_usuario):
        """Registra un cierre de sesión"""
        accion = f"Cierre de sesión {tipo_usuario}"
        descripcion = f"Usuario ID {id_usuario} cerró sesión"
        
        detalles = {
            'id_usuario': id_usuario,
            'tipo_usuario': tipo_usuario
        }
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.LOGOUT,
            modulo='Autenticación',
            accion=accion,
            descripcion=descripcion,
            id_usuario=id_usuario,
            detalles_json=detalles,
            exitoso=True
        )
    
    @staticmethod
    def registrar_creacion(modulo, entidad, id_entidad, valores_nuevos, descripcion=''):
        """Registra la creación de un nuevo registro"""
        accion = f"Creación de {entidad}"
        if not descripcion:
            descripcion = f"Se creó un nuevo registro de {entidad} (ID: {id_entidad})"
        
        detalles = {
            'entidad': entidad,
            'id_entidad': id_entidad,
            'valores_nuevos': valores_nuevos
        }
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.CREACION,
            modulo=modulo,
            accion=accion,
            descripcion=descripcion,
            detalles_json=detalles,
            exitoso=True
        )
    
    @staticmethod
    def registrar_modificacion(modulo, entidad, id_entidad, valores_anteriores, 
                              valores_nuevos, descripcion=''):
        """Registra la modificación de un registro existente"""
        accion = f"Modificación de {entidad}"
        if not descripcion:
            # Crear descripción detallada con los cambios
            cambios_info = AuditoriaHelper._formatear_cambios(valores_anteriores, valores_nuevos)
            descripcion = f"Se modificó el registro de {entidad} (ID: {id_entidad})"
            if cambios_info:
                descripcion += f"\n\nCambios:\n{cambios_info}"
        
        detalles = {
            'entidad': entidad,
            'id_entidad': id_entidad,
            'valores_anteriores': valores_anteriores,
            'valores_nuevos': valores_nuevos
        }
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.MODIFICACION,
            modulo=modulo,
            accion=accion,
            descripcion=descripcion,
            detalles_json=detalles,
            exitoso=True
        )
    
    @staticmethod
    def registrar_eliminacion(modulo, entidad, id_entidad, valores_anteriores, descripcion=''):
        """Registra la eliminación de un registro"""
        accion = f"Eliminación de {entidad}"
        if not descripcion:
            descripcion = f"Se eliminó el registro de {entidad} (ID: {id_entidad})"
        
        detalles = {
            'entidad': entidad,
            'id_entidad': id_entidad,
            'valores_anteriores': valores_anteriores
        }
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.ELIMINACION,
            modulo=modulo,
            accion=accion,
            descripcion=descripcion,
            detalles_json=detalles,
            exitoso=True
        )
    
    @staticmethod
    def registrar_consulta(modulo, entidad, id_entidad=None, descripcion='', 
                          parametros_busqueda=None):
        """Registra una consulta de datos"""
        accion = f"Consulta de {entidad}"
        if not descripcion:
            if id_entidad:
                descripcion = f"Se consultó el registro de {entidad} (ID: {id_entidad})"
            else:
                descripcion = f"Se realizó una consulta de {entidad}"
        
        detalles = {
            'entidad': entidad,
            'id_entidad': id_entidad,
            'parametros_busqueda': parametros_busqueda
        } if (id_entidad or parametros_busqueda) else None
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.CONSULTA,
            modulo=modulo,
            accion=accion,
            descripcion=descripcion,
            detalles_json=detalles,
            exitoso=True
        )
    
    @staticmethod
    def registrar_incidencia(tipo_incidencia, severidad, descripcion, id_entidad=None, 
                            detalles=None):
        """Registra una incidencia del sistema"""
        accion = f"Incidencia: {tipo_incidencia}"
        desc_completa = f"Severidad: {severidad}\n{descripcion}"
        
        detalles_inc = {
            'tipo_incidencia': tipo_incidencia,
            'severidad': severidad,
            'id_entidad': id_entidad
        }
        
        if detalles:
            detalles_inc.update(detalles)
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.INCIDENCIA,
            modulo='Sistema',
            accion=accion,
            descripcion=desc_completa,
            detalles_json=detalles_inc,
            exitoso=False
        )
    
    @staticmethod
    def registrar_error(modulo, accion, error_msg, detalles=None):
        """Registra un error del sistema"""
        accion_completa = f"Error en {accion}"
        descripcion = f"Error: {error_msg}"
        
        detalles_error = {
            'mensaje_error': error_msg,
            'traceback': detalles.get('traceback', '') if detalles else ''
        }
        
        if detalles:
            detalles_error.update(detalles)
        
        return AuditoriaHelper.registrar(
            tipo_evento=AuditoriaHelper.ERROR,
            modulo=modulo,
            accion=accion_completa,
            descripcion=descripcion,
            detalles_json=detalles_error,
            exitoso=False
        )
    
    # ========== MÉTODOS DE CONSULTA ==========
    
    @staticmethod
    def obtener_historial(filtros=None, limite=100, offset=0):
        """
        Obtiene el historial de auditoría con filtros opcionales
        
        Args:
            filtros (dict): Diccionario con filtros opcionales:
                - id_usuario: int
                - id_empleado: int
                - tipo_evento: str
                - modulo: str
                - fecha_desde: datetime
                - fecha_hasta: datetime
            limite (int): Número máximo de registros a devolver
            offset (int): Número de registros a saltar
            
        Returns:
            list: Lista de registros de auditoría
        """
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            sql = "SELECT * FROM AUDITORIA WHERE 1=1"
            params = []
            
            if filtros:
                if 'id_usuario' in filtros:
                    sql += " AND id_usuario = %s"
                    params.append(filtros['id_usuario'])
                
                if 'id_empleado' in filtros:
                    sql += " AND id_empleado = %s"
                    params.append(filtros['id_empleado'])
                
                if 'tipo_evento' in filtros:
                    sql += " AND tipo_evento = %s"
                    params.append(filtros['tipo_evento'])
                
                if 'modulo' in filtros:
                    sql += " AND modulo = %s"
                    params.append(filtros['modulo'])
                
                if 'fecha_desde' in filtros:
                    sql += " AND fecha_registro >= %s"
                    params.append(filtros['fecha_desde'])
                
                if 'fecha_hasta' in filtros:
                    sql += " AND fecha_registro <= %s"
                    params.append(filtros['fecha_hasta'])
            
            sql += " ORDER BY fecha_registro DESC LIMIT %s OFFSET %s"
            params.extend([limite, offset])
            
            cursor.execute(sql, params)
            registros = cursor.fetchall()
            
            cursor.close()
            conexion.close()
            
            return registros
            
        except Exception as e:
            logging.error(f"Error al obtener historial de auditoría: {e}")
            return []
    
    @staticmethod
    def obtener_estadisticas(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de auditoría
        
        Args:
            fecha_desde (datetime): Fecha inicial
            fecha_hasta (datetime): Fecha final
            
        Returns:
            dict: Diccionario con estadísticas
        """
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            sql = """
                SELECT 
                    tipo_evento,
                    modulo,
                    COUNT(*) as total
                FROM AUDITORIA
                WHERE 1=1
            """
            params = []
            
            if fecha_desde:
                sql += " AND fecha_registro >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                sql += " AND fecha_registro <= %s"
                params.append(fecha_hasta)
            
            sql += " GROUP BY tipo_evento, modulo ORDER BY total DESC"
            
            cursor.execute(sql, params)
            resultados = cursor.fetchall()
            
            cursor.close()
            conexion.close()
            
            return {
                'por_tipo_modulo': resultados,
                'total': sum([r[2] for r in resultados])
            }
            
        except Exception as e:
            logging.error(f"Error al obtener estadísticas de auditoría: {e}")
            return {'por_tipo_modulo': [], 'total': 0}
