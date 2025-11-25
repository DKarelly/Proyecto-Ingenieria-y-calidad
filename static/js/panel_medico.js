// ========== VARIABLES GLOBALES DE PAGINACIÓN ==========
let paginaActualPacientes = 1;
let paginaActualDiagnosticos = 1;
const itemsPorPagina = 10;

// ========== EVENTOS INICIALES ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('Panel Médico cargado correctamente');

    // Búsqueda de pacientes
    const buscarInput = document.getElementById('buscar-paciente');
    if (buscarInput) {
        buscarInput.addEventListener('input', function(e) {
            const termino = e.target.value.toLowerCase();
            paginaActualPacientes = 1; // Resetear a primera página al buscar
            filtrarYPaginarPacientes(termino);
        });
        
        // Inicializar paginación de pacientes si hay filas
        const filasPacientes = document.querySelectorAll('.paciente-row');
        if (filasPacientes.length > 0) {
            filtrarYPaginarPacientes('');
        }
    }

    // Búsqueda de diagnósticos
    const buscarDiagnosticoInput = document.getElementById('buscar-diagnostico');
    if (buscarDiagnosticoInput) {
        buscarDiagnosticoInput.addEventListener('input', function(e) {
            const termino = e.target.value.toLowerCase();
            paginaActualDiagnosticos = 1; // Resetear a primera página al buscar
            filtrarYPaginarDiagnosticos(termino);
        });
        
        // Inicializar paginación de diagnósticos si hay filas
        const filasDiagnosticos = document.querySelectorAll('.diagnostico-row');
        if (filasDiagnosticos.length > 0) {
            filtrarYPaginarDiagnosticos('');
        }
    }

    // Formulario de diagnóstico
    const diagnosticoForm = document.getElementById('diagnostico-form');
    if (diagnosticoForm) {
        diagnosticoForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            
            // Agregar flags de autorización
            const autorizarExamen = document.getElementById('check_autorizar_examen')?.checked || false;
            const autorizarOperacion = document.getElementById('check_autorizar_operacion')?.checked || false;
            
            formData.append('autorizar_examen', autorizarExamen);
            formData.append('autorizar_operacion', autorizarOperacion);

            try {
                const response = await fetch('/medico/diagnosticos/guardar', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert(result.message);
                    window.location.reload();
                } else {
                    alert('Error: ' + result.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al guardar el diagnóstico');
            }
        });
    }

});

// ========== FUNCIONES PARA DIAGNÓSTICOS ==========
function abrirFormularioDiagnostico(idCita, nombrePaciente, dni, idPaciente, fechaCita, horaCita) {
    // RESTRICCIÓN ACTIVA: Solo permitir registrar diagnósticos dentro del día y horario permitido
    // Si la hora actual es antes de la hora de inicio o ya pasó la medianoche del día de la cita, se bloquea.
    if (!validarHorarioCita(fechaCita, horaCita)) {
        return;
    }
    
    const formDiagnostico = document.getElementById('form-diagnostico');
    const idCitaInput = document.getElementById('id_cita');
    const idPacienteInput = document.getElementById('id_paciente');
    const pacienteInfo = document.getElementById('form-paciente-info');
    const diagnosticoInput = document.getElementById('diagnostico');
    const observacionesInput = document.getElementById('observaciones');
    
    if (!formDiagnostico || !idCitaInput || !idPacienteInput) {
        console.error('Elementos del formulario de diagnóstico no encontrados');
        return;
    }
    
    formDiagnostico.classList.remove('hidden');
    idCitaInput.value = idCita;
    idPacienteInput.value = idPaciente || '';
    if (pacienteInfo) pacienteInfo.textContent = `Paciente: ${nombrePaciente} - DNI: ${dni}`;
    if (diagnosticoInput) diagnosticoInput.value = '';
    if (observacionesInput) observacionesInput.value = '';
    
    // Marcar como nuevo registro (no modificación)
    const esModificacionField = document.getElementById('es_modificacion');
    if (!esModificacionField) {
        const hiddenField = document.createElement('input');
        hiddenField.type = 'hidden';
        hiddenField.id = 'es_modificacion';
        hiddenField.name = 'es_modificacion';
        hiddenField.value = 'false';
        const diagnosticoForm = document.getElementById('diagnostico-form');
        if (diagnosticoForm) diagnosticoForm.appendChild(hiddenField);
    } else {
        esModificacionField.value = 'false';
    }
    
    // Cambiar título del formulario
    const titulo = document.querySelector('#form-diagnostico h3');
    if (titulo) titulo.textContent = 'Registrar Diagnóstico';
    
    // Resetear checkboxes de autorización
    const checkExamen = document.getElementById('check_autorizar_examen');
    const checkOperacion = document.getElementById('check_autorizar_operacion');
    const fieldsExamen = document.getElementById('fields_examen');
    const fieldsOperacion = document.getElementById('fields_operacion');
    const divDerivar = document.getElementById('div_derivar_operacion');
    const divMedico = document.getElementById('div_medico_operacion');
    
    if (checkExamen) checkExamen.checked = false;
    if (checkOperacion) checkOperacion.checked = false;
    if (fieldsExamen) fieldsExamen.classList.add('hidden');
    if (fieldsOperacion) fieldsOperacion.classList.add('hidden');
    if (divDerivar) divDerivar.classList.add('hidden');
    if (divMedico) divMedico.classList.add('hidden');
    
    // Scroll al formulario
    formDiagnostico.scrollIntoView({ behavior: 'smooth' });
}

function abrirFormularioModificacion(idCita, nombrePaciente, dni, idPaciente, fechaCita, horaCita) {
    // Para modificación, cargar los datos existentes del diagnóstico
    fetch(`/medico/api/obtener_diagnostico/${idCita}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('form-diagnostico').classList.remove('hidden');
                document.getElementById('id_cita').value = idCita;
                document.getElementById('id_paciente').value = idPaciente || '';
                document.getElementById('form-paciente-info').textContent = `Paciente: ${nombrePaciente} - DNI: ${dni} (Modificación)`;
                document.getElementById('diagnostico').value = data.diagnostico || '';
                document.getElementById('observaciones').value = data.observaciones || '';
                
                // Marcar como modificación
                if (!document.getElementById('es_modificacion')) {
                    const hiddenField = document.createElement('input');
                    hiddenField.type = 'hidden';
                    hiddenField.id = 'es_modificacion';
                    hiddenField.name = 'es_modificacion';
                    hiddenField.value = 'true';
                    document.getElementById('diagnostico-form').appendChild(hiddenField);
                } else {
                    document.getElementById('es_modificacion').value = 'true';
                }
                
                // Cambiar título del formulario
                document.querySelector('#form-diagnostico h3').textContent = 'Modificar Diagnóstico';
                
                // Nota: Las autorizaciones no se pueden modificar una vez creadas
                document.getElementById('check_autorizar_examen').checked = false;
                document.getElementById('check_autorizar_examen').disabled = true;
                document.getElementById('check_autorizar_operacion').checked = false;
                document.getElementById('check_autorizar_operacion').disabled = true;
                document.getElementById('fields_examen').classList.add('hidden');
                document.getElementById('fields_operacion').classList.add('hidden');
                
                // Scroll al formulario
                document.getElementById('form-diagnostico').scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error al cargar el diagnóstico: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar el diagnóstico para modificación');
        });
}

/**
 * FUNCIÓN DE VALIDACIÓN DE HORARIO PARA DIAGNÓSTICOS
 * ====================================================
 * 
 * RESTRICCIÓN TEMPORAL DESACTIVADA
 * 
 * Esta función implementa una restricción de tiempo para el registro de diagnósticos:
 * 
 * 1. RESTRICCIÓN ANTES DE LA CITA:
 *    - No permite registrar diagnósticos antes de que inicie la hora de la cita
 *    - Ejemplo: Si la cita es a las 14:00, no se puede registrar a las 13:55
 *    - Mensaje: "Esta cita aún no ha iniciado. Podrá registrar el diagnóstico a partir de las HH:MM"
 * 
 * 2. RESTRICCIÓN DESPUÉS DE MEDIANOCHE:
 *    - No permite registrar diagnósticos después de las 23:59:59 del día de la cita
 *    - Ejemplo: Si la cita fue el 21/11/2025, no se puede registrar el 22/11/2025
 *    - Mensaje: "El plazo para registrar el diagnóstico ha expirado. Solo se permite registrar el mismo día de la cita."
 * 
 * 3. VENTANA PERMITIDA:
 *    - El diagnóstico SOLO puede registrarse desde la hora de inicio de la cita hasta las 23:59:59 del mismo día
 *    - Ejemplo: Cita a las 10:00 del 21/11/2025 → Puede registrarse entre 10:00 y 23:59:59 del 21/11/2025
 * 
 * RAZÓN DE LA DESACTIVACIÓN:
 * - Actualmente comentada para permitir flexibilidad en el registro de diagnósticos
 * - Para reactivarla, descomentar las llamadas a esta función en:
 *   * abrirFormularioDiagnostico() (línea ~83)
 *   * abrirFormularioModificacion() (si se requiere)
 */
function validarHorarioCita(fechaCita, horaCita) {
    if (!fechaCita || !horaCita) {
        return true; // Si no hay datos, permitir (compatibilidad con citas antiguas)
    }
    
    try {
        // Parsear fecha y hora de la cita
        const [year, month, day] = fechaCita.split('-').map(Number);
        const [hours, minutes, seconds] = horaCita.toString().split(':').map(Number);
        
        const fechaHoraCita = new Date(year, month - 1, day, hours, minutes, seconds || 0);
        const ahora = new Date();
        
        // Validar que la cita ya haya iniciado
        if (ahora < fechaHoraCita) {
            const horaFormatted = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
            alert(`Esta cita aún no ha iniciado.\nPodrá registrar el diagnóstico a partir de las ${horaFormatted}`);
            return false;
        }
        
        // Validar que no haya pasado la medianoche del día de la cita
        const fechaLimite = new Date(year, month - 1, day, 23, 59, 59);
        if (ahora > fechaLimite) {
            alert('El plazo para registrar el diagnóstico ha expirado.\nSolo se permite registrar el mismo día de la cita.');
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Error al validar horario:', error);
        return true; // En caso de error, permitir (para no bloquear accidentalmente)
    }
}

function cerrarFormularioDiagnostico() {
    document.getElementById('form-diagnostico').classList.add('hidden');
    // Re-habilitar checkboxes de autorización por si estaban deshabilitados
    document.getElementById('check_autorizar_examen').disabled = false;
    document.getElementById('check_autorizar_operacion').disabled = false;
}

// ========== FUNCIONES PARA HISTORIAL DE PACIENTES ==========
async function verHistorialPaciente(idPaciente) {
    try {
        const response = await fetch(`/medico/historial_paciente/${idPaciente}`);
        const result = await response.json();
        
        if (result.success) {
            mostrarModalHistorial(result.paciente, result.historial);
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar el historial');
    }
}

function mostrarModalHistorial(paciente, historial) {
    const modal = document.getElementById('modal-historial');
    const nombreEl = document.getElementById('modal-paciente-nombre');
    const infoEl = document.getElementById('modal-paciente-info');
    const contenidoEl = document.getElementById('modal-historial-contenido');
    
    nombreEl.textContent = `Historial Médico - ${paciente.nombre}`;
    infoEl.textContent = `DNI: ${paciente.dni} | Edad: ${paciente.edad} años`;
    
    // Construir HTML del historial
    let html = '<div class="space-y-4">';
    
    if (historial.length === 0) {
        html += `
            <div class="text-center py-8 text-gray-500">
                <span class="material-symbols-outlined text-5xl mb-2 block text-gray-400">folder_off</span>
                <p>No hay historial disponible</p>
            </div>
        `;
    } else {
        historial.forEach(cita => {
            const estadoClass = cita.estado === 'Completada' ? 'bg-emerald-100 text-emerald-700' : 
                               cita.estado === 'Pendiente' ? 'bg-amber-100 text-amber-700' : 
                               cita.estado === 'Confirmada' ? 'bg-blue-100 text-blue-700' :
                               'bg-gray-100 text-gray-700';
            
            html += `
                <div class="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-gradient-to-r from-white to-gray-50">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-cyan-600 text-2xl">event</span>
                            <div>
                                <p class="font-semibold text-gray-800">${cita.fecha}</p>
                                <p class="text-sm text-gray-600 flex items-center gap-1">
                                    <span class="material-symbols-outlined text-xs">schedule</span>
                                    ${cita.hora}
                                </p>
                            </div>
                        </div>
                        <span class="px-3 py-1 ${estadoClass} rounded-full text-xs font-semibold shadow-sm">
                            ${cita.estado}
                        </span>
                    </div>
                    ${cita.diagnostico && cita.diagnostico.trim() !== '' ? `
                        <div class="mt-3 pt-3 border-t border-gray-200">
                            <p class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                <span class="material-symbols-outlined text-sm">clinical_notes</span>
                                Diagnóstico:
                            </p>
                            <p class="text-sm text-gray-600 pl-5">${cita.diagnostico}</p>
                        </div>
                    ` : ''}
                    ${cita.observaciones && cita.observaciones.trim() !== '' ? `
                        <div class="mt-2 ${cita.diagnostico && cita.diagnostico.trim() !== '' ? '' : 'pt-3 border-t border-gray-200'}">
                            <p class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                <span class="material-symbols-outlined text-sm">note</span>
                                Observaciones:
                            </p>
                            <p class="text-sm text-gray-600 pl-5">${cita.observaciones}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        });
    }
    
    html += '</div>';
    contenidoEl.innerHTML = html;
    
    modal.classList.remove('hidden');
}

function cerrarModalHistorial() {
    document.getElementById('modal-historial').classList.add('hidden');
}

// Cerrar modales al hacer clic fuera
document.addEventListener('click', function(e) {
    const modalHistorial = document.getElementById('modal-historial');
    if (modalHistorial && e.target === modalHistorial) {
        cerrarModalHistorial();
    }
    
    const modalDiagnostico = document.getElementById('form-diagnostico');
    if (modalDiagnostico && e.target === modalDiagnostico) {
        cerrarFormularioDiagnostico();
    }
});

// ========== FUNCIONES PARA NAVEGACIÓN DEL CALENDARIO ==========
function cambiarSemana(direccion) {
    // Obtener parámetros actuales de la URL
    const urlParams = new URLSearchParams(window.location.search);
    let offsetSemana = parseInt(urlParams.get('offset_semana')) || 0;
    
    // Calcular nuevo offset
    offsetSemana += direccion;
    
    // Construir nueva URL manteniendo el subsistema
    urlParams.set('subsistema', 'agenda');
    urlParams.set('offset_semana', offsetSemana);
    
    // Navegar a la nueva URL
    window.location.href = `/medico/panel?${urlParams.toString()}`;
}

function irHoy() {
    // Ir a la semana actual (offset = 0)
    window.location.href = '/medico/panel?subsistema=agenda&offset_semana=0';
}

// ========== FUNCIONES PARA MANEJO DE EVENTOS EN EL CALENDARIO ==========
function abrirFormularioEvento(dia, hora, minutos = 0) {
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    const horarioFormato = `${String(hora).padStart(2, '0')}:${String(minutos).padStart(2, '0')}`;
    console.log(`Crear evento para ${dias[dia]} a las ${horarioFormato}`);
    alert(`Función para crear evento:\nDía: ${dias[dia]}\nHora: ${horarioFormato}\n\nPróximamente disponible.`);
}

function nuevoEvento() {
    console.log('Crear nuevo evento');
    alert('Función para crear un nuevo evento.\nPróximamente disponible.');
}

function verDetalleEvento(eventId) {
    console.log(`Ver detalles del evento ${eventId}`);
    alert(`Ver detalles del evento ${eventId}.\nPróximamente disponible.`);
}

function verDetalleCita(citaId) {
    // Obtener información de la cita desde los datos del calendario
    const citaElements = document.querySelectorAll('.cita-event');
    let citaEncontrada = null;
    let celda = null;
    
    citaElements.forEach(el => {
        const onclick = el.getAttribute('onclick');
        if (onclick && onclick.includes(`verDetalleCita(${citaId})`)) {
            citaEncontrada = {
                paciente: el.querySelector('.text-xs.font-bold') ? el.querySelector('.text-xs.font-bold').textContent : 'Paciente',
                tipo: el.querySelectorAll('.text-xs')[1] ? el.querySelectorAll('.text-xs')[1].textContent : 'Consulta',
                horario: el.querySelector('.text-xs.font-medium') ? el.querySelector('.text-xs.font-medium').textContent : ''
            };
            celda = el.closest('td');
        }
    });

    if (citaEncontrada && celda) {
        // Obtener el índice de la columna y el encabezado correspondiente
        const columnIndex = Array.from(celda.parentElement.children).indexOf(celda);
        const table = celda.closest('table');
        let diaTexto = '';
        let fechaTexto = '';

        if (table) {
            const headerRow = table.querySelector('thead tr');
            if (headerRow && headerRow.children[columnIndex]) {
                const diaHeader = headerRow.children[columnIndex];
                // intentamos leer un div (nombre del día) y una etiqueta pequeña con la fecha
                diaTexto = diaHeader.querySelector('div')?.textContent.trim() || diaHeader.textContent.trim() || '';
                fechaTexto = diaHeader.querySelector('.text-xs')?.textContent.trim() || diaHeader.querySelector('time')?.textContent.trim() || '';
            }
        }

        // Mapear abreviaturas a nombres completos (es)
        function diaCompleto(nombre) {
            if (!nombre) return '';
            const m = {
                'Lun': 'Lunes', 'Mar': 'Martes', 'Mie': 'Miércoles', 'Mié': 'Miércoles', 'Mié': 'Miércoles',
                'Jue': 'Jueves', 'Vie': 'Viernes', 'Sab': 'Sábado', 'Dom': 'Domingo',
                'Lunes':'Lunes','Martes':'Martes','Miércoles':'Miércoles','Jueves':'Jueves','Viernes':'Viernes','Sábado':'Sábado','Domingo':'Domingo'
            };
            // tomar la primera palabra si incluye la fecha junto al nombre
            const key = nombre.split(' ')[0];
            return m[key] || nombre;
        }

        // Evitar duplicar la fecha si ya está incluida en el encabezado
        const dayToken = (diaTexto || '').split(/\s+/)[0];
        const diaNombre = diaCompleto(dayToken);
        const fechaFinal = fechaTexto ? `${diaNombre} ${fechaTexto}` : diaNombre || fechaTexto || '';

        // Llenar el modal con la información
        document.getElementById('modal-cita-titulo').textContent = citaEncontrada.paciente + ' - ' + citaEncontrada.tipo;
        document.getElementById('modal-cita-fecha').textContent = fechaFinal;
        document.getElementById('modal-cita-horario').textContent = citaEncontrada.horario;

        // Mostrar modal (fondo tenue y posición alta)
        const modal = document.getElementById('modal-detalle-cita');
        modal.classList.remove('hidden');
    } else {
        console.log(`Ver detalles de la cita ${citaId}`);
    }
}

function cerrarModalDetalleCita() {
    document.getElementById('modal-detalle-cita').classList.add('hidden');
}

// Cerrar modal al hacer clic fuera
document.addEventListener('click', function(e) {
    const modalCita = document.getElementById('modal-detalle-cita');
    if (modalCita && e.target === modalCita) {
        cerrarModalDetalleCita();
    }
});

// ========== FUNCIONES PARA NOTIFICACIONES ==========
function filtrarNotificaciones(tipo) {
    const notificaciones = document.querySelectorAll('.notificacion-item');
    const noNotificaciones = document.getElementById('no-notificaciones');
    const botones = document.querySelectorAll('.filtro-notificacion');
    let visibles = 0;

    // Actualizar botones activos
    botones.forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(tipo)) {
            btn.classList.add('active');
        }
    });

    // Filtrar notificaciones
    notificaciones.forEach(notif => {
        if (tipo === 'todas') {
            notif.style.display = '';
            visibles++;
        } else if (notif.dataset.tipo === tipo) {
            notif.style.display = '';
            visibles++;
        } else {
            notif.style.display = 'none';
        }
    });

    // Mostrar mensaje si no hay notificaciones
    if (visibles === 0) {
        noNotificaciones.classList.remove('hidden');
    } else {
        noNotificaciones.classList.add('hidden');
    }
}

function marcarLeida(button) {
    const notificacion = button.closest('.notificacion-item');
    notificacion.dataset.leida = 'true';
    notificacion.classList.add('opacity-60');
    
    // Ocultar indicador de nueva
    const indicador = notificacion.querySelector('.w-2.h-2');
    if (indicador) {
        indicador.style.display = 'none';
    }

    // Ocultar botón de marcar como leída
    button.style.display = 'none';

    // Actualizar contador (simulado)
    actualizarContadores();
}

function marcarTodasLeidas() {
    const notificaciones = document.querySelectorAll('.notificacion-item[data-leida="false"]');
    notificaciones.forEach(notif => {
        notif.dataset.leida = 'true';
        notif.classList.add('opacity-60');
        
        const indicador = notif.querySelector('.w-2.h-2');
        if (indicador) {
            indicador.style.display = 'none';
        }

        const boton = notif.querySelector('button[onclick*="marcarLeida"]');
        if (boton) {
            boton.style.display = 'none';
        }
    });

    actualizarContadores();
    alert('Todas las notificaciones han sido marcadas como leídas');
}

function actualizarContadores() {
    // Esta función actualizaría los contadores en tiempo real
    // Por ahora solo simula la actualización
    console.log('Contadores actualizados');
}

// ========== FUNCIONES PARA AUTORIZACIONES DE PROCEDIMIENTOS ==========

function toggleAutorizacionExamen() {
    const checkbox = document.getElementById('check_autorizar_examen');
    const fields = document.getElementById('fields_examen');
    
    if (checkbox.checked) {
        fields.classList.remove('hidden');
        cargarServiciosExamen();
    } else {
        fields.classList.add('hidden');
    }
}

function toggleAutorizacionOperacion() {
    const checkbox = document.getElementById('check_autorizar_operacion');
    const fields = document.getElementById('fields_operacion');
    
    if (checkbox.checked) {
        fields.classList.remove('hidden');
        cargarServiciosOperacion();
    } else {
        fields.classList.add('hidden');
        document.getElementById('div_derivar_operacion').classList.add('hidden');
    }
}

async function cargarServiciosExamen() {
    try {
        const response = await fetch('/medico/api/obtener_servicios_examen');
        const result = await response.json();
        
        if (result.success) {
            const select = document.getElementById('servicio_examen');
            
            // Limpiar opciones excepto la primera
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Agregar servicios
            result.servicios.forEach(servicio => {
                const option = document.createElement('option');
                option.value = servicio.id_servicio;
                option.textContent = servicio.nombre;
                if (servicio.nombre_especialidad) {
                    option.textContent += ` (${servicio.nombre_especialidad})`;
                }
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar servicios de examen:', error);
    }
}

async function cargarServiciosOperacion() {
    try {
        const response = await fetch('/medico/api/obtener_servicios_operacion');
        const result = await response.json();
        
        if (result.success) {
            const select = document.getElementById('servicio_operacion');
            
            // Limpiar opciones excepto la primera
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Agregar servicios
            result.servicios.forEach(servicio => {
                const option = document.createElement('option');
                option.value = servicio.id_servicio;
                option.textContent = servicio.nombre;
                if (servicio.nombre_especialidad) {
                    option.textContent += ` (${servicio.nombre_especialidad})`;
                }
                option.dataset.especialidad = servicio.id_especialidad || '';
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar servicios de operación:', error);
    }
}

function onServicioOperacionChange() {
    const select = document.getElementById('servicio_operacion');
    const divDerivar = document.getElementById('div_derivar_operacion');
    
    if (select.value) {
        divDerivar.classList.remove('hidden');
        cargarMedicosMiEspecialidad();
    } else {
        divDerivar.classList.add('hidden');
    }
}

async function cargarMedicosMiEspecialidad() {
    const selectMedico = document.getElementById('medico_derivar_operacion');
    
    try {
        const response = await fetch('/medico/api/obtener_medicos_mi_especialidad');
        const result = await response.json();
        
        if (result.success) {
            // Limpiar opciones excepto la primera
            while (selectMedico.options.length > 1) {
                selectMedico.remove(1);
            }
            
            // Agregar médicos de la misma especialidad
            if (result.medicos && result.medicos.length > 0) {
                result.medicos.forEach(medico => {
                    const option = document.createElement('option');
                    option.value = medico.id_empleado;
                    option.textContent = medico.nombre_completo;
                    selectMedico.appendChild(option);
                });
            } else {
                console.log('No hay otros médicos de esta especialidad disponibles');
            }
        } else {
            console.error('Error al cargar médicos:', result.message);
        }
    } catch (error) {
        console.error('Error al cargar médicos de mi especialidad:', error);
    }
}

// ========== FUNCIONES DE BÚSQUEDA Y PAGINACIÓN ==========

/**
 * Filtra y pagina la lista de pacientes
 */
function filtrarYPaginarPacientes(termino) {
    const filas = document.querySelectorAll('.paciente-row');
    let filasFiltradas = [];
    
    console.log(`Filtrando pacientes con término: "${termino}", Total filas: ${filas.length}`);
    
    // Filtrar filas
    filas.forEach(fila => {
        const nombre = fila.dataset.nombre.toLowerCase();
        const dni = fila.dataset.dni.toLowerCase();
        
        if (nombre.includes(termino) || dni.includes(termino)) {
            filasFiltradas.push(fila);
        } else {
            fila.style.display = 'none';
        }
    });
    
    // Calcular paginación
    const totalPaginas = Math.ceil(filasFiltradas.length / itemsPorPagina);
    const inicio = (paginaActualPacientes - 1) * itemsPorPagina;
    const fin = inicio + itemsPorPagina;
    
    console.log(`Pacientes filtrados: ${filasFiltradas.length}, Total páginas: ${totalPaginas}, Página actual: ${paginaActualPacientes}`);
    
    // Mostrar solo items de la página actual
    filasFiltradas.forEach((fila, index) => {
        if (index >= inicio && index < fin) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
    
    // Generar controles de paginación
    generarPaginacion('paginacion-pacientes', totalPaginas, paginaActualPacientes, cambiarPaginaPacientes);
}

/**
 * Filtra y pagina la lista de diagnósticos pendientes
 */
function filtrarYPaginarDiagnosticos(termino) {
    const filas = document.querySelectorAll('.diagnostico-row');
    let filasFiltradas = [];
    
    console.log(`Filtrando diagnósticos con término: "${termino}", Total filas: ${filas.length}`);
    
    // Filtrar filas
    filas.forEach(fila => {
        const paciente = fila.dataset.paciente.toLowerCase();
        const dni = fila.dataset.dni.toLowerCase();
        
        if (paciente.includes(termino) || dni.includes(termino)) {
            filasFiltradas.push(fila);
        } else {
            fila.style.display = 'none';
        }
    });
    
    // Calcular paginación
    const totalPaginas = Math.ceil(filasFiltradas.length / itemsPorPagina);
    const inicio = (paginaActualDiagnosticos - 1) * itemsPorPagina;
    const fin = inicio + itemsPorPagina;
    
    console.log(`Diagnósticos filtrados: ${filasFiltradas.length}, Total páginas: ${totalPaginas}, Página actual: ${paginaActualDiagnosticos}`);
    
    // Mostrar solo items de la página actual
    filasFiltradas.forEach((fila, index) => {
        if (index >= inicio && index < fin) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
    
    // Generar controles de paginación
    generarPaginacion('paginacion-diagnosticos', totalPaginas, paginaActualDiagnosticos, cambiarPaginaDiagnosticos);
}

/**
 * Genera los controles de paginación
 */
function generarPaginacion(contenedorId, totalPaginas, paginaActual, callbackCambiarPagina) {
    const contenedor = document.getElementById(contenedorId);
    if (!contenedor) return;
    
    // Si no hay páginas o solo una, ocultar paginación
    if (totalPaginas <= 1) {
        contenedor.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Botón anterior
    html += `
        <button onclick="${callbackCambiarPagina.name}(${paginaActual - 1})" 
                ${paginaActual === 1 ? 'disabled' : ''}
                class="px-3 py-2 rounded-lg border ${paginaActual === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-cyan-600 hover:bg-cyan-50 border-cyan-200'} transition-colors">
            <span class="material-symbols-outlined text-sm">chevron_left</span>
        </button>
    `;
    
    // Números de página
    const maxBotones = 5;
    let inicio = Math.max(1, paginaActual - Math.floor(maxBotones / 2));
    let fin = Math.min(totalPaginas, inicio + maxBotones - 1);
    
    if (fin - inicio < maxBotones - 1) {
        inicio = Math.max(1, fin - maxBotones + 1);
    }
    
    if (inicio > 1) {
        html += `
            <button onclick="${callbackCambiarPagina.name}(1)" 
                    class="px-4 py-2 rounded-lg border bg-white text-gray-700 hover:bg-cyan-50 border-gray-200 transition-colors">
                1
            </button>
        `;
        if (inicio > 2) {
            html += '<span class="px-2 text-gray-500">...</span>';
        }
    }
    
    for (let i = inicio; i <= fin; i++) {
        html += `
            <button onclick="${callbackCambiarPagina.name}(${i})" 
                    class="px-4 py-2 rounded-lg border ${i === paginaActual ? 'bg-cyan-600 text-white border-cyan-600' : 'bg-white text-gray-700 hover:bg-cyan-50 border-gray-200'} transition-colors font-semibold">
                ${i}
            </button>
        `;
    }
    
    if (fin < totalPaginas) {
        if (fin < totalPaginas - 1) {
            html += '<span class="px-2 text-gray-500">...</span>';
        }
        html += `
            <button onclick="${callbackCambiarPagina.name}(${totalPaginas})" 
                    class="px-4 py-2 rounded-lg border bg-white text-gray-700 hover:bg-cyan-50 border-gray-200 transition-colors">
                ${totalPaginas}
            </button>
        `;
    }
    
    // Botón siguiente
    html += `
        <button onclick="${callbackCambiarPagina.name}(${paginaActual + 1})" 
                ${paginaActual === totalPaginas ? 'disabled' : ''}
                class="px-3 py-2 rounded-lg border ${paginaActual === totalPaginas ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-cyan-600 hover:bg-cyan-50 border-cyan-200'} transition-colors">
            <span class="material-symbols-outlined text-sm">chevron_right</span>
        </button>
    `;
    
    contenedor.innerHTML = html;
}

/**
 * Cambia la página actual de pacientes
 */
function cambiarPaginaPacientes(nuevaPagina) {
    paginaActualPacientes = nuevaPagina;
    const termino = document.getElementById('buscar-paciente')?.value.toLowerCase() || '';
    filtrarYPaginarPacientes(termino);
}

/**
 * Cambia la página actual de diagnósticos
 */
function cambiarPaginaDiagnosticos(nuevaPagina) {
    paginaActualDiagnosticos = nuevaPagina;
    const termino = document.getElementById('buscar-diagnostico')?.value.toLowerCase() || '';
    filtrarYPaginarDiagnosticos(termino);
}

