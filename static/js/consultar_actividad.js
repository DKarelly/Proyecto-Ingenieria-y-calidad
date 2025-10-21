// Consultar Actividad - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    let registrosCompletos = [];
    let registrosFiltrados = [];
    let paginaActual = 1;
    const registrosPorPagina = 10;
    let registroAEliminar = null;

    // Elementos DOM
    const btnBuscar = document.getElementById('btnBuscar');
    const btnExportar = document.getElementById('btnExportar');
    const filtroEmpleado = document.getElementById('filtroEmpleado');
    const filtroHorario = document.getElementById('filtroHorario');
    const filtroFecha = document.getElementById('filtroFecha');
    const tablaRegistros = document.getElementById('tablaRegistros');
    const btnAnterior = document.getElementById('btnAnterior');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const paginaActualSpan = document.getElementById('paginaActual');
    const totalPaginasSpan = document.getElementById('totalPaginas');

    // Modales
    const modalDetalle = document.getElementById('modalDetalle');
    const modalEliminar = document.getElementById('modalEliminar');
    const closeButtons = document.querySelectorAll('.close');
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');

    // Cargar registros al inicio
    cargarRegistros();

    // Event Listeners
    btnBuscar.addEventListener('click', aplicarFiltros);
    btnExportar.addEventListener('click', exportarRegistros);
    btnAnterior.addEventListener('click', paginaAnterior);
    btnSiguiente.addEventListener('click', paginaSiguiente);
    btnCancelarEliminar.addEventListener('click', cerrarModalEliminar);
    btnConfirmarEliminar.addEventListener('click', confirmarEliminacion);

    // Filtros en tiempo real
    filtroEmpleado.addEventListener('input', aplicarFiltros);
    filtroFecha.addEventListener('change', aplicarFiltros);

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

    // Función para cargar registros desde la API
    async function cargarRegistros() {
        try {
            mostrarCargando();
            const response = await fetch('/seguridad/api/registros');
            const data = await response.json();

            if (data.success) {
                registrosCompletos = data.data;
                registrosFiltrados = [...registrosCompletos];
                paginaActual = 1;
                renderizarTabla();
                actualizarPaginacion();
            } else {
                mostrarError('Error al cargar los registros');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error de conexión con el servidor');
        }
    }

    // Función para aplicar filtros
    function aplicarFiltros() {
        const empleadoValue = filtroEmpleado.value.toLowerCase().trim();
        const fechaValue = filtroFecha.value;
        const horarioValue = filtroHorario.value.toLowerCase().trim();

        registrosFiltrados = registrosCompletos.filter(registro => {
            const matchEmpleado = !empleadoValue || 
                registro.nombreEmpleado.toLowerCase().includes(empleadoValue);
            
            const matchFecha = !fechaValue || 
                registro.fechaHora.startsWith(fechaValue);
            
            // TODO: Implementar filtro de horario si es necesario
            const matchHorario = true;

            return matchEmpleado && matchFecha && matchHorario;
        });

        paginaActual = 1;
        renderizarTabla();
        actualizarPaginacion();
    }

    // Función para renderizar la tabla
    function renderizarTabla() {
        const inicio = (paginaActual - 1) * registrosPorPagina;
        const fin = inicio + registrosPorPagina;
        const registrosPagina = registrosFiltrados.slice(inicio, fin);

        if (registrosPagina.length === 0) {
            tablaRegistros.innerHTML = `
                <tr>
                    <td colspan="7" class="no-registros">
                        <i class="fas fa-inbox"></i> No se encontraron registros
                    </td>
                </tr>
            `;
            return;
        }

        tablaRegistros.innerHTML = registrosPagina.map(registro => `
            <tr>
                <td>${registro.idRegistro}</td>
                <td>${registro.nombreEmpleado}</td>
                <td>${registro.descripcion}</td>
                <td>${formatearFechaHora(registro.fechaHora)}</td>
                <td>${registro.ipOrigen}</td>
                <td class="${registro.resultado === 'Exitoso' ? 'resultado-exitoso' : 'resultado-fallido'}">
                    ${registro.resultado}
                </td>
                <td>
                    <div class="controles">
                        <button class="btn-control btn-ver" onclick="verDetalle(${registro.idRegistro})" title="Ver detalle">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-control btn-eliminar" onclick="eliminarRegistro(${registro.idRegistro})" title="Eliminar">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Función para mostrar detalle de un registro
    window.verDetalle = function(idRegistro) {
        const registro = registrosCompletos.find(r => r.idRegistro === idRegistro);
        if (!registro) return;

        document.getElementById('detalleId').textContent = registro.idRegistro;
        document.getElementById('detalleEmpleado').textContent = registro.nombreEmpleado;
        document.getElementById('detalleDescripcion').textContent = registro.descripcion;
        document.getElementById('detalleFechaHora').textContent = formatearFechaHora(registro.fechaHora);
        document.getElementById('detalleIP').textContent = registro.ipOrigen;
        document.getElementById('detalleResultado').textContent = registro.resultado;

        const detalleErrorContainer = document.getElementById('detalleErrorContainer');
        if (registro.detallesError) {
            document.getElementById('detalleError').textContent = registro.detallesError;
            detalleErrorContainer.style.display = 'block';
        } else {
            detalleErrorContainer.style.display = 'none';
        }

        modalDetalle.style.display = 'block';
    };

    // Función para eliminar registro
    window.eliminarRegistro = function(idRegistro) {
        registroAEliminar = idRegistro;
        modalEliminar.style.display = 'block';
    };

    // Función para confirmar eliminación
    function confirmarEliminacion() {
        if (registroAEliminar) {
            // Eliminar del array local
            registrosCompletos = registrosCompletos.filter(r => r.idRegistro !== registroAEliminar);
            registrosFiltrados = registrosFiltrados.filter(r => r.idRegistro !== registroAEliminar);
            
            // TODO: Hacer llamada a la API para eliminar del servidor
            console.log('Eliminando registro:', registroAEliminar);
            
            renderizarTabla();
            actualizarPaginacion();
            cerrarModalEliminar();
            
            // Mostrar notificación
            mostrarNotificacion('Registro eliminado exitosamente', 'success');
        }
    }

    // Función para cerrar modal de eliminar
    function cerrarModalEliminar() {
        modalEliminar.style.display = 'none';
        registroAEliminar = null;
    }

    // Función para exportar registros
    async function exportarRegistros() {
        try {
            // Mostrar opciones de exportación
            const formato = await mostrarOpcionesExportacion();
            if (!formato) return;

            const response = await fetch('/seguridad/api/exportar-registros', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ formato })
            });

            const data = await response.json();
            
            if (data.success) {
                mostrarNotificacion(`Registros exportados en formato ${formato.toUpperCase()}`, 'success');
                // TODO: Descargar el archivo generado
            } else {
                mostrarNotificacion('Error al exportar registros', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('Error al exportar registros', 'error');
        }
    }

    // Función para mostrar opciones de exportación
    function mostrarOpcionesExportacion() {
        return new Promise((resolve) => {
            const opciones = ['pdf', 'excel'];
            const seleccion = prompt('Seleccione formato de exportación:\n1. PDF\n2. Excel\n\nIngrese el número:');
            
            if (seleccion === '1') {
                resolve('pdf');
            } else if (seleccion === '2') {
                resolve('excel');
            } else {
                resolve(null);
            }
        });
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
        const totalPaginas = Math.ceil(registrosFiltrados.length / registrosPorPagina);
        if (paginaActual < totalPaginas) {
            paginaActual++;
            renderizarTabla();
            actualizarPaginacion();
        }
    }

    function actualizarPaginacion() {
        const totalPaginas = Math.ceil(registrosFiltrados.length / registrosPorPagina) || 1;
        paginaActualSpan.textContent = paginaActual;
        totalPaginasSpan.textContent = totalPaginas;

        btnAnterior.disabled = paginaActual === 1;
        btnSiguiente.disabled = paginaActual === totalPaginas;
    }

    // Funciones auxiliares
    function formatearFechaHora(fechaHora) {
        const fecha = new Date(fechaHora);
        if (isNaN(fecha)) return fechaHora;
        
        const opciones = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        
        return fecha.toLocaleString('es-ES', opciones);
    }

    function mostrarCargando() {
        tablaRegistros.innerHTML = `
            <tr>
                <td colspan="7" class="loading-message">
                    <i class="fas fa-spinner fa-spin"></i> Cargando registros...
                </td>
            </tr>
        `;
    }

    function mostrarError(mensaje) {
        tablaRegistros.innerHTML = `
            <tr>
                <td colspan="7" class="no-registros" style="color: #e74c3c;">
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
