// Gestion Recursos Fisicos - JavaScript
let todosLosRecursos = []; // Almacena todos los recursos para búsqueda dinámica

document.addEventListener('DOMContentLoaded', function() {
    cargarRecursos();

    // Event listener para búsqueda dinámica
    const searchInput = document.getElementById('search-recurso');
    const clearSearchBtn = document.getElementById('clear-search-recurso');

    searchInput.addEventListener('input', function() {
        const termino = this.value.trim();

        // Mostrar/ocultar botón de limpiar
        if (termino) {
            clearSearchBtn.classList.remove('hidden');
        } else {
            clearSearchBtn.classList.add('hidden');
        }

        // Búsqueda dinámica en tiempo real
        filtrarRecursos(termino);
    });

    clearSearchBtn.addEventListener('click', function() {
        searchInput.value = '';
        this.classList.add('hidden');
        filtrarRecursos('');
        searchInput.focus();
    });

    // Event listeners para modales
    document.getElementById('btnRegistrarRecurso').addEventListener('click', function() {
        cargarTiposRecursoModal();
        document.getElementById('modalRegistrarRecurso').classList.add('show');
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

    // Formulario registrar recurso
    document.getElementById('formRegistrarRecurso').addEventListener('submit', registrarRecurso);

    // Botón cancelar en registrar
    document.getElementById('formRegistrarRecurso').querySelector('button[type="button"]').addEventListener('click', function() {
        document.getElementById('modalRegistrarRecurso').classList.remove('show');
    });
});

function cargarTiposRecurso() {
    fetch('/admin/api/tipos-recurso')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('filtroTipo');
            select.innerHTML = '<option value="">Todos los tipos</option>';

            data.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_recurso;
                option.textContent = tipo.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando tipos de recurso:', error);
        });
}

function cargarRecursos() {
    fetch('/admin/api/recursos')
        .then(response => response.json())
        .then(data => {
            todosLosRecursos = data; // guarda copia completa

            // Usa la paginación genérica
            inicializarPaginacion({
                datos: todosLosRecursos,
                registrosPorPagina: 8,
                renderFuncion: poblarTabla
            });
        })
        .catch(error => {
            console.error('Error cargando recursos:', error);
        });
}

function buscarRecursos() {
    const tipoRecurso = document.getElementById('filtroTipo').value;
    const termino = document.getElementById('filtroRecurso').value.trim();

    const data = {
        tipo_recurso: tipoRecurso,
        termino: termino
    };

    fetch('/admin/api/recursos/buscar', {
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
        console.error('Error buscando recursos:', error);
    });
}

function limpiarFiltros() {
    document.getElementById('filtroTipo').value = '';
    document.getElementById('filtroRecurso').value = '';
    cargarRecursos();
}

function poblarTabla(recursos) {
    const tbody = document.getElementById('tabla-recursos-body');
    tbody.innerHTML = '';

    if (recursos.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="5" class="px-6 py-4 text-center text-gray-500">No se encontraron recursos</td>';
        tbody.appendChild(tr);
        return;
    }

    // Ordenar recursos por id_recurso de menor a mayor
    recursos.sort((a, b) => parseInt(a.id_recurso) - parseInt(b.id_recurso));

    recursos.forEach(recurso => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition-colors';

        const estadoClass = recurso.estado.toLowerCase() === 'activo' ? 'badge-activo' : 'badge-inactivo';
        const estadoText = recurso.estado.toLowerCase() === 'activo' ? 'Activo' : 'Inactivo';

        tr.innerHTML = `
            <td class="px-6 py-4 text-sm text-gray-900 font-medium">${recurso.id_recurso}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${recurso.nombre}</td>
            <td class="px-6 py-4 text-center">
                <span class="badge ${estadoClass} text-white text-xs font-semibold px-3 py-1 rounded-full">
                    ${estadoText}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">${recurso.tipo_recurso || ''}</td>
            <td class="px-6 py-4 text-center">
                <button class="btn-editar text-blue-600 hover:text-blue-800 mx-1 transition-colors" title="Editar" data-id="${recurso.id_recurso}">
                    <i class="fas fa-edit text-lg"></i>
                </button>
                <button class="btn-eliminar text-red-600 hover:text-red-800 mx-1 transition-colors" title="Eliminar" data-id="${recurso.id_recurso}">
                    <i class="fas fa-trash-alt text-lg"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });

    // Re-asignar event listeners a los botones
    asignarEventosBotones();
}

function cargarTiposRecursoModal() {
    fetch('/admin/api/tipos-recurso')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('tipoRecurso');
            select.innerHTML = '<option value="" disabled selected>Seleccione un tipo</option>';

            data.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_recurso;
                option.textContent = tipo.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando tipos de recurso para modal:', error);
        });
}

function registrarRecurso(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = {
        nombre: formData.get('nombreRecurso'),
        estado: formData.get('estadoRecurso'),
        id_tipo_recurso: formData.get('tipoRecurso')
    };

    console.log('Datos a enviar:', data); // Debug

    fetch('/admin/api/recursos', {
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
            alert('Recurso registrado exitosamente');
            document.getElementById('modalRegistrarRecurso').classList.remove('show');
            event.target.reset();
            cargarRecursos(); // Recargar la tabla
        } else {
            alert('Error al registrar el recurso: ' + (result.message || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error registrando recurso:', error);
        alert('Error al registrar el recurso');
    });
}

function asignarEventosBotones() {
    // Botones de editar
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            cargarRecursoParaEditar(id);
        });
    });

    // Botones de eliminar
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            confirmarEliminarRecurso(id);
        });
    });
}

function cargarRecursoParaEditar(id_recurso) {
    fetch(`/admin/api/recursos/${id_recurso}`)
        .then(response => response.json())
        .then(recurso => {
            // Rellenar el modal de edición
            document.getElementById('codigoRecurso').value = recurso.id_recurso;
            document.getElementById('nombreRecursoEdit').value = recurso.nombre;
            document.getElementById('estadoRecursoEdit').value = recurso.estado;
            document.getElementById('tipoRecursoEdit').value = recurso.id_tipo_recurso;

            // Cargar tipos de recurso para el select de edición
            cargarTiposRecursoEditar();

            // Mostrar el modal
            document.getElementById('modalModificarRecurso').classList.add('show');
        })
        .catch(error => {
            console.error('Error cargando recurso para editar:', error);
            alert('Error al cargar el recurso');
        });
}

function cargarTiposRecursoEditar() {
    fetch('/admin/api/tipos-recurso')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('tipoRecursoEdit');
            select.innerHTML = '<option value="" disabled selected>Seleccione un tipo</option>';

            data.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_recurso;
                option.textContent = tipo.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando tipos de recurso para editar:', error);
        });
}

function confirmarEliminarRecurso(id_recurso) {
    if (confirm('¿Está seguro que desea desactivar este recurso?')) {
        fetch(`/admin/api/recursos/${id_recurso}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Recurso desactivado exitosamente');
                cargarRecursos(); // Recargar la tabla
            } else {
                alert('Error al desactivar el recurso: ' + (result.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error eliminando recurso:', error);
            alert('Error al desactivar el recurso');
        });
    }
}

// Event listener para el formulario de modificar recurso
document.getElementById('formModificarRecurso').addEventListener('submit', modificarRecurso);

function modificarRecurso(event) {
    event.preventDefault();

    const id_recurso = document.getElementById('codigoRecurso').value;
    const formData = new FormData(event.target);
    const data = {
        nombre: formData.get('nombreRecursoEdit'),
        estado: formData.get('estadoRecursoEdit'),
        id_tipo_recurso: formData.get('tipoRecursoEdit')
    };

    fetch(`/admin/api/recursos/${id_recurso}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Recurso modificado exitosamente');
            document.getElementById('modalModificarRecurso').classList.remove('show');
            cargarRecursos(); // Recargar la tabla
        } else {
            alert('Error al modificar el recurso: ' + (result.message || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error modificando recurso:', error);
        alert('Error al modificar el recurso');
    });
}

// Event listener para el botón cancelar en modificar
document.getElementById('formModificarRecurso').querySelector('button[type="button"]').addEventListener('click', function() {
    document.getElementById('modalModificarRecurso').classList.remove('show');
});
