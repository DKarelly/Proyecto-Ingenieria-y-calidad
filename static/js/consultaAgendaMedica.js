// consultaAgendaMedica.js - Funcionalidad para Consultar Agenda Médica con paginación
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const filtroEmpleado = document.getElementById('filtroEmpleado');
    const filtroFecha = document.getElementById('filtroFecha');
    const filtroServicio = document.getElementById('filtroServicio');
    const btnBuscar = document.getElementById('btnBuscar');
    const btnLimpiar = document.getElementById('btnLimpiar');
    const tablaAgenda = document.getElementById('tablaAgenda');

    // Variables globales
    let servicios = [];
    let empleadoSeleccionado = null;
    let servicioSeleccionado = null;
    let timeoutEmpleado;
    let agendaCompleta = []; // 👈 guardará todos los datos para paginar

    // Inicializar la página
    inicializar();

    function inicializar() {
        cargarServicios();
        cargarAgenda();
        configurarEventos();
    }

    function configurarEventos() {
        btnLimpiar.addEventListener('click', () => {
            limpiarFiltros();
            cargarAgenda();
        });

        // Autocomplete para empleado
        filtroEmpleado.addEventListener('input', function() {
            clearTimeout(timeoutEmpleado);
            const termino = this.value.trim();

            if (termino.length < 2) {
                ocultarSugerencias();
                filtrarAgendaDinamicamente();
                return;
            }

            timeoutEmpleado = setTimeout(() => {
                buscarEmpleados(termino).then(mostrarSugerenciasEmpleados);
            }, 150);
            filtrarAgendaDinamicamente();
        });

        filtroEmpleado.addEventListener('blur', () => setTimeout(ocultarSugerencias, 200));

        filtroFecha.addEventListener('input', filtrarAgendaDinamicamente);
        filtroServicio.addEventListener('change', function() {
            servicioSeleccionado = servicios.find(s => s.id_servicio == this.value) || null;
            filtrarAgendaDinamicamente();
        });
    }

    // 🔹 Cargar servicios para el filtro
    function cargarServicios() {
        fetch('/admin/api/servicios/buscar-agenda')
            .then(res => res.json())
            .then(data => {
                servicios = data;
                const selectServicio = document.getElementById('filtroServicio');
                selectServicio.innerHTML = '<option value="">Todos los servicios</option>';
                data.forEach(servicio => {
                    const option = document.createElement('option');
                    option.value = servicio.id_servicio;
                    option.textContent = servicio.nombre;
                    selectServicio.appendChild(option);
                });
            })
            .catch(err => {
                console.error('Error al cargar servicios:', err);
                document.getElementById('filtroServicio').innerHTML =
                    '<option value="">Error al cargar servicios</option>';
            });
    }

    // 🔹 Cargar la agenda médica (POST con filtros)
    function cargarAgenda() {
        const data = {};

        if (filtroEmpleado.value.trim()) data.nombre_empleado = filtroEmpleado.value.trim();
        if (filtroFecha.value) data.fecha = filtroFecha.value;
        if (servicioSeleccionado) data.id_servicio = servicioSeleccionado.id_servicio;

        fetch('/admin/api/agenda/consultar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
            .then(res => res.json())
            .then(data => {
                agendaCompleta = data || [];
                inicializarPaginacion({
                    datos: agendaCompleta,
                    registrosPorPagina: 20, // 👈 20 filas por página
                    renderFuncion: mostrarAgendaPaginada
                });
            })
            .catch(err => {
                console.error('Error al cargar agenda:', err);
                mostrarError('Error al cargar la agenda médica');
            });
    }

    // 🔹 Función que renderiza solo los datos de la página actual
    function mostrarAgendaPaginada(datosPagina) {
        tablaAgenda.innerHTML = '';

        if (!datosPagina || datosPagina.length === 0) {
            tablaAgenda.innerHTML = `
                <tr>
                    <td colspan="10" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-calendar-times text-4xl mb-4"></i>
                        <p>No se encontraron registros de agenda médica</p>
                    </td>
                </tr>`;
            return;
        }

        datosPagina.forEach(item => {
            tablaAgenda.appendChild(crearFilaAgenda(item));
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

        fila.querySelector('.btn-ver-detalle').addEventListener('click', function() {
            mostrarDetalleAgenda(JSON.parse(this.dataset.item));
        });

        return fila;
    }

    // 🧩 Funciones auxiliares (sin cambios)
    function buscarEmpleados(termino) {
        return fetch(`/admin/api/empleados/buscar?termino=${encodeURIComponent(termino)}`)
            .then(res => res.json())
            .catch(() => []);
    }

    function mostrarSugerencias(input, sugerencias, tipo) {
        ocultarSugerencias();
        if (sugerencias.length === 0) return;

        const contenedor = document.createElement('div');
        contenedor.className =
            'absolute z-10 w-full bg-white border border-gray-300 rounded-lg shadow-lg mt-1 max-h-48 overflow-y-auto';
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
            }

            contenedor.appendChild(opcion);
        });

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(contenedor);
    }

    function mostrarSugerenciasEmpleados(sugerencias) {
        mostrarSugerencias(filtroEmpleado, sugerencias, 'empleado');
    }

    function filtrarAgendaDinamicamente() {
        const filtroEmp = filtroEmpleado.value.toLowerCase().trim();
        const filtroFec = filtroFecha.value;
        const filtroServ = servicioSeleccionado ? servicioSeleccionado.id_servicio : null;

        const agendaFiltrada = agendaCompleta.filter(item => {
            const coincideEmpleado = !filtroEmp || (item.nombre_empleado && item.nombre_empleado.toLowerCase().includes(filtroEmp));
            const coincideFecha = !filtroFec || (item.fecha && item.fecha.startsWith(filtroFec));
            const coincideServicio = !filtroServ || (item.id_servicio == filtroServ);

            return coincideEmpleado && coincideFecha && coincideServicio;
        });

        // Actualizar la paginación con los datos filtrados
        inicializarPaginacion({
            datos: agendaFiltrada,
            registrosPorPagina: 20,
            renderFuncion: mostrarAgendaPaginada
        });
    }

    function ocultarSugerencias() {
        document.querySelectorAll('[id^="sugerencias-"]').forEach(s => s.remove());
    }

    function limpiarFiltros() {
        filtroEmpleado.value = '';
        filtroFecha.value = '';
        filtroServicio.value = '';
        empleadoSeleccionado = null;
        servicioSeleccionado = null;
        filtroServicio.selectedIndex = 0;
    }

    function mostrarDetalleAgenda(item) {
        //document.getElementById('detalleIdEmpleado').textContent = item.id_empleado || '-';
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

        const modal = document.getElementById('modalDetalle');
        modal.classList.add('show');

        modal.querySelector('.close').onclick = () => modal.classList.remove('show');
        window.onclick = e => {
            if (e.target === modal) modal.classList.remove('show');
        };
    }

    function obtenerClaseEstado(estado) {
        if (!estado) return 'inactivo';
        const e = estado.toLowerCase();
        if (e.includes('confirmad') || e.includes('activo')) return 'activo';
        if (e.includes('pendiente')) return 'pendiente';
        if (e.includes('cancelad') || e.includes('inactivo')) return 'inactivo';
        return 'activo';
    }

    function formatearFecha(fecha) {
        if (!fecha) return '-';
        const date = new Date(fecha);
        return date.toLocaleDateString('es-ES');
    }

    function mostrarError(mensaje) {
        console.error(mensaje);
        alert(mensaje);
    }
});
