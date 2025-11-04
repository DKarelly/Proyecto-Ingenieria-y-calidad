# Documentación del Módulo de Reportes

## Descripción General
El módulo de reportes permite generar, consultar, y gestionar diferentes tipos de reportes del sistema de gestión clínica, incluyendo reportes por categoría, reportes de actividad (auditoría) y reportes de ocupación de recursos. Cada reporte puede incluir archivos adjuntos que se pueden descargar posteriormente.

---

## Estructura de Base de Datos

### Tablas Principales

#### REPORTE
Almacena los reportes generados en el sistema.

```sql
CREATE TABLE REPORTE (
  id_reporte INT PRIMARY KEY AUTO_INCREMENT,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  nombre VARCHAR(255) NOT NULL,
  tipo VARCHAR(100),
  descripcion TEXT,
  contenido_json JSON,
  estado VARCHAR(50) DEFAULT 'Pendiente',
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  id_categoria INT,
  id_empleado INT,
  id_servicio INT,
  id_recurso INT
);
```

#### REPORTE_ARCHIVO
Almacena los archivos adjuntos a los reportes.

```sql
CREATE TABLE REPORTE_ARCHIVO (
  id_archivo INT PRIMARY KEY AUTO_INCREMENT,
  id_reporte INT NOT NULL,
  nombre_archivo VARCHAR(255) NOT NULL,
  ruta_archivo VARCHAR(500) NOT NULL,
  tipo_archivo VARCHAR(100) NOT NULL,
  tamano_bytes BIGINT NOT NULL,
  fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_reporte) REFERENCES REPORTE(id_reporte) ON DELETE CASCADE
);
```

#### CATEGORIA
Categorías para clasificar los reportes.

```sql
CREATE TABLE CATEGORIA (
  id_categoria INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  estado VARCHAR(20) DEFAULT 'Activo'
);
```

#### AUDITORIA
Registros de auditoría del sistema.

```sql
CREATE TABLE AUDITORIA (
  id_auditoria INT PRIMARY KEY AUTO_INCREMENT,
  accion VARCHAR(255) NOT NULL,
  modulo VARCHAR(100),
  tipo_evento VARCHAR(100),
  descripcion TEXT,
  id_empleado INT,
  fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(45)
);
```

---

## Funcionalidades Implementadas

### 1. Consultar Reportes por Categoría

**Ruta:** `/reportes/consultar-por-categoria`

#### Características:
- Listar todos los reportes del sistema
- Filtrar por categoría, tipo, y rango de fechas
- Búsqueda en tiempo real por código, nombre o tipo
- Ver detalles completos de cada reporte
- Descargar archivos adjuntos
- Eliminar reportes (con confirmación)
- Generar nuevos reportes con archivos adjuntos
- Exportar reportes a PDF/Excel

#### Endpoints API Utilizados:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/reportes/buscar` | Buscar reportes con filtros |
| GET | `/api/reportes/<id>` | Obtener detalle de un reporte |
| POST | `/api/reportes/crear` | Crear nuevo reporte |
| POST | `/api/reportes/<id>/subir-archivo` | Subir archivo adjunto |
| GET | `/api/reportes/descargar-archivo/<id>` | Descargar archivo |
| DELETE | `/api/reportes/eliminar-archivo/<id>` | Eliminar archivo |
| DELETE | `/api/reportes/<id>/eliminar` | Eliminar reporte |
| GET | `/api/reportes/categorias` | Obtener lista de categorías |

#### Archivos Involucrados:
- **Backend:** `routes/reportes.py`
- **Frontend:** `templates/consultar_por_categoria.html`
- **JavaScript:** `static/js/reportes.js`
- **Modelos:** `models/reporte.py`

---

### 2. Generar Reporte de Actividad (Auditoría)

**Ruta:** `/reportes/generar-reporte-actividad`

#### Características:
- Visualizar registros de auditoría del sistema
- Filtrar por empleado, rango de fechas y tipo de evento
- Ver detalles de cada actividad
- Consultar archivos adjuntos asociados
- Descargar archivos de auditoría
- Generar nuevos registros de auditoría manualmente
- Exportar datos a PDF

#### Endpoints API Utilizados:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auditoria` | Obtener registros de auditoría con filtros |
| GET | `/api/auditoria/<id>` | Obtener detalle de un registro |
| DELETE | `/api/auditoria/<id>` | Eliminar registro de auditoría |
| GET | `/api/auditoria/<id>/archivos` | Obtener archivos asociados |
| GET | `/api/auditoria/descargar-archivo/<id>` | Descargar archivo |
| POST | `/api/auditoria/generar` | Crear registro de auditoría manual |
| GET | `/api/auditoria/exportar` | Exportar auditoría a PDF |
| GET | `/api/empleados` | Obtener lista de empleados |
| GET | `/api/modulos` | Obtener módulos del sistema |
| GET | `/api/tipos-evento` | Obtener tipos de eventos |

#### Archivos Involucrados:
- **Backend:** `routes/reportes.py`
- **Frontend:** `templates/generar_reporte_actividad.html`
- **JavaScript:** `static/js/reporte_actividad.js`

---

### 3. Generar Reporte de Ocupación de Recursos

**Ruta:** `/reportes/ocupacion-recursos`

#### Características:
- Visualizar recursos físicos y su nivel de ocupación
- Filtrar por tipo de recurso
- Búsqueda por nombre de recurso
- Ver detalle de uso de cada recurso
- Consultar historial de operaciones
- Ver qué empleados han utilizado el recurso
- Generar reportes con archivos adjuntos
- Exportar datos a PDF

#### Endpoints API Utilizados:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/recursos-ocupacion` | Obtener recursos con ocupación |
| GET | `/api/recursos-por-tipo/<id>` | Obtener recursos por tipo |
| GET | `/api/recursos/<id>/detalle` | Obtener detalle de uso de recurso |
| GET | `/api/recursos/<id>/archivos` | Obtener archivos del recurso |
| GET | `/api/recursos/descargar-archivo/<id>` | Descargar archivo |
| POST | `/api/recursos-ocupacion/generar` | Generar reporte de ocupación |
| GET | `/api/recursos-ocupacion/exportar` | Exportar a PDF |
| GET | `/api/tipos-recursos` | Obtener tipos de recursos |

#### Archivos Involucrados:
- **Backend:** `routes/reportes.py`
- **Frontend:** `templates/generar_ocupacion_recursos.html`
- **JavaScript:** `static/js/reporte_recursos.js`

---

## Gestión de Archivos Adjuntos

### Características Generales:
1. **Subida de Archivos:**
   - Validación de tipo de archivo
   - Límite de tamaño: 10MB
   - Nombres únicos con timestamp
   - Almacenamiento en carpeta `uploads/reportes/`

2. **Formatos Permitidos:**
   - Documentos: PDF, DOC, DOCX
   - Hojas de cálculo: XLS, XLSX
   - Imágenes: PNG, JPG, JPEG, GIF

3. **Descarga de Archivos:**
   - Descarga directa desde el navegador
   - Indicador visual de progreso
   - Abre en nueva pestaña

4. **Visualización:**
   - Iconos diferenciados por tipo de archivo
   - Información de tamaño y fecha de subida
   - Lista de archivos adjuntos en modal de detalle

5. **Seguridad:**
   - Solo usuarios autenticados (empleados) pueden acceder
   - Validación de sesión en todos los endpoints
   - Archivos eliminados físicamente al eliminar reporte (CASCADE)

### Código de Ejemplo - Subir Archivo:

```javascript
// Configurar input de archivo
const inputArchivo = document.getElementById('archivo');
const formData = new FormData();
formData.append('archivo', inputArchivo.files[0]);

// Subir archivo
const response = await fetch(`/reportes/api/reportes/${idReporte}/subir-archivo`, {
    method: 'POST',
    body: formData
});

const result = await response.json();
if (result.success) {
    console.log('Archivo subido:', result.archivo);
}
```

### Código de Ejemplo - Descargar Archivo:

```javascript
function descargarArchivo(idArchivo) {
    window.open(`/reportes/api/reportes/descargar-archivo/${idArchivo}`, '_blank');
}
```

---

## Modelos de Datos (Python)

### Clase Reporte (`models/reporte.py`)

#### Métodos Principales:

```python
# Crear nuevo reporte
Reporte.crear(
    id_categoria=1,
    tipo='Reporte Mensual',
    descripcion='Descripción del reporte',
    contenido_json=None,
    id_empleado=5
)

# Obtener todos los reportes
reportes = Reporte.obtener_todos()

# Obtener por ID
reporte = Reporte.obtener_por_id(id_reporte)

# Buscar con filtros
reportes = Reporte.buscar_reportes({
    'busqueda': 'término',
    'id_categoria': 1,
    'fecha_inicio': '2025-01-01',
    'fecha_fin': '2025-12-31'
})

# Agregar archivo adjunto
Reporte.agregar_archivo(
    id_reporte=10,
    nombre_archivo='documento.pdf',
    ruta_archivo='uploads/reportes/20251103_documento.pdf',
    tipo_archivo='application/pdf',
    tamano_bytes=1024000
)

# Obtener archivos adjuntos
archivos = Reporte.obtener_archivos(id_reporte)

# Eliminar archivo
Reporte.eliminar_archivo(id_archivo)

# Eliminar reporte
Reporte.eliminar(id_reporte)
```

---

## Interfaz de Usuario

### Componentes Principales:

1. **Tabla de Listado:**
   - Paginación
   - Columnas ordenables
   - Badges de estado
   - Botones de acción (ver, editar, eliminar)

2. **Filtros de Búsqueda:**
   - Input de búsqueda en tiempo real
   - Selectores de categoría y tipo
   - Selectores de rango de fechas
   - Botones de generar y exportar

3. **Modal de Detalle:**
   - Información completa del reporte
   - Lista de archivos adjuntos
   - Vista previa de archivos (imágenes, PDFs)
   - Botones de descarga
   - Botones de exportación y eliminación

4. **Modal de Generar Reporte:**
   - Formulario con categoría y descripción
   - Input de archivo con arrastrar y soltar
   - Barra de progreso de subida
   - Validación de formulario

5. **Toasts y Notificaciones:**
   - Mensajes de éxito (verde)
   - Mensajes de error (rojo)
   - Indicadores de carga
   - Confirmaciones de eliminación

---

## Seguridad

### Autenticación y Autorización:
- Todos los endpoints requieren sesión activa
- Solo usuarios tipo "empleado" pueden acceder
- Validación en backend con decoradores Flask

```python
@reportes_bp.route("/api/reportes/<int:id_reporte>", methods=["GET"])
def api_detalle_reporte(id_reporte):
    if "usuario_id" not in session or session.get("tipo_usuario") != "empleado":
        return jsonify({"error": "No autorizado"}), 401
    # ... resto del código
```

### Validación de Archivos:
- Extensiones permitidas definidas en constante
- Validación de tamaño máximo
- Nombres de archivo sanitizados con `secure_filename`
- Almacenamiento en carpeta segura

```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

---

## Flujos de Trabajo

### Flujo: Crear Reporte con Archivo Adjunto

1. Usuario hace clic en "Generar Reporte"
2. Se abre modal con formulario
3. Usuario selecciona categoría
4. Usuario escribe descripción
5. Usuario selecciona archivo (opcional)
6. Usuario hace clic en "Guardar"
7. Sistema valida datos
8. Sistema crea registro en tabla REPORTE
9. Sistema guarda archivo físicamente (si existe)
10. Sistema crea registro en tabla REPORTE_ARCHIVO
11. Sistema muestra mensaje de éxito
12. Sistema recarga lista de reportes

### Flujo: Descargar Archivo de Reporte

1. Usuario hace clic en reporte para ver detalle
2. Sistema carga información y archivos adjuntos
3. Se muestra modal con lista de archivos
4. Usuario hace clic en botón de descarga
5. Sistema abre archivo en nueva pestaña
6. Navegador descarga el archivo

### Flujo: Consultar Auditoría

1. Usuario accede a "Reporte de Actividad"
2. Sistema carga registros de auditoría
3. Usuario aplica filtros (empleado, fechas, tipo)
4. Sistema actualiza tabla con resultados
5. Usuario hace clic en "Ver detalle"
6. Sistema muestra información completa del registro
7. Usuario puede descargar archivos asociados

---

## Configuración

### Variables de Configuración (`routes/reportes.py`):

```python
UPLOAD_FOLDER = 'uploads/reportes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
```

### Estructura de Carpetas:

```
Proyecto-Ingenieria-y-calidad/
├── uploads/
│   └── reportes/           # Archivos adjuntos de reportes
│       └── 20251103_archivo.pdf
├── static/
│   ├── css/
│   │   └── estilos.css    # Estilos del módulo
│   └── js/
│       ├── reportes.js     # JavaScript para categorías
│       ├── reporte_actividad.js   # JavaScript para auditoría
│       └── reporte_recursos.js    # JavaScript para recursos
├── templates/
│   ├── consultar_por_categoria.html
│   ├── generar_reporte_actividad.html
│   └── generar_ocupacion_recursos.html
├── routes/
│   └── reportes.py        # Endpoints del módulo
└── models/
    └── reporte.py         # Modelo de datos
```

---

## Pruebas y Debugging

### Logs en Consola:

Los archivos JavaScript incluyen logs detallados para debugging:

```javascript
console.log('[API RECURSOS-OCUPACION] Iniciando endpoint...');
console.log('[DETALLE] Cargando detalle del recurso:', idRecurso);
console.log('Actividades recibidas:', actividades);
```

### Manejo de Errores:

Todos los endpoints incluyen manejo de errores con try-catch:

```python
try:
    # Código de la función
    return jsonify({"success": True, "data": data})
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500
```

---

## Próximas Mejoras

### Funcionalidades Pendientes:

1. **Exportación a PDF/Excel:** Implementar generación real de documentos
2. **Vista Previa Mejorada:** Previsualizar PDFs e imágenes en modal
3. **Compresión de Archivos:** Reducir tamaño de archivos grandes
4. **Versionamiento:** Mantener historial de cambios en reportes
5. **Notificaciones:** Alertas cuando se genere un nuevo reporte
6. **Permisos Granulares:** Roles específicos para crear/editar/eliminar
7. **Dashboard:** Gráficos y estadísticas de reportes generados
8. **Búsqueda Avanzada:** Filtros adicionales y búsqueda por contenido JSON

---

## Contacto y Soporte

Para preguntas o problemas relacionados con el módulo de reportes, contactar al equipo de desarrollo del proyecto de Ingeniería y Calidad de Software - USAT.

**Última actualización:** 03 de noviembre de 2025
