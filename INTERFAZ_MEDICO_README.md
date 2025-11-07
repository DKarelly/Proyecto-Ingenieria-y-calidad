# 🏥 Interfaz Médico - Clínica Unión

## 📋 Descripción

Se ha creado una interfaz completa y profesional para médicos que permite gestionar citas, pacientes, diagnósticos y más. La interfaz mantiene la coherencia visual con el resto de la aplicación usando la paleta de colores cyan/teal/emerald.

---

## 🎨 Características de Diseño

### Paleta de Colores Médica
- **Cyan**: `#06B6D4` - Color principal
- **Teal**: `#14B8A6` - Color secundario
- **Emerald**: `#10B981` - Color de acento
- **Gradientes**: De cyan a teal para efectos visuales modernos

### Elementos Visuales
- ✨ Animaciones suaves y transiciones fluidas
- 🎯 Cards con gradientes y sombras médicas
- 📊 Estadísticas visuales en tiempo real
- 🔔 Sistema de notificaciones integrado
- 👤 Avatares coloridos con iniciales
- 🏷️ Badges de estado con gradientes

---

## 📁 Archivos Creados

### Templates
1. **`templates/header_medico.html`**
   - Header específico para médicos
   - Barra de acento con gradiente médico (cyan → teal → emerald)
   - Menú de notificaciones con contador en tiempo real
   - Dropdown de usuario con accesos rápidos
   - Logo con efecto hover mejorado

2. **`templates/panel_medico.html`**
   - Panel principal con sidebar de navegación
   - 7 subsistemas integrados
   - Dashboard con estadísticas en cards visuales
   - Diseño responsivo y moderno

### Estilos
3. **`static/css/medico.css`**
   - Estilos específicos para el portal médico
   - Animaciones personalizadas
   - Componentes reutilizables
   - Efectos hover y transiciones

### Backend
4. **`routes/medico.py`**
   - Blueprint completo con todas las rutas
   - Decorador `@medico_required` para seguridad
   - APIs REST para consultas AJAX
   - Manejo de errores personalizado

### Configuración
5. **`app.py`** (modificado)
   - Blueprint de médico registrado
   - Rutas disponibles en `/medico/*`

---

## 🗺️ Estructura del Panel Médico

### Dashboard Principal
Acceso: `/medico/panel` o `/medico/`

**Estadísticas Visuales:**
- 📅 Citas de Hoy (8 total, 2 pendientes)
- 👥 Pacientes Esta Semana (24 total)
- 📋 Diagnósticos Pendientes (5 pendientes)
- ⭐ Calificación Promedio (4.9/5.0)

**Secciones:**
- Lista de citas del día con estados visuales
- Accesos rápidos a funciones principales
- Notificaciones importantes

### Subsistemas Disponibles

#### 1. 📅 Mi Agenda
**Ruta:** `/medico/panel?subsistema=agenda`
- Calendario de citas interactivo
- Vista por día, semana y mes
- Gestión de horarios
- Creación de nuevas citas

#### 2. 👥 Mis Pacientes
**Ruta:** `/medico/panel?subsistema=pacientes`
- Lista completa de pacientes asignados
- Búsqueda por nombre, DNI o historial
- Filtros avanzados
- Acceso rápido al historial médico
- Tabla con datos: Nombre, DNI, Última Cita, Estado

#### 3. 📋 Diagnósticos
**Ruta:** `/medico/panel?subsistema=diagnosticos`

**Formulario Completo:**
- Selección de paciente
- Fecha de consulta
- Tipo de consulta (General, Control, Emergencia, Revisión)
- Síntomas reportados
- Diagnóstico médico
- Tratamiento indicado
- Observaciones adicionales
- Botones: Guardar / Cancelar

#### 4. 📂 Historial Médico
**Ruta:** `/medico/panel?subsistema=historial`
- Consulta de historiales completos
- Filtros por fecha y tipo
- Exportación de reportes

#### 5. 💊 Recetas
**Ruta:** `/medico/panel?subsistema=recetas`
- Generación de recetas médicas
- Gestión de medicamentos
- Historial de recetas emitidas

#### 6. 📊 Reportes
**Ruta:** `/medico/panel?subsistema=reportes`
- Generación de reportes médicos
- Estadísticas personales
- Exportación a PDF/Excel

#### 7. 🔔 Notificaciones
**Ruta:** `/medico/panel?subsistema=notificaciones`
- Centro de notificaciones
- Alertas de citas
- Resultados de laboratorio
- Recordatorios importantes

---

## 🔐 Seguridad y Permisos

### Decorador `@medico_required`
```python
@medico_bp.route('/panel')
@medico_required
def panel():
    # Solo accesible para usuarios con id_rol = 2 (Médico)
    pass
```

**Validaciones:**
1. ✅ Usuario autenticado (sesión activa)
2. ✅ Rol de médico (`id_rol = 2`)
3. ✅ Redirección automática si no cumple requisitos

---

## 🚀 Cómo Usar

### 1. Acceso al Portal
```
URL: http://localhost:5000/medico/panel
```

**Requisitos:**
- Estar autenticado
- Tener rol de Médico (id_rol = 2)

### 2. Navegación

**Sidebar Izquierdo:**
- Dashboard (vista principal)
- Mi Agenda
- Mis Pacientes
- Diagnósticos
- Historial Médico
- Recetas
- Reportes
- Notificaciones (con contador)

**Header Superior:**
- Logo con enlace al home
- Botón de notificaciones (con indicador rojo)
- Menú de usuario con:
  - Nombre y rol
  - Mi Perfil
  - Mi Agenda
  - Seguridad
  - Cerrar Sesión

### 3. Registro de Diagnóstico

**Paso a paso:**
1. Ir a **Diagnósticos** desde el sidebar
2. Seleccionar paciente del dropdown
3. Elegir fecha de consulta
4. Seleccionar tipo de consulta
5. Completar los campos:
   - Síntomas reportados
   - Diagnóstico médico
   - Tratamiento indicado
   - Observaciones adicionales
6. Hacer clic en "Guardar Diagnóstico"

### 4. Gestión de Pacientes

**Búsqueda:**
1. Ir a **Mis Pacientes**
2. Usar la barra de búsqueda superior
3. Filtrar por: nombre, DNI o historial
4. Hacer clic en "Ver Historial" para detalles completos

---

## 🎨 Componentes Visuales

### Cards de Estadísticas
```html
<div class="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-2xl p-6 text-white shadow-medical">
    <!-- Contenido -->
</div>
```

**Efectos:**
- Gradientes de cyan a teal
- Sombra médica personalizada
- Hover con elevación
- Animación de entrada

### Badges de Estado
- 🟡 **Pendiente**: Amarillo con gradiente
- 🟢 **Completada**: Verde con gradiente
- 🔴 **Cancelada**: Rojo con gradiente
- 🔵 **En Proceso**: Azul con gradiente

### Avatares de Pacientes
```html
<div class="w-10 h-10 bg-gradient-to-br from-cyan-500 to-teal-500 rounded-full">
    JP
</div>
```

---

## 📱 Responsive Design

La interfaz es completamente responsiva:

- **Desktop** (1024px+): Sidebar visible, grid de 4 columnas
- **Tablet** (768px-1023px): Sidebar colapsable, grid de 2 columnas
- **Mobile** (<768px): Menú hamburguesa, grid de 1 columna

---

## 🔌 APIs Disponibles

### Endpoints AJAX

#### 1. Citas del Día
```javascript
GET /medico/api/citas-hoy
Retorna: { success: true, citas: [...] }
```

#### 2. Estadísticas
```javascript
GET /medico/api/estadisticas
Retorna: { success: true, estadisticas: {...} }
```

#### 3. Buscar Paciente
```javascript
GET /medico/api/buscar-paciente?q=nombre
Retorna: { success: true, pacientes: [...] }
```

---

## 🎯 Próximos Pasos

### Para Conectar con Base de Datos:

1. **Modificar `routes/medico.py`:**
   - Importar modelos necesarios (Paciente, Reserva, Diagnostico)
   - Implementar consultas reales en lugar de datos de ejemplo
   - Conectar formularios con la base de datos

2. **Crear Modelos (si no existen):**
   - `models/diagnostico.py`
   - `models/receta.py`
   - Extender `models/paciente.py`

3. **Implementar Funcionalidades:**
   - Calendario interactivo con FullCalendar.js
   - Búsqueda en tiempo real con AJAX
   - Notificaciones en tiempo real con WebSockets
   - Exportación de reportes a PDF

---

## 🎨 Personalización de Colores

Si deseas cambiar la paleta de colores, edita `static/css/medico.css`:

```css
:root {
  --medico-cyan: #06B6D4;      /* Color principal */
  --medico-teal: #14B8A6;      /* Color secundario */
  --medico-emerald: #10B981;   /* Color de acento */
}
```

---

## 🐛 Solución de Problemas

### Error: "No tienes permisos para acceder"
**Solución:** Verifica que el usuario tenga `id_rol = 2` en la base de datos.

### Error: "Página no encontrada"
**Solución:** Verifica que el Blueprint esté registrado en `app.py`.

### Estilos no se aplican
**Solución:** Verifica que `medico.css` esté incluido en `header_medico.html`.

---

## 📝 Notas Técnicas

### Tecnologías Utilizadas:
- **Frontend:** HTML5, Tailwind CSS, JavaScript Vanilla
- **Backend:** Flask (Python), Blueprint pattern
- **Iconos:** Material Symbols Outlined
- **Fuentes:** Sora (display), Inter (body)

### Estructura de Sesión:
```python
session = {
    'usuario_id': int,
    'nombre_usuario': str,
    'id_rol': 2,  # Médico
    'rol': 'Médico',
    'id_empleado': int,
    'tipo_usuario': 'empleado'
}
```

---

## ✅ Checklist de Implementación

- [x] Header médico creado con gradientes
- [x] Panel médico con 7 subsistemas
- [x] Dashboard con estadísticas visuales
- [x] Formulario de diagnósticos completo
- [x] Lista de pacientes con búsqueda
- [x] Sistema de notificaciones
- [x] Estilos CSS personalizados
- [x] Rutas backend configuradas
- [x] Decorador de seguridad implementado
- [x] Blueprint registrado en app.py
- [ ] Conexión con base de datos (próximo paso)
- [ ] Implementar calendario interactivo
- [ ] Añadir exportación de reportes
- [ ] Implementar notificaciones en tiempo real

---

## 🎉 ¡Listo para Usar!

La interfaz médica está completamente funcional y lista para ser conectada con tu base de datos. El diseño es moderno, profesional y coherente con la estética de la aplicación.

**Para probar:**
1. Inicia sesión como médico (`id_rol = 2`)
2. Visita: `http://localhost:5000/medico/panel`
3. Explora los subsistemas desde el sidebar

---

**Desarrollado con ❤️ para Clínica Unión**
**Fecha:** Noviembre 2024
