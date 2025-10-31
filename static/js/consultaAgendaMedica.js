// consultaAgendaMedica.js - Funcionalidad para Consultar Agenda Médica

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const filtroEmpleado = document.getElementById('filtroEmpleado');
    const filtroFecha = document.getElementById('filtroFecha');
    const filtroServicio = document.getElementById('filtroServicio');
    const btnBuscar = document.getElementById('btnBuscar');
    const btnLimpiar = document.getElementById('btnLimpiar');
    const tablaAgenda = document.getElementById('tablaAgenda');

    // Variables para autocomplete
    let servicios = [];
    let empleadoSeleccionado = null;
    let servicioSeleccionado = null;
    let timeoutEmpleado;

    // Inicializar la página
    inicializar();

    function inicializar() {
        cargarServicios();
        cargarAgenda();

        // Configurar eventos
        configurarEventos();
    }

    function configurarEventos() {
        // Botón buscar
        btnBuscar.addEventListener('click', function() {
            cargarAgenda();
        });

        // Botón limpiar
        btnLimpiar.addEventListener('click', function() {
            limpiarFiltros();
            cargarAgenda();
        });

        // Autocomplete para empleado
        filtroEmpleado.addEventListener('input', function() {
            clearTimeout(timeoutEmpleado);
            const termino = this.value.trim();

            if (termino.length < 2) {
                ocultarSugerencias();
                return;
            }

            timeoutEmpleado = setTimeout(() => {
                buscarEmpleados(termino).then(sugerencias => {
                    mostrarSugerenciasEmpleados(sugerencias);
                });
            }, 100);
        });

        filtroEmpleado.addEventListener('blur', function() {
            setTimeout(() => ocultarSugerencias(), 200);
        });

        // Evento para servicio (select)
        filtroServicio.addEventListener('change', function() {
            servicioSeleccionado = servicios.find(s => s.id_servicio == this.value) || null;
        });
    }



    function cargarServicios() {
        fetch('/admin/api/servicios/buscar-agenda')
            .then(response => response.json())
            .then(data => {
                servicios = data;
                // Llenar el select de servicios
                const selectServicio = document.getElementById('filtroServicio');
                selectServicio.innerHTML = '<option value="">Todos los servicios</option>';
                data.forEach(servicio => {
                    const option = document.createElement('option');
                    option.value = servicio.id_servicio;
                    option.textContent = servicio.nombre;
                    selectServicio.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error al cargar servicios:', error);
                // Mostrar mensaje de error al usuario
                const selectServicio = document.getElementById('filtroServicio');
                selectServicio.innerHTML = '<option value="">Error al cargar servicios</option>';
            });
    }

    function cargarAgenda() {
        const data = {};

        // Buscar por nombre del empleado (si se ingresa texto)
        if (filtroEmpleado.value.trim()) {
            data.nombre_empleado = filtroEmpleado.value.trim();
        }

        // Buscar por fecha
        if (filtroFecha.value) {
            data.fecha = filtroFecha.value;
        }

        // Buscar por ID del servicio seleccionado
        if (servicioSeleccionado) {
            data.id_servicio = servicioSeleccionado.id_servicio;
        }

        fetch('/admin/api/agenda/consultar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                mostrarAgenda(data);
            })
            .catch(error => {
                console.error('Error al cargar agenda:', error);
                mostrarError('Error al cargar la agenda médica');
            });
    }

    function mostrarAgenda(agenda) {
        tablaAgenda.innerHTML = '';

        if (agenda.length === 0) {
            tablaAgenda.innerHTML = `
                <tr>
                    <td colspan="10" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-calendar-times text-4xl mb-4"></i>
                        <p>No se encontraron registros de agenda médica</p>
                    </td>
                </tr>
            `;
            return;
        }

        agenda.forEach(item => {
            const fila = crearFilaAgenda(item);
            tablaAgenda.appendChild(fila);
        });
    }

    function crearFilaAgenda(item) {
        const fila = document.createElement('tr');
        fila.className = 'hover:bg-gray-50 transition-colors';

        const estadoClass = obtenerClaseEstado(item.estado_atencion);

        fila.innerHTML = `
            <td class="px-6 py-4 text-sm text-gray-900 font-medium">${item.id_empleado}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${item.nombre_empleado}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${item.tipo}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${item.tipo_reserva}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${formatearFecha(item.fecha)}</td>
            <td class="px-6 py-4 text-sm text-gray-600 font-mono">${item.hora_inicio || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-600 font-mono">${item.hora_fin || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${item.servicio}</td>
            <td class="px-6 py-4 text-center">
                <span class="badge-${estadoClass} text-white text-xs font-semibold px-3 py-1 rounded-full">
                    ${item.estado_atencion || 'Sin estado'}
                </span>
            </td>
            <td class="px-6 py-4 text-center">
                <button class="btn-ver-detalle text-cyan-600 hover:text-cyan-800 mx-1 transition-colors"
                    title="Ver detalle" data-item='${JSON.stringify(item)}'>
                    <i class="fas fa-eye text-lg"></i>
                </button>
            </td>
        `;

        // Agregar evento al botón de detalle
        const btnDetalle = fila.querySelector('.btn-ver-detalle');
        btnDetalle.addEventListener('click', function() {
            mostrarDetalleAgenda(JSON.parse(this.dataset.item));
        });

        return fila;
    }

    function buscarEmpleados(termino) {
        return fetch(`/admin/api/empleados/buscar?termino=${encodeURIComponent(termino)}`)
            .then(response => response.json())
            .then(data => data)
            .catch(error => {
                console.error('Error al buscar empleados:', error);
                return [];
            });
    }

    function mostrarSugerencias(input, sugerencias, tipo) {
        ocultarSugerencias();

        if (sugerencias.length === 0) return;

        const contenedor = document.createElement('div');
        contenedor.className = 'absolute z-10 w-full bg-white border border-gray-300 rounded-lg shadow-lg mt-1 max-h-48 overflow-y-auto';
        contenedor.id = `sugerencias-${tipo}`;

        sugerencias.forEach(item => {
            const opcion = document.createElement('div');
            opcion.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm';

            if (tipo === 'empleado') {
                opcion.textContent = `${item.nombres} ${item.apellidos}`;
                opcion.addEventListener('click', () => {
                    input.value = opcion.textContent;
                    empleadoSeleccionado = item;
                    ocultarSugerencias();
                });
            } else if (tipo === 'servicio') {
                opcion.textContent = item.nombre;
                opcion.addEventListener('click', () => {
                    input.value = opcion.textContent;
                    servicioSeleccionado = item;
                    ocultarSugerencias();
                });
            }

            contenedor.appendChild(opcion);
        });

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(contenedor);
    }

    function mostrarSugerenciasEmpleados(sugerencias) {
        mostrarSugerencias(filtroEmpleado, sugerencias, 'empleado');
    }

    function ocultarSugerencias() {
        const sugerencias = document.querySelectorAll('[id^="sugerencias-"]');
        sugerencias.forEach(sug => sug.remove());
    }

    // Ocultar sugerencias al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#filtroEmpleado') && !e.target.closest('#sugerencias-empleado')) {
            ocultarSugerencias();
        }
    });

    function limpiarFiltros() {
        filtroEmpleado.value = '';
        filtroFecha.value = '';
        filtroServicio.value = '';
        empleadoSeleccionado = null;
        servicioSeleccionado = null;
        // Resetear el select de servicios
        filtroServicio.selectedIndex = 0;
    }

    function mostrarDetalleAgenda(item) {
        // Poblar los campos del modal con los datos del item
        document.getElementById('detalleIdEmpleado').textContent = item.id_empleado || '-';
        document.getElementById('detalleDoctor').textContent = item.nombre_empleado || '-';
        document.getElementById('detalleTipo').textContent = item.tipo || '-';
        document.getElementById('detalleTipoReserva').textContent = item.tipo_reserva || '-';
        document.getElementById('detalleFechaProgramada').textContent = formatearFecha(item.fecha) || '-';
        document.getElementById('detalleHoraInicio').textContent = item.hora_inicio || '-';
        document.getElementById('detalleHoraFin').textContent = item.hora_fin || '-';
        document.getElementById('detalleServicio').textContent = item.servicio || '-';
        document.getElementById('detalleEstadoAtencion').textContent = item.estado_atencion || '-';
        document.getElementById('detalleDiagnostico').textContent = item.diagnostico || '-';
        document.getElementById('detalleObservaciones').textContent = item.observaciones || '-';

        // Mostrar el modal
        const modal = document.getElementById('modalDetalle');
        modal.classList.add('show');

        // Configurar cierre del modal
        const closeBtn = modal.querySelector('.close');
        closeBtn.onclick = function() {
            modal.classList.remove('show');
        };

        // Cerrar al hacer clic fuera del contenido del modal
        window.onclick = function(event) {
            if (event.target === modal) {
                modal.classList.remove('show');
            }
        };
    }

    function obtenerDiaSemana(fecha) {
        if (!fecha) return '-';
        const date = new Date(fecha);
        return date.toLocaleDateString('es-ES', { weekday: 'long' });
    }

    function obtenerDisponibilidad(estado) {
        if (!estado) return 'No disponible';
        const estadoLower = estado.toLowerCase();
        if (estadoLower.includes('confirmad') || estadoLower.includes('activo')) {
            return 'Disponible';
        }
        return 'No disponible';
    }

    function obtenerClaseEstado(estado) {
        if (!estado) return 'inactivo';

        const estadoLower = estado.toLowerCase();
        if (estadoLower.includes('confirmad') || estadoLower.includes('activo')) return 'activo';
        if (estadoLower.includes('pendiente')) return 'pendiente';
        if (estadoLower.includes('cancelad') || estadoLower.includes('inactivo')) return 'inactivo';
        return 'activo'; // default
    }

    function formatearFecha(fecha) {
        if (!fecha) return '-';
        const date = new Date(fecha);
        return date.toLocaleDateString('es-ES');
    }

    function mostrarError(mensaje) {
        // Aquí puedes implementar un sistema de notificaciones
        console.error(mensaje);
        alert(mensaje);
    }
});
