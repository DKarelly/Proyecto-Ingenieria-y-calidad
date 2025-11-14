// Variables globales
let incidenciasData = [];
let prioridadActiva = 'Baja'; // Prioridad activa por defecto

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

// Filtrar incidencias por prioridad localmente
function filtrarPorPrioridad(prioridad) {
    if (!incidenciasData || incidenciasData.length === 0) {
        mostrarIncidencias([]);
        return;
    }
    
    // Si no hay prioridad especificada, mostrar todas
    if (!prioridad) {
        mostrarIncidencias(incidenciasData);
        return;
    }
    
    // Filtrar por prioridad (normalizar espacios)
    const prioridadNormalizada = prioridad.trim();
    
    const incidenciasFiltradas = incidenciasData.filter(incidencia => {
        const prioridadIncidencia = incidencia.prioridad ? incidencia.prioridad.trim() : '';
        return prioridadIncidencia === prioridadNormalizada;
    });
    
    mostrarIncidencias(incidenciasFiltradas);
}

// Cargar incidencias pendientes al inicio
async function cargarIncidencias() {
    try {
        const response = await fetch('/seguridad/api/incidencias/pendientes', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            incidenciasData = await response.json();
            
            // Verificar si hay datos
            if (!incidenciasData || incidenciasData.length === 0) {
                mostrarIncidencias([]);
                actualizarContadoresPrioridad();
                return;
            }
            
            // Actualizar contadores después de cargar
            actualizarContadoresPrioridad();
            
            // Filtrar por la prioridad activa (por defecto 'Baja')
            // Si no hay coincidencias, mostrar todas las incidencias
            const filtradas = incidenciasData.filter(inc => {
                const prioridadIncidencia = inc.prioridad ? inc.prioridad.trim() : '';
                return prioridadIncidencia === prioridadActiva.trim();
            });
            
            if (filtradas.length === 0 && incidenciasData.length > 0) {
                mostrarIncidencias(incidenciasData);
            } else {
                filtrarPorPrioridad(prioridadActiva);
            }
        } else {
            const errorText = await response.text();
            console.error('Error al cargar incidencias:', response.status, errorText);
            
            // Mostrar mensaje de error más específico
            const tbody = document.getElementById('tabla-incidencias-cuerpo');
            if (tbody) {
                let mensajeError = 'Error al cargar las incidencias';
                if (response.status === 401) {
                    mensajeError = 'Sesión expirada. Por favor, recarga la página';
                } else if (response.status === 404) {
                    mensajeError = 'Ruta no encontrada. Verifica que el servidor esté corriendo';
                } else if (response.status === 500) {
                    mensajeError = 'Error del servidor. Contacta al administrador';
                }
                
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="px-6 py-8 text-center">
                            <div class="flex flex-col items-center gap-3">
                                <i class="fas fa-exclamation-triangle text-red-300 text-4xl"></i>
                                <p class="text-red-500 font-medium">${mensajeError}</p>
                                <p class="text-gray-400 text-sm">Status: ${response.status}</p>
                            </div>
                        </td>
                    </tr>
                `;
            }
        }
    } catch (error) {
        console.error('Error de conexión:', error);
        const tbody = document.getElementById('tabla-incidencias-cuerpo');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="px-6 py-8 text-center">
                        <div class="flex flex-col items-center gap-3">
                            <i class="fas fa-exclamation-triangle text-red-300 text-4xl"></i>
                            <p class="text-red-500 font-medium">Error de conexión</p>
                            <p class="text-gray-400 text-sm">No se pudo conectar con el servidor: ${error.message}</p>
                        </div>
                    </td>
                </tr>
            `;
        }
    }
}

// Mostrar incidencias en la tabla
function mostrarIncidencias(incidencias) {
    const tbody = document.getElementById('tabla-incidencias-cuerpo');
    if (!tbody) {
        console.error('No se encontró el elemento tbody con id "tabla-incidencias-cuerpo"');
        return;
    }
    
    tbody.innerHTML = '';

    // Actualizar contador de resultados
    const contadorResultados = document.getElementById('contadorResultados');
    if (contadorResultados) {
        if (incidencias.length === 0) {
            contadorResultados.textContent = 'No hay incidencias pendientes';
        } else {
            const texto = incidencias.length === 1 ? 'incidencia pendiente' : 'incidencias pendientes';
            contadorResultados.textContent = `${incidencias.length} ${texto}`;
        }
    }

    // Actualizar badge de filtros activos
    actualizarBadgeFiltros();

    if (incidencias.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-8 text-center">
                    <div class="flex flex-col items-center gap-3">
                        <i class="fas fa-check-circle text-green-300 text-4xl"></i>
                        <p class="text-gray-500 font-medium">No hay incidencias pendientes</p>
                        <p class="text-gray-400 text-sm">Todas las incidencias están resueltas</p>
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
                    <span class="tooltip">Confirmar Resolución</span>
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

// Autocompletado para pacientes (inicializado en DOMContentLoaded)
let timeoutPaciente;

function mostrarSugerenciasPaciente(pacientes) {
    const contenedor = document.getElementById('sugerenciasPaciente');
    if (!contenedor) return;
    
    contenedor.innerHTML = '';

    if (pacientes.length === 0) {
        contenedor.innerHTML = '<div class="px-4 py-2 text-gray-500 text-sm">No se encontraron pacientes</div>';
        contenedor.classList.remove('hidden');
        return;
    }

    pacientes.forEach(paciente => {
        const div = document.createElement('div');
        div.className = 'px-4 py-2 hover:bg-cyan-50 cursor-pointer transition-colors';
        div.innerHTML = `
            <div class="font-medium text-gray-800">${paciente.nombre_completo}</div>
            ${paciente.dni ? `<div class="text-xs text-gray-500">DNI: ${paciente.dni}</div>` : ''}
        `;
        div.onclick = function(e) {
            e.stopPropagation();
            const filtroPaciente = document.getElementById('filtroPaciente');
            if (filtroPaciente) {
                filtroPaciente.value = paciente.nombre_completo;
                contenedor.classList.add('hidden');
                // Aplicar filtros inmediatamente al seleccionar
                aplicarFiltrosDinamicos();
            }
        };
        contenedor.appendChild(div);
    });

    contenedor.classList.remove('hidden');
}

// Autocompletado para empleados (inicializado en DOMContentLoaded)
let timeoutEmpleado;

function mostrarSugerenciasEmpleado(empleados) {
    const contenedor = document.getElementById('sugerenciasEmpleado');
    if (!contenedor) return;
    
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
            const filtroEmpleado = document.getElementById('filtroEmpleado');
            if (filtroEmpleado) {
                filtroEmpleado.value = empleado.nombre_completo;
                contenedor.classList.add('hidden');
                aplicarFiltrosDinamicos(); // Aplicar filtro al seleccionar
            }
        };
        contenedor.appendChild(div);
    });

    contenedor.classList.remove('hidden');
}

// Ocultar sugerencias al hacer clic fuera
document.addEventListener('click', function(e) {
    const sugerenciasPaciente = document.getElementById('sugerenciasPaciente');
    if (sugerenciasPaciente && !e.target.closest('#filtroPaciente') && !e.target.closest('#sugerenciasPaciente')) {
        sugerenciasPaciente.classList.add('hidden');
    }
    const sugerenciasEmpleado = document.getElementById('sugerenciasEmpleado');
    if (sugerenciasEmpleado && !e.target.closest('#filtroEmpleado') && !e.target.closest('#sugerenciasEmpleado')) {
        sugerenciasEmpleado.classList.add('hidden');
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
                // Esto también actualizará los contadores automáticamente
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
    const filtroPaciente = document.getElementById('filtroPaciente');
    const filtroEmpleado = document.getElementById('filtroEmpleado');
    const filtroFechaRegistro = document.getElementById('filtroFechaRegistro');
    const filtroFechaResolucion = document.getElementById('filtroFechaResolucion');
    const filtroEstado = document.getElementById('filtroEstado');
    const filtroCategoria = document.getElementById('filtroCategoria');
    
    const filtros = {
        paciente: filtroPaciente ? filtroPaciente.value.trim() : '',
        empleado: filtroEmpleado ? filtroEmpleado.value.trim() : '',
        fecha_registro: filtroFechaRegistro ? filtroFechaRegistro.value : '',
        fecha_resolucion: filtroFechaResolucion ? filtroFechaResolucion.value : '',
        estado: filtroEstado ? filtroEstado.value : '',
        categoria: filtroCategoria ? filtroCategoria.value : ''
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

// Funciones de validación
function validarFiltroPaciente(valor, mostrarErrores = true) {
    const errorEl = document.getElementById('errorFiltroPaciente');
    const inputEl = document.getElementById('filtroPaciente');
    
    if (!errorEl || !inputEl) return true;
    
    // Si el campo está vacío, no hay error
    if (!valor || valor.trim().length === 0) {
        if (mostrarErrores) {
            ocultarError('errorFiltroPaciente');
            inputEl.classList.remove('border-red-500');
        }
        return true;
    }
    
    // Limpiar errores previos
    if (mostrarErrores) {
        ocultarError('errorFiltroPaciente');
        inputEl.classList.remove('border-red-500');
    }
    
    // Validar longitud
    if (valor.length > 100) {
        if (mostrarErrores) {
            mostrarError('errorFiltroPaciente', 'El nombre del paciente no puede exceder 100 caracteres', inputEl);
        }
        return false;
    }
    
    // Validar caracteres permitidos (solo letras, espacios y algunos caracteres especiales)
    // Permitir búsqueda parcial mientras escribe
    if (valor && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\.\-']+$/.test(valor)) {
        if (mostrarErrores) {
            mostrarError('errorFiltroPaciente', 'Solo se permiten letras, espacios y caracteres básicos', inputEl);
        }
        return false;
    }
    
    return true;
}

function validarFechas(fechaRegistro, fechaResolucion) {
    const errorFechaRegistro = document.getElementById('errorFiltroFechaRegistro');
    const errorFechaResolucion = document.getElementById('errorFiltroFechaResolucion');
    const inputFechaRegistro = document.getElementById('filtroFechaRegistro');
    const inputFechaResolucion = document.getElementById('filtroFechaResolucion');
    
    // Limpiar errores previos
    if (errorFechaRegistro) ocultarError('errorFiltroFechaRegistro');
    if (errorFechaResolucion) ocultarError('errorFiltroFechaResolucion');
    if (inputFechaRegistro) inputFechaRegistro.classList.remove('border-red-500');
    if (inputFechaResolucion) inputFechaResolucion.classList.remove('border-red-500');
    
    const hoy = new Date().toISOString().split('T')[0];
    let esValido = true;
    
    // Validar fecha de registro
    if (fechaRegistro) {
        if (fechaRegistro > hoy) {
            mostrarError('errorFiltroFechaRegistro', 'La fecha de registro no puede ser futura', inputFechaRegistro);
            esValido = false;
        }
    }
    
    // Validar fecha de resolución
    if (fechaResolucion) {
        if (fechaResolucion > hoy) {
            mostrarError('errorFiltroFechaResolucion', 'La fecha de resolución no puede ser futura', inputFechaResolucion);
            esValido = false;
        }
        
        // Validar que fecha resolución no sea anterior a fecha registro
        if (fechaRegistro && fechaResolucion && fechaResolucion < fechaRegistro) {
            mostrarError('errorFiltroFechaResolucion', 'La fecha de resolución no puede ser anterior a la fecha de registro', inputFechaResolucion);
            esValido = false;
        }
    }
    
    return esValido;
}

function mostrarError(idError, mensaje, inputEl) {
    const errorEl = document.getElementById(idError);
    if (errorEl) {
        errorEl.textContent = mensaje;
        errorEl.classList.remove('hidden');
    }
    if (inputEl) {
        inputEl.classList.add('border-red-500');
    }
}

function ocultarError(idError) {
    const errorEl = document.getElementById(idError);
    if (errorEl) {
        errorEl.classList.add('hidden');
        errorEl.textContent = '';
    }
}

function limpiarErroresValidacion() {
    ocultarError('errorFiltroPaciente');
    ocultarError('errorFiltroEstado');
    ocultarError('errorFiltroFechaRegistro');
    ocultarError('errorFiltroFechaResolucion');
    ocultarError('errorFiltroCategoria');
    
    const inputs = ['filtroPaciente', 'filtroFechaRegistro', 'filtroFechaResolucion'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('border-red-500');
    });
}

// Función para aplicar filtros dinámicamente
let timeoutFiltros;
async function aplicarFiltrosDinamicos() {
    clearTimeout(timeoutFiltros);

    timeoutFiltros = setTimeout(async () => {
        const filtroPaciente = document.getElementById('filtroPaciente');
        const filtroEmpleado = document.getElementById('filtroEmpleado');
        const filtroFechaRegistro = document.getElementById('filtroFechaRegistro');
        const filtroFechaResolucion = document.getElementById('filtroFechaResolucion');
        const filtroEstado = document.getElementById('filtroEstado');
        const filtroCategoria = document.getElementById('filtroCategoria');
        
        // Obtener valores de filtros
        const valorPaciente = filtroPaciente ? filtroPaciente.value.trim() : '';
        const valorEmpleado = filtroEmpleado ? filtroEmpleado.value.trim() : '';
        const fechaRegistro = filtroFechaRegistro ? filtroFechaRegistro.value : '';
        const fechaResolucion = filtroFechaResolucion ? filtroFechaResolucion.value : '';
        const valorEstado = filtroEstado ? filtroEstado.value : '';
        const valorCategoria = filtroCategoria ? filtroCategoria.value : '';
        
        // Si hay un nombre de paciente, buscar inmediatamente sin validaciones estrictas
        // Solo validar si hay errores críticos (longitud > 100)
        if (valorPaciente.length > 100) {
            mostrarError('errorFiltroPaciente', 'El nombre del paciente no puede exceder 100 caracteres', filtroPaciente);
            return;
        }
        
        // Validar fechas solo si ambas están presentes
        if (fechaRegistro && fechaResolucion) {
            if (!validarFechas(fechaRegistro, fechaResolucion)) {
                return; // No aplicar filtros si hay error de validación en fechas
            }
        }
        
        // Construir filtros
        // Si hay un nombre de paciente, buscar inmediatamente por ese paciente sin importar otros filtros
        const filtros = {
            paciente: valorPaciente,
            empleado: valorEmpleado,
            fecha_registro: fechaRegistro,
            fecha_resolucion: fechaResolucion,
            // Si hay un estado seleccionado explícitamente, usarlo; si no, buscar solo "En progreso" por defecto
            // PERO si hay un nombre de paciente, buscar TODOS los estados para mostrar todas las incidencias de ese paciente
            estado: valorPaciente ? '' : (valorEstado || ''),
            categoria: valorCategoria || '',
            // Si hay un nombre de paciente, ignorar la prioridad para mostrar todas las incidencias de ese paciente
            // Si no hay nombre de paciente, usar la prioridad activa
            prioridad: valorPaciente ? '' : (prioridadActiva || '')
        };

        console.log('🔍 Aplicando filtros:', filtros);

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

            console.log('📡 Respuesta del servidor:', response.status, response.ok);

            if (response.ok) {
                const incidenciasFiltradas = await response.json();
                console.log('✅ Incidencias encontradas:', incidenciasFiltradas ? incidenciasFiltradas.length : 0);
                console.log('📋 Datos:', incidenciasFiltradas);
                mostrarIncidencias(incidenciasFiltradas);
                // NO actualizar incidenciasData aquí, mantener los datos originales para contadores
            } else {
                const errorText = await response.text();
                console.error('❌ Error en la búsqueda - Status:', response.status);
                console.error('❌ Error response:', errorText);
                
                if (response.status === 401) {
                    showToast('Sesión expirada. Por favor, recarga la página', 'error');
                } else if (response.status === 404) {
                    console.error('Ruta no encontrada. Verifica que el servidor esté corriendo correctamente.');
                    showToast('Error: Ruta no encontrada. Verifica la conexión', 'error');
                } else {
                    showToast('Error al aplicar filtros', 'error');
                }
            }
        } catch (error) {
            console.error('Error de red:', error);
            showToast('Error de conexión al filtrar. Verifica tu conexión a internet', 'error');
        }
    }, 200); // Reducido a 200ms para respuesta más rápida
}

// Botón limpiar filtros (inicializado en DOMContentLoaded)
// Inicializar la página
document.addEventListener('DOMContentLoaded', function() {
    // Configurar límite máximo de fechas (hoy)
    const hoy = new Date().toISOString().split('T')[0];
    const filtroFechaRegistro = document.getElementById('filtroFechaRegistro');
    const filtroFechaResolucion = document.getElementById('filtroFechaResolucion');
    if (filtroFechaRegistro) {
        filtroFechaRegistro.setAttribute('max', hoy);
    }
    if (filtroFechaResolucion) {
        filtroFechaResolucion.setAttribute('max', hoy);
    }
    
    // Inicializar autocompletado para pacientes con validación
    const filtroPacienteEl = document.getElementById('filtroPaciente');
    if (filtroPacienteEl) {
        // Bandera para evitar ejecutar al cargar la página
        let pacienteInputInicializado = false;
        
        // Esperar un poco antes de activar el listener para evitar que se dispare al cargar
        setTimeout(() => {
            pacienteInputInicializado = true;
        }, 500);
        
        // Validar y filtrar en tiempo real mientras escribe
        filtroPacienteEl.addEventListener('input', function() {
            // NO hacer nada si aún no se ha inicializado (evitar disparo inicial)
            if (!pacienteInputInicializado) {
                return;
            }
            
            // Limpiar números automáticamente
            this.value = this.value.replace(/[0-9]/g, '');
            
            const termino = this.value.trim();
            
            // Si el campo está vacío, limpiar errores y volver a mostrar todas las incidencias de la prioridad activa
            if (termino.length === 0) {
                ocultarError('errorFiltroPaciente');
                this.classList.remove('border-red-500');
                // Volver a filtrar solo por prioridad (SIN llamar al servidor)
                filtrarPorPrioridad(prioridadActiva);
                const sugerenciasPaciente = document.getElementById('sugerenciasPaciente');
                if (sugerenciasPaciente) {
                    sugerenciasPaciente.classList.add('hidden');
                }
                return; // ← IMPORTANTE: return aquí para NO ejecutar aplicarFiltrosDinamicos
            }
            
            // Validar solo si hay contenido y no excede el límite
            if (termino.length > 100) {
                mostrarError('errorFiltroPaciente', 'El nombre no puede exceder 100 caracteres', this);
                return;
            } else {
                ocultarError('errorFiltroPaciente');
                this.classList.remove('border-red-500');
            }
            
            // Solo aplicar filtros dinámicos si hay un término de búsqueda válido
            if (termino.length > 0) {
                aplicarFiltrosDinamicos();
            }
            
            // Mostrar sugerencias de autocompletado
            clearTimeout(timeoutPaciente);
            const sugerenciasPaciente = document.getElementById('sugerenciasPaciente');
            if (!sugerenciasPaciente) return;

            if (termino.length < 2) {
                sugerenciasPaciente.classList.add('hidden');
                return;
            }

            // Mostrar sugerencias después de un pequeño delay
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
        
        // Cerrar sugerencias cuando se hace clic fuera o se pierde el foco
        filtroPacienteEl.addEventListener('blur', function(e) {
            // Esperar un poco para permitir que el clic en la sugerencia se procese
            setTimeout(() => {
                const sugerenciasPaciente = document.getElementById('sugerenciasPaciente');
                if (sugerenciasPaciente && !sugerenciasPaciente.contains(document.activeElement)) {
                    sugerenciasPaciente.classList.add('hidden');
                }
            }, 200);
        });
    }
    
    // Cerrar sugerencias al hacer clic fuera
    document.addEventListener('click', function(e) {
        const filtroPaciente = document.getElementById('filtroPaciente');
        const sugerenciasPaciente = document.getElementById('sugerenciasPaciente');
        if (filtroPaciente && sugerenciasPaciente && 
            !filtroPaciente.contains(e.target) && 
            !sugerenciasPaciente.contains(e.target)) {
            sugerenciasPaciente.classList.add('hidden');
        }
    });

    // Inicializar autocompletado para empleados
    const filtroEmpleadoElement = document.getElementById('filtroEmpleado');
    if (filtroEmpleadoElement) {
        filtroEmpleadoElement.addEventListener('input', function() {
            clearTimeout(timeoutEmpleado);
            const termino = this.value.trim();

            const sugerenciasEmpleado = document.getElementById('sugerenciasEmpleado');
            if (!sugerenciasEmpleado) return;

            if (termino.length < 2) {
                sugerenciasEmpleado.classList.add('hidden');
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
    }

    // Inicializar búsqueda dinámica empleados en modal editar
    const editResponsableEl = document.getElementById('editResponsable');
    if (editResponsableEl) {
        editResponsableEl.addEventListener('input', function() {
            clearTimeout(timeoutEditEmpleado);
            const termino = this.value.trim();

            const sugerenciasEditEmpleado = document.getElementById('sugerenciasEditEmpleado');
            const editResponsableId = document.getElementById('editResponsableId');
            const editResponsableSeleccionado = document.getElementById('editResponsableSeleccionado');

            if (termino.length < 2) {
                if (sugerenciasEditEmpleado) sugerenciasEditEmpleado.classList.add('hidden');
                if (editResponsableId) editResponsableId.value = '';
                if (editResponsableSeleccionado) editResponsableSeleccionado.textContent = '';
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
    }

    // NOTA: El filtro de paciente ya tiene su listener de input configurado arriba (línea 828)
    // que incluye la lógica de aplicarFiltrosDinamicos(), por lo que no necesitamos duplicarlo aquí

    // Bandera para evitar que se disparen eventos durante la carga inicial
    let filtrosInicializados = false;
    setTimeout(() => {
        filtrosInicializados = true;
    }, 500);
    
    const filtroEmpleadoEl = document.getElementById('filtroEmpleado');
    if (filtroEmpleadoEl) {
        filtroEmpleadoEl.addEventListener('input', function() {
            if (!filtrosInicializados) return;
            aplicarFiltrosDinamicos();
        });
    }

    const filtroFechaRegistroEl = document.getElementById('filtroFechaRegistro');
    const filtroFechaResolucionEl = document.getElementById('filtroFechaResolucion');
    
    if (filtroFechaRegistroEl) {
        // Validar y aplicar filtros cuando cambia la fecha de registro
        filtroFechaRegistroEl.addEventListener('change', function() {
            if (!filtrosInicializados) return;
            const fechaRegistro = this.value;
            const fechaResolucion = filtroFechaResolucionEl ? filtroFechaResolucionEl.value : '';
            
            // Validar fechas
            validarFechas(fechaRegistro, fechaResolucion);
            
            // Si la fecha de resolución existe y es anterior a la nueva fecha de registro, limpiarla
            if (fechaResolucion && fechaRegistro && fechaResolucion < fechaRegistro) {
                if (filtroFechaResolucionEl) {
                    filtroFechaResolucionEl.value = '';
                }
            }
            
            aplicarFiltrosDinamicos();
        });
        
        // También aplicar en input para mayor responsividad
        filtroFechaRegistroEl.addEventListener('input', function() {
            if (!filtrosInicializados) return;
            aplicarFiltrosDinamicos();
        });
    }

    if (filtroFechaResolucionEl) {
        // Validar y aplicar filtros cuando cambia la fecha de resolución
        filtroFechaResolucionEl.addEventListener('change', function() {
            if (!filtrosInicializados) return;
            const fechaRegistro = filtroFechaRegistroEl ? filtroFechaRegistroEl.value : '';
            const fechaResolucion = this.value;
            
            // Validar fechas
            validarFechas(fechaRegistro, fechaResolucion);
            
            aplicarFiltrosDinamicos();
        });
        
        // También aplicar en input para mayor responsividad
        filtroFechaResolucionEl.addEventListener('input', function() {
            if (!filtrosInicializados) return;
            aplicarFiltrosDinamicos();
        });
    }

    const filtroEstadoEl = document.getElementById('filtroEstado');
    if (filtroEstadoEl) {
        // Aplicar filtros inmediatamente al cambiar estado
        filtroEstadoEl.addEventListener('change', function() {
            if (!filtrosInicializados) return;
            ocultarError('errorFiltroEstado');
            aplicarFiltrosDinamicos();
        });
        
        // También aplicar en input para mayor responsividad
        filtroEstadoEl.addEventListener('input', function() {
            if (!filtrosInicializados) return;
            aplicarFiltrosDinamicos();
        });
    }

    const filtroCategoriaEl = document.getElementById('filtroCategoria');
    if (filtroCategoriaEl) {
        // Aplicar filtros inmediatamente al cambiar categoría
        filtroCategoriaEl.addEventListener('change', function() {
            if (!filtrosInicializados) return;
            ocultarError('errorFiltroCategoria');
            aplicarFiltrosDinamicos();
        });
        
        // También aplicar en input para mayor responsividad
        filtroCategoriaEl.addEventListener('input', function() {
            if (!filtrosInicializados) return;
            aplicarFiltrosDinamicos();
        });
    }

    // Botón limpiar filtros
    const btnLimpiar = document.getElementById('btnLimpiar');
    if (btnLimpiar) {
        btnLimpiar.onclick = function() {
            const filtroPaciente = document.getElementById('filtroPaciente');
            const filtroEmpleado = document.getElementById('filtroEmpleado');
            const filtroFechaRegistro = document.getElementById('filtroFechaRegistro');
            const filtroFechaResolucion = document.getElementById('filtroFechaResolucion');
            const filtroEstado = document.getElementById('filtroEstado');
            const filtroCategoria = document.getElementById('filtroCategoria');
            const sugerenciasPaciente = document.getElementById('sugerenciasPaciente');
            const sugerenciasEmpleado = document.getElementById('sugerenciasEmpleado');
            
            // Limpiar valores
            if (filtroPaciente) {
                filtroPaciente.value = '';
                filtroPaciente.classList.remove('border-red-500');
            }
            if (filtroEmpleado) filtroEmpleado.value = '';
            if (filtroFechaRegistro) {
                filtroFechaRegistro.value = '';
                filtroFechaRegistro.classList.remove('border-red-500');
            }
            if (filtroFechaResolucion) {
                filtroFechaResolucion.value = '';
                filtroFechaResolucion.classList.remove('border-red-500');
            }
            if (filtroEstado) filtroEstado.value = '';
            if (filtroCategoria) filtroCategoria.value = '';
            if (sugerenciasPaciente) sugerenciasPaciente.classList.add('hidden');
            if (sugerenciasEmpleado) sugerenciasEmpleado.classList.add('hidden');
            
            // Limpiar errores de validación
            limpiarErroresValidacion();
            
            // Actualizar badge y aplicar filtros
            actualizarBadgeFiltros();
            
            // Filtrar solo por prioridad activa (sin otros filtros)
            filtrarPorPrioridad(prioridadActiva);
        }
    }

    // Inicializar pestañas primero (sin esperar datos)
    inicializarPestanasPrioridad();
    
    // Cargar incidencias (esto actualizará los contadores y filtrará)
    cargarIncidencias();
});

// ========== PESTAÑAS DE PRIORIDAD ==========

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
            
            // Verificar si hay filtros adicionales activos
            const filtroPaciente = document.getElementById('filtroPaciente');
            const filtroFechaRegistro = document.getElementById('filtroFechaRegistro');
            const filtroFechaResolucion = document.getElementById('filtroFechaResolucion');
            const filtroEstado = document.getElementById('filtroEstado');
            const filtroCategoria = document.getElementById('filtroCategoria');
            
            // Si hay filtros adicionales, usar la búsqueda del servidor
            const hayFiltrosAdicionales = 
                (filtroPaciente && filtroPaciente.value.trim()) ||
                (filtroFechaRegistro && filtroFechaRegistro.value) ||
                (filtroFechaResolucion && filtroFechaResolucion.value) ||
                (filtroEstado && filtroEstado.value) ||
                (filtroCategoria && filtroCategoria.value);
            
            if (hayFiltrosAdicionales) {
                // Si hay filtros adicionales, usar la búsqueda del servidor
                aplicarFiltrosDinamicos();
            } else {
                // Si no hay filtros adicionales, filtrar localmente por prioridad (más rápido)
                filtrarPorPrioridad(prioridadActiva);
            }
        });
    });
    
    // Actualizar contadores al cargar (se llamará después de cargarIncidencias)
}

function actualizarContadoresPrioridad() {
    const contadores = { 'Baja': 0, 'Media': 0, 'Alta': 0 };
    
    if (incidenciasData && incidenciasData.length > 0) {
        incidenciasData.forEach(incidencia => {
            const prioridad = incidencia.prioridad ? incidencia.prioridad.trim() : null;
            if (prioridad && contadores.hasOwnProperty(prioridad)) {
                contadores[prioridad]++;
            }
        });
    }
    
    document.querySelectorAll('.priority-tab').forEach(tab => {
        const prioridad = tab.getAttribute('data-priority');
        const badge = tab.querySelector('.badge-count');
        if (badge && contadores.hasOwnProperty(prioridad)) {
            badge.textContent = contadores[prioridad] || 0;
        }
    });
}

// ========== BÚSQUEDA DINÁMICA EMPLEADOS EN MODAL EDITAR ==========
// (inicializado en DOMContentLoaded)
let timeoutEditEmpleado;

function mostrarSugerenciasEditEmpleado(empleados) {
    const contenedor = document.getElementById('sugerenciasEditEmpleado');
    if (!contenedor) return;
    
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
            const editResponsable = document.getElementById('editResponsable');
            const editResponsableId = document.getElementById('editResponsableId');
            const editResponsableSeleccionado = document.getElementById('editResponsableSeleccionado');
            
            if (editResponsable) editResponsable.value = empleado.nombre_completo;
            if (editResponsableId) editResponsableId.value = empleado.id_empleado;
            if (editResponsableSeleccionado) {
                editResponsableSeleccionado.innerHTML = `
                    <span class="text-green-600">✓ Responsable: <strong>${empleado.nombre_completo}</strong></span>
                `;
            }
            contenedor.classList.add('hidden');
        };
        contenedor.appendChild(div);
    });

    contenedor.classList.remove('hidden');
}

// Ocultar sugerencias al hacer clic fuera
document.addEventListener('click', function(e) {
    const sugerenciasEditEmpleado = document.getElementById('sugerenciasEditEmpleado');
    if (sugerenciasEditEmpleado && !e.target.closest('#editResponsable') && !e.target.closest('#sugerenciasEditEmpleado')) {
        sugerenciasEditEmpleado.classList.add('hidden');
    }
});
