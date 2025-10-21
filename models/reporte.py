# Modelo Reporte - Generación y gestión de reportes estadísticos
from datetime import datetime, timedelta
import random

class Reporte:
    def __init__(self, id_reporte, nombre_reporte, categoria, fecha_generacion, 
                 hora_generacion, id_usuario, ruta_archivo):
        self.id_reporte = id_reporte
        self.nombre_reporte = nombre_reporte
        self.categoria = categoria
        self.fecha_generacion = fecha_generacion
        self.hora_generacion = hora_generacion
        self.id_usuario = id_usuario
        self.ruta_archivo = ruta_archivo

    @staticmethod
    def listar_reportes():
        """Retorna todos los reportes generados"""
        # TODO: Implementar conexión a base de datos
        reportes = []
        categorias = ['Citas Médicas', 'Usuarios', 'Servicios', 'Recursos', 'Financiero']
        empleados = [
            'Juan Pérez',
            'María García',
            'Carlos López',
            'Ana Martínez',
            'Pedro Sánchez'
        ]
        estados = ['Completado', 'Completado', 'Completado']  # Más completados
        
        # Generar reportes de ejemplo
        for i in range(1, 26):
            fecha_generacion = datetime.now() - timedelta(days=random.randint(0, 30))
            reportes.append({
                'idReporte': i,
                'nombreReporte': f'Reporte {categorias[i % len(categorias)]} - {i}',
                'categoria': categorias[i % len(categorias)],
                'fechaGeneracion': fecha_generacion.strftime('%Y-%m-%d'),
                'horaGeneracion': fecha_generacion.strftime('%H:%M:%S'),
                'nombreEmpleado': empleados[i % len(empleados)],
                'idUsuario': (i % 5) + 1,
                'rutaArchivo': f'/reportes/{fecha_generacion.strftime("%Y%m%d")}/reporte_{i}.pdf',
                'estado': estados[i % len(estados)],
                'descripcion': f'Análisis detallado de {categorias[i % len(categorias)].lower()} del período'
            })
        
        return reportes

    @staticmethod
    def buscar_reportes_por_categoria(categoria, fecha=None):
        """Busca reportes por categoría y opcionalmente por fecha"""
        reportes = Reporte.listar_reportes()
        
        # Filtrar por categoría
        if categoria and categoria != 'Todas':
            reportes = [r for r in reportes if r['categoria'] == categoria]
        
        # Filtrar por fecha
        if fecha:
            reportes = [r for r in reportes if r['fechaGeneracion'] == fecha]
        
        return reportes

    @staticmethod
    def generar_reporte(categoria, id_usuario, nombre_empleado):
        """Genera un nuevo reporte"""
        fecha_generacion = datetime.now()
        nuevo_reporte = {
            'idReporte': random.randint(1000, 9999),
            'nombreReporte': f'Reporte {categoria} - {fecha_generacion.strftime("%Y%m%d%H%M%S")}',
            'categoria': categoria,
            'fechaGeneracion': fecha_generacion.strftime('%Y-%m-%d'),
            'horaGeneracion': fecha_generacion.strftime('%H:%M:%S'),
            'nombreEmpleado': nombre_empleado,
            'idUsuario': id_usuario,
            'rutaArchivo': f'/reportes/{fecha_generacion.strftime("%Y%m%d")}/reporte_{random.randint(1000, 9999)}.pdf',
            'estado': 'Completado',
            'descripcion': f'Reporte generado de {categoria}'
        }
        # TODO: Guardar en base de datos
        return nuevo_reporte

    @staticmethod
    def historial_reportes_por_categoria():
        """Obtiene el historial de reportes agrupados por categoría"""
        reportes = Reporte.listar_reportes()
        historial = {}
        
        for reporte in reportes:
            categoria = reporte['categoria']
            if categoria not in historial:
                historial[categoria] = []
            historial[categoria].append(reporte)
        
        return historial

    @staticmethod
    def generar_reporte_actividad(categoria, fecha_inicio=None, fecha_fin=None):
        """Genera reporte de actividad por categoría y rango de fechas"""
        # TODO: Implementar lógica real de generación
        return {
            'categoria': categoria,
            'totalRegistros': random.randint(50, 500),
            'fechaInicio': fecha_inicio or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'fechaFin': fecha_fin or datetime.now().strftime('%Y-%m-%d'),
            'estado': 'Generado exitosamente'
        }
