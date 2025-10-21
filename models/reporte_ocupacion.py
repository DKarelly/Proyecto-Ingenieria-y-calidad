# Modelo ReporteOcupacion - Reportes de ocupación de recursos
from datetime import datetime, timedelta
import random

class ReporteOcupacion:
    def __init__(self, id_reporte_ocup, id_recurso, tipo_recurso, periodo, 
                 porcentaje, disponibilidad, fecha_generacion):
        self.id_reporte_ocup = id_reporte_ocup
        self.id_recurso = id_recurso
        self.tipo_recurso = tipo_recurso
        self.periodo = periodo
        self.porcentaje = porcentaje
        self.disponibilidad = disponibilidad
        self.fecha_generacion = fecha_generacion

    @staticmethod
    def generar_reporte_ocupacion(tipo_recurso_id=None):
        """Genera reporte de ocupación de recursos"""
        from models.recurso import Recurso
        
        if tipo_recurso_id:
            recursos = Recurso.buscar_por_tipo(tipo_recurso_id)
        else:
            recursos = Recurso.listar_recursos()
        
        reportes = []
        for recurso in recursos:
            # Generar datos de ocupación simulados
            porcentaje_ocupacion = random.randint(40, 95)
            disponibilidad = 100 - porcentaje_ocupacion
            
            reportes.append({
                'idReporteOcup': recurso['idRecurso'],
                'idRecurso': recurso['idRecurso'],
                'nombreRecurso': recurso['nombreRecurso'],
                'tipoRecurso': recurso['tipoRecurso'],
                'descripcion': recurso['descripcion'],
                'estado': recurso['estado'],
                'periodo': '30 días',
                'porcentajeOcupacion': f'{porcentaje_ocupacion}%',
                'disponibilidad': f'{disponibilidad}%',
                'horasUso': random.randint(100, 600),
                'horasDisponibles': 720,  # 30 días * 24 horas
                'fechaGeneracion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return reportes

    @staticmethod
    def buscar_reporte_ocupacion(id_recurso):
        """Busca reporte de ocupación de un recurso específico"""
        reportes = ReporteOcupacion.generar_reporte_ocupacion()
        return next((r for r in reportes if r['idRecurso'] == id_recurso), None)

    @staticmethod
    def listar_por_tipo(tipo_recurso):
        """Lista reportes de ocupación por tipo de recurso"""
        reportes = ReporteOcupacion.generar_reporte_ocupacion()
        if tipo_recurso and tipo_recurso != 'Todos':
            return [r for r in reportes if r['tipoRecurso'] == tipo_recurso]
        return reportes
