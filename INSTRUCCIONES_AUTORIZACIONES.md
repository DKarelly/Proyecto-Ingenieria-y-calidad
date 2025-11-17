# Instrucciones para Implementar el Sistema de Autorizaciones

Este documento describe cómo implementar el sistema de autorizaciones de exámenes y operaciones en la Clínica Unión.

## 1. Aplicar Cambios en la Base de Datos

### Opción A: Usando MySQL Workbench (Recomendado)

1. Abre MySQL Workbench
2. Conecta a tu base de datos `bd_calidad`
3. Abre el archivo `scripts/crear_tablas_autorizaciones.sql`
4. Ejecuta el script completo (Ctrl+Shift+Enter o botón "Execute")
5. Verifica que las tablas se crearon correctamente:
   ```sql
   SHOW TABLES LIKE 'AUTORIZACION_%';
   ```

### Opción B: Desde la línea de comandos

```bash
mysql -u tu_usuario -p bd_calidad < scripts/crear_tablas_autorizaciones.sql
```

## 2. Características Implementadas

### Para Médicos (Panel Médico)

1. **Diagnóstico con Autorizaciones**: Al completar un diagnóstico, el médico puede:
   - Autorizar uno o más exámenes del catálogo
   - Autorizar una operación
   - Derivar la operación a otro médico de la misma especialidad
   - Agregar observaciones específicas para cada autorización

2. **Selección mediante Combo Box**:
   - Los exámenes se filtran automáticamente (solo tipo_servicio = 4)
   - Las operaciones se filtran por especialidad del médico
   - Los médicos para derivación se filtran por especialidad y disponibilidad

### Para Pacientes

1. **Vista de Autorizaciones**: Nueva página en `/paciente/autorizaciones`
   - Muestra todos los exámenes autorizados pendientes
   - Muestra todas las operaciones autorizadas pendientes
   - Incluye información del médico que autorizó
   - Muestra observaciones médicas

2. **Botones de Acción**:
   - "Programar Examen": Redirige a formulario de reserva de examen
   - "Programar Operación": Redirige a formulario de reserva de operación
   - Los botones solo aparecen si hay autorizaciones pendientes

## 3. Flujo de Trabajo

```
1. Paciente asiste a consulta médica
   ↓
2. Médico realiza diagnóstico y:
   - Completa el diagnóstico
   - Opcionalmente autoriza examen(es)
   - Opcionalmente autoriza operación
   - Puede derivar operación a colega
   ↓
3. Paciente accede a /paciente/autorizaciones
   ↓
4. Paciente ve sus autorizaciones pendientes
   ↓
5. Paciente programa el examen u operación
   ↓
6. Sistema actualiza estado de autorización a "Programado"
```

## 4. Tablas Creadas

### AUTORIZACION_EXAMEN
- Almacena autorizaciones de exámenes
- Vincula: cita, paciente, médico, servicio de examen
- Estados: Pendiente, Programado, Completado, Cancelado

### AUTORIZACION_OPERACION
- Almacena autorizaciones de operaciones
- Vincula: cita, paciente, médico autorizador, médico asignado, servicio de operación
- Campo `es_derivacion`: indica si fue derivado a otro médico
- Estados: Pendiente, Programado, Completado, Cancelado

## 5. APIs Disponibles

### Para Médicos
- `GET /medico/api/servicios-examenes`: Lista de servicios de exámenes
- `GET /medico/api/servicios-operaciones`: Lista de servicios de operaciones (filtrado por especialidad)
- `GET /medico/api/medicos-misma-especialidad`: Lista de médicos para derivación
- `POST /medico/diagnosticos/guardar`: Guarda diagnóstico con autorizaciones

### Para Pacientes
- `GET /paciente/autorizaciones`: Vista de autorizaciones
- `GET /paciente/api/autorizaciones-pendientes`: API JSON con autorizaciones pendientes

## 6. Compatibilidad

✅ MySQL 8.0+
✅ MySQL Workbench
✅ MariaDB 10.2+

El script SQL usa sintaxis estándar de MySQL compatible con Workbench.

## 7. Validaciones Implementadas

- Filtrado automático de servicios por tipo (exámenes vs operaciones)
- Filtrado de médicos por especialidad para derivaciones
- Validación de estados mediante CHECK constraints
- Foreign keys para integridad referencial
- Índices para optimizar consultas frecuentes

## 8. Mejoras Futuras (Opcionales)

- Notificaciones automáticas al paciente cuando recibe autorizaciones
- Recordatorios para programar exámenes/operaciones autorizados
- Dashboard con estadísticas de autorizaciones por médico
- Exportar autorizaciones a PDF para el paciente
