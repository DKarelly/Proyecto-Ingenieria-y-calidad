"""
Suite de pruebas para la aplicación Flask
Incluye pruebas de caja blanca, caja negra e integración
"""

# Configuración de pytest para el módulo de tests
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Versión de las pruebas
__version__ = '1.0.0'

# Metadata de las pruebas
__author__ = 'Equipo de Desarrollo'
__test_suite__ = 'Pruebas de Caja Blanca'