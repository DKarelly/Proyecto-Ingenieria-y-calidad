// reprogramar-reserva.js - Lógica del submódulo de reprogramación de reservas
(function() {
  'use strict';

let solicitudes = [];
let solicitudSeleccionada = null;
let programacionSeleccionada = null;

// Scope helpers: limit selectors to the reprogramar submodule container
function rrRoot() {
  const cont = document.getElementById('mod-reprogramar');
  return cont ? cont : document;
}
function rr$(id) {
  return rrRoot().querySelector('#' + id);
}

// Inicialización y manejo de submódulos
function initSubmodulos() {
  const btnReprogramar = document.getElementById('btn-mod-reprogramar');
  const btnCancelaciones = document.getElementById('btn-mod-cancelaciones');
  const modReprogramar = document.getElementById('mod-reprogramar');
  const modCancelaciones = document.getElementById('mod-cancelaciones');

  if (!btnReprogramar || !btnCancelaciones || !modReprogramar || !modCancelaciones) return;

  btnReprogramar.addEventListener('click', () => {
    console.log('➡️ Cambiando a submódulo: Reprogramar Reserva');
    modReprogramar.classList.remove('hidden');
    modCancelaciones.classList.add('hidden');
    btnReprogramar.classList.add('bg-cyan-600','text-white');
    btnReprogramar.classList.remove('bg-gray-200','text-gray-800');
    btnCancelaciones.classList.add('bg-gray-200','text-gray-800');
    btnCancelaciones.classList.remove('bg-cyan-600','text-white');
    cargarSolicitudes();
  });

  btnCancelaciones.addEventListener('click', () => {
    console.log('➡️ Cambiando a submódulo: Gestionar Cancelaciones');
    modReprogramar.classList.add('hidden');
    modCancelaciones.classList.remove('hidden');
    btnCancelaciones.classList.add('bg-cyan-600','text-white');
    btnCancelaciones.classList.remove('bg-gray-200','text-gray-800');
    btnReprogramar.classList.add('bg-gray-200','text-gray-800');
    btnReprogramar.classList.remove('bg-cyan-600','text-white');
    // Asegurar que el contenedor aparezca en viewport
    modCancelaciones.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

// Carga de solicitudes de reprogramación
async function cargarSolicitudes() {
  console.log('🔄 Cargando solicitudes de reprogramación...');
  const loadingEl = rr$('loading');
  const sinResultadosEl = rr$('sin-resultados');
  const tablaContainerEl = rr$('tabla-container');

  if (loadingEl) loadingEl.classList.remove('hidden');
  if (sinResultadosEl) sinResultadosEl.classList.add('hidden');
  if (tablaContainerEl) tablaContainerEl.classList.add('hidden');

  try {
    const resp = await fetch('/reservas/api/solicitudes-reprogramacion');
    const data = await resp.json();

    console.log('📥 Respuesta del servidor:', data);

    if (!resp.ok) throw new Error(data.error || 'Error al cargar solicitudes');

    // Las solicitudes de reprogramación ya vienen filtradas desde el backend
    // (nueva_programacion_id IS NOT NULL), pero añadimos filtro defensivo
    solicitudes = (data.solicitudes || []).filter(s => s.estado === 'Pendiente');
    console.log(`📋 Total de solicitudes de reprogramación recibidas: ${solicitudes.length}`);
    console.log('🔍 Datos completos de reprogramación:', solicitudes.map(s => ({
      id: s.id_solicitud,
      nueva_prog_id: s.nueva_programacion_id,
      tipo: s.tipo,
      estado: s.estado_solicitud
    })));

    mostrarSolicitudes();
    cargarEstadisticas();
    if (solicitudes.length > 0) {
      const tablaContainerEl = rr$('tabla-container');
      const sinResultadosEl = rr$('sin-resultados');
      if (tablaContainerEl) tablaContainerEl.classList.remove('hidden');
      if (sinResultadosEl) sinResultadosEl.classList.add('hidden');
    }
  } catch (err) {
    console.error('❌ Error:', err);
    mostrarNotificacion('Error al cargar solicitudes', 'error');
    if (loadingEl) loadingEl.classList.add('hidden');
    if (sinResultadosEl) sinResultadosEl.classList.remove('hidden');
  }
}

// Estadísticas
async function cargarEstadisticas() {
  try {
    const resp = await fetch('/reservas/api/estadisticas-reprogramacion');
    const data = await resp.json();

    if (resp.ok) {
      const pendEl = rr$('total-pendientes');
      const rehoyEl = rr$('total-reprogramadas');
      if (pendEl) pendEl.textContent = data.pendientes || 0;
      if (rehoyEl) rehoyEl.textContent = data.reprogramadas_hoy || 0;
    }
  } catch (err) {
    console.error('Error al cargar estadísticas:', err);
  }
}

// Render de solicitudes
function mostrarSolicitudes() {
  const loadingEl = rr$('loading');
  if (loadingEl) loadingEl.classList.add('hidden');

  const sinResultadosEl = rr$('sin-resultados');
  if (solicitudes.length === 0) {
    if (sinResultadosEl) sinResultadosEl.classList.remove('hidden');
    return;
  }

  if (sinResultadosEl) sinResultadosEl.classList.add('hidden');
  const tablaContainerEl = rr$('tabla-container');
  if (tablaContainerEl) tablaContainerEl.classList.remove('hidden');

  const tbody = rr$('tabla-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  solicitudes.forEach(sol => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50 transition-colors';

    const fechaSolicitud = new Date(sol.fecha_solicitud);
    const fechaFormateada = fechaSolicitud.toLocaleDateString('es-ES', {
      day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    const fechaCita = new Date(sol.fecha_actual + 'T00:00:00');
    const fechaCitaFormateada = fechaCita.toLocaleDateString('es-ES', {
      weekday: 'short', day: '2-digit', month: 'short'
    });

    const maxReprog = sol.num_reprogramaciones >= 2;
    const badgeReprog = maxReprog ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800';

    tr.innerHTML = `
      <td class="px-6 py-4">
        <div class="text-sm font-mono text-gray-900">#${sol.id_solicitud}</div>
        <div class="text-xs text-gray-500">${fechaFormateada}</div>
      </td>
      <td class="px-6 py-4">
        <div class="text-sm font-medium text-gray-900">${sol.paciente_nombre}</div>
        <div class="text-xs text-gray-500">${sol.paciente_dni}</div>
      </td>
      <td class="px-6 py-4">
        <div class="text-sm text-gray-900">${sol.servicio_nombre}</div>
        ${sol.medico_nombre ? `<div class="text-xs text-gray-500">${sol.medico_nombre}</div>` : ''}
      </td>
      <td class="px-6 py-4">
        <div class="text-sm text-gray-900">${fechaCitaFormateada}</div>
        <div class="text-xs text-gray-500">${sol.hora_inicio_actual} - ${sol.hora_fin_actual}</div>
      </td>
      <td class="px-6 py-4">
        <div class="text-sm text-gray-700 max-w-xs truncate" title="${sol.motivo}">${sol.motivo}</div>
      </td>
      <td class="px-6 py-4">
        <span class="px-3 py-1 rounded-full text-xs font-semibold ${badgeReprog}">${sol.num_reprogramaciones} / 2</span>
      </td>
      <td class="px-6 py-4 whitespace-nowrap">
        <button onclick="abrirModalAprobar(${sol.id_solicitud})" class="text-green-600 hover:text-green-800 font-medium mr-3" ${maxReprog ? 'disabled title="Máximo de reprogramaciones alcanzado"' : ''}>
          <i class="fas fa-check mr-1"></i>Aprobar
        </button>
        <button onclick="abrirModalRechazar(${sol.id_solicitud})" class="text-red-600 hover:text-red-800 font-medium">
          <i class="fas fa-times mr-1"></i>Rechazar
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// Modales
function abrirModalAprobar(idSolicitud) {
  solicitudSeleccionada = solicitudes.find(s => s.id_solicitud === idSolicitud);
  if (!solicitudSeleccionada) return;
  rr$('modal-paciente').textContent = solicitudSeleccionada.paciente_nombre;
  rr$('modal-dni').textContent = solicitudSeleccionada.paciente_dni;
  rr$('modal-servicio').textContent = solicitudSeleccionada.servicio_nombre;
  rr$('modal-medico').textContent = solicitudSeleccionada.medico_nombre || '-';
  rr$('modal-fecha-actual').textContent = `${solicitudSeleccionada.fecha_actual} ${solicitudSeleccionada.hora_inicio_actual}-${solicitudSeleccionada.hora_fin_actual}`;
  rr$('modal-reprogramaciones').textContent = solicitudSeleccionada.num_reprogramaciones;
  rr$('modal-motivo').textContent = solicitudSeleccionada.motivo;

  programacionSeleccionada = null;
  const btnConfirm = rr$('btn-confirmar-aprobar'); if (btnConfirm) btnConfirm.disabled = true;
  const horariosCont = rr$('horarios-container'); if (horariosCont) horariosCont.innerHTML = '';
  const horariosEmpty = rr$('horarios-sin-resultados'); if (horariosEmpty) horariosEmpty.classList.add('hidden');

  const modalApr = rr$('modal-aprobar'); if (modalApr) modalApr.classList.remove('hidden');
}

function cerrarModalAprobar() {
  const modalApr = rr$('modal-aprobar'); if (modalApr) modalApr.classList.add('hidden');
  solicitudSeleccionada = null;
  programacionSeleccionada = null;
}

async function buscarHorariosDisponibles() {
  const fechaEl = rr$('modal-fecha');
  const fecha = fechaEl ? fechaEl.value : '';
  if (!fecha) {
    mostrarNotificacion('Selecciona una fecha', 'error');
    return;
  }

  const container = rr$('horarios-container');
  const loading = rr$('horarios-loading');
  const sinResultados = rr$('horarios-sin-resultados');

  container.innerHTML = '';
  container.classList.add('hidden');
  sinResultados.classList.add('hidden');
  loading.classList.remove('hidden');

  try {
    const resp = await fetch(`/reservas/api/buscar-horarios-disponibles?fecha=${fecha}`);
    const data = await resp.json();

    loading.classList.add('hidden');

    if (!data.horarios || data.horarios.length === 0) {
      sinResultados.classList.remove('hidden');
      return;
    }

    container.classList.remove('hidden');
    data.horarios.forEach(horario => {
      const card = document.createElement('div');
      card.className = 'border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-cyan-500 transition-all';
      card.onclick = () => seleccionarHorario(horario.id_programacion, card);

      const fechaObj = new Date(horario.fecha + 'T00:00:00');
      const fechaStr = fechaObj.toLocaleDateString('es-ES', { weekday: 'short', day: '2-digit', month: 'short' });

      card.innerHTML = `
        <div class="text-center">
          <p class="text-sm font-semibold text-gray-700">${fechaStr}</p>
          <p class="text-lg font-bold text-cyan-600">${horario.hora_inicio} - ${horario.hora_fin}</p>
          <p class="text-xs text-gray-500 mt-1">${horario.profesional}</p>
          ${horario.especialidad ? `<p class=\"text-xs text-gray-400\">${horario.especialidad}</p>` : ''}
        </div>
      `;

      container.appendChild(card);
    });
  } catch (err) {
    console.error('Error:', err);
    loading.classList.add('hidden');
    sinResultados.classList.remove('hidden');
    mostrarNotificacion('Error al buscar horarios', 'error');
  }
}

function seleccionarHorario(idProgramacion, cardElement) {
  rrRoot().querySelectorAll('#horarios-container > div').forEach(c => {
    c.classList.remove('border-cyan-500', 'bg-cyan-50');
    c.classList.add('border-gray-200');
  });

  cardElement.classList.remove('border-gray-200');
  cardElement.classList.add('border-cyan-500', 'bg-cyan-50');

  programacionSeleccionada = idProgramacion;
  const btn = rr$('btn-confirmar-aprobar');
  if (btn) btn.disabled = false;
}

async function confirmarAprobar() {
  if (!programacionSeleccionada) {
    mostrarNotificacion('Selecciona un horario', 'error');
    return;
  }

  const respuestaEl = rr$('modal-respuesta');
  const respuesta = ((respuestaEl ? respuestaEl.value : '') || '').trim() || 'Solicitud aprobada';

  const btn = rr$('btn-confirmar-aprobar');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Procesando...';
  }

  try {
    const resp = await fetch('/reservas/api/aprobar-reprogramacion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_solicitud: solicitudSeleccionada.id_solicitud,
        id_programacion: programacionSeleccionada,
        respuesta: respuesta
      })
    });

    const data = await resp.json();

    if (!resp.ok) throw new Error(data.error || 'Error al aprobar');

    mostrarNotificacion('Reprogramación aprobada exitosamente', 'success');
    cerrarModalAprobar();
    cargarSolicitudes();
  } catch (err) {
    console.error('Error:', err);
    mostrarNotificacion(err.message, 'error');
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-check mr-2"></i>Aprobar Reprogramación';
    }
  }
}

function abrirModalRechazar(idSolicitud) {
  solicitudSeleccionada = solicitudes.find(s => s.id_solicitud === idSolicitud);
  if (!solicitudSeleccionada) return;
  const input = rr$('rechazar-respuesta');
  if (input) input.value = '';
  const modal = rr$('modal-rechazar');
  if (modal) modal.classList.remove('hidden');
}

function cerrarModalRechazar() {
  const modal = rr$('modal-rechazar');
  if (modal) modal.classList.add('hidden');
  solicitudSeleccionada = null;
}

async function confirmarRechazar() {
  const respuestaEl = rr$('rechazar-respuesta');
  const respuesta = (respuestaEl ? respuestaEl.value : '').trim();
  if (!respuesta) {
    mostrarNotificacion('Debes indicar el motivo del rechazo', 'error');
    return;
  }

  try {
    const resp = await fetch('/reservas/api/rechazar-reprogramacion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_solicitud: solicitudSeleccionada.id_solicitud, respuesta })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Error al rechazar');
    mostrarNotificacion('Solicitud rechazada', 'success');
    cerrarModalRechazar();
    cargarSolicitudes();
  } catch (err) {
    console.error('Error:', err);
    mostrarNotificacion(err.message, 'error');
  }
}

function mostrarNotificacion(mensaje, tipo) {
  const toast = document.createElement('div');
  const bgColor = tipo === 'success' ? 'bg-green-500' : tipo === 'error' ? 'bg-red-500' : 'bg-blue-500';
  const icon = tipo === 'success' ? 'fa-check-circle' : tipo === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';

  toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center animate-fade-in`;
  toast.innerHTML = `
    <i class="fas ${icon} mr-2"></i>
    <span>${mensaje}</span>
  `;

  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initSubmodulos();
  cargarSolicitudes();
  cargarEstadisticas();
});

})(); // End IIFE
