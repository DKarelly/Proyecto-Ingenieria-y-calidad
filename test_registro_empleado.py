"""
Script de prueba para verificar el registro de empleado
"""
from models.usuario import Usuario
from models.empleado import Empleado
import random
import string

# Generar datos únicos
timestamp = ''.join(random.choices(string.digits, k=6))
nombres = "TestEmpleado"
apellidos = f"Prueba{timestamp}"
documento = f"99{timestamp}"
sexo = "Masculino"
telefono = f"9{timestamp[:8]}"
fecha_nacimiento = "1990-05-15"
email = f"test.empleado.{timestamp}@prueba.com"
password = "Test1234"
id_rol = 1  # Administrador
id_distrito = 140312  # Distrito de ejemplo
id_especialidad = None

print("="*60)
print("PRUEBA DE REGISTRO DE EMPLEADO")
print("="*60)
print(f"Datos a insertar:")
print(f"  Nombres: {nombres}")
print(f"  Apellidos: {apellidos}")
print(f"  Documento: {documento}")
print(f"  Email: {email}")
print(f"  Teléfono: {telefono}")
print(f"  Sexo: {sexo}")
print(f"  Fecha Nacimiento: {fecha_nacimiento}")
print(f"  Rol: {id_rol}")
print(f"  Distrito: {id_distrito}")
print(f"  Especialidad: {id_especialidad}")
print("="*60)

# Paso 1: Verificar que el correo no existe
print("\n[1/4] Verificando que el correo no existe...")
usuario_existente = Usuario.obtener_por_correo(email)
if usuario_existente:
    print(f"❌ ERROR: El correo {email} ya existe")
    exit(1)
print("✓ Correo disponible")

# Paso 2: Verificar que el documento no existe
print("\n[2/4] Verificando que el documento no existe...")
empleado_existente = Empleado.obtener_por_documento(documento)
if empleado_existente:
    print(f"❌ ERROR: El documento {documento} ya existe")
    exit(1)
print("✓ Documento disponible")

# Paso 3: Crear usuario
print("\n[3/4] Creando usuario...")
resultado_usuario = Usuario.crear_usuario(
    contrasena=password,
    correo=email,
    telefono=telefono
)

if 'error' in resultado_usuario:
    print(f"❌ ERROR al crear usuario: {resultado_usuario['error']}")
    exit(1)

id_usuario = resultado_usuario['id_usuario']
print(f"✓ Usuario creado con ID: {id_usuario}")

# Paso 4: Crear empleado
print("\n[4/4] Creando empleado...")
resultado_empleado = Empleado.crear(
    nombres=nombres,
    apellidos=apellidos,
    documento_identidad=documento,
    sexo=sexo,
    id_usuario=id_usuario,
    id_rol=id_rol,
    id_distrito=id_distrito,
    id_especialidad=id_especialidad,
    fecha_nacimiento=fecha_nacimiento
)

if 'error' in resultado_empleado:
    print(f"❌ ERROR al crear empleado: {resultado_empleado['error']}")
    # Limpiar: eliminar usuario creado
    Usuario.eliminar(id_usuario)
    exit(1)

id_empleado = resultado_empleado['id_empleado']
print(f"✓ Empleado creado con ID: {id_empleado}")

# Verificación final
print("\n" + "="*60)
print("VERIFICACIÓN FINAL")
print("="*60)

print("\n[Verificando en BD] Obteniendo usuario recién creado...")
usuario_verificado = Usuario.obtener_por_id(id_usuario)
if usuario_verificado:
    print(f"✓ Usuario encontrado en BD:")
    print(f"  - ID: {usuario_verificado['id_usuario']}")
    print(f"  - Correo: {usuario_verificado['correo']}")
    print(f"  - Teléfono: {usuario_verificado['telefono']}")
    print(f"  - Estado: {usuario_verificado['estado']}")
else:
    print("❌ Usuario NO encontrado en BD")

print("\n[Verificando en BD] Obteniendo empleado recién creado...")
empleado_verificado = Empleado.obtener_por_id(id_empleado)
if empleado_verificado:
    print(f"✓ Empleado encontrado en BD:")
    print(f"  - ID: {empleado_verificado['id_empleado']}")
    print(f"  - Nombres: {empleado_verificado['nombres']}")
    print(f"  - Apellidos: {empleado_verificado['apellidos']}")
    print(f"  - Documento: {empleado_verificado['documento_identidad']}")
    print(f"  - Sexo: {empleado_verificado['sexo']}")
    print(f"  - Fecha Nacimiento: {empleado_verificado['fecha_nacimiento']}")
    print(f"  - Estado: {empleado_verificado['estado']}")
    print(f"  - Rol: {empleado_verificado.get('rol', 'N/A')}")
    print(f"  - Distrito: {empleado_verificado.get('distrito', 'N/A')}")
else:
    print("❌ Empleado NO encontrado en BD")

print("\n" + "="*60)
print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
print("="*60)
print(f"\nCREDENCIALES DE PRUEBA:")
print(f"  Email: {email}")
print(f"  Password: {password}")
print("="*60)
