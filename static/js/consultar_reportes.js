// Consultar Reportes por Categoría - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    let reportesCompletos = [];
    let reportesFiltrados = [];
    let categorias = [];
    let paginaActual = 1;
    const reportesPorPagina = 10;

    // Elementos DOM
    const filtroCategoria = document.getElementById('filtroCategoria');
    const filtroFecha = document.getElementById('filtroFecha');
    const btnGenerarReporte = document.getElementById('btnGenerarReporte');
    const btnExportar = document.getElementById('btnExportar');
    const tablaReportes = document.getElementById('tablaReportes');
    const btnAnterior = document.getElementById('btnAnterior');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const paginaActualSpan = document.getElementById('paginaActual');
    const totalPaginasSpan = document.getElementById('totalPaginas');

    // Modales
    const modalDetalle = document.getElementById('modalDetalle');
    const modalGenerar = document.getElementById('modalGenerar');
    const modalExportar = document.getElementById('modalExportar');
    const closeButtons = document.querySelectorAll('.close');
    const btnCancelarGenerar = document.getElementById('btnCancelarGenerar');
    const formGenerarReporte = document.getElementById('formGenerarReporte');
    const categoriaReporte = document.getElementById('categoriaReporte');

    // Cargar datos al inicio
    cargarCategorias();
    cargarReportes();

    // Event Listeners
    filtroCategoria.addEventListener('change', aplicarFiltros);
    filtroFecha.addEventListener('change', aplicarFiltros);
    btnGenerarReporte.addEventListener('click', abrirModalGenerar);
    btnExportar.addEventListener('click', abrirModalExportar);
    btnAnterior.addEventListener('click', paginaAnterior);
    btnSiguiente.addEventListener('click', paginaSiguiente);
    btnCancelarGenerar.addEventListener('click', cerrarModalGenerar);
    formGenerarReporte.addEventListener('submit', generarReporte);

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
            exportarReportes(formato);
        });
    });

    // Función para cargar categorías
    async function cargarCategorias() {
        try {
            const response = await fetch('/reportes/api/categorias');
            const data = await response.json();

            if (data.success) {
                categorias = data.data;
                
                // Llenar select de filtro
                categorias.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.nombreCategoria;
                    option.textContent = cat.nombreCategoria;
                    filtroCategoria.appendChild(option);
                });

                // Llenar select del modal de generar
                categorias.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.nombreCategoria;
                    option.textContent = cat.nombreCategoria;
                    categoriaReporte.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error al cargar categorías:', error);
            mostrarNotificacion('Error al cargar categorías', 'error');
        }
    }

    // Función para cargar reportes
    async function cargarReportes() {
        try {
            mostrarCargando();
            const response = await fetch('/reportes/api/reportes');
            const data = await response.json();

            if (data.success) {
                reportesCompletos = data.data;
                reportesFiltrados = [...reportesCompletos];
                paginaActual = 1;
                renderizarTabla();
                actualizarPaginacion();
            } else {
                mostrarError('Error al cargar los reportes');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error de conexión con el servidor');
        }
    }

    // Función para aplicar filtros
    function aplicarFiltros() {
        const categoriaValue = filtroCategoria.value;
        const fechaValue = filtroFecha.value;

        reportesFiltrados = reportesCompletos.filter(reporte => {
            const matchCategoria = !categoriaValue || 
                categoriaValue === 'Todas' || 
                reporte.categoria === categoriaValue;
            
            const matchFecha = !fechaValue || 
                reporte.fechaGeneracion === fechaValue;

            return matchCategoria && matchFecha;
        });

        paginaActual = 1;
        renderizarTabla();
        actualizarPaginacion();
    }

    // Función para renderizar la tabla
    function renderizarTabla() {
        const inicio = (paginaActual - 1) * reportesPorPagina;
        const fin = inicio + reportesPorPagina;
        const reportesPagina = reportesFiltrados.slice(inicio, fin);

        if (reportesPagina.length === 0) {
            tablaReportes.innerHTML = `
                <tr>
                    <td colspan="5" class="no-reportes">
                        <i class="fas fa-inbox"></i> No se encontraron reportes
                    </td>
                </tr>
            `;
            return;
        }

        tablaReportes.innerHTML = reportesPagina.map(reporte => `
            <tr onclick="verDetalle(${reporte.idReporte})">
                <td>${formatearFechaHora(reporte.fechaGeneracion, reporte.horaGeneracion)}</td>
                <td>${reporte.categoria}</td>
                <td>${reporte.nombreEmpleado}</td>
                <td>${reporte.descripcion}</td>
                <td>
                    <span class="estado-badge estado-${reporte.estado.toLowerCase().replace(' ', '-')}">
                        ${reporte.estado}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    // Función para ver detalle de un reporte
    window.verDetalle = function(idReporte) {
        const reporte = reportesCompletos.find(r => r.idReporte === idReporte);
        if (!reporte) return;

        document.getElementById('detalleId').textContent = reporte.idReporte;
        document.getElementById('detalleNombre').textContent = reporte.nombreReporte;
        document.getElementById('detalleCategoria').textContent = reporte.categoria;
        document.getElementById('detalleFecha').textContent = formatearFecha(reporte.fechaGeneracion);
        document.getElementById('detalleHora').textContent = reporte.horaGeneracion;
        document.getElementById('detalleEmpleado').textContent = reporte.nombreEmpleado;
        document.getElementById('detalleDescripcion').textContent = reporte.descripcion;
        document.getElementById('detalleRuta').textContent = reporte.rutaArchivo;
        document.getElementById('detalleEstado').innerHTML = `
            <span class="estado-badge estado-${reporte.estado.toLowerCase().replace(' ', '-')}">
                ${reporte.estado}
            </span>
        `;

        // Configurar botón de descarga
        document.getElementById('btnDescargar').onclick = function() {
            descargarReporte(reporte);
        };

        modalDetalle.style.display = 'block';
    };

    // Función para abrir modal de generar
    function abrirModalGenerar() {
        modalGenerar.style.display = 'block';
        formGenerarReporte.reset();
    }

    // Función para cerrar modal de generar
    function cerrarModalGenerar() {
        modalGenerar.style.display = 'none';
    }

    // Función para generar reporte
    async function generarReporte(event) {
        event.preventDefault();
        
        const categoria = categoriaReporte.value;
        const descripcion = document.getElementById('descripcionReporte').value;

        if (!categoria) {
            mostrarNotificacion('Debe seleccionar una categoría', 'error');
            return;
        }

        // Mostrar spinner
        const spinner = document.getElementById('spinnerGenerar');
        const texto = document.getElementById('textoGenerar');
        spinner.style.display = 'inline-block';
        texto.textContent = 'Generando...';

        try {
            const response = await fetch('/reportes/api/generar-reporte', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    categoria: categoria,
                    descripcion: descripcion,
                    idUsuario: 1,
                    nombreEmpleado: 'Admin Sistema'
                })
            });

            const data = await response.json();

            if (data.success) {
                mostrarNotificacion('Reporte generado exitosamente', 'success');
                cerrarModalGenerar();
                cargarReportes(); // Recargar la lista de reportes
            } else {
                mostrarNotificacion(data.message || 'Error al generar reporte', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('Error al generar reporte', 'error');
        } finally {
            // Ocultar spinner
            spinner.style.display = 'none';
            texto.textContent = 'Generar';
        }
    }

    // Función para abrir modal de exportar
    function abrirModalExportar() {
        modalExportar.style.display = 'block';
    }

    // Función para exportar reportes
    function exportarReportes(formato) {
        // Simular exportación
        mostrarNotificacion(`Exportando reportes en formato ${formato.toUpperCase()}...`, 'success');
        modalExportar.style.display = 'none';
        
        // TODO: Implementar exportación real
        setTimeout(() => {
            mostrarNotificacion('Reportes exportados exitosamente', 'success');
        }, 1500);
    }

    // Función para descargar reporte
    function descargarReporte(reporte) {
        mostrarNotificacion(`Descargando reporte: ${reporte.nombreReporte}`, 'success');
        // TODO: Implementar descarga real
        console.log('Descargando reporte:', reporte);
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
        const totalPaginas = Math.ceil(reportesFiltrados.length / reportesPorPagina);
        if (paginaActual < totalPaginas) {
            paginaActual++;
            renderizarTabla();
            actualizarPaginacion();
        }
    }

    function actualizarPaginacion() {
        const totalPaginas = Math.ceil(reportesFiltrados.length / reportesPorPagina) || 1;
        paginaActualSpan.textContent = paginaActual;
        totalPaginasSpan.textContent = totalPaginas;

        btnAnterior.disabled = paginaActual === 1;
        btnSiguiente.disabled = paginaActual === totalPaginas;
    }

    // Funciones auxiliares
    function formatearFechaHora(fecha, hora) {
        const fechaObj = new Date(fecha + ' ' + hora);
        if (isNaN(fechaObj)) return `${fecha} ${hora}`;
        
        const opciones = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return fechaObj.toLocaleString('es-ES', opciones);
    }

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

    function mostrarCargando() {
        tablaReportes.innerHTML = `
            <tr>
                <td colspan="5" class="loading-message">
                    <i class="fas fa-spinner fa-spin"></i> Cargando reportes...
                </td>
            </tr>
        `;
    }

    function mostrarError(mensaje) {
        tablaReportes.innerHTML = `
            <tr>
                <td colspan="5" class="no-reportes" style="color: #e74c3c;">
                    <i class="fas fa-exclamation-triangle"></i> ${mensaje}
                </td>
            </tr>
        `;
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
