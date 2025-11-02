// Variables globales
let incidenciasData = [];
let empleadosData = [];
let incidenciaSeleccionada = null;
let empleadoSeleccionado = null;

// Cargar datos al iniciar
document.addEventListener('DOMContentLoaded', function() {
    inicializarPagina();
});

// Inicializar página
async function inicializarPagina() {
    mostrarCargando(true);
    await Promise.all([
        cargarIncidencias(),
        cargarEmpleados()
    ]);
    mostrarCargando(false);
    configurarEventListeners();
}

// Configurar event listeners
function configurarEventListeners() {
    // Búsqueda de incidencias
    const inputBusqueda = document.getElementById('inputBusqueda');
    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', debounce(filtrarIncidencias, 300));
    }

    // Filtro de prioridad
    const filtroPrioridad = document.getElementById('filtroPrioridad');
    if (filtroPrioridad) {
        filtroPrioridad.addEventListener('change', filtrarIncidencias);
    }

    // Búsqueda de empleados en el modal
    const buscarEmpleadoInput = document.getElementById('buscarEmpleadoInput');
    if (buscarEmpleadoInput) {
        buscarEmpleadoInput.addEventListener('input', debounce(filtrarEmpleados, 300));
    }

    // Botón confirmar asignación
    const btnConfirmarAsignacion = document.getElementById('btnConfirmarAsignacion');
    if (btnConfirmarAsignacion) {
        btnConfirmarAsignacion.addEventListener('click', confirmarAsignacion);
    }
}

// Función debounce para optimizar búsquedas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// 1. LISTAR INCIDENCIAS
// ============================================
async function cargarIncidencias() {
    try {
        const response = await fetch('/seguridad/api/incidencias/sin-asignar');
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const data = await response.json();
        
        // Validar que los datos sean un array
        if (!Array.isArray(data)) {
            console.error('Los datos recibidos no son un array:', data);
            throw new Error('Formato de datos inválido');
        }
        
        // Filtrar incidencias válidas
        incidenciasData = data.filter(inc => inc && inc.id_incidencia);
        
        if (incidenciasData.length !== data.length) {
            console.warn(`Se filtraron ${data.length - incidenciasData.length} incidencias inválidas`);
        }
        
        mostrarIncidencias();
    } catch (error) {
        console.error('Error al cargar incidencias:', error);
        mostrarNotificacion('Error al cargar las incidencias. Por favor, intente nuevamente.', 'error');
        incidenciasData = [];
        mostrarIncidencias();
    }
}

// Mostrar incidencias en la tabla
function mostrarIncidencias() {
    const tbody = document.getElementById('tablaIncidencias');
    tbody.innerHTML = '';

    if (incidenciasData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-3 text-gray-300"></i>
                    <p class="text-lg">No se encontraron incidencias sin asignar</p>
                </td>
            </tr>
        `;
        return;
    }

    incidenciasData.forEach(incidencia => {
        // Validar que la incidencia existe y tiene ID
        if (!incidencia || !incidencia.id_incidencia) {
            console.warn('Incidencia inválida encontrada:', incidencia);
            return;
        }

        // Asegurar que prioridad tenga un valor por defecto
        const prioridad = incidencia.prioridad || 'Media';
        const categoria = incidencia.categoria || 'Sin categoría';
        const descripcion = incidencia.descripcion || 'Sin descripción';
        const paciente = incidencia.paciente || 'N/A';

        // Determinar el color de prioridad
        let badgePrioridad = '';
        let iconoPrioridad = '';
        switch(prioridad) {
            case 'Alta':
                badgePrioridad = 'bg-red-100 text-red-700';
                iconoPrioridad = 'fa-circle-exclamation';
                break;
            case 'Media':
                badgePrioridad = 'bg-amber-100 text-amber-700';
                iconoPrioridad = 'fa-exclamation';
                break;
            case 'Baja':
            default:
                badgePrioridad = 'bg-green-100 text-green-700';
                iconoPrioridad = 'fa-check-circle';
        }

        const row = document.createElement('tr');
        row.className = 'hover:bg-cyan-50 transition-colors cursor-pointer';
        row.innerHTML = `
            <td class="px-6 py-4 text-sm font-bold text-cyan-600">#${incidencia.id_incidencia}</td>
            <td class="px-6 py-4 text-sm text-gray-700">${formatearFecha(incidencia.fecha_registro)}</td>
            <td class="px-6 py-4 text-sm text-gray-700">
                <div class="max-w-xs">
                    <p class="line-clamp-2" title="${descripcion}">${descripcion}</p>
                </div>
            </td>
            <td class="px-6 py-4 text-sm">
                <span class="px-3 py-1.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 inline-flex items-center gap-1">
                    <i class="fas fa-tag"></i>
                    ${categoria}
                </span>
            </td>
            <td class="px-6 py-4 text-sm">
                <span class="px-3 py-1.5 rounded-full text-xs font-semibold ${badgePrioridad} inline-flex items-center gap-1">
                    <i class="fas ${iconoPrioridad}"></i>
                    ${prioridad}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-700 font-medium">${paciente}</td>
            <td class="px-6 py-4 text-center">
                <button class="btn-asignar px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all shadow-sm hover:shadow-md inline-flex items-center gap-2"
                        data-id="${incidencia.id_incidencia}"
                        data-prioridad="${prioridad}"
                        title="Asignar responsable">
                    <i class="fas fa-user-plus"></i>
                    Asignar
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    // Agregar eventos a los botones de asignar
    document.querySelectorAll('.btn-asignar').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const idIncidencia = this.getAttribute('data-id');
            abrirModalAsignar(idIncidencia);
        });
    });

    // Actualizar contador
    actualizarContadorResultados();
}

// ============================================
// 2. BUSCAR INCIDENCIA POR NOMBRE/ID
// ============================================
function filtrarIncidencias() {
    const inputBusqueda = document.getElementById('inputBusqueda');
    const filtroPrioridad = document.getElementById('filtroPrioridad');

    const termino = inputBusqueda ? inputBusqueda.value.toLowerCase() : '';
    const prioridadFiltro = filtroPrioridad ? filtroPrioridad.value : '';

    const filas = document.querySelectorAll('#tablaIncidencias tr');
    let visibles = 0;

    filas.forEach(fila => {
        // Evitar filtrar la fila de "no se encontraron resultados"
        if (!fila.querySelector('.btn-asignar')) {
            return;
        }

        const texto = fila.textContent.toLowerCase();

        const incidenciaId = fila.querySelector('.btn-asignar')?.getAttribute('data-id');
        const incidencia = incidenciasData.find(inc => inc && inc.id_incidencia == incidenciaId);

        // Si no se encuentra la incidencia, usar valores predeterminados
        const prioridadActual = incidencia ? (incidencia.prioridad || 'Media') : 'Media';

        const coincideBusqueda = !termino || texto.includes(termino);
        const coincidePrioridad = !prioridadFiltro || prioridadActual === prioridadFiltro;

        if (coincideBusqueda && coincidePrioridad) {
            fila.style.display = '';
            visibles++;
        } else {
            fila.style.display = 'none';
        }
    });

    actualizarContadorResultados(visibles);
}

function actualizarContadorResultados(visibles = null) {
    const contador = document.getElementById('contadorResultados');
    if (!contador) return;

    const totalIncidencias = incidenciasData.length;
    const cantidadVisible = visibles !== null ? visibles : totalIncidencias;

    if (cantidadVisible === 0) {
        contador.innerHTML = '<i class="fas fa-exclamation-circle mr-1 text-amber-500"></i>No se encontraron incidencias sin asignar';
    } else if (cantidadVisible === totalIncidencias) {
        contador.innerHTML = `<i class="fas fa-list mr-1 text-blue-500"></i>Mostrando ${totalIncidencias} incidencia${totalIncidencias !== 1 ? 's' : ''} sin asignar`;
    } else {
        contador.innerHTML = `<i class="fas fa-filter mr-1 text-blue-500"></i>Mostrando ${cantidadVisible} de ${totalIncidencias} incidencias sin asignar`;
    }
}

// ============================================
// 3. LISTAR EMPLEADOS
// ============================================
async function cargarEmpleados() {
    try {
        const response = await fetch('/seguridad/api/empleados');
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const data = await response.json();

        // Validar que los datos sean un array
        if (!Array.isArray(data)) {
            console.error('Los datos de empleados no son un array:', data);
            throw new Error('Formato de datos de empleados inválido');
        }

        // Filtrar empleados válidos
        empleadosData = data.filter(emp => emp && emp.id_empleado);

        if (empleadosData.length !== data.length) {
            console.warn(`Se filtraron ${data.length - empleadosData.length} empleados inválidos`);
        }

        if (!empleadosData || empleadosData.length === 0) {
            mostrarNotificacion('No hay empleados disponibles para asignar', 'warning');
        }
    } catch (error) {
        console.error('Error al cargar empleados:', error);
        mostrarNotificacion('Error al cargar los empleados. Por favor, intente nuevamente.', 'error');
        empleadosData = [];
    }
}

// Mostrar empleados en el modal
function mostrarEmpleados(empleadosFiltrados = null) {
    const listaEmpleados = document.getElementById('listaEmpleados');
    const contadorEmpleados = document.getElementById('contadorEmpleados');

    if (!listaEmpleados) return;

    const empleados = empleadosFiltrados || empleadosData;
    listaEmpleados.innerHTML = '';

    if (empleados.length === 0) {
        listaEmpleados.innerHTML = `
            <div class="px-4 py-8 text-center text-gray-500">
                <i class="fas fa-user-slash text-3xl mb-2 text-gray-300"></i>
                <p>No se encontraron empleados</p>
            </div>
        `;
        if (contadorEmpleados) {
            contadorEmpleados.textContent = '0 empleados disponibles';
        }
        return;
    }

    empleados.forEach(empleado => {
        // Validar que el empleado existe y tiene las propiedades necesarias
        if (!empleado || !empleado.id_empleado) {
            console.warn('Empleado inválido encontrado:', empleado);
            return;
        }

        // Asegurarse de que nombre_completo existe
        const nombreCompleto = empleado.nombre_completo || `Empleado #${empleado.id_empleado}`;

        const empleadoDiv = document.createElement('div');
        empleadoDiv.className = 'empleado-item px-4 py-3 hover:bg-cyan-50 cursor-pointer transition-colors border-b border-gray-200 last:border-b-0';
        empleadoDiv.setAttribute('data-id', empleado.id_empleado);
        
        empleadoDiv.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center text-white font-bold">
                    ${obtenerInicialesNombre(nombreCompleto)}
                </div>
                <div class="flex-1">
                    <p class="font-semibold text-gray-800">${nombreCompleto}</p>
                    <p class="text-xs text-gray-500">
                        <i class="fas fa-id-badge mr-1"></i>
                        ID: ${empleado.id_empleado}
                    </p>
                </div>
                <i class="fas fa-chevron-right text-gray-400"></i>
            </div>
        `;

        empleadoDiv.addEventListener('click', function() {
            seleccionarEmpleado(empleado);
        });

        listaEmpleados.appendChild(empleadoDiv);
    });

    if (contadorEmpleados) {
        contadorEmpleados.textContent = `${empleados.length} empleado${empleados.length !== 1 ? 's' : ''} disponible${empleados.length !== 1 ? 's' : ''}`;
    }
}

// ============================================
// 4. BUSCAR EMPLEADO POR NOMBRE
// ============================================
function filtrarEmpleados() {
    const buscarEmpleadoInput = document.getElementById('buscarEmpleadoInput');
    const termino = buscarEmpleadoInput ? buscarEmpleadoInput.value.toLowerCase() : '';

    if (!termino) {
        mostrarEmpleados();
        return;
    }

    const empleadosFiltrados = empleadosData.filter(empleado => {
        // Validar que el empleado existe y tiene propiedades
        if (!empleado || !empleado.id_empleado) return false;
        
        const nombreCompleto = empleado.nombre_completo || '';
        const idEmpleado = empleado.id_empleado ? empleado.id_empleado.toString() : '';
        
        return nombreCompleto.toLowerCase().includes(termino) ||
               idEmpleado.includes(termino);
    });

    mostrarEmpleados(empleadosFiltrados);
}

// ============================================
// 5. MODAL ASIGNAR RESPONSABLE
// ============================================
function abrirModalAsignar(idIncidencia) {
    // Validar que se recibió un ID
    if (!idIncidencia) {
        mostrarNotificacion('ID de incidencia no válido', 'error');
        return;
    }

    // Buscar la incidencia
    const incidencia = incidenciasData.find(inc => inc && inc.id_incidencia == idIncidencia);

    if (!incidencia) {
        mostrarNotificacion('No se encontró la incidencia', 'error');
        console.error('Incidencia no encontrada con ID:', idIncidencia);
        return;
    }

    incidenciaSeleccionada = incidencia;
    empleadoSeleccionado = null;

    // Llenar datos de la incidencia en el modal con valores seguros
    const modalIncidenciaId = document.getElementById('modalIncidenciaId');
    const modalIncidenciaFecha = document.getElementById('modalIncidenciaFecha');
    const modalIncidenciaDescripcion = document.getElementById('modalIncidenciaDescripcion');
    const modalIncidenciaPaciente = document.getElementById('modalIncidenciaPaciente');

    if (modalIncidenciaId) {
        modalIncidenciaId.textContent = `#${incidencia.id_incidencia || 'N/A'}`;
    }
    if (modalIncidenciaFecha) {
        modalIncidenciaFecha.textContent = incidencia.fecha_registro ? formatearFecha(incidencia.fecha_registro) : 'Sin fecha';
    }
    if (modalIncidenciaDescripcion) {
        modalIncidenciaDescripcion.textContent = incidencia.descripcion || 'Sin descripción';
    }
    if (modalIncidenciaPaciente) {
        modalIncidenciaPaciente.textContent = incidencia.paciente || 'N/A';
    }

    // Limpiar búsqueda y selección
    const buscarEmpleadoInput = document.getElementById('buscarEmpleadoInput');
    if (buscarEmpleadoInput) {
        buscarEmpleadoInput.value = '';
    }

    const empleadoSeleccionadoDiv = document.getElementById('empleadoSeleccionadoDiv');
    if (empleadoSeleccionadoDiv) {
        empleadoSeleccionadoDiv.classList.add('hidden');
    }

    // Mostrar empleados
    mostrarEmpleados();

    // Mostrar modal
    const modal = document.getElementById('modalAsignarResponsable');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

function cerrarModalAsignar() {
    const modal = document.getElementById('modalAsignarResponsable');
    modal.classList.add('hidden');
    modal.classList.remove('flex');

    incidenciaSeleccionada = null;
    empleadoSeleccionado = null;
}

function seleccionarEmpleado(empleado) {
    // Validar que el empleado existe
    if (!empleado || !empleado.id_empleado) {
        mostrarNotificacion('Error al seleccionar empleado', 'error');
        return;
    }
    
    empleadoSeleccionado = empleado;

    // Obtener el nombre completo del empleado
    const nombreCompleto = empleado.nombre_completo || `Empleado #${empleado.id_empleado}`;

    // Mostrar empleado seleccionado
    const empleadoSeleccionadoNombre = document.getElementById('empleadoSeleccionadoNombre');
    if (empleadoSeleccionadoNombre) {
        empleadoSeleccionadoNombre.textContent = nombreCompleto;
    }
    
    const empleadoSeleccionadoDiv = document.getElementById('empleadoSeleccionadoDiv');
    if (empleadoSeleccionadoDiv) {
        empleadoSeleccionadoDiv.classList.remove('hidden');
    }

    // Marcar visualmente en la lista
    document.querySelectorAll('.empleado-item').forEach(item => {
        if (item.getAttribute('data-id') == empleado.id_empleado) {
            item.classList.add('bg-cyan-100', 'border-l-4', 'border-cyan-500');
        } else {
            item.classList.remove('bg-cyan-100', 'border-l-4', 'border-cyan-500');
        }
    });
}

// ============================================
// 6. REGISTRAR RESPONSABLE DE INCIDENCIA
// ============================================
async function confirmarAsignacion() {
    if (!incidenciaSeleccionada) {
        mostrarNotificacion('No se ha seleccionado una incidencia', 'error');
        return;
    }

    if (!empleadoSeleccionado || !empleadoSeleccionado.id_empleado) {
        mostrarNotificacion('Por favor seleccione un empleado responsable', 'warning');
        return;
    }

    // Obtener nombre completo del empleado
    const nombreEmpleado = empleadoSeleccionado.nombre_completo || `Empleado #${empleadoSeleccionado.id_empleado}`;
    const incidenciaId = incidenciaSeleccionada.id_incidencia;
    const incidenciaPrioridad = incidenciaSeleccionada.prioridad || 'Media';

    // Confirmar acción
    const confirmacion = confirm(
        `¿Está seguro de asignar la incidencia #${incidenciaId} a ${nombreEmpleado}?`
    );

    if (!confirmacion) {
        return;
    }

    const btnConfirmar = document.getElementById('btnConfirmarAsignacion');
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Asignando...';

    try {
        const response = await fetch(`/seguridad/api/incidencias/${incidenciaId}/asignar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id_empleado: parseInt(empleadoSeleccionado.id_empleado),
                // Al asignar un empleado, cambiar el estado a "En proceso"
                estado: 'En proceso',
                prioridad: incidenciaPrioridad
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al asignar responsable');
        }

        await response.json();

        // Cerrar modal de asignar
        cerrarModalAsignar();

        // Mostrar modal de éxito
        const modalExitoMensaje = document.getElementById('modalExitoMensaje');
        if (modalExitoMensaje) {
            modalExitoMensaje.textContent = `El empleado ${nombreEmpleado} ha sido asignado correctamente a la incidencia #${incidenciaId}`;
        }
        mostrarModalExito();

        // Recargar incidencias
        await cargarIncidencias();

        mostrarNotificacion('Responsable asignado exitosamente', 'success');

    } catch (error) {
        console.error('Error al asignar responsable:', error);
        mostrarNotificacion(error.message || 'Error al asignar responsable', 'error');
    } finally {
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = '<i class="fas fa-check mr-2"></i>Asignar Responsable';
    }
}

// ============================================
// FUNCIONES AUXILIARES
// ============================================

function formatearFecha(fecha) {
    if (!fecha) return 'N/A';

    try {
        const date = new Date(fecha);
        const opciones = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('es-ES', opciones);
    } catch (error) {
        return fecha;
    }
}

function obtenerInicialesNombre(nombreCompleto) {
    if (!nombreCompleto) return '??';

    const palabras = nombreCompleto.trim().split(' ');
    if (palabras.length === 1) {
        return palabras[0].substring(0, 2).toUpperCase();
    }
    return (palabras[0][0] + palabras[palabras.length - 1][0]).toUpperCase();
}

function mostrarModalExito() {
    const modal = document.getElementById('modalExito');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function cerrarModalExito() {
    const modal = document.getElementById('modalExito');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Mostrar notificación toast
function mostrarNotificacion(mensaje, tipo = 'info') {
    const colores = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-amber-500',
        'info': 'bg-blue-500'
    };

    const iconos = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };

    const notificacion = document.createElement('div');
    notificacion.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${colores[tipo] || colores.info} text-white flex items-center gap-3 animate-slide-in`;
    notificacion.innerHTML = `
        <i class="fas ${iconos[tipo] || iconos.info}"></i>
        <span>${mensaje}</span>
    `;
    document.body.appendChild(notificacion);

    setTimeout(() => {
        notificacion.classList.add('animate-fade-out');
        setTimeout(() => notificacion.remove(), 300);
    }, 3000);
}

// Mostrar/ocultar indicador de carga
function mostrarCargando(mostrar) {
    let spinner = document.getElementById('spinnerCarga');

    if (mostrar && !spinner) {
        spinner = document.createElement('div');
        spinner.id = 'spinnerCarga';
        spinner.className = 'fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50';
        spinner.innerHTML = `
            <div class="bg-white rounded-lg p-6 shadow-xl flex flex-col items-center gap-4">
                <i class="fas fa-spinner fa-spin text-4xl text-cyan-600"></i>
                <p class="text-gray-700 font-medium">Cargando datos...</p>
            </div>
        `;
        document.body.appendChild(spinner);
    } else if (!mostrar && spinner) {
        spinner.remove();
    }
}
