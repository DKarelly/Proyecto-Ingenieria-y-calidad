# Modelo Categoría - Clasificación de reportes
from datetime import datetime

class Categoria:
    def __init__(self, id_categoria, nombre_categoria, descripcion, estado=True):
        self.id_categoria = id_categoria
        self.nombre_categoria = nombre_categoria
        self.descripcion = descripcion
        self.estado = estado

    @staticmethod
    def listar_categorias():
        """Retorna lista de categorías disponibles"""
        # TODO: Implementar conexión a base de datos
        return [
            {
                'idCategoria': 1,
                'nombreCategoria': 'Citas Médicas',
                'descripcion': 'Reportes relacionados con citas programadas, canceladas y asistidas',
                'estado': True
            },
            {
                'idCategoria': 2,
                'nombreCategoria': 'Usuarios',
                'descripcion': 'Reportes de actividad y gestión de usuarios del sistema',
                'estado': True
            },
            {
                'idCategoria': 3,
                'nombreCategoria': 'Servicios',
                'descripcion': 'Reportes de servicios médicos ofrecidos (consultas, laboratorio, rayos X)',
                'estado': True
            },
            {
                'idCategoria': 4,
                'nombreCategoria': 'Recursos',
                'descripcion': 'Reportes de ocupación y disponibilidad de recursos médicos',
                'estado': True
            },
            {
                'idCategoria': 5,
                'nombreCategoria': 'Financiero',
                'descripcion': 'Reportes financieros y de facturación',
                'estado': True
            }
        ]

    @staticmethod
    def buscar_categoria(id_categoria):
        """Busca una categoría por ID"""
        categorias = Categoria.listar_categorias()
        return next((c for c in categorias if c['idCategoria'] == id_categoria), None)

    @staticmethod
    def listar_por_estado(estado=True):
        """Lista categorías activas o inactivas"""
        categorias = Categoria.listar_categorias()
        return [c for c in categorias if c['estado'] == estado]
