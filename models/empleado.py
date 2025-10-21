# Modelo Empleado - Personal del centro médico
from datetime import datetime

class Empleado:
    def __init__(self, id_empleado, nombre_empleado, apellido_empleado, dni_empleado, 
                 correo_empleado, contraseña_empleado, estado_empleado, fecha_registro):
        self.id_empleado = id_empleado
        self.nombre_empleado = nombre_empleado
        self.apellido_empleado = apellido_empleado
        self.dni_empleado = dni_empleado
        self.correo_empleado = correo_empleado
        self.contraseña_empleado = contraseña_empleado
        self.estado_empleado = estado_empleado
        self.fecha_registro = fecha_registro

    @staticmethod
    def listar_empleados():
        """Retorna lista de empleados desde la base de datos"""
        # TODO: Implementar conexión a base de datos
        return [
            {
                'idEmpleado': 1,
                'nombreEmpleado': 'Juan',
                'apellidoEmpleado': 'Pérez',
                'dniEmpleado': '12345678'
            },
            {
                'idEmpleado': 2,
                'nombreEmpleado': 'María',
                'apellidoEmpleado': 'García',
                'dniEmpleado': '87654321'
            }
        ]

    @staticmethod
    def buscar_empleado(nombre_empleado):
        """Busca empleados por nombre"""
        empleados = Empleado.listar_empleados()
        if nombre_empleado:
            return [e for e in empleados if nombre_empleado.lower() in 
                    f"{e['nombreEmpleado']} {e['apellidoEmpleado']}".lower()]
        return empleados

    @staticmethod
    def actualizar_datos(id_empleado):
        """Actualiza los datos del empleado"""
        # TODO: Implementar actualización en base de datos
        pass

    @staticmethod
    def actualizar_estado(id_empleado, estado):
        """Actualiza el estado del empleado"""
        # TODO: Implementar actualización de estado en base de datos
        pass
