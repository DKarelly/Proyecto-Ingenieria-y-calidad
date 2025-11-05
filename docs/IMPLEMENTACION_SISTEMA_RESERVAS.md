# 🏥 SISTEMA INTEGRAL DE RESERVAS MÉDICAS - GUÍA DE IMPLEMENTACIÓN

## 📋 ÍNDICE
1. [Archivos Creados](#archivos-creados)
2. [Migraciones de Base de Datos](#migraciones)
3. [Modelos Python](#modelos)
4. [Rutas y APIs](#rutas)
5. [Vistas HTML](#vistas)
6. [Pasos de Implementación](#pasos)
7. [Características Implementadas](#características)

---

## 1. 📁 ARCHIVOS CREADOS

### Base de Datos
- ✅ `scripts/actualizar_esquema_reservas.sql` - Script completo de migración

### Modelos Python
- ✅ `models/operacion.py` - Modelo de Operaciones + Equipo Médico
- ✅ `models/examen_actualizado.py` - Modelo de Exámenes + Tipos + Detalles
- ✅ `models/reserva.py` - **ACTUALIZADO** con campos tipo_reserva y cita_origen_id

### Vistas HTML
- ✅ `templates/HistorialReservasUnificado.html` - Vista principal con filtros dinámicos

### Pendientes (a crear)
- ⏳ `templates/HistorialClinicoMejorado.html`
- ⏳ `templates/GestionOperaciones.html`
- ⏳ `templates/GestionExamenes.html`
- ⏳ APIs adicionales en `routes/reservas.py`

---

## 2. 🗄️ MIGRACIONES DE BASE DE DATOS

### Ejecutar Script de Migración

```bash
# Conectar a MySQL
mysql -u tu_usuario -p CLINICA < scripts/actualizar_esquema_reservas.sql
```

### Cambios Aplicados

#### Tabla RESERVA
```sql
- Nuevo campo: tipo_reserva ENUM('CITA_MEDICA', 'OPERACION', 'EXAMEN')
- Nuevo campo: cita_origen_id INT NULL (FK a RESERVA)
- Índices: idx_tipo_reserva, idx_cita_origen, idx_paciente_tipo
```

#### Tabla CITA
```sql
- Nuevo campo: tratamiento TEXT
```

#### Nueva Tabla: OPERACION
```sql
- Información completa de operaciones quirúrgicas
- Equipo médico, quirófano, tiempos, resultados
- Estados: PENDIENTE, CONFIRMADA, EN_CURSO, COMPLETADA, CANCELADA
```

#### Nueva Tabla: EQUIPO_MEDICO_OPERACION
```sql
- Gestión del equipo médico por operación
- Roles: CIRUJANO_PRINCIPAL, CIRUJANO_ASISTENTE, ANESTESIOLOGO, ENFERMERA, OTRO
```

#### Tabla EXAMEN (actualizada)
```sql
- tipo_examen ENUM('LABORATORIO', 'IMAGENOLOGIA', 'PATOLOGIA', 'CARDIOLOGIA', 'OTRO')
- indicaciones_especiales TEXT
- resultados_pdf VARCHAR(255)
- interpretacion_medica TEXT
- created_at, updated_at
```

#### Nueva Tabla: TIPO_EXAMEN
```sql
- Catálogo de tipos de exámenes
- 11 tipos predefinidos insertados
```

#### Nueva Tabla: EXAMEN_DETALLE
```sql
- Relación N:N entre EXAMEN y TIPO_EXAMEN
- Permite múltiples tipos por examen
```

#### Vistas Creadas
```sql
- v_historial_completo_paciente
- v_historial_clinico_paciente
```

#### Procedimientos y Triggers
```sql
- sp_estadisticas_paciente()
- tr_reserva_update (auditoría automática)
- Tabla AUDITORIA_RESERVAS
```

---

## 3. 🐍 MODELOS PYTHON

### models/operacion.py

```python
class Operacion:
    - crear(data)
    - obtener_por_id(id_operacion)
    - obtener_por_reserva(id_reserva)
    - obtener_por_paciente(id_paciente)
    - obtener_derivadas_de_cita(id_cita)
    - actualizar(id_operacion, data)
    - confirmar(id_operacion)
    - completar(id_operacion, data)
    - cancelar(id_operacion)
    - obtener_por_estado(estado)
    - obtener_por_fecha(fecha)

class EquipoMedicoOperacion:
    - agregar_miembro(id_operacion, id_empleado, rol)
    - obtener_equipo(id_operacion)
    - eliminar_miembro(id_equipo)
```

### models/examen_actualizado.py

```python
class ExamenMedico:
    - crear(data)
    - obtener_por_id(id_examen)
    - obtener_por_reserva(id_reserva)
    - obtener_por_paciente(id_paciente)
    - obtener_derivados_de_cita(id_cita)
    - actualizar(id_examen, data)
    - confirmar(id_examen)
    - registrar_resultados(id_examen, observaciones, interpretacion, pdf_path)
    - cancelar(id_examen)
    - obtener_por_estado(estado)
    - obtener_por_tipo(tipo_examen)

class TipoExamen:
    - obtener_todos()
    - obtener_por_categoria(categoria)
    - obtener_por_id(id_tipo_examen)
    - crear(data)

class ExamenDetalle:
    - agregar(id_examen, id_tipo_examen, observaciones)
    - obtener_por_examen(id_examen)
    - eliminar(id_detalle)
```

### models/reserva.py (ACTUALIZADO)

**Nuevos métodos agregados:**
```python
- crear() - ahora acepta tipo_reserva y cita_origen_id
- obtener_por_tipo(tipo_reserva, id_paciente)
- obtener_derivadas(id_cita_origen)
- obtener_historial_clinico(id_paciente)
- obtener_con_filtros(múltiples parámetros)
```

---

## 4. 🛣️ RUTAS Y APIs

### APIs a Crear en routes/reservas.py

```python
# ===== HISTORIAL CLÍNICO =====
@reservas_bp.route('/historial-clinico')
def historial_clinico():
    """Vista de historial clínico con diagnósticos"""
    
@reservas_bp.route('/api/historial-clinico/<int:id_paciente>')
def api_historial_clinico(id_paciente):
    """API: Citas completadas con diagnóstico"""

# ===== OPERACIONES =====
@reservas_bp.route('/operaciones')
def gestionar_operaciones():
    """Vista de gestión de operaciones"""

@reservas_bp.route('/api/operaciones/crear', methods=['POST'])
def api_crear_operacion():
    """Crear nueva operación (desde cita o directa)"""

@reservas_bp.route('/api/operaciones/<int:id_operacion>')
def api_detalle_operacion(id_operacion):
    """Detalle completo de operación"""

@reservas_bp.route('/api/operaciones/<int:id_operacion>/completar', methods=['POST'])
def api_completar_operacion(id_operacion):
    """Completar operación con resultados"""

# ===== EXÁMENES =====
@reservas_bp.route('/examenes')
def gestionar_examenes():
    """Vista de gestión de exámenes"""

@reservas_bp.route('/api/examenes/tipos')
def api_tipos_examen():
    """Catálogo de tipos de examen"""

@reservas_bp.route('/api/examenes/crear', methods=['POST'])
def api_crear_examen():
    """Crear nuevo examen (desde cita o directo)"""

@reservas_bp.route('/api/examenes/<int:id_examen>/resultados', methods=['POST'])
def api_registrar_resultados(id_examen):
    """Registrar resultados de examen"""

# ===== VINCULACIÓN =====
@reservas_bp.route('/api/reservas/<int:id_reserva>/derivadas')
def api_reservas_derivadas(id_reserva):
    """Obtener operaciones/exámenes derivados de una cita"""
```

---

## 5. 🎨 VISTAS HTML A CREAR

### ✅ COMPLETO: HistorialReservasUnificado.html
- ✅ Filtros dinámicos (tipo, estado, fechas)
- ✅ Cards con iconos por tipo
- ✅ Badges de color por estado
- ✅ Contador de resultados
- ✅ Modal de detalle
- ✅ Diseño responsive

### ⏳ PENDIENTE: HistorialClinicoMejorado.html

**Características:**
```html
<!-- Timeline de citas completadas -->
<!-- Botones: Solicitar Operación | Solicitar Examen -->
<!-- Mostrar derivadas: "Generó 2 operaciones y 1 examen" -->
<!-- Filtros: fecha, especialidad, profesional, palabras clave -->
<!-- Botón: Imprimir informe, Enviar por correo -->
```

### ⏳ PENDIENTE: GestionOperaciones.html

**Secciones:**
```html
<!-- Formulario creación (desde cita o directo) -->
<!-- Listado con filtros (estado, fecha, cirujano, tipo) -->
<!-- Vista calendario y lista -->
<!-- Acciones: Confirmar, Completar, Reprogramar, Cancelar -->
<!-- Gestión de equipo médico -->
<!-- Enlace a cita origen si existe -->
```

### ⏳ PENDIENTE: GestionExamenes.html

**Secciones:**
```html
<!-- Formulario creación (desde cita o directo) -->
<!-- Selector múltiple de tipos de examen -->
<!-- Listado agrupado por tipo -->
<!-- Acciones: Confirmar, Registrar resultados, Cancelar -->
<!-- Upload de PDF resultados -->
<!-- Interpretación médica -->
<!-- Enlace a cita origen si existe -->
```

---

## 6. 🚀 PASOS DE IMPLEMENTACIÓN

### PASO 1: Base de Datos ⚠️ CRÍTICO
```bash
# 1. Backup de BD actual
mysqldump -u usuario -p CLINICA > backup_antes_migracion.sql

# 2. Ejecutar migración
mysql -u usuario -p CLINICA < scripts/actualizar_esquema_reservas.sql

# 3. Verificar tablas creadas
mysql -u usuario -p CLINICA -e "SHOW TABLES;"
```

### PASO 2: Actualizar imports en routes/reservas.py
```python
# Agregar al inicio del archivo:
from models.operacion import Operacion, EquipoMedicoOperacion
from models.examen_actualizado import ExamenMedico, TipoExamen, ExamenDetalle
```

### PASO 3: Crear APIs pendientes
```python
# Copiar las definiciones de la sección "RUTAS Y APIs"
# Implementar en routes/reservas.py
```

### PASO 4: Crear vistas HTML pendientes
```html
<!-- Usar HistorialReservasUnificado.html como plantilla -->
<!-- Mantener diseño y estructura consistente -->
<!-- Usar Bootstrap 5 -->
<!-- Iconos: Font Awesome -->
```

### PASO 5: Actualizar navegación
```python
# En templates/header_admin.html o sidebar correspondiente
# Agregar enlaces:
- Historial Completo de Reservas
- Historial Clínico
- Gestionar Operaciones
- Gestionar Exámenes
```

### PASO 6: Testing
```python
# 1. Crear una cita médica
# 2. Completarla con diagnóstico
# 3. Desde el historial clínico, solicitar operación
# 4. Desde el historial clínico, solicitar examen
# 5. Verificar vinculación bidireccional
# 6. Filtrar por tipo en historial unificado
```

---

## 7. ✨ CARACTERÍSTICAS IMPLEMENTADAS

### ✅ Modelo de Datos
- [x] Campo tipo_reserva en RESERVA
- [x] Campo cita_origen_id para vinculación
- [x] Tabla OPERACION completa
- [x] Tabla EXAMEN mejorada
- [x] Catálogos de tipos
- [x] Auditoría automática
- [x] Vistas de consulta optimizadas

### ✅ Modelos Python
- [x] Operacion con todos los métodos
- [x] ExamenMedico con todos los métodos
- [x] Reserva actualizada con filtros
- [x] Gestión de equipo médico
- [x] Gestión de tipos de examen

### ✅ Frontend
- [x] Historial Unificado con filtros dinámicos
- [x] Diseño responsive
- [x] Iconos por tipo de reserva
- [x] Badges de color por estado
- [x] Modal de detalle

### ⏳ Pendiente
- [ ] Historial Clínico mejorado
- [ ] Gestión de Operaciones
- [ ] Gestión de Exámenes
- [ ] APIs de creación/actualización
- [ ] Integración con notificaciones
- [ ] Impresión de informes
- [ ] Envío por correo

---

## 8. 🎨 SISTEMA DE COLORES

### Estados
```css
PENDIENTE:   bg-warning   (🟡 Amarillo)
CONFIRMADA:  bg-info      (🔵 Azul)
COMPLETADA:  bg-success   (🟢 Verde)
CANCELADA:   bg-danger    (🔴 Rojo)
```

### Tipos
```css
CITA_MEDICA: 💙 #0dcaf0 (Azul claro) + 🩺
OPERACION:   💜 #6f42c1 (Púrpura)   + 🏥
EXAMEN:      🧡 #fd7e14 (Naranja)   + 🔬
```

---

## 9. 📊 FLUJO COMPLETO

```
1. Paciente agenda CITA_MEDICA
   ↓
2. Estado: PENDIENTE → CONFIRMADA
   ↓
3. Médico atiende y registra diagnóstico
   ↓
4. Estado: COMPLETADA (aparece en Historial Clínico)
   ↓
5. Desde detalle de cita:
   ├─→ [Solicitar Operación] → Crea RESERVA tipo OPERACION
   │   └─→ cita_origen_id = id_cita
   │   └─→ Aparece en Historial Unificado (filtro Operaciones)
   │
   └─→ [Solicitar Examen] → Crea RESERVA tipo EXAMEN
       └─→ cita_origen_id = id_cita
       └─→ Aparece en Historial Unificado (filtro Exámenes)
```

---

## 10. 🔒 REGLAS DE NEGOCIO

1. ✅ Solo citas COMPLETADAS con diagnóstico aparecen en Historial Clínico
2. ✅ Operaciones/Exámenes pueden o no tener cita_origen_id
3. ✅ Vinculación bidireccional visible en ambos sentidos
4. ✅ No permitir eliminar citas con derivadas (solo cancelar)
5. ⏳ Auditoría automática de cambios (trigger implementado)
6. ⏳ Notificaciones cuando operación/examen es confirmado
7. ✅ Filtros dinámicos sin botón buscar

---

## 11. 📝 QUERIES ÚTILES

### Historial Completo
```sql
SELECT * FROM v_historial_completo_paciente 
WHERE id_paciente = ? 
ORDER BY fecha_cita DESC;
```

### Historial Clínico
```sql
SELECT * FROM v_historial_clinico_paciente 
WHERE id_paciente = ? 
ORDER BY fecha_cita DESC;
```

### Reservas Derivadas
```sql
SELECT * FROM RESERVA 
WHERE cita_origen_id = ?;
```

### Estadísticas
```sql
CALL sp_estadisticas_paciente(?);
```

---

## 12. 🐛 TROUBLESHOOTING

### Error: "Unknown column 'tipo_reserva'"
```sql
-- Verificar que la migración se ejecutó:
DESC RESERVA;
-- Debe mostrar el campo tipo_reserva
```

### Error: "Table 'OPERACION' doesn't exist"
```sql
-- Ejecutar solo la creación de tablas:
CREATE TABLE OPERACION (...); -- Ver script completo
```

### Importar modelos falla
```python
# Verificar rutas relativas:
from models.operacion import Operacion
from models.examen_actualizado import ExamenMedico
```

---

## 13. 📚 RECURSOS

- **Bootstrap 5**: https://getbootstrap.com/docs/5.3/
- **Font Awesome**: https://fontawesome.com/icons
- **MySQL Docs**: https://dev.mysql.com/doc/
- **Flask Blueprints**: https://flask.palletsprojects.com/

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

1. ✅ Ejecutar script de migración de BD
2. ⏳ Crear vista HistorialClinicoMejorado.html
3. ⏳ Crear API `/api/solicitar-operacion`
4. ⏳ Crear API `/api/solicitar-examen`
5. ⏳ Crear vista GestionOperaciones.html
6. ⏳ Crear vista GestionExamenes.html
7. ⏳ Integrar con sistema de notificaciones
8. ⏳ Testing end-to-end

---

**Creado por**: GitHub Copilot  
**Fecha**: 2025-11-05  
**Versión**: 1.0
