/**
 * Gestión de Cuentas Internas - Registro de Empleados
 * Validaciones y manejo del formulario de registro
 */

// Validacion de sesion
if (window.usuario) {
    const u = window.usuario;
    const nameEl = document.getElementById('admin-username');
    const roleEl = document.getElementById('admin-role');
    if (nameEl && u.nombre) nameEl.textContent = u.nombre;
    if (roleEl && u.rol) roleEl.textContent = u.rol;
}

// ========== CONSTANTES Y VARIABLES GLOBALES ==========
const modal = document.getElementById('register-employee-modal');
const openButton = document.getElementById('new-employee-button');
const closeButton = document.getElementById('close-register-employee-modal');
const employeeForm = document.querySelector('#register-employee-modal form');

let employeeDepartamentos = [];
let employeeProvincias = [];
let employeeDistritos = [];

// Expresiones regulares
const nameRegex = /^[\p{L}\s]+$/u;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const today = new Date();
const adultDate = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());

// Lista de IDs de campos para validación
const fieldIds = [
    'employee-nombres',
    'employee-apellidos',
    'employee-documento',
    'employee-sexo',
    'employee-telefono',
    'employee-nacimiento',
    'employee-email',
    'employee-departamento',
    'employee-provincia',
    'employee-distrito',
    'employee-password',
    'employee-confirm-password',
    'employee-rol'
];

// ========== FUNCIONES DE UTILIDAD ==========

/**
 * Establece o limpia el error de un campo
 */
const setFieldError = (fieldId, message) => {
    const field = document.getElementById(fieldId);
    if (!field) return;

    const errorElement = document.querySelector(`[data-error-for="${fieldId}"]`);
    const container = field.closest('div');

    if (message) {
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        }
        if (container) {
            container.classList.add('has-error');
        }
        field.setAttribute('aria-invalid', 'true');
        field.classList.add('border-red-500');
    } else {
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.add('hidden');
        }
        if (container) {
            container.classList.remove('has-error');
        }
        field.removeAttribute('aria-invalid');
        field.classList.remove('border-red-500');
    }
};

/**
 * Toggle visibilidad de contraseña
 */
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
    const confirmPasswordInput = document.getElementById('employee-confirm-password');
    const toggleIcon = document.getElementById('employee-confirm-password-toggle-icon');

    if (confirmPasswordInput.type === 'password') {
        confirmPasswordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        confirmPasswordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// ========== VALIDADORES DE CAMPOS ==========

const validators = {
    'employee-nombres': value => {
        if (!value) return 'El nombre es obligatorio';
        if (value.length < 2) return 'El nombre debe tener al menos 2 caracteres';
        if (value.length > 60) return 'El nombre no puede exceder 60 caracteres';
        if (!nameRegex.test(value)) return 'Solo se permiten letras y espacios';
        return '';
    },
    'employee-apellidos': value => {
        if (!value) return 'Los apellidos son obligatorios';
        if (value.length < 2) return 'Los apellidos deben tener al menos 2 caracteres';
        if (value.length > 60) return 'Los apellidos no pueden exceder 60 caracteres';
        if (!nameRegex.test(value)) return 'Solo se permiten letras y espacios';
        return '';
    },
    'employee-documento': (value, field) => {
        const digits = value.replace(/\D/g, '');
        if (digits !== value) {
            field.value = digits;
        }
        if (!digits) return 'El documento de identidad es obligatorio';
        if (digits.length < 8 || digits.length > 12) return 'El documento debe tener entre 8 y 12 dígitos';
        return '';
    },
    'employee-sexo': () => {
        const sexoSeleccionado = document.querySelector('input[name="sexo"]:checked');
        if (!sexoSeleccionado) return 'Debe seleccionar el sexo';
        return '';
    },
    'employee-telefono': (value, field) => {
        const digits = value.replace(/\D/g, '');
        if (digits !== value) {
            field.value = digits;
        }
        if (!digits) return 'El teléfono es obligatorio';
        if (digits.length < 6 || digits.length > 15) return 'El teléfono debe tener entre 6 y 15 dígitos';
        return '';
    },
    'employee-nacimiento': value => {
        if (!value) return 'La fecha de nacimiento es obligatoria';
        const selected = new Date(value);
        if (isNaN(selected.getTime())) return 'Fecha no válida';
        if (selected > adultDate) return 'El empleado debe ser mayor de edad (18 años)';
        if (selected < new Date('1900-01-01')) return 'Fecha de nacimiento no válida';
        return '';
    },
    'employee-email': value => {
        if (!value) return 'El correo electrónico es obligatorio';
        if (value.length > 120) return 'El correo no puede exceder 120 caracteres';
        if (!emailRegex.test(value)) return 'Formato de correo electrónico inválido';
        return '';
    },
    'employee-departamento': value => {
        if (!value) return 'Debe seleccionar un departamento';
        return '';
    },
    'employee-provincia': value => {
        if (!value) return 'Debe seleccionar una provincia';
        return '';
    },
    'employee-distrito': value => {
        if (!value) return 'Debe seleccionar un distrito';
        return '';
    },
    'employee-password': value => {
        if (!value) return 'La contraseña es obligatoria';
        if (value.length < 8) return 'La contraseña debe tener al menos 8 caracteres';
        if (value.length > 64) return 'La contraseña no puede exceder 64 caracteres';
        if (!/[A-Za-z]/.test(value)) return 'La contraseña debe incluir al menos una letra';
        if (!/\d/.test(value)) return 'La contraseña debe incluir al menos un número';
        if (!/[A-Z]/.test(value)) return 'La contraseña debe incluir al menos una mayúscula';
        return '';
    },
    'employee-confirm-password': value => {
        const password = document.getElementById('employee-password').value;
        if (!value) return 'Debe confirmar la contraseña';
        if (value !== password) return 'Las contraseñas no coinciden';
        return '';
    },
    'employee-rol': value => {
        if (!value) return 'Debe seleccionar un rol';
        return '';
    }
};

/**
 * Valida un campo individual
 */
const validateField = fieldId => {
    const field = document.getElementById(fieldId);

    // Para radio buttons (sexo), no hay un campo único
    if (fieldId === 'employee-sexo') {
        const validator = validators[fieldId];
        const message = validator ? validator() : "";
        setFieldError(fieldId, message || "");
        return !message;
    }

    if (!field) return true;

    const isPassword = field.type === "password";
    const value = isPassword ? field.value : field.value.trim();

    if (!isPassword && field.type !== "date" && field.tagName !== "SELECT") {
        field.value = value;
    }

    const validator = validators[fieldId];
    const message = validator ? validator(value, field) : "";
    setFieldError(fieldId, message || "");
    return !message;
};

/**
 * Resetea el formulario y limpia errores
 */
const resetEmployeeForm = () => {
    if (!employeeForm) return;
    employeeForm.reset();
    fieldIds.forEach(id => setFieldError(id, ''));

    // Resetear selects de ubicación
    const selectProvincia = document.getElementById('employee-provincia');
    const selectDistrito = document.getElementById('employee-distrito');

    if (selectProvincia) {
        selectProvincia.innerHTML = '<option value="">Seleccione un departamento primero...</option>';
        selectProvincia.disabled = true;
    }

    if (selectDistrito) {
        selectDistrito.innerHTML = '<option value="">Seleccione una provincia primero...</option>';
        selectDistrito.disabled = true;
    }

    // Ocultar campo especialidad
    const especialidadContainer = document.getElementById('employee-especialidad-container');
    if (especialidadContainer) {
        especialidadContainer.classList.add('hidden');
    }
};

// ========== CASCADA DE UBICACIONES ==========

/**
 * Cargar departamentos al inicializar
 */
async function cargarEmpleadoDepartamentos() {
    try {
        const response = await fetch('/usuarios/api/departamentos');
        employeeDepartamentos = await response.json();

        const selectDepartamento = document.getElementById('employee-departamento');
        selectDepartamento.innerHTML = '<option value="">Seleccione un departamento...</option>';

        employeeDepartamentos.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.id_departamento;
            option.textContent = dept.nombre;
            selectDepartamento.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar departamentos:', error);
        alert('Error al cargar departamentos. Por favor, recargue la página.');
    }
}

/**
 * Cargar provincias según departamento
 */
async function cargarEmpleadoProvincias(id_departamento) {
    try {
        const response = await fetch(`/usuarios/api/provincias/${id_departamento}`);
        employeeProvincias = await response.json();

        const selectProvincia = document.getElementById('employee-provincia');
        const selectDistrito = document.getElementById('employee-distrito');

        selectProvincia.innerHTML = '<option value="">Seleccione una provincia...</option>';
        selectDistrito.innerHTML = '<option value="">Seleccione una provincia primero...</option>';
        selectDistrito.disabled = true;

        employeeProvincias.forEach(prov => {
            const option = document.createElement('option');
            option.value = prov.id_provincia;
            option.textContent = prov.nombre;
            selectProvincia.appendChild(option);
        });

        selectProvincia.disabled = false;
    } catch (error) {
        console.error('Error al cargar provincias:', error);
        alert('Error al cargar provincias. Por favor, intente nuevamente.');
    }
}

/**
 * Cargar distritos según provincia
 */
async function cargarEmpleadoDistritos(id_provincia) {
    try {
        const response = await fetch(`/usuarios/api/distritos/${id_provincia}`);
        employeeDistritos = await response.json();

        const selectDistrito = document.getElementById('employee-distrito');
        selectDistrito.innerHTML = '<option value="">Seleccione un distrito...</option>';

        employeeDistritos.forEach(dist => {
            const option = document.createElement('option');
            option.value = dist.id_distrito;
            option.textContent = dist.nombre;
            selectDistrito.appendChild(option);
        });

        selectDistrito.disabled = false;
    } catch (error) {
        console.error('Error al cargar distritos:', error);
        alert('Error al cargar distritos. Por favor, intente nuevamente.');
    }
}

// ========== MANEJO DE ESPECIALIDADES ==========

/**
 * Cargar especialidades cuando se abre el modal
 */
async function cargarEspecialidades() {
    try {
        const response = await fetch('/cuentas/api/especialidades');
        const especialidades = await response.json();

        const selectEspecialidad = document.getElementById('employee-especialidad');
        selectEspecialidad.innerHTML = '<option value="">Seleccione una especialidad</option>';

        especialidades.forEach(esp => {
            const option = document.createElement('option');
            option.value = esp.id_especialidad;
            option.textContent = esp.nombre;
            selectEspecialidad.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar especialidades:', error);
    }
}

// ========== EVENT LISTENERS ==========

/**
 * Event listeners para la cascada de ubicación
 */
document.getElementById('employee-departamento')?.addEventListener('change', function() {
    const id_departamento = this.value;
    const selectProvincia = document.getElementById('employee-provincia');
    const selectDistrito = document.getElementById('employee-distrito');

    if (id_departamento) {
        cargarEmpleadoProvincias(id_departamento);
    } else {
        selectProvincia.innerHTML = '<option value="">Seleccione un departamento primero...</option>';
        selectProvincia.disabled = true;
        selectDistrito.innerHTML = '<option value="">Seleccione una provincia primero...</option>';
        selectDistrito.disabled = true;
    }
});

document.getElementById('employee-provincia')?.addEventListener('change', function() {
    const id_provincia = this.value;
    const selectDistrito = document.getElementById('employee-distrito');

    if (id_provincia) {
        cargarEmpleadoDistritos(id_provincia);
    } else {
        selectDistrito.innerHTML = '<option value="">Seleccione una provincia primero...</option>';
        selectDistrito.disabled = true;
    }
});

/**
 * Mostrar/Ocultar especialidades según el rol seleccionado
 */
document.getElementById('employee-rol')?.addEventListener('change', function() {
    const rolSelect = this;
    const especialidadContainer = document.getElementById('employee-especialidad-container');
    const especialidadSelect = document.getElementById('employee-especialidad');

    // Obtener el texto del rol seleccionado
    const rolTexto = rolSelect.options[rolSelect.selectedIndex]?.text || '';

    // Verificar si el rol contiene "Médico" o "Medico" (case insensitive)
    if (rolTexto.toLowerCase().includes('medico') || rolTexto.toLowerCase().includes('médico')) {
        especialidadContainer.classList.remove('hidden');
        especialidadSelect.required = true;
        cargarEspecialidades();
    } else {
        especialidadContainer.classList.add('hidden');
        especialidadSelect.required = false;
        especialidadSelect.value = '';
    }
});

/**
 * Configuración de validaciones en tiempo real
 */
if (employeeForm) {
    // Configurar fecha máxima para el campo de nacimiento
    const nacimientoInput = document.getElementById('employee-nacimiento');
    if (nacimientoInput) {
        nacimientoInput.max = adultDate.toISOString().split('T')[0];
    }

    // Agregar event listeners para validación en tiempo real
    fieldIds.forEach(id => {
        const field = document.getElementById(id);

        // Para radio buttons (sexo)
        if (id === 'employee-sexo') {
            const radioButtons = document.querySelectorAll('input[name="sexo"]');
            radioButtons.forEach(radio => {
                radio.addEventListener('change', () => validateField(id));
            });
            return;
        }

        if (!field) return;

        const eventName = field.tagName === 'SELECT' || field.type === 'date' ? 'change' : 'input';
        field.addEventListener(eventName, () => validateField(id));
        field.addEventListener('blur', () => validateField(id));
    });

    // Validar también cuando cambia la contraseña para revalidar confirmación
    document.getElementById('employee-password')?.addEventListener('input', () => {
        const confirmField = document.getElementById('employee-confirm-password');
        if (confirmField && confirmField.value) {
            validateField('employee-confirm-password');
        }
    });

    // Validación de solo números en documento y teléfono
    document.getElementById('employee-documento')?.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
    
    document.getElementById('employee-telefono')?.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    /**
     * Manejo del envío del formulario
     */
    employeeForm.addEventListener('submit', event => {
        event.preventDefault();

        // Validar todos los campos
        let isValid = true;
        let firstInvalid = null;

        fieldIds.forEach(id => {
            if (!validateField(id)) {
                isValid = false;
                if (!firstInvalid) {
                    firstInvalid = id;
                }
            }
        });

        // Validar especialidad si es médico
        const rolSelect = document.getElementById('employee-rol');
        const rolTexto = rolSelect.options[rolSelect.selectedIndex]?.text || '';
        const especialidadSelect = document.getElementById('employee-especialidad');

        if ((rolTexto.toLowerCase().includes('medico') || rolTexto.toLowerCase().includes('médico'))) {
            if (!especialidadSelect.value) {
                setFieldError('employee-especialidad', 'Debe seleccionar una especialidad');
                isValid = false;
                if (!firstInvalid) firstInvalid = 'employee-especialidad';
            } else {
                setFieldError('employee-especialidad', '');
            }
        }

        if (!isValid) {
            // Hacer scroll al primer campo inválido
            const firstInvalidField = document.getElementById(firstInvalid);
            if (firstInvalidField) {
                firstInvalidField.focus();
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }

        // Si todo es válido, enviar el formulario
        employeeForm.submit();
    });
}

/**
 * Control del modal
 */
const toggleModal = shouldOpen => {
    if (!modal) return;

    if (shouldOpen) {
        resetEmployeeForm();
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        cargarEmpleadoDepartamentos();
        requestAnimationFrame(() => {
            document.getElementById('employee-nombres')?.focus();
        });
    } else {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        resetEmployeeForm();
    }
};

openButton?.addEventListener('click', () => toggleModal(true));
closeButton?.addEventListener('click', () => toggleModal(false));

// Cerrar modal al hacer clic fuera
modal?.addEventListener('click', event => {
    if (event.target === modal) {
        toggleModal(false);
    }
});

// Cerrar modal con tecla Escape
document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
        toggleModal(false);
    }
});

// ========== BÚSQUEDA DE EMPLEADOS (DESHABILITADO - Ahora se usa paginación dinámica) ==========
// El código de búsqueda antiguo ha sido reemplazado por la paginación dinámica con API

// ========== ELIMINAR EMPLEADO ==========

/**
 * Función para eliminar empleado
 */
function eliminarEmpleado(idEmpleado, nombreCompleto) {
    if (!confirm(`¿Está seguro de eliminar al empleado ${nombreCompleto}?\n\nEsta acción desactivará la cuenta del empleado.`)) {
        return;
    }
    
    // Redirigir al endpoint que maneja la eliminación con tab=empleados
    window.location.href = `/cuentas/eliminar-empleado/${idEmpleado}?tab=empleados`;
}

// ========== PAGINACIÓN DINÁMICA SOLO CON NÚMEROS ========
// Variables globales
let paginaActual = 1;
const registrosPorPagina = 20;
let empleadosGlobal = []; // Guardar los empleados cargados

function poblarTabla(empleados) {
    const tbody = document.getElementById('tabla-empleados-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    empleadosGlobal = empleados; // Guardamos todos los empleados para paginar
    if (!empleados || empleados.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="6" class="px-6 py-4 text-center text-gray-500">No se encontraron empleados</td>';
        tbody.appendChild(tr);
        actualizarPaginacion(0);
        return;
    }

    // Calcular índices para la página actual
    const totalRegistros = empleados.length;
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, totalRegistros);
    const empleadosPagina = empleados.slice(inicio, fin);

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
    poblarTabla(empleadosGlobal);
}

// ========== INICIALIZACIÓN ===========
document.addEventListener('DOMContentLoaded', function() {
    // Cargar empleados y pacientes al inicializar la página
    cargarEmpleados();
    cargarPacientes();
});

async function cargarEmpleados() {
    try {
        const response = await fetch('/cuentas/api/empleados');
        const empleados = await response.json();
        poblarTabla(empleados);
    } catch (error) {
        console.error('Error al cargar empleados:', error);
    }
}

// ========== PAGINACIÓN PARA PACIENTES ==========
let paginaActualPacientes = 1;
const registrosPorPaginaPacientes = 20;
let pacientesGlobal = []; // Guardar los pacientes cargados

function poblarTablaPacientes(pacientes) {
    const tbody = document.getElementById('tabla-pacientes-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    pacientesGlobal = pacientes; // Guardamos todos los pacientes para paginar
    if (!pacientes || pacientes.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="6" class="px-6 py-4 text-center text-gray-500">No se encontraron pacientes</td>';
        tbody.appendChild(tr);
        actualizarPaginacionPacientes(0);
        return;
    }

    // Calcular índices para la página actual
    const totalRegistros = pacientes.length;
    const inicio = (paginaActualPacientes - 1) * registrosPorPaginaPacientes;
    const fin = Math.min(inicio + registrosPorPaginaPacientes, totalRegistros);
    const pacientesPagina = pacientes.slice(inicio, fin);

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

    // Actualizar paginación visual
    actualizarPaginacionPacientes(totalRegistros);
}

function actualizarPaginacionPacientes(totalRegistros) {
    const paginacionContainer = document.getElementById('paginacionNumeros-pacientes');
    const inicioRango = document.getElementById('inicio-rango-pacientes');
    const finRango = document.getElementById('fin-rango-pacientes');
    const totalRegistrosSpan = document.getElementById('total-registros-pacientes');

    const totalPaginas = Math.ceil(totalRegistros / registrosPorPaginaPacientes);
    paginacionContainer.innerHTML = '';

    // Mostrar rango y total
    const inicio = totalRegistros === 0 ? 0 : (paginaActualPacientes - 1) * registrosPorPaginaPacientes + 1;
    const fin = Math.min(paginaActualPacientes * registrosPorPaginaPacientes, totalRegistros);
    inicioRango.textContent = inicio;
    finRango.textContent = fin;
    totalRegistrosSpan.textContent = totalRegistros;

    if (totalPaginas <= 1) return; // No mostrar si solo hay 1 página

    // Limitar cantidad de botones visibles (ej. máx 6)
    const maxVisible = 6;
    let inicioPagina = Math.max(1, paginaActualPacientes - 2);
    let finPagina = Math.min(totalPaginas, inicioPagina + maxVisible - 1);

    if (finPagina - inicioPagina < maxVisible - 1) {
        inicioPagina = Math.max(1, finPagina - maxVisible + 1);
    }

    // Crear botones de página
    for (let i = inicioPagina; i <= finPagina; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === paginaActualPacientes
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', () => cambiarPaginaPacientes(i));
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
        ultimoBtn.addEventListener('click', () => cambiarPaginaPacientes(totalPaginas));
        paginacionContainer.appendChild(ultimoBtn);
    }
}

function cambiarPaginaPacientes(numeroPagina) {
    paginaActualPacientes = numeroPagina;
    poblarTablaPacientes(pacientesGlobal);
}

async function cargarPacientes() {
    try {
        const response = await fetch('/cuentas/api/pacientes');
        const pacientes = await response.json();
        poblarTablaPacientes(pacientes);
    } catch (error) {
        console.error('Error al cargar pacientes:', error);
    }
}
