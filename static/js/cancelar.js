(function() {
  'use strict';

let solicitudes = [];
let solicitudSeleccionada = null;
// Cuando está incrustado en ReprogramarReserva, limitamos el alcance al contenedor del submódulo
function getRoot() {
  const cont = document.getElementById('mod-cancelaciones');
  return cont ? cont : document;
}
function getEl(id) {
  // Primero buscar en el scope del submódulo si existe
  const cont = document.getElementById('mod-cancelaciones');
  if (cont) {
    const el = cont.querySelector('#' + id);
    if (el) return el;
  }
  // Fallback: buscar globalmente
  return document.getElementById(id);
}

// Permite inicialización manual desde otras vistas (submódulos)
window.cancelacionesInit = function() {
  try {
    cargarSolicitudes();
    cargarEstadisticas();
  } catch (e) { console.error('Error al inicializar cancelaciones:', e); }
};

// Inicialización automática solo si los elementos existen en el DOM principal
document.addEventListener('DOMContentLoaded', () => {
  const tablaContainer = getEl('tabla-container');
  const loading = getEl('loading');
  if (tablaContainer && loading) {
    window.cancelacionesInit();
  }
});

async function cargarSolicitudes() {
  const loading = getEl('loading');
  const sinResultados = getEl('sin-resultados');
  const tablaContainer = getEl('tabla-container');
  if (loading) loading.classList.remove('hidden');
  if (sinResultados) sinResultados.classList.add('hidden');
  if (tablaContainer) tablaContainer.classList.add('hidden');

  try {
    console.log('🔄 Cargando solicitudes de cancelación...');
    const resp = await fetch('/reservas/api/trabajador/solicitudes-cancelacion');
    const data = await resp.json();
    console.log('📥 Respuesta del servidor:', data);
    if (!resp.ok) throw new Error(data.error || 'Error al cargar solicitudes');
    console.log('📋 Total de solicitudes recibidas:', data.solicitudes ? data.solicitudes.length : 0);
    
    // TEMPORAL: Mostrar TODAS las solicitudes para debug
    const todasSolicitudes = data.solicitudes || [];
    console.log('🔍 TODAS las cancelaciones (sin filtrar):', todasSolicitudes.map(s => ({
      id: s.id_solicitud,
      estado: s.estado,
      nueva_prog_id: s.nueva_programacion_id,
      tipo: s.tipo,
      motivo: s.motivo
    })));
    
    // Las cancelaciones ya vienen filtradas desde el backend (nueva_programacion_id IS NULL)
    // pero añadimos filtro defensivo por estado Pendiente
    solicitudes = todasSolicitudes.filter(s => s.estado === 'Pendiente');
    console.log('✅ Solicitudes pendientes filtradas:', solicitudes.length);
    console.log('📊 Datos de solicitudes pendientes:', solicitudes);
    mostrarSolicitudes();
    cargarEstadisticas();
  } catch (err) {
    console.error('❌ Error al cargar solicitudes:', err);
    mostrarNotificacion('Error al cargar solicitudes', 'error');
    if (loading) loading.classList.add('hidden');
    if (sinResultados) sinResultados.classList.remove('hidden');
  }
}

async function cargarEstadisticas() {
  try {
    console.log('📊 Cargando estadísticas...');
    const resp = await fetch('/reservas/api/trabajador/solicitudes-cancelacion');
    const data = await resp.json();
    if (resp.ok && data.solicitudes) {
      const hoy = new Date().toISOString().split('T')[0];
      console.log('📅 Fecha de hoy:', hoy);
      // Cancelaciones ya filtradas por backend (nueva_programacion_id IS NULL)
      const pendientes = data.solicitudes.filter(s => s.estado === 'Pendiente').length;
      const aprobadasHoy = data.solicitudes.filter(s => s.estado === 'Aprobada' && s.fecha_respuesta && s.fecha_respuesta.startsWith(hoy)).length;
      console.log('📈 Estadísticas calculadas:', { total: data.solicitudes.length, pendientes, aprobadasHoy });
      const totalPendEl = getEl('total-pendientes');
      const totalAprEl = getEl('total-aprobadas');
      if (totalPendEl) totalPendEl.textContent = pendientes;
      if (totalAprEl) totalAprEl.textContent = aprobadasHoy;
    }
  } catch (err) {
    console.error('❌ Error al cargar estadísticas:', err);
  }
}

function mostrarSolicitudes() {
  console.log('🎨 Renderizando solicitudes en la tabla...');
  const loading = getEl('loading');
  const sinResultados = getEl('sin-resultados');
  const tablaContainer = getEl('tabla-container');
  const tbody = getEl('tabla-body');
  if (loading) loading.classList.add('hidden');
  if (!solicitudes || solicitudes.length === 0) {
    console.log('ℹ️ No hay solicitudes pendientes para mostrar');
    if (sinResultados) sinResultados.classList.remove('hidden');
    return;
  }
  console.log(`✅ Mostrando ${solicitudes.length} solicitudes en la tabla`);
  if (sinResultados) sinResultados.classList.add('hidden');
  if (tablaContainer) tablaContainer.classList.remove('hidden');
  if (!tbody) return;
  tbody.innerHTML = '';
  solicitudes.forEach((sol, index) => {
    console.log(`🔨 Renderizando solicitud ${index + 1}:`, sol);
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50 transition-colors';
    const fechaSolicitud = new Date(sol.fecha_solicitud);
    const fechaFormateada = fechaSolicitud.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    const fechaCita = new Date(sol.fecha_programacion + 'T00:00:00');
    const fechaCitaFormateada = fechaCita.toLocaleDateString('es-ES', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
    tr.innerHTML = `
      <td class="px-6 py-4">
        <div class="text-sm font-mono text-gray-900">#${sol.id_solicitud}</div>
        <div class="text-xs text-gray-500">${fechaFormateada}</div>
      </td>
      <td class="px-6 py-4">
        <div class="text-sm font-medium text-gray-900">${sol.paciente_nombres} ${sol.paciente_apellidos}</div>
        <div class="text-xs text-gray-500">DNI: ${sol.paciente_dni}</div>
      </td>
      <td class="px-6 py-4">
        <div class="text-sm text-gray-900">${sol.servicio}</div>
        ${sol.especialidad ? `<div class=\"text-xs text-gray-500\">${sol.especialidad}</div>` : '<div class=\"text-xs text-gray-500\">Consulta General</div>'}
      </td>
      <td class="px-6 py-4">
        <div class="text-sm text-gray-900">${fechaCitaFormateada}</div>
        <div class="text-xs text-gray-500">${sol.hora_inicio} - ${sol.hora_fin}</div>
      </td>
      <td class="px-6 py-4">
        <div class="text-sm text-gray-700 max-w-xs truncate" title="${sol.motivo}">${sol.motivo}</div>
      </td>
      <td class="px-6 py-4 text-center whitespace-nowrap">
        <button onclick="abrirModalAprobar(${sol.id_solicitud})" class="inline-flex items-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg transition-all">
          <i class="fas fa-check mr-2"></i>Aprobar
        </button>
      </td>`;
    tbody.appendChild(tr);
  });
}

function abrirModalAprobar(idSolicitud) {
  solicitudSeleccionada = solicitudes.find(s => s.id_solicitud === idSolicitud);
  if (!solicitudSeleccionada) return;
  getEl('modal-paciente').textContent = `${solicitudSeleccionada.paciente_nombres} ${solicitudSeleccionada.paciente_apellidos}`;
  getEl('modal-dni').textContent = solicitudSeleccionada.paciente_dni;
  getEl('modal-servicio').textContent = solicitudSeleccionada.servicio;
  getEl('modal-medico').textContent = solicitudSeleccionada.especialidad || 'Consulta General';
  const fechaCita = new Date(solicitudSeleccionada.fecha_programacion + 'T00:00:00');
  const fechaStr = fechaCita.toLocaleDateString('es-ES', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
  getEl('modal-fecha-hora').textContent = `${fechaStr} - ${solicitudSeleccionada.hora_inicio} a ${solicitudSeleccionada.hora_fin}`;
  getEl('modal-estado').textContent = solicitudSeleccionada.estado_reserva || 'Pendiente';
  getEl('modal-motivo').textContent = solicitudSeleccionada.motivo;
  const comentarioEl = getEl('modal-comentario'); if (comentarioEl) comentarioEl.value = '';
  const modal = getEl('modal-aprobar'); if (modal) modal.classList.remove('hidden');
}

function cerrarModalAprobar() {
  const modal = getEl('modal-aprobar'); if (modal) modal.classList.add('hidden');
  solicitudSeleccionada = null;
}

async function confirmarAprobar() {
  if (!solicitudSeleccionada) return;
  const comentarioEl = getEl('modal-comentario');
  const comentario = comentarioEl ? (comentarioEl.value.trim() || 'Solicitud de cancelación aprobada') : 'Solicitud de cancelación aprobada';
  const btn = getEl('btn-confirmar-aprobar');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Procesando...'; }
  try {
    const resp = await fetch('/reservas/api/trabajador/procesar-cancelacion', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_solicitud: solicitudSeleccionada.id_solicitud, accion: 'Aprobada', respuesta: comentario })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Error al aprobar');
    mostrarNotificacion('Cancelación aprobada exitosamente. Se enviaron notificaciones al paciente y médico.', 'success');
    cerrarModalAprobar();
    cargarSolicitudes();
  } catch (err) {
    console.error('Error:', err);
    mostrarNotificacion(err.message, 'error');
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-check mr-2"></i>Aprobar Cancelación'; }
  }
}

function mostrarNotificacion(mensaje, tipo) {
  const toast = document.createElement('div');
  const bgColor = tipo === 'success' ? 'bg-green-500' : tipo === 'error' ? 'bg-red-500' : 'bg-blue-500';
  const icon = tipo === 'success' ? 'fa-check-circle' : tipo === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
  toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center animate-fade-in`;
  toast.innerHTML = `<i class="fas ${icon} mr-3 text-xl"></i><span>${mensaje}</span>`;
  document.body.appendChild(toast);
  setTimeout(()=>toast.remove(), 4000);
}

})(); // End IIFE
