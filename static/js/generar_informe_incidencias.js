// ============================================
// VARIABLES GLOBALES
// ============================================
let incidenciasData = [];
let paginaActual = 1;
const incidenciasPorPagina = 10;

// ============================================
// INICIALIZACIÓN
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    inicializarEventos();
    cargarPacientes();
    cargarCategorias();
    cargarEstados();
});

function inicializarEventos() {
    // Botón generar reporte
    document.getElementById('btnGenerarReporte').addEventListener('click', generarReporte);
    
    // Botones de paginación
    document.getElementById('btnPrevPage').addEventListener('click', paginaAnterior);
    document.getElementById('btnNextPage').addEventListener('click', paginaSiguiente);
    
    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', function(event) {
        const modalDetalle = document.getElementById('modalDetalle');
        const modalExito = document.getElementById('modalExito');
        
        if (event.target === modalDetalle) {
            cerrarModal();
        }
        if (event.target === modalExito) {
            cerrarModalExito();
        }
    });
}

// ============================================
// CARGA DE DATOS INICIALES
// ============================================
async function cargarPacientes() {
    try {
        const response = await fetch('/incidencias/api/pacientes');
        const result = await response.json();
        
        if (result.success) {
            const select = document.getElementById('pacienteSelect');
            
            result.data.forEach(paciente => {
                const option = document.createElement('option');
                option.value = paciente.id;
                option.textContent = `${paciente.nombre} ${paciente.apellido} - DNI: ${paciente.dni}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar pacientes:', error);
        mostrarNotificacion('Error al cargar la lista de pacientes', 'error');
    }
}

async function cargarCategorias() {
    try {
        const response = await fetch('/incidencias/api/categorias');
        const result = await response.json();
        
        if (result.success) {
            const select = document.getElementById('categoriaSelect');
            
            result.data.forEach(categoria => {
                const option = document.createElement('option');
                option.value = categoria.id;
                option.textContent = categoria.nombre;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar categorías:', error);
        mostrarNotificacion('Error al cargar las categorías', 'error');
    }
}

async function cargarEstados() {
    try {
        const response = await fetch('/incidencias/api/estados');
        const result = await response.json();
        
        if (result.success) {
            const select = document.getElementById('estadoSelect');
            
            result.data.forEach(estado => {
                const option = document.createElement('option');
                option.value = estado;
                option.textContent = estado;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar estados:', error);
        mostrarNotificacion('Error al cargar los estados', 'error');
    }
}

// ============================================
// GENERAR REPORTE
// ============================================
async function generarReporte() {
    const pacienteId = document.getElementById('pacienteSelect').value;
    const fecha = document.getElementById('fechaInput').value;
    const categoriaId = document.getElementById('categoriaSelect').value;
    const estado = document.getElementById('estadoSelect').value;
    
    // Mostrar loading
    const btnGenerar = document.getElementById('btnGenerarReporte');
    const textoOriginal = btnGenerar.innerHTML;
    btnGenerar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
    btnGenerar.disabled = true;
    
    try {
        const response = await fetch('/incidencias/api/generar-informe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paciente_id: pacienteId,
                fecha: fecha,
                categoria_id: categoriaId,
                estado: estado
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            incidenciasData = result.data.incidencias;
            paginaActual = 1;
            
            // Mostrar sección de resultados
            document.getElementById('resultsSection').style.display = 'block';
            
            // Actualizar contador
            document.getElementById('totalIncidencias').textContent = 
                `${result.data.total} incidencia${result.data.total !== 1 ? 's' : ''}`;
            
            // Renderizar tabla
            renderizarTabla();
            
            // Mostrar modal de éxito
            document.getElementById('mensajeResultado').textContent = result.message;
            mostrarModalExito();
            
            // Scroll a resultados
            document.getElementById('resultsSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        } else {
            mostrarNotificacion(result.message, 'error');
        }
    } catch (error) {
        console.error('Error al generar reporte:', error);
        mostrarNotificacion('Error al generar el informe. Por favor, intente nuevamente.', 'error');
    } finally {
        // Restaurar botón
        btnGenerar.innerHTML = textoOriginal;
        btnGenerar.disabled = false;
    }
}

// ============================================
// RENDERIZAR TABLA
// ============================================
function renderizarTabla() {
    const tbody = document.getElementById('tablaIncidencias');
    tbody.innerHTML = '';
    
    // Calcular índices para la paginación
    const inicio = (paginaActual - 1) * incidenciasPorPagina;
    const fin = inicio + incidenciasPorPagina;
    const incidenciasPagina = incidenciasData.slice(inicio, fin);
    
    if (incidenciasPagina.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 1rem; display: block;"></i>
                    No se encontraron incidencias con los filtros seleccionados
                </td>
            </tr>
        `;
        return;
    }
    
    incidenciasPagina.forEach(incidencia => {
        const tr = document.createElement('tr');
        
        // Obtener clases para badges
        const estadoClass = obtenerClaseEstado(incidencia.estado);
        const prioridadClass = obtenerClasePrioridad(incidencia.prioridad);
        
        tr.innerHTML = `
            <td>${incidencia.id}</td>
            <td>${incidencia.fechaRegistro}</td>
            <td>${incidencia.descripcion}</td>
            <td><span class="badge ${estadoClass}">${incidencia.estado}</span></td>
            <td><span class="badge ${prioridadClass}">${incidencia.prioridad}</span></td>
            <td>${incidencia.fechaResolucion}</td>
            <td>${truncarTexto(incidencia.observaciones, 50)}</td>
            <td class="td-controls">
                <div class="control-buttons">
                    <button class="btn-view" onclick="verDetalle(${incidencia.id})" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-delete" onclick="eliminarIncidencia(${incidencia.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
    
    // Actualizar controles de paginación
    actualizarPaginacion();
}

// ============================================
// FUNCIONES AUXILIARES PARA ESTILOS
// ============================================
function obtenerClaseEstado(estado) {
    const clases = {
        'Abierta': 'estado-abierta',
        'En Proceso': 'estado-proceso',
        'Resuelta': 'estado-resuelta',
        'Cerrada': 'estado-cerrada'
    };
    return clases[estado] || '';
}

function obtenerClasePrioridad(prioridad) {
    const clases = {
        'Baja': 'prioridad-baja',
        'Media': 'prioridad-media',
        'Alta': 'prioridad-alta',
        'Crítica': 'prioridad-critica'
    };
    return clases[prioridad] || '';
}

function truncarTexto(texto, maxLength) {
    if (texto.length <= maxLength) return texto;
    return texto.substring(0, maxLength) + '...';
}

// ============================================
// PAGINACIÓN
// ============================================
function actualizarPaginacion() {
    const totalPaginas = Math.ceil(incidenciasData.length / incidenciasPorPagina);
    
    document.getElementById('paginaActual').textContent = paginaActual;
    document.getElementById('totalPaginas').textContent = totalPaginas;
    
    // Habilitar/deshabilitar botones
    document.getElementById('btnPrevPage').disabled = paginaActual === 1;
    document.getElementById('btnNextPage').disabled = paginaActual >= totalPaginas;
}

function paginaAnterior() {
    if (paginaActual > 1) {
        paginaActual--;
        renderizarTabla();
        scrollToTable();
    }
}

function paginaSiguiente() {
    const totalPaginas = Math.ceil(incidenciasData.length / incidenciasPorPagina);
    if (paginaActual < totalPaginas) {
        paginaActual++;
        renderizarTabla();
        scrollToTable();
    }
}

function scrollToTable() {
    document.getElementById('resultsSection').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// ============================================
// MODAL DETALLE
// ============================================
async function verDetalle(incidenciaId) {
    try {
        const response = await fetch(`/incidencias/api/incidencia/${incidenciaId}`);
        const result = await response.json();
        
        if (result.success) {
            const incidencia = result.data;
            
            // Llenar datos del modal
            document.getElementById('detalle-id').textContent = incidencia.id;
            document.getElementById('detalle-fecha').textContent = incidencia.fechaRegistro;
            document.getElementById('detalle-descripcion').textContent = incidencia.descripcion;
            
            const estadoBadge = document.getElementById('detalle-estado');
            estadoBadge.textContent = incidencia.estado;
            estadoBadge.className = 'badge ' + obtenerClaseEstado(incidencia.estado);
            
            const prioridadBadge = document.getElementById('detalle-prioridad');
            prioridadBadge.textContent = incidencia.prioridad;
            prioridadBadge.className = 'badge ' + obtenerClasePrioridad(incidencia.prioridad);
            
            document.getElementById('detalle-resolucion').textContent = incidencia.fechaResolucion;
            document.getElementById('detalle-observaciones').textContent = incidencia.observaciones;
            
            // Mostrar modal
            document.getElementById('modalDetalle').classList.add('active');
        } else {
            mostrarNotificacion('No se pudo cargar el detalle de la incidencia', 'error');
        }
    } catch (error) {
        console.error('Error al obtener detalle:', error);
        mostrarNotificacion('Error al cargar el detalle', 'error');
    }
}

function cerrarModal() {
    document.getElementById('modalDetalle').classList.remove('active');
}

// ============================================
// MODAL ÉXITO
// ============================================
function mostrarModalExito() {
    document.getElementById('modalExito').classList.add('active');
}

function cerrarModalExito() {
    document.getElementById('modalExito').classList.remove('active');
}

// ============================================
// ELIMINAR INCIDENCIA
// ============================================
function eliminarIncidencia(incidenciaId) {
    if (confirm('¿Está seguro de que desea eliminar esta incidencia?')) {
        // Buscar el índice de la incidencia
        const index = incidenciasData.findIndex(inc => inc.id === incidenciaId);
        
        if (index !== -1) {
            // Eliminar del array
            incidenciasData.splice(index, 1);
            
            // Actualizar contador
            document.getElementById('totalIncidencias').textContent = 
                `${incidenciasData.length} incidencia${incidenciasData.length !== 1 ? 's' : ''}`;
            
            // Si la página actual queda vacía, ir a la anterior
            const totalPaginas = Math.ceil(incidenciasData.length / incidenciasPorPagina);
            if (paginaActual > totalPaginas && totalPaginas > 0) {
                paginaActual = totalPaginas;
            }
            
            // Renderizar tabla
            renderizarTabla();
            
            mostrarNotificacion('Incidencia eliminada correctamente', 'success');
        }
    }
}

// ============================================
// NOTIFICACIONES
// ============================================
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion notificacion-${tipo}`;
    
    const iconos = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    notificacion.innerHTML = `
        <i class="fas fa-${iconos[tipo]}"></i>
        <span>${mensaje}</span>
    `;
    
    // Agregar estilos si no existen
    if (!document.getElementById('notificacion-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notificacion-styles';
        styles.textContent = `
            .notificacion {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-weight: 600;
                z-index: 3000;
                animation: slideInRight 0.3s ease;
                max-width: 400px;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            .notificacion-success {
                background: #27ae60;
                color: white;
            }
            
            .notificacion-error {
                background: #e74c3c;
                color: white;
            }
            
            .notificacion-warning {
                background: #f39c12;
                color: white;
            }
            
            .notificacion-info {
                background: #3498db;
                color: white;
            }
            
            .notificacion i {
                font-size: 1.25rem;
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Agregar al DOM
    document.body.appendChild(notificacion);
    
    // Eliminar después de 3 segundos
    setTimeout(() => {
        notificacion.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notificacion);
        }, 300);
    }, 3000);
}

// ============================================
// FUNCIONES DE EXPORTACIÓN (PREPARADAS)
// ============================================
function exportarPDF() {
    mostrarNotificacion('Funcionalidad de exportación a PDF en desarrollo', 'info');
}

function exportarExcel() {
    mostrarNotificacion('Funcionalidad de exportación a Excel en desarrollo', 'info');
}
