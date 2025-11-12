/**
 * Paginación para Gestión de Cuentas Internas - Versión Limpia
 */

// Variables globales para empleados
let paginaActual = 1;
const registrosPorPagina = 20;
let empleadosGlobal = [];

// Variables globales para pacientes
let paginaActualPacientes = 1;
const registrosPorPaginaPacientes = 20;
let pacientesGlobal = [];

// ========== FUNCIONES DE EMPLEADOS ==========
function poblarTablaEmpleados(empleados) {
    const tbody = document.getElementById('tabla-empleados-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    empleadosGlobal = empleados;
    
    if (!empleados || empleados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No se encontraron empleados</td></tr>';
        actualizarPaginacionEmpleados(0);
        return;
    }

    // Calcular registros para la página actual
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, empleados.length);
    const empleadosPagina = empleados.slice(inicio, fin);

    // Renderizar filas
    empleadosPagina.forEach(empleado => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 transition-colors';
        tr.innerHTML = `
            <td class="px-6 py-4 font-semibold text-slate-700">#${empleado.id_empleado}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                    <div class="h-10 w-10 rounded-full bg-cyan-100 flex items-center justify-center">
                        <i class="fa-solid fa-user text-cyan-600"></i>
                    </div>
                    <span class="text-sm font-semibold text-slate-900">${empleado.nombres} ${empleado.apellidos}</span>
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
                <i class="fa-solid fa-envelope text-slate-400 mr-2"></i>
                ${empleado.correo}
            </td>
            <td class="px-6 py-4">
                <span class="admin-badge info inline-flex items-center">
                    <i class="fa-solid fa-user-tag mr-1.5"></i>
                    ${empleado.rol || 'Sin rol'}
                </span>
            </td>
            <td class="px-6 py-4">
                <span class="admin-badge success inline-flex items-center">
                    <i class="fa-solid fa-circle-check mr-1.5"></i>
                    Activo
                </span>
            </td>
            <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center gap-2">
                    <a href="/cuentas/editar-empleado/${empleado.id_empleado}" 
                       class="btn btn-outline text-cyan-600 hover:text-white hover:bg-cyan-500" 
                       title="Editar">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </a>
                    <button onclick="eliminarEmpleado(${empleado.id_empleado}, '${empleado.nombres} ${empleado.apellidos}')" 
                            class="btn btn-outline text-red-600 hover:text-white hover:bg-red-500" 
                            title="Eliminar">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });

    actualizarPaginacionEmpleados(empleados.length);
}

function actualizarPaginacionEmpleados(totalRegistros) {
    const paginacionContainer = document.getElementById('paginacionNumeros');
    const inicioRango = document.getElementById('inicio-rango');
    const finRango = document.getElementById('fin-rango');
    const totalRegistrosSpan = document.getElementById('total-registros');

    if (!paginacionContainer || !inicioRango || !finRango || !totalRegistrosSpan) return;

    const totalPaginas = Math.ceil(totalRegistros / registrosPorPagina);
    paginacionContainer.innerHTML = '';

    // Actualizar texto de rango
    const inicio = totalRegistros === 0 ? 0 : (paginaActual - 1) * registrosPorPagina + 1;
    const fin = Math.min(paginaActual * registrosPorPagina, totalRegistros);
    inicioRango.textContent = inicio;
    finRango.textContent = fin;
    totalRegistrosSpan.textContent = totalRegistros;

    if (totalPaginas <= 1) return;

    // Crear botones de página
    for (let i = 1; i <= totalPaginas; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === paginaActual
                ? 'bg-cyan-600 text-white border-cyan-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', () => {
            paginaActual = i;
            poblarTablaEmpleados(empleadosGlobal);
        });
        paginacionContainer.appendChild(btn);
    }
}

// ========== FUNCIONES DE PACIENTES ==========
function poblarTablaPacientes(pacientes) {
    const tbody = document.getElementById('tabla-pacientes-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    pacientesGlobal = pacientes;
    
    if (!pacientes || pacientes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No se encontraron pacientes</td></tr>';
        actualizarPaginacionPacientes(0);
        return;
    }

    // Calcular registros para la página actual
    const inicio = (paginaActualPacientes - 1) * registrosPorPaginaPacientes;
    const fin = Math.min(inicio + registrosPorPaginaPacientes, pacientes.length);
    const pacientesPagina = pacientes.slice(inicio, fin);

    // Renderizar filas
    pacientesPagina.forEach(paciente => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 transition-colors';
        tr.innerHTML = `
            <td class="px-6 py-4 font-semibold text-slate-700">#${paciente.id_paciente}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                    <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <i class="fa-solid fa-user-injured text-blue-600"></i>
                    </div>
                    <span class="text-sm font-semibold text-slate-900">${paciente.nombres} ${paciente.apellidos}</span>
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
                <i class="fa-solid fa-envelope text-slate-400 mr-2"></i>
                ${paciente.correo || 'N/A'}
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
                <i class="fa-solid fa-id-card text-slate-400 mr-2"></i>
                ${paciente.documento_identidad || 'N/A'}
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
                <i class="fa-solid fa-phone text-slate-400 mr-2"></i>
                ${paciente.telefono || 'N/A'}
            </td>
            <td class="px-6 py-4">
                <span class="admin-badge success inline-flex items-center">
                    <i class="fa-solid fa-circle-check mr-1.5"></i>
                    Activo
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });

    actualizarPaginacionPacientes(pacientes.length);
}

function actualizarPaginacionPacientes(totalRegistros) {
    const paginacionContainer = document.getElementById('paginacionNumeros-pacientes');
    const inicioRango = document.getElementById('inicio-rango-pacientes');
    const finRango = document.getElementById('fin-rango-pacientes');
    const totalRegistrosSpan = document.getElementById('total-registros-pacientes');

    if (!paginacionContainer || !inicioRango || !finRango || !totalRegistrosSpan) return;

    const totalPaginas = Math.ceil(totalRegistros / registrosPorPaginaPacientes);
    paginacionContainer.innerHTML = '';

    // Actualizar texto de rango
    const inicio = totalRegistros === 0 ? 0 : (paginaActualPacientes - 1) * registrosPorPaginaPacientes + 1;
    const fin = Math.min(paginaActualPacientes * registrosPorPaginaPacientes, totalRegistros);
    inicioRango.textContent = inicio;
    finRango.textContent = fin;
    totalRegistrosSpan.textContent = totalRegistros;

    if (totalPaginas <= 1) return;

    // Crear botones de página
    for (let i = 1; i <= totalPaginas; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === paginaActualPacientes
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', () => {
            paginaActualPacientes = i;
            poblarTablaPacientes(pacientesGlobal);
        });
        paginacionContainer.appendChild(btn);
    }
}

// ========== CARGA DE DATOS ==========
async function cargarEmpleados() {
    try {
        console.log('Cargando empleados...');
        const response = await fetch('/cuentas/api/empleados');
        const empleados = await response.json();
        console.log('Empleados cargados:', empleados.length);
        poblarTablaEmpleados(empleados);
    } catch (error) {
        console.error('Error al cargar empleados:', error);
    }
}

async function cargarPacientes() {
    try {
        console.log('Cargando pacientes...');
        const response = await fetch('/cuentas/api/pacientes');
        const pacientes = await response.json();
        console.log('Pacientes cargados:', pacientes.length);
        poblarTablaPacientes(pacientes);
    } catch (error) {
        console.error('Error al cargar pacientes:', error);
    }
}

// ========== FUNCIONES AUXILIARES ==========
function eliminarEmpleado(idEmpleado, nombreCompleto) {
    if (!confirm(`¿Está seguro de eliminar al empleado ${nombreCompleto}?\n\nEsta acción desactivará la cuenta del empleado.`)) {
        return;
    }
    window.location.href = `/cuentas/eliminar-empleado/${idEmpleado}?tab=empleados`;
}

function toggleEmployeePassword() {
    const passwordInput = document.getElementById('employee-password');
    const toggleIcon = document.getElementById('employee-password-toggle-icon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

function toggleEmployeeConfirmPassword() {
    const passwordInput = document.getElementById('employee-confirm-password');
    const toggleIcon = document.getElementById('employee-confirm-password-toggle-icon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// ========== MANEJO DE MODAL ==========
function abrirModalEmpleado() {
    const modal = document.getElementById('register-employee-modal');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevenir scroll del body
    }
}

function cerrarModalEmpleado() {
    const modal = document.getElementById('register-employee-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = ''; // Restaurar scroll del body
    }
}

// ========== BÚSQUEDA DE EMPLEADOS ==========
function buscarEmpleados() {
    const searchInput = document.getElementById('search-empleado');
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        poblarTablaEmpleados(empleadosGlobal);
        return;
    }
    
    const empleadosFiltrados = empleadosGlobal.filter(empleado => {
        const nombreCompleto = `${empleado.nombres} ${empleado.apellidos}`.toLowerCase();
        const email = (empleado.correo || '').toLowerCase();
        const rol = (empleado.rol || '').toLowerCase();
        
        return nombreCompleto.includes(searchTerm) || 
               email.includes(searchTerm) || 
               rol.includes(searchTerm);
    });
    
    paginaActual = 1; // Reset a primera página
    poblarTablaEmpleados(empleadosFiltrados);
}

// ========== INICIALIZACIÓN ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, inicializando paginación...');
    cargarEmpleados();
    cargarPacientes();
    
    // Event listener para abrir modal
    const btnNuevoEmpleado = document.getElementById('new-employee-button');
    if (btnNuevoEmpleado) {
        btnNuevoEmpleado.addEventListener('click', abrirModalEmpleado);
    }
    
    // Event listener para cerrar modal
    const btnCerrarModal = document.getElementById('close-register-employee-modal');
    if (btnCerrarModal) {
        btnCerrarModal.addEventListener('click', cerrarModalEmpleado);
    }
    
    // Cerrar modal al hacer clic fuera de él
    const modal = document.getElementById('register-employee-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                cerrarModalEmpleado();
            }
        });
    }
    
    // Event listener para búsqueda
    const searchInput = document.getElementById('search-empleado');
    if (searchInput) {
        searchInput.addEventListener('input', buscarEmpleados);
    }
    
    // Event listener para limpiar búsqueda
    const clearSearchBtn = document.getElementById('clear-search-empleado');
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', function() {
            searchInput.value = '';
            clearSearchBtn.classList.add('hidden');
            buscarEmpleados();
        });
    }
    
    // Mostrar/ocultar botón de limpiar búsqueda
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const clearBtn = document.getElementById('clear-search-empleado');
            if (this.value.trim() !== '') {
                clearBtn.classList.remove('hidden');
            } else {
                clearBtn.classList.add('hidden');
            }
        });
    }
});