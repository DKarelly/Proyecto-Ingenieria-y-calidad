import pymysql
import logging
from queue import Queue, Empty
from threading import Lock
from functools import lru_cache
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.WARNING)

# Cache simple para consultas frecuentes (5 minutos)
_query_cache = {}
_cache_timeout = timedelta(minutes=5)

def cache_query(key, data):
    """Guarda resultado en caché"""
    _query_cache[key] = {
        'data': data,
        'timestamp': datetime.now()
    }

def get_cached_query(key):
    """Obtiene resultado del caché si no ha expirado"""
    if key in _query_cache:
        cached = _query_cache[key]
        if datetime.now() - cached['timestamp'] < _cache_timeout:
            return cached['data']
        else:
            del _query_cache[key]
    return None

def clear_cache():
    """Limpia el caché"""
    _query_cache.clear()

# Pool de conexiones simple para mejorar rendimiento
class SimpleConnectionPool:
    """Pool de conexiones simple para PyMySQL"""
    
    def __init__(self, pool_size=10, **db_config):
        self.pool_size = pool_size
        self.db_config = db_config
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa las conexiones en el pool"""
        for _ in range(self.pool_size):
            try:
                conn = pymysql.connect(**self.db_config)
                self.pool.put(conn)
            except Exception as e:
                logging.error(f"Error al crear conexión en pool: {e}")
    
    def get_connection(self):
        """Obtiene una conexión del pool"""
        try:
            # Intentar obtener una conexión existente
            conn = self.pool.get(block=False)
            
            # Verificar si la conexión está activa
            try:
                conn.ping(reconnect=True)
                return conn
            except:
                # Si la conexión está muerta, crear una nueva
                return pymysql.connect(**self.db_config)
                
        except Empty:
            # Si no hay conexiones disponibles, crear una nueva temporal
            return pymysql.connect(**self.db_config)
    
    def return_connection(self, conn):
        """Devuelve una conexión al pool"""
        try:
            if conn and conn.open:
                self.pool.put(conn, block=False)
            else:
                conn.close()
        except:
            try:
                conn.close()
            except:
                pass

# Pool de conexiones global
connection_pool = None

def inicializar_pool():
    """Inicializa el pool de conexiones a la base de datos"""
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = SimpleConnectionPool(
                pool_size=10,  # Número de conexiones en el pool
                host='tramway.proxy.rlwy.net',
                port=37865,
                user='root',
                password='voVwDDOsuNzPptZwHFRJtQViYgiMHCZf',
                db='bd_calidad',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            logging.info("Pool de conexiones inicializado correctamente")
        except Exception as e:
            logging.error(f"Error al inicializar pool de conexiones: {e}")
            connection_pool = None

def obtener_conexion():
    """Obtiene una conexión del pool o crea una nueva si el pool no está disponible"""
    global connection_pool
    
    # Inicializar pool si no existe
    if connection_pool is None:
        inicializar_pool()
    
    try:
        # Intentar obtener conexión del pool
        if connection_pool is not None:
            return connection_pool.get_connection()
    except Exception as e:
        logging.warning(f"Error al obtener conexión del pool: {e}. Creando conexión directa.")
    
    # Fallback: crear conexión directa si el pool falla
    return pymysql.connect(
        host='tramway.proxy.rlwy.net',
        port=37865,
        user='root',
        password='voVwDDOsuNzPptZwHFRJtQViYgiMHCZf',
        db='bd_calidad',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )