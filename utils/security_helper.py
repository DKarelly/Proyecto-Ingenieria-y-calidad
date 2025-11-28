"""
Helper para seguridad y rate limiting de intentos de login
"""
from datetime import datetime, timedelta
from flask import request
from bd import obtener_conexion

class SecurityHelper:
    """
    Clase para gestionar seguridad de login:
    - Rate limiting (máximo 5 intentos)
    - Bloqueo temporal después de intentos fallidos
    - Registro de intentos fallidos
    """
    
    MAX_INTENTOS = 5
    TIEMPO_BLOQUEO_MINUTOS = 15
    TIEMPO_VENTANA_MINUTOS = 15  # Ventana de tiempo para contar intentos
    
    @staticmethod
    def obtener_ip_cliente():
        """Obtiene la IP real del cliente, considerando proxies"""
        try:
            if request:
                # Verificar si viene de un proxy
                if request.headers.get('X-Forwarded-For'):
                    return request.headers.get('X-Forwarded-For').split(',')[0].strip()
                elif request.headers.get('X-Real-IP'):
                    return request.headers.get('X-Real-IP')
                else:
                    return request.remote_addr
            return '0.0.0.0'
        except:
            return '0.0.0.0'
    
    @staticmethod
    def registrar_intento_fallido(correo, ip_address, razon='Credenciales incorrectas'):
        """
        Registra un intento fallido de login
        
        Args:
            correo (str): Correo del usuario que intentó iniciar sesión
            ip_address (str): IP del cliente
            razon (str): Razón del fallo (siempre genérico para no revelar información)
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    INSERT INTO intentos_login_fallidos 
                    (correo, ip_address, razon, fecha_intento)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (correo, ip_address, razon, datetime.now()))
                conexion.commit()
        except Exception as e:
            # Si la tabla no existe, crearla
            if 'Table' in str(e) and "doesn't exist" in str(e):
                SecurityHelper._crear_tabla_intentos()
                # Reintentar inserción
                with conexion.cursor() as cursor:
                    sql = """
                        INSERT INTO intentos_login_fallidos 
                        (correo, ip_address, razon, fecha_intento)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (correo, ip_address, razon, datetime.now()))
                    conexion.commit()
        finally:
            conexion.close()
    
    @staticmethod
    def verificar_bloqueo(ip_address=None):
        """
        Verifica si una IP está bloqueada por exceso de intentos
        
        NOTA: El bloqueo solo se aplica por IP, no por correo.
        Esto permite que usuarios legítimos puedan intentar múltiples veces
        si olvidan su contraseña, mientras previene ataques de fuerza bruta.
        
        Args:
            ip_address (str, optional): IP a verificar
            
        Returns:
            dict: {
                'bloqueado': bool,
                'intentos_restantes': int,
                'tiempo_restante_minutos': int,
                'mensaje': str
            }
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Si no hay IP, no hay bloqueo
                if not ip_address:
                    return {
                        'bloqueado': False,
                        'intentos_restantes': SecurityHelper.MAX_INTENTOS,
                        'tiempo_restante_minutos': 0,
                        'mensaje': ''
                    }
                
                # Calcular tiempo límite (últimos 15 minutos)
                tiempo_limite = datetime.now() - timedelta(minutes=SecurityHelper.TIEMPO_VENTANA_MINUTOS)
                
                # Contar intentos por IP en la ventana de tiempo
                sql = """
                    SELECT COUNT(*) as total_intentos,
                           MAX(fecha_intento) as ultimo_intento
                    FROM intentos_login_fallidos
                    WHERE ip_address = %s
                    AND fecha_intento >= %s
                """
                cursor.execute(sql, (ip_address, tiempo_limite))
                
                resultado = cursor.fetchone()
                
                total_intentos = resultado['total_intentos'] if resultado else 0
                ultimo_intento = resultado['ultimo_intento'] if resultado else None
                
                # Verificar si está bloqueado
                if total_intentos >= SecurityHelper.MAX_INTENTOS:
                    if ultimo_intento:
                        # Calcular tiempo restante de bloqueo
                        tiempo_bloqueo = ultimo_intento + timedelta(minutes=SecurityHelper.TIEMPO_BLOQUEO_MINUTOS)
                        tiempo_restante = tiempo_bloqueo - datetime.now()
                        
                        if tiempo_restante.total_seconds() > 0:
                            minutos_restantes = int(tiempo_restante.total_seconds() / 60) + 1
                            return {
                                'bloqueado': True,
                                'intentos_restantes': 0,
                                'tiempo_restante_minutos': minutos_restantes,
                                'mensaje': f'Demasiados intentos fallidos desde esta dirección. Por favor, intente nuevamente en {minutos_restantes} minutos.'
                            }
                    else:
                        return {
                            'bloqueado': True,
                            'intentos_restantes': 0,
                            'tiempo_restante_minutos': SecurityHelper.TIEMPO_BLOQUEO_MINUTOS,
                            'mensaje': f'Demasiados intentos fallidos desde esta dirección. Por favor, intente nuevamente en {SecurityHelper.TIEMPO_BLOQUEO_MINUTOS} minutos.'
                        }
                
                # No está bloqueado
                intentos_restantes = max(0, SecurityHelper.MAX_INTENTOS - total_intentos)
                return {
                    'bloqueado': False,
                    'intentos_restantes': intentos_restantes,
                    'tiempo_restante_minutos': 0,
                    'mensaje': ''
                }
                
        except Exception as e:
            # Si la tabla no existe, crearla y retornar que no está bloqueado
            if 'Table' in str(e) and "doesn't exist" in str(e):
                SecurityHelper._crear_tabla_intentos()
                return {
                    'bloqueado': False,
                    'intentos_restantes': SecurityHelper.MAX_INTENTOS,
                    'tiempo_restante_minutos': 0,
                    'mensaje': ''
                }
            # En caso de otro error, permitir el intento (fail-open)
            print(f"[ERROR SecurityHelper] Error al verificar bloqueo: {e}")
            return {
                'bloqueado': False,
                'intentos_restantes': SecurityHelper.MAX_INTENTOS,
                'tiempo_restante_minutos': 0,
                'mensaje': ''
            }
        finally:
            conexion.close()
    
    @staticmethod
    def limpiar_intentos_antiguos():
        """
        Limpia intentos fallidos antiguos (más de 1 hora)
        Para mantener la base de datos limpia
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                tiempo_limite = datetime.now() - timedelta(hours=1)
                sql = """
                    DELETE FROM intentos_login_fallidos
                    WHERE fecha_intento < %s
                """
                cursor.execute(sql, (tiempo_limite,))
                conexion.commit()
        except Exception as e:
            # Si la tabla no existe, no hacer nada
            if 'Table' in str(e) and "doesn't exist" in str(e):
                SecurityHelper._crear_tabla_intentos()
        finally:
            conexion.close()
    
    @staticmethod
    def _crear_tabla_intentos():
        """
        Crea la tabla de intentos fallidos si no existe
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    CREATE TABLE IF NOT EXISTS intentos_login_fallidos (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        correo VARCHAR(255) NOT NULL,
                        ip_address VARCHAR(45) NOT NULL,
                        razon VARCHAR(255) DEFAULT 'Credenciales incorrectas',
                        fecha_intento DATETIME NOT NULL,
                        INDEX idx_correo (correo),
                        INDEX idx_ip (ip_address),
                        INDEX idx_fecha (fecha_intento)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
                cursor.execute(sql)
                conexion.commit()
        except Exception as e:
            print(f"[ERROR SecurityHelper] Error al crear tabla: {e}")
        finally:
            conexion.close()
    
    @staticmethod
    def limpiar_intentos_exitoso(ip_address):
        """
        Limpia los intentos fallidos de una IP cuando un login es exitoso
        Esto permite que la IP pueda intentar nuevamente si había sido bloqueada
        
        NOTA: Solo limpia por IP, no por correo, para mantener auditoría
        """
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    DELETE FROM intentos_login_fallidos
                    WHERE ip_address = %s
                """
                cursor.execute(sql, (ip_address,))
                conexion.commit()
        except Exception as e:
            # Si la tabla no existe, no hacer nada
            pass
        finally:
            conexion.close()

