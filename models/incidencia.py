from datetime import datetime, timedelta
import random

class Incidencia:
    """
    Modelo para gestionar incidencias en el sistema de la clínica.
    
    Atributos:
        id: Identificador único de la incidencia
        fechaRegistro: Fecha en que se registró la incidencia
        descripcion: Descripción detallada de la incidencia
        estado: Estado actual (Abierta, En Proceso, Resuelta, Cerrada)
        prioridad: Nivel de prioridad (Baja, Media, Alta, Crítica)
        fechaResolucion: Fecha en que se resolvió (puede ser None)
        observaciones: Notas adicionales sobre la incidencia
    """
    
    @staticmethod
    def obtener_todas():
        """Retorna una lista de incidencias simuladas"""
        estados = ['Abierta', 'En Proceso', 'Resuelta', 'Cerrada']
        prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
        
        descripciones = [
            'Fallo en el sistema de registro de pacientes',
            'Error en la base de datos de historias clínicas',
            'Problema con el equipo de rayos X',
            'Falta de suministros médicos en farmacia',
            'Aire acondicionado no funciona en sala de espera',
            'Sistema de citas presenta lentitud',
            'Impresora de recetas médicas averiada',
            'Fuga de agua en el baño del segundo piso',
            'Computadora de recepción no enciende',
            'Software de facturación genera errores',
            'Teléfono de emergencias sin línea',
            'Puerta automática de entrada atascada',
            'Sistema de respaldo no realiza copias',
            'Monitor de signos vitales descalibrado',
            'Red WiFi inestable en área de consultas',
            'Silla de ruedas requiere mantenimiento',
            'Extintor vencido en planta baja',
            'Iluminación deficiente en pasillo principal',
            'Autoclave presenta fallas intermitentes',
            'Sistema de alarma de emergencia sin batería',
            'Refrigerador de medicamentos con temperatura alta',
            'Camilla de emergencias con rueda rota',
            'Escaleras requieren señalización de seguridad',
            'Ascensor hace ruidos extraños',
            'Sistema de video vigilancia no graba'
        ]
        
        observaciones_templates = [
            'Se reportó el problema y se está evaluando la solución.',
            'Técnico asignado está trabajando en la resolución.',
            'Se requiere aprobación de gerencia para proceder.',
            'Problema resuelto satisfactoriamente.',
            'Se está esperando la llegada de repuestos.',
            'Incidencia crítica, requiere atención inmediata.',
            'Se programó mantenimiento preventivo.',
            'Usuario reporta que el problema persiste.',
            'Se realizaron pruebas y el sistema funciona correctamente.',
            'Pendiente de validación por parte del área solicitante.'
        ]
        
        incidencias = []
        fecha_base = datetime.now()
        
        for i in range(1, 26):
            # Generar fecha de registro (últimos 60 días)
            dias_atras = random.randint(0, 60)
            fecha_registro = fecha_base - timedelta(days=dias_atras)
            
            estado = random.choice(estados)
            prioridad = random.choice(prioridades)
            
            # Si está resuelta o cerrada, generar fecha de resolución
            fecha_resolucion = None
            if estado in ['Resuelta', 'Cerrada']:
                dias_resolucion = random.randint(1, 10)
                fecha_resolucion = fecha_registro + timedelta(days=dias_resolucion)
            
            incidencia = {
                'id': i,
                'fechaRegistro': fecha_registro.strftime('%d/%m/%Y'),
                'descripcion': descripciones[i-1],
                'estado': estado,
                'prioridad': prioridad,
                'fechaResolucion': fecha_resolucion.strftime('%d/%m/%Y') if fecha_resolucion else '-',
                'observaciones': random.choice(observaciones_templates)
            }
            
            incidencias.append(incidencia)
        
        # Ordenar por fecha de registro (más recientes primero)
        incidencias.sort(key=lambda x: datetime.strptime(x['fechaRegistro'], '%d/%m/%Y'), reverse=True)
        
        return incidencias
    
    @staticmethod
    def obtener_por_id(incidencia_id):
        """Retorna una incidencia específica por su ID"""
        incidencias = Incidencia.obtener_todas()
        for incidencia in incidencias:
            if incidencia['id'] == incidencia_id:
                return incidencia
        return None
    
    @staticmethod
    def obtener_estados():
        """Retorna la lista de estados posibles"""
        return ['Abierta', 'En Proceso', 'Resuelta', 'Cerrada']
    
    @staticmethod
    def obtener_prioridades():
        """Retorna la lista de prioridades posibles"""
        return ['Baja', 'Media', 'Alta', 'Crítica']
    
    @staticmethod
    def obtener_categorias():
        """Retorna las categorías de incidencias"""
        return [
            {'id': 1, 'nombre': 'Tecnología'},
            {'id': 2, 'nombre': 'Infraestructura'},
            {'id': 3, 'nombre': 'Equipamiento Médico'},
            {'id': 4, 'nombre': 'Suministros'},
            {'id': 5, 'nombre': 'Seguridad'}
        ]
