let medicosData = [];
let medicosFiltrados = [];
let especialidades = new Set();

// Función para actualizar estadísticas
function actualizarEstadisticas() {
    document.getElementById('total-medicos').textContent = medicosData.length;
    document.getElementById('total-especialidades').textContent = especialidades.size;
    document.getElementById('total-resultados').textContent = medicosFiltrados.length;
}

// Función para renderizar tabla
function renderizarTabla() {
    const tbody = document.getElementById('medicos-table-body');
    
    if (!tbody) {
        console.warn('No se encontró el elemento medicos-table-body');
        return;
    }

    if (medicosFiltrados.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-8 text-center text-gray-500">
                    <i class="fas fa-info-circle mr-2"></i>
                    No se encontraron médicos con los filtros aplicados
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = medicosFiltrados.map(medico => `
        <tr class="hover:bg-cyan-50 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 bg-cyan-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-user-md text-cyan-600"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-gray-900">${medico.nombres} ${medico.apellidos}</p>
                        <p class="text-xs text-gray-500">${medico.rol || 'Sin rol'}</p>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-gray-600 font-mono text-sm">${medico.documento_identidad || 'N/A'}</span>
            </td>
            <td class="px-6 py-4">
                <span class="px-3 py-1 text-xs font-semibold rounded-full ${
                    medico.especialidad
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                }">
                    <i class="fas fa-stethoscope mr-1"></i>
                    ${medico.especialidad || 'Sin especialidad'}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm">
                    <div class="text-gray-600">
                        <i class="fas fa-envelope mr-1 text-cyan-600"></i>
                        ${medico.correo || 'N/A'}
                    </div>
                    <div class="text-gray-600">
                        <i class="fas fa-phone mr-1 text-cyan-600"></i>
                        ${medico.telefono || 'N/A'}
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 text-center whitespace-nowrap">
                <button
                    data-id="${medico.id_empleado}"
                    data-nombre="${medico.nombres} ${medico.apellidos}"
                    data-especialidad="${medico.especialidad || 'Sin especialidad'}"
                    class="ver-servicios-btn bg-cyan-100 hover:bg-cyan-600 hover:text-white text-cyan-700 font-semibold py-2 px-4 rounded-lg inline-flex items-center justify-center transition-all transform hover:scale-105 shadow-sm hover:shadow-md">
                    <i class="fas fa-list-ul mr-2"></i>
                    Ver Servicios
                </button>
            </td>
        </tr>
    `).join('');

    // Re-attachar event listeners
    attachVerServiciosListeners();
}

// Función para aplicar filtros
function aplicarFiltros() {
    const busqueda = document.getElementById('search-employee').value.toLowerCase().trim();
    const especialidadFiltro = document.getElementById('filtro-especialidad').value;

    medicosFiltrados = medicosData.filter(medico => {
        const nombreCompleto = `${medico.nombres} ${medico.apellidos}`.toLowerCase();
        const especialidad = (medico.especialidad || '').toLowerCase();

        const cumpleBusqueda = !busqueda ||
            nombreCompleto.includes(busqueda) ||
            especialidad.includes(busqueda);

        const cumpleEspecialidad = !especialidadFiltro ||
            medico.especialidad === especialidadFiltro;

        return cumpleBusqueda && cumpleEspecialidad;
    });

    renderizarTabla();
    actualizarEstadisticas();
}

// Función para cargar médicos desde API
async function cargarMedicos() {
    const tbody = document.getElementById('medicos-table-body');
    if (!tbody) {
        console.error('No se encontró el elemento medicos-table-body');
        return;
    }
    
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-8 text-center text-gray-500">
                    <i class="fas fa-spinner fa-spin mr-2"></i>
                    Cargando médicos...
                </td>
            </tr>
        `;

    try {
        // Cargar médicos desde API
        const response = await fetch('/reservas/api/medicos-todos', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        
        // Procesar datos recibidos
        if (data.medicos && Array.isArray(data.medicos)) {
            medicosData = data.medicos;
        } else if (Array.isArray(data)) {
            medicosData = data;
        } else {
            medicosData = [];
        }

        // Formatear datos para consistencia
        medicosData = medicosData.map(medico => ({
            id_empleado: medico.id_empleado,
            nombres: medico.nombres || '',
            apellidos: medico.apellidos || '',
            documento_identidad: medico.documento_identidad || medico.documento || '',
            correo: medico.correo || '',
            telefono: medico.telefono || '',
            especialidad: medico.especialidad || '',
            rol: medico.rol || 'Médico'
        }));

        // Extraer especialidades únicas
        medicosData.forEach(medico => {
            if (medico.especialidad) {
                especialidades.add(medico.especialidad);
            }
        });

        // Llenar select de especialidades
        const selectEspecialidad = document.getElementById('filtro-especialidad');
        if (selectEspecialidad) {
            especialidades.forEach(esp => {
                const option = document.createElement('option');
                option.value = esp;
                option.textContent = esp;
                selectEspecialidad.appendChild(option);
            });
        }

        aplicarFiltros();

    } catch (error) {
        console.error('Error al cargar médicos:', error);
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="px-6 py-8 text-center text-red-600">
                        <i class="fas fa-exclamation-circle mr-2"></i>
                        Error al cargar los médicos: ${error.message}
                    </td>
                </tr>
            `;
        }
    }
}

// Función para abrir modal y cargar servicios
async function verServicios(id, nombre, especialidad) {
    const modal = document.getElementById('servicios-modal');
    const serviciosList = document.getElementById('servicios-list');
    const medicoInfo = document.getElementById('medico-info');
    const modalTitle = document.getElementById('servicios-modal-title');

    // Validar que todos los elementos existan
    if (!modal) {
        console.error('No se encontró el modal servicios-modal');
        alert('Error: No se pudo abrir el modal. Por favor, recarga la página.');
        return;
    }

    if (!serviciosList) {
        console.error('No se encontró el elemento servicios-list');
        return;
    }

    if (!medicoInfo) {
        console.error('No se encontró el elemento medico-info');
        return;
    }

    // Actualizar título y info del médico
    if (modalTitle) {
        modalTitle.textContent = `Servicios de ${nombre}`;
    }
    
    medicoInfo.innerHTML = `
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-600 mb-1"><strong>Médico:</strong> ${nombre}</p>
                <p class="text-sm text-gray-600"><strong>Especialidad:</strong> ${especialidad}</p>
            </div>
            <div class="bg-cyan-100 rounded-full p-3">
                <i class="fas fa-user-md text-cyan-600 text-xl"></i>
            </div>
        </div>
    `;

    // Mostrar modal
    modal.classList.remove('hidden');

    // Resetear lista de servicios
    serviciosList.innerHTML = `
        <div class="flex justify-center items-center py-8">
            <i class="fas fa-spinner fa-spin text-cyan-600 text-2xl mr-2"></i>
            <span class="text-gray-600">Cargando servicios...</span>
        </div>
    `;

    try {
        const resp = await fetch(`/reservas/api/servicios-por-medico/${id}`);

        if (!resp.ok) {
            throw new Error('Error al obtener servicios');
        }

        const data = await resp.json();

        if (data.error) {
            serviciosList.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-circle text-red-500 text-3xl mb-2"></i>
                    <p class="text-red-600 font-semibold">${data.error}</p>
                </div>
            `;
            return;
        }

        const servicios = data.servicios || [];

        if (servicios.length === 0) {
            serviciosList.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-info-circle text-gray-400 text-3xl mb-2"></i>
                    <p class="text-gray-500 font-semibold">No hay servicios disponibles para este médico</p>
                    <p class="text-gray-400 text-sm mt-2">La especialidad del médico no tiene servicios asignados</p>
                </div>
            `;
            return;
        }

        // Renderizar servicios
        const ul = document.createElement('div');
        ul.className = 'grid grid-cols-1 md:grid-cols-2 gap-4';

        servicios.forEach(servicio => {
            const card = document.createElement('div');
            card.className = 'border border-gray-200 rounded-lg p-4 hover:border-cyan-500 hover:shadow-md transition-all';
            card.innerHTML = `
                <div class="flex items-start justify-between mb-2">
                    <div class="flex-1">
                        <h4 class="font-semibold text-gray-900 mb-1">
                            <i class="fas fa-concierge-bell text-cyan-600 mr-2"></i>
                            ${servicio.nombre}
                        </h4>
                        <p class="text-sm text-gray-600 mb-2">${servicio.descripcion || 'Sin descripción'}</p>
                    </div>
                </div>
                <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-200">
                    <span class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full font-semibold">
                        ${servicio.tipo_servicio || 'General'}
                    </span>
                    <span class="text-xs px-2 py-1 ${
                        servicio.estado === 'Activo'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                    } rounded-full font-semibold">
                        ${servicio.estado || 'Activo'}
                    </span>
                </div>
            `;
            ul.appendChild(card);
        });

        serviciosList.innerHTML = '';
        serviciosList.appendChild(ul);

    } catch (err) {
        console.error('Error:', err);
        serviciosList.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-2"></i>
                <p class="text-red-600 font-semibold">Error al cargar servicios</p>
                <p class="text-gray-500 text-sm mt-2">${err.message}</p>
            </div>
        `;
    }
}

// Función para cerrar modal
function cerrarModal() {
    const modal = document.getElementById('servicios-modal');
    modal.classList.add('hidden');
}

// Función para attachar listeners a botones de ver servicios
function attachVerServiciosListeners() {
    document.querySelectorAll('.ver-servicios-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const nombre = this.getAttribute('data-nombre');
            const especialidad = this.getAttribute('data-especialidad');
            verServicios(id, nombre, especialidad);
        });
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Cargar médicos
    cargarMedicos();

    // Búsqueda en tiempo real
    const searchEmployee = document.getElementById('search-employee');
    if (searchEmployee) {
        searchEmployee.addEventListener('input', aplicarFiltros);
    }

    // Filtro de especialidad
    const filtroEspecialidad = document.getElementById('filtro-especialidad');
    if (filtroEspecialidad) {
        filtroEspecialidad.addEventListener('change', aplicarFiltros);
    }

    // Botón limpiar
    const btnLimpiar = document.getElementById('btn-limpiar');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', function() {
            if (searchEmployee) searchEmployee.value = '';
            if (filtroEspecialidad) filtroEspecialidad.value = '';
            aplicarFiltros();
        });
    }

    // Cerrar modal
    const closeModal = document.getElementById('close-servicios-modal');
    const closeModalBtn = document.getElementById('close-servicios-modal-btn');
    if (closeModal) {
        closeModal.addEventListener('click', cerrarModal);
    }
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', cerrarModal);
    }

    // Cerrar modal con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            cerrarModal();
        }
    });

    // Cerrar modal clickeando fuera
    const serviciosModal = document.getElementById('servicios-modal');
    if (serviciosModal) {
        serviciosModal.addEventListener('click', function(e) {
            if (e.target === this) {
                cerrarModal();
            }
        });
    }

    // Cargar información del usuario
    try {
        if (window.usuario) {
            const u = window.usuario;
            const nameEl = document.getElementById('admin-username');
            const roleEl = document.getElementById('admin-role');
            if (nameEl && u.nombre) nameEl.textContent = u.nombre;
            if (roleEl && u.rol) roleEl.textContent = u.rol;
        }
    } catch (error) {
        console.error('Error al cargar datos de sesión:', error);
    }
});
