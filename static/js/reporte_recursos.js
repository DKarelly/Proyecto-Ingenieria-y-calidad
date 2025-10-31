// reporte_recursos.js - Script para listar ocupación de recursos con búsqueda en tiempo real

console.log('[REPORTE RECURSOS] Iniciando script...');

// Variable global para almacenar recursos actuales
let recursosGlobales = [];
let recursoActual = null;

// Cargar tipos de recursos al inicio
async function cargarTiposRecursos() {
    try {
        console.log('[TIPOS RECURSOS] Cargando tipos de recursos...');
        const response = await fetch('/reportes/api/tipos-recursos');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const tipos = await response.json();
        console.log('[TIPOS RECURSOS] Tipos recibidos:', tipos);
        
        const filtroTipoRecurso = document.getElementById('filtroTipoRecurso');
        const tipoRecursoReporte = document.getElementById('tipoRecursoReporte');
        
        if (filtroTipoRecurso) {
            filtroTipoRecurso.innerHTML = '<option value="">Todos los tipos</option>';
            tipos.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_recurso;
                option.textContent = tipo.nombre;
                filtroTipoRecurso.appendChild(option);
            });
        }
        
        if (tipoRecursoReporte) {
            tipoRecursoReporte.innerHTML = '<option value="">Seleccione un tipo de recurso</option>';
            tipos.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id_tipo_recurso;
                option.textContent = tipo.nombre;
                tipoRecursoReporte.appendChild(option);
            });
        }
        
        console.log('[TIPOS RECURSOS] Tipos cargados exitosamente');
    } catch (error) {
        console.error('[TIPOS RECURSOS] Error al cargar tipos de recursos:', error);
    }
}

// Cargar recursos filtrados por tipo (para dropdown cascada)
async function cargarRecursosPorTipo(idTipo) {
    try {
        console.log('[RECURSOS POR TIPO] Cargando recursos del tipo:', idTipo);
        
        const response = await fetch(`/reportes/api/recursos-por-tipo/${idTipo}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const recursos = await response.json();
        console.log('[RECURSOS POR TIPO] Recursos recibidos:', recursos);
        
        const recursoReporte = document.getElementById('recursoReporte');
        
        if (recursoReporte) {
            recursoReporte.innerHTML = '<option value="">Todos los recursos del tipo</option>';
            recursos.forEach(recurso => {
                const option = document.createElement('option');
                option.value = recurso.id_recurso;
                option.textContent = recurso.nombre;
                recursoReporte.appendChild(option);
            });
        }
        
        console.log('[RECURSOS POR TIPO] Recursos cargados en dropdown');
        
    } catch (error) {
        console.error('[RECURSOS POR TIPO] Error:', error);
    }
}

// Cargar recursos con su ocupación desde la BD (tabla RECURSO)
async function cargarRecursosOcupacion(filtros = {}) {
    try {
        console.log('[RECURSOS] Cargando recursos con filtros:', filtros);
        
        const response = await fetch('/reportes/api/recursos-ocupacion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_tipo_recurso: filtros.id_tipo_recurso || null,
                limite: 100
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        recursosGlobales = await response.json();
        console.log('[RECURSOS] Recursos recibidos:', recursosGlobales.length);
        
        aplicarFiltrosVisuales();
        
    } catch (error) {
        console.error('[RECURSOS] Error al cargar recursos:', error);
        const tbody = document.getElementById('tablaReportes');
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-8 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-2 block"></i>
                    <p>Error al cargar los recursos</p>
                </td>
            </tr>
        `;
    }
}

// Aplicar filtros visuales (búsqueda en tiempo real)
function aplicarFiltrosVisuales() {
    const buscar = (document.getElementById('filtroBuscarRecurso')?.value || '').toLowerCase();
    const tipoFiltro = document.getElementById('filtroTipoRecurso')?.value || '';
    
    let recursosFiltrados = recursosGlobales;
    
    // Filtrar por tipo si está seleccionado
    if (tipoFiltro) {
        recursosFiltrados = recursosFiltrados.filter(r => 
            r.id_tipo_recurso == tipoFiltro
        );
    }
    
    // Filtrar por búsqueda de texto
    if (buscar) {
        recursosFiltrados = recursosFiltrados.filter(r => 
            (r.nombre || '').toLowerCase().includes(buscar) ||
            (r.tipo_recurso || '').toLowerCase().includes(buscar)
        );
    }
    
    console.log('[FILTROS] Recursos filtrados:', recursosFiltrados.length);
    
    renderizarTablaRecursos(recursosFiltrados);
}

// Renderizar tabla de recursos
function renderizarTablaRecursos(recursos) {
    const tbody = document.getElementById('tablaReportes');
    
    if (recursos && recursos.length > 0) {
        tbody.innerHTML = '';
        recursos.forEach(recurso => {
            const estadoClass = {
                'Activo': 'badge-disponible',
                'Inactivo': 'badge-inactivo',
                'Mantenimiento': 'badge-mantenimiento',
                'Disponible': 'badge-disponible',
                'Ocupado': 'badge-ocupado'
            }[recurso.estado] || 'badge-mantenimiento';

            const ocupacion = parseFloat(recurso.ocupacion_porcentaje || 0);

            const row = `
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 text-sm text-gray-900 font-medium">#${recurso.id_recurso}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">${recurso.nombre || 'Sin nombre'}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">${recurso.tipo_recurso || 'N/A'}</td>
                    <td class="px-6 py-4">
                        <span class="${estadoClass} text-white text-xs font-semibold px-3 py-1 rounded-full">
                            ${recurso.estado || 'N/A'}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-sm font-bold ${ocupacion > 70 ? 'text-red-600' : ocupacion > 40 ? 'text-yellow-600' : 'text-green-600'}">${ocupacion.toFixed(1)}%</td>
                    <td class="px-6 py-4 text-center space-x-2">
                        <button onclick="verDetalleRecurso(${recurso.id_recurso}, '${(recurso.nombre || '').replace(/'/g, "\\'")}', '${(recurso.tipo_recurso || '').replace(/'/g, "\\'")}', ${recurso.operaciones_mes || 0})" 
                                class="text-cyan-600 hover:text-cyan-800 transition-colors" 
                                title="Ver detalle de uso">
                            <i class="fas fa-eye text-lg"></i>
                        </button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
        
        // Habilitar exportación
        document.getElementById('btnExportar').disabled = false;
    } else {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-2 block"></i>
                    <p>No se encontraron recursos</p>
                </td>
            </tr>
        `;
        document.getElementById('btnExportar').disabled = true;
    }
}

// Función para ver detalle de uso de recurso con empleados
async function verDetalleRecurso(idRecurso, nombreRecurso, tipoRecurso, totalUsos) {
    try {
        console.log('[DETALLE] Cargando detalle del recurso:', idRecurso);
        
        // Mostrar información básica
        document.getElementById('detalleNombre').textContent = nombreRecurso;
        document.getElementById('detalleTipo').textContent = tipoRecurso;
        document.getElementById('detalleTotalUsos').textContent = totalUsos;
        
        // Abrir modal
        document.getElementById('modalDetalle').classList.add('show');
        
        // Cargar historial de usos
        const response = await fetch(`/reportes/api/recursos/${idRecurso}/detalle`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const usos = await response.json();
        console.log('[DETALLE] Usos cargados:', usos.length);
        
        const tbody = document.getElementById('tablaUsosRecurso');
        
        if (usos && usos.length > 0) {
            tbody.innerHTML = usos.map(uso => `
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-3 text-sm text-gray-900">${uso.fecha_formateada || 'N/A'}</td>
                    <td class="px-4 py-3 text-sm text-gray-900">${uso.empleado || 'Sin asignar'}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">${uso.servicio || 'Sin servicio'}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">${uso.hora_inicio_formateada || 'N/A'}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">${uso.hora_fin_formateada || 'N/A'}</td>
                    <td class="px-4 py-3">
                        <span class="badge-${uso.estado_reserva === 'Confirmada' ? 'disponible' : 'mantenimiento'} text-white text-xs px-2 py-1 rounded-full">
                            ${uso.estado_reserva || 'N/A'}
                        </span>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                        <i class="fas fa-inbox text-3xl mb-2 block"></i>
                        <p>No hay registros de uso para este recurso</p>
                    </td>
                </tr>
            `;
        }
        
    } catch (error) {
        console.error('[DETALLE] Error al cargar detalle:', error);
        document.getElementById('tablaUsosRecurso').innerHTML = `
            <tr>
                <td colspan="6" class="px-4 py-8 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-3xl mb-2 block"></i>
                    <p>Error al cargar el historial de uso</p>
                </td>
            </tr>
        `;
    }
}

// Exportar a PDF
function exportarRecursosPDF() {
    const tipoRecurso = document.getElementById('filtroTipoRecurso').value;
    
    let url = '/reportes/api/recursos-ocupacion/exportar?formato=pdf';
    
    if (tipoRecurso) url += `&id_tipo_recurso=${tipoRecurso}`;
    
    window.open(url, '_blank');
    document.getElementById('modalExportar').classList.remove('show');
}

// Funcionalidad de modales
function setupModales() {
    const modales = ['modalDetalle', 'modalEliminar', 'modalExito', 'modalExportar', 'modalGenerarReporte'];
    
    modales.forEach(modalId => {
        const modal = document.getElementById(modalId);
        const closeBtn = modal?.querySelector('.close');
        
        if (closeBtn) {
            closeBtn.onclick = function() {
                modal.classList.remove('show');
            }
        }
    });

    window.onclick = function(event) {
        modales.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (event.target == modal) {
                modal.classList.remove('show');
            }
        });
    }
    
    // Botón cerrar éxito
    const btnCerrarExito = document.getElementById('btnCerrarExito');
    if (btnCerrarExito) {
        btnCerrarExito.onclick = function() {
            document.getElementById('modalExito').classList.remove('show');
        }
    }
}

// ========== FUNCIONES PARA GENERAR REPORTE ==========

// Abrir modal de generar reporte
function abrirModalGenerarRecursos() {
    console.log('[GENERAR REPORTE] Abriendo modal...');
    
    // Limpiar formulario
    const form = document.getElementById('formGenerarReporte');
    if (form) {
        form.reset();
    }
    
    // Ocultar contenedor de recursos hasta que se seleccione tipo
    const contenedorRecurso = document.getElementById('contenedorRecurso');
    if (contenedorRecurso) {
        contenedorRecurso.style.display = 'none';
    }
    
    const progresoDiv = document.getElementById('progresoSubidaRecurso');
    if (progresoDiv) {
        progresoDiv.classList.add('hidden');
    }
    
    document.getElementById('modalGenerarReporte').classList.add('show');
}

// Cerrar modal
function cerrarModalGenerarRecursos() {
    console.log('[GENERAR REPORTE] Cerrando modal...');
    document.getElementById('modalGenerarReporte').classList.remove('show');
}

// Enviar formulario de generación
async function enviarFormularioRecursos(e) {
    e.preventDefault();
    console.log('[GENERAR REPORTE] Enviando formulario...');
    
    const tipoRecursoId = document.getElementById('tipoRecursoReporte').value;
    const recursoId = document.getElementById('recursoReporte').value;
    const fechaOperacion = document.getElementById('fechaOperacionReporte').value;
    const descripcion = document.getElementById('descripcionRecursoReporte').value;
    
    if (!tipoRecursoId) {
        alert('Por favor seleccione un tipo de recurso');
        return;
    }
    
    const formData = new FormData();
    formData.append('id_tipo_recurso', tipoRecursoId);
    if (recursoId) formData.append('id_recurso', recursoId);
    if (fechaOperacion) formData.append('fecha_operacion', fechaOperacion);
    formData.append('descripcion', descripcion || '');
    
    try {
        // Mostrar progreso
        const progresoDiv = document.getElementById('progresoSubidaRecurso');
        const spinner = document.getElementById('spinnerGenerarRecurso');
        const textoBtn = document.getElementById('textoGenerarRecurso');
        
        if (progresoDiv) progresoDiv.classList.remove('hidden');
        if (spinner) spinner.style.display = 'inline-block';
        if (textoBtn) textoBtn.textContent = 'Generando...';
        
        const response = await fetch('/reportes/api/recursos-ocupacion/generar', {
            method: 'POST',
            body: formData
        });
        
        console.log('[GENERAR REPORTE] Respuesta status:', response.status);
        
        if (response.ok) {
            const resultado = await response.json();
            console.log('[GENERAR REPORTE] Resultado:', resultado);
            
            cerrarModalGenerarRecursos();
            
            // Mostrar modal de éxito
            const exitoTotal = document.getElementById('exitoTotal');
            const exitoFecha = document.getElementById('exitoFecha');
            
            if (exitoTotal) exitoTotal.textContent = resultado.total_recursos || 'N/A';
            if (exitoFecha) exitoFecha.textContent = new Date().toLocaleDateString('es-PE');
            
            document.getElementById('modalExito').classList.add('show');
            
            // Recargar tabla
            await cargarRecursosOcupacion();
        } else {
            const error = await response.json();
            alert('Error al generar el reporte: ' + (error.message || 'Error desconocido'));
        }
        
    } catch (error) {
        console.error('[GENERAR REPORTE] Error:', error);
        alert('Error al generar el reporte: ' + error.message);
    } finally {
        // Ocultar progreso
        const progresoDiv = document.getElementById('progresoSubidaRecurso');
        const spinner = document.getElementById('spinnerGenerarRecurso');
        const textoBtn = document.getElementById('textoGenerarRecurso');
        
        if (progresoDiv) progresoDiv.classList.add('hidden');
        if (spinner) spinner.style.display = 'none';
        if (textoBtn) textoBtn.textContent = 'Generar Reporte';
    }
}

// Event listeners
function setupEventListeners() {
    console.log('[EVENT LISTENERS] Configurando event listeners...');
    
    // Filtro tipo de recurso - búsqueda en tiempo real
    const filtroTipoRecurso = document.getElementById('filtroTipoRecurso');
    if (filtroTipoRecurso) {
        filtroTipoRecurso.addEventListener('change', () => {
            const idTipo = filtroTipoRecurso.value;
            if (idTipo) {
                cargarRecursosOcupacion({ id_tipo_recurso: idTipo });
            } else {
                cargarRecursosOcupacion();
            }
        });
    }
    
    // Búsqueda en tiempo real
    const filtroBuscarRecurso = document.getElementById('filtroBuscarRecurso');
    if (filtroBuscarRecurso) {
        filtroBuscarRecurso.addEventListener('input', aplicarFiltrosVisuales);
    }
    
    // Dropdown cascada - cuando cambia el tipo de recurso en el modal
    const tipoRecursoReporte = document.getElementById('tipoRecursoReporte');
    if (tipoRecursoReporte) {
        tipoRecursoReporte.addEventListener('change', async function() {
            const idTipo = this.value;
            const contenedorRecurso = document.getElementById('contenedorRecurso');
            
            if (idTipo && contenedorRecurso) {
                contenedorRecurso.style.display = 'block';
                await cargarRecursosPorTipo(idTipo);
            } else if (contenedorRecurso) {
                contenedorRecurso.style.display = 'none';
            }
        });
    }
    
    const btnExportar = document.getElementById('btnExportar');
    if (btnExportar) {
        btnExportar.addEventListener('click', () => {
            document.getElementById('modalExportar').classList.add('show');
        });
    }
    
    // Botón generar reporte
    const btnGenerarReporte = document.getElementById('btnGenerarReporte');
    if (btnGenerarReporte) {
        console.log('[EVENT LISTENERS] Botón generar reporte encontrado');
        btnGenerarReporte.addEventListener('click', abrirModalGenerarRecursos);
    } else {
        console.error('[EVENT LISTENERS] No se encontró el botón generar reporte');
    }
    
    // Formulario de generación
    const formGenerar = document.getElementById('formGenerarReporte');
    if (formGenerar) {
        console.log('[EVENT LISTENERS] Formulario generar reporte encontrado');
        formGenerar.addEventListener('submit', enviarFormularioRecursos);
    } else {
        console.error('[EVENT LISTENERS] No se encontró el formulario generar reporte');
    }
    
    // Botón cancelar modal generar
    const btnCancelar = document.getElementById('btnCancelarGenerarRecurso');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', cerrarModalGenerarRecursos);
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', async function() {
    console.log('[INIT] Iniciando página de ocupación de recursos...');
    
    // Cargar tipos de recursos primero
    await cargarTiposRecursos();
    
    // Cargar recursos
    await cargarRecursosOcupacion();
    
    // Setup modales y event listeners
    setupModales();
    setupEventListeners();
    
    console.log('[INIT] Página inicializada correctamente');
});
