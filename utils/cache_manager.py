"""
Módulo de gestión de caché para mejorar el rendimiento del sistema
Cachea datos frecuentemente consultados como catálogos y configuraciones
"""
from functools import wraps
from datetime import datetime, timedelta
import logging

# Diccionario simple para almacenar caché en memoria
# Para producción, considere usar Redis o Memcached
_cache_store = {}
_cache_timestamps = {}

# Configuración de tiempos de expiración por tipo de dato
CACHE_EXPIRATION = {
    'catalogos': timedelta(hours=24),      # Catálogos cambian raramente
    'usuarios': timedelta(minutes=15),      # Usuarios pueden cambiar más seguido
    'servicios': timedelta(hours=1),        # Servicios actualizados ocasionalmente
    'horarios': timedelta(minutes=30),      # Horarios actualizados regularmente
    'configuracion': timedelta(hours=12),   # Configuración casi estática
    'default': timedelta(minutes=5)         # Cache por defecto
}

def obtener_cache(key):
    """
    Obtiene un valor del cache si existe y no ha expirado
    
    Args:
        key (str): Clave del cache
        
    Returns:
        El valor cacheado o None si no existe o expiró
    """
    if key not in _cache_store:
        return None
    
    # Verificar si el cache ha expirado
    timestamp = _cache_timestamps.get(key)
    if timestamp and datetime.now() > timestamp:
        # Cache expirado, eliminarlo
        eliminar_cache(key)
        return None
    
    return _cache_store[key]

def guardar_cache(key, value, tipo='default'):
    """
    Guarda un valor en el cache con tiempo de expiración
    
    Args:
        key (str): Clave del cache
        value: Valor a cachear
        tipo (str): Tipo de dato para determinar tiempo de expiración
    """
    expiracion = CACHE_EXPIRATION.get(tipo, CACHE_EXPIRATION['default'])
    _cache_store[key] = value
    _cache_timestamps[key] = datetime.now() + expiracion
    logging.debug(f"Cache guardado: {key} (expira en {expiracion})")

def eliminar_cache(key):
    """
    Elimina un valor específico del cache
    
    Args:
        key (str): Clave del cache a eliminar
    """
    if key in _cache_store:
        del _cache_store[key]
    if key in _cache_timestamps:
        del _cache_timestamps[key]
    logging.debug(f"Cache eliminado: {key}")

def limpiar_cache_tipo(tipo):
    """
    Limpia todos los caches de un tipo específico
    
    Args:
        tipo (str): Tipo de cache a limpiar
    """
    keys_to_delete = [k for k in _cache_store.keys() if k.startswith(f"{tipo}_")]
    for key in keys_to_delete:
        eliminar_cache(key)
    logging.info(f"Cache limpiado para tipo: {tipo}")

def limpiar_todo_cache():
    """Limpia todo el cache"""
    _cache_store.clear()
    _cache_timestamps.clear()
    logging.info("Todo el cache ha sido limpiado")

def cache_resultado(tipo='default', tiempo_expiracion=None):
    """
    Decorador para cachear resultados de funciones
    
    Args:
        tipo (str): Tipo de cache para determinar expiración
        tiempo_expiracion (timedelta): Tiempo custom de expiración (opcional)
        
    Uso:
        @cache_resultado(tipo='catalogos')
        def obtener_especialidades():
            # código que consulta BD
            return resultados
    """
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave única basada en nombre de función y argumentos
            cache_key = f"{tipo}_{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Intentar obtener del cache
            resultado = obtener_cache(cache_key)
            if resultado is not None:
                logging.debug(f"Cache hit: {cache_key}")
                return resultado
            
            # Si no está en cache, ejecutar función
            logging.debug(f"Cache miss: {cache_key}")
            resultado = func(*args, **kwargs)
            
            # Guardar en cache
            if tiempo_expiracion:
                # Guardar con tiempo custom
                _cache_store[cache_key] = resultado
                _cache_timestamps[cache_key] = datetime.now() + tiempo_expiracion
            else:
                guardar_cache(cache_key, resultado, tipo)
            
            return resultado
        return wrapper
    return decorador

def obtener_estadisticas_cache():
    """
    Obtiene estadísticas del cache para monitoreo
    
    Returns:
        dict: Estadísticas del cache
    """
    total_items = len(_cache_store)
    items_por_tipo = {}
    
    for key in _cache_store.keys():
        tipo = key.split('_')[0]
        items_por_tipo[tipo] = items_por_tipo.get(tipo, 0) + 1
    
    return {
        'total_items': total_items,
        'items_por_tipo': items_por_tipo,
        'memoria_mb': sum(len(str(v)) for v in _cache_store.values()) / (1024 * 1024)
    }
