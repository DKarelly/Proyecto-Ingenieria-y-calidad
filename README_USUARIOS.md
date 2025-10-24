# Sistema de Usuarios - Clínica Unión

## 🚀 Instrucciones de Configuración

### 1. Crear la Base de Datos

Primero, crea la base de datos en MySQL/MariaDB:

```sql
CREATE DATABASE IF NOT EXISTS bdunion;
USE bdunion;
```

### 2. Ejecutar el Script de Tablas

Ejecuta el archivo `prueba.sql` para crear todas las tablas:

```bash
mysql -u root -p bdunion < prueba.sql
```

O desde phpMyAdmin, importa el archivo `prueba.sql`.

### 3. Insertar Datos Iniciales

Ejecuta el archivo `datos_iniciales.sql` para insertar departamentos, provincias, distritos, roles y especialidades:

```bash
mysql -u root -p bdunion < datos_iniciales.sql
```

### 4. Instalar Dependencias de Python

```bash
pip install flask pymysql werkzeug
```

### 5. Configurar la Conexión a la Base de Datos

Edita el archivo `bd.py` y ajusta los parámetros de conexión:

```python
def obtener_conexion():
    return pymysql.connect(
        host='localhost',
        port=3327,  # Cambia según tu configuración
        user='root',
        password='',  # Tu contraseña de MySQL
        db='bdunion',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
```

### 6. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 📋 Funcionalidades Implementadas

### En la Página Principal (home.html)

- ✅ **Registro de Pacientes**: Los usuarios pueden registrarse como pacientes desde el modal
- ✅ **Login**: Inicio de sesión con correo y contraseña
- ✅ **Sesión Persistente**: Se guarda la información del usuario en localStorage
- ✅ **Botón de Usuario Dinámico**: Muestra la inicial del nombre cuando está logueado
- ✅ **Menú Desplegable**: Al hacer hover sobre el botón de usuario, muestra opciones:
  - Ver Perfil
  - Gestionar Usuarios (solo empleados)
  - Cerrar Sesión

### Rutas API Disponibles

- `POST /usuarios/api/login` - Login de usuario
- `POST /usuarios/api/register` - Registro de nuevo paciente
- `GET /usuarios/api/usuarios` - Listar usuarios (solo empleados)
- `GET /usuarios/api/usuarios/<id>` - Obtener usuario por ID

### Rutas Web Disponibles

- `/usuarios/login` - Página de login
- `/usuarios/logout` - Cerrar sesión
- `/usuarios/perfil` - Ver perfil del usuario
- `/usuarios/listar` - Gestión de usuarios (solo empleados)
- `/usuarios/crear` - Crear nuevo usuario (solo empleados)
- `/usuarios/editar/<id>` - Editar usuario (solo empleados)
- `/usuarios/cambiar-contrasena` - Cambiar contraseña propia

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con `werkzeug.security`
- ✅ Validación de campos en backend
- ✅ Control de acceso basado en roles
- ✅ Sesiones seguras con Flask
- ✅ Protección contra duplicados (correo y documento únicos)

## 📝 Notas Importantes

1. **Secret Key**: Cambia el `secret_key` en `app.py` por una clave segura en producción
2. **Ubicación**: El registro de pacientes usa IDs por defecto (1) para departamento, provincia y distrito. Considera implementar selectores dinámicos en producción.
3. **Primera vez**: Para crear tu primer usuario administrador (empleado), necesitarás insertarlo manualmente en la base de datos o usar la ruta `/usuarios/crear` después de crear un empleado en la tabla EMPLEADO.

## 🧪 Prueba del Sistema

1. Abre `http://localhost:5000`
2. Haz clic en el icono de usuario (esquina superior derecha)
3. Selecciona "Regístrate"
4. Completa el formulario de registro
5. Inicia sesión con las credenciales creadas
6. El botón de usuario mostrará tu inicial y un menú desplegable

## 🛠️ Estructura de Archivos

```
Union/
├── app.py                          # Aplicación principal Flask
├── bd.py                           # Configuración de base de datos
├── prueba.sql                      # Script de creación de tablas
├── datos_iniciales.sql             # Datos iniciales
├── models/
│   └── usuario.py                  # Modelo de Usuario
├── routes/
│   └── usuarios.py                 # Controlador de usuarios
├── templates/
│   ├── home.html                   # Página principal con modals
│   └── usuarios/
│       ├── login.html              # Página de login standalone
│       ├── perfil.html             # Perfil del usuario
│       ├── listar.html             # Lista de usuarios
│       ├── crear.html              # Crear usuario
│       ├── editar.html             # Editar usuario
│       └── cambiar_contrasena.html # Cambiar contraseña
└── static/
    ├── css/
    │   └── estilos.css
    └── js/
        └── home.js                 # JavaScript con funcionalidad de login/registro
```

## 🐛 Solución de Problemas

### Error de conexión a la base de datos
- Verifica que MySQL/MariaDB esté corriendo
- Revisa el puerto en `bd.py` (3327 o 3306)
- Verifica usuario y contraseña

### Error "Base de datos no seleccionada"
- Asegúrate de haber ejecutado `datos_iniciales.sql`
- Verifica que la base de datos `bdunion` exista

### El botón de usuario no muestra el menú
- Abre la consola del navegador (F12) para ver errores
- Verifica que `home.js` se esté cargando correctamente
- Limpia la caché del navegador

### No se puede registrar
- Verifica que las tablas DEPARTAMENTO, PROVINCIA y DISTRITO tengan datos
- Revisa la consola de Flask para ver el error específico
