// gestion-cancelaciones.js - Gestión de solicitudes de cancelación para trabajadores

let solicitudesData = [];
let solicitudActual = null;

document.addEventListener('DOMContentLoaded', function() {
    cargarSolicitudes();

    // Event listeners para filtros
    document.getElementById('filtroEstado').addEventListener('change', aplicarFiltros);
    document.getElementById('filtroTipo').addEventListener('change', aplicarFiltros);
    document.getElementById('filtroFechaDesde').addEventListener('change', aplicarFiltros);
    document.getElementById('filtroFechaHasta').addEventListener('change', aplicarFiltros);
    document.getElementById('btnLimpiarFiltros').addEventListener('click', limpiarFiltros);

    // Event listeners para el modal
    document.getElementById('btnCancelarComentario').addEventListener('click', function() {
        document.getElementById('comentarioModal').classList.add('hidden');
        solicitudActual = null;
    });

    document.getElementById('btnConfirmarComentario').addEventListener('click', async function() {
        if (!solicitudActual) return;

        const comentario = document.getElementById('comentarioTextarea').value.trim();

        try {
            const response = await fetch('/reservas/api/trabajador/procesar-cancelacion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id_reserva: solicitudActual.idReserva,
                    estado_cancelacion: solicitudActual.nuevoEstado,
                    comentario: comentario
                })
            });

            const data = await response.json();

            if (data.success) {
                alert('✅ ' + data.message);
                cargarSolicitudes(); // Recargar la lista
            } else {
                alert('❌ Error: ' + data.error);
            }
        } catch (error) {
            console.error('💥 Error:', error);
            alert('❌ Error al procesar la solicitud. Intenta nuevamente.');
        }

        document.getElementById('comentarioModal').classList.add('hidden');
        solicitudActual = null;
    });
});

async function cargarSolicitudes() {
    try {
        const response = await fetch('/reservas/api/trabajador/solicitudes-cancelacion');
        const data = await response.json();

        if (data.error) {
            mostrarError(data.error);
            return;
        }

        solicitudesData = data.solicitudes || [];
        
        // Ordenar por fecha de solicitud (más reciente primero)
        solicitudesData.sort((a, b) => {
            const fechaA = new Date(a.fecha_solicitud || 0);
            const fechaB = new Date(b.fecha_solicitud || 0);
            return fechaB - fechaA;
        });
        
        mostrarSolicitudes(solicitudesData);

    } catch (error) {
        console.error('Error al cargar solicitudes:', error);
        mostrarError('Error al cargar las solicitudes. Por favor, intenta nuevamente.');
    }
}

function mostrarSolicitudes(solicitudes) {
    const container = document.getElementById('solicitudesContainer');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const contadorResultados = document.getElementById('contadorResultados');

    loadingState.classList.add('hidden');

    if (!solicitudes || solicitudes.length === 0) {
        container.classList.add('hidden');
        emptyState.classList.remove('hidden');
        contadorResultados.textContent = 'Mostrando 0 solicitudes';
        return;
    }

    emptyState.classList.add('hidden');
    container.classList.remove('hidden');
    contadorResultados.textContent = `Mostrando ${solicitudes.length} solicitud${solicitudes.length !== 1 ? 'es' : ''}`;

    container.innerHTML = solicitudes.map(solicitud => {
        const fechaSolicitud = new Date(solicitud.fecha_solicitud);
        const fechaSolicitudStr = fechaSolicitud.toLocaleString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const fechaReserva = new Date(solicitud.fecha_programacion);
        const fechaReservaStr = fechaReserva.toLocaleDateString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const tipoInfo = getTipoInfo(solicitud.tipo);
        const estadoClass = `status-${solicitud.estado || 'Pendiente'}`;

        return `
            <div class="bg-white rounded-xl shadow-md overflow-hidden border-2 ${solicitud.estado === 'Pendiente' ? 'border-yellow-400' : 'border-gray-200'} hover:shadow-lg transition-all">
                <div class="p-6">
                    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-4">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-3">
                                <span class="status-badge ${estadoClass}">${solicitud.estado || 'Pendiente'}</span>
                                <span class="px-3 py-1 rounded-full text-xs font-semibold ${tipoInfo.color}">${tipoInfo.icono} ${tipoInfo.texto}</span>
                            </div>
                            
                            <h3 class="text-xl font-bold text-gray-900 mb-2">${solicitud.servicio}</h3>
                            <p class="text-gray-600 mb-1">${solicitud.especialidad || 'Consulta General'}</p>
                            
                            <div class="mt-3 space-y-2">
                                <p class="text-sm text-gray-700">
                                    <strong>Paciente:</strong> ${solicitud.paciente_nombres} ${solicitud.paciente_apellidos}
                                </p>
                                <p class="text-sm text-gray-700">
                                    <strong>DNI:</strong> ${solicitud.paciente_dni}
                                </p>
                                <p class="text-sm text-gray-700">
                                    <strong>Fecha de reserva:</strong> ${fechaReservaStr}
                                </p>
                                <p class="text-sm text-gray-700">
                                    <strong>Horario:</strong> ${solicitud.hora_inicio} - ${solicitud.hora_fin}
                                </p>
                                <p class="text-sm text-gray-700">
                                    <strong>Solicitud realizada:</strong> ${fechaSolicitudStr}
                                </p>
                            </div>
                        </div>
                        
                        <div class="lg:w-1/3">
                            <div class="bg-gray-50 rounded-lg p-4 border-l-4 border-yellow-500">
                                <p class="text-xs font-semibold text-gray-600 mb-2">MOTIVO DE CANCELACIÓN:</p>
                                <p class="text-sm text-gray-800">${solicitud.motivo}</p>
                            </div>
                        </div>
                    </div>

                    ${solicitud.estado === 'Pendiente' ? `
                        <div class="pt-4 border-t border-gray-200 flex gap-3">
                            <button onclick="procesarSolicitud(${solicitud.id_reserva}, 'Rechazada')" 
                                    class="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-red-600 hover:to-red-700 transition-all flex items-center justify-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                                </svg>
                                Rechazar Solicitud
                            </button>
                            <button onclick="procesarSolicitud(${solicitud.id_reserva}, 'Aprobada')"
                                    class="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:from-green-600 hover:to-green-700 transition-all flex items-center justify-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="20 6 9 17 4 12"/>
                                </svg>
                                Aprobar Cancelación
                            </button>
                        </div>
                    ` : `
                        <div class="pt-4 border-t border-gray-200">
                            <p class="text-sm text-gray-600">
                                ${solicitud.estado === 'Aprobada' ? '✅ Esta solicitud fue aprobada y la reserva está cancelada.' : '❌ Esta solicitud fue rechazada y la reserva sigue activa.'}
                            </p>
                            ${solicitud.respuesta ? `<p class="text-sm text-gray-500 mt-2"><strong>Respuesta:</strong> ${solicitud.respuesta}</p>` : ''}
                        </div>
                    `}
                </div>
            </div>
        `;
    }).join('');
}

function getTipoInfo(tipo) {
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

function aplicarFiltros() {
    const estado = document.getElementById('filtroEstado').value;
    const tipo = document.getElementById('filtroTipo').value;
    const fechaDesde = document.getElementById('filtroFechaDesde').value;
    const fechaHasta = document.getElementById('filtroFechaHasta').value;

    let solicitudesFiltradas = [...solicitudesData];

    if (estado) {
        solicitudesFiltradas = solicitudesFiltradas.filter(s =>
            (s.estado || 'Pendiente') === estado
        );
    }

    if (tipo) {
        solicitudesFiltradas = solicitudesFiltradas.filter(s => s.tipo == tipo);
    }

    if (fechaDesde) {
        solicitudesFiltradas = solicitudesFiltradas.filter(s => {
            const fechaSolicitud = new Date(s.fecha_solicitud);
            return fechaSolicitud >= new Date(fechaDesde);
        });
    }

    if (fechaHasta) {
        solicitudesFiltradas = solicitudesFiltradas.filter(s => {
            const fechaSolicitud = new Date(s.fecha_solicitud);
            return fechaSolicitud <= new Date(fechaHasta + 'T23:59:59');
        });
    }

    mostrarSolicitudes(solicitudesFiltradas);
}

function limpiarFiltros() {
    document.getElementById('filtroEstado').value = 'Pendiente';
    document.getElementById('filtroTipo').value = '';
    document.getElementById('filtroFechaDesde').value = '';
    document.getElementById('filtroFechaHasta').value = '';
    aplicarFiltros();
}

async function procesarSolicitud(idReserva, nuevoEstado) {
    console.log('📤 Procesando solicitud:', { idReserva, nuevoEstado });

    if (!idReserva) {
        console.error('❌ ID de reserva no válido');
        alert('Error: ID de reserva no válido');
        return;
    }

    solicitudActual = { idReserva, nuevoEstado };
    const accion = nuevoEstado === 'Aprobada' ? 'aprobar' : 'rechazar';
    document.getElementById('modalTitle').textContent = `¿${accion.charAt(0).toUpperCase() + accion.slice(1)} solicitud?`;
    document.getElementById('comentarioTextarea').value = '';
    document.getElementById('comentarioModal').classList.remove('hidden');
}

function mostrarError(mensaje) {
    const container = document.getElementById('solicitudesContainer');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');

    loadingState.classList.add('hidden');
    container.classList.add('hidden');
    emptyState.classList.remove('hidden');

    emptyState.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="mx-auto text-red-300 mb-4">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h3 class="text-xl font-semibold text-gray-800 mb-2">Error al cargar</h3>
        <p class="text-gray-600 mb-6">${mensaje}</p>
        <button onclick="cargarSolicitudes()" class="bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all">
            Intentar Nuevamente
        </button>
    `;
}