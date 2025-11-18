# Sistema de Autorizaciones de Procedimientos Médicos

## Descripción General

Este documento describe la funcionalidad implementada que permite a los médicos autorizar a pacientes para realizar exámenes médicos u operaciones durante el registro de un diagnóstico. El sistema incluye derivación a otros especialistas cuando sea necesario.

---

## Tabla de Contenidos

1. [Características Principales](#características-principales)
2. [Modelo de Datos](#modelo-de-datos)
3. [Flujo de Trabajo](#flujo-de-trabajo)
4. [Interfaz de Usuario](#interfaz-de-usuario)
5. [API y Backend](#api-y-backend)
6. [Casos de Uso](#casos-de-uso)
7. [Configuración e Instalación](#configuración-e-instalación)

---

## Características Principales

### 0. Diagnóstico Simple (Sin Autorizaciones) ⭐ **MÁS COMÚN**
- **El médico puede registrar solo el diagnóstico sin autorizar nada**
- La mayoría de consultas NO requieren exámenes ni operaciones
- El diagnóstico se guarda normalmente
- La cita se marca como "Completada"
- No se crean registros de autorización
- Los botones del paciente permanecen deshabilitados (comportamiento correcto)

### 1. Autorización de Exámenes (Opcional)
- El médico **puede opcionalmente** autorizar exámenes médicos durante el diagnóstico
- Se selecciona tipo de examen desde combobox de servicios activos
- Solo servicios de tipo EXAMEN están disponibles
- La autorización se crea automáticamente

### 2. Autorización de Operaciones (Opcional)
- El médico **puede opcionalmente** autorizar operaciones quirúrgicas
- Se selecciona tipo de operación desde combobox de servicios activos
- Solo servicios de tipo OPERACION están disponibles
- Puede realizarla él mismo o derivar a otro especialista
- Se selecciona especialidad requerida (opcional)
- Se asigna médico específico de esa especialidad (opcional)

### 3. Derivación Inteligente
- Si se selecciona una especialidad, el sistema lista solo médicos de esa especialidad
- El médico puede elegir a quién derivar o dejar sin asignar
- Si no requiere especialidad específica, la puede realizar él mismo

### 4. Control de Acceso para Pacientes
- Los botones de "Agendar Examen" y "Agendar Operación" están **deshabilitados** por defecto
- Solo se habilitan cuando el médico ha otorgado la autorización correspondiente
- El paciente puede ver sus autorizaciones pendientes
- **Comportamiento correcto**: Si no hay autorización, los botones permanecen deshabilitados

---

## Modelo de Datos

### Tabla: `AUTORIZACION_PROCEDIMIENTO`

```sql
CREATE TABLE `AUTORIZACION_PROCEDIMIENTO` (
  `id_autorizacion` INT NOT NULL AUTO_INCREMENT,
  `id_cita` INT NOT NULL,
  `id_paciente` INT NOT NULL,
  `id_medico_autoriza` INT NOT NULL,
  `tipo_procedimiento` ENUM('EXAMEN', 'OPERACION') NOT NULL,
  `id_servicio` INT NOT NULL,
  `id_especialidad_requerida` INT NULL,
  `id_medico_asignado` INT NULL,
  `fecha_autorizacion` DATETIME NOT NULL,
  `fecha_actualizacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id_autorizacion`),
  FOREIGN KEY (`id_cita`) REFERENCES `CITA` (`id_cita`) ON DELETE CASCADE,
  FOREIGN KEY (`id_paciente`) REFERENCES `PACIENTE` (`id_paciente`) ON DELETE CASCADE,
  FOREIGN KEY (`id_medico_autoriza`) REFERENCES `EMPLEADO` (`id_empleado`) ON DELETE RESTRICT,
  FOREIGN KEY (`id_medico_asignado`) REFERENCES `EMPLEADO` (`id_empleado`) ON DELETE SET NULL,
  FOREIGN KEY (`id_especialidad_requerida`) REFERENCES `ESPECIALIDAD` (`id_especialidad`) ON DELETE SET NULL,
  FOREIGN KEY (`id_servicio`) REFERENCES `SERVICIO` (`id_servicio`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Cambios principales**:
- ❌ Eliminado campo `estado` (no se necesita)
- ❌ Eliminados campos `descripcion`, `indicaciones`, `prioridad`
- ✅ Agregado campo `id_servicio` (referencia al servicio específico)
- ✅ Se usa el nombre y detalles del servicio en lugar de descripción manual

### Relaciones

```
CITA (1) -----> (N) AUTORIZACION_PROCEDIMIENTO
PACIENTE (1) --> (N) AUTORIZACION_PROCEDIMIENTO
EMPLEADO (Autoriza) (1) --> (N) AUTORIZACION_PROCEDIMIENTO
EMPLEADO (Asignado) (1) --> (N) AUTORIZACION_PROCEDIMIENTO
ESPECIALIDAD (1) --> (N) AUTORIZACION_PROCEDIMIENTO
```

---

## Flujo de Trabajo

### Escenario 1: Autorización de Examen

```
1. Médico atiende paciente y registra diagnóstico
2. Médico marca checkbox "Autorizar Examen Médico"
3. Completa:
   - Tipo de Examen (combobox con servicios de tipo EXAMEN)
4. Guarda diagnóstico
5. Sistema crea registro en AUTORIZACION_PROCEDIMIENTO
   - tipo_procedimiento = 'EXAMEN'
   - id_servicio = [servicio seleccionado]
6. Paciente puede ahora agendar el examen
```

### Escenario 2: Operación Sin Derivación

```
1. Médico marca checkbox "Autorizar Operación"
2. Completa:
   - Tipo de Operación (combobox con servicios de tipo OPERACION)
3. NO selecciona especialidad (puede hacerla él mismo)
4. Guarda diagnóstico
5. Sistema asigna automáticamente al médico actual
6. Paciente puede agendar operación con ese médico
```

### Escenario 3: Operación Con Derivación

```
1. Médico marca checkbox "Autorizar Operación"
2. Completa:
   - Tipo de Operación (combobox con servicios)
3. Selecciona especialidad requerida (ej: Cardiología)
4. Sistema carga lista de médicos cardiólogos activos
5. Médico selecciona cirujano específico (opcional)
6. Guarda diagnóstico
7. Sistema crea autorización:
   - id_servicio = [operación seleccionada]
   - id_especialidad_requerida = Cardiología
   - id_medico_asignado = [Cirujano seleccionado o NULL]
8. Paciente solo puede agendar con médicos de Cardiología
```

---

## Interfaz de Usuario

### Panel Médico - Formulario de Diagnóstico

El formulario incluye nueva sección **"Autorizar Procedimientos"**:

#### Autorizar Examen Médico
- ☑ Checkbox para activar
- Combobox: Tipo de Examen (*) - Cargado con servicios activos de tipo EXAMEN

#### Autorizar Operación
- ☑ Checkbox para activar
- Combobox: Tipo de Operación (*) - Cargado con servicios activos de tipo OPERACION
- Combobox: Especialidad Requerida (opcional) - Se muestra si se selecciona operación
- Combobox: Asignar Médico (se muestra solo si hay especialidad seleccionada)

### Interacción

```javascript
// Al marcar checkbox de examen
toggleAutorizacionExamen() {
  // Muestra/oculta campos del examen
  // Carga servicios de tipo EXAMEN
}

// Al marcar checkbox de operación
toggleAutorizacionOperacion() {
  // Muestra/oculta campos de operación
  // Carga servicios de tipo OPERACION
  // Carga especialidades
}

// Al seleccionar operación
onServicioOperacionChange() {
  // Muestra selector de especialidad
}

// Al seleccionar especialidad
cargarMedicosPorEspecialidad() {
  // Carga médicos con esa especialidad via API
  // Muestra selector de médico
}
```

### Vista del Paciente

**Antes de autorización:**
```html
<button disabled class="opacity-50 cursor-not-allowed">
  Agendar Examen
  <span class="text-xs">Requiere autorización médica</span>
</button>
```

**Después de autorización:**
```html
<button class="bg-cyan-500 hover:bg-cyan-600">
  Agendar Examen
</button>
```

---

## API y Backend

### Endpoints Implementados

#### 1. Guardar Diagnóstico con Autorizaciones
```python
@medico_bp.route('/diagnosticos/guardar', methods=['POST'])
@medico_required
def guardar_diagnostico():
    # Datos del formulario
    id_cita = request.form.get('id_cita')
    id_paciente = request.form.get('id_paciente')
    diagnostico = request.form.get('diagnostico')
    observaciones = request.form.get('observaciones', '')
    
    # Flags de autorización
    autorizar_examen = request.form.get('autorizar_examen') == 'true'
    autorizar_operacion = request.form.get('autorizar_operacion') == 'true'
    
    # IDs de servicios seleccionados
    id_servicio_examen = request.form.get('id_servicio_examen')
    id_servicio_operacion = request.form.get('id_servicio_operacion')
    
    # Guardar diagnóstico
    # ...
    
    # Crear autorizaciones si se solicitaron
    if autorizar_examen and id_servicio_examen:
        AutorizacionProcedimiento.crear({
            'id_cita': id_cita,
            'id_paciente': id_paciente,
            'id_medico_autoriza': id_empleado,
            'tipo_procedimiento': 'EXAMEN',
            'id_servicio': int(id_servicio_examen),
        })
    
    if autorizar_operacion and id_servicio_operacion:
        AutorizacionProcedimiento.crear({
            'id_cita': id_cita,
            'id_paciente': id_paciente,
            'id_medico_autoriza': id_empleado,
            'tipo_procedimiento': 'OPERACION',
            'id_servicio': int(id_servicio_operacion),
            'id_especialidad_requerida': id_especialidad,
            'id_medico_asignado': id_medico,
        })
```

#### 2. Obtener Servicios de Examen
```python
@medico_bp.route('/api/obtener_servicios_examen', methods=['GET'])
@medico_required
def obtener_servicios_examen():
    # Retorna lista de servicios de tipo EXAMEN (id_tipo_servicio = 4)
    return jsonify({
        'success': True,
        'servicios': [...]  # [{id_servicio, nombre, especialidad, ...}]
    })
```

#### 3. Obtener Servicios de Operación
```python
@medico_bp.route('/api/obtener_servicios_operacion', methods=['GET'])
@medico_required
def obtener_servicios_operacion():
    # Retorna servicios de tipo OPERACION (id_tipo_servicio = 2)
    # Filtra por especialidad del médico actual para mostrar opciones relevantes
    return jsonify({
        'success': True,
        'servicios': [...]  # [{id_servicio, nombre, especialidad, ...}]
    })
```

#### 4. Obtener Especialidades
```python
@medico_bp.route('/api/obtener_especialidades', methods=['GET'])
@medico_required
def obtener_especialidades():
    # Retorna lista de especialidades activas
    return jsonify({
        'success': True,
        'especialidades': [...]
    })
```

#### 5. Obtener Médicos por Especialidad
```python
@medico_bp.route('/api/obtener_medicos_por_especialidad/<int:id_especialidad>')
@medico_required
def obtener_medicos_por_especialidad(id_especialidad):
    # Retorna médicos activos con esa especialidad
    # Solo médicos con id_rol = 2 (médico) y estado = 'activo'
    return jsonify({
        'success': True,
        'medicos': [...]
    })
```

---

## Casos de Uso

### Caso de Uso 0: Solo Diagnóstico (Sin Autorizaciones)
**Actor**: Cualquier Médico  
**Objetivo**: Registrar diagnóstico sin necesidad de procedimientos adicionales

**Flujo**:
1. Médico registra diagnóstico: "Resfriado común"
2. Observaciones: "Reposo, hidratación, paracetamol si hay fiebre"
3. **NO marca ningún checkbox** de autorización
4. Guarda diagnóstico
5. Cita se marca como Completada
6. ✅ Paciente NO necesita exámenes ni operaciones
7. ✅ No se crean autorizaciones
8. ✅ Botones de examen/operación permanecen deshabilitados (correcto)

**Nota importante**: Las autorizaciones son **totalmente opcionales**. La mayoría de las consultas médicas solo requieren diagnóstico y tratamiento, sin necesidad de procedimientos adicionales.

---

### Caso de Uso 1: Examen de Laboratorio
**Actor**: Médico General  
**Objetivo**: Autorizar hemograma completo

**Flujo**:
1. Médico registra diagnóstico: "Anemia leve"
2. Marca "Autorizar Examen Médico"
3. Selecciona tipo: "Hemograma completo" (del combobox)
4. Guarda
5. Paciente recibe autorización y puede agendar en laboratorio

---

### Caso de Uso 2: Operación de Cataratas
**Actor**: Oftalmólogo  
**Objetivo**: Programar cirugía de cataratas

**Flujo**:
1. Médico oftalmólogo registra diagnóstico: "Catarata bilateral"
2. Marca "Autorizar Operación"
3. Selecciona tipo: "Facoemulsificación con implante de lente" (del combobox)
4. NO selecciona especialidad (puede hacerla él mismo)
5. Guarda
6. Paciente puede agendar operación con ese oftalmólogo

---

### Caso de Uso 3: Derivación a Cardiología
**Actor**: Médico General  
**Objetivo**: Derivar para cirugía cardiovascular

**Flujo**:
1. Médico general registra diagnóstico: "Estenosis aórtica severa"
2. Marca "Autorizar Operación"
3. Selecciona tipo: "Reemplazo valvular aórtico" (del combobox)
4. Especialidad: Cardiología
5. Sistema muestra lista de cardiólogos:
   - Dr. Juan Pérez (Cardiólogo)
   - Dra. María González (Cardióloga)
6. Selecciona: Dr. Juan Pérez
7. Guarda
8. Paciente puede agendar operación solo con cardiólogos

---

### Caso de Uso 4: Operación Sin Médico Asignado
**Actor**: Médico General  
**Objetivo**: Autorizar apendicectomía sin asignar cirujano específico

**Flujo**:
1. Médico registra diagnóstico: "Apendicitis aguda"
2. Marca "Autorizar Operación"
3. Selecciona tipo: "Apendicectomía laparoscópica" (del combobox)
4. Especialidad: Cirugía General
5. NO selecciona médico específico
6. Sistema deja `id_medico_asignado` = NULL
7. Administración puede asignar cualquier cirujano general disponible
8. Paciente ve que necesita operación pero aún sin cirujano asignado

---

## Configuración e Instalación

### 1. Crear Tabla en Base de Datos

```bash
# Ejecutar script SQL
mysql -u usuario -p nombre_base_datos < scripts/crear_tabla_autorizacion_procedimiento.sql
```

### 2. Importar Modelo en Python

El modelo ya está importado en `models/__init__.py`:

```python
from .autorizacion_procedimiento import AutorizacionProcedimiento
```

### 3. Verificar Rutas

Las rutas ya están registradas en `routes/medico.py`:

```python
from models.autorizacion_procedimiento import AutorizacionProcedimiento
```

### 4. Actualizar Frontend

El template `panel_medico.html` ya incluye:
- Formulario de autorizaciones
- JavaScript para interacción
- Funciones de carga de datos

---

## Validaciones Implementadas

### Backend
1. **Campos requeridos**:
   - `id_cita`, `id_paciente`, `id_medico_autoriza` son obligatorios
   - `descripcion` es obligatoria
   - `tipo_procedimiento` debe ser 'EXAMEN' o 'OPERACION'

2. **Constraint en BD**:
   - Si es EXAMEN, `id_especialidad_requerida` debe ser NULL
   - Si es OPERACION, puede tener especialidad o no

3. **Asignación automática**:
   - Si no hay especialidad y no hay médico asignado → se asigna al médico actual
   - Si hay especialidad pero no médico asignado → queda NULL para asignación posterior

### Frontend
1. **Habilitación condicional**:
   - Campos de examen solo visibles si checkbox marcado
   - Campos de operación solo visibles si checkbox marcado
   - Selector de médico solo visible si se selecciona especialidad

2. **Validación de formulario**:
   - Descripción es requerida si checkbox está marcado
   - Se previene submit sin datos necesarios

---

## Próximos Pasos (No Implementado)

Ver documento: [CASOS_NO_CONTEMPLADOS_AUTORIZACIONES.md](./CASOS_NO_CONTEMPLADOS_AUTORIZACIONES.md)

### Críticos
- [ ] Vencimiento de autorizaciones
- [ ] Consumo de autorizaciones (enlace con RESERVA)
- [ ] Notificaciones al paciente
- [ ] Validación de especialidad del médico asignado

### Importante
- [ ] Dashboard de autorizaciones para médico
- [ ] Historial de autorizaciones para paciente
- [ ] Flujo de aprobación administrativa
- [ ] Modificación de autorizaciones

---

## Soporte y Contacto

Para dudas o problemas con esta funcionalidad:
- Revisar documentación técnica en `models/autorizacion_procedimiento.py`
- Consultar casos no contemplados en `docs/CASOS_NO_CONTEMPLADOS_AUTORIZACIONES.md`
- Verificar logs en el servidor para errores de backend

---

*Documentación generada: 13 de noviembre de 2025*  
*Versión del sistema: 1.0*  
*Autor: Equipo de Desarrollo*
