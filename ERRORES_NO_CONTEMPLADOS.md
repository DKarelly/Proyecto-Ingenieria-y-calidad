# Errores No Contemplados en la Aplicación

Este documento describe posibles errores y casos no contemplados que podrían afectar el funcionamiento de la aplicación de gestión clínica.

---

## 🔴 1. GESTIÓN DE SESIONES Y AUTENTICACIÓN

### 1.1 Sesión Expirada sin Notificación
- **Problema**: Si una sesión expira mientras el usuario está utilizando la aplicación, no hay un manejo explícito del error.
- **Impacto**: El usuario podría intentar realizar acciones y recibir errores genéricos en lugar de ser redirigido al login.
- **Solución Recomendada**: Implementar middleware para detectar sesiones expiradas y redirigir automáticamente con un mensaje apropiado.

### 1.2 Login Concurrente desde Múltiples Dispositivos
- **Problema**: No hay control sobre el inicio de sesión simultáneo desde diferentes dispositivos o navegadores.
- **Impacto**: Podría causar inconsistencias en la sesión o comportamientos inesperados.
- **Solución Recomendada**: Implementar tokens de sesión únicos o política de "última sesión activa".

### 1.3 Validación de Email en Recuperación de Contraseña
- **Problema**: El sistema muestra el código en consola para desarrollo, pero no valida si el email de destino es válido.
- **Impacto**: Los usuarios podrían no recibir códigos de recuperación si su email está mal configurado.
- **Solución Recomendada**: Validar formato y existencia del dominio del email antes de enviar.

### 1.4 Código de Recuperación Sin Límite de Intentos
- **Problema**: No hay límite de intentos para validar códigos de recuperación.
- **Impacto**: Vulnerable a ataques de fuerza bruta.
- **Solución Recomendada**: Limitar a 3-5 intentos antes de invalidar el código.

---

## 🔴 2. GESTIÓN DE BASE DE DATOS

### 2.1 Pool de Conexiones sin Manejo de Reconexión
- **Problema**: Si la conexión a la base de datos se pierde, el pool podría no reconectar automáticamente.
- **Impacto**: Errores en todas las operaciones hasta reiniciar la aplicación.
- **Solución Recomendada**: Implementar `ping(reconnect=True)` en todas las obtenciones de conexión del pool.

### 2.2 Transacciones sin Rollback Completo
- **Problema**: Algunos endpoints tienen try-except pero no garantizan rollback en todos los casos de error.
- **Impacto**: Datos inconsistentes en la base de datos (ej: reserva creada pero programación no actualizada).
- **Solución Recomendada**: Envolver todas las operaciones de escritura en bloques try-finally con rollback explícito.

### 2.3 Deadlocks en Operaciones Concurrentes
- **Problema**: Operaciones como crear reservas o actualizar stock de medicamentos podrían generar deadlocks.
- **Impacto**: Errores aleatorios cuando múltiples usuarios realizan acciones simultáneas.
- **Solución Recomendada**: Implementar bloqueos optimistas (SELECT FOR UPDATE) y retry logic.

### 2.4 Falta de Índices en Consultas Frecuentes
- **Problema**: Consultas como búsqueda de horarios disponibles o filtrado de reservas podrían ser lentas sin índices.
- **Impacto**: Degradación del rendimiento con muchos usuarios.
- **Solución Recomendada**: Crear índices en columnas frecuentemente consultadas (fecha, id_empleado, estado, etc.).

### 2.5 Inyección SQL en Endpoints API
- **Problema**: Aunque se usan placeholders, algunos endpoints concatenan strings en consultas SQL.
- **Impacto**: Vulnerable a ataques de inyección SQL.
- **Solución Recomendada**: Revisar todos los queries y garantizar uso de parámetros preparados.

---

## 🔴 3. VALIDACIÓN DE DATOS

### 3.1 Validación de Edad sin Control de Fecha Futura
- **Problema**: En `editar_perfil`, se valida edad mínima (18 años) pero no se valida fecha futura.
- **Impacto**: Un usuario podría ingresar fechas futuras y causar errores de cálculo.
- **Solución Recomendada**: Validar que `fecha_nacimiento <= fecha_actual - 18 años`.

### 3.2 DNI Duplicado en Registro
- **Problema**: No hay validación explícita de DNI único antes de crear un paciente/empleado.
- **Impacto**: Posibles registros duplicados o errores de integridad.
- **Solución Recomendada**: Validar unicidad del DNI antes de insertar.

### 3.3 Validación de Formato de Teléfono
- **Problema**: No hay validación de formato de teléfono (solo se acepta como string).
- **Impacto**: Teléfonos inválidos almacenados en la base de datos.
- **Solución Recomendada**: Validar formato internacional (+XX XXXXXXXXX) o nacional.

### 3.4 Validación de Stock Negativo en Farmacia
- **Problema**: Aunque hay verificación, no hay validación de cantidades negativas al registrar ingresos.
- **Impacto**: Posible corrupción de datos de inventario.
- **Solución Recomendada**: Validar que cantidad > 0 en todos los endpoints de farmacia.

### 3.5 Fechas de Vencimiento Pasadas
- **Problema**: No hay validación que impida ingresar medicamentos con fecha de vencimiento ya pasada.
- **Impacto**: Inventario con datos incorrectos desde el inicio.
- **Solución Recomendada**: Validar que `fecha_vencimiento > fecha_actual` al registrar ingreso.

---

## 🔴 4. GESTIÓN DE RESERVAS Y HORARIOS

### 4.1 Reservas Duplicadas en el Mismo Horario
- **Problema**: No hay validación para evitar múltiples reservas en la misma programación.
- **Impacto**: Dos pacientes podrían tener cita en el mismo horario.
- **Solución Recomendada**: Implementar constraint UNIQUE en (id_programacion) en RESERVA o validar antes de insertar.

### 4.2 Actualización de Horarios Vencidos con Race Condition
- **Problema**: La función `actualizar_horarios_vencidos()` usa timeout corto pero podría fallar con alta concurrencia.
- **Impacto**: Horarios no actualizados o deadlocks en la base de datos.
- **Solución Recomendada**: Implementar como job programado (cron) en lugar de ejecución bajo demanda.

### 4.3 Cancelación de Reserva sin Notificación al Médico
- **Problema**: Al cancelar una reserva, solo se notifica al paciente, no al médico.
- **Impacto**: Médicos no saben cuando un paciente cancela su cita.
- **Solución Recomendada**: Agregar notificación al empleado (médico) al cancelar.

### 4.4 Reprogramación sin Límite de Veces
- **Problema**: Se valida máximo 2 reprogramaciones, pero no hay control en el frontend.
- **Impacto**: Usuarios podrían intentar reprogramar más veces y recibir errores confusos.
- **Solución Recomendada**: Deshabilitar botón de reprogramación si ya se alcanzó el límite.

### 4.5 Programaciones sin Validación de Conflictos de Horario
- **Problema**: No hay validación para evitar que un médico tenga dos programaciones superpuestas.
- **Impacto**: Conflictos de agenda para médicos.
- **Solución Recomendada**: Validar que no existan programaciones superpuestas al crear.

### 4.6 Reservas en Fechas Pasadas
- **Problema**: No hay validación explícita para evitar crear reservas en fechas/horas pasadas.
- **Impacto**: Reservas inválidas creadas por error.
- **Solución Recomendada**: Validar `fecha >= fecha_actual AND hora >= hora_actual` al crear reserva.

---

## 🔴 5. GESTIÓN DE FARMACIA

### 5.1 Entrega de Medicamentos sin Validación de ID Paciente
- **Problema**: El endpoint acepta 'undefined' como id_paciente en algunos casos.
- **Impacto**: Entregas registradas sin paciente válido.
- **Solución Recomendada**: Validar estrictamente que id_paciente sea un entero válido.

### 5.2 Stock Insuficiente sin Bloqueo Atómico
- **Problema**: Aunque hay verificación de stock, dos entregas simultáneas podrían causar stock negativo.
- **Impacto**: Inventario inconsistente.
- **Solución Recomendada**: Usar SELECT FOR UPDATE en todas las operaciones de stock.

### 5.3 Medicamentos Vencidos sin Alertas Proactivas
- **Problema**: Solo se muestran medicamentos por vencer, pero no hay sistema de alertas automáticas.
- **Impacto**: Medicamentos vencidos podrían no ser retirados a tiempo.
- **Solución Recomendada**: Implementar notificaciones automáticas 30, 15 y 7 días antes del vencimiento.

### 5.4 Historial de Entregas sin Auditoría
- **Problema**: No hay registro de quién modificó o eliminó entregas.
- **Impacto**: Falta de trazabilidad en operaciones críticas.
- **Solución Recomendada**: Agregar tabla de auditoría con timestamp y id_usuario.

---

## 🔴 6. NOTIFICACIONES

### 6.1 Notificaciones sin Cola de Procesamiento
- **Problema**: Las notificaciones se crean sincrónicamente en la misma transacción.
- **Impacto**: Si falla la creación de notificación, podría fallar toda la operación.
- **Solución Recomendada**: Implementar cola de notificaciones asíncrona (Redis/Celery).

### 6.2 Recordatorios sin Verificación de Envío
- **Problema**: Los recordatorios se programan pero no hay verificación de que se enviaron correctamente.
- **Impacto**: Pacientes podrían no recibir recordatorios importantes.
- **Solución Recomendada**: Implementar tabla de log de notificaciones enviadas con estado.

### 6.3 Notificaciones sin Límite de Cantidad
- **Problema**: No hay límite de notificaciones almacenadas por usuario.
- **Impacto**: Tabla de notificaciones podría crecer indefinidamente.
- **Solución Recomendada**: Implementar límite (ej: últimas 100) o auto-eliminación después de 90 días.

---

## 🔴 7. MANEJO DE ARCHIVOS Y UPLOADS

### 7.1 Fotos de Perfil sin Validación de Tipo
- **Problema**: No hay validación de tipo de archivo en uploads de fotos de perfil.
- **Impacto**: Usuarios podrían subir archivos maliciosos o de tipo incorrecto.
- **Solución Recomendada**: Validar extensión y MIME type (solo jpg, png, webp).

### 7.2 Uploads sin Límite de Tamaño
- **Problema**: No hay límite de tamaño de archivo explícito.
- **Impacto**: Archivos muy grandes podrían saturar el servidor.
- **Solución Recomendada**: Configurar `MAX_CONTENT_LENGTH` en Flask (ej: 5MB).

### 7.3 Nombres de Archivo sin Sanitización
- **Problema**: No hay sanitización de nombres de archivo en uploads.
- **Impacto**: Vulnerable a path traversal attacks.
- **Solución Recomendada**: Usar `secure_filename()` de werkzeug en todos los uploads.

---

## 🔴 8. MANEJO DE ERRORES Y LOGS

### 8.1 Errores sin Logging Centralizado
- **Problema**: Los errores se imprimen con `print()` en lugar de usar logging.
- **Impacto**: Difícil rastrear errores en producción.
- **Solución Recomendada**: Usar módulo logging con niveles apropiados (ERROR, WARNING, INFO).

### 8.2 Mensajes de Error Exponen Información Sensible
- **Problema**: Algunos endpoints devuelven mensajes de error con detalles de SQL o rutas internas.
- **Impacto**: Vulnerabilidad de información sensible.
- **Solución Recomendada**: Retornar mensajes genéricos al usuario y loggear detalles internamente.

### 8.3 Errores 500 sin Página Personalizada
- **Problema**: No hay página de error 500 personalizada.
- **Impacto**: Usuarios ven error genérico de Flask en producción.
- **Solución Recomendada**: Implementar error handlers personalizados (@app.errorhandler).

---

## 🔴 9. SEGURIDAD

### 9.1 CSRF Protection No Implementado
- **Problema**: No se observa implementación de tokens CSRF en formularios.
- **Impacto**: Vulnerable a ataques Cross-Site Request Forgery.
- **Solución Recomendada**: Implementar Flask-WTF con CSRFProtect.

### 9.2 Headers de Seguridad Ausentes
- **Problema**: No hay configuración de headers de seguridad (X-Frame-Options, CSP, etc.).
- **Impacto**: Vulnerable a clickjacking y XSS.
- **Solución Recomendada**: Implementar Flask-Talisman o configurar headers manualmente.

### 9.3 Rate Limiting No Implementado
- **Problema**: No hay límite de peticiones por usuario/IP.
- **Impacto**: Vulnerable a ataques de fuerza bruta y DDoS.
- **Solución Recomendada**: Implementar Flask-Limiter en endpoints críticos (login, API).

### 9.4 Contraseñas sin Política de Complejidad Configurable
- **Problema**: La política de contraseña está hardcodeada (8 chars, mayúscula, minúscula, número).
- **Impacto**: No se puede ajustar según requerimientos de seguridad.
- **Solución Recomendada**: Configurar política en archivo de configuración o variables de entorno.

### 9.5 Secret Key en Código
- **Problema**: `SECRET_KEY` tiene valor por defecto en código fuente.
- **Impacto**: Si no se configura correctamente, la seguridad está comprometida.
- **Solución Recomendada**: Forzar configuración de SECRET_KEY desde variables de entorno sin valor por defecto.

---

## 🔴 10. RENDIMIENTO

### 10.1 Queries N+1 en Listados
- **Problema**: Algunos endpoints hacen consultas adicionales dentro de loops (ej: obtener info de empleado para cada reserva).
- **Impacto**: Degradación del rendimiento con muchos registros.
- **Solución Recomendada**: Usar JOINs en lugar de consultas individuales.

### 10.2 Caché No Implementado para Catálogos
- **Problema**: Catálogos (departamentos, provincias, distritos) se consultan cada vez.
- **Impacto**: Consultas innecesarias a la base de datos.
- **Solución Recomendada**: Implementar caché en memoria (Flask-Caching) para datos estáticos.

### 10.3 Consultas sin Paginación
- **Problema**: Endpoints como `/api/listar-reservas` retornan todos los registros sin paginación.
- **Impacto**: Timeout y alto consumo de memoria con muchos datos.
- **Solución Recomendada**: Implementar paginación con LIMIT y OFFSET.

### 10.4 Actualización de Horarios en Cada Consulta
- **Problema**: `actualizar_horarios_vencidos()` se ejecuta en cada consulta de horarios.
- **Impacto**: Operaciones UPDATE innecesarias que afectan rendimiento.
- **Solución Recomendada**: Ejecutar como cron job cada hora en lugar de bajo demanda.

---

## 🔴 11. EXPERIENCIA DE USUARIO

### 11.1 Mensajes de Error No Descriptivos
- **Problema**: Muchos mensajes flash solo dicen "Error al..." sin detalles útiles.
- **Impacto**: Usuarios no saben qué hacer para corregir el error.
- **Solución Recomendada**: Proveer mensajes específicos y accionables.

### 11.2 Formularios sin Validación en Tiempo Real
- **Problema**: La validación solo ocurre al enviar el formulario.
- **Impacto**: Mala experiencia de usuario al corregir múltiples errores.
- **Solución Recomendada**: Implementar validación JavaScript en tiempo real.

### 11.3 Carga de Páginas sin Indicadores de Progreso
- **Problema**: No hay spinners o indicadores de carga en operaciones lentas.
- **Impacto**: Usuarios no saben si la página está cargando o congelada.
- **Solución Recomendada**: Agregar spinners con JavaScript para operaciones asíncronas.

### 11.4 Confirmación de Acciones Destructivas sin Modal
- **Problema**: Acciones como cancelar reserva o eliminar usuario no tienen confirmación explícita.
- **Impacto**: Usuarios podrían realizar acciones por error.
- **Solución Recomendada**: Implementar modales de confirmación para acciones críticas.

---

## 🔴 12. COMPATIBILIDAD Y ACCESIBILIDAD

### 12.1 Templates sin Etiquetas Alt en Imágenes
- **Problema**: No se verificó si todas las imágenes tienen atributo alt.
- **Impacto**: Problemas de accesibilidad para usuarios con lectores de pantalla.
- **Solución Recomendada**: Auditar y agregar alt a todas las imágenes.

### 12.2 Formularios sin Labels Apropiados
- **Problema**: Algunos inputs podrían no tener labels asociados.
- **Impacto**: Problemas de accesibilidad y usabilidad.
- **Solución Recomendada**: Asegurar que todos los inputs tengan `<label for="...">`.

### 12.3 Sin Soporte para Modo Oscuro
- **Problema**: No hay implementación de tema oscuro.
- **Impacto**: Experiencia visual pobre en ambientes con poca luz.
- **Solución Recomendada**: Implementar toggle de tema oscuro con Tailwind.

---

## 🔴 13. INTEGRACIÓN Y COMUNICACIÓN

### 13.1 Envío de Emails sin Confirmación de Entrega
- **Problema**: No hay verificación de que los emails se enviaron correctamente.
- **Impacact**: Usuarios podrían no recibir notificaciones importantes sin saberlo.
- **Solución Recomendada**: Implementar log de emails enviados con estado (exitoso/fallido).

### 13.2 Emails sin Rate Limiting
- **Problema**: No hay límite de emails enviados por usuario.
- **Impacto**: Vulnerable a spam o abuso del servicio SMTP.
- **Solución Recomendada**: Limitar emails por usuario/IP (ej: 10 por hora).

### 13.3 Templates de Email sin Diseño Responsive
- **Problema**: Los emails HTML podrían no verse bien en móviles.
- **Impacto**: Mala experiencia en dispositivos móviles.
- **Solución Recomendada**: Usar templates responsive para emails.

---

## 🔴 14. DATOS Y REPORTES

### 14.1 Reportes sin Exportación a PDF/Excel
- **Problema**: Los reportes solo se muestran en pantalla, no se pueden exportar.
- **Impacto**: Usuarios no pueden compartir o guardar reportes fácilmente.
- **Solución Recomendada**: Implementar exportación a PDF con ReportLab o Excel con openpyxl.

### 14.2 Estadísticas sin Agregaciones Optimizadas
- **Problema**: Las estadísticas se calculan en cada petición sin caché.
- **Impacto**: Alto consumo de recursos con muchos datos.
- **Solución Recomendada**: Precalcular estadísticas diarias/semanales con cron job.

### 14.3 Gráficos sin Datos Históricos
- **Problema**: No hay visualización de tendencias o datos históricos.
- **Impacto**: Difícil tomar decisiones basadas en datos.
- **Solución Recomendada**: Implementar gráficos con Chart.js o similar.

---

## 🔴 15. DEPLOYMENT Y CONFIGURACIÓN

### 15.1 Debug Mode Habilitado en Producción
- **Problema**: El código tiene `debug=True` en app.run().
- **Impacto**: Expone información sensible y vulnerabilidades.
- **Solución Recomendada**: Usar variable de entorno para controlar debug mode.

### 15.2 Sin Configuración de Entornos (Dev/Prod)
- **Problema**: No hay separación clara de configuraciones por entorno.
- **Impacto**: Riesgo de usar configuración de desarrollo en producción.
- **Solución Recomendada**: Implementar config.py con clases por entorno.

### 15.3 Credenciales de BD Hardcodeadas
- **Problema**: Las credenciales de base de datos están en el código fuente.
- **Impacto**: Vulnerabilidad de seguridad grave.
- **Solución Recomendada**: Usar variables de entorno para todas las credenciales.

### 15.4 Sin Monitoreo de Salud de la Aplicación
- **Problema**: No hay endpoint de health check.
- **Impacto**: Difícil detectar si la aplicación está funcionando correctamente.
- **Solución Recomendada**: Implementar `/health` endpoint con verificación de DB.

---

## 🔴 16. TESTING Y CALIDAD

### 16.1 Tests Incompletos
- **Problema**: Solo hay tests para farmacia e ingresos, no para otros módulos.
- **Impacto**: Cambios podrían romper funcionalidades no probadas.
- **Solución Recomendada**: Aumentar cobertura de tests a 80%+ con pytest.

### 16.2 Sin Tests de Integración
- **Problema**: No hay tests que verifiquen flujos completos de usuario.
- **Impacto**: Bugs en interacciones entre módulos podrían pasar desapercibidos.
- **Solución Recomendada**: Implementar tests de integración con Selenium o Playwright.

### 16.3 Sin Análisis Estático de Código
- **Problema**: No se usa linter o análisis estático.
- **Impacto**: Código inconsistente y con posibles bugs.
- **Solución Recomendada**: Configurar pylint o flake8 en CI/CD.

---

## 📊 Priorización de Errores

### 🔴 **Críticos** (Requieren atención inmediata):
1. Credenciales de BD hardcodeadas (15.3)
2. CSRF Protection no implementado (9.1)
3. Inyección SQL posible (2.5)
4. Secret Key en código (9.5)
5. Debug mode en producción (15.1)

### 🟠 **Altos** (Requieren atención pronto):
1. Sesión expirada sin manejo (1.1)
2. Transacciones sin rollback completo (2.2)
3. Deadlocks en operaciones concurrentes (2.3)
4. Reservas duplicadas (4.1)
5. Stock negativo en farmacia (5.2)

### 🟡 **Medios** (Planificar corrección):
1. Validación de edad sin control futuro (3.1)
2. Sin rate limiting (9.3)
3. Queries N+1 (10.1)
4. Sin caché para catálogos (10.2)
5. Mensajes de error no descriptivos (11.1)

### 🟢 **Bajos** (Mejoras a futuro):
1. Sin modo oscuro (12.3)
2. Reportes sin exportación (14.1)
3. Sin gráficos históricos (14.3)
4. Templates de email no responsive (13.3)

---

## 📝 Recomendaciones Generales

1. **Implementar un sistema de logging robusto** con niveles y rotación de archivos
2. **Crear una suite completa de tests** con cobertura mínima del 80%
3. **Configurar CI/CD** con validación automática de código
4. **Implementar monitoreo** (Sentry, New Relic, etc.)
5. **Documentar APIs** con Swagger/OpenAPI
6. **Revisar y actualizar dependencias** regularmente
7. **Implementar backups automatizados** de base de datos
8. **Crear documentación de usuario** detallada
9. **Realizar auditorías de seguridad** periódicas
10. **Establecer proceso de code review** antes de merge a main

---

*Documento generado el: 19 de Noviembre, 2025*
*Última actualización: 19 de Noviembre, 2025*
