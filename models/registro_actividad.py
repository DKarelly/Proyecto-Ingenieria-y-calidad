# Modelo Registro Actividad - Auditoría del sistema
from datetime import datetime

class RegistroActividad:
    def __init__(self, id_registro, id_empleado, descripcion, fecha_hora, 
                 ip_origen, resultado, detalles_error=None):
        self.id_registro = id_registro
        self.id_empleado = id_empleado
        self.descripcion = descripcion
        self.fecha_hora = fecha_hora
        self.ip_origen = ip_origen
        self.resultado = resultado
        self.detalles_error = detalles_error

    @staticmethod
    def listar_registros():
        """Retorna todos los registros de actividad"""
        # TODO: Implementar conexión a base de datos
        return [
            {
                'idRegistro': 1,
                'idEmpleado': 1,
                'nombreEmpleado': 'Juan Pérez',
                'descripcion': 'Inicio de sesión exitoso',
                'fechaHora': '2025-10-21 08:30:00',
                'ipOrigen': '192.168.1.100',
                'resultado': 'Exitoso',
                'detallesError': None
            },
            {
                'idRegistro': 2,
                'idEmpleado': 2,
                'nombreEmpleado': 'María García',
                'descripcion': 'Modificación de cita médica',
                'fechaHora': '2025-10-21 09:15:00',
                'ipOrigen': '192.168.1.101',
                'resultado': 'Exitoso',
                'detallesError': None
            },
            {
                'idRegistro': 3,
                'idEmpleado': 1,
                'nombreEmpleado': 'Juan Pérez',
                'descripcion': 'Intento de acceso no autorizado',
                'fechaHora': '2025-10-21 10:00:00',
                'ipOrigen': '192.168.1.100',
                'resultado': 'Fallido',
                'detallesError': 'Permisos insuficientes'
            }
        ]

    @staticmethod
    def buscar_registros(filtros):
        """Busca registros aplicando filtros"""
        registros = RegistroActividad.listar_registros()
        resultados = registros

        # Filtrar por empleado
        if filtros.get('empleado'):
            resultados = [r for r in resultados if filtros['empleado'].lower() in 
                         r['nombreEmpleado'].lower()]

        # Filtrar por fecha
        if filtros.get('fecha'):
            resultados = [r for r in resultados if filtros['fecha'] in r['fechaHora']]

        # Filtrar por horario (si se implementa)
        # if filtros.get('horario'):
        #     # Lógica para filtrar por horario

        return resultados

    @staticmethod
    def registrar_actividad(id_empleado, descripcion, ip_origen, resultado, detalles_error=None):
        """Registra una nueva actividad en el sistema"""
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # TODO: Implementar inserción en base de datos
        nuevo_registro = {
            'idEmpleado': id_empleado,
            'descripcion': descripcion,
            'fechaHora': fecha_hora,
            'ipOrigen': ip_origen,
            'resultado': resultado,
            'detallesError': detalles_error
        }
        return nuevo_registro

    @staticmethod
    def exportar_registros(formato='pdf'):
        """Exporta los registros en formato PDF o Excel"""
        # TODO: Implementar exportación
        pass
