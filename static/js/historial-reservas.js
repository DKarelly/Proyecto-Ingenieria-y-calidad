// historial-reservas.js - Gestión del historial de reservas del paciente con pestañas

console.log('🔄 Historial de reservas cargado - Versión 2.0');

let reservasData = [];
let tipoActivo = 1; // Por defecto: CITAS
let reservaDestacada = null; // ID de la reserva a destacar

// Cargar reservas al iniciar
document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 Inicializando historial de reservas...');
    
    // Establecer fecha actual como valor por defecto en "Desde"
    const hoy = new Date();
    const fechaHoy = hoy.toISOString().split('T')[0]; // Formato YYYY-MM-DD
    document.getElementById('filtroFechaDesde').value = fechaHoy;
    console.log('📅 Filtro "Desde" establecido a:', fechaHoy);
    
    // Obtener parámetro de reserva de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const reservaId = urlParams.get('reserva');
    if (reservaId) {
        reservaDestacada = parseInt(reservaId);
        console.log('🎯 Reserva destacada:', reservaDestacada);
    }
    
    cargarReservas();

    // Event listeners para filtros
    document.getElementById('filtroEstado').addEventListener('change', aplicarFiltros);
    document.getElementById('filtroFechaDesde').addEventListener('change', aplicarFiltros);
    document.getElementById('filtroFechaHasta').addEventListener('change', aplicarFiltros);
    document.getElementById('btnLimpiarFiltros').addEventListener('click', limpiarFiltros);

    // Event listeners para pestañas
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            cambiarPestana(this);
        });
    });
});

// Función para cambiar de pestaña
function cambiarPestana(button) {
    const tipo = parseInt(button.dataset.tipo);
    tipoActivo = tipo;

    // Actualizar estilos de pestañas
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('border-cyan-500', 'text-cyan-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    button.classList.remove('border-transparent', 'text-gray-500');
    button.classList.add('border-cyan-500', 'text-cyan-600');

    // Aplicar filtros con el nuevo tipo
    aplicarFiltros();
}

// Función para cargar todas las reservas
async function cargarReservas() {
    try {
        const response = await fetch('/reservas/api/paciente/mis-reservas');
        const data = await response.json();

        if (data.error) {
            mostrarError(data.error);
            return;
        }

        reservasData = data.reservas || [];
        
        // Si hay una reserva destacada, cambiar a su pestaña automáticamente
        if (reservaDestacada) {
            const reserva = reservasData.find(r => r.id_reserva === reservaDestacada);
            if (reserva) {
                // Determinar el tipo según la reserva
                let tipoReserva = reserva.tipo || 1;
                tipoActivo = tipoReserva;
                
                // Actualizar visualmente la pestaña activa
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('border-cyan-500', 'text-cyan-600');
                    btn.classList.add('border-transparent', 'text-gray-500');
                    if (parseInt(btn.dataset.tipo) === tipoReserva) {
                        btn.classList.remove('border-transparent', 'text-gray-500');
                        btn.classList.add('border-cyan-500', 'text-cyan-600');
                    }
                });
            }
        }
        
        // Ordenar por fecha programación (más reciente primero)
        reservasData.sort((a, b) => {
            const fechaA = new Date(a.fecha_programacion || a.fecha_registro);
            const fechaB = new Date(b.fecha_programacion || b.fecha_registro);
            return fechaB - fechaA; // Orden descendente (más reciente primero)
        });
        
        mostrarReservas(reservasData);

    } catch (error) {
        console.error('Error al cargar reservas:', error);
        mostrarError('Error al cargar las reservas. Por favor, intenta nuevamente.');
    }
}

// Función para mostrar las reservas según la pestaña activa
function mostrarReservas(reservas) {
    const container = document.getElementById('reservasContainer');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const contadorResultados = document.getElementById('contadorResultados');

    loadingState.classList.add('hidden');

    if (!reservas || reservas.length === 0) {
        container.classList.add('hidden');
        emptyState.classList.remove('hidden');
        contadorResultados.textContent = 'Mostrando 0 reservas';
        return;
    }

    emptyState.classList.add('hidden');
    container.classList.remove('hidden');
    contadorResultados.textContent = `Mostrando ${reservas.length} reserva${reservas.length !== 1 ? 's' : ''}`;

    // Generar HTML según el tipo activo
    if (tipoActivo === 1) {
        // PESTAÑA DE CITAS
        container.innerHTML = reservas.map(reserva => generarTarjetaCita(reserva)).join('');
    } else if (tipoActivo === 2) {
        // PESTAÑA DE OPERACIONES
        container.innerHTML = reservas.map(reserva => generarTarjetaOperacion(reserva)).join('');
    } else if (tipoActivo === 3) {
        // PESTAÑA DE EXÁMENES
        container.innerHTML = reservas.map(reserva => generarTarjetaExamen(reserva)).join('');
    }
    
    // Si hay una reserva destacada, hacer scroll hacia ella
    if (reservaDestacada) {
        setTimeout(() => {
            const elementoDestacado = document.getElementById(`reserva-${reservaDestacada}`);
            if (elementoDestacado) {
                elementoDestacado.scrollIntoView({ behavior: 'smooth', block: 'center' });
                // Añadir animación de pulso
                elementoDestacado.classList.add('animate-pulse');
                setTimeout(() => {
                    elementoDestacado.classList.remove('animate-pulse');
                }, 2000);
            }
        }, 300);
    }
}

// Generar tarjeta para CITAS
function generarTarjetaCita(reserva) {
    const fechaStr = reserva.fecha_programacion || reserva.fecha_cita;
    const fecha = new Date(fechaStr + 'T00:00:00');
    const fechaFormateada = fecha.toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const estadoCancelacion = reserva.estado_cancelacion || 'Ninguna';
    const {estadoClass, estadoTexto, borderColorClass, bgColorClass} = obtenerEstilosEstado(reserva.estado_reserva, estadoCancelacion);
    
    const tieneExamenesOOperaciones = (reserva.examenes && reserva.examenes.length > 0) || (reserva.operaciones && reserva.operaciones.length > 0);
    const esCitaCompletada = reserva.estado_reserva === 'Completada';
    const esCitaInasistida = reserva.estado_reserva === 'Inasistida';
    const esCitaCancelada = reserva.estado_reserva === 'Cancelada';
    
    // Verificar si esta es la reserva destacada
    const esDestacada = reservaDestacada && reserva.id_reserva === reservaDestacada;
    const estilosDestacado = esDestacada ? 'ring-4 ring-cyan-400 shadow-2xl' : '';

    let html = `
        <div id="reserva-${reserva.id_reserva}" class="${bgColorClass} border-2 ${borderColorClass} ${estilosDestacado} rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl">
            <div class="p-6">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center text-2xl">
                            🩺
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${reserva.servicio}</h3>
                            <p class="text-sm text-gray-600">ID: #${reserva.id_reserva}</p>
                        </div>
                    </div>
                    <span class="${estadoClass} status-badge">${estadoTexto}</span>
                </div>

                <div class="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl p-4 mb-4">
                    <div class="flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan-600">
                            <rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>
                        </svg>
                        <div>
                            <p class="text-2xl font-bold text-cyan-600">${fechaFormateada.split(',')[0]}</p>
                            <p class="text-gray-600">${fechaFormateada.split(',').slice(1).join(',').trim()}</p>
                        </div>
                    </div>
                </div>

                <div class="grid md:grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-cyan-100 rounded-lg flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan-600">
                                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs text-gray-500">Horario</p>
                            <p class="font-semibold text-gray-800">${reserva.hora_inicio} - ${reserva.hora_fin}</p>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-blue-600">
                                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs text-gray-500">Médico</p>
                            <p class="font-semibold text-gray-800">${reserva.medico_nombres ? 'Dr(a). ' + reserva.medico_nombres + ' ' + reserva.medico_apellidos : 'Por asignar'}</p>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-purple-600">
                                <rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs text-gray-500">Registrada</p>
                            <p class="font-semibold text-gray-800">${new Date(reserva.fecha_registro).toLocaleDateString('es-ES')}</p>
                        </div>
                    </div>
                </div>
    `;

    // Si es una cita completada con exámenes/operaciones, mostrar subcarpeta
    if (esCitaCompletada && tieneExamenesOOperaciones) {
        html += `
                <div class="mt-4 pt-4 border-t border-gray-200">
                    <button onclick="toggleDetalleCita(${reserva.id_reserva})" class="w-full flex items-center justify-between bg-gradient-to-r from-indigo-50 to-purple-50 hover:from-indigo-100 hover:to-purple-100 rounded-lg p-4 transition-all duration-300">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-indigo-500 rounded-lg flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                                </svg>
                            </div>
                            <div class="text-left">
                                <p class="font-semibold text-gray-800">Procedimientos Asociados</p>
                                <p class="text-sm text-gray-600">
                                    ${reserva.examenes && reserva.examenes.length > 0 ? reserva.examenes.length + ' examen(es)' : ''}
                                    ${reserva.examenes && reserva.examenes.length > 0 && reserva.operaciones && reserva.operaciones.length > 0 ? ' • ' : ''}
                                    ${reserva.operaciones && reserva.operaciones.length > 0 ? reserva.operaciones.length + ' operación(es)' : ''}
                                </p>
                            </div>
                        </div>
                        <svg id="icon-${reserva.id_reserva}" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="transform transition-transform">
                            <polyline points="6 9 12 15 18 9"/>
                        </svg>
                    </button>
                    <div id="detalle-${reserva.id_reserva}" class="hidden mt-3 space-y-3">
                        ${generarDetallesExamenesOperaciones(reserva)}
                    </div>
                </div>
        `;
    }

    // Botones de acción (NO mostrar si es Completada, Inasistida o Cancelada)
    if (!esCitaCompletada && !esCitaInasistida && !esCitaCancelada && estadoCancelacion === 'Ninguna') {
        // Calcular días hasta la cita
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);
        const fechaCita = new Date(fechaStr + 'T00:00:00');
        const diasDiferencia = Math.ceil((fechaCita - hoy) / (1000 * 60 * 60 * 24));
        const puedeModificar = diasDiferencia >= 2; // Debe ser al menos 2 días antes
        
        console.log(`📅 Reserva #${reserva.id_reserva}: Fecha=${fechaStr}, Días diferencia=${diasDiferencia}, Puede modificar=${puedeModificar}`);
        
        html += `
                <div class="mt-6 pt-4 border-t border-gray-200">
                    <div class="flex flex-col gap-3">
        `;
        
        // Mensaje de advertencia si faltan menos de 2 días
        if (!puedeModificar) {
            html += `
                        <div class="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg">
                            <div class="flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-amber-600">
                                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                                    <path d="M12 9v4"/><path d="M12 17h.01"/>
                                </svg>
                                <div>
                                    <p class="text-sm font-semibold text-amber-800">Cita próxima</p>
                                    <p class="text-xs text-amber-700">Las solicitudes de reprogramación o cancelación deben realizarse con al menos 2 días de anticipación.</p>
                                </div>
                            </div>
                        </div>
            `;
        }
        
        // Determinar estado de reprogramación y cancelación
        const tieneReprogramacionAprobada = reserva.tiene_reprogramacion_aprobada > 0;
        const tieneSolicitudReprogramacion = reserva.tiene_solicitud_reprogramacion > 0;
        const tieneSolicitudCancelacion = reserva.tiene_solicitud_cancelacion > 0;
        
        html += `
                        <div class="grid md:grid-cols-2 gap-3">
        `;
        
        // BOTÓN DE REPROGRAMACIÓN (condicional según estado)
        if (tieneReprogramacionAprobada) {
            // Si tiene reprogramación aprobada, mostrar botón verde para EJECUTAR la reprogramación
            html += `
                            <button onclick="abrirModalReprogramar(${reserva.id_reserva}, '${reserva.servicio}', '${reserva.fecha_programacion}')" 
                                    class="group relative overflow-hidden bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-3.5 px-5 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-[1.02]">
                                <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="relative z-10">
                                    <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>
                                    <circle cx="12" cy="12" r="2"/>
                                </svg>
                                <span class="relative z-10">✓ Reprogramar Ahora</span>
                            </button>
            `;
        } else if (tieneSolicitudReprogramacion) {
            // Si tiene solicitud de reprogramación pendiente, mostrar botón deshabilitado
            html += `
                            <button disabled 
                                    class="group relative overflow-hidden bg-gray-500 cursor-not-allowed text-white font-semibold py-3.5 px-5 rounded-xl flex items-center justify-center gap-2 shadow-md">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                                </svg>
                                <span>Reprogramación Pendiente...</span>
                            </button>
            `;
        } else {
            // Si no tiene ninguna solicitud, mostrar botón azul para SOLICITAR reprogramación
            html += `
                            <button ${!puedeModificar ? 'disabled' : ''} 
                                    onclick="${puedeModificar ? `solicitarReprogramacion(${reserva.id_reserva}, '${reserva.servicio}', '${reserva.fecha_programacion}')` : 'return false;'}" 
                                    class="group relative overflow-hidden bg-gradient-to-r from-blue-500 to-blue-600 ${!puedeModificar ? 'opacity-50 cursor-not-allowed' : 'hover:from-blue-600 hover:to-blue-700'} text-white font-semibold py-3.5 px-5 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-lg ${puedeModificar ? 'hover:shadow-xl hover:scale-[1.02]' : ''}">
                                <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -translate-x-full ${puedeModificar ? 'group-hover:translate-x-full' : ''} transition-transform duration-700"></div>
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="relative z-10">
                                    <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>
                                </svg>
                                <span class="relative z-10">Solicitar Reprogramación</span>
                            </button>
            `;
        }
        
        // BOTÓN DE CANCELACIÓN (condicional según estado)
        if (tieneSolicitudCancelacion) {
            // Si tiene solicitud de cancelación pendiente, mostrar botón deshabilitado
            html += `
                            <button disabled 
                                    class="group relative overflow-hidden bg-gray-500 cursor-not-allowed text-white font-semibold py-3.5 px-5 rounded-xl flex items-center justify-center gap-2 shadow-md">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                                </svg>
                                <span>Cancelación Pendiente...</span>
                            </button>
            `;
        } else {
            // Botón normal de solicitar cancelación
            html += `
                            <button ${!puedeModificar ? 'disabled' : ''} 
                                    onclick="${puedeModificar ? `solicitarCancelacion(${reserva.id_reserva}, '${reserva.servicio}', '${reserva.fecha_programacion}')` : 'return false;'}" 
                                    class="group relative overflow-hidden bg-gradient-to-r from-red-500 to-red-600 ${!puedeModificar ? 'opacity-50 cursor-not-allowed' : 'hover:from-red-600 hover:to-red-700'} text-white font-semibold py-3.5 px-5 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-lg ${puedeModificar ? 'hover:shadow-xl hover:scale-[1.02]' : ''}">
                                <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -translate-x-full ${puedeModificar ? 'group-hover:translate-x-full' : ''} transition-transform duration-700"></div>
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="relative z-10">
                                    <circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>
                                </svg>
                                <span class="relative z-10">Solicitar Cancelación</span>
                            </button>
            `;
        }
        
        html += `
                        </div>
                    </div>
                </div>
        `;
    }

    html += `
            </div>
        </div>
    `;

    return html;
}

// Generar detalles de exámenes y operaciones de una cita completada
function generarDetallesExamenesOperaciones(reserva) {
    let html = '';

    // EXÁMENES
    if (reserva.examenes && reserva.examenes.length > 0) {
        reserva.examenes.forEach(examen => {
            const examFecha = examen.fecha_examen ? new Date(examen.fecha_examen + 'T00:00:00').toLocaleDateString('es-ES') : 'No especificada';
            const puedeReprogramar = examen.estado !== 'Completada';
            html += `
                <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div class="flex justify-between items-start mb-3">
                        <div class="flex items-center gap-2">
                            <span class="text-xl">🔬</span>
                            <h5 class="font-semibold text-gray-800">${examen.nombre_servicio || 'Examen'}</h5>
                        </div>
                        <span class="px-2 py-1 rounded-full text-xs font-semibold ${examen.estado === 'Completada' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                            ${examen.estado === 'Completada' ? '✅ Completada' : '⏳ ' + examen.estado}
                        </span>
                    </div>
                    <div class="grid md:grid-cols-2 gap-2 text-sm">
                        <p class="text-gray-700"><strong>Fecha:</strong> ${examFecha}</p>
                        ${examen.hora_examen ? `<p class="text-gray-700"><strong>Hora:</strong> ${examen.hora_examen}</p>` : ''}
                        ${examen.observacion ? `<p class="text-gray-600 col-span-2"><strong>Observaciones:</strong> ${examen.observacion}</p>` : ''}
                    </div>
                    ${puedeReprogramar && examen.id_reserva ? `
                    <div class="mt-3 pt-3 border-t border-purple-300 flex gap-2">
                        <button onclick="solicitarReprogramacion(${examen.id_reserva}, '${examen.nombre_servicio || 'Examen'}', '${examen.fecha_examen}')" 
                                class="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-3 rounded-lg text-sm transition-all">
                            🔄 Solicitar Reprogramación
                        </button>
                    </div>
                    ` : ''}
                </div>
            `;
        });
    }

    // OPERACIONES
    if (reserva.operaciones && reserva.operaciones.length > 0) {
        reserva.operaciones.forEach(operacion => {
            const opFecha = operacion.fecha_operacion ? new Date(operacion.fecha_operacion + 'T00:00:00').toLocaleDateString('es-ES') : 'No especificada';
            const opCompletada = operacion.hora_fin ? true : false;
            const puedeReprogramar = !opCompletada;
            html += `
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div class="flex justify-between items-start mb-3">
                        <div class="flex items-center gap-2">
                            <span class="text-xl">⚕️</span>
                            <h5 class="font-semibold text-gray-800">Operación</h5>
                        </div>
                        <span class="px-2 py-1 rounded-full text-xs font-semibold ${opCompletada ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                            ${opCompletada ? '✅ Completada' : '⏳ Pendiente'}
                        </span>
                    </div>
                    <div class="grid md:grid-cols-2 gap-2 text-sm">
                        <p class="text-gray-700"><strong>Fecha:</strong> ${opFecha}</p>
                        ${operacion.hora_inicio ? `<p class="text-gray-700"><strong>Hora:</strong> ${operacion.hora_inicio}${operacion.hora_fin ? ' - ' + operacion.hora_fin : ''}</p>` : ''}
                        ${operacion.observaciones ? `<p class="text-gray-600 col-span-2"><strong>Observaciones:</strong> ${operacion.observaciones}</p>` : ''}
                    </div>
                    ${puedeReprogramar && operacion.id_reserva ? `
                    <div class="mt-3 pt-3 border-t border-red-300 flex gap-2">
                        <button onclick="solicitarReprogramacion(${operacion.id_reserva}, 'Operación', '${operacion.fecha_operacion}')" 
                                class="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-3 rounded-lg text-sm transition-all">
                            🔄 Solicitar Reprogramación
                        </button>
                    </div>
                    ` : ''}
                </div>
            `;
        });
    }

    return html;
}

// Generar tarjeta para OPERACIONES
function generarTarjetaOperacion(reserva) {
    const fechaStr = reserva.fecha_programacion;
    const fecha = new Date(fechaStr + 'T00:00:00');
    const fechaFormateada = fecha.toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const estadoCancelacion = reserva.estado_cancelacion || 'Ninguna';
    const {estadoClass, estadoTexto, borderColorClass, bgColorClass} = obtenerEstilosEstado(reserva.estado_reserva, estadoCancelacion);
    
    // Verificar si esta es la reserva destacada
    const esDestacada = reservaDestacada && reserva.id_reserva === reservaDestacada;
    const estilosDestacado = esDestacada ? 'ring-4 ring-cyan-400 shadow-2xl' : '';

    return `
        <div id="reserva-${reserva.id_reserva}" class="${bgColorClass} border-2 ${borderColorClass} ${estilosDestacado} rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl">
            <div class="p-6">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-gradient-to-br from-red-400 to-red-600 rounded-xl flex items-center justify-center text-2xl">
                            ⚕️
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${reserva.servicio}</h3>
                            <p class="text-sm text-gray-600">ID: #${reserva.id_reserva}</p>
                        </div>
                    </div>
                    <span class="${estadoClass} status-badge">${estadoTexto}</span>
                </div>

                <div class="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-4 mb-4">
                    <div class="flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-red-600">
                            <rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>
                        </svg>
                        <div>
                            <p class="text-2xl font-bold text-red-600">${fechaFormateada.split(',')[0]}</p>
                            <p class="text-gray-600">${fechaFormateada.split(',').slice(1).join(',').trim()}</p>
                        </div>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-red-600">
                                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs text-gray-500">Horario</p>
                            <p class="font-semibold text-gray-800">${reserva.hora_inicio} - ${reserva.hora_fin}</p>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-purple-600">
                                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs text-gray-500">Médico</p>
                            <p class="font-semibold text-gray-800">${reserva.medico_nombres ? 'Dr(a). ' + reserva.medico_nombres + ' ' + reserva.medico_apellidos : 'Por asignar'}</p>
                        </div>
                    </div>
                </div>

                ${reserva.operaciones && reserva.operaciones.length > 0 && reserva.operaciones[0].id_cita ? `
                <div class="mt-4 pt-4 border-t border-gray-200">
                    <button onclick="verDetalleCitaOperacion(${reserva.id_reserva}, ${reserva.operaciones[0].id_cita})" 
                            class="w-full bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-indigo-600 hover:to-indigo-700 transition-all duration-300 flex items-center justify-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
                        </svg>
                        Ver Detalle de Cita Médica
                    </button>
                </div>
                ` : ''}

                ${estadoCancelacion === 'Ninguna' && reserva.estado_reserva !== 'Cancelada' && reserva.estado_reserva !== 'Completada' ? `
                <div class="mt-4 pt-4 border-t border-gray-200">
                    <div class="grid md:grid-cols-2 gap-3">
                        <button onclick="solicitarReprogramacion(${reserva.id_reserva}, '${reserva.servicio}', '${reserva.fecha_programacion}')" 
                                class="bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-300 flex items-center justify-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>
                            </svg>
                            Solicitar Reprogramación
                        </button>
                        <button onclick="solicitarCancelacion(${reserva.id_reserva}, '${reserva.servicio}', '${reserva.fecha_programacion}')" 
                                class="bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-300 flex items-center justify-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                            </svg>
                            Solicitar Cancelación
                        </button>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Generar tarjeta para EXÁMENES
function generarTarjetaExamen(reserva) {
    const fechaStr = reserva.fecha_programacion;
    const fecha = new Date(fechaStr + 'T00:00:00');
    const fechaFormateada = fecha.toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const estadoCancelacion = reserva.estado_cancelacion || 'Ninguna';
    const {estadoClass, estadoTexto, borderColorClass, bgColorClass} = obtenerEstilosEstado(reserva.estado_reserva, estadoCancelacion);
    
    // Verificar si esta es la reserva destacada
    const esDestacada = reservaDestacada && reserva.id_reserva === reservaDestacada;
    const estilosDestacado = esDestacada ? 'ring-4 ring-cyan-400 shadow-2xl' : '';

    return `
        <div id="reserva-${reserva.id_reserva}" class="${bgColorClass} border-2 ${borderColorClass} ${estilosDestacado} rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl">
            <div class="p-6">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center text-2xl">
                            🔬
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${reserva.servicio}</h3>
                            <p class="text-sm text-gray-600">ID: #${reserva.id_reserva}</p>
                        </div>
                    </div>
                    <span class="${estadoClass} status-badge">${estadoTexto}</span>
                </div>

                <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 mb-4">
                    <div class="flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-purple-600">
                            <rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>
                        </svg>
                        <div>
                            <p class="text-2xl font-bold text-purple-600">${fechaFormateada.split(',')[0]}</p>
                            <p class="text-gray-600">${fechaFormateada.split(',').slice(1).join(',').trim()}</p>
                        </div>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-purple-600">
                                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs text-gray-500">Horario</p>
                            <p class="font-semibold text-gray-800">${reserva.hora_inicio} - ${reserva.hora_fin}</p>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-pink-100 rounded-lg flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-pink-600">
                                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs text-gray-500">Responsable</p>
                            <p class="font-semibold text-gray-800">${reserva.medico_nombres ? reserva.medico_nombres + ' ' + reserva.medico_apellidos : 'Por asignar'}</p>
                        </div>
                    </div>
                </div>

                ${reserva.examenes && reserva.examenes.length > 0 ? `
                <div class="mt-4 pt-4 border-t border-gray-200">
                    <button onclick="verDetalleCitaExamen(${reserva.id_reserva})" 
                            class="w-full bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-indigo-600 hover:to-indigo-700 transition-all duration-300 flex items-center justify-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
                        </svg>
                        Ver Detalle de Cita Médica
                    </button>
                </div>
                ` : ''}

                ${estadoCancelacion === 'Ninguna' && reserva.estado_reserva !== 'Cancelada' && reserva.estado_reserva !== 'Completada' ? `
                <div class="mt-4 pt-4 border-t border-gray-200">
                    <div class="grid md:grid-cols-2 gap-3">
                        <button onclick="solicitarReprogramacion(${reserva.id_reserva}, '${reserva.servicio}', '${reserva.fecha_programacion}')" 
                                class="bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-300 flex items-center justify-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>
                            </svg>
                            Solicitar Reprogramación
                        </button>
                        <button onclick="solicitarCancelacion(${reserva.id_reserva}, '${reserva.servicio}', '${reserva.fecha_programacion}')" 
                                class="bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-300 flex items-center justify-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                            </svg>
                            Solicitar Cancelación
                        </button>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Función auxiliar para obtener estilos de estado
function obtenerEstilosEstado(estadoReserva, estadoCancelacion) {
    let estadoClass = `status-${estadoReserva}`;
    let estadoTexto = estadoReserva;
    let borderColorClass = 'border-gray-100';
    let bgColorClass = 'bg-white';
    
    if (estadoCancelacion === 'Solicitada') {
        estadoClass = 'bg-gray-300 text-gray-700';
        estadoTexto = '⏳ Cancelación Solicitada';
        borderColorClass = 'border-gray-400';
        bgColorClass = 'bg-gray-50';
    } else if (estadoCancelacion === 'Cancelada') {
        estadoClass = 'bg-red-200 text-red-900';
        estadoTexto = '❌ Cancelada';
        borderColorClass = 'border-red-300';
        bgColorClass = 'bg-red-50';
    }

    return {estadoClass, estadoTexto, borderColorClass, bgColorClass};
}

// Toggle para mostrar/ocultar detalles de cita completada
function toggleDetalleCita(idReserva) {
    const detalle = document.getElementById(`detalle-${idReserva}`);
    const icon = document.getElementById(`icon-${idReserva}`);
    
    if (detalle.classList.contains('hidden')) {
        detalle.classList.remove('hidden');
        icon.classList.add('rotate-180');
    } else {
        detalle.classList.add('hidden');
        icon.classList.remove('rotate-180');
    }
}

// Función auxiliar para obtener información del tipo
function getTipoInfo(tipo) {
    // tipo: 1 = Cita Médica, 2 = Operación, 3 = Examen
    if (tipo == 1) {
        return {
            icono: '🩺',
            texto: 'Cita Médica',
            color: 'bg-blue-100 text-blue-800'
        };
    } else if (tipo == 2) {
        return {
            icono: '⚕️',
            texto: 'Operación',
            color: 'bg-red-100 text-red-800'
        };
    } else if (tipo == 3) {
        return {
            icono: '🔬',
            texto: 'Examen',
            color: 'bg-purple-100 text-purple-800'
        };
    } else {
        return {
            icono: '📋',
            texto: 'Reserva',
            color: 'bg-gray-100 text-gray-800'
        };
    }
}

// Función para aplicar filtros
function aplicarFiltros() {
    const estado = document.getElementById('filtroEstado').value;
    const fechaDesde = document.getElementById('filtroFechaDesde').value;
    const fechaHasta = document.getElementById('filtroFechaHasta').value;

    let reservasFiltradas = [...reservasData];

    // Filtrar por tipo activo (pestaña seleccionada)
    reservasFiltradas = reservasFiltradas.filter(r => r.tipo == tipoActivo);

    // Filtrar por estado
    if (estado) {
        reservasFiltradas = reservasFiltradas.filter(r => r.estado_reserva === estado);
    }

    // Filtrar por fecha desde
    if (fechaDesde) {
        reservasFiltradas = reservasFiltradas.filter(r => {
            const fechaReserva = r.fecha_programacion || r.fecha_cita;
            return new Date(fechaReserva) >= new Date(fechaDesde);
        });
    }

    // Filtrar por fecha hasta
    if (fechaHasta) {
        reservasFiltradas = reservasFiltradas.filter(r => {
            const fechaReserva = r.fecha_programacion || r.fecha_cita;
            return new Date(fechaReserva) <= new Date(fechaHasta);
        });
    }

    mostrarReservas(reservasFiltradas);
}

// Función para limpiar filtros
function limpiarFiltros() {
    document.getElementById('filtroEstado').value = '';
    // Restablecer "Desde" a la fecha actual
    const hoy = new Date();
    const fechaHoy = hoy.toISOString().split('T')[0];
    document.getElementById('filtroFechaDesde').value = fechaHoy;
    document.getElementById('filtroFechaHasta').value = '';
    aplicarFiltros(); // Aplica filtros con la pestaña activa
}

// Función para mostrar errores
function mostrarError(mensaje) {
    const container = document.getElementById('reservasContainer');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');

    loadingState.classList.add('hidden');
    container.classList.add('hidden');
    emptyState.classList.remove('hidden');

    emptyState.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-red-300 mb-4">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h3 class="text-xl font-semibold text-gray-800 mb-2">Error al cargar</h3>
        <p class="text-gray-600 mb-6">${mensaje}</p>
        <button onclick="cargarReservas()" class="bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold py-3 px-6 rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all duration-300">
            Intentar Nuevamente
        </button>
    `;
}

// ==================== FUNCIONES DE CANCELACIÓN Y REPROGRAMACIÓN ====================

let reservaActual = null;

function abrirModalCancelacion(idReserva, nombreServicio) {
    reservaActual = { id: idReserva, nombre: nombreServicio };
    
    // Crear modal dinámicamente
    const modalHTML = `
        <div id="modalCancelacion" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="p-6 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
                            <span class="text-3xl">⚠️</span>
                            Cancelar Reserva
                        </h2>
                        <button onclick="cerrarModalCancelacion()" class="text-gray-400 hover:text-gray-600 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded">
                        <p class="text-sm text-blue-800">
                            <strong>💡 Recomendación:</strong> Antes de cancelar, considera <strong>reprogramar</strong> tu reserva para otra fecha. 
                            Es más rápido y mantienes tu lugar en el sistema.
                        </p>
                    </div>
                    
                    <div class="mb-6">
                        <h3 class="font-semibold text-gray-700 mb-2">Servicio a cancelar:</h3>
                        <p class="text-lg text-gray-900">${nombreServicio}</p>
                    </div>
                    
                    <div class="mb-6">
                        <label class="block font-semibold text-gray-700 mb-2" for="motivoCancelacion">
                            Motivo de cancelación <span class="text-red-500">*</span>
                        </label>
                        <textarea 
                            id="motivoCancelacion" 
                            rows="4" 
                            class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                            placeholder="Por favor, explica el motivo de tu cancelación (mínimo 20 caracteres)..."
                            maxlength="500"
                        ></textarea>
                        <p class="text-xs text-gray-500 mt-1">
                            <span id="contadorCaracteres">0</span>/500 caracteres
                        </p>
                    </div>
                </div>
                
                <div class="p-6 border-t border-gray-200 flex gap-3">
                    <button onclick="cerrarModalCancelacion()" 
                            class="flex-1 bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-300 transition-all">
                        Volver
                    </button>
                    <button onclick="confirmarCancelacion()"
                            class="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-red-600 hover:to-red-700 transition-all">
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Contador de caracteres
    document.getElementById('motivoCancelacion').addEventListener('input', function() {
        document.getElementById('contadorCaracteres').textContent = this.value.length;
    });
}

function cerrarModalCancelacion() {
    const modal = document.getElementById('modalCancelacion');
    if (modal) {
        modal.remove();
    }
    reservaActual = null;
}

async function confirmarCancelacion() {
    const motivo = document.getElementById('motivoCancelacion').value.trim();
    
    if (!motivo || motivo.length < 10) {
        alert('Por favor, proporciona un motivo válido (mínimo 20 caracteres)');
        return;
    }
    
    try {
        const response = await fetch('/reservas/api/solicitar-cancelacion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_reserva: reservaActual.id,
                motivo: motivo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            cerrarModalCancelacion();
            cargarReservas(); // Recargar la lista
        } else {
            alert('❌ Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al enviar la solicitud. Intenta nuevamente.');
    }
}

function abrirModalReprogramacion(idReserva, nombreServicio, idServicio, fechaActual) {
    reservaActual = { 
        id: idReserva, 
        nombre: nombreServicio,
        idServicio: idServicio,
        fechaActual: fechaActual
    };
    
    const modalHTML = `
        <div id="modalReprogramacion" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div class="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="p-6 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
                            <span class="text-3xl">🔄</span>
                            Reprogramar Reserva
                        </h2>
                        <button onclick="cerrarModalReprogramacion()" class="text-gray-400 hover:text-gray-600 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <div class="bg-green-50 border-l-4 border-green-500 p-4 mb-6 rounded">
                        <p class="text-sm text-green-800">
                            <strong>✅ Buena elección:</strong> Reprogramar es más rápido que cancelar y volver a reservar.
                        </p>
                    </div>
                    
                    <div class="mb-6">
                        <h3 class="font-semibold text-gray-700 mb-2">Servicio:</h3>
                        <p class="text-lg text-gray-900">${nombreServicio}</p>
                    </div>
                    
                    <div class="mb-4">
                        <label class="block font-semibold text-gray-700 mb-2" for="nuevaFecha">
                            Nueva Fecha <span class="text-red-500">*</span>
                        </label>
                        <input 
                            type="date" 
                            id="nuevaFecha" 
                            class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                            min="${new Date().toISOString().split('T')[0]}"
                        />
                    </div>
                    
                    <div id="horariosContainer" class="hidden mb-6">
                        <label class="block font-semibold text-gray-700 mb-2">
                            Selecciona un nuevo horario <span class="text-red-500">*</span>
                        </label>
                        <div id="horariosLista" class="grid grid-cols-3 sm:grid-cols-4 gap-2">
                            <!-- Horarios se cargarán aquí -->
                        </div>
                        <p id="horaActualInfo" class="text-sm text-gray-600 mt-2"></p>
                    </div>
                    
                    <div id="loadingHorarios" class="hidden text-center py-4">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                        <p class="text-gray-600 mt-2">Cargando horarios disponibles...</p>
                    </div>
                </div>
                
                <div class="p-6 border-t border-gray-200 flex gap-3">
                    <button onclick="cerrarModalReprogramacion()" 
                            class="flex-1 bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-300 transition-all">
                        Cancelar
                    </button>
                    <button id="btnConfirmarReprogramacion" onclick="confirmarReprogramacion()" 
                            class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all"
                            disabled>
                        Confirmar Reprogramación
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Event listener para fecha
    document.getElementById('nuevaFecha').addEventListener('change', cargarHorariosDisponibles);
}

function cerrarModalReprogramacion() {
    const modal = document.getElementById('modalReprogramacion');
    if (modal) {
        modal.remove();
    }
    reservaActual = null;
}

let horaSeleccionada = null;

async function cargarHorariosDisponibles() {
    const fecha = document.getElementById('nuevaFecha').value;
    
    if (!fecha) return;
    
    const loadingDiv = document.getElementById('loadingHorarios');
    const horariosContainer = document.getElementById('horariosContainer');
    
    loadingDiv.classList.remove('hidden');
    horariosContainer.classList.add('hidden');
    
    console.log('Datos enviados:', {
        id_reserva: reservaActual.id,
        id_servicio: reservaActual.idServicio || null,
        fecha: fecha
    });
    
    try {
        const response = await fetch('/reservas/api/horarios-disponibles-reprogramacion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_reserva: reservaActual.id,
                id_servicio: reservaActual.idServicio || null,
                fecha: fecha
            })
        });
        
        const data = await response.json();
        
        console.log('Respuesta del servidor:', data);
        
        loadingDiv.classList.add('hidden');
        
        if (!response.ok) {
            horariosContainer.classList.remove('hidden');
            document.getElementById('horariosLista').innerHTML = `
                <div class="col-span-full text-center py-4 bg-red-50 rounded-lg">
                    <p class="text-red-600">Error: ${data.error || 'No se pudieron cargar los horarios'}</p>
                </div>
            `;
            return;
        }
        
        if (data.success && data.horarios.length > 0) {
            horariosContainer.classList.remove('hidden');
            const horariosLista = document.getElementById('horariosLista');
            const horaActualInfo = document.getElementById('horaActualInfo');
            
            horaActualInfo.textContent = `Hora actual de tu reserva: ${data.hora_actual}`;
            
            horariosLista.innerHTML = data.horarios.sort().map(hora => `
                <button 
                    onclick="seleccionarHora('${hora}')" 
                    class="hora-btn py-2 px-3 border-2 border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-sm font-semibold"
                    data-hora="${hora}">
                    ${hora}
                </button>
            `).join('');
        } else {
            horariosContainer.classList.remove('hidden');
            document.getElementById('horariosLista').innerHTML = `
                <div class="col-span-full text-center py-4">
                    <p class="text-gray-600">No hay horarios disponibles para esta fecha.</p>
                    <p class="text-sm text-gray-500 mt-2">Intenta con otra fecha.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        loadingDiv.classList.add('hidden');
        alert('Error al cargar horarios. Intenta nuevamente.');
    }
}

function seleccionarHora(hora) {
    horaSeleccionada = hora;
    
    // Actualizar estilos
    document.querySelectorAll('.hora-btn').forEach(btn => {
        btn.classList.remove('border-blue-600', 'bg-blue-500', 'text-white');
        btn.classList.add('border-gray-300');
    });
    
    const btnSeleccionado = document.querySelector(`[data-hora="${hora}"]`);
    btnSeleccionado.classList.remove('border-gray-300');
    btnSeleccionado.classList.add('border-blue-600', 'bg-blue-500', 'text-white');
    
    // Habilitar botón de confirmar
    document.getElementById('btnConfirmarReprogramacion').disabled = false;
}

async function confirmarReprogramacion() {
    const nuevaFecha = document.getElementById('nuevaFecha').value;
    
    
    if (!nuevaFecha || !horaSeleccionada) {
        alert('Por favor, selecciona una fecha y una hora');
        return;
    }
    
    const btnConfirmar = document.getElementById('btnConfirmarReprogramacion');
    btnConfirmar.disabled = true;
    btnConfirmar.textContent = 'Procesando...';
    
    try {
        const response = await fetch('/reservas/api/reprogramar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_reserva: reservaActual.id,
                nueva_fecha: nuevaFecha,
                nueva_hora: horaSeleccionada,
                id_servicio: reservaActual.idServicio || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            cerrarModalReprogramacion();
            cargarReservas(); // Recargar la lista
        } else {
            alert('❌ Error: ' + data.error);
            btnConfirmar.disabled = false;
            btnConfirmar.textContent = 'Confirmar Reprogramación';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al reprogramar. Intenta nuevamente.');
        btnConfirmar.disabled = false;
        btnConfirmar.textContent = 'Confirmar Reprogramación';
    }
}

// ========== NUEVAS FUNCIONES PARA SOLICITUDES ==========

// Función para solicitar reprogramación
async function solicitarReprogramacion(idReserva, nombreServicio, fechaActual) {
    console.log('🔄 Solicitando reprogramación para reserva:', idReserva);
    const modalHTML = `
        <div id="modalSolicitudReprogramacion" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
            <div class="bg-white rounded-2xl max-w-lg w-full shadow-2xl transform animate-slideIn">
                <div class="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-t-2xl">
                    <div class="flex items-center justify-between">
                        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                            <span class="text-3xl">🔄</span>
                            Solicitar Reprogramación
                        </h2>
                        <button onclick="cerrarModalSolicitudReprogramacion()" class="text-white hover:text-gray-200 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-r-lg">
                        <div class="flex items-start gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-blue-600 flex-shrink-0 mt-0.5">
                                <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
                            </svg>
                            <div>
                                <p class="text-sm font-semibold text-blue-900 mb-1">Proceso de Solicitud</p>
                                <p class="text-xs text-blue-800">
                                    Tu solicitud será revisada por el personal administrativo. Recibirás una notificación con la respuesta en las próximas 24-48 horas.
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-6 bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                                <polyline points="14 2 14 8 20 8"/>
                            </svg>
                            Detalles de tu Reserva
                        </h3>
                        <div class="space-y-2 text-sm">
                            <p class="text-gray-600"><span class="font-semibold">Servicio:</span> ${nombreServicio}</p>
                            <p class="text-gray-600"><span class="font-semibold">Fecha actual:</span> ${new Date(fechaActual + 'T00:00:00').toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                        </div>
                    </div>
                    
                    <div class="mb-6">
                        <label class="block font-semibold text-gray-700 mb-2" for="motivoReprogramacion">
                            Motivo de la reprogramación <span class="text-red-500">*</span>
                        </label>
                        <textarea 
                            id="motivoReprogramacion" 
                            rows="4" 
                            class="w-full border-2 border-gray-300 rounded-xl p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-none"
                            placeholder="Explica por qué necesitas reprogramar tu cita (mínimo 20 caracteres)..."
                            maxlength="500"
                        ></textarea>
                        <p class="text-xs text-gray-500 mt-2 flex items-center justify-between">
                            <span id="contadorReprog">0/20 caracteres mínimos</span>
                            <span><span id="contadorCaracteresReprog">0</span>/500</span>
                        </p>
                    </div>
                </div>
                
                <div class="p-6 bg-gray-50 rounded-b-2xl border-t border-gray-200 flex gap-3">
                    <button onclick="cerrarModalSolicitudReprogramacion()" 
                            class="flex-1 bg-white border-2 border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all">
                        Cancelar
                    </button>
                    <button onclick="confirmarSolicitudReprogramacion(${idReserva})" 
                            class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl">
                        Enviar Solicitud
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Contador de caracteres
    document.getElementById('motivoReprogramacion').addEventListener('input', function() {
        const contador = document.getElementById('contadorCaracteresReprog');
        const contadorMin = document.getElementById('contadorReprog');
        const longitud = this.value.length;
        contador.textContent = longitud;
        
        if (longitud < 20) {
            contadorMin.textContent = `${longitud}/20 caracteres mínimos`;
            contadorMin.classList.add('text-red-500');
            contadorMin.classList.remove('text-green-600');
        } else {
            contadorMin.textContent = '✓ Mínimo alcanzado';
            contadorMin.classList.remove('text-red-500');
            contadorMin.classList.add('text-green-600');
        }
    });
}

function cerrarModalSolicitudReprogramacion() {
    const modal = document.getElementById('modalSolicitudReprogramacion');
    if (modal) {
        modal.remove();
    }
}

async function confirmarSolicitudReprogramacion(idReserva) {
    const motivo = document.getElementById('motivoReprogramacion').value.trim();
    
    if (motivo.length < 20) {
        alert('❌ El motivo debe tener al menos 20 caracteres.');
        return;
    }
    
    try {
        const response = await fetch('/reservas/api/solicitar-reprogramacion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_reserva: idReserva,
                motivo: motivo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            cerrarModalSolicitudReprogramacion();
            mostrarNotificacionExito('✅ Solicitud Enviada', 'Tu solicitud de reprogramación ha sido enviada. Recibirás una respuesta pronto.');
            cargarReservas();
        } else {
            alert('❌ Error: ' + (data.error || 'No se pudo enviar la solicitud'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al enviar la solicitud. Intenta nuevamente.');
    }
}

// Función para solicitar reprogramación
async function solicitarReprogramacion(idReserva, nombreServicio, fechaActual) {
    console.log('🔄 Solicitando reprogramación para reserva:', idReserva);
    const modalHTML = `
        <div id="modalSolicitudReprogramacion" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
            <div class="bg-white rounded-2xl max-w-lg w-full shadow-2xl transform animate-slideIn">
                <div class="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-t-2xl">
                    <div class="flex items-center justify-between">
                        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                            <span class="text-3xl">🔄</span>
                            Solicitar Reprogramación
                        </h2>
                        <button onclick="cerrarModalSolicitudReprogramacion()" class="text-white hover:text-gray-200 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-r-lg">
                        <div class="flex items-start gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-blue-600 flex-shrink-0 mt-0.5">
                                <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                            </svg>
                            <div>
                                <p class="text-sm font-semibold text-blue-900 mb-1">Solicitud en revisión</p>
                                <p class="text-xs text-blue-800">
                                    Tu solicitud será evaluada por nuestro personal. Una vez aprobada, podrás seleccionar una nueva fecha.
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-6 bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                                <polyline points="14 2 14 8 20 8"/>
                            </svg>
                            Detalles de tu Reserva
                        </h3>
                        <div class="space-y-2 text-sm">
                            <p class="text-gray-600"><span class="font-semibold">Servicio:</span> ${nombreServicio}</p>
                            <p class="text-gray-600"><span class="font-semibold">Fecha actual:</span> ${new Date(fechaActual + 'T00:00:00').toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                        </div>
                    </div>
                    
                    <div class="mb-6">
                        <label class="block font-semibold text-gray-700 mb-2" for="motivoReprogramacion">
                            Motivo de la reprogramación <span class="text-red-500">*</span>
                        </label>
                        <textarea 
                            id="motivoReprogramacion" 
                            rows="4" 
                            class="w-full border-2 border-gray-300 rounded-xl p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-none"
                            placeholder="Por favor, explica por qué necesitas reprogramar tu cita..."></textarea>
                        <p class="text-xs text-gray-500 mt-2">Mínimo 20 caracteres</p>
                    </div>
                    
                    <div class="flex gap-3">
                        <button 
                            onclick="cerrarModalSolicitudReprogramacion()" 
                            class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-4 rounded-xl transition-all duration-200">
                            Cancelar
                        </button>
                        <button 
                            onclick="confirmarSolicitudReprogramacion(${idReserva})" 
                            class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl">
                            Enviar Solicitud
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function cerrarModalSolicitudReprogramacion() {
    const modal = document.getElementById('modalSolicitudReprogramacion');
    if (modal) {
        modal.classList.add('animate-fadeOut');
        setTimeout(() => modal.remove(), 300);
    }
}

async function confirmarSolicitudReprogramacion(idReserva) {
    const motivo = document.getElementById('motivoReprogramacion').value.trim();
    
    if (!motivo || motivo.length < 20) {
        alert('Por favor, proporciona un motivo detallado (mínimo 20 caracteres)');
        return;
    }
    
    try {
        const response = await fetch('/reservas/api/solicitar-reprogramacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_reserva: idReserva, motivo: motivo })
        });
        
        const data = await response.json();
        
        if (data.success) {
            cerrarModalSolicitudReprogramacion();
            alert('✅ Solicitud enviada correctamente. Te notificaremos cuando sea revisada.');
            cargarReservas(); // Recargar para actualizar el estado del botón
        } else {
            alert('❌ ' + (data.error || 'Error al enviar la solicitud'));
        }
    } catch (error) {
        console.error('Error al solicitar reprogramación:', error);
        alert('❌ Error de conexión al enviar la solicitud');
    }
}

// Función para abrir el modal de reprogramación (cuando ya está aprobada)
async function abrirModalReprogramar(idReserva, nombreServicio, fechaActual) {
    console.log('📅 Abriendo calendario de reprogramación para reserva:', idReserva);
    
    // Guardar datos en variables globales
    window.reservaReprogramar = {
        id: idReserva,
        servicio: nombreServicio,
        fechaActual: fechaActual
    };
    
    const modalHTML = `
        <div id="modalReprogramar" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
            <div class="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl transform animate-slideIn">
                <div class="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-t-2xl sticky top-0 z-10">
                    <div class="flex items-center justify-between">
                        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                            <span class="text-3xl">📅</span>
                            Reprogramar Cita
                        </h2>
                        <button onclick="cerrarModalReprogramar()" class="text-white hover:text-gray-200 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <div class="bg-green-50 border-l-4 border-green-500 p-4 mb-6 rounded-r-lg">
                        <div class="flex items-start gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-green-600 flex-shrink-0 mt-0.5">
                                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                            </svg>
                            <div>
                                <p class="text-sm font-semibold text-green-900 mb-1">✓ Solicitud Aprobada</p>
                                <p class="text-xs text-green-800">
                                    Tu solicitud de reprogramación fue aprobada. Selecciona una nueva fecha en el calendario.
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-4 bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold text-gray-700 mb-2">📋 Reserva Actual</h3>
                        <div class="space-y-1 text-sm">
                            <p class="text-gray-600"><span class="font-semibold">Servicio:</span> ${nombreServicio}</p>
                            <p class="text-gray-600"><span class="font-semibold">Fecha actual:</span> ${new Date(fechaActual + 'T00:00:00').toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                        </div>
                    </div>
                    
                    <div id="calendarioReprogramar"></div>
                    
                    <div id="detalleSeleccionReprogramar" class="mt-4 hidden">
                        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
                            <p class="text-sm font-semibold text-blue-900 mb-2">Nueva fecha seleccionada:</p>
                            <p id="textoSeleccionReprogramar" class="text-sm text-blue-800"></p>
                            <button 
                                onclick="confirmarReprogramacion()" 
                                class="mt-3 w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl">
                                ✓ Confirmar Reprogramación
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Inicializar el calendario con horarios disponibles (reutilizando lógica de nueva-cita)
    await inicializarCalendarioReprogramar(idReserva);
}

function cerrarModalReprogramar() {
    const modal = document.getElementById('modalReprogramar');
    if (modal) {
        modal.classList.add('animate-fadeOut');
        setTimeout(() => modal.remove(), 300);
    }
    window.reservaReprogramar = null;
    window.calendarioReprogramar = null;
}

async function inicializarCalendarioReprogramar(idReserva) {
    try {
        // Obtener horarios disponibles del mismo servicio
        const response = await fetch(`/reservas/api/horarios-disponibles-reserva/${idReserva}`);
        const data = await response.json();
        
        if (!data.success) {
            alert('❌ ' + (data.error || 'Error al cargar horarios'));
            return;
        }
        
        const eventos = data.horarios.map(horario => ({
            id: horario.id_programacion,
            title: horario.hora_inicio + ' - ' + horario.hora_fin,
            start: horario.fecha + 'T' + horario.hora_inicio,
            end: horario.fecha + 'T' + horario.hora_fin,
            extendedProps: {
                id_horario: horario.id_horario,
                id_servicio: horario.id_servicio,
                estado: horario.estado
            },
            backgroundColor: '#10b981',
            borderColor: '#059669'
        }));
        
        const calendarEl = document.getElementById('calendarioReprogramar');
        window.calendarioReprogramar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek'
            },
            events: eventos,
            eventClick: function(info) {
                window.programacionSeleccionadaReprogramar = info.event.id;
                const fechaHora = new Date(info.event.start);
                document.getElementById('textoSeleccionReprogramar').textContent = 
                    fechaHora.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) +
                    ' a las ' + fechaHora.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
                document.getElementById('detalleSeleccionReprogramar').classList.remove('hidden');
            },
            eventContent: function(arg) {
                return { html: `<div class="text-xs font-semibold">${arg.event.title}</div>` };
            }
        });
        
        window.calendarioReprogramar.render();
        
    } catch (error) {
        console.error('Error al inicializar calendario de reprogramación:', error);
        alert('❌ Error al cargar el calendario');
    }
}

async function confirmarReprogramacion() {
    if (!window.programacionSeleccionadaReprogramar || !window.reservaReprogramar) {
        alert('❌ Selecciona un horario primero');
        return;
    }
    
    try {
        const response = await fetch('/api/reprogramar-reserva', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_reserva: window.reservaReprogramar.id,
                nueva_programacion: window.programacionSeleccionadaReprogramar
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            cerrarModalReprogramar();
            alert('✅ ¡Cita reprogramada exitosamente!');
            cargarReservas(); // Recargar historial
        } else {
            alert('❌ ' + (data.error || 'Error al reprogramar'));
        }
    } catch (error) {
        console.error('Error al confirmar reprogramación:', error);
        alert('❌ Error de conexión');
    }
}

// Función para solicitar cancelación
async function solicitarCancelacion(idReserva, nombreServicio, fechaActual) {
    console.log('❌ Solicitando cancelación para reserva:', idReserva);
    const modalHTML = `
        <div id="modalSolicitudCancelacion" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
            <div class="bg-white rounded-2xl max-w-lg w-full shadow-2xl transform animate-slideIn">
                <div class="bg-gradient-to-r from-red-500 to-red-600 p-6 rounded-t-2xl">
                    <div class="flex items-center justify-between">
                        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                            <span class="text-3xl">⚠️</span>
                            Solicitar Cancelación
                        </h2>
                        <button onclick="cerrarModalSolicitudCancelacion()" class="text-white hover:text-gray-200 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6 rounded-r-lg">
                        <div class="flex items-start gap-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-amber-600 flex-shrink-0 mt-0.5">
                                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                                <path d="M12 9v4"/><path d="M12 17h.01"/>
                            </svg>
                            <div>
                                <p class="text-sm font-semibold text-amber-900 mb-1">¿Consideraste reprogramar?</p>
                                <p class="text-xs text-amber-800">
                                    Antes de cancelar, recuerda que puedes reprogramar tu cita para otra fecha. Es más rápido y mantienes tu reserva.
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-6 bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                                <polyline points="14 2 14 8 20 8"/>
                            </svg>
                            Detalles de tu Reserva
                        </h3>
                        <div class="space-y-2 text-sm">
                            <p class="text-gray-600"><span class="font-semibold">Servicio:</span> ${nombreServicio}</p>
                            <p class="text-gray-600"><span class="font-semibold">Fecha:</span> ${new Date(fechaActual + 'T00:00:00').toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                        </div>
                    </div>
                    
                    <div class="mb-6">
                        <label class="block font-semibold text-gray-700 mb-2" for="motivoCancelacion">
                            Motivo de la cancelación <span class="text-red-500">*</span>
                        </label>
                        <textarea 
                            id="motivoCancelacion" 
                            rows="4" 
                            class="w-full border-2 border-gray-300 rounded-xl p-3 focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all resize-none"
                            placeholder="Explica por qué necesitas cancelar tu cita (mínimo 20 caracteres)..."
                            maxlength="500"
                        ></textarea>
                        <p class="text-xs text-gray-500 mt-2 flex items-center justify-between">
                            <span id="contadorCancel">0/20 caracteres mínimos</span>
                            <span><span id="contadorCaracteresCancel">0</span>/500</span>
                        </p>
                    </div>
                </div>
                
                <div class="p-6 bg-gray-50 rounded-b-2xl border-t border-gray-200 flex gap-3">
                    <button onclick="cerrarModalSolicitudCancelacion()" 
                            class="flex-1 bg-white border-2 border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all">
                        Volver
                    </button>
                    <button onclick="confirmarSolicitudCancelacion(${idReserva})" 
                            class="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-red-600 hover:to-red-700 transition-all shadow-lg hover:shadow-xl">
                        Enviar Solicitud
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Contador de caracteres
    document.getElementById('motivoCancelacion').addEventListener('input', function() {
        const contador = document.getElementById('contadorCaracteresCancel');
        const contadorMin = document.getElementById('contadorCancel');
        const longitud = this.value.length;
        contador.textContent = longitud;
        
        if (longitud < 20) {
            contadorMin.textContent = `${longitud}/20 caracteres mínimos`;
            contadorMin.classList.add('text-red-500');
            contadorMin.classList.remove('text-green-600');
        } else {
            contadorMin.textContent = '✓ Mínimo alcanzado';
            contadorMin.classList.remove('text-red-500');
            contadorMin.classList.add('text-green-600');
        }
    });
}

function cerrarModalSolicitudCancelacion() {
    const modal = document.getElementById('modalSolicitudCancelacion');
    if (modal) {
        modal.remove();
    }
}

async function confirmarSolicitudCancelacion(idReserva) {
    const motivo = document.getElementById('motivoCancelacion').value.trim();
    
    console.log(`📝 Confirmando cancelación: ID=${idReserva}, Motivo length=${motivo.length}`);
    
    if (motivo.length < 20) {
        alert('❌ El motivo debe tener al menos 20 caracteres.');
        return;
    }
    
    try {
        const payload = {
            id_reserva: idReserva,
            motivo: motivo
        };
        console.log('📤 Enviando payload:', payload);
        
        const response = await fetch('/reservas/api/solicitar-cancelacion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        console.log('📥 Response status:', response.status);
        const data = await response.json();
        console.log('📥 Response data:', data);
        
        if (data.success) {
            cerrarModalSolicitudCancelacion();
            mostrarNotificacionExito('✅ Solicitud Enviada', 'Tu solicitud de cancelación ha sido enviada. Recibirás una respuesta pronto.');
            cargarReservas();
        } else {
            alert('❌ Error: ' + (data.error || 'No se pudo enviar la solicitud'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al enviar la solicitud. Intenta nuevamente.');
    }
}

// Función auxiliar para mostrar notificaciones de éxito
function mostrarNotificacionExito(titulo, mensaje) {
    const notifHTML = `
        <div id="notificacionExito" class="fixed top-4 right-4 bg-white rounded-xl shadow-2xl p-6 max-w-md z-[9999] animate-slideIn border-l-4 border-green-500">
            <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="text-green-600">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                </div>
                <div class="flex-1">
                    <h3 class="font-bold text-gray-900 mb-1">${titulo}</h3>
                    <p class="text-sm text-gray-600">${mensaje}</p>
                </div>
                <button onclick="document.getElementById('notificacionExito').remove()" class="text-gray-400 hover:text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', notifHTML);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        const notif = document.getElementById('notificacionExito');
        if (notif) {
            notif.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notif.remove(), 300);
        }
    }, 5000);
}

// ==================== FUNCIONES PARA VER DETALLE DE CITA ====================

async function verDetalleCitaOperacion(idReserva, idCita) {
    try {
        const response = await fetch(`/reservas/api/paciente/mis-reservas`);
        const data = await response.json();
        
        if (data.error) {
            alert('❌ Error al cargar los datos');
            return;
        }
        
        // Buscar la reserva y la cita
        const reserva = data.reservas.find(r => r.citas && r.citas.some(c => c.id_cita === idCita));
        
        if (!reserva || !reserva.citas || reserva.citas.length === 0) {
            alert('❌ No se encontró la cita médica asociada');
            return;
        }
        
        const cita = reserva.citas.find(c => c.id_cita === idCita);
        mostrarModalDetalleCita(cita, reserva, 'OPERACION');
        
    } catch (error) {
        console.error('Error al cargar detalle de cita:', error);
        alert('❌ Error al cargar el detalle de la cita');
    }
}

async function verDetalleCitaExamen(idReserva) {
    try {
        const response = await fetch(`/reservas/api/paciente/mis-reservas`);
        const data = await response.json();
        
        if (data.error) {
            alert('❌ Error al cargar los datos');
            return;
        }
        
        // Buscar la reserva original (la cita médica)
        const reservaExamen = data.reservas.find(r => r.id_reserva === idReserva);
        
        if (!reservaExamen || !reservaExamen.examenes || reservaExamen.examenes.length === 0) {
            alert('❌ No se encontró información de la cita médica asociada');
            return;
        }
        
        // Buscar la cita completada que generó este examen
        const citaRelacionada = data.reservas.find(r => 
            r.tipo === 1 && 
            r.citas && 
            r.citas.length > 0 && 
            r.citas[0].estado === 'Completada' &&
            r.estado_reserva === 'Completada'
        );
        
        if (citaRelacionada && citaRelacionada.citas && citaRelacionada.citas.length > 0) {
            mostrarModalDetalleCita(citaRelacionada.citas[0], citaRelacionada, 'EXAMEN');
        } else {
            alert('ℹ️ Este examen fue autorizado por el médico durante una consulta previa');
        }
        
    } catch (error) {
        console.error('Error al cargar detalle de cita:', error);
        alert('❌ Error al cargar el detalle de la cita');
    }
}

function mostrarModalDetalleCita(cita, reserva, tipoProcedimiento) {
    const fechaCita = new Date(cita.fecha_cita + 'T00:00:00').toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    const modalHTML = `
        <div id="modalDetalleCita" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
            <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl transform animate-slideIn">
                <div class="bg-gradient-to-r from-cyan-500 to-blue-500 p-6 rounded-t-2xl sticky top-0 z-10">
                    <div class="flex items-center justify-between">
                        <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                            <span class="text-3xl">🩺</span>
                            Detalle de Cita Médica
                        </h2>
                        <button onclick="cerrarModalDetalleCita()" class="text-white hover:text-gray-200 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-r-lg">
                        <p class="text-sm text-blue-800">
                            <strong>📌 Información:</strong> Esta cita médica generó la autorización para el ${tipoProcedimiento === 'OPERACION' ? 'procedimiento quirúrgico' : 'examen de laboratorio'}.
                        </p>
                    </div>
                    
                    <!-- Información de la cita -->
                    <div class="space-y-4">
                        <div class="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl p-4">
                            <h3 class="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan-600">
                                    <rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>
                                </svg>
                                Datos de la Consulta
                            </h3>
                            <div class="grid md:grid-cols-2 gap-3 text-sm">
                                <div>
                                    <p class="text-gray-600 font-semibold">Fecha:</p>
                                    <p class="text-gray-800">${fechaCita}</p>
                                </div>
                                <div>
                                    <p class="text-gray-600 font-semibold">Horario:</p>
                                    <p class="text-gray-800">${cita.hora_inicio} - ${cita.hora_fin}</p>
                                </div>
                                <div>
                                    <p class="text-gray-600 font-semibold">Servicio:</p>
                                    <p class="text-gray-800">${reserva.servicio || 'Consulta Médica'}</p>
                                </div>
                                <div>
                                    <p class="text-gray-600 font-semibold">Médico:</p>
                                    <p class="text-gray-800">${reserva.medico_nombres ? 'Dr(a). ' + reserva.medico_nombres + ' ' + reserva.medico_apellidos : 'No especificado'}</p>
                                </div>
                                ${reserva.especialidad ? `
                                <div class="col-span-2">
                                    <p class="text-gray-600 font-semibold">Especialidad:</p>
                                    <p class="text-gray-800">${reserva.especialidad}</p>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        ${cita.diagnostico ? `
                        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
                            <h3 class="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-green-600">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
                                    <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
                                </svg>
                                Diagnóstico
                            </h3>
                            <p class="text-gray-700 text-sm whitespace-pre-wrap">${cita.diagnostico}</p>
                        </div>
                        ` : ''}
                        
                        ${cita.observaciones ? `
                        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r-lg">
                            <h3 class="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-yellow-600">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
                                </svg>
                                Observaciones
                            </h3>
                            <p class="text-gray-700 text-sm whitespace-pre-wrap">${cita.observaciones}</p>
                        </div>
                        ` : ''}
                        
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <p class="text-sm text-gray-600">
                                <span class="font-semibold">Estado de la cita:</span> 
                                <span class="px-3 py-1 rounded-full text-xs font-semibold ${cita.estado === 'Completada' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}">
                                    ${cita.estado}
                                </span>
                            </p>
                        </div>
                    </div>
                </div>
                
                <div class="p-6 bg-gray-50 rounded-b-2xl border-t border-gray-200">
                    <button onclick="cerrarModalDetalleCita()" 
                            class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold py-3 px-6 rounded-xl hover:from-cyan-600 hover:to-blue-600 transition-all shadow-lg hover:shadow-xl">
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function cerrarModalDetalleCita() {
    const modal = document.getElementById('modalDetalleCita');
    if (modal) {
        modal.remove();
    }
}

