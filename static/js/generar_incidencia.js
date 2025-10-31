/**
 * Script para generar incidencias dinámicamente
 * Conecta con la tabla INCIDENCIA de la base de datos
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando página de generar incidencia...');
    
    // Cargar pacientes y empleados al iniciar
    cargarPacientes();
    cargarEmpleados();
    
    // Configurar fecha actual
    configurarFechaActual();
    
    // Configurar envío del formulario
    const formulario = document.getElementById('formIncidencia');
    if (formulario) {
        formulario.addEventListener('submit', enviarFormulario);
    }
});

/**
 * Configurar fecha y hora actual en el campo de fecha
 */
function configurarFechaActual() {
    const inputFecha = document.getElementById('fechaReporte');
    if (!inputFecha) return;
    
    const ahora = new Date();
    const opciones = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };
    
    const fechaFormateada = ahora.toLocaleString('es-PE', opciones);
    inputFecha.value = fechaFormateada;
    console.log('Fecha actual configurada:', fechaFormateada);
}

/**
 * Cargar lista de pacientes desde la BD
 */
async function cargarPacientes() {
    console.log('Cargando pacientes...');
    const selectPaciente = document.getElementById('selectPaciente');
    
    if (!selectPaciente) {
        console.error('No se encontró el select de pacientes');
        return;
    }
    
    try {
        const response = await fetch('/seguridad/api/pacientes', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Respuesta API pacientes status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Pacientes recibidos:', data);
        
        if (data.success && Array.isArray(data.pacientes)) {
            // Limpiar opciones anteriores (excepto la primera)
            selectPaciente.innerHTML = '<option value="">Seleccione un paciente</option>';
            
            // Agregar pacientes
            data.pacientes.forEach(paciente => {
                const option = document.createElement('option');
                option.value = paciente.id_paciente;
                option.textContent = `${paciente.nombres} ${paciente.apellidos} - DNI: ${paciente.dni}`;
                selectPaciente.appendChild(option);
            });
            
            console.log(`${data.pacientes.length} pacientes cargados exitosamente`);
        } else {
            console.error('Formato de datos inesperado:', data);
            mostrarError('Error al cargar la lista de pacientes');
        }
    } catch (error) {
        console.error('Error al cargar pacientes:', error);
        mostrarError('No se pudieron cargar los pacientes. Intente nuevamente.');
    }
}

/**
 * Cargar lista de empleados desde la BD
 */
async function cargarEmpleados() {
    console.log('Cargando empleados...');
    const selectEmpleado = document.getElementById('selectEmpleado');
    
    if (!selectEmpleado) {
        console.error('No se encontró el select de empleados');
        return;
    }
    
    try {
        const response = await fetch('/reportes/api/empleados', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Respuesta API empleados status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Empleados recibidos:', data);
        
        if (data.success && Array.isArray(data.empleados)) {
            // Limpiar opciones anteriores (excepto la primera)
            selectEmpleado.innerHTML = '<option value="">Asignar después</option>';
            
            // Agregar empleados
            data.empleados.forEach(empleado => {
                const option = document.createElement('option');
                option.value = empleado.id_empleado;
                option.textContent = `${empleado.nombres} ${empleado.apellidos} - ${empleado.cargo}`;
                selectEmpleado.appendChild(option);
            });
            
            console.log(`${data.empleados.length} empleados cargados exitosamente`);
        } else {
            console.error('Formato de datos inesperado:', data);
            console.warn('No se pudieron cargar los empleados (campo opcional)');
        }
    } catch (error) {
        console.error('Error al cargar empleados:', error);
        console.warn('Campo de empleado será opcional');
    }
}

/**
 * Enviar formulario de incidencia
 */
async function enviarFormulario(e) {
    e.preventDefault();
    console.log('Enviando formulario de incidencia...');
    
    const form = e.target;
    const btnSubmit = form.querySelector('button[type="submit"]');
    
    // Obtener valores del formulario
    const idPaciente = document.getElementById('selectPaciente').value;
    const descripcion = document.getElementById('descripcion').value.trim();
    const categoria = document.getElementById('categoria').value;
    const idEmpleado = document.getElementById('selectEmpleado').value;
    
    console.log('Datos del formulario:', {
        id_paciente: idPaciente,
        descripcion: descripcion,
        categoria: categoria,
        id_empleado: idEmpleado || 'Sin asignar'
    });
    
    // Validación
    if (!idPaciente) {
        mostrarError('Debe seleccionar un paciente');
        return;
    }
    
    if (!descripcion) {
        mostrarError('Debe ingresar una descripción');
        return;
    }
    
    if (!categoria) {
        mostrarError('Debe seleccionar una categoría');
        return;
    }
    
    // Deshabilitar botón durante el envío
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Guardando...';
    
    try {
        const payload = {
            id_paciente: parseInt(idPaciente),
            descripcion: descripcion,
            categoria: categoria
        };
        
        // Solo incluir id_empleado si se seleccionó uno
        if (idEmpleado) {
            payload.id_empleado = parseInt(idEmpleado);
        }
        
        const response = await fetch('/seguridad/api/incidencias/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        console.log('Respuesta del servidor status:', response.status);
        const data = await response.json();
        console.log('Respuesta del servidor:', data);
        
        if (data.success) {
            mostrarExito('Incidencia creada exitosamente');
            
            // Limpiar formulario
            form.reset();
            configurarFechaActual();
            
            // Redirigir después de 2 segundos
            setTimeout(() => {
                window.location.href = '/seguridad/incidencias/consultar-incidencia';
            }, 2000);
        } else {
            mostrarError(data.message || 'Error al crear la incidencia');
        }
    } catch (error) {
        console.error('Error al enviar formulario:', error);
        mostrarError('Error de conexión. Intente nuevamente.');
    } finally {
        // Rehabilitar botón
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="fas fa-plus-circle"></i> Crear Incidencia';
    }
}

/**
 * Mostrar mensaje de error
 */
function mostrarError(mensaje) {
    console.error('Error:', mensaje);
    
    // Buscar contenedor de mensajes o crear uno
    let contenedor = document.getElementById('mensajeContainer');
    if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.id = 'mensajeContainer';
        contenedor.className = 'fixed top-20 right-6 z-50';
        document.body.appendChild(contenedor);
    }
    
    // Crear alerta
    const alerta = document.createElement('div');
    alerta.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-lg mb-4 animate-fade-in';
    alerta.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-exclamation-circle text-xl mr-3"></i>
            <div>
                <p class="font-bold">Error</p>
                <p class="text-sm">${mensaje}</p>
            </div>
            <button class="ml-auto text-red-700 hover:text-red-900" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    contenedor.appendChild(alerta);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alerta.parentElement) {
            alerta.remove();
        }
    }, 5000);
}

/**
 * Mostrar mensaje de éxito
 */
function mostrarExito(mensaje) {
    console.log('Éxito:', mensaje);
    
    // Buscar contenedor de mensajes o crear uno
    let contenedor = document.getElementById('mensajeContainer');
    if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.id = 'mensajeContainer';
        contenedor.className = 'fixed top-20 right-6 z-50';
        document.body.appendChild(contenedor);
    }
    
    // Crear alerta
    const alerta = document.createElement('div');
    alerta.className = 'bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-lg mb-4 animate-fade-in';
    alerta.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-check-circle text-xl mr-3"></i>
            <div>
                <p class="font-bold">Éxito</p>
                <p class="text-sm">${mensaje}</p>
            </div>
            <button class="ml-auto text-green-700 hover:text-green-900" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    contenedor.appendChild(alerta);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        if (alerta.parentElement) {
            alerta.remove();
        }
    }, 3000);
}
