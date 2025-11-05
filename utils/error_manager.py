"""
Módulo centralizado para gestión de mensajes de error y validaciones
Proporciona mensajes claros, específicos y orientativos a los usuarios
"""
import re
from datetime import datetime

class ErrorManager:
    """Gestor centralizado de mensajes de error"""
    
    # Códigos de error para soporte técnico
    CODIGO_ERRORES = {
        'EMAIL_INVALIDO': 'ERR-001',
        'CONTRASENA_DEBIL': 'ERR-002',
        'TELEFONO_INVALIDO': 'ERR-003',
        'CAMPO_REQUERIDO': 'ERR-004',
        'FECHA_INVALIDA': 'ERR-005',
        'RANGO_FECHA_INVALIDO': 'ERR-006',
        'HORA_INVALIDA': 'ERR-007',
        'DUPLICADO': 'ERR-008',
        'NO_ENCONTRADO': 'ERR-009',
        'PERMISOS_INSUFICIENTES': 'ERR-010',
        'SESION_EXPIRADA': 'ERR-011',
        'CONEXION_BD': 'ERR-012',
        'ARCHIVO_INVALIDO': 'ERR-013',
        'LIMITE_EXCEDIDO': 'ERR-014',
        'FORMATO_INVALIDO': 'ERR-015'
    }
    
    @staticmethod
    def crear_mensaje(que_paso, por_que, como_solucionarlo, codigo_error=None, tipo='error'):
        """
        Crea un mensaje estructurado siguiendo el formato:
        "Qué pasó + Por qué + Cómo solucionarlo"
        
        Args:
            que_paso (str): Descripción de qué ocurrió
            por_que (str): Razón del error
            como_solucionarlo (str): Pasos para solucionar
            codigo_error (str): Código de error para soporte
            tipo (str): Tipo de mensaje (error, advertencia, exito, info)
            
        Returns:
            dict: Mensaje estructurado
        """
        mensaje = {
            'tipo': tipo,
            'que_paso': que_paso,
            'por_que': por_que,
            'solucion': como_solucionarlo,
            'codigo': codigo_error,
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear mensaje completo legible
        mensaje['texto_completo'] = f"{que_paso}. {por_que}. {como_solucionarlo}"
        
        if codigo_error:
            mensaje['texto_completo'] += f" (Código: {codigo_error})"
        
        return mensaje
    
    @staticmethod
    def validar_email(email):
        """
        Valida formato de correo electrónico
        
        Returns:
            dict: Resultado de validación con mensaje de error si aplica
        """
        if not email or email.strip() == '':
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='El correo electrónico es obligatorio',
                    por_que='Este campo no puede estar vacío',
                    como_solucionarlo='Por favor ingrese su correo electrónico',
                    codigo_error=ErrorManager.CODIGO_ERRORES['CAMPO_REQUERIDO']
                )
            }
        
        # Patrón de validación de email
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(patron_email, email):
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='El formato del correo electrónico no es válido',
                    por_que='Debe incluir un @ y un dominio válido',
                    como_solucionarlo='Ejemplo de formato correcto: usuario@dominio.com',
                    codigo_error=ErrorManager.CODIGO_ERRORES['EMAIL_INVALIDO']
                )
            }
        
        return {'valido': True}
    
    @staticmethod
    def validar_contrasena(contrasena):
        """
        Valida fortaleza de contraseña
        
        Returns:
            dict: Resultado de validación con mensaje de error si aplica
        """
        if not contrasena:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='La contraseña es obligatoria',
                    por_que='Este campo no puede estar vacío',
                    como_solucionarlo='Por favor ingrese una contraseña segura',
                    codigo_error=ErrorManager.CODIGO_ERRORES['CAMPO_REQUERIDO']
                )
            }
        
        if len(contrasena) < 8:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='La contraseña es demasiado corta',
                    por_que='Debe tener al menos 8 caracteres para mayor seguridad',
                    como_solucionarlo='Ingrese una contraseña de 8 o más caracteres',
                    codigo_error=ErrorManager.CODIGO_ERRORES['CONTRASENA_DEBIL']
                )
            }
        
        # Verificar complejidad mínima
        tiene_mayuscula = any(c.isupper() for c in contrasena)
        tiene_minuscula = any(c.islower() for c in contrasena)
        tiene_numero = any(c.isdigit() for c in contrasena)
        
        if not (tiene_mayuscula and tiene_minuscula and tiene_numero):
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='La contraseña no cumple los requisitos de seguridad',
                    por_que='Debe contener mayúsculas, minúsculas y números',
                    como_solucionarlo='Ejemplo: MiContraseña123',
                    codigo_error=ErrorManager.CODIGO_ERRORES['CONTRASENA_DEBIL']
                )
            }
        
        return {'valido': True}
    
    @staticmethod
    def validar_telefono(telefono):
        """
        Valida formato de número telefónico
        
        Returns:
            dict: Resultado de validación con mensaje de error si aplica
        """
        if not telefono:
            return {'valido': True}  # Telefono es opcional
        
        # Limpiar caracteres no numéricos
        telefono_limpio = re.sub(r'\D', '', telefono)
        
        if len(telefono_limpio) < 9 or len(telefono_limpio) > 15:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='El número de teléfono no es válido',
                    por_que='Debe tener entre 9 y 15 dígitos',
                    como_solucionarlo='Ingrese un número de teléfono válido (ej: 987654321 o +51987654321)',
                    codigo_error=ErrorManager.CODIGO_ERRORES['TELEFONO_INVALIDO']
                )
            }
        
        return {'valido': True}
    
    @staticmethod
    def validar_fecha(fecha_str, formato='%Y-%m-%d'):
        """
        Valida formato de fecha
        
        Returns:
            dict: Resultado de validación con mensaje de error si aplica
        """
        if not fecha_str:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='La fecha es obligatoria',
                    por_que='Este campo no puede estar vacío',
                    como_solucionarlo='Por favor seleccione una fecha',
                    codigo_error=ErrorManager.CODIGO_ERRORES['CAMPO_REQUERIDO']
                )
            }
        
        try:
            fecha = datetime.strptime(fecha_str, formato)
            return {'valido': True, 'fecha': fecha}
        except ValueError:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='El formato de fecha no es válido',
                    por_que='La fecha ingresada no coincide con el formato esperado',
                    como_solucionarlo='Use el formato AAAA-MM-DD (ejemplo: 2025-01-15)',
                    codigo_error=ErrorManager.CODIGO_ERRORES['FECHA_INVALIDA']
                )
            }
    
    @staticmethod
    def validar_rango_fechas(fecha_inicio, fecha_fin):
        """
        Valida que un rango de fechas sea coherente
        
        Returns:
            dict: Resultado de validación con mensaje de error si aplica
        """
        val_inicio = ErrorManager.validar_fecha(fecha_inicio)
        if not val_inicio['valido']:
            return val_inicio
        
        val_fin = ErrorManager.validar_fecha(fecha_fin)
        if not val_fin['valido']:
            return val_fin
        
        if val_inicio['fecha'] > val_fin['fecha']:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='El rango de fechas no es válido',
                    por_que='La fecha de inicio es posterior a la fecha de fin',
                    como_solucionarlo='Asegúrese de que la fecha de inicio sea anterior a la fecha de fin',
                    codigo_error=ErrorManager.CODIGO_ERRORES['RANGO_FECHA_INVALIDO']
                )
            }
        
        return {'valido': True}
    
    @staticmethod
    def validar_archivo(archivo, extensiones_permitidas, tamano_max_mb=10):
        """
        Valida un archivo subido
        
        Args:
            archivo: Archivo de Flask request.files
            extensiones_permitidas (list): Lista de extensiones permitidas (ej: ['pdf', 'jpg', 'png'])
            tamano_max_mb (int): Tamaño máximo en MB
            
        Returns:
            dict: Resultado de validación con mensaje de error si aplica
        """
        if not archivo or archivo.filename == '':
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='No se ha seleccionado ningún archivo',
                    por_que='Debe adjuntar un archivo',
                    como_solucionarlo='Haga clic en "Seleccionar archivo" y elija un archivo',
                    codigo_error=ErrorManager.CODIGO_ERRORES['CAMPO_REQUERIDO']
                )
            }
        
        # Validar extensión
        extension = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
        if extension not in extensiones_permitidas:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='El tipo de archivo no está permitido',
                    por_que=f'Solo se aceptan archivos: {", ".join(extensiones_permitidas)}',
                    como_solucionarlo=f'Por favor seleccione un archivo con extensión válida',
                    codigo_error=ErrorManager.CODIGO_ERRORES['ARCHIVO_INVALIDO']
                )
            }
        
        # Validar tamaño (aproximado desde el objeto de Flask)
        archivo.seek(0, 2)  # Ir al final del archivo
        tamano_bytes = archivo.tell()
        archivo.seek(0)  # Volver al inicio
        
        tamano_mb = tamano_bytes / (1024 * 1024)
        if tamano_mb > tamano_max_mb:
            return {
                'valido': False,
                'mensaje': ErrorManager.crear_mensaje(
                    que_paso='El archivo es demasiado grande',
                    por_que=f'El tamaño máximo permitido es {tamano_max_mb}MB',
                    como_solucionarlo='Por favor seleccione un archivo más pequeño',
                    codigo_error=ErrorManager.CODIGO_ERRORES['LIMITE_EXCEDIDO']
                )
            }
        
        return {'valido': True}
    
    @staticmethod
    def mensaje_exito(accion, detalle=''):
        """Crea un mensaje de éxito"""
        return {
            'tipo': 'exito',
            'titulo': '¡Operación exitosa!',
            'mensaje': f'{accion} {detalle}',
            'icono': 'check-circle'
        }
    
    @staticmethod
    def mensaje_advertencia(titulo, mensaje, sugerencia=''):
        """Crea un mensaje de advertencia"""
        return {
            'tipo': 'advertencia',
            'titulo': titulo,
            'mensaje': mensaje,
            'sugerencia': sugerencia,
            'icono': 'exclamation-triangle'
        }
    
    @staticmethod
    def mensaje_info(titulo, mensaje):
        """Crea un mensaje informativo"""
        return {
            'tipo': 'info',
            'titulo': titulo,
            'mensaje': mensaje,
            'icono': 'info-circle'
        }

# Instancia global del gestor de errores
error_manager = ErrorManager()
