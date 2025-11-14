// Variables globales
let incidenciasData = [];

// Función para mostrar notificaciones toast
function showToast(message, type = 'success') {
    // Remover toasts existentes
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = '';
    if (type === 'success') {
        icon = '<i class="fas fa-check-circle text-green-500 text-xl"></i>';
    } else if (type === 'error') {
        icon = '<i class="fas fa-times-circle text-red-500 text-xl"></i>';
    } else if (type === 'warning') {
        icon = '<i class="fas fa-exclamation-triangle text-yellow-500 text-xl"></i>';
    }

    toast.innerHTML = `
        ${icon}
        <div class="flex-1">
            <p class="font-semibold text-gray-900">${message}</p>
        </div>
        <button class="text-gray-400 hover:text-gray-600 ml-2" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    document.body.appendChild(toast);

    // Auto-remover después de 5 segundos
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}

// Funcionalidad de modales
const modales = ['modalDetalle', 'modalResolver'];

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
        console.log('Cargando incidencias...');
        const response = await fetch('/seguridad/api/incidencias');
        console.log('Respuesta del API:', response.status, response.ok);
        if (response.ok) {
            incidenciasData = await response.json();
            console.log('Datos cargados:', incidenciasData);
            actualizarContadoresPrioridad();
            aplicarFiltrosDinamicos(); // Aplicar filtro de prioridad inicial
        } else {
            console.error('Error al cargar incidencias - Status:', response.status);
            const errorText = await response.text();
            console.error('Error response:', errorText);
        }
    } catch (error) {
        console.error('Error de conexión:', error);
    }
}

// Mostrar incidencias en la tabla
function mostrarIncidencias(incidencias) {
    const tbody = document.getElementById('tablaIncidencias');
    tbody.innerHTML = '';

    // Actualizar contador de resultados
    const contadorResultados = document.getElementById('contadorResultados');
    if (contadorResultados) {
        const texto = incidencias.length === 1 ? 'incidencia encontrada' : 'incidencias encontradas';
        contadorResultados.textContent = `${incidencias.length} ${texto}`;
    }

    // Actualizar badge de filtros activos
    actualizarBadgeFiltros();

    if (incidencias.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="px-6 py-8 text-center">
                    <div class="flex flex-col items-center gap-3">
                        <i class="fas fa-search text-gray-300 text-4xl"></i>
                        <p class="text-gray-500 font-medium">No se encontraron incidencias</p>
                        <p class="text-gray-400 text-sm">Intenta ajustar los filtros de búsqueda</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    incidencias.forEach(incidencia => {
        const estadoClass = incidencia.estado ? incidencia.estado.toLowerCase().replace(' ', '-') : 'abierta';
        const categoria = incidencia.categoria || 'Sin categoría';
        const prioridad = incidencia.prioridad || 'Media';
        const estado = incidencia.estado || 'Abierta';

        let prioridadBadge = '';
        if (prioridad === 'Alta') {
            prioridadBadge = '<span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">🔴 Alta</span>';
        } else if (prioridad === 'Media') {
            prioridadBadge = '<span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">🟡 Media</span>';
        } else {
            prioridadBadge = '<span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">🟢 Baja</span>';
        }

        // Determinar si mostrar botón de resolver
        // Solo mostrar en estados: Abierta, En Progreso, En proceso
        // NO mostrar en: Resuelta, Cerrada
        const estadosResueltos = ['Resuelta', 'Cerrada'];
        const puedeResolver = !estadosResueltos.includes(estado);
        
        let btnResolver = '';
        if (puedeResolver) {
            btnResolver = `
                <button class="btn-resolver action-btn action-btn-resolve" data-id="${incidencia.id_incidencia}" data-estado="${estado}">
                    <i class="fas fa-check"></i>
                    <span class="tooltip">Resolver</span>
                </button>
            `;
        }

        const row = `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-cyan-600">#${incidencia.id_incidencia}</td>
                <td class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title="${incidencia.descripcion}">${incidencia.descripcion}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${incidencia.fecha_registro}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${incidencia.paciente}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">${categoria}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${prioridadBadge}</td>

                <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium badge-${estadoClass}">
                        ${estado}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                    <div class="flex justify-center space-x-2">
                        <button class="btn-ver-detalle action-btn action-btn-view" data-id="${incidencia.id_incidencia}">
                            <i class="fas fa-eye"></i>
                            <span class="tooltip">Ver Detalle</span>
                        </button>
                        ${btnResolver}
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
        document.getElementById('detalleCategoria').textContent = incidencia.categoria || 'Sin categoría';
        document.getElementById('detalleDescripcion').textContent = incidencia.descripcion;
        document.getElementById('detalleEstado').textContent = incidencia.estado || 'Abierta';
        document.getElementById('detallePrioridad').textContent = incidencia.prioridad || 'Media';

        document.getElementById('detalleFechaResolucion').textContent = incidencia.fecha_resolucion || 'Pendiente';
        document.getElementById('detalleObservaciones').textContent = incidencia.observaciones || 'Sin observaciones';
        document.getElementById('modalDetalle').classList.add('show');
    }
}

// Mostrar editar incidencia
function mostrarEditarIncidencia(id) {
    const incidencia = incidenciasData.find(inc => inc.id_incidencia == id);
    if (incidencia) {
        document.getElementById('editId').value = id;
        document.getElementById('editDescripcion').value = incidencia.descripcion;
        document.getElementById('editEstado').value = incidencia.estado || 'Abierta';
        document.getElementById('editPrioridad').value = incidencia.prioridad || 'Media';
        document.getElementById('editCategoria').value = incidencia.categoria || 'Otro';
        

        // Cargar empleado si existe
        if (incidencia.empleado && incidencia.empleado !== 'Sin asignar') {
            document.getElementById('editResponsable').value = incidencia.empleado;
            document.getElementById('editResponsableId').value = incidencia.id_empleado || '';
            document.getElementById('editResponsableSeleccionado').innerHTML = `
                <span class="text-green-600">✓ Responsable: <strong>${incidencia.empleado}</strong></span>
            `;
        } else {
            document.getElementById('editResponsable').value = '';
            document.getElementById('editResponsableId').value = '';
            document.getElementById('editResponsableSeleccionado').textContent = '';
        }
        
        document.getElementById('editObservaciones').value = incidencia.observaciones || '';
        document.getElementById('modalEditar').classList.add('show');
    }
}

// Mostrar resolver incidencia
function mostrarResolverIncidencia(id) {
    const incidencia = incidenciasData.find(inc => inc.id_incidencia == id);
    
    if (!incidencia) {
        showToast('No se encontró la incidencia', 'error');
        return;
    }

    // Verificar que la incidencia no esté ya resuelta o cerrada
    const estado = incidencia.estado || 'Abierta';
    if (estado === 'Resuelta' || estado === 'Cerrada') {
        showToast('Esta incidencia ya está resuelta o cerrada', 'warning');
        return;
    }

    document.getElementById('resolverId').value = id;
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
            aplicarFiltrosDinamicos(); // Aplicar filtro al seleccionar
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
            aplicarFiltrosDinamicos(); // Aplicar filtro al seleccionar
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
    formEditar.onsubmit = async function(e) {
        e.preventDefault();

        const btnGuardar = formEditar.querySelector('button[type="submit"]');
        const btnGuardarOriginal = btnGuardar.innerHTML;

        // Deshabilitar botón y mostrar loader
        btnGuardar.disabled = true;
        btnGuardar.innerHTML = '<span class="btn-loader"></span> Guardando...';

        const idIncidencia = document.getElementById('editId').value;
        const idEmpleado = document.getElementById('editResponsableId').value;
        
        const datos = {
            id_incidencia: idIncidencia,
            descripcion: document.getElementById('editDescripcion').value,
            estado: document.getElementById('editEstado').value,
            prioridad: document.getElementById('editPrioridad').value,
            categoria: document.getElementById('editCategoria').value,
            id_empleado: idEmpleado || null, // Incluir ID del empleado
            observaciones: document.getElementById('editObservaciones').value
        };

        try {
            const response = await fetch(`/seguridad/api/incidencias/${idIncidencia}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datos)
            });

            if (response.ok) {
                await response.json();
                document.getElementById('modalEditar').classList.remove('show');
                showToast('Incidencia actualizada exitosamente', 'success');

                // Recargar las incidencias para reflejar los cambios
                await cargarIncidencias();
            } else {
                const error = await response.json();
                showToast(error.error || 'Error al actualizar la incidencia', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error de conexión al actualizar la incidencia', 'error');
        } finally {
            // Restaurar botón
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = btnGuardarOriginal;
        }
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

// Formulario de resolver incidencia
const formResolver = document.getElementById('formResolver');
if (formResolver) {
    formResolver.onsubmit = async function(e) {
        e.preventDefault();

        const btnConfirmar = document.getElementById('btnConfirmarResolver');
        const btnConfirmarOriginal = btnConfirmar.innerHTML;

        // Deshabilitar botón y mostrar loader
        btnConfirmar.disabled = true;
        btnConfirmar.innerHTML = '<span class="btn-loader"></span> Resolviendo...';

        const idIncidencia = document.getElementById('resolverId').value;

        try {
            const url = `/seguridad/api/incidencias/${idIncidencia}/resolver`;
            console.log('Enviando a URL:', url);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({})
            });

            console.log('Respuesta:', response.status);

            if (response.ok) {
                await response.json();
                document.getElementById('modalResolver').classList.remove('show');
                showToast('Incidencia marcada como resuelta exitosamente', 'success');

                // Recargar las incidencias para reflejar los cambios
                await cargarIncidencias();
            } else {
                const errorText = await response.text();
                console.error('Error response:', errorText);
                let errorMessage = 'Error al resolver la incidencia';
                try {
                    const error = JSON.parse(errorText);
                    errorMessage = error.error || errorMessage;
                } catch (e) {
                    // Si no es JSON, usar el texto como está
                }
                showToast(errorMessage, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error de conexión al resolver la incidencia', 'error');
        } finally {
            // Restaurar botón
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = btnConfirmarOriginal;
        }
    }
}

// Función para contar filtros activos
function contarFiltrosActivos() {
    let count = 0;
    const filtros = {
        paciente: document.getElementById('filtroPaciente').value.trim(),
        empleado: document.getElementById('filtroEmpleado').value.trim(),
        fecha_registro: document.getElementById('filtroFechaRegistro').value,
        fecha_resolucion: document.getElementById('filtroFechaResolucion').value,
        estado: document.getElementById('filtroEstado').value,
        categoria: document.getElementById('filtroCategoria').value
        // prioridad: controlada por pestañas, no incluir en conteo de filtros
    };

    Object.values(filtros).forEach(valor => {
        if (valor && valor.trim() !== '') count++;
    });

    return count;
}

// Función para actualizar badge de filtros activos
function actualizarBadgeFiltros() {
    const count = contarFiltrosActivos();
    const badge = document.getElementById('badgeFiltrosActivos');
    const numFiltros = document.getElementById('numFiltrosActivos');

    if (count > 0) {
        badge.classList.remove('hidden');
        numFiltros.textContent = count;
    } else {
        badge.classList.add('hidden');
    }
}

// Función para aplicar filtros dinámicamente
let timeoutFiltros;
async function aplicarFiltrosDinamicos() {
    clearTimeout(timeoutFiltros);

    timeoutFiltros = setTimeout(async () => {
        const filtros = {
            paciente: document.getElementById('filtroPaciente').value.trim(),
            empleado: document.getElementById('filtroEmpleado').value.trim(),
            fecha_registro: document.getElementById('filtroFechaRegistro').value,
            fecha_resolucion: document.getElementById('filtroFechaResolucion').value,
            estado: document.getElementById('filtroEstado').value,
            categoria: document.getElementById('filtroCategoria').value,
            prioridad: prioridadActiva // Usar la prioridad de la pestaña activa
        };

        // Actualizar badge de filtros
        actualizarBadgeFiltros();

        try {
            const response = await fetch('/seguridad/api/incidencias/buscar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify(filtros)
            });

            if (response.ok) {
                const incidenciasFiltradas = await response.json();
                mostrarIncidencias(incidenciasFiltradas);
                // NO actualizar incidenciasData aquí, mantener los datos originales para contadores
            } else {
                console.error('Error en la búsqueda');
                showToast('Error al aplicar filtros', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error de conexión al filtrar', 'error');
        }
    }, 500); // Esperar 500ms después de que el usuario deje de escribir
}

// Agregar eventos dinámicos a todos los filtros
// Para inputs de texto: usar 'input' para filtrar mientras escribes
document.getElementById('filtroPaciente').addEventListener('input', aplicarFiltrosDinamicos);
document.getElementById('filtroEmpleado').addEventListener('input', aplicarFiltrosDinamicos);

// Para selects y fechas: usar 'change' ya que se dispara inmediatamente al cambiar
document.getElementById('filtroFechaRegistro').addEventListener('change', aplicarFiltrosDinamicos);
document.getElementById('filtroFechaResolucion').addEventListener('change', aplicarFiltrosDinamicos);
document.getElementById('filtroEstado').addEventListener('change', aplicarFiltrosDinamicos);
document.getElementById('filtroCategoria').addEventListener('change', aplicarFiltrosDinamicos);

// Botón limpiar filtros
const btnLimpiar = document.getElementById('btnLimpiar');
if (btnLimpiar) {
    btnLimpiar.onclick = function() {
        document.getElementById('filtroPaciente').value = '';
        document.getElementById('filtroEmpleado').value = '';
        document.getElementById('filtroFechaRegistro').value = '';
        document.getElementById('filtroFechaResolucion').value = '';
        document.getElementById('filtroEstado').value = '';
        document.getElementById('filtroCategoria').value = '';
        document.getElementById('sugerenciasPaciente').classList.add('hidden');
        document.getElementById('sugerenciasEmpleado').classList.add('hidden');
        actualizarBadgeFiltros(); // Actualizar badge
        aplicarFiltrosDinamicos(); // Aplicar filtros de nuevo (con prioridad activa)
    }
}

// Formulario de búsqueda - Prevenir comportamiento por defecto
document.getElementById('formFiltros').addEventListener('submit', function(e) {
    e.preventDefault();
    // Los filtros ya se aplican dinámicamente, así que no necesitamos hacer nada aquí
});

// Inicializar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarIncidencias();
    inicializarPestanasPrioridad();
});

// ========== PESTAÑAS DE PRIORIDAD ==========
let prioridadActiva = 'Baja';

function inicializarPestanasPrioridad() {
    const tabs = document.querySelectorAll('.priority-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remover active de todos
            tabs.forEach(t => t.classList.remove('active'));
            
            // Agregar active al clickeado
            this.classList.add('active');
            
            // Actualizar prioridad activa
            prioridadActiva = this.getAttribute('data-priority');
            
            // Aplicar filtros con nueva prioridad
            aplicarFiltrosDinamicos();
        });
    });
    
    // Actualizar contadores al cargar
    actualizarContadoresPrioridad();
}

function actualizarContadoresPrioridad() {
    const contadores = {
        'Baja': 0,
        'Media': 0,
        'Alta': 0
    };
    
    incidenciasData.forEach(incidencia => {
        if (contadores.hasOwnProperty(incidencia.prioridad)) {
            contadores[incidencia.prioridad]++;
        }
    });
    
    // Actualizar badges
    document.querySelectorAll('.priority-tab').forEach(tab => {
        const prioridad = tab.getAttribute('data-priority');
        const badge = tab.querySelector('.badge-count');
        if (badge) {
            badge.textContent = contadores[prioridad] || 0;
        }
    });
}

// ========== BÚSQUEDA DINÁMICA EMPLEADOS EN MODAL EDITAR ==========
let timeoutEditEmpleado;
document.getElementById('editResponsable').addEventListener('input', function() {
    clearTimeout(timeoutEditEmpleado);
    const termino = this.value.trim();

    if (termino.length < 2) {
        document.getElementById('sugerenciasEditEmpleado').classList.add('hidden');
        document.getElementById('editResponsableId').value = '';
        document.getElementById('editResponsableSeleccionado').textContent = '';
        return;
    }

    timeoutEditEmpleado = setTimeout(async () => {
        try {
            const response = await fetch(`/seguridad/api/incidencias/buscar-empleados?termino=${encodeURIComponent(termino)}`);
            if (response.ok) {
                const empleados = await response.json();
                mostrarSugerenciasEditEmpleado(empleados);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }, 300);
});

function mostrarSugerenciasEditEmpleado(empleados) {
    const contenedor = document.getElementById('sugerenciasEditEmpleado');
    contenedor.innerHTML = '';

    if (empleados.length === 0) {
        contenedor.innerHTML = '<div class="px-4 py-3 text-gray-500 text-sm">No se encontraron empleados</div>';
        contenedor.classList.remove('hidden');
        return;
    }

    empleados.forEach(empleado => {
        const div = document.createElement('div');
        div.className = 'px-4 py-3 hover:bg-cyan-50 cursor-pointer border-b border-gray-100 last:border-0';
        div.innerHTML = `
            <div class="font-semibold text-gray-800">${empleado.nombre_completo}</div>
            <div class="text-sm text-gray-500">${empleado.cargo || 'Empleado'}</div>
        `;
        div.onclick = function() {
            document.getElementById('editResponsable').value = empleado.nombre_completo;
            document.getElementById('editResponsableId').value = empleado.id_empleado;
            document.getElementById('editResponsableSeleccionado').innerHTML = `
                <span class="text-green-600">✓ Responsable: <strong>${empleado.nombre_completo}</strong></span>
            `;
            contenedor.classList.add('hidden');
        };
        contenedor.appendChild(div);
    });

    contenedor.classList.remove('hidden');
}

// Ocultar sugerencias al hacer clic fuera
document.addEventListener('click', function(e) {
    if (!e.target.closest('#editResponsable') && !e.target.closest('#sugerenciasEditEmpleado')) {
        document.getElementById('sugerenciasEditEmpleado').classList.add('hidden');
    }
});
