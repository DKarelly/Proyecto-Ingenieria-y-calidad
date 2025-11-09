// Gestion Catalogo Servicio - JavaScript
let idServicioEliminar = null; // Variable global para el ID del servicio a eliminar

document.addEventListener('DOMContentLoaded', function () {
    cargarTiposServicio();
    cargarEspecialidades();
    cargarServicios();

    // Botón limpiar
    const btnLimpiar = document.getElementById('btnLimpiar');
    if (btnLimpiar) btnLimpiar.addEventListener('click', limpiarFiltros);

    // Debounce helper
    const debounce = (fn, delay = 300) => {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(null, args), delay);
        };
    };

    // Búsqueda dinámica: input + selects
    const inputBuscar = document.getElementById('filtroServicio');
    if (inputBuscar) inputBuscar.addEventListener('input', debounce(buscarServicios, 300));

    const selectTipo = document.getElementById('filtroTipoServicio');
    const selectEspecialidad = document.getElementById('filtroEspecialidad');
    if (selectTipo) selectTipo.addEventListener('change', buscarServicios);
    if (selectEspecialidad) selectEspecialidad.addEventListener('change', buscarServicios);

    // Abrir modal registrar
    const btnRegistrar = document.getElementById('btnRegistrarServicio');
    if (btnRegistrar) {
        btnRegistrar.addEventListener('click', function () {
            cargarTiposServicioModal();
            const modal = document.getElementById('modalRegistrarServicio');
            if (modal) modal.classList.add('show');
        });
    }

    // Cerrar modales (botones con clase .close)
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function () {
            const modal = this.closest('.modal');
            if (modal) modal.classList.remove('show');
        });
    });

    // Cerrar modal al clickear fuera del contenido
    window.addEventListener('click', function (event) {
        if (event.target.classList && event.target.classList.contains('modal')) {
            event.target.classList.remove('show');
        }
    });

    // Formulario registrar servicio
    const formRegistrar = document.getElementById('formRegistrarServicio');
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', registrarServicio);
        const cancelarReg = formRegistrar.querySelector('button[type="button"]');
        if (cancelarReg) cancelarReg.addEventListener('click', function () {
            const modal = document.getElementById('modalRegistrarServicio');
            if (modal) modal.classList.remove('show');
        });
    }

    // Formulario modificar servicio
    const formModificar = document.getElementById('formModificarServicio');
    if (formModificar) {
        formModificar.addEventListener('submit', modificarServicio);
        const cancelarMod = formModificar.querySelector('button[type="button"]');
        if (cancelarMod) cancelarMod.addEventListener('click', function () {
            const modal = document.getElementById('modalModificarServicio');
            if (modal) modal.classList.remove('show');
        });
    }

    // Modal eliminar servicio
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    if (btnCancelarEliminar) {
        btnCancelarEliminar.addEventListener('click', function () {
            const modal = document.getElementById('modalEliminar');
            if (modal) modal.classList.remove('show');
        });
    }

    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', eliminarServicio);
    }
});

function cargarTiposServicio() {
    fetch('/admin/api/tipos-servicio')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('filtroTipoServicio');
            if (!select) return;
            select.innerHTML = '<option value="">Todos los tipos</option>';

            data.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_servicio;
                option.textContent = tipo.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando tipos de servicio:', error);
        });
}

function cargarEspecialidades() {
    fetch('/admin/api/especialidades')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('filtroEspecialidad');
            if (!select) return;
            select.innerHTML = '<option value="">Todas las especialidades</option>';

            data.forEach(especialidad => {
                const option = document.createElement('option');
                option.value = especialidad.id_especialidad;
                option.textContent = especialidad.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando especialidades:', error);
        });
}

function cargarServicios() {
    fetch('/admin/api/servicios')
        .then(response => response.json())
        .then(data => {
            poblarTabla(data);
        })
        .catch(error => {
            console.error('Error cargando servicios:', error);
        });
}

function buscarServicios() {
    const tipoServicioEl = document.getElementById('filtroTipoServicio');
    const especialidadEl = document.getElementById('filtroEspecialidad');
    const terminoEl = document.getElementById('filtroServicio');

    const tipoServicio = tipoServicioEl ? tipoServicioEl.value : '';
    const especialidad = especialidadEl ? especialidadEl.value : '';
    const termino = terminoEl ? terminoEl.value.trim() : '';

    const data = {
        tipo_servicio: tipoServicio,
        especialidad: especialidad,
        termino: termino
    };

    fetch('/admin/api/servicios/buscar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            poblarTabla(data);
        })
        .catch(error => {
            console.error('Error buscando servicios:', error);
        });
}

function limpiarFiltros() {
    const tipoServicioEl = document.getElementById('filtroTipoServicio');
    const especialidadEl = document.getElementById('filtroEspecialidad');
    const terminoEl = document.getElementById('filtroServicio');

    if (tipoServicioEl) tipoServicioEl.value = '';
    if (especialidadEl) especialidadEl.value = '';
    if (terminoEl) terminoEl.value = '';
    cargarServicios();
}

// ======== PAGINACIÓN DINÁMICA SOLO CON NÚMEROS ========
// Variables globales
let paginaActual = 1;
const registrosPorPagina = 20;
let serviciosGlobal = []; // Guardar los servicios cargados

function poblarTabla(servicios) {
    const tbody = document.getElementById('tabla-servicios-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    serviciosGlobal = servicios; // Guardamos todos los servicios para paginar
    if (!servicios || servicios.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="7" class="px-6 py-4 text-center text-gray-500">No se encontraron servicios</td>';
        tbody.appendChild(tr);
        actualizarPaginacion(0);
        return;
    }

    // Ordenar servicios por ID
    servicios.sort((a, b) => parseInt(a.id_servicio) - parseInt(b.id_servicio));

    // Calcular índices para la página actual
    const totalRegistros = servicios.length;
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, totalRegistros);
    const serviciosPagina = servicios.slice(inicio, fin);

    serviciosPagina.forEach(servicio => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition-colors';

        const estadoClass = servicio.estado?.toLowerCase() === 'activo' ? 'badge-activo' : 'badge-inactivo';
        const estadoText = servicio.estado?.toLowerCase() === 'activo' ? 'Activo' : 'Inactivo';

        tr.innerHTML = `
            <td class="px-6 py-4 text-sm text-gray-900 font-medium">${servicio.id_servicio}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${servicio.nombre}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${servicio.descripcion || ''}</td>
            <td class="px-6 py-4 text-center">
                <span class="badge ${estadoClass} text-white text-xs font-semibold px-3 py-1 rounded-full">
                    ${estadoText}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">${servicio.tipo_servicio || ''}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${servicio.especialidad || ''}</td>
            <td class="px-6 py-4 text-center">
                <button class="btn-editar text-blue-600 hover:text-blue-800 mx-1 transition-colors" title="Editar" data-id="${servicio.id_servicio}">
                    <i class="fas fa-edit text-lg"></i>
                </button>
                <button class="btn-eliminar text-red-600 hover:text-red-800 mx-1 transition-colors" title="Eliminar" data-id="${servicio.id_servicio}">
                    <i class="fas fa-trash-alt text-lg"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Reasignar eventos
    asignarEventosBotones();

    // Actualizar paginación visual
    actualizarPaginacion(totalRegistros);
}

function actualizarPaginacion(totalRegistros) {
    const paginacionContainer = document.getElementById('paginacionNumeros');
    const inicioRango = document.getElementById('inicio-rango');
    const finRango = document.getElementById('fin-rango');
    const totalRegistrosSpan = document.getElementById('total-registros');

    const totalPaginas = Math.ceil(totalRegistros / registrosPorPagina);
    paginacionContainer.innerHTML = '';

    // Mostrar rango y total
    const inicio = totalRegistros === 0 ? 0 : (paginaActual - 1) * registrosPorPagina + 1;
    const fin = Math.min(paginaActual * registrosPorPagina, totalRegistros);
    inicioRango.textContent = inicio;
    finRango.textContent = fin;
    totalRegistrosSpan.textContent = totalRegistros;

    if (totalPaginas <= 1) return; // No mostrar si solo hay 1 página

    // Limitar cantidad de botones visibles (ej. máx 6)
    const maxVisible = 6;
    let inicioPagina = Math.max(1, paginaActual - 2);
    let finPagina = Math.min(totalPaginas, inicioPagina + maxVisible - 1);

    if (finPagina - inicioPagina < maxVisible - 1) {
        inicioPagina = Math.max(1, finPagina - maxVisible + 1);
    }

    // Crear botones de página
    for (let i = inicioPagina; i <= finPagina; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === paginaActual
                ? 'bg-cyan-600 text-white border-cyan-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', () => cambiarPagina(i));
        paginacionContainer.appendChild(btn);
    }

    // Agregar "..." si hay más páginas
    if (finPagina < totalPaginas) {
        const span = document.createElement('span');
        span.className = 'px-2 text-gray-500';
        span.textContent = '...';
        paginacionContainer.appendChild(span);

        const ultimoBtn = document.createElement('button');
        ultimoBtn.textContent = totalPaginas;
        ultimoBtn.className =
            'px-3 py-2 text-sm font-medium border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-100';
        ultimoBtn.addEventListener('click', () => cambiarPagina(totalPaginas));
        paginacionContainer.appendChild(ultimoBtn);
    }
}

function cambiarPagina(numeroPagina) {
    paginaActual = numeroPagina;
    poblarTabla(serviciosGlobal);
}

// Agregar estos event listeners al DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // ... código existente ...

    // Eventos de paginación
    document.getElementById('btn-anterior').addEventListener('click', () => {
        if (paginaActual > 1) {
            paginaActual--;
            buscarServicios();
        }
    });

    document.getElementById('btn-siguiente').addEventListener('click', () => {
        paginaActual++;
        buscarServicios();
    });

    // Resetear página al usar filtros
    document.getElementById('filtroServicio').addEventListener('input', () => {
        paginaActual = 1;
    });
    document.getElementById('filtroTipoServicio').addEventListener('change', () => {
        paginaActual = 1;
    });
    document.getElementById('filtroEspecialidad').addEventListener('change', () => {
        paginaActual = 1;
    });
    document.getElementById('btnLimpiar').addEventListener('click', () => {
        paginaActual = 1;
    });
});

function cargarTiposServicioModal() {
    fetch('/admin/api/tipos-servicio')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('tipoServicio');
            if (!select) return;
            select.innerHTML = '<option value="">Seleccione tipo de servicio</option>';

            data.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_servicio;
                option.textContent = tipo.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando tipos de servicio para modal:', error);
        });

    // Cargar especialidades para el modal de registro
    fetch('/admin/api/especialidades')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('especialidadServicio');
            if (!select) return;
            select.innerHTML = '<option value="">Seleccione especialidad (opcional)</option>';

            data.forEach(especialidad => {
                const option = document.createElement('option');
                option.value = especialidad.id_especialidad;
                option.textContent = especialidad.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando especialidades para modal:', error);
        });
}

function registrarServicio(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = {
        nombre: formData.get('nombreServicio'),
        descripcion: formData.get('descripcionServicio'),
        estado: formData.get('estadoServicio'),
        id_tipo_servicio: formData.get('tipoServicio'),
        id_especialidad: formData.get('especialidadServicio') || null
    };

    console.log('Datos a enviar:', data); // Debug

    fetch('/admin/api/servicios', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            console.log('Respuesta del servidor:', result); // Debug
            if (result.success) {
                alert('Servicio registrado exitosamente');
                const modal = document.getElementById('modalRegistrarServicio');
                if (modal) modal.classList.remove('show');
                event.target.reset();
                cargarServicios(); // Recargar la tabla
            } else {
                alert('Error al registrar el servicio: ' + (result.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error registrando servicio:', error);
            alert('Error al registrar el servicio');
        });
}

function asignarEventosBotones() {
    // Botones de editar
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            cargarServicioParaEditar(id);
        });
    });

    // Botones de eliminar
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            confirmarEliminarServicio(id);
        });
    });
}

function cargarServicioParaEditar(id_servicio) {
    fetch(`/admin/api/servicios/${id_servicio}`)
        .then(response => response.json())
        .then(servicio => {
            // Cargar tipos de servicio y especialidades para el select de edición, luego rellenar
            cargarTiposServicioEditar(servicio);
        })
        .catch(error => {
            console.error('Error cargando servicio para editar:', error);
            alert('Error al cargar el servicio');
        });
}

function cargarTiposServicioEditar(servicio) {
    // Cargar tipos de servicio
    fetch('/admin/api/tipos-servicio')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('tipoServicioEditar');
            if (!select) return;
            select.innerHTML = '<option value="">Seleccione tipo de servicio</option>';

            data.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_servicio;
                option.textContent = tipo.nombre;
                select.appendChild(option);
            });

            // Seleccionar el tipo de servicio actual
            select.value = servicio.id_tipo_servicio;
        })
        .catch(error => {
            console.error('Error cargando tipos de servicio para editar:', error);
        });

    // Cargar especialidades para el modal de edición
    fetch('/admin/api/especialidades')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('especialidadServicioEditar');
            if (!select) return;
            select.innerHTML = '<option value="">Seleccione especialidad (opcional)</option>';

            data.forEach(especialidad => {
                const option = document.createElement('option');
                option.value = especialidad.id_especialidad;
                option.textContent = especialidad.nombre;
                select.appendChild(option);
            });

            // Seleccionar la especialidad actual
            select.value = servicio.id_especialidad || '';

            // Rellenar los demás campos después de cargar las opciones
            const codigoEl = document.getElementById('codigoServicio');
            if (codigoEl) codigoEl.value = servicio.id_servicio;

            const nombreEl = document.getElementById('nombreServicioEditar');
            if (nombreEl) nombreEl.value = servicio.nombre;

            const descripcionEl = document.getElementById('descripcionServicioEditar');
            if (descripcionEl) descripcionEl.value = servicio.descripcion;

            const estadoEl = document.getElementById('estadoServicioEditar');
            if (estadoEl) estadoEl.value = servicio.estado;

            // Mostrar el modal
            const modal = document.getElementById('modalModificarServicio');
            if (modal) modal.classList.add('show');
        })
        .catch(error => {
            console.error('Error cargando especialidades para editar:', error);
        });
}

function confirmarEliminarServicio(id_servicio) {
    idServicioEliminar = id_servicio; // Guardar el ID en la variable global
    const modal = document.getElementById('modalEliminar');
    if (modal) modal.classList.add('show');
}

function eliminarServicio() {
    if (!idServicioEliminar) return;

    const data = {
        estado: 'Inactivo'
    };

    fetch(`/admin/api/servicios/${idServicioEliminar}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Servicio desactivado exitosamente');
                const modal = document.getElementById('modalEliminar');
                if (modal) modal.classList.remove('show');
                cargarServicios(); // Recargar la tabla
            } else {
                alert('Error al desactivar el servicio: ' + (result.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error desactivando servicio:', error);
            alert('Error al desactivar el servicio');
        });
}

function modificarServicio(event) {
    event.preventDefault();

    const id_servicio_el = document.getElementById('codigoServicio');
    const id_servicio = id_servicio_el ? id_servicio_el.value : null;
    if (!id_servicio) {
        alert('ID de servicio no encontrado');
        return;
    }

    const formData = new FormData(event.target);
    const data = {
        nombre: formData.get('nombreServicioEditar'),
        descripcion: formData.get('descripcionServicioEditar'),
        estado: formData.get('estadoServicioEditar'),
        id_tipo_servicio: formData.get('tipoServicioEditar'),
        id_especialidad: formData.get('especialidadServicioEditar') || null
    };

    fetch(`/admin/api/servicios/${id_servicio}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Servicio modificado exitosamente');
                const modal = document.getElementById('modalModificarServicio');
                if (modal) modal.classList.remove('show');
                cargarServicios(); // Recargar la tabla
            } else {
                alert('Error al modificar el servicio: ' + (result.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error modificando servicio:', error);
            alert('Error al modificar el servicio');
        });
}