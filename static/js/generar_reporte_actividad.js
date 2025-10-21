// Generar Reporte de Actividad - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    let recursosCompletos = [];
    let recursosFiltrados = [];
    let empleados = [];
    let paginaActual = 1;
    const recursosPorPagina = 10;
    let recursoAEliminar = null;
    let reporteGenerado = false;

    // Elementos DOM
    const filtroEmpleado = document.getElementById('filtroEmpleado');
    const filtroFecha = document.getElementById('filtroFecha');
    const btnGenerarReporte = document.getElementById('btnGenerarReporte');
    const btnExportar = document.getElementById('btnExportar');
    const tablaRecursos = document.getElementById('tablaRecursos');
    const btnAnterior = document.getElementById('btnAnterior');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const paginaActualSpan = document.getElementById('paginaActual');
    const totalPaginasSpan = document.getElementById('totalPaginas');
    const paginacionContainer = document.getElementById('paginacionContainer');

    // Modales
    const modalDetalle = document.getElementById('modalDetalle');
    const modalEliminar = document.getElementById('modalEliminar');
    const modalExito = document.getElementById('modalExito');
    const modalExportar = document.getElementById('modalExportar');
    const closeButtons = document.querySelectorAll('.close');
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    const btnCerrarExito = document.getElementById('btnCerrarExito');

    // Cargar empleados al inicio
    cargarEmpleados();

    // Event Listeners
    btnGenerarReporte.addEventListener('click', generarReporte);
    btnExportar.addEventListener('click', abrirModalExportar);
    btnAnterior.addEventListener('click', paginaAnterior);
    btnSiguiente.addEventListener('click', paginaSiguiente);
    btnCancelarEliminar.addEventListener('click', cerrarModalEliminar);
    btnConfirmarEliminar.addEventListener('click', confirmarEliminacion);
    btnCerrarExito.addEventListener('click', cerrarModalExito);

    // Cerrar modales
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });

    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });

    // Botones de exportación
    document.querySelectorAll('.btn-export-option').forEach(btn => {
        btn.addEventListener('click', function() {
            const formato = this.dataset.formato;
            exportarReporte(formato);
        });
    });

    // Función para cargar empleados
    async function cargarEmpleados() {
        try {
            const response = await fetch('/seguridad/api/empleados');
            const data = await response.json();

            if (data.success) {
                empleados = data.data;
                
                // Llenar select de empleados
                empleados.forEach(emp => {
                    const option = document.createElement('option');
                    option.value = emp.idEmpleado;
                    option.textContent = `${emp.nombreEmpleado} ${emp.apellidoEmpleado}`;
                    option.dataset.nombre = `${emp.nombreEmpleado} ${emp.apellidoEmpleado}`;
                    filtroEmpleado.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error al cargar empleados:', error);
            mostrarNotificacion('Error al cargar lista de empleados', 'error');
        }
    }

    // Función para generar reporte
    async function generarReporte() {
        const idEmpleado = filtroEmpleado.value;
        const fecha = filtroFecha.value;

        // Validar campos
        if (!idEmpleado) {
            mostrarNotificacion('Debe seleccionar un empleado', 'error');
            return;
        }

        if (!fecha) {
            mostrarNotificacion('Debe seleccionar una fecha', 'error');
            return;
        }

        // Mostrar loading
        const iconOriginal = btnGenerarReporte.innerHTML;
        btnGenerarReporte.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
        btnGenerarReporte.disabled = true;

        try {
            const response = await fetch('/reportes/api/generar-actividad', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    idEmpleado: idEmpleado,
                    fecha: fecha
                })
            });

            const data = await response.json();

            if (data.success) {
                recursosCompletos = data.data.recursos;
                recursosFiltrados = [...recursosCompletos];
                paginaActual = 1;
                reporteGenerado = true;
                
                // Habilitar botón de exportar
                btnExportar.disabled = false;
                
                // Mostrar tabla
                renderizarTabla();
                actualizarPaginacion();
                paginacionContainer.style.display = 'flex';
                
                // Mostrar modal de éxito
                mostrarModalExito(idEmpleado, fecha, data.data.total);
            } else {
                mostrarNotificacion(data.message || 'Error al generar reporte', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('Error al generar reporte de actividad', 'error');
        } finally {
            btnGenerarReporte.innerHTML = iconOriginal;
            btnGenerarReporte.disabled = false;
        }
    }

    // Función para mostrar modal de éxito
    function mostrarModalExito(idEmpleado, fecha, total) {
        const empleadoSeleccionado = filtroEmpleado.options[filtroEmpleado.selectedIndex];
        const nombreEmpleado = empleadoSeleccionado.dataset.nombre;

        document.getElementById('exitoEmpleado').textContent = nombreEmpleado;
        document.getElementById('exitoFecha').textContent = formatearFecha(fecha);
        document.getElementById('exitoTotal').textContent = total;

        modalExito.style.display = 'block';
    }

    // Función para cerrar modal de éxito
    function cerrarModalExito() {
        modalExito.style.display = 'none';
    }

    // Función para renderizar tabla
    function renderizarTabla() {
        const inicio = (paginaActual - 1) * recursosPorPagina;
        const fin = inicio + recursosPorPagina;
        const recursosPagina = recursosFiltrados.slice(inicio, fin);

        if (recursosPagina.length === 0) {
            tablaRecursos.innerHTML = `
                <tr class="empty-row">
                    <td colspan="4" class="no-recursos">
                        <i class="fas fa-inbox"></i> No se encontraron recursos
                    </td>
                </tr>
            `;
            return;
        }

        tablaRecursos.innerHTML = recursosPagina.map(recurso => `
            <tr>
                <td>${recurso.idRecurso}</td>
                <td>${recurso.nombreRecurso}</td>
                <td>
                    <span class="estado-badge estado-${recurso.estado.toLowerCase().replace(' ', '-')}">
                        ${recurso.estado}
                    </span>
                </td>
                <td>
                    <div class="controles">
                        <button class="btn-control btn-ver" onclick="verDetalle(${recurso.idRecurso})" title="Ver detalle">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-control btn-eliminar" onclick="eliminarRecurso(${recurso.idRecurso})" title="Eliminar">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Función para ver detalle de un recurso
    window.verDetalle = function(idRecurso) {
        const recurso = recursosCompletos.find(r => r.idRecurso === idRecurso);
        if (!recurso) return;

        const empleadoSeleccionado = filtroEmpleado.options[filtroEmpleado.selectedIndex];
        const nombreEmpleado = empleadoSeleccionado.dataset.nombre;
        const fecha = filtroFecha.value;

        document.getElementById('detalleId').textContent = recurso.idRecurso;
        document.getElementById('detalleNombre').textContent = recurso.nombreRecurso;
        document.getElementById('detalleTipo').textContent = recurso.tipo;
        document.getElementById('detalleEstado').innerHTML = `
            <span class="estado-badge estado-${recurso.estado.toLowerCase().replace(' ', '-')}">
                ${recurso.estado}
            </span>
        `;
        document.getElementById('detalleEmpleado').textContent = nombreEmpleado;
        document.getElementById('detalleFecha').textContent = formatearFecha(fecha);
        document.getElementById('detalleDescripcion').textContent = recurso.descripcion;
        document.getElementById('detalleUso').textContent = recurso.uso;

        modalDetalle.style.display = 'block';
    };

    // Función para eliminar recurso
    window.eliminarRecurso = function(idRecurso) {
        recursoAEliminar = idRecurso;
        modalEliminar.style.display = 'block';
    };

    // Función para confirmar eliminación
    function confirmarEliminacion() {
        if (recursoAEliminar) {
            // Eliminar del array local
            recursosCompletos = recursosCompletos.filter(r => r.idRecurso !== recursoAEliminar);
            recursosFiltrados = recursosFiltrados.filter(r => r.idRecurso !== recursoAEliminar);
            
            renderizarTabla();
            actualizarPaginacion();
            cerrarModalEliminar();
            
            // Mostrar notificación
            mostrarNotificacion('Recurso eliminado del reporte', 'success');

            // Si no quedan recursos, deshabilitar exportación
            if (recursosCompletos.length === 0) {
                btnExportar.disabled = true;
                reporteGenerado = false;
                paginacionContainer.style.display = 'none';
            }
        }
    }

    // Función para cerrar modal de eliminar
    function cerrarModalEliminar() {
        modalEliminar.style.display = 'none';
        recursoAEliminar = null;
    }

    // Función para abrir modal de exportar
    function abrirModalExportar() {
        if (!reporteGenerado || recursosCompletos.length === 0) {
            mostrarNotificacion('Debe generar un reporte primero', 'error');
            return;
        }
        modalExportar.style.display = 'block';
    }

    // Función para exportar reporte
    function exportarReporte(formato) {
        const empleadoSeleccionado = filtroEmpleado.options[filtroEmpleado.selectedIndex];
        const nombreEmpleado = empleadoSeleccionado.dataset.nombre;
        const fecha = filtroFecha.value;

        mostrarNotificacion(`Exportando reporte de actividad en formato ${formato.toUpperCase()}...`, 'success');
        modalExportar.style.display = 'none';
        
        // TODO: Implementar exportación real
        setTimeout(() => {
            mostrarNotificacion(`Reporte exportado: ${nombreEmpleado} - ${fecha}`, 'success');
        }, 1500);
    }

    // Paginación
    function paginaAnterior() {
        if (paginaActual > 1) {
            paginaActual--;
            renderizarTabla();
            actualizarPaginacion();
        }
    }

    function paginaSiguiente() {
        const totalPaginas = Math.ceil(recursosFiltrados.length / recursosPorPagina);
        if (paginaActual < totalPaginas) {
            paginaActual++;
            renderizarTabla();
            actualizarPaginacion();
        }
    }

    function actualizarPaginacion() {
        const totalPaginas = Math.ceil(recursosFiltrados.length / recursosPorPagina) || 1;
        paginaActualSpan.textContent = paginaActual;
        totalPaginasSpan.textContent = totalPaginas;

        btnAnterior.disabled = paginaActual === 1;
        btnSiguiente.disabled = paginaActual === totalPaginas;
    }

    // Funciones auxiliares
    function formatearFecha(fecha) {
        const fechaObj = new Date(fecha);
        if (isNaN(fechaObj)) return fecha;
        
        const opciones = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        
        return fechaObj.toLocaleDateString('es-ES', opciones);
    }

    function mostrarNotificacion(mensaje, tipo) {
        // Crear elemento de notificación
        const notificacion = document.createElement('div');
        notificacion.className = `notificacion notificacion-${tipo}`;
        notificacion.innerHTML = `
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${mensaje}
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
                    padding: 15px 25px;
                    border-radius: 5px;
                    color: white;
                    font-weight: 500;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                    z-index: 10000;
                    animation: slideInRight 0.3s ease, fadeOut 0.3s ease 2.7s;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .notificacion-success {
                    background-color: #27ae60;
                }
                .notificacion-error {
                    background-color: #e74c3c;
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
                @keyframes fadeOut {
                    from {
                        opacity: 1;
                    }
                    to {
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notificacion);
        
        // Eliminar después de 3 segundos
        setTimeout(() => {
            notificacion.remove();
        }, 3000);
    }
});
