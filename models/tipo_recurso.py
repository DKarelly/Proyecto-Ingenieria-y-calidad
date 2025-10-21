# Modelo TipoRecurso - Clasificación de recursos
from datetime import datetime

class TipoRecurso:
    def __init__(self, id_tipo_recurso, descripcion, nombre_tipo):
        self.id_tipo_recurso = id_tipo_recurso
        self.descripcion = descripcion
        self.nombre_tipo = nombre_tipo

    @staticmethod
    def listar_tipos_recurso():
        """Retorna todos los tipos de recursos"""
        # TODO: Implementar conexión a base de datos
        return [
            {
                'idTipoRecurso': 1,
                'nombreTipo': 'Consultorio',
                'descripcion': 'Salas de consulta médica general y especializada'
            },
            {
                'idTipoRecurso': 2,
                'nombreTipo': 'Equipo Médico',
                'descripcion': 'Equipos e instrumentos médicos especializados'
            },
            {
                'idTipoRecurso': 3,
                'nombreTipo': 'Laboratorio',
                'descripcion': 'Instalaciones para análisis clínicos y pruebas de laboratorio'
            },
            {
                'idTipoRecurso': 4,
                'nombreTipo': 'Rayos X',
                'descripcion': 'Salas de radiología y equipos de diagnóstico por imágenes'
            },
            {
                'idTipoRecurso': 5,
                'nombreTipo': 'Ambulancia',
                'descripcion': 'Vehículos de emergencia y transporte médico'
            },
            {
                'idTipoRecurso': 6,
                'nombreTipo': 'Quirófano',
                'descripcion': 'Salas de cirugía y procedimientos quirúrgicos'
            }
        ]

    @staticmethod
    def buscar_tipo(id_tipo_recurso):
        """Busca un tipo de recurso por ID"""
        tipos = TipoRecurso.listar_tipos_recurso()
        return next((t for t in tipos if t['idTipoRecurso'] == id_tipo_recurso), None)
