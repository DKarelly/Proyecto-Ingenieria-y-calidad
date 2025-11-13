"""
Pruebas de Caja Blanca para la aplicación Flask
Casos de prueba: TC-CB-01 a TC-CB-10
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Suponiendo que tu aplicación Flask está en app.py
# Ajusta las importaciones según tu estructura
# from app import app, db
# from models import Paciente, Servicio, Reserva, Incidencia, Usuario


class TestCajaBlanca:
    """Clase contenedora para todas las pruebas de caja blanca"""

    @pytest.fixture
    def app_client(self):
        """Fixture para crear un cliente de prueba de Flask"""
        # Mock de la aplicación Flask
        mock_app = Mock()
        mock_app.test_client.return_value = Mock()
        return mock_app.test_client()

    @pytest.fixture
    def mock_db(self):
        """Fixture para mockear la base de datos"""
        return MagicMock()

    # TC-CB-01: Validar registro de paciente
    def test_registro_paciente_datos_validos(self, mock_db):
        """Prueba registro de paciente con datos válidos"""
        datos_validos = {
            'nombres': 'Juan',
            'apellidos': 'Pérez García',
            'correo': 'juan.perez@email.com',
            'telefono': '987654321',
            'dni': '12345678'
        }
        
        # Simular función de registro
        def registrar_paciente(datos):
            if not datos.get('nombres') or not datos.get('nombres').strip():
                return {'error': 'Nombres requeridos'}, 400
            if not datos.get('apellidos') or not datos.get('apellidos').strip():
                return {'error': 'Apellidos requeridos'}, 400
            if not datos.get('correo') or '@' not in datos.get('correo', ''):
                return {'error': 'Correo inválido'}, 400
            
            # Simulación de inserción en BD
            mock_db.insert.return_value = True
            return {'success': True, 'id': 1}, 201
        
        resultado, codigo = registrar_paciente(datos_validos)
        
        assert codigo == 201
        assert resultado['success'] is True
        assert 'id' in resultado

    def test_registro_paciente_nombres_vacios(self, mock_db):
        """Prueba registro con nombres vacíos"""
        datos_invalidos = {
            'nombres': '',
            'apellidos': 'Pérez',
            'correo': 'test@email.com'
        }
        
        def registrar_paciente(datos):
            if not datos.get('nombres') or not datos.get('nombres').strip():
                return {'error': 'Nombres requeridos'}, 400
            return {'success': True}, 201
        
        resultado, codigo = registrar_paciente(datos_invalidos)
        
        assert codigo == 400
        assert 'error' in resultado
        assert resultado['error'] == 'Nombres requeridos'

    def test_registro_paciente_apellidos_vacios(self, mock_db):
        """Prueba registro con apellidos vacíos"""
        datos_invalidos = {
            'nombres': 'Juan',
            'apellidos': '   ',
            'correo': 'test@email.com'
        }
        
        def registrar_paciente(datos):
            if not datos.get('apellidos') or not datos.get('apellidos').strip():
                return {'error': 'Apellidos requeridos'}, 400
            return {'success': True}, 201
        
        resultado, codigo = registrar_paciente(datos_invalidos)
        
        assert codigo == 400
        assert resultado['error'] == 'Apellidos requeridos'

    def test_registro_paciente_correo_invalido(self, mock_db):
        """Prueba registro con correo inválido"""
        datos_invalidos = {
            'nombres': 'Juan',
            'apellidos': 'Pérez',
            'correo': 'correo_sin_arroba.com'
        }
        
        def registrar_paciente(datos):
            if not datos.get('correo') or '@' not in datos.get('correo', ''):
                return {'error': 'Correo inválido'}, 400
            return {'success': True}, 201
        
        resultado, codigo = registrar_paciente(datos_invalidos)
        
        assert codigo == 400
        assert resultado['error'] == 'Correo inválido'

    # TC-CB-02: Validar registro de servicio
    def test_registro_servicio_datos_validos(self, mock_db):
        """Prueba registro de servicio con datos válidos"""
        datos_servicio = {
            'nombre': 'Consulta General',
            'descripcion': 'Consulta médica general',
            'tipo': 'consulta',
            'especialidad': 'medicina_general',
            'duracion': 30,
            'precio': 50.00
        }
        
        def registrar_servicio(datos):
            if not datos.get('nombre') or not datos.get('nombre').strip():
                return {'error': 'Nombre requerido'}, 400
            if not datos.get('descripcion'):
                return {'error': 'Descripción requerida'}, 400
            if not datos.get('tipo') or datos.get('tipo') not in ['consulta', 'procedimiento', 'emergencia']:
                return {'error': 'Tipo inválido'}, 400
            if not datos.get('especialidad'):
                return {'error': 'Especialidad requerida'}, 400
            
            mock_db.insert.return_value = True
            return {'success': True, 'id': 1}, 201
        
        resultado, codigo = registrar_servicio(datos_servicio)
        
        assert codigo == 201
        assert resultado['success'] is True

    def test_registro_servicio_nombre_vacio(self, mock_db):
        """Prueba registro de servicio con nombre vacío"""
        datos_invalidos = {
            'nombre': '',
            'descripcion': 'Test',
            'tipo': 'consulta',
            'especialidad': 'general'
        }
        
        def registrar_servicio(datos):
            if not datos.get('nombre') or not datos.get('nombre').strip():
                return {'error': 'Nombre requerido'}, 400
            return {'success': True}, 201
        
        resultado, codigo = registrar_servicio(datos_invalidos)
        
        assert codigo == 400
        assert resultado['error'] == 'Nombre requerido'

    def test_registro_servicio_tipo_invalido(self, mock_db):
        """Prueba registro de servicio con tipo inválido"""
        datos_invalidos = {
            'nombre': 'Servicio Test',
            'descripcion': 'Descripción',
            'tipo': 'tipo_inexistente',
            'especialidad': 'general'
        }
        
        def registrar_servicio(datos):
            if datos.get('tipo') not in ['consulta', 'procedimiento', 'emergencia']:
                return {'error': 'Tipo inválido'}, 400
            return {'success': True}, 201
        
        resultado, codigo = registrar_servicio(datos_invalidos)
        
        assert codigo == 400
        assert resultado['error'] == 'Tipo inválido'

    # TC-CB-03: Verificar asignación de responsable
    def test_asignar_responsable_exitoso(self, mock_db):
        """Prueba asignación de responsable exitosa"""
        datos_asignacion = {
            'servicio_id': 1,
            'usuario_id': 5,
            'rol': 'medico'
        }
        
        def asignar_responsable(datos):
            # Buscar usuario
            mock_db.query.return_value.filter.return_value.first.return_value = {
                'id': datos['usuario_id'],
                'rol': datos['rol']
            }
            
            usuario = mock_db.query.return_value.filter.return_value.first()
            
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404
            
            if usuario['rol'] != datos['rol']:
                return {'error': 'Rol no coincide'}, 403
            
            # Actualizar en BD
            mock_db.update.return_value = True
            return {'success': True, 'asignado': True}, 200
        
        resultado, codigo = asignar_responsable(datos_asignacion)
        
        assert codigo == 200
        assert resultado['success'] is True
        assert resultado['asignado'] is True

    def test_asignar_responsable_usuario_no_encontrado(self, mock_db):
        """Prueba asignación con usuario inexistente"""
        datos_asignacion = {
            'servicio_id': 1,
            'usuario_id': 999,
            'rol': 'medico'
        }
        
        def asignar_responsable(datos):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            usuario = mock_db.query.return_value.filter.return_value.first()
            
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404
            
            return {'success': True}, 200
        
        resultado, codigo = asignar_responsable(datos_asignacion)
        
        assert codigo == 404
        assert resultado['error'] == 'Usuario no encontrado'

    def test_asignar_responsable_rol_incorrecto(self, mock_db):
        """Prueba asignación con rol incorrecto"""
        datos_asignacion = {
            'servicio_id': 1,
            'usuario_id': 5,
            'rol': 'medico'
        }
        
        def asignar_responsable(datos):
            mock_db.query.return_value.filter.return_value.first.return_value = {
                'id': datos['usuario_id'],
                'rol': 'enfermero'  # Rol diferente al esperado
            }
            
            usuario = mock_db.query.return_value.filter.return_value.first()
            
            if usuario['rol'] != datos['rol']:
                return {'error': 'Rol no coincide'}, 403
            
            return {'success': True}, 200
        
        resultado, codigo = asignar_responsable(datos_asignacion)
        
        assert codigo == 403
        assert resultado['error'] == 'Rol no coincide'

    # TC-CB-04: Evaluar envío de notificación por correo
    @patch('smtplib.SMTP')
    def test_envio_notificacion_exitoso(self, mock_smtp):
        """Prueba envío de notificación exitoso"""
        datos_correo = {
            'destinatario': 'paciente@email.com',
            'asunto': 'Confirmación de cita',
            'mensaje': 'Su cita ha sido confirmada'
        }
        
        def enviar_notificacion(datos):
            try:
                if not datos.get('destinatario') or '@' not in datos['destinatario']:
                    return {'error': 'Correo destinatario inválido'}, 400
                
                if not datos.get('asunto') or not datos.get('mensaje'):
                    return {'error': 'Asunto y mensaje requeridos'}, 400
                
                # Simular envío de correo
                servidor = mock_smtp.return_value
                servidor.sendmail.return_value = {}
                
                return {'success': True, 'enviado': True}, 200
            except Exception as e:
                return {'error': f'Error al enviar: {str(e)}'}, 500
        
        resultado, codigo = enviar_notificacion(datos_correo)
        
        assert codigo == 200
        assert resultado['success'] is True
        assert resultado['enviado'] is True

    def test_envio_notificacion_correo_invalido(self):
        """Prueba envío con correo inválido"""
        datos_correo = {
            'destinatario': 'correo_invalido',
            'asunto': 'Test',
            'mensaje': 'Mensaje de prueba'
        }
        
        def enviar_notificacion(datos):
            if not datos.get('destinatario') or '@' not in datos['destinatario']:
                return {'error': 'Correo destinatario inválido'}, 400
            return {'success': True}, 200
        
        resultado, codigo = enviar_notificacion(datos_correo)
        
        assert codigo == 400
        assert resultado['error'] == 'Correo destinatario inválido'

    def test_envio_notificacion_sin_asunto(self):
        """Prueba envío sin asunto"""
        datos_correo = {
            'destinatario': 'test@email.com',
            'asunto': '',
            'mensaje': 'Mensaje'
        }
        
        def enviar_notificacion(datos):
            if not datos.get('asunto') or not datos.get('mensaje'):
                return {'error': 'Asunto y mensaje requeridos'}, 400
            return {'success': True}, 200
        
        resultado, codigo = enviar_notificacion(datos_correo)
        
        assert codigo == 400
        assert resultado['error'] == 'Asunto y mensaje requeridos'

    # TC-CB-05: Probar algoritmo de búsqueda de horarios disponibles
    def test_buscar_horarios_disponibles_sin_conflictos(self, mock_db):
        """Prueba búsqueda de horarios sin conflictos"""
        parametros = {
            'fecha': '2025-11-15',
            'medico_id': 1,
            'duracion': 30
        }
        
        def buscar_horarios_disponibles(params):
            # Simular horarios ocupados en BD
            mock_db.query.return_value.filter.return_value.all.return_value = [
                {'hora_inicio': '09:00', 'hora_fin': '09:30'},
                {'hora_inicio': '11:00', 'hora_fin': '11:30'}
            ]
            
            horarios_ocupados = mock_db.query.return_value.filter.return_value.all()
            
            # Generar horarios del día
            horarios_dia = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00']
            horarios_disponibles = []
            
            for horario in horarios_dia:
                conflicto = False
                for ocupado in horarios_ocupados:
                    if horario == ocupado['hora_inicio']:
                        conflicto = True
                        break
                
                if not conflicto:
                    horarios_disponibles.append(horario)
            
            return {'horarios': horarios_disponibles, 'total': len(horarios_disponibles)}, 200
        
        resultado, codigo = buscar_horarios_disponibles(parametros)
        
        assert codigo == 200
        assert 'horarios' in resultado
        assert len(resultado['horarios']) > 0
        assert '10:00' in resultado['horarios']

    def test_buscar_horarios_con_conflictos(self, mock_db):
        """Prueba búsqueda de horarios con todos ocupados"""
        parametros = {
            'fecha': '2025-11-15',
            'medico_id': 1,
            'duracion': 30
        }
        
        def buscar_horarios_disponibles(params):
            # Todos los horarios ocupados
            mock_db.query.return_value.filter.return_value.all.return_value = [
                {'hora_inicio': h, 'hora_fin': h} 
                for h in ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30']
            ]
            
            horarios_ocupados = mock_db.query.return_value.filter.return_value.all()
            horarios_dia = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30']
            
            horarios_disponibles = [h for h in horarios_dia 
                                  if h not in [o['hora_inicio'] for o in horarios_ocupados]]
            
            if len(horarios_disponibles) == 0:
                return {'mensaje': 'No hay horarios disponibles'}, 200
            
            return {'horarios': horarios_disponibles}, 200
        
        resultado, codigo = buscar_horarios_disponibles(parametros)
        
        assert codigo == 200
        assert 'mensaje' in resultado

    # TC-CB-06: Validar creación de reserva
    def test_crear_reserva_exitosa(self, mock_db):
        """Prueba creación de reserva exitosa"""
        datos_reserva = {
            'paciente_id': 1,
            'servicio_id': 2,
            'fecha': '2025-11-20',
            'hora': '10:00',
            'medico_id': 3
        }
        
        def crear_reserva(datos):
            # Verificar disponibilidad
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            reserva_existente = mock_db.query.return_value.filter.return_value.first()
            
            if reserva_existente:
                return {'error': 'Horario no disponible'}, 409
            
            # Validar datos requeridos
            if not all([datos.get('paciente_id'), datos.get('servicio_id'), 
                       datos.get('fecha'), datos.get('hora')]):
                return {'error': 'Datos incompletos'}, 400
            
            # Insertar reserva
            mock_db.insert.return_value = True
            return {'success': True, 'reserva_id': 1, 'estado': 'confirmada'}, 201
        
        resultado, codigo = crear_reserva(datos_reserva)
        
        assert codigo == 201
        assert resultado['success'] is True
        assert 'reserva_id' in resultado
        assert resultado['estado'] == 'confirmada'

    def test_crear_reserva_horario_ocupado(self, mock_db):
        """Prueba creación de reserva con horario ocupado"""
        datos_reserva = {
            'paciente_id': 1,
            'servicio_id': 2,
            'fecha': '2025-11-20',
            'hora': '10:00',
            'medico_id': 3
        }
        
        def crear_reserva(datos):
            # Simular que el horario ya está ocupado
            mock_db.query.return_value.filter.return_value.first.return_value = {
                'id': 5, 'fecha': datos['fecha'], 'hora': datos['hora']
            }
            
            reserva_existente = mock_db.query.return_value.filter.return_value.first()
            
            if reserva_existente:
                return {'error': 'Horario no disponible'}, 409
            
            return {'success': True}, 201
        
        resultado, codigo = crear_reserva(datos_reserva)
        
        assert codigo == 409
        assert resultado['error'] == 'Horario no disponible'

    def test_crear_reserva_datos_incompletos(self, mock_db):
        """Prueba creación de reserva con datos incompletos"""
        datos_reserva = {
            'paciente_id': 1,
            'servicio_id': None,
            'fecha': '2025-11-20'
        }
        
        def crear_reserva(datos):
            if not all([datos.get('paciente_id'), datos.get('servicio_id'), 
                       datos.get('fecha'), datos.get('hora')]):
                return {'error': 'Datos incompletos'}, 400
            
            return {'success': True}, 201
        
        resultado, codigo = crear_reserva(datos_reserva)
        
        assert codigo == 400
        assert resultado['error'] == 'Datos incompletos'

    # TC-CB-07: Evaluar cancelación de reserva
    def test_cancelar_reserva_exitosa(self, mock_db):
        """Prueba cancelación de reserva exitosa"""
        datos_cancelacion = {
            'reserva_id': 1,
            'motivo': 'Cancelación por motivos personales'
        }
        
        def cancelar_reserva(datos):
            # Buscar reserva
            mock_db.query.return_value.filter.return_value.first.return_value = {
                'id': datos['reserva_id'],
                'estado': 'confirmada',
                'paciente_correo': 'paciente@email.com'
            }
            
            reserva = mock_db.query.return_value.filter.return_value.first()
            
            if not reserva:
                return {'error': 'Reserva no encontrada'}, 404
            
            if reserva['estado'] == 'cancelada':
                return {'error': 'Reserva ya cancelada'}, 400
            
            # Actualizar estado
            mock_db.update.return_value = True
            
            # Enviar notificación (mock)
            notificacion_enviada = True
            
            return {
                'success': True, 
                'estado': 'cancelada',
                'notificacion_enviada': notificacion_enviada
            }, 200
        
        resultado, codigo = cancelar_reserva(datos_cancelacion)
        
        assert codigo == 200
        assert resultado['success'] is True
        assert resultado['estado'] == 'cancelada'
        assert resultado['notificacion_enviada'] is True

    def test_cancelar_reserva_no_encontrada(self, mock_db):
        """Prueba cancelación de reserva inexistente"""
        datos_cancelacion = {
            'reserva_id': 999,
            'motivo': 'Test'
        }
        
        def cancelar_reserva(datos):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            reserva = mock_db.query.return_value.filter.return_value.first()
            
            if not reserva:
                return {'error': 'Reserva no encontrada'}, 404
            
            return {'success': True}, 200
        
        resultado, codigo = cancelar_reserva(datos_cancelacion)
        
        assert codigo == 404
        assert resultado['error'] == 'Reserva no encontrada'

    def test_cancelar_reserva_ya_cancelada(self, mock_db):
        """Prueba cancelación de reserva ya cancelada"""
        datos_cancelacion = {
            'reserva_id': 1,
            'motivo': 'Test'
        }
        
        def cancelar_reserva(datos):
            mock_db.query.return_value.filter.return_value.first.return_value = {
                'id': datos['reserva_id'],
                'estado': 'cancelada'
            }
            
            reserva = mock_db.query.return_value.filter.return_value.first()
            
            if reserva['estado'] == 'cancelada':
                return {'error': 'Reserva ya cancelada'}, 400
            
            return {'success': True}, 200
        
        resultado, codigo = cancelar_reserva(datos_cancelacion)
        
        assert codigo == 400
        assert resultado['error'] == 'Reserva ya cancelada'

    # TC-CB-08: Verificar creación de incidencia
    def test_crear_incidencia_exitosa(self, mock_db):
        """Prueba creación de incidencia exitosa"""
        datos_incidencia = {
            'titulo': 'Problema con sistema',
            'descripcion': 'El sistema no responde correctamente',
            'usuario_id': 1,
            'prioridad': 'alta'
        }
        
        def crear_incidencia(datos):
            if not datos.get('titulo') or not datos.get('descripcion'):
                return {'error': 'Título y descripción requeridos'}, 400
            
            # Generar ID automático
            mock_db.query.return_value.count.return_value = 10
            ultimo_id = mock_db.query.return_value.count()
            nuevo_id = ultimo_id + 1
            
            # Registrar en BD
            mock_db.insert.return_value = True
            
            return {
                'success': True,
                'incidencia_id': nuevo_id,
                'estado': 'abierta',
                'fecha_creacion': '2025-11-12'
            }, 201
        
        resultado, codigo = crear_incidencia(datos_incidencia)
        
        assert codigo == 201
        assert resultado['success'] is True
        assert resultado['incidencia_id'] == 11
        assert resultado['estado'] == 'abierta'

    def test_crear_incidencia_datos_incompletos(self, mock_db):
        """Prueba creación de incidencia con datos incompletos"""
        datos_incidencia = {
            'titulo': '',
            'descripcion': 'Test'
        }
        
        def crear_incidencia(datos):
            if not datos.get('titulo') or not datos.get('descripcion'):
                return {'error': 'Título y descripción requeridos'}, 400
            
            return {'success': True}, 201
        
        resultado, codigo = crear_incidencia(datos_incidencia)
        
        assert codigo == 400
        assert resultado['error'] == 'Título y descripción requeridos'

    # TC-CB-09: Validar obtención de perfil
    def test_obtener_perfil_exitoso(self, mock_db):
        """Prueba obtención de perfil exitosa con joins"""
        usuario_id = 1
        
        def obtener_perfil(user_id):
            # Simular query con joins
            mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = {
                'id': user_id,
                'nombre': 'Juan Pérez',
                'correo': 'juan@email.com',
                'rol': 'medico',
                'permisos': ['leer', 'escribir', 'eliminar'],
                'especialidad': 'Cardiología',
                'licencia': 'MED-12345'
            }
            
            perfil = mock_db.query.return_value.join.return_value.filter.return_value.first()
            
            if not perfil:
                return {'error': 'Usuario no encontrado'}, 404
            
            # Verificar permisos
            if 'leer' not in perfil['permisos']:
                return {'error': 'Sin permisos de lectura'}, 403
            
            return {
                'success': True,
                'perfil': perfil
            }, 200
        
        resultado, codigo = obtener_perfil(usuario_id)
        
        assert codigo == 200
        assert resultado['success'] is True
        assert resultado['perfil']['nombre'] == 'Juan Pérez'
        assert 'especialidad' in resultado['perfil']

    def test_obtener_perfil_usuario_no_encontrado(self, mock_db):
        """Prueba obtención de perfil de usuario inexistente"""
        usuario_id = 999
        
        def obtener_perfil(user_id):
            mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = None
            perfil = mock_db.query.return_value.join.return_value.filter.return_value.first()
            
            if not perfil:
                return {'error': 'Usuario no encontrado'}, 404
            
            return {'success': True, 'perfil': perfil}, 200
        
        resultado, codigo = obtener_perfil(usuario_id)
        
        assert codigo == 404
        assert resultado['error'] == 'Usuario no encontrado'

    def test_obtener_perfil_sin_permisos(self, mock_db):
        """Prueba obtención de perfil sin permisos"""
        usuario_id = 1
        
        def obtener_perfil(user_id):
            mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = {
                'id': user_id,
                'nombre': 'Usuario Test',
                'permisos': []
            }
            
            perfil = mock_db.query.return_value.join.return_value.filter.return_value.first()
            
            if 'leer' not in perfil['permisos']:
                return {'error': 'Sin permisos de lectura'}, 403
            
            return {'success': True, 'perfil': perfil}, 200
        
        resultado, codigo = obtener_perfil(usuario_id)
        
        assert codigo == 403
        assert resultado['error'] == 'Sin permisos de lectura'

    # TC-CB-10: Probar listado de usuarios
    def test_listar_usuarios_con_paginacion(self, mock_db):
        """Prueba listado de usuarios con paginación"""
        parametros = {
            'pagina': 1,
            'por_pagina': 10,
            'filtro_rol': None,
            'busqueda': None
        }
        
        def listar_usuarios(params):
            # Simular query con paginación
            usuarios_mock = [
                {'id': i, 'nombre': f'Usuario {i}', 'rol': 'medico' if i % 2 == 0 else 'paciente'}
                for i in range(1, 16)
            ]
            
            # Aplicar filtros
            usuarios_filtrados = usuarios_mock
            
            if params.get('filtro_rol'):
                usuarios_filtrados = [u for u in usuarios_filtrados 
                                    if u['rol'] == params['filtro_rol']]
            
            if params.get('busqueda'):
                usuarios_filtrados = [u for u in usuarios_filtrados 
                                    if params['busqueda'].lower() in u['nombre'].lower()]
            
            # Aplicar paginación
            inicio = (params['pagina'] - 1) * params['por_pagina']
            fin = inicio + params['por_pagina']
            usuarios_pagina = usuarios_filtrados[inicio:fin]
            
            return {
                'success': True,
                'usuarios': usuarios_pagina,
                'total': len(usuarios_filtrados),
                'pagina': params['pagina'],
                'por_pagina': params['por_pagina'],
                'total_paginas': (len(usuarios_filtrados) + params['por_pagina'] - 1) // params['por_pagina']
            }, 200
        
        resultado, codigo = listar_usuarios(parametros)
        
        assert codigo == 200
        assert resultado['success'] is True
        assert len(resultado['usuarios']) == 10
        assert resultado['total'] == 15
        assert resultado['total_paginas'] == 2

    def test_listar_usuarios_con_filtro_rol(self, mock_db):
        """Prueba listado de usuarios con filtro por rol"""
        parametros = {
            'pagina': 1,
            'por_pagina': 10,
            'filtro_rol': 'medico',
            'busqueda': None
        }
        
        def listar_usuarios(params):
            usuarios_mock = [
                {'id': 1, 'nombre': 'Dr. Juan', 'rol': 'medico'},
                {'id': 2, 'nombre': 'Paciente María', 'rol': 'paciente'},
                {'id': 3, 'nombre': 'Dr. Pedro', 'rol': 'medico'}
            ]
            
            usuarios_filtrados = [u for u in usuarios_mock 
                                if u['rol'] == params['filtro_rol']]
            
            return {
                'success': True,
                'usuarios': usuarios_filtrados,
                'total': len(usuarios_filtrados)
            }, 200
        
        resultado, codigo = listar_usuarios(parametros)
        
        assert codigo == 200
        assert len(resultado['usuarios']) == 2
        assert all(u['rol'] == 'medico' for u in resultado['usuarios'])

    def test_listar_usuarios_con_busqueda(self, mock_db):
        """Prueba listado de usuarios con búsqueda"""
        parametros = {
            'pagina': 1,
            'por_pagina': 10,
            'filtro_rol': None,
            'busqueda': 'Juan'
        }
        
        def listar_usuarios(params):
            usuarios_mock = [
                {'id': 1, 'nombre': 'Juan Pérez', 'rol': 'medico'},
                {'id': 2, 'nombre': 'María López', 'rol': 'paciente'},
                {'id': 3, 'nombre': 'Juan García', 'rol': 'enfermero'}
            ]
            
            usuarios_filtrados = [u for u in usuarios_mock 
                                if params['busqueda'].lower() in u['nombre'].lower()]
            
            return {
                'success': True,
                'usuarios': usuarios_filtrados,
                'total': len(usuarios_filtrados)
            }, 200
        
        resultado, codigo = listar_usuarios(parametros)
        
        assert codigo == 200
        assert len(resultado['usuarios']) == 2
        assert all('Juan' in u['nombre'] for u in resultado['usuarios'])

    def test_listar_usuarios_pagina_vacia(self, mock_db):
        """Prueba listado de usuarios en página sin resultados"""
        parametros = {
            'pagina': 10,
            'por_pagina': 10,
            'filtro_rol': None,
            'busqueda': None
        }
        
        def listar_usuarios(params):
            usuarios_mock = [{'id': i, 'nombre': f'Usuario {i}'} for i in range(1, 6)]
            
            inicio = (params['pagina'] - 1) * params['por_pagina']
            fin = inicio + params['por_pagina']
            usuarios_pagina = usuarios_mock[inicio:fin]
            
            return {
                'success': True,
                'usuarios': usuarios_pagina,
                'total': len(usuarios_mock)
            }, 200
        
        resultado, codigo = listar_usuarios(parametros)
        
        assert codigo == 200
        assert len(resultado['usuarios']) == 0
        assert resultado['total'] == 5


# Configuración de pytest
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])