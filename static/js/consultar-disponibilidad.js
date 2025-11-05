// Variables globales
let empleados = [];
let roles = [];
let todosLosHorarios = [];
let searchTimeout = null;

// Variables de paginación
let paginaActual = 1;
let registrosPorPagina = 25;
let totalPaginas = 0;

// Elementos del DOM
let rolSelect, empleadoInput, empleadoList, empleadoId, empleadoRol;
let estadoSelect, fechaDesdeInput, fechaHastaInput;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos
    rolSelect = document.getElementById('rol-select');
    empleadoInput = document.getElementById('empleado-input');
    empleadoList = document.getElementById('empleado-list');
    empleadoId = document.getElementById('empleado-id');
    empleadoRol = document.getElementById('empleado-rol');
    
    estadoSelect = document.getElementById('estado-select');
    fechaDesdeInput = document.getElementById('fecha-desde-input');
    fechaHastaInput = document.getElementById('fecha-hasta-input');
    
    // Cargar datos iniciales
    cargarDatos();
    
    // Event listeners para autocomplete de empleados
    empleadoInput.addEventListener('input', function() {
        filtrarEmpleados(this.value);
    });
    
    // Event listeners para búsqueda automática
    rolSelect.addEventListener('change', function() {
        // Limpiar empleado cuando cambia el rol
        empleadoInput.value = '';
        empleadoId.value = '';
        buscarAutomatico();
    });
    empleadoInput.addEventListener('change', buscarAutomatico);
    estadoSelect.addEventListener('change', buscarAutomatico);
    fechaDesdeInput.addEventListener('change', buscarAutomatico);
    fechaHastaInput.addEventListener('change', buscarAutomatico);
    
    // Botón limpiar
    document.getElementById('btn-limpiar').addEventListener('click', limpiarFiltros);
    
    // Event listeners para paginación
    document.getElementById('btn-primera-pagina').addEventListener('click', () => irAPagina(1));
    document.getElementById('btn-ultima-pagina').addEventListener('click', () => irAPagina(totalPaginas));
    document.getElementById('btn-pagina-anterior').addEventListener('click', () => irAPagina(paginaActual - 1));
    document.getElementById('btn-pagina-siguiente').addEventListener('click', () => irAPagina(paginaActual + 1));
    document.getElementById('registros-por-pagina').addEventListener('change', function() {
        registrosPorPagina = parseInt(this.value);
        paginaActual = 1;
        actualizarVistaTabla();
    });
    
    // Modal cerrar
    document.getElementById('btn-cerrar-modal').addEventListener('click', cerrarModal);
    document.getElementById('modal-detalle').addEventListener('click', function(e) {
        if (e.target === this) {
            cerrarModal();
        }
    });
    
    // Cerrar listas al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!empleadoInput.contains(e.target) && !empleadoList.contains(e.target)) {
            empleadoList.classList.add('hidden');
        }
    });
});

// Cargar empleados y horarios iniciales
async function cargarDatos() {
    try {
        // Cargar todos los empleados
        const respEmpleados = await fetch('/reservas/api/empleados-todos');
        if (respEmpleados.ok) {
            const data = await respEmpleados.json();
            empleados = data.empleados || data || [];
            empleados.sort((a, b) => a.id_empleado - b.id_empleado);
            document.getElementById('total-empleados').textContent = empleados.length;
            
            // Extraer roles únicos
            const rolesSet = new Set();
            empleados.forEach(e => {
                if (e.rol) rolesSet.add(e.rol);
            });
            roles = Array.from(rolesSet).sort();
            
            // Llenar select de roles
            roles.forEach(rol => {
                const option = document.createElement('option');
                option.value = rol;
                option.textContent = rol;
                rolSelect.appendChild(option);
            });
        }
        
        // Cargar TODOS los horarios disponibles al inicio
        buscarHorarios();
        
    } catch (error) {
        console.error('Error al cargar datos:', error);
        mostrarNotificacion('Error al cargar los datos', 'error');
    }
}

// Filtrar empleados según rol y texto
function filtrarEmpleados(texto) {
    const textoLower = texto.toLowerCase().trim();
    const rolFiltro = rolSelect.value;
    
    if (textoLower === '') {
        empleadoList.classList.add('hidden');
        empleadoId.value = '';
        return;
    }
    
    let filtrados = empleados.filter(e => 
        (e.nombres.toLowerCase().includes(textoLower) ||
        e.apellidos.toLowerCase().includes(textoLower) ||
        e.id_empleado.toString().includes(textoLower)) &&
        (rolFiltro === '' || e.rol === rolFiltro)
    );
    
    mostrarListaEmpleados(filtrados);
}

// Mostrar lista de empleados - solo especialidad para médicos
function mostrarListaEmpleados(items) {
    empleadoList.innerHTML = '';
    
    if (items.length === 0) {
        empleadoList.innerHTML = '<div class="p-4 text-gray-500 text-sm">No se encontraron empleados</div>';
        empleadoList.classList.remove('hidden');
        return;
    }
    
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'autocomplete-item';
        
        // Solo mostrar especialidad si es médico (rol == Médico o similar)
        const esMedico = item.rol && item.rol.toLowerCase().includes('médico');
        const especialidadHTML = esMedico && item.especialidad && item.especialidad !== '-' 
            ? `<div class="text-xs text-gray-500 mt-1">Especialidad: ${item.especialidad}</div>`
            : '';
        
        div.innerHTML = `
            <div class="font-medium text-gray-800">ID ${item.id_empleado} - ${item.nombres} ${item.apellidos}</div>
            <div class="text-xs text-gray-600 mt-1">Rol: ${item.rol || 'Sin Rol'}</div>
            ${especialidadHTML}
        `;
        div.addEventListener('click', function() {
            seleccionarEmpleado(item);
        });
        empleadoList.appendChild(div);
    });
    
    empleadoList.classList.remove('hidden');
}

// Seleccionar empleado
function seleccionarEmpleado(empleado) {
    empleadoInput.value = `${empleado.nombres} ${empleado.apellidos}`;
    empleadoId.value = empleado.id_empleado;
    empleadoRol.value = empleado.rol || '';
    empleadoList.classList.add('hidden');
    buscarAutomatico();
}

// Búsqueda automática con debounce
function buscarAutomatico() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        buscarHorarios();
    }, 500);
}

// Buscar horarios con filtros
async function buscarHorarios() {
    const idEmpleado = empleadoId.value;
    const estado = estadoSelect.value;
    const fechaDesde = fechaDesdeInput.value;
    const fechaHasta = fechaHastaInput.value;
    const rol = rolSelect.value;
    
    // Mostrar loading
    document.getElementById('loading-indicator').classList.remove('hidden');
    document.getElementById('placeholder-mensaje').classList.add('hidden');
    document.getElementById('no-resultados').classList.add('hidden');
    document.getElementById('horarios-container').classList.add('hidden');
    
    try {
        // Construir URL
        let url = '/reservas/api/buscar-horarios-disponibles-completo?';
        const params = [];
        
        if (idEmpleado) params.push(`id_empleado=${idEmpleado}`);
        if (estado) params.push(`disponibilidad=${encodeURIComponent(estado)}`);
        if (fechaDesde) params.push(`fecha_desde=${fechaDesde}`);
        if (fechaHasta) params.push(`fecha_hasta=${fechaHasta}`);
        if (rol) params.push(`rol=${encodeURIComponent(rol)}`);
        
        url += params.join('&');
        
        const response = await fetch(url);
        const data = await response.json();
        
        // Ocultar loading
        document.getElementById('loading-indicator').classList.add('hidden');
        
        if (data.horarios && data.horarios.length > 0) {
            // Ordenar por ID de horario
            data.horarios.sort((a, b) => a.id_horario - b.id_horario);
            
            todosLosHorarios = data.horarios;
            paginaActual = 1; // Resetear a primera página
            actualizarVistaTabla();
            document.getElementById('horarios-encontrados').textContent = data.horarios.length;
        } else {
            document.getElementById('no-resultados').classList.remove('hidden');
            document.getElementById('horarios-encontrados').textContent = '0';
            document.getElementById('paginacion-container').classList.add('hidden');
        }
        
    } catch (error) {
        console.error('Error al buscar horarios:', error);
        document.getElementById('loading-indicator').classList.add('hidden');
        mostrarNotificacion('Error al buscar horarios disponibles', 'error');
    }
}

// Mostrar horarios en tabla
function mostrarHorariosTabla(horarios) {
    const tbody = document.getElementById('horarios-tbody');
    tbody.innerHTML = '';
    
    horarios.forEach(horario => {
        const tr = document.createElement('tr');
        
        // Determinar si el horario está disponible
        const esDisponible = horario.disponibilidad && horario.disponibilidad.toLowerCase() === 'disponible';
        tr.className = esDisponible ? 'row-disponible' : 'row-no-disponible';
        
        // Badge de disponibilidad
        let badgeDisponibilidad = '';
        if (horario.disponibilidad) {
            const color = horario.disponibilidad.toLowerCase() === 'disponible' ? 'bg-green-100 text-green-800' :
                         horario.disponibilidad.toLowerCase() === 'ocupado' ? 'bg-yellow-100 text-yellow-800' :
                         'bg-gray-100 text-gray-800';
            badgeDisponibilidad = `<span class="px-2 py-1 text-xs font-semibold rounded ${color}">${horario.disponibilidad}</span>`;
        }
        
        // Badge de estado
        let badgeEstado = '';
        if (horario.estado) {
            const colorEstado = horario.estado.toLowerCase() === 'activo' ? 'bg-blue-100 text-blue-800' :
                               'bg-gray-100 text-gray-800';
            badgeEstado = `<span class="px-2 py-1 text-xs font-semibold rounded ${colorEstado}">${horario.estado}</span>`;
        }
        
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                ${horario.id_horario}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                ${horario.profesional || '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${horario.especialidad || '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${horario.fecha}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                ${horario.hora_inicio}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${horario.hora_fin}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${badgeDisponibilidad}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${badgeEstado}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-center">
                <button 
                    onclick="verDetalle(${horario.id_horario})"
                    class="text-cyan-600 hover:text-cyan-800 font-medium">
                    <i class="fas fa-eye mr-1"></i>Ver
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
    
    document.getElementById('horarios-container').classList.remove('hidden');
    document.getElementById('calendario-subtitulo').textContent = `Mostrando ${horarios.length} horarios`;
}

// Ver detalle del horario
function verDetalle(idHorario) {
    const horario = todosLosHorarios.find(h => h.id_horario === idHorario);
    
    if (!horario) {
        mostrarNotificacion('Horario no encontrado', 'error');
        return;
    }
    
    const modalContenido = document.getElementById('modal-contenido');
    modalContenido.innerHTML = `
        <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase">ID Horario</p>
                    <p class="text-lg font-semibold text-gray-800">${horario.id_horario}</p>
                </div>
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase">ID Empleado</p>
                    <p class="text-lg font-semibold text-gray-800">${horario.id_empleado}</p>
                </div>
            </div>
            
            <div>
                <p class="text-xs font-bold text-gray-500 uppercase">Empleado</p>
                <p class="text-lg font-semibold text-gray-800">${horario.profesional || '-'}</p>
            </div>
            
            <div>
                <p class="text-xs font-bold text-gray-500 uppercase">Especialidad</p>
                <p class="text-lg text-gray-800">${horario.especialidad || '-'}</p>
            </div>
            
            <div class="grid grid-cols-3 gap-4">
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase">Fecha</p>
                    <p class="text-lg font-semibold text-gray-800">
                        <i class="fas fa-calendar mr-2 text-cyan-600"></i>
                        ${horario.fecha}
                    </p>
                </div>
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase">Hora Inicio</p>
                    <p class="text-lg font-semibold text-gray-800">
                        <i class="fas fa-clock mr-2 text-green-600"></i>
                        ${horario.hora_inicio}
                    </p>
                </div>
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase">Hora Fin</p>
                    <p class="text-lg font-semibold text-gray-800">
                        <i class="fas fa-clock mr-2 text-red-600"></i>
                        ${horario.hora_fin}
                    </p>
                </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase">Disponibilidad</p>
                    <p class="text-lg">
                        <span class="px-3 py-2 rounded font-semibold ${
                            horario.disponibilidad && horario.disponibilidad.toLowerCase() === 'disponible' ? 'bg-green-100 text-green-800' :
                            horario.disponibilidad && horario.disponibilidad.toLowerCase() === 'ocupado' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                        }">
                            ${horario.disponibilidad || '-'}
                        </span>
                    </p>
                </div>
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase">Estado</p>
                    <p class="text-lg">
                        <span class="px-3 py-2 rounded font-semibold ${
                            horario.estado && horario.estado.toLowerCase() === 'activo' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                        }">
                            ${horario.estado || '-'}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('modal-detalle').classList.remove('hidden');
}

// Cerrar modal
function cerrarModal() {
    document.getElementById('modal-detalle').classList.add('hidden');
}

// Limpiar filtros
function limpiarFiltros() {
    rolSelect.value = '';
    empleadoInput.value = '';
    empleadoId.value = '';
    empleadoRol.value = '';
    estadoSelect.value = '';
    fechaDesdeInput.value = '';
    fechaHastaInput.value = '';
    
    empleadoList.classList.add('hidden');
    
    // Al limpiar, cargar TODOS los horarios
    buscarHorarios();
}

// ===== FUNCIONES DE PAGINACIÓN =====

// Actualizar vista de tabla con paginación
function actualizarVistaTabla() {
    const totalRegistros = todosLosHorarios.length;
    totalPaginas = Math.ceil(totalRegistros / registrosPorPagina);
    
    // Asegurar que la página actual esté en rango
    if (paginaActual > totalPaginas) paginaActual = totalPaginas;
    if (paginaActual < 1) paginaActual = 1;
    
    // Calcular registros a mostrar
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, totalRegistros);
    const horariosPagina = todosLosHorarios.slice(inicio, fin);
    
    // Mostrar horarios de la página actual
    mostrarHorariosTabla(horariosPagina);
    
    // Actualizar controles de paginación
    actualizarControlesPaginacion(totalRegistros, inicio, fin);
}

// Actualizar controles de paginación
function actualizarControlesPaginacion(totalRegistros, inicio, fin) {
    // Mostrar información de registros
    document.getElementById('registros-inicio').textContent = totalRegistros > 0 ? inicio + 1 : 0;
    document.getElementById('registros-fin').textContent = fin;
    document.getElementById('total-registros').textContent = totalRegistros;
    
    // Habilitar/deshabilitar botones
    const btnPrimera = document.getElementById('btn-primera-pagina');
    const btnAnterior = document.getElementById('btn-pagina-anterior');
    const btnSiguiente = document.getElementById('btn-pagina-siguiente');
    const btnUltima = document.getElementById('btn-ultima-pagina');
    
    btnPrimera.disabled = paginaActual === 1;
    btnAnterior.disabled = paginaActual === 1;
    btnSiguiente.disabled = paginaActual === totalPaginas || totalPaginas === 0;
    btnUltima.disabled = paginaActual === totalPaginas || totalPaginas === 0;
    
    // Generar números de página
    generarNumerosPagina();
    
    // Mostrar/ocultar contenedor de paginación
    const paginacionContainer = document.getElementById('paginacion-container');
    if (totalRegistros > 0) {
        paginacionContainer.classList.remove('hidden');
    } else {
        paginacionContainer.classList.add('hidden');
    }
}

// Generar botones de números de página
function generarNumerosPagina() {
    const container = document.getElementById('numeros-pagina');
    container.innerHTML = '';
    
    if (totalPaginas === 0) return;
    
    // Determinar rango de páginas a mostrar
    let inicio = Math.max(1, paginaActual - 2);
    let fin = Math.min(totalPaginas, paginaActual + 2);
    
    // Ajustar si estamos al inicio o al final
    if (paginaActual <= 3) {
        fin = Math.min(5, totalPaginas);
    }
    if (paginaActual > totalPaginas - 3) {
        inicio = Math.max(1, totalPaginas - 4);
    }
    
    // Agregar primera página si no está en el rango
    if (inicio > 1) {
        agregarBotonPagina(container, 1);
        if (inicio > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'px-3 py-2 text-gray-500';
            ellipsis.textContent = '...';
            container.appendChild(ellipsis);
        }
    }
    
    // Agregar páginas en el rango
    for (let i = inicio; i <= fin; i++) {
        agregarBotonPagina(container, i);
    }
    
    // Agregar última página si no está en el rango
    if (fin < totalPaginas) {
        if (fin < totalPaginas - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'px-3 py-2 text-gray-500';
            ellipsis.textContent = '...';
            container.appendChild(ellipsis);
        }
        agregarBotonPagina(container, totalPaginas);
    }
}

// Agregar botón de página individual
function agregarBotonPagina(container, numeroPagina) {
    const btn = document.createElement('button');
    btn.textContent = numeroPagina;
    
    if (numeroPagina === paginaActual) {
        btn.className = 'px-4 py-2 rounded-lg bg-cyan-600 text-white font-semibold';
    } else {
        btn.className = 'px-4 py-2 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 transition-colors';
    }
    
    btn.addEventListener('click', () => irAPagina(numeroPagina));
    container.appendChild(btn);
}

// Ir a una página específica
function irAPagina(numeroPagina) {
    if (numeroPagina < 1 || numeroPagina > totalPaginas) return;
    paginaActual = numeroPagina;
    actualizarVistaTabla();
}

// Mostrar notificación
function mostrarNotificacion(mensaje, tipo = 'info') {
    const colores = {
        'success': 'bg-green-100 border-green-500 text-green-800',
        'error': 'bg-red-100 border-red-500 text-red-800',
        'info': 'bg-blue-100 border-blue-500 text-blue-800'
    };
    
    const notif = document.createElement('div');
    notif.className = `fixed top-4 right-4 ${colores[tipo]} border-l-4 p-4 rounded shadow-lg z-50 animate-fade-in`;
    notif.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'exclamation-circle' : 'info-circle'} mr-3"></i>
            <span>${mensaje}</span>
        </div>
    `;
    
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.remove();
    }, 3000);
}
