# Modelo Paciente

class Paciente:
    def __init__(self, id, nombre, apellido, dni, fecha_nacimiento, telefono, email, direccion):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
    
    @staticmethod
    def obtener_todos():
        """Retorna una lista de todos los pacientes (datos simulados)"""
        pacientes = [
            {
                'id': 1,
                'nombre': 'Juan',
                'apellido': 'Pérez García',
                'dni': '12345678',
                'fecha_nacimiento': '1985-03-15',
                'telefono': '987654321',
                'email': 'juan.perez@email.com',
                'direccion': 'Av. Principal 123'
            },
            {
                'id': 2,
                'nombre': 'María',
                'apellido': 'López Rodríguez',
                'dni': '23456789',
                'fecha_nacimiento': '1990-07-22',
                'telefono': '987654322',
                'email': 'maria.lopez@email.com',
                'direccion': 'Jr. Los Olivos 456'
            },
            {
                'id': 3,
                'nombre': 'Carlos',
                'apellido': 'Sánchez Torres',
                'dni': '34567890',
                'fecha_nacimiento': '1978-11-08',
                'telefono': '987654323',
                'email': 'carlos.sanchez@email.com',
                'direccion': 'Calle Las Flores 789'
            },
            {
                'id': 4,
                'nombre': 'Ana',
                'apellido': 'Martínez Silva',
                'dni': '45678901',
                'fecha_nacimiento': '1995-01-30',
                'telefono': '987654324',
                'email': 'ana.martinez@email.com',
                'direccion': 'Av. Los Pinos 321'
            },
            {
                'id': 5,
                'nombre': 'Luis',
                'apellido': 'Ramírez Castro',
                'dni': '56789012',
                'fecha_nacimiento': '1982-09-14',
                'telefono': '987654325',
                'email': 'luis.ramirez@email.com',
                'direccion': 'Jr. San Martín 654'
            },
            {
                'id': 6,
                'nombre': 'Patricia',
                'apellido': 'Flores Mendoza',
                'dni': '67890123',
                'fecha_nacimiento': '1988-05-19',
                'telefono': '987654326',
                'email': 'patricia.flores@email.com',
                'direccion': 'Calle Libertad 987'
            },
            {
                'id': 7,
                'nombre': 'Roberto',
                'apellido': 'Díaz Fernández',
                'dni': '78901234',
                'fecha_nacimiento': '1975-12-03',
                'telefono': '987654327',
                'email': 'roberto.diaz@email.com',
                'direccion': 'Av. Grau 147'
            },
            {
                'id': 8,
                'nombre': 'Carmen',
                'apellido': 'Vargas Gutiérrez',
                'dni': '89012345',
                'fecha_nacimiento': '1992-04-25',
                'telefono': '987654328',
                'email': 'carmen.vargas@email.com',
                'direccion': 'Jr. Comercio 258'
            },
            {
                'id': 9,
                'nombre': 'Jorge',
                'apellido': 'Cruz Morales',
                'dni': '90123456',
                'fecha_nacimiento': '1980-08-11',
                'telefono': '987654329',
                'email': 'jorge.cruz@email.com',
                'direccion': 'Calle Real 369'
            },
            {
                'id': 10,
                'nombre': 'Elena',
                'apellido': 'Rojas Vega',
                'dni': '01234567',
                'fecha_nacimiento': '1997-02-17',
                'telefono': '987654330',
                'email': 'elena.rojas@email.com',
                'direccion': 'Av. Bolognesi 741'
            }
        ]
        return pacientes
    
    @staticmethod
    def obtener_por_id(id):
        """Retorna un paciente específico por su ID"""
        pacientes = Paciente.obtener_todos()
        for paciente in pacientes:
            if paciente['id'] == id:
                return paciente
        return None
    
    @staticmethod
    def obtener_por_dni(dni):
        """Retorna un paciente por su DNI"""
        pacientes = Paciente.obtener_todos()
        for paciente in pacientes:
            if paciente['dni'] == dni:
                return paciente
        return None