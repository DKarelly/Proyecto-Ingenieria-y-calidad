// Gestion Catalogo Servicio - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    cargarTiposServicio();
    cargarEspecialidades();
    cargarServicios();

    // Event listeners para filtros
    document.getElementById('btnBuscar').addEventListener('click', buscarServicios);
    document.getElementById('btnLimpiar').addEventListener('click', limpiarFiltros);

    // Event listeners para modales
    document.getElementById('btnRegistrarServicio').addEventListener('click', function() {
        cargarTiposServicioModal();
        document.getElementById('modalRegistrarServicio').classList.add('show');
    });

    // Cerrar modales
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            this.closest('.modal').classList.remove('show');
        });
    });

    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('show');
        }
    });

    // Formulario registrar servicio
    document.getElementById('formRegistrarServicio').addEventListener('submit', registrarServicio);

    // Botón cancelar en registrar
    document.getElementById('formRegistrarServicio').querySelector('button[type="button"]').addEventListener('click', function() {
        document.getElementById('modalRegistrarServicio').classList.remove('show');
    });
});

function cargarTiposServicio() {
    fetch('/admin/api/tipos-servicio')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('filtroTipoServicio');
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
    const tipoServicio = document.getElementById('filtroTipoServicio').value;
    const especialidad = document.getElementById('filtroEspecialidad').value;
    const termino = document.getElementById('filtroServicio').value.trim();

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
    document.getElementById('filtroTipoServicio').value = '';
    document.getElementById('filtroEspecialidad').value = '';
    document.getElementById('filtroServicio').value = '';
    cargarServicios();
}

function poblarTabla(servicios) {
    const tbody = document.getElementById('tabla-servicios-body');
    tbody.innerHTML = '';

        if (servicios.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="7" class="px-6 py-4 text-center text-gray-500">No se encontraron servicios</td>';
            tbody.appendChild(tr);
            return;
        }

    // Ordenar servicios por id_servicio de menor a mayor
    servicios.sort((a, b) => parseInt(a.id_servicio) - parseInt(b.id_servicio));

    servicios.forEach(servicio => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition-colors';

        const estadoClass = servicio.estado.toLowerCase() === 'activo' ? 'badge-activo' : 'badge-inactivo';
        
        /* COMPARAR CON EL ESTADO DE LA BD */
        const estadoText = servicio.estado.toLowerCase() === 'activo' ? 'Activo' : 'Inactivo';

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

    // Re-asignar event listeners a los botones
    asignarEventosBotones();
}

function cargarTiposServicioModal() {
    fetch('/admin/api/tipos-servicio')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('tipoServicio');
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
            document.getElementById('modalRegistrarServicio').classList.remove('show');
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
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            cargarServicioParaEditar(id);
        });
    });

    // Botones de eliminar
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', function() {
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
            document.getElementById('codigoServicio').value = servicio.id_servicio;
            document.getElementById('nombreServicioEditar').value = servicio.nombre;
            document.getElementById('descripcionServicioEditar').value = servicio.descripcion;
            document.getElementById('estadoServicioEditar').value = servicio.estado;

            // Mostrar el modal
            document.getElementById('modalModificarServicio').classList.add('show');
        })
        .catch(error => {
            console.error('Error cargando especialidades para editar:', error);
        });
}

function confirmarEliminarServicio(id_servicio) {
    if (confirm('¿Está seguro que desea desactivar este servicio?')) {
        fetch(`/admin/api/servicios/${id_servicio}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Servicio desactivado exitosamente');
                cargarServicios(); // Recargar la tabla
            } else {
                alert('Error al desactivar el servicio: ' + (result.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error eliminando servicio:', error);
            alert('Error al desactivar el servicio');
        });
    }
}

// Event listener para el formulario de modificar servicio
document.getElementById('formModificarServicio').addEventListener('submit', modificarServicio);

function modificarServicio(event) {
    event.preventDefault();

    const id_servicio = document.getElementById('codigoServicio').value;
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
            document.getElementById('modalModificarServicio').classList.remove('show');
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

// Event listener para el botón cancelar en modificar
document.getElementById('formModificarServicio').querySelector('button[type="button"]').addEventListener('click', function() {
    document.getElementById('modalModificarServicio').classList.remove('show');
});
