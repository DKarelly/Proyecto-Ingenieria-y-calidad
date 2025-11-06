/**
 * Script para el registro de exámenes de laboratorio
 * Carga servicios dinámicamente y valida horarios disponibles
 */

// Variables globales
let servicioSeleccionado = null;
let currentStep = 1;
let serviciosDisponibles = [];

// Elementos del DOM
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Cargar servicios de examen desde la BD
    cargarServiciosExamen();

    // Configurar fecha mínima (hoy)
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('fechaExamen').setAttribute('min', hoy);

    // Event listener para cambio de fecha
    document.getElementById('fechaExamen').addEventListener('change', function() {
        const fecha = this.value;
        if (fecha) {
            cargarHorariosDisponibles(fecha);
        }
    });

    // Event listener para cambio de hora
    document.getElementById('horaExamen').addEventListener('change', function() {
        const hora = this.value;
        const fecha = document.getElementById('fechaExamen').value;
        
        if (fecha && hora) {
            document.getElementById('btnStep2Next').disabled = false;
        } else {
            document.getElementById('btnStep2Next').disabled = true;
        }
    });

    // Navegación entre pasos
    document.getElementById('btnStep1Next').addEventListener('click', function() {
        if (servicioSeleccionado) {
            goToStep(2);
        } else {
            alert('Por favor, selecciona un tipo de examen');
        }
    });

    document.getElementById('btnStep2Back').addEventListener('click', () => goToStep(1));
    document.getElementById('btnStep2Next').addEventListener('click', function() {
        const fecha = document.getElementById('fechaExamen').value;
        const hora = document.getElementById('horaExamen').value;

        if (!fecha || !hora) {
            alert('Por favor, completa la fecha y hora del examen');
            return;
        }

        mostrarResumen();
        goToStep(3);
    });

    document.getElementById('btnStep3Back').addEventListener('click', () => goToStep(2));

    // Submit del formulario
    document.getElementById('examenForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await confirmarExamen();
    });
});

async function cargarServiciosExamen() {
    const loadingDiv = document.getElementById('loadingServicios');
    const containerDiv = document.getElementById('serviciosContainer');
    const errorDiv = document.getElementById('errorServicios');

    try {
        const response = await fetch('/reservas/api/servicios-examen');
        const data = await response.json();

        if (response.ok && data.success) {
            serviciosDisponibles = data.servicios;
            
            if (serviciosDisponibles.length === 0) {
                errorDiv.querySelector('p').textContent = 'No hay servicios de examen disponibles en este momento.';
                errorDiv.classList.remove('hidden');
                loadingDiv.classList.add('hidden');
                return;
            }

            // Renderizar servicios
            containerDiv.innerHTML = '';
            
            // Iconos y colores por categoría
            const categorias = {
                'Hemograma': { color: 'red', icon: 'M20 13.5V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v6.5M4 17.5L12 22l8-4.5M12 22v-6' },
                'Perfil': { color: 'orange', icon: 'M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z' },
                'Radiografía': { color: 'blue', icon: 'M3 3h18M3 21h18M3 3v18M21 3v18' },
                'Ecografía': { color: 'purple', icon: 'M12 2v20M2 12h20' },
                'Tomografía': { color: 'indigo', icon: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5' },
                'Electrocardiograma': { color: 'pink', icon: 'M3 12h4l3-9 4 18 3-9h4' },
                'Examen': { color: 'green', icon: 'M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z' }
            };

            serviciosDisponibles.forEach(servicio => {
                // Determinar categoría
                let categoria = 'Examen';
                for (let cat in categorias) {
                    if (servicio.nombre.includes(cat)) {
                        categoria = cat;
                        break;
                    }
                }

                const config = categorias[categoria];
                const colorClass = `${config.color}-100`;
                const colorStroke = {
                    'red': '#dc2626',
                    'orange': '#ea580c',
                    'blue': '#2563eb',
                    'purple': '#9333ea',
                    'indigo': '#4f46e5',
                    'pink': '#ec4899',
                    'green': '#16a34a'
                }[config.color];

                const card = document.createElement('div');
                card.className = 'servicio-card border-2 border-gray-200 rounded-lg p-4 hover:border-orange-500 cursor-pointer transition-all';
                card.dataset.servicioId = servicio.id_servicio;
                card.dataset.servicioNombre = servicio.nombre;
                
                card.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-${colorClass} rounded-lg flex items-center justify-center flex-shrink-0">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${colorStroke}" stroke-width="2">
                                <path d="${config.icon}"/>
                            </svg>
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="font-semibold text-gray-800 truncate">${servicio.nombre}</p>
                            <p class="text-sm text-gray-500 truncate">${servicio.descripcion || 'Examen de diagnóstico'}</p>
                        </div>
                    </div>
                `;

                card.addEventListener('click', function() {
                    // Remover selección anterior
                    document.querySelectorAll('.servicio-card').forEach(c => {
                        c.classList.remove('border-orange-500', 'bg-orange-50');
                        c.classList.add('border-gray-200');
                    });

                    // Marcar como seleccionado
                    this.classList.remove('border-gray-200');
                    this.classList.add('border-orange-500', 'bg-orange-50');

                    servicioSeleccionado = {
                        id: servicio.id_servicio,
                        nombre: servicio.nombre,
                        descripcion: servicio.descripcion
                    };

                    // Habilitar botón continuar
                    document.getElementById('btnStep1Next').disabled = false;
                });

                containerDiv.appendChild(card);
            });

            // Mostrar grid y ocultar loading
            loadingDiv.classList.add('hidden');
            containerDiv.classList.remove('hidden');

        } else {
            throw new Error(data.error || 'Error al cargar servicios');
        }

    } catch (error) {
        console.error('Error:', error);
        errorDiv.classList.remove('hidden');
        loadingDiv.classList.add('hidden');
    }
}

async function cargarHorariosDisponibles(fecha) {
    const selectHora = document.getElementById('horaExamen');
    const loadingDiv = document.getElementById('loadingHorarios');
    
    // Mostrar loading
    loadingDiv.classList.remove('hidden');
    selectHora.disabled = true;
    selectHora.innerHTML = '<option value="">Cargando horarios...</option>';
    document.getElementById('btnStep2Next').disabled = true;

    try {
        const response = await fetch(`/reservas/api/horarios-disponibles-examen?fecha=${fecha}`);
        const data = await response.json();

        if (response.ok && data.success) {
            if (data.horarios.length === 0) {
                selectHora.innerHTML = '<option value="">No hay horarios disponibles para esta fecha</option>';
                loadingDiv.classList.add('hidden');
                return;
            }

            // Llenar select con horarios disponibles
            selectHora.innerHTML = '<option value="">Selecciona una hora</option>';
            
            data.horarios.forEach(horario => {
                const option = document.createElement('option');
                option.value = horario.hora_inicio;
                option.textContent = `${horario.hora_inicio} - ${horario.hora_fin}`;
                selectHora.appendChild(option);
            });

            selectHora.disabled = false;
            loadingDiv.classList.add('hidden');

        } else {
            throw new Error(data.error || 'Error al cargar horarios');
        }

    } catch (error) {
        console.error('Error:', error);
        selectHora.innerHTML = '<option value="">Error al cargar horarios. Intenta con otra fecha.</option>';
        loadingDiv.classList.add('hidden');
        alert('Error al cargar horarios disponibles. Por favor, intenta con otra fecha.');
    }
}

function goToStep(step) {
    // Ocultar todos los pasos
    step1.classList.add('hidden');
    step2.classList.add('hidden');
    step3.classList.add('hidden');

    // Mostrar paso actual
    if (step === 1) step1.classList.remove('hidden');
    else if (step === 2) step2.classList.remove('hidden');
    else if (step === 3) step3.classList.remove('hidden');

    // Actualizar indicadores
    updateStepIndicators(step);
    currentStep = step;

    // Scroll hacia arriba
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateStepIndicators(step) {
    const indicators = [
        { ind: 'step1-indicator', text: 'step1-text', line: null },
        { ind: 'step2-indicator', text: 'step2-text', line: 'line1' },
        { ind: 'step3-indicator', text: 'step3-text', line: 'line2' }
    ];

    indicators.forEach((item, index) => {
        const indicator = document.getElementById(item.ind);
        const text = document.getElementById(item.text);
        const line = item.line ? document.getElementById(item.line) : null;

        if (index + 1 < step) {
            // Completado
            indicator.className = 'step-indicator step-completed w-12 h-12 rounded-full flex items-center justify-center font-bold mb-2';
            text.className = 'text-sm font-medium text-green-600';
            if (line) line.className = 'flex-1 h-1 bg-green-500 mx-2';
        } else if (index + 1 === step) {
            // Activo
            indicator.className = 'step-indicator step-active w-12 h-12 rounded-full flex items-center justify-center font-bold mb-2';
            text.className = 'text-sm font-medium text-orange-600';
            if (line) line.className = 'flex-1 h-1 bg-gray-300 mx-2';
        } else {
            // Inactivo
            indicator.className = 'step-indicator step-inactive w-12 h-12 rounded-full flex items-center justify-center font-bold mb-2';
            text.className = 'text-sm font-medium text-gray-400';
            if (line) line.className = 'flex-1 h-1 bg-gray-300 mx-2';
        }
    });
}

function mostrarResumen() {
    const fecha = document.getElementById('fechaExamen').value;
    const hora = document.getElementById('horaExamen').value;
    const observaciones = document.getElementById('observaciones').value.trim();

    // Formatear fecha
    const fechaObj = new Date(fecha + 'T00:00:00');
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const fechaFormateada = fechaObj.toLocaleDateString('es-ES', options);

    document.getElementById('resumenTipo').textContent = servicioSeleccionado.nombre;
    document.getElementById('resumenFecha').textContent = fechaFormateada;
    document.getElementById('resumenHora').textContent = hora;

    if (observaciones) {
        document.getElementById('resumenObservaciones').textContent = observaciones;
        document.getElementById('resumenObservacionesDiv').classList.remove('hidden');
    } else {
        document.getElementById('resumenObservacionesDiv').classList.add('hidden');
    }
}

async function confirmarExamen() {
    const btnConfirmar = document.getElementById('btnConfirmar');
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<svg class="animate-spin inline mr-2" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="0.75"/></svg>Procesando...';

    try {
        const fechaExamen = document.getElementById('fechaExamen').value;
        
        // Crear el examen completo (crea automáticamente la reserva y programación)
        const responseExamen = await fetch('/reservas/api/examenes/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_servicio: servicioSeleccionado.id,
                fecha_examen: fechaExamen,
                hora_examen: document.getElementById('horaExamen').value,
                observacion: `${servicioSeleccionado.nombre}\n${document.getElementById('observaciones').value}`.trim(),
                estado: 'Pendiente'
            })
        });

        const dataExamen = await responseExamen.json();

        if (responseExamen.ok && dataExamen.success) {
            alert('¡Examen agendado exitosamente! Recibirás una confirmación pronto.');
            window.location.href = '/reservas/paciente/historial';
        } else {
            alert('Error al agendar el examen: ' + (dataExamen.error || 'Error desconocido'));
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="inline mr-2"><polyline points="20 6 9 17 4 12"/></svg>Confirmar Examen';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al agendar el examen: ' + error.message);
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="inline mr-2"><polyline points="20 6 9 17 4 12"/></svg>Confirmar Examen';
    }
}
