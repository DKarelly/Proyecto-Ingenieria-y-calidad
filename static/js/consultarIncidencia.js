// Variables globales
let incidenciasData = [];

// Funcionalidad de modales
const modales = ['modalDetalle', 'modalEditar', 'modalResolver'];

modales.forEach(modalId => {
    const modal = document.getElementById(modalId);
    if (modal) {
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) {
            closeBtn.onclick = function() {
                modal.classList.remove('show');
            }
        }
    }
});

window.onclick = function(event) {
    modales.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal && event.target == modal) {
            modal.classList.remove('show');
        }
    });
}

// Cargar incidencias al inicio
async function cargarIncidencias() {
    try {
        const response = await fetch('/seguridad/api/incidencias');
        if (response.ok) {
            incidenciasData = await response.json();
            mostrarIncidencias(incidenciasData);
        } else {
            console.error('Error al cargar incidencias');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Mostrar incidencias en la tabla
function mostrarIncidencias(incidencias) {
    const tbody = document.getElementById('tablaIncidencias');
    tbody.innerHTML = '';

    if (incidencias.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    No se encontraron incidencias
                </td>
            </tr>
        `;
        return;
    }

    incidencias.forEach(incidencia => {
        const estadoClass = incidencia.estado ? incidencia.estado.toLowerCase().replace(' ', '-') : 'abierta';

        const row = `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${incidencia.id_incidencia}</td>
                <td class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title="${incidencia.descripcion}">${incidencia.descripcion}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${incidencia.fecha_registro}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${incidencia.paciente}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${incidencia.empleado}</td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium badge-${estadoClass}">
                        ${incidencia.estado || 'Abierta'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                    <div class="flex justify-center space-x-2">
                        <button class="btn-ver-detalle text-cyan-600 hover:text-cyan-900 p-1" data-id="${incidencia.id_incidencia}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-editar text-blue-600 hover:text-blue-900 p-1" data-id="${incidencia.id_incidencia}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-resolver text-green-600 hover:text-green-900 p-1" data-id="${incidencia.id_incidencia}">
                            <i class="fas fa-check"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });

    // Reasignar eventos a los botones
    asignarEventosBotones();
}

// Asignar eventos a botones dinámicos
function asignarEventosBotones() {
    // Botones de ver detalle
    document.querySelectorAll('.btn-ver-detalle').forEach(btn => {
        btn.onclick = function() {
            const id = this.getAttribute('data-id');
            mostrarDetalleIncidencia(id);
        }
    });

    // Botones de editar
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.onclick = function() {
            const id = this.getAttribute('data-id');
            mostrarEditarIncidencia(id);
        }
    });

    // Botones de resolver
    document.querySelectorAll('.btn-resolver').forEach(btn => {
        btn.onclick = function() {
            const id = this.getAttribute('data-id');
            mostrarResolverIncidencia(id);
        }
    });
}

// Mostrar detalle de incidencia
function mostrarDetalleIncidencia(id) {
    const incidencia = incidenciasData.find(inc => inc.id_incidencia == id);
    if (incidencia) {
        document.getElementById('detalleId').textContent = incidencia.id_incidencia;
        document.getElementById('detallePaciente').textContent = incidencia.paciente;
        document.getElementById('detalleFecha').textContent = incidencia.fecha_registro;
        document.getElementById('detalleCategoria').textContent = 'N/A'; // No hay categoria en la DB
        document.getElementById('detalleDescripcion').textContent = incidencia.descripcion;
        document.getElementById('detalleEstado').textContent = incidencia.estado || 'Abierta';
        document.getElementById('detallePrioridad').textContent = 'N/A'; // No hay prioridad en la DB
        document.getElementById('detalleResponsable').textContent = incidencia.empleado;
        document.getElementById('detalleFechaResolucion').textContent = incidencia.fecha_resolucion || 'Pendiente';
        document.getElementById('detalleObservaciones').textContent = incidencia.observaciones || 'Sin observaciones';
        document.getElementById('modalDetalle').classList.add('show');
    }
}

// Mostrar editar incidencia
function mostrarEditarIncidencia(id) {
    const incidencia = incidenciasData.find(inc => inc.id_incidencia == id);
    if (incidencia) {
        document.getElementById('editDescripcion').value = incidencia.descripcion;
        document.getElementById('editEstado').value = incidencia.estado || 'Abierta';
        document.getElementById('editPrioridad').value = 'N/A'; // No hay prioridad en la DB
        document.getElementById('editCategoria').value = 'N/A'; // No hay categoria en la DB
        document.getElementById('editResponsable').value = incidencia.empleado;
        document.getElementById('editObservaciones').value = incidencia.observaciones || '';
        document.getElementById('modalEditar').classList.add('show');
    }
}

// Mostrar resolver incidencia
function mostrarResolverIncidencia(id) {
    document.getElementById('modalResolver').classList.add('show');
}

// Autocompletado para pacientes
let timeoutPaciente;
document.getElementById('filtroPaciente').addEventListener('input', function() {
    clearTimeout(timeoutPaciente);
    const termino = this.value.trim();

    if (termino.length < 2) {
        document.getElementById('sugerenciasPaciente').classList.add('hidden');
        return;
    }

    timeoutPaciente = setTimeout(async () => {
        try {
            const response = await fetch(`/seguridad/api/incidencias/buscar-pacientes?termino=${encodeURIComponent(termino)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            if (response.ok) {
                const pacientes = await response.json();
                mostrarSugerenciasPaciente(pacientes);
            } else {
                console.error('Error en respuesta:', response.status);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }, 300);
});

function mostrarSugerenciasPaciente(pacientes) {
    const contenedor = document.getElementById('sugerenciasPaciente');
    contenedor.innerHTML = '';

    if (pacientes.length === 0) {
        contenedor.classList.add('hidden');
        return;
    }

    pacientes.forEach(paciente => {
        const div = document.createElement('div');
        div.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
        div.textContent = paciente.nombre_completo;
        div.onclick = function() {
            document.getElementById('filtroPaciente').value = paciente.nombre_completo;
            contenedor.classList.add('hidden');
        };
        contenedor.appendChild(div);
    });

    contenedor.classList.remove('hidden');
}

// Autocompletado para empleados
let timeoutEmpleado;
document.getElementById('filtroEmpleado').addEventListener('input', function() {
    clearTimeout(timeoutEmpleado);
    const termino = this.value.trim();

    if (termino.length < 2) {
        document.getElementById('sugerenciasEmpleado').classList.add('hidden');
        return;
    }

    timeoutEmpleado = setTimeout(async () => {
        try {
            const response = await fetch(`/seguridad/api/incidencias/buscar-empleados?termino=${encodeURIComponent(termino)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            if (response.ok) {
                const empleados = await response.json();
                mostrarSugerenciasEmpleado(empleados);
            } else {
                console.error('Error en respuesta:', response.status);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }, 300);
});

function mostrarSugerenciasEmpleado(empleados) {
    const contenedor = document.getElementById('sugerenciasEmpleado');
    contenedor.innerHTML = '';

    if (empleados.length === 0) {
        contenedor.classList.add('hidden');
        return;
    }

    empleados.forEach(empleado => {
        const div = document.createElement('div');
        div.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
        div.textContent = empleado.nombre_completo;
        div.onclick = function() {
            document.getElementById('filtroEmpleado').value = empleado.nombre_completo;
            contenedor.classList.add('hidden');
        };
        contenedor.appendChild(div);
    });

    contenedor.classList.remove('hidden');
}

// Ocultar sugerencias al hacer clic fuera
document.addEventListener('click', function(e) {
    if (!e.target.closest('#filtroPaciente') && !e.target.closest('#sugerenciasPaciente')) {
        document.getElementById('sugerenciasPaciente').classList.add('hidden');
    }
    if (!e.target.closest('#filtroEmpleado') && !e.target.closest('#sugerenciasEmpleado')) {
        document.getElementById('sugerenciasEmpleado').classList.add('hidden');
    }
});

// Formulario de edición
const formEditar = document.getElementById('formEditar');
if (formEditar) {
    formEditar.onsubmit = function(e) {
        e.preventDefault();
        document.getElementById('modalEditar').classList.remove('show');
        alert('Incidencia actualizada exitosamente');
        // Aquí iría la lógica para actualizar la incidencia
    }

    // Botón cancelar
    const btnCancelar = formEditar.querySelector('button[type="button"]');
    if (btnCancelar) {
        btnCancelar.onclick = function() {
            document.getElementById('modalEditar').classList.remove('show');
        }
    }
}

// Botones de resolver modal
const btnCancelarResolver = document.getElementById('btnCancelarResolver');
if (btnCancelarResolver) {
    btnCancelarResolver.onclick = function() {
        document.getElementById('modalResolver').classList.remove('show');
    }
}

const btnConfirmarResolver = document.getElementById('btnConfirmarResolver');
if (btnConfirmarResolver) {
    btnConfirmarResolver.onclick = function() {
        document.getElementById('modalResolver').classList.remove('show');
        alert('Incidencia marcada como resuelta');
        // Aquí iría la lógica para resolver la incidencia
    }
}

// Botón limpiar filtros
const btnLimpiar = document.getElementById('btnLimpiar');
if (btnLimpiar) {
    btnLimpiar.onclick = function() {
        document.getElementById('filtroPaciente').value = '';
        document.getElementById('filtroEmpleado').value = '';
        document.getElementById('filtroFechaRegistro').value = '';
        document.getElementById('filtroFechaResolucion').value = '';
        document.getElementById('filtroEstado').value = '';
        document.getElementById('sugerenciasPaciente').classList.add('hidden');
        document.getElementById('sugerenciasEmpleado').classList.add('hidden');
        cargarIncidencias(); // Recargar todas las incidencias
    }
}

// Formulario de búsqueda
document.getElementById('formFiltros').addEventListener('submit', async function(e) {
    e.preventDefault();

    const filtros = {
        paciente: document.getElementById('filtroPaciente').value.trim(),
        empleado: document.getElementById('filtroEmpleado').value.trim(),
        fecha_registro: document.getElementById('filtroFechaRegistro').value,
        fecha_resolucion: document.getElementById('filtroFechaResolucion').value,
        estado: document.getElementById('filtroEstado').value,
        categoria: document.getElementById('filtroCategoria') ? document.getElementById('filtroCategoria').value : '',
        prioridad: document.getElementById('filtroPrioridad') ? document.getElementById('filtroPrioridad').value : ''
    };

    try {
        const response = await fetch('/seguridad/api/incidencias/buscar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filtros)
        });

        if (response.ok) {
            const incidenciasFiltradas = await response.json();
            mostrarIncidencias(incidenciasFiltradas);
        } else {
            console.error('Error en la búsqueda');
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

// Inicializar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarIncidencias();
});
