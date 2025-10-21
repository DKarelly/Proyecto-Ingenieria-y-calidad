# Modelo Recurso - Gestión de recursos médicos y equipamiento
from datetime import datetime

class Recurso:
    def __init__(self, id_recurso, id_tipo_recurso, descripcion, estado, nombre_recurso):
        self.id_recurso = id_recurso
        self.id_tipo_recurso = id_tipo_recurso
        self.descripcion = descripcion
        self.estado = estado
        self.nombre_recurso = nombre_recurso

    @staticmethod
    def listar_recursos():
        """Retorna todos los recursos del sistema"""
        # TODO: Implementar conexión a base de datos
        recursos = []
        
        # Consultorios
        for i in range(1, 6):
            recursos.append({
                'idRecurso': i,
                'idTipoRecurso': 1,
                'nombreRecurso': f'Consultorio {i}',
                'descripcion': f'Sala de consulta médica número {i}',
                'estado': 'Disponible' if i % 2 == 0 else 'Ocupado',
                'tipoRecurso': 'Consultorio'
            })
        
        # Equipos Médicos
        equipos = ['Ecógrafo', 'Electrocardiografo', 'Tensiómetro', 'Desfibrilador', 'Monitor de Signos']
        for i, equipo in enumerate(equipos, start=6):
            recursos.append({
                'idRecurso': i,
                'idTipoRecurso': 2,
                'nombreRecurso': equipo,
                'descripcion': f'Equipo médico {equipo}',
                'estado': 'Disponible' if i % 3 == 0 else 'Ocupado',
                'tipoRecurso': 'Equipo Médico'
            })
        
        # Laboratorios
        for i in range(11, 14):
            recursos.append({
                'idRecurso': i,
                'idTipoRecurso': 3,
                'nombreRecurso': f'Laboratorio {i-10}',
                'descripcion': f'Sala de análisis clínicos {i-10}',
                'estado': 'Disponible' if i % 2 == 0 else 'Mantenimiento',
                'tipoRecurso': 'Laboratorio'
            })
        
        # Salas de Rayos X
        for i in range(14, 17):
            recursos.append({
                'idRecurso': i,
                'idTipoRecurso': 4,
                'nombreRecurso': f'Sala de Rayos X {i-13}',
                'descripcion': f'Sala de radiología {i-13}',
                'estado': 'Disponible' if i % 2 == 0 else 'Ocupado',
                'tipoRecurso': 'Rayos X'
            })
        
        # Ambulancias
        for i in range(17, 20):
            recursos.append({
                'idRecurso': i,
                'idTipoRecurso': 5,
                'nombreRecurso': f'Ambulancia {i-16}',
                'descripcion': f'Vehículo de emergencia {i-16}',
                'estado': 'Disponible' if i % 2 == 0 else 'En Servicio',
                'tipoRecurso': 'Ambulancia'
            })
        
        return recursos

    @staticmethod
    def buscar_recurso(id_recurso):
        """Busca un recurso por ID"""
        recursos = Recurso.listar_recursos()
        return next((r for r in recursos if r['idRecurso'] == id_recurso), None)

    @staticmethod
    def buscar_por_tipo(id_tipo_recurso):
        """Filtra recursos por tipo"""
        recursos = Recurso.listar_recursos()
        if id_tipo_recurso:
            return [r for r in recursos if r['idTipoRecurso'] == int(id_tipo_recurso)]
        return recursos

    @staticmethod
    def buscar_por_nombre(nombre):
        """Busca recursos por nombre"""
        recursos = Recurso.listar_recursos()
        if nombre:
            return [r for r in recursos if nombre.lower() in r['nombreRecurso'].lower()]
        return recursos
