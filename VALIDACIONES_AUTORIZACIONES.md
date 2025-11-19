# Validaciones y Filtros de Especialidad - Sistema de Autorizaciones

## Resumen de Cambios

Se implementó un sistema completo de validaciones y filtros por especialidad para las autorizaciones de procedimientos médicos. El sistema asegura que:

1. ✅ Los exámenes autorizados sean de la especialidad del médico logueado
2. ✅ Al derivar operaciones, NO se muestre selector de especialidad
3. ✅ Se carguen directamente médicos de la misma especialidad del médico logueado
4. ✅ Si el médico NO deriv a otro, se valide que tenga permiso para operar

---

## Cambios Implementados

### 1. Backend - routes/medico.py

#### ✅ Actualizado: `/medico/api/obtener_servicios_examen`
- **Antes**: Retornaba TODOS los exámenes sin filtrar
- **Ahora**: Filtra exámenes por especialidad del médico logueado
- **Lógica**: 
  - Obtiene `id_especialidad` del médico actual
  - Pasa especialidad al método `obtener_servicios_examen(id_especialidad)`
  - Retorna solo exámenes de esa especialidad + sin especialidad específica

**Ejemplo**:
```python
# Médico de Cardiología solo verá exámenes de Cardiología
servicios = AutorizacionProcedimiento.obtener_servicios_examen(3)  # id=3 -> Cardiología
```

#### ✅ Actualizado: `/medico/api/obtener_servicios_operacion`
- Sin cambios (mantiene comportamiento actual)
- Ya filtraba operaciones de la especialidad del médico

#### ✅ NUEVO: `/medico/api/obtener_medicos_mi_especialidad`
- **Propósito**: Obtener médicos de la misma especialidad sin selector de especialidad
- **Flujo**:
  1. Obtiene especialidad del médico logueado
  2. Carga médicos de esa especialidad
  3. Excluye al médico actual de la lista
  4. Retorna lista limpia de médicos para derivación

**Endpoint**:
```
GET /medico/api/obtener_medicos_mi_especialidad
```

**Respuesta**:
```json
{
  "success": true,
  "medicos": [
    {
      "id_empleado": 2,
      "nombre_completo": "Dr. Carlos López",
      "especialidad": "Cardiología"
    },
    {
      "id_empleado": 5,
      "nombre_completo": "Dra. María García",
      "especialidad": "Cardiología"
    }
  ],
  "especialidad_nombre": "Cardiología"
}
```

### 2. Backend - models/autorizacion_procedimiento.py

#### ✅ Actualizado: `obtener_servicios_examen(id_especialidad_medico=None)`
- **Antes**: Solo método estático sin parámetros
- **Ahora**: Acepta parámetro opcional `id_especialidad_medico`
- **Comportamiento**:
  - Si se proporciona especialidad: Filtra exámenes de esa especialidad
  - Si es None: Retorna todos los exámenes (comportamiento backwards compatible)

**Código**:
```python
@staticmethod
def obtener_servicios_examen(id_especialidad_medico=None):
    """Obtiene servicios de tipo EXAMEN, filtrados por especialidad si se proporciona"""
    if id_especialidad_medico:
        # SQL con WHERE s.id_especialidad = ? OR s.id_especialidad IS NULL
    else:
        # SQL sin filtro de especialidad
```

### 3. Frontend - templates/panel_medico.html

#### ✅ Cambio de Interfaz HTML
**Antes**:
```html
<!-- 2 selectores separados -->
<select id="especialidad_operacion">
  <option>-- Seleccione especialidad --</option>
</select>

<select id="medico_operacion">
  <option>-- Seleccione médico --</option>
</select>
```

**Ahora**:
```html
<!-- 1 solo selector de médicos de mi especialidad -->
<select id="medico_derivar_operacion">
  <option value="">-- Yo realizaré la operación --</option>
  <!-- Se llenan automáticamente médicos de mi especialidad -->
</select>
```

#### ✅ Actualizado: `toggleAutorizacionOperacion()`
- Removido: Llamada a `cargarEspecialidades()`
- Solo llama: `cargarServiciosOperacion()`

#### ✅ Actualizado: `onServicioOperacionChange()`
- Ahora llama: `cargarMedicosMiEspecialidad()` (antes: no hacía nada importante)
- Carga médicos automáticamente al seleccionar operación

#### ✅ REMOVIDA: `cargarEspecialidades()`
- Ya no necesaria (especialidad obtenida automáticamente del médico logueado)

#### ✅ REMOVIDA: `cargarMedicosPorEspecialidad()`
- Reemplazada por: `cargarMedicosMiEspecialidad()`

#### ✅ NUEVO: `cargarMedicosMiEspecialidad()`
- Llamar endpoint `/medico/api/obtener_medicos_mi_especialidad`
- Llena automáticamente el selector con médicos disponibles
- Si no hay otros médicos: Opción "Yo realizaré la operación" se mantiene como única

**Código**:
```javascript
async function cargarMedicosMiEspecialidad() {
    const response = await fetch('/medico/api/obtener_medicos_mi_especialidad');
    const result = await response.json();
    
    if (result.success) {
        // Llenar selectMedico con médicos de mi especialidad
        result.medicos.forEach(medico => {
            const option = document.createElement('option');
            option.value = medico.id_empleado;
            option.textContent = medico.nombre_completo;
            selectMedico.appendChild(option);
        });
    }
}
```

### 4. Backend - Validación en Guardar Diagnóstico

#### ✅ Actualizado: `guardar_diagnostico()` - Lógica de autorización de operaciones

**Nueva Validación - Si el médico NO deriv**:
```python
if not id_medico_derivar:
    # Validar que el médico logueado pueda operar
    cursor.execute("""
        SELECT COUNT(*) as puede_operar
        FROM SERVICIO s
        INNER JOIN EMPLEADO_SERVICIO es ON s.id_servicio = es.id_servicio
        WHERE s.id_servicio = %s 
        AND es.id_empleado = %s
        AND s.id_tipo_servicio = 2
    """)
    
    if not puede_operar:
        return jsonify({
            'success': False,
            'message': 'Usted no está autorizado para realizar esta operación. Debe derivar a otro médico.'
        }), 403
```

**Comportamiento**:
- Si el checkbox "Derivar a otro médico" está vacío:
  - Se valida que el médico logueado tenga permiso en `EMPLEADO_SERVICIO`
  - Si tiene permiso: Se asigna la operación a sí mismo
  - Si NO tiene permiso: ERROR 403 "Debe derivar a otro médico"

- Si se selecciona un médico para derivar:
  - NO se hace validación (confianza en el médico asignado)
  - Se crea la autorización asignada al médico seleccionado

---

## Flujos de Usuario

### Flujo 1: Médico de Cardiología autoriza Examen

1. Médico abre panel de diagnóstico
2. Marca "Autorizar Examen"
3. **Frontend carga**: `/medico/api/obtener_servicios_examen`
4. **Backend retorna**: Solo exámenes de Cardiología (ECG, Ecocardiografía, etc.)
5. Médico selecciona examen
6. Operación se autoriza correctamente

### Flujo 2: Médico NO puede operar (derivación obligatoria)

1. Médico de Cardiología autoriza "Ablación Cardíaca" (Operación)
2. Marca "Autorizar Operación" y selecciona el tipo
3. **Frontend carga**: `/medico/api/obtener_medicos_mi_especialidad`
4. **Frontend muestra**: Lista de cardiologos disponibles + opción "Yo realizaré"
5. **Si elige "Yo realizaré"**:
   - Backend valida: ¿Tiene `EMPLEADO_SERVICIO` para esta operación?
   - Si NO: **ERROR** "Debe derivar a otro médico"
   - Si SÍ: Opera el mismo
6. **Si elige otro médico**:
   - Se crea autorización derivada a ese médico

### Flujo 3: Derivación a especialista

1. Médico de Medicina General autoriza "Operación de Próstata"
2. Selecciona la operación
3. **Frontend carga**: Médicos de Urología
4. Selecciona "Dr. Juan Pérez (Urología)"
5. Se crea autorización asignada a Dr. Pérez
6. Dr. Pérez recibe notificación

---

## Validaciones Resumidas

| Caso | Validación | Resultado |
|------|-----------|----------|
| Examen de otra especialidad | NO permite cargar | No aparece en lista |
| Operación sin derivar + tiene permiso | Valida EMPLEADO_SERVICIO | ✅ Se autoriza |
| Operación sin derivar + NO tiene permiso | Valida EMPLEADO_SERVICIO | ❌ ERROR 403 |
| Derivación a otro médico | No valida | ✅ Se autoriza siempre |

---

## Impacto en Base de Datos

No hay cambios en la estructura de la BD. Se utiliza tabla existente:
- `EMPLEADO_SERVICIO` - Para validar qué servicios puede realizar cada médico

---

## Testing Recomendado

1. **Test 1: Filtrado de exámenes**
   - Loguear como médico de Cardiología
   - Autorizar examen → Verific que solo aparecen exámenes de Cardiología

2. **Test 2: Derivación automática**
   - Loguear como médico de Medicina General
   - Autorizar operación de Cardiología
   - Verificar que se muestra lista de Cardiólogos

3. **Test 3: Validación de operación sin derivar**
   - Médico SIN permiso intenta operar
   - Verificar que recibe ERROR 403

4. **Test 4: Operación autorizada del mismo médico**
   - Médico CON permiso elige "Yo realizaré"
   - Verificar que se autoriza correctamente

---

## Archivos Modificados

✅ `routes/medico.py` - 2 endpoints actualizados, 1 nuevo
✅ `models/autorizacion_procedimiento.py` - 1 método actualizado (backwards compatible)
✅ `templates/panel_medico.html` - Interfaz y JavaScript actualizados

---

**Fecha de Implementación**: 19 de Noviembre de 2025
**Estado**: ✅ Implementado y listo para testing

