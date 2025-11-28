// ========== VARIABLES GLOBALES DE PAGINACIÓN ==========
let paginaActualPacientes = 1;
let paginaActualDiagnosticos = 1;
const itemsPorPagina = 10;

// ========== CONTROL DE VALIDACIONES ==========
// Esta variable controla si las validaciones de tiempo están activas
// true = validaciones activadas (comportamiento normal)
// false = validaciones desactivadas (modo provisional para casos especiales)
let validacionesActivas = true;

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
            
            // Prevenir doble submit
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn.disabled) return;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="animate-spin inline-block mr-2">⏳</span> Guardando...';

            const formData = new FormData(this);
            
            // Agregar flags de autorización
            const autorizarExamen = document.getElementById('check_autorizar_examen')?.checked || false;
            const autorizarOperacion = document.getElementById('check_autorizar_operacion')?.checked || false;
            
            formData.append('autorizar_examen', autorizarExamen);
            formData.append('autorizar_operacion', autorizarOperacion);
            
            // Agregar múltiples exámenes si están seleccionados
            if (autorizarExamen) {
                const examenesSeleccionados = obtenerExamenesSeleccionados();
                formData.delete('id_servicio_examen'); // Eliminar el campo individual
                examenesSeleccionados.forEach((id, index) => {
                    formData.append(`examenes[${index}]`, id);
                });
                formData.append('cantidad_examenes', examenesSeleccionados.length);
            }
            
            // Agregar flag para omitir validación de tiempo si está desactivada
            if (!validacionesActivas) {
                formData.append('omitir_validacion_tiempo', 'true');
            }

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
                    // Rehabilitar botón en caso de error
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Guardar Diagnóstico';
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al guardar el diagnóstico');
                // Rehabilitar botón en caso de error
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Guardar Diagnóstico';
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
    // Si las validaciones están desactivadas, permitir siempre
    if (!validacionesActivas) {
        console.log('⚠️ Validaciones de tiempo DESACTIVADAS - Permitiendo registro sin restricción');
        return true;
    }
    
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

// ========== FUNCIONES PARA CONTROL DE VALIDACIONES ==========
/**
 * Alterna el estado de las validaciones de tiempo para diagnósticos
 * Cuando está desactivado, permite registrar diagnósticos sin restricción de horario
 */
function toggleValidaciones() {
    validacionesActivas = !validacionesActivas;
    actualizarBotonValidaciones();
    
    const estado = validacionesActivas ? 'ACTIVADAS' : 'DESACTIVADAS';
    const mensaje = validacionesActivas 
        ? '✅ Validaciones de tiempo ACTIVADAS\n\nSolo podrá registrar diagnósticos durante el horario de la cita y hasta la medianoche del mismo día.'
        : '⚠️ Validaciones de tiempo DESACTIVADAS\n\nAhora puede registrar diagnósticos sin restricción de horario.\n\nNota: Este modo es provisional para casos especiales.';
    
    alert(mensaje);
    console.log(`Validaciones de tiempo: ${estado}`);
}

/**
 * Actualiza la apariencia visual del botón de validaciones según el estado
 */
function actualizarBotonValidaciones() {
    const boton = document.getElementById('btn-toggle-validaciones');
    const icono = document.getElementById('icono-validaciones');
    const texto = document.getElementById('texto-validaciones');
    
    if (!boton || !icono || !texto) return;
    
    if (validacionesActivas) {
        // Estado: Validaciones activas (botón para desactivar)
        boton.className = 'flex items-center gap-2 px-3 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors text-sm font-medium shadow-sm';
        icono.textContent = 'verified';
        texto.textContent = 'Validaciones: ON';
        boton.title = 'Validaciones de tiempo activas - Click para desactivar';
    } else {
        // Estado: Validaciones inactivas (botón para activar)
        boton.className = 'flex items-center gap-2 px-3 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-colors text-sm font-medium shadow-sm animate-pulse';
        icono.textContent = 'warning';
        texto.textContent = 'Validaciones: OFF';
        boton.title = 'Validaciones de tiempo desactivadas - Click para activar';
    }
}

// ========== FUNCIONES PARA AUTO-COMPLETAR CITAS ==========
/**
 * Auto-completa las citas de días anteriores que no recibieron diagnóstico.
 * Las marca como "Completada" con observación indicando que no se registró diagnóstico.
 * NO crea autorizaciones ni procedimientos.
 */
async function autoCompletarCitasPasadas() {
    const confirmar = confirm(
        '⚠️ Auto-completar Citas Sin Diagnóstico\n\n' +
        'Esta acción marcará como "Completadas" todas las citas de días anteriores que no tienen diagnóstico registrado.\n\n' +
        'Las citas se marcarán con:\n' +
        '• Diagnóstico: "[No registrado]"\n' +
        '• Observación: "Diagnóstico no registrado por el médico"\n\n' +
        '⚠️ IMPORTANTE: No se crearán autorizaciones de exámenes ni operaciones.\n\n' +
        '¿Desea continuar?'
    );
    
    if (!confirmar) return;
    
    try {
        const response = await fetch('/medico/api/auto_completar_citas_sin_diagnostico', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})  // Sin fecha = usa el día anterior
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.citas_actualizadas > 0) {
                let mensaje = `✅ ${result.message}\n\nCitas actualizadas:\n`;
                result.detalle.forEach(cita => {
                    mensaje += `• ${cita.paciente} (${cita.fecha})\n`;
                });
                alert(mensaje);
                
                // Recargar la página para actualizar la lista
                window.location.reload();
            } else {
                alert(`✅ ${result.message}`);
            }
        } else {
            alert(`❌ Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al auto-completar citas: ' + error.message);
    }
}

// ========== FUNCIONES PARA HISTORIAL DE PACIENTES ==========
async function verHistorialPaciente(idPaciente) {
    try {
        const response = await fetch(`/medico/historial_paciente/${idPaciente}`);
        const result = await response.json();
        
        if (result.success) {
            mostrarModalHistorial(result.paciente, result.historial, result.examenes || [], result.operaciones || []);
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar el historial');
    }
}

function mostrarModalHistorial(paciente, historial, examenes, operaciones) {
    const modal = document.getElementById('modal-historial');
    const nombreEl = document.getElementById('modal-paciente-nombre');
    const infoEl = document.getElementById('modal-paciente-info');
    const contenidoEl = document.getElementById('modal-historial-contenido');
    
    nombreEl.textContent = `Historial Médico - ${paciente.nombre}`;
    infoEl.textContent = `DNI: ${paciente.dni} | Edad: ${paciente.edad} años`;
    
    // Construir HTML del historial con tabs
    let html = `
        <div class="mb-4">
            <div class="flex border-b border-gray-200">
                <button type="button" onclick="cambiarTabHistorial('citas')" id="tab-citas" 
                        class="tab-historial px-4 py-2 text-sm font-semibold border-b-2 border-cyan-500 text-cyan-600">
                    <span class="material-symbols-outlined text-sm align-middle mr-1">event</span>
                    Citas (${historial.length})
                </button>
                <button type="button" onclick="cambiarTabHistorial('examenes')" id="tab-examenes"
                        class="tab-historial px-4 py-2 text-sm font-semibold border-b-2 border-transparent text-gray-500 hover:text-gray-700">
                    <span class="material-symbols-outlined text-sm align-middle mr-1">biotech</span>
                    Exámenes (${examenes.length})
                </button>
                <button type="button" onclick="cambiarTabHistorial('operaciones')" id="tab-operaciones"
                        class="tab-historial px-4 py-2 text-sm font-semibold border-b-2 border-transparent text-gray-500 hover:text-gray-700">
                    <span class="material-symbols-outlined text-sm align-middle mr-1">surgical</span>
                    Operaciones (${operaciones.length})
                </button>
            </div>
        </div>
    `;
    
    // Contenido de Citas
    html += '<div id="content-citas" class="tab-content-historial space-y-4">';
    if (historial.length === 0) {
        html += `
            <div class="text-center py-8 text-gray-500">
                <span class="material-symbols-outlined text-5xl mb-2 block text-gray-400">event_busy</span>
                <p>No hay citas registradas</p>
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
    
    html += '</div>'; // Cierra content-citas
    
    // Contenido de Exámenes
    html += '<div id="content-examenes" class="tab-content-historial space-y-4 hidden">';
    if (examenes.length === 0) {
        html += `
            <div class="text-center py-8 text-gray-500">
                <span class="material-symbols-outlined text-5xl mb-2 block text-gray-400">biotech</span>
                <p>No hay exámenes registrados</p>
            </div>
        `;
    } else {
        examenes.forEach(examen => {
            const estadoClass = examen.estado === 'Completada' ? 'bg-emerald-100 text-emerald-700' : 
                               examen.estado === 'Pendiente' ? 'bg-amber-100 text-amber-700' : 
                               'bg-gray-100 text-gray-700';
            const estadoIcon = examen.estado === 'Completada' ? 'check_circle' : 
                              examen.estado === 'Pendiente' ? 'pending' : 'event';
            
            html += `
                <div class="border border-violet-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-gradient-to-r from-violet-50 to-purple-50">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-violet-600 text-2xl">biotech</span>
                            <div>
                                <p class="font-semibold text-gray-800">${examen.servicio}</p>
                                <p class="text-sm text-gray-600 flex items-center gap-1">
                                    <span class="material-symbols-outlined text-xs">calendar_today</span>
                                    ${examen.fecha}
                                    ${examen.hora ? ` - <span class="material-symbols-outlined text-xs">schedule</span> ${examen.hora}` : ''}
                                </p>
                            </div>
                        </div>
                        <span class="px-3 py-1 ${estadoClass} rounded-full text-xs font-semibold shadow-sm flex items-center gap-1">
                            <span class="material-symbols-outlined text-xs">${estadoIcon}</span>
                            ${examen.estado}
                        </span>
                    </div>
                    ${examen.observacion && examen.observacion.trim() !== '' ? `
                        <div class="mt-3 pt-3 border-t border-violet-200">
                            <p class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                <span class="material-symbols-outlined text-sm">note</span>
                                Observaciones:
                            </p>
                            <p class="text-sm text-gray-600 pl-5">${examen.observacion}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        });
    }
    html += '</div>'; // Cierra content-examenes
    
    // Contenido de Operaciones
    html += '<div id="content-operaciones" class="tab-content-historial space-y-4 hidden">';
    if (operaciones.length === 0) {
        html += `
            <div class="text-center py-8 text-gray-500">
                <span class="material-symbols-outlined text-5xl mb-2 block text-gray-400">surgical</span>
                <p>No hay operaciones registradas</p>
            </div>
        `;
    } else {
        operaciones.forEach(operacion => {
            const estadoClass = operacion.estado === 'Completada' ? 'bg-emerald-100 text-emerald-700' : 
                               operacion.estado === 'Pendiente' ? 'bg-amber-100 text-amber-700' : 
                               operacion.estado === 'Cancelada' ? 'bg-gray-100 text-gray-700' :
                               'bg-gray-100 text-gray-700';
            const estadoIcon = operacion.estado === 'Completada' ? 'check_circle' : 
                              operacion.estado === 'Pendiente' ? 'pending' : 
                              operacion.estado === 'Cancelada' ? 'event_busy' : 'event';
            
            html += `
                <div class="border border-orange-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-gradient-to-r from-orange-50 to-red-50">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-orange-600 text-2xl">surgical</span>
                            <div>
                                <p class="font-semibold text-gray-800">${operacion.servicio}</p>
                                <p class="text-sm text-gray-600 flex items-center gap-1">
                                    <span class="material-symbols-outlined text-xs">calendar_today</span>
                                    ${operacion.fecha}
                                    ${operacion.hora ? ` - <span class="material-symbols-outlined text-xs">schedule</span> ${operacion.hora}` : ''}
                                </p>
                            </div>
                        </div>
                        <span class="px-3 py-1 ${estadoClass} rounded-full text-xs font-semibold shadow-sm flex items-center gap-1">
                            <span class="material-symbols-outlined text-xs">${estadoIcon}</span>
                            ${operacion.estado}
                        </span>
                    </div>
                    ${operacion.medico ? `
                        <div class="mt-2 text-sm">
                            <p class="text-gray-500">Médico asignado:</p>
                            <p class="font-medium text-gray-700">${operacion.medico}</p>
                        </div>
                    ` : ''}
                    ${operacion.observaciones && operacion.observaciones.trim() !== '' ? `
                        <div class="mt-3 pt-3 border-t border-orange-200">
                            <p class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                <span class="material-symbols-outlined text-sm">note</span>
                                Observaciones:
                            </p>
                            <p class="text-sm text-gray-600 pl-5 whitespace-pre-wrap">${operacion.observaciones}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        });
    }
    html += '</div>'; // Cierra content-operaciones
    
    contenidoEl.innerHTML = html;
    
    modal.classList.remove('hidden');
}

// Función para cambiar tabs en el modal historial
function cambiarTabHistorial(tab) {
    // Ocultar todos los contenidos
    document.querySelectorAll('.tab-content-historial').forEach(el => el.classList.add('hidden'));
    
    // Desactivar todos los tabs
    document.querySelectorAll('.tab-historial').forEach(el => {
        el.classList.remove('border-cyan-500', 'text-cyan-600');
        el.classList.add('border-transparent', 'text-gray-500');
    });
    
    // Mostrar contenido seleccionado
    document.getElementById(`content-${tab}`).classList.remove('hidden');
    
    // Activar tab seleccionado
    const tabBtn = document.getElementById(`tab-${tab}`);
    tabBtn.classList.add('border-cyan-500', 'text-cyan-600');
    tabBtn.classList.remove('border-transparent', 'text-gray-500');
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

// Variables para control de exámenes múltiples
let examenesAgregados = [];
const MAX_EXAMENES = 3;

function toggleAutorizacionExamen() {
    const checkbox = document.getElementById('check_autorizar_examen');
    const fields = document.getElementById('fields_examen');
    
    if (checkbox.checked) {
        fields.classList.remove('hidden');
        cargarServiciosExamen();
        examenesAgregados = []; // Reset al abrir
        actualizarListaExamenes();
    } else {
        fields.classList.add('hidden');
        examenesAgregados = [];
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

/**
 * Agrega un examen a la lista (máximo 3)
 */
function agregarExamen() {
    const select = document.getElementById('servicio_examen');
    const idServicio = select.value;
    const nombreServicio = select.options[select.selectedIndex]?.text;
    
    if (!idServicio) {
        alert('Seleccione un examen primero');
        return;
    }
    
    if (examenesAgregados.length >= MAX_EXAMENES) {
        alert(`Solo puede agregar hasta ${MAX_EXAMENES} exámenes por diagnóstico`);
        return;
    }
    
    // Verificar que no esté duplicado
    if (examenesAgregados.some(e => e.id === idServicio)) {
        alert('Este examen ya fue agregado');
        return;
    }
    
    examenesAgregados.push({
        id: idServicio,
        nombre: nombreServicio
    });
    
    actualizarListaExamenes();
    select.value = ''; // Reset select
}

/**
 * Elimina un examen de la lista
 */
function eliminarExamen(idServicio) {
    examenesAgregados = examenesAgregados.filter(e => e.id !== idServicio);
    actualizarListaExamenes();
}

/**
 * Actualiza la visualización de la lista de exámenes
 */
function actualizarListaExamenes() {
    const container = document.getElementById('lista_examenes_agregados');
    const contador = document.getElementById('contador_examenes');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    if (examenesAgregados.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm italic">No hay exámenes agregados</p>';
    } else {
        examenesAgregados.forEach(examen => {
            const div = document.createElement('div');
            div.className = 'flex items-center justify-between bg-white p-2 rounded-lg border border-blue-200';
            div.innerHTML = `
                <span class="text-sm text-gray-700">${examen.nombre}</span>
                <button type="button" onclick="eliminarExamen('${examen.id}')" 
                        class="text-red-500 hover:text-red-700 p-1" title="Eliminar">
                    <span class="material-symbols-outlined text-sm">close</span>
                </button>
            `;
            container.appendChild(div);
        });
    }
    
    if (contador) {
        contador.textContent = `${examenesAgregados.length}/${MAX_EXAMENES}`;
        contador.className = examenesAgregados.length >= MAX_EXAMENES 
            ? 'text-red-600 font-bold' 
            : 'text-gray-600';
    }
}

/**
 * Obtiene los IDs de los exámenes seleccionados
 */
function obtenerExamenesSeleccionados() {
    return examenesAgregados.map(e => e.id);
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


// ========== NUEVO SISTEMA DE AGENDA DINÁMICA ==========

/**
 * Variables globales para la agenda dinámica
 */
let agendaOffsetSemana = 0;
let agendaEventos = [];
let agendaRangoDisponible = { fecha_min: null, fecha_max: null };
let agendaCacheEventos = {}; // Cache de eventos por semana

/**
 * Nombres de días y meses en español
 */
const DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
const DIAS_COMPLETOS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

/**
 * Inicializa la agenda dinámica al cargar la página
 */
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en la vista de agenda
    if (document.getElementById('agenda-container')) {
        cargarAgendaSemanal(0);
    }
});

/**
 * Carga los eventos de la agenda para una semana específica
 */
async function cargarAgendaSemanal(offset) {
    const loading = document.getElementById('agenda-loading');
    const calendario = document.getElementById('agenda-calendario');
    const vacio = document.getElementById('agenda-vacio');
    
    // Verificar si ya tenemos en cache
    if (agendaCacheEventos[offset]) {
        // IMPORTANTE: Actualizar el offset actual ANTES de renderizar
        agendaOffsetSemana = offset;
        renderizarAgenda(agendaCacheEventos[offset]);
        return;
    }
    
    // Mostrar loading
    if (loading) loading.classList.remove('hidden');
    if (calendario) calendario.classList.add('hidden');
    if (vacio) vacio.classList.add('hidden');
    
    try {
        const response = await fetch(`/medico/api/agenda-semanal?offset=${offset}`);
        const data = await response.json();
        
        if (data.success) {
            agendaOffsetSemana = offset;
            agendaEventos = data.eventos;
            agendaRangoDisponible = data.rango_disponible;
            
            // Guardar en cache
            agendaCacheEventos[offset] = data;
            
            renderizarAgenda(data);
        } else {
            console.error('Error al cargar agenda:', data.message);
            mostrarErrorAgenda('Error al cargar la agenda');
        }
    } catch (error) {
        console.error('Error de conexión:', error);
        mostrarErrorAgenda('Error de conexión con el servidor');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

/**
 * Renderiza el calendario con los eventos
 */
function renderizarAgenda(data) {
    const calendario = document.getElementById('agenda-calendario');
    const vacio = document.getElementById('agenda-vacio');
    const tituloSemana = document.getElementById('titulo-semana');
    const btnHoy = document.getElementById('btn-hoy');
    
    // Actualizar título de semana
    const inicio = new Date(data.semana.inicio + 'T00:00:00');
    const fin = new Date(data.semana.fin + 'T00:00:00');
    tituloSemana.textContent = `Semana del ${inicio.getDate()} al ${fin.getDate()} ${MESES[fin.getMonth()]} ${fin.getFullYear()}`;
    
    // Mostrar/ocultar botón "Hoy"
    if (btnHoy) {
        btnHoy.style.display = data.semana.offset !== 0 ? 'flex' : 'none';
    }
    
    // Si no hay eventos, mostrar mensaje vacío
    if (!data.eventos || data.eventos.length === 0) {
        if (vacio) vacio.classList.remove('hidden');
        if (calendario) calendario.classList.add('hidden');
        actualizarListaEventosDia([]);
        return;
    }
    
    // Generar calendario
    if (calendario) {
        calendario.classList.remove('hidden');
        generarCalendarioSemanal(data.eventos, data.semana);
    }
    
    // Actualizar lista de eventos del día actual
    const hoy = new Date();
    const hoyStr = hoy.toISOString().split('T')[0];
    const eventosHoy = data.eventos.filter(e => e.fecha === hoyStr);
    actualizarListaEventosDia(eventosHoy);
}

/**
 * Genera la estructura del calendario semanal estilo cuadrícula HORIZONTAL
 */
function generarCalendarioSemanal(eventos, semana) {
    const diasContainer = document.getElementById('agenda-dias');
    const bodyContainer = document.getElementById('agenda-body');
    
    const fechaInicio = new Date(semana.inicio + 'T00:00:00');
    
    // Usar zona horaria de Perú (UTC-5)
    const hoyPeru = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/Lima' }));
    const hoyStr = hoyPeru.getFullYear() + '-' + 
                   String(hoyPeru.getMonth() + 1).padStart(2, '0') + '-' + 
                   String(hoyPeru.getDate()).padStart(2, '0');
    
    const DIAS_HEADER = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO'];
    
    // Generar array de fechas de la semana
    const fechasSemana = [];
    for (let i = 0; i < 7; i++) {
        const fecha = new Date(fechaInicio);
        fecha.setDate(fecha.getDate() + i);
        const fechaStr = fecha.getFullYear() + '-' + 
                        String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                        String(fecha.getDate()).padStart(2, '0');
        fechasSemana.push({
            fecha: fecha,
            fechaStr: fechaStr,
            esHoy: fechaStr === hoyStr,
            nombreDia: DIAS_HEADER[i],
            diaNum: fecha.getDate()
        });
    }
    
    // Determinar rango de horas
    let horaMin = 7, horaMax = 18;
    if (eventos.length > 0) {
        eventos.forEach(e => {
            const h = parseInt(e.hora_inicio.split(':')[0]);
            const hFin = parseInt(e.hora_fin.split(':')[0]);
            if (h < horaMin) horaMin = Math.max(6, h);
            if (hFin > horaMax) horaMax = Math.min(22, hFin + 1);
        });
    }
    
    // ===== GENERAR TABLA HTML CON CUADRÍCULA =====
    let tableHTML = `
        <table class="w-full" style="table-layout: fixed; border-collapse: collapse;">
            <thead>
                <tr>
                    <th style="width: 80px; border: 1px solid #e2e8f0; background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 12px 8px;">
                        <span class="material-symbols-outlined text-gray-400" style="font-size: 20px;">schedule</span>
                    </th>
    `;
    
    // Encabezados de días mejorados con bordes
    fechasSemana.forEach((d) => {
        const bgStyle = d.esHoy 
            ? 'background: linear-gradient(135deg, #06b6d4, #0891b2);' 
            : 'background: linear-gradient(135deg, #f8fafc, #f1f5f9);';
        const textColor = d.esHoy ? 'color: white;' : 'color: #334155;';
        tableHTML += `
            <th style="border: 1px solid #e2e8f0; padding: 12px 8px; ${bgStyle}">
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <span style="font-size: 11px; font-weight: 700; letter-spacing: 0.5px; ${textColor}">${d.nombreDia}</span>
                    <span style="font-size: 18px; font-weight: 700; margin-top: 4px; ${textColor}">${d.diaNum}</span>
                </div>
            </th>
        `;
    });
    
    tableHTML += `</tr></thead><tbody>`;
    
    // Filas de horas con cuadrícula
    for (let hora = horaMin; hora <= horaMax; hora++) {
        tableHTML += `<tr>`;
        
        // Celda de hora con borde
        tableHTML += `
            <td style="width: 80px; border: 1px solid #e2e8f0; background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 12px 8px; text-align: center; vertical-align: middle;">
                <span style="font-size: 13px; font-weight: 600; color: #64748b;">${String(hora).padStart(2, '0')}:00</span>
            </td>
        `;
        
        // Celdas de cada día con bordes
        fechasSemana.forEach(d => {
            const bgColor = d.esHoy ? '#ecfeff' : '#ffffff';
            
            const eventosEnCelda = eventos.filter(e => {
                const horaEvento = parseInt(e.hora_inicio.split(':')[0]);
                return e.fecha === d.fechaStr && horaEvento === hora;
            });
            
            tableHTML += `<td style="border: 1px solid #e2e8f0; background-color: ${bgColor}; padding: 4px; vertical-align: top; min-height: 60px;" data-fecha="${d.fechaStr}" data-hora="${hora}">`;
            
            if (eventosEnCelda.length > 0) {
                eventosEnCelda.forEach(evento => {
                    const estilos = obtenerEstilosEvento(evento);
                    const horaCorta = evento.hora_inicio.substring(0, 5);
                    
                    tableHTML += `
                        <div style="
                            background: ${estilos.bg};
                            border-left: 4px solid ${estilos.borderColor};
                            color: ${estilos.color};
                            border-radius: 8px;
                            padding: 8px 10px;
                            margin: 3px;
                            cursor: pointer;
                            transition: all 0.2s ease;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                        " 
                        class="evento-agenda hover:shadow-lg hover:scale-105"
                        onclick="verDetalleEvento('${evento.tipo}', ${evento.id})"
                        title="${evento.titulo} - ${evento.hora_inicio} a ${evento.hora_fin}">
                            <div style="display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 800; margin-bottom: 2px;">
                                <span class="material-symbols-outlined" style="font-size: 14px;">${estilos.icon}</span>
                                ${horaCorta}
                            </div>
                            <div style="font-size: 11px; font-weight: 600; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                ${evento.titulo}
                            </div>
                        </div>
                    `;
                });
            }
            
            tableHTML += `</td>`;
        });
        
        tableHTML += `</tr>`;
    }
    
    tableHTML += `</tbody></table>`;
    
    // Limpiar contenedores y poner la tabla
    diasContainer.innerHTML = '';
    bodyContainer.innerHTML = tableHTML;
}

/**
 * Obtiene los estilos inline para un evento según su tipo y estado
 */
function obtenerEstilosEvento(evento) {
    let styles = {
        bg: '',
        color: '',
        borderColor: '',
        icon: 'calendar_today'
    };
    
    if (evento.estado === 'Cancelada') {
        styles.bg = '#f3f4f6';
        styles.color = '#6b7280';
        styles.borderColor = '#9ca3af';
        styles.icon = 'event_busy';
    } else {
        switch(evento.tipo) {
            case 'cita':
                if (evento.estado === 'Completada' || evento.estado === 'Confirmada') {
                    styles.bg = 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)';
                    styles.color = '#065f46';
                    styles.borderColor = '#10b981';
                    styles.icon = 'check_circle';
                } else {
                    styles.bg = 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)';
                    styles.color = '#92400e';
                    styles.borderColor = '#f59e0b';
                    styles.icon = 'event';
                }
                break;
            case 'examen':
                styles.bg = 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)';
                styles.color = '#3730a3';
                styles.borderColor = '#6366f1';
                styles.icon = 'biotech';
                break;
            case 'operacion':
                styles.bg = 'linear-gradient(135deg, #ffe4e6 0%, #fecdd3 100%)';
                styles.color = '#9f1239';
                styles.borderColor = '#f43f5e';
                styles.icon = 'surgical';
                break;
            default:
                styles.bg = 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)';
                styles.color = '#92400e';
                styles.borderColor = '#f59e0b';
                styles.icon = 'event';
        }
    }
    
    return styles;
}

/**
 * Obtiene los colores para un evento según su tipo y estado
 */
function obtenerColorEvento(evento) {
    if (evento.estado === 'Cancelada') {
        return {
            bg: 'bg-red-100',
            text: 'text-red-700',
            textSecondary: 'text-red-600'
        };
    }
    
    switch(evento.tipo) {
        case 'cita':
            if (evento.estado === 'Completada' || evento.estado === 'Confirmada') {
                return {
                    bg: 'bg-emerald-100',
                    text: 'text-emerald-700',
                    textSecondary: 'text-emerald-600'
                };
            } else {
                return {
                    bg: 'bg-amber-100',
                    text: 'text-amber-700',
                    textSecondary: 'text-amber-600'
                };
            }
        case 'examen':
            return {
                bg: 'bg-violet-100',
                text: 'text-violet-700',
                textSecondary: 'text-violet-600'
            };
        case 'operacion':
            return {
                bg: 'bg-rose-100',
                text: 'text-rose-700',
                textSecondary: 'text-rose-600'
            };
        default:
            return {
                bg: 'bg-gray-100',
                text: 'text-gray-700',
                textSecondary: 'text-gray-600'
            };
    }
}

/**
 * Calcula la duración en minutos entre dos horas
 */
function calcularDuracionMinutos(inicio, fin) {
    const [h1, m1] = inicio.split(':').map(Number);
    const [h2, m2] = fin.split(':').map(Number);
    return (h2 * 60 + m2) - (h1 * 60 + m1);
}

/**
 * Actualiza la lista de eventos del día
 */
function actualizarListaEventosDia(eventos) {
    const container = document.getElementById('lista-eventos-dia');
    const titulo = document.getElementById('titulo-eventos-dia');
    const contador = document.getElementById('contador-eventos-dia');
    
    if (!container) return;
    
    const hoy = new Date();
    const opciones = { weekday: 'long', day: 'numeric', month: 'long' };
    
    if (titulo) {
        titulo.innerHTML = `
            <span class="material-symbols-outlined text-cyan-600">event_note</span>
            Eventos de Hoy - ${hoy.toLocaleDateString('es-ES', opciones)}
        `;
    }
    
    if (contador) {
        contador.textContent = `${eventos.length} evento(s)`;
    }
    
    if (eventos.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <div class="w-16 h-16 mx-auto bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mb-4">
                    <span class="material-symbols-outlined text-4xl text-gray-400">event_busy</span>
                </div>
                <p class="font-semibold">No hay eventos programados para hoy</p>
                <p class="text-sm mt-2 text-gray-400">Tu agenda está libre</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    eventos.sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
    
    eventos.forEach(evento => {
        // Determinar colores según tipo y estado
        let borderColor, bgColor, iconColor;
        switch(evento.tipo) {
            case 'cita':
                borderColor = evento.estado === 'Completada' ? 'border-emerald-200' : 
                              evento.estado === 'Confirmada' ? 'border-blue-200' : 
                              evento.estado === 'Cancelada' ? 'border-red-200' : 'border-amber-200';
                bgColor = evento.estado === 'Completada' ? 'bg-emerald-50' : 
                          evento.estado === 'Confirmada' ? 'bg-blue-50' : 
                          evento.estado === 'Cancelada' ? 'bg-red-50' : 'bg-amber-50';
                iconColor = 'from-cyan-500 to-teal-500';
                break;
            case 'examen':
                borderColor = evento.estado === 'Completada' ? 'border-blue-200' : 'border-blue-300';
                bgColor = evento.estado === 'Completada' ? 'bg-blue-50/50' : 'bg-blue-50';
                iconColor = 'from-blue-500 to-cyan-500';
                break;
            case 'operacion':
                borderColor = evento.estado === 'Completada' ? 'border-orange-200' : 'border-orange-300';
                bgColor = evento.estado === 'Completada' ? 'bg-orange-50/50' : 'bg-orange-50';
                iconColor = 'from-orange-500 to-red-500';
                break;
            default:
                borderColor = 'border-gray-200';
                bgColor = 'bg-gray-50';
                iconColor = 'from-gray-500 to-gray-600';
        }
        
        // Badge de tipo
        const tipoBadge = evento.tipo === 'cita' ? '' : `
            <span class="text-[10px] px-2 py-0.5 rounded-full ${evento.tipo === 'examen' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'} font-semibold">
                ${evento.tipo === 'examen' ? 'EXAMEN' : 'OPERACIÓN'}
            </span>
        `;
        
        // Badge de estado
        let estadoBadge = '';
        switch(evento.estado) {
            case 'Pendiente':
                estadoBadge = `<span class="inline-flex items-center gap-1.5 px-2 py-1 bg-amber-100 text-amber-700 text-xs font-bold rounded-lg">
                    <span class="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></span>Pendiente
                </span>`;
                break;
            case 'Confirmada':
            case 'Confirmado':
                estadoBadge = `<span class="inline-flex items-center gap-1.5 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-lg">
                    <span class="material-symbols-outlined text-xs">check_circle</span>Confirmada
                </span>`;
                break;
            case 'Completada':
            case 'Completado':
                estadoBadge = `<span class="inline-flex items-center gap-1.5 px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-lg">
                    <span class="material-symbols-outlined text-xs">task_alt</span>Completada
                </span>`;
                break;
            case 'Cancelada':
                estadoBadge = `<span class="inline-flex items-center gap-1.5 px-2 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-lg">
                    <span class="material-symbols-outlined text-xs">cancel</span>Cancelada
                </span>`;
                break;
        }
        
        // Obtener iniciales del paciente
        const partes = evento.titulo.split(' ');
        const iniciales = partes.length >= 2 ? partes[0][0] + partes[1][0] : partes[0].slice(0, 2);
        
        html += `
            <div class="flex items-center gap-4 p-4 rounded-xl border-2 ${borderColor} ${bgColor} hover:shadow-md transition-all cursor-pointer"
                 onclick="verDetalleEvento('${evento.tipo}', ${evento.id})">
                <div class="flex-shrink-0">
                    <div class="w-12 h-12 md:w-14 md:h-14 bg-gradient-to-br ${iconColor} rounded-xl flex items-center justify-center text-white font-bold text-sm md:text-lg shadow-md">
                        ${iniciales.toUpperCase()}
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <h4 class="font-bold text-gray-800 text-sm md:text-base truncate">${evento.titulo}</h4>
                        ${tipoBadge}
                    </div>
                    <p class="text-xs md:text-sm text-gray-600 truncate">${evento.subtitulo}</p>
                </div>
                <div class="text-right">
                    <p class="font-bold text-sm md:text-lg text-cyan-600">${evento.hora_inicio}</p>
                    <div class="mt-2">${estadoBadge}</div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Navega a la semana anterior o siguiente
 */
function navegarAgenda(direccion) {
    cargarAgendaSemanal(agendaOffsetSemana + direccion);
}

/**
 * Navega a la semana actual
 */
function irAHoy() {
    cargarAgendaSemanal(0);
}

/**
 * Ver detalle de un evento específico
 */
async function verDetalleEvento(tipo, id) {
    const modal = document.getElementById('modal-detalle-evento');
    if (!modal) return;
    
    try {
        const response = await fetch(`/medico/api/detalle-evento/${tipo}/${id}`);
        const data = await response.json();
        
        if (data.success) {
            mostrarModalEvento(data.evento, tipo);
        } else {
            alert('Error al cargar el detalle del evento');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión');
    }
}

// Variables globales para el modal de eventos
let eventoActual = null;
let tipoEventoActual = null;

/**
 * Muestra el modal con el detalle del evento
 */
function mostrarModalEvento(evento, tipo) {
    const modal = document.getElementById('modal-detalle-evento');
    const header = document.getElementById('modal-evento-header');
    const icono = document.getElementById('modal-evento-icono');
    const tipoEl = document.getElementById('modal-evento-tipo');
    const estadoEl = document.getElementById('modal-evento-estado');
    const pacienteEl = document.getElementById('modal-evento-paciente');
    const servicioEl = document.getElementById('modal-evento-servicio');
    const fechaEl = document.getElementById('modal-evento-fecha');
    const horaEl = document.getElementById('modal-evento-hora');
    
    // Guardar evento actual para uso posterior
    eventoActual = evento;
    tipoEventoActual = tipo;
    
    // Color del header según tipo
    let gradiente = '';
    let iconoTexto = '';
    let tipoTexto = '';
    
    switch(tipo) {
        case 'cita':
            gradiente = 'from-cyan-500 to-teal-500';
            iconoTexto = 'event';
            tipoTexto = 'Cita Médica';
            break;
        case 'examen':
            gradiente = 'from-blue-500 to-cyan-500';
            iconoTexto = 'biotech';
            tipoTexto = 'Examen Médico';
            break;
        case 'operacion':
            gradiente = 'from-red-500 to-orange-500';
            iconoTexto = 'surgical';
            tipoTexto = 'Operación';
            break;
    }
    
    header.className = `px-6 py-5 text-white bg-gradient-to-br ${gradiente}`;
    icono.textContent = iconoTexto;
    tipoEl.textContent = tipoTexto;
    estadoEl.textContent = evento.estado || 'Pendiente';
    pacienteEl.textContent = evento.paciente || '-';
    servicioEl.textContent = evento.servicio || '-';
    
    // Formatear fecha
    if (evento.fecha) {
        const fecha = new Date(evento.fecha + 'T00:00:00');
        fechaEl.textContent = fecha.toLocaleDateString('es-ES', { 
            weekday: 'long', 
            day: 'numeric', 
            month: 'long', 
            year: 'numeric' 
        });
    } else {
        fechaEl.textContent = '-';
    }
    
    // Formatear hora
    if (evento.hora_inicio && evento.hora_fin) {
        horaEl.textContent = `${evento.hora_inicio} - ${evento.hora_fin}`;
    } else if (evento.hora_inicio) {
        horaEl.textContent = evento.hora_inicio;
    } else {
        horaEl.textContent = '-';
    }
    
    // Manejar sección de observaciones para exámenes y operaciones
    manejarSeccionObservaciones(evento, tipo);
    
    modal.classList.remove('hidden');
}

/**
 * Maneja la visibilidad y contenido de la sección de observaciones
 */
function manejarSeccionObservaciones(evento, tipo) {
    const seccionObservaciones = document.getElementById('seccion-observaciones');
    const observacionesExistentes = document.getElementById('observaciones-existentes');
    const formularioCompletar = document.getElementById('formulario-completar');
    const btnCompletar = document.getElementById('btn-completar-procedimiento');
    const btnCompletarTexto = document.getElementById('btn-completar-texto');
    const camposOperacion = document.getElementById('campos-operacion');
    
    // Limpiar formularios
    const inputObservaciones = document.getElementById('input-observaciones');
    const inputProcedimientos = document.getElementById('input-procedimientos');
    const inputComplicaciones = document.getElementById('input-complicaciones');
    
    if (inputObservaciones) inputObservaciones.value = '';
    if (inputProcedimientos) inputProcedimientos.value = '';
    if (inputComplicaciones) inputComplicaciones.value = '';
    
    // Solo mostrar para exámenes y operaciones
    if (tipo === 'examen' || tipo === 'operacion') {
        seccionObservaciones.classList.remove('hidden');
        
        const esPendiente = evento.estado === 'Pendiente' || evento.estado === 'pendiente';
        
        if (esPendiente) {
            // Mostrar formulario para completar
            observacionesExistentes.classList.add('hidden');
            formularioCompletar.classList.remove('hidden');
            btnCompletar.classList.remove('hidden');
            
            // Mostrar campos adicionales solo para operaciones
            if (tipo === 'operacion') {
                camposOperacion.classList.remove('hidden');
                btnCompletarTexto.textContent = 'Completar Operación';
            } else {
                camposOperacion.classList.add('hidden');
                btnCompletarTexto.textContent = 'Completar Examen';
            }
        } else {
            // Mostrar observaciones existentes si ya está completado
            formularioCompletar.classList.add('hidden');
            btnCompletar.classList.add('hidden');
            
            // Cargar observaciones desde el servidor
            cargarObservacionesExistentes(evento.id, tipo);
        }
    } else {
        // Para citas, ocultar toda la sección
        seccionObservaciones.classList.add('hidden');
        btnCompletar.classList.add('hidden');
    }
}

/**
 * Carga las observaciones existentes de un examen/operación
 */
async function cargarObservacionesExistentes(idEvento, tipo) {
    const observacionesExistentes = document.getElementById('observaciones-existentes');
    const textoObservaciones = document.getElementById('texto-observaciones-existentes');
    const fechaCompletado = document.getElementById('fecha-completado');
    
    try {
        const response = await fetch(`/medico/api/obtener-observaciones/${tipo}/${idEvento}`);
        const data = await response.json();
        
        if (data.success && data.observaciones) {
            textoObservaciones.textContent = data.observaciones;
            if (data.completado) {
                fechaCompletado.textContent = 'Estado: Completado';
            } else {
                fechaCompletado.textContent = '';
            }
            observacionesExistentes.classList.remove('hidden');
        } else {
            observacionesExistentes.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error al cargar observaciones:', error);
        observacionesExistentes.classList.add('hidden');
    }
}

/**
 * Completa un procedimiento (examen u operación)
 */
async function completarProcedimiento() {
    if (!eventoActual || !tipoEventoActual) {
        alert('Error: No hay evento seleccionado');
        return;
    }
    
    const inputObservaciones = document.getElementById('input-observaciones');
    const observaciones = inputObservaciones.value.trim();
    
    if (!observaciones) {
        alert('Por favor, ingresa las observaciones del procedimiento');
        inputObservaciones.focus();
        return;
    }
    
    const btnCompletar = document.getElementById('btn-completar-procedimiento');
    const btnCompletarTexto = document.getElementById('btn-completar-texto');
    const textoOriginal = btnCompletarTexto.textContent;
    
    // Mostrar estado de carga
    btnCompletar.disabled = true;
    btnCompletarTexto.textContent = 'Procesando...';
    
    try {
        let url = '';
        let body = { observaciones: observaciones };
        
        if (tipoEventoActual === 'examen') {
            url = `/medico/api/completar-examen/${eventoActual.id}`;
        } else if (tipoEventoActual === 'operacion') {
            url = `/medico/api/completar-operacion/${eventoActual.id}`;
            
            // Agregar campos adicionales para operaciones
            const inputProcedimientos = document.getElementById('input-procedimientos');
            const inputComplicaciones = document.getElementById('input-complicaciones');
            
            if (inputProcedimientos && inputProcedimientos.value.trim()) {
                body.procedimientos_realizados = inputProcedimientos.value.trim();
            }
            if (inputComplicaciones && inputComplicaciones.value.trim()) {
                body.complicaciones = inputComplicaciones.value.trim();
            }
        } else {
            alert('Tipo de procedimiento no válido');
            return;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mostrar mensaje de éxito
            alert(`${tipoEventoActual === 'examen' ? 'Examen' : 'Operación'} completado exitosamente`);
            
            // Cerrar modal
            cerrarModalEvento();
            
            // Recargar la agenda para reflejar el cambio
            if (typeof cargarAgendaSemanal === 'function') {
                // Limpiar cache para forzar recarga
                if (typeof agendaCacheEventos !== 'undefined') {
                    agendaCacheEventos = {};
                }
                cargarAgendaSemanal(agendaOffsetSemana);
            }
        } else {
            alert(data.message || 'Error al completar el procedimiento');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión al completar el procedimiento');
    } finally {
        // Restaurar botón
        btnCompletar.disabled = false;
        btnCompletarTexto.textContent = textoOriginal;
    }
}

/**
 * Cierra el modal de detalle de evento
 */
function cerrarModalEvento() {
    const modal = document.getElementById('modal-detalle-evento');
    if (modal) modal.classList.add('hidden');
    
    // Limpiar variables globales
    eventoActual = null;
    tipoEventoActual = null;
}

/**
 * Muestra un mensaje de error en la agenda
 */
function mostrarErrorAgenda(mensaje) {
    const vacio = document.getElementById('agenda-vacio');
    if (vacio) {
        vacio.innerHTML = `
            <span class="material-symbols-outlined text-6xl text-red-300 mb-4 block">error</span>
            <p class="text-red-500 font-medium">${mensaje}</p>
            <button onclick="cargarAgendaSemanal(agendaOffsetSemana)" class="mt-4 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors">
                Reintentar
            </button>
        `;
        vacio.classList.remove('hidden');
    }
}

// Cerrar modales al hacer clic fuera
document.addEventListener('click', function(e) {
    const modalEvento = document.getElementById('modal-detalle-evento');
    if (modalEvento && e.target === modalEvento) {
        cerrarModalEvento();
    }
});

// ========== EXPORTAR FUNCIONES AL OBJETO WINDOW ==========
// Necesario para que los eventos onclick en el HTML puedan acceder a estas funciones
window.navegarAgenda = navegarAgenda;
window.irAHoy = irAHoy;
window.verDetalleEvento = verDetalleEvento;
window.cerrarModalEvento = cerrarModalEvento;
window.cargarAgendaSemanal = cargarAgendaSemanal;
window.completarProcedimiento = completarProcedimiento;
