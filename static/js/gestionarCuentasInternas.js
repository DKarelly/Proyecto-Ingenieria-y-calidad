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

// ========== BÚSQUEDA DE EMPLEADOS ==========

const searchEmpleadoInput = document.getElementById('search-empleado');
const clearSearchEmpleado = document.getElementById('clear-search-empleado');
const empleadoRows = document.querySelectorAll('.admin-table tbody tr');

searchEmpleadoInput?.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase().trim();

    // Mostrar/ocultar botón de limpiar
    if (searchTerm) {
        clearSearchEmpleado?.classList.remove('hidden');
    } else {
        clearSearchEmpleado?.classList.add('hidden');
    }

    // Filtrar filas de la tabla
    empleadoRows.forEach(row => {
        if (row.querySelector('td[colspan]')) return; // Skip empty state row

        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

// Limpiar búsqueda de empleados
clearSearchEmpleado?.addEventListener('click', function() {
    searchEmpleadoInput.value = '';
    searchEmpleadoInput.dispatchEvent(new Event('input'));
    searchEmpleadoInput.focus();
});

// ========== ELIMINAR EMPLEADO ==========

/**
 * Función para eliminar empleado
 */
function eliminarEmpleado(idEmpleado, nombreCompleto) {
    if (!confirm(`¿Está seguro de eliminar al empleado ${nombreCompleto}?\n\nEsta acción desactivará la cuenta del empleado.`)) {
        return;
    }

    fetch(`/cuentas/eliminar-empleado/${idEmpleado}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message || 'Empleado eliminado correctamente');
            window.location.reload();
        } else {
            alert('Error: ' + (data.message || 'No se pudo eliminar el empleado'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud');
    });
}
