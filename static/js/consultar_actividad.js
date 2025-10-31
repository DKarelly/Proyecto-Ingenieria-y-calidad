// consultar_actividad.js - Script para consultar actividad del sistema desde AUDITORIA

// Cargar empleados al inicio
async function cargarEmpleados() {
    try {
        const response = await fetch('/reportes/api/empleados');
        const empleados = await response.json();
        
        console.log('Empleados cargados:', empleados.length);
        
        // Podemos agregar un selector de empleados si se necesita más adelante
    } catch (error) {
        console.error('Error al cargar empleados:', error);
    }
}

// Cargar actividades desde la tabla AUDITORIA
async function cargarActividades(filtros = {}) {
    try {
        console.log('Cargando actividades con filtros:', filtros);
        
        const response = await fetch('/reportes/api/auditoria', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_empleado: filtros.id_empleado || null,
                fecha_inicio: filtros.fecha || null,
                fecha_fin: filtros.fecha || null,
                limite: 100
            })
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const actividades = await response.json();
        console.log('Actividades recibidas:', actividades);
        
        const tbody = document.getElementById('tablaRegistros');
        
        if (actividades && actividades.length > 0) {
            tbody.innerHTML = '';
            actividades.forEach((actividad, index) => {
                // Determinar el resultado basado en el tipo de evento
                const esExitoso = !['Error', 'Fallido', 'Eliminación'].includes(actividad.tipo_evento);
                const estadoClass = esExitoso ? 'badge-exitoso' : 'badge-fallido';
                const estadoTexto = esExitoso ? 'Exitoso' : 'Fallido';

                const tr = document.createElement('tr');
                tr.className = 'hover:bg-gray-50 transition-colors cursor-pointer';
                tr.innerHTML = `
                    <td class="px-6 py-4 text-sm text-gray-900 font-medium">ACT-${String(actividad.id_auditoria).padStart(3, '0')}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">${actividad.empleado || 'Sistema'}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">${actividad.accion || actividad.descripcion || 'Sin descripción'}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">
                        <div class="font-medium">${actividad.fecha_formateada ? actividad.fecha_formateada.split(' ')[0] : 'N/A'}</div>
                        <div class="text-gray-500 text-xs">${actividad.fecha_formateada ? actividad.fecha_formateada.split(' ')[1] : ''}</div>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-600 font-mono">${actividad.ip_address || 'N/A'}</td>
                    <td class="px-6 py-4">
                        <span class="${estadoClass} text-white text-xs font-semibold px-3 py-1 rounded-full">
                            ${estadoTexto}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-center">
                        <button onclick="verDetalleActividad(${actividad.id_auditoria})" class="btn btn-outline btn-ver-detalle text-cyan-600 hover:text-white hover:bg-cyan-500 mx-1" title="Ver detalle">
                            <i class="fas fa-eye text-lg"></i>
                        </button>
                    </td>
                `;
                
                // Agregar evento click para seleccionar la auditoría (evitando el botón de detalle)
                tr.addEventListener('click', function(e) {
                    // No seleccionar si se hizo click en el botón de detalle
                    if (!e.target.closest('button')) {
                        seleccionarAuditoria(actividad, tr);
                    }
                });
                
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-2 block"></i>
                        <p>No se encontraron registros de actividad</p>
                        <p class="text-sm mt-2">Intente ajustar los filtros de búsqueda</p>
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('Error al cargar actividades:', error);
        const tbody = document.getElementById('tablaRegistros');
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-2 block"></i>
                    <p>Error al cargar las actividades</p>
                    <p class="text-sm mt-2">${error.message}</p>
                </td>
            </tr>
        `;
    }
}

// Variable global para almacenar el registro actual
let actividadActual = null;

// Función para ver detalle de actividad
async function verDetalleActividad(idAuditoria) {
    try {
        const response = await fetch(`/reportes/api/auditoria/${idAuditoria}`);
        const actividad = await response.json();
        
        actividadActual = actividad;
        
        // Determinar el resultado
        const esExitoso = !['Error', 'Fallido', 'Eliminación'].includes(actividad.tipo_evento);
        
        // Llenar modal con datos
        document.getElementById('detalleId').textContent = `ACT-${String(actividad.id_auditoria).padStart(3, '0')}`;
        document.getElementById('detalleEmpleado').textContent = actividad.empleado || 'Sistema';
        document.getElementById('detalleDescripcion').textContent = actividad.accion || actividad.descripcion || 'Sin descripción';
        document.getElementById('detalleFechaHora').textContent = actividad.fecha_formateada || 'N/A';
        document.getElementById('detalleIP').textContent = actividad.ip_address || 'N/A';
        
        const detalleResultado = document.getElementById('detalleResultado');
        const detalleErrorContainer = document.getElementById('detalleErrorContainer');
        
        if (esExitoso) {
            detalleResultado.textContent = 'Exitoso';
            detalleResultado.className = 'font-bold text-green-600';
            detalleResultado.parentElement.className = 'col-span-2 bg-green-50 p-3 rounded-lg border border-green-200';
            detalleErrorContainer.style.display = 'none';
        } else {
            detalleResultado.textContent = 'Fallido';
            detalleResultado.className = 'font-bold text-red-600';
            detalleResultado.parentElement.className = 'col-span-2 bg-red-50 p-3 rounded-lg border border-red-200';
            
            if (actividad.descripcion) {
                document.getElementById('detalleError').textContent = actividad.descripcion;
                detalleErrorContainer.style.display = 'block';
            }
        }
        
        document.getElementById('modalDetalle').classList.add('show');
    } catch (error) {
        console.error('Error al cargar detalle:', error);
        alert('Error al cargar el detalle de la actividad');
    }
}

// Aplicar filtros
function aplicarFiltros() {
    const empleadoTexto = document.getElementById('filtroEmpleado')?.value || '';
    const fecha = document.getElementById('filtroFecha')?.value || '';
    const horario = document.getElementById('filtroHorario')?.value || '';
    
    const filtros = {
        empleado: empleadoTexto,
        fecha: fecha,
        horario: horario
    };
    
    console.log('Aplicando filtros:', filtros);
    cargarActividades(filtros);
}

// Exportar datos
function exportarDatos(formato) {
    const fecha = document.getElementById('filtroFecha')?.value || '';
    
    let url = `/reportes/api/auditoria/exportar?formato=${formato}`;
    
    if (fecha) {
        url += `&fecha_inicio=${fecha}&fecha_fin=${fecha}`;
    }
    
    console.log('Exportando a:', formato);
    window.open(url, '_blank');
    document.getElementById('modalExportacion').classList.remove('show');
}

// Configurar modales
function setupModales() {
    const modales = ['modalDetalle', 'modalEliminar', 'modalExportacion'];
    
    modales.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            const closeBtn = modal.querySelector('.close');
            if (closeBtn) {
                closeBtn.onclick = function() {
                    modal.classList.remove('show');
                }
            }
        }
    });

    window.onclick = function(event) {
        modales.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal && event.target == modal) {
                modal.classList.remove('show');
            }
        });
    }
}

// Event listeners
function setupEventListeners() {
    // Botón buscar
    const btnBuscar = document.getElementById('btnBuscar');
    if (btnBuscar) {
        btnBuscar.onclick = aplicarFiltros;
    }
    
    // Botón exportar
    const btnExportar = document.getElementById('btnExportar');
    if (btnExportar) {
        btnExportar.onclick = function() {
            document.getElementById('modalExportacion').classList.add('show');
        }
    }
    
    // Opciones de exportación
    document.querySelectorAll('.btn-export-option').forEach(btn => {
        btn.onclick = function() {
            const formato = this.dataset.formato;
            exportarDatos(formato);
        }
    });
    
    // Botón cancelar eliminar
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    if (btnCancelarEliminar) {
        btnCancelarEliminar.onclick = function() {
            document.getElementById('modalEliminar').classList.remove('show');
        }
    }
    
    // Auto-buscar al cambiar fecha
    const filtroFecha = document.getElementById('filtroFecha');
    if (filtroFecha) {
        filtroFecha.addEventListener('change', aplicarFiltros);
    }
}

// ==================== REGISTRO DE REPORTES ====================
let auditoriaSeleccionada = null;

function abrirModalRegistrarReporte() {
    if (!auditoriaSeleccionada) {
        alert('Por favor, seleccione una actividad de la tabla primero');
        return;
    }
    
    // Mostrar información de la auditoría seleccionada
    const infoDiv = document.getElementById('infoAuditoria');
    if (infoDiv) {
        infoDiv.textContent = `Actividad #${auditoriaSeleccionada.id_auditoria} - ${auditoriaSeleccionada.empleado} - ${auditoriaSeleccionada.accion} (${auditoriaSeleccionada.fecha})`;
    }
    
    // Limpiar formulario
    document.getElementById('formRegistrarReporte').reset();
    document.getElementById('archivoReporteSeleccionado').classList.add('hidden');
    
    // Mostrar modal
    document.getElementById('modalRegistrarReporte').classList.add('show');
}

function cerrarModalRegistrarReporte() {
    document.getElementById('modalRegistrarReporte').classList.remove('show');
}

function seleccionarAuditoria(actividad, fila) {
    // Remover selección previa
    const filasTabla = document.querySelectorAll('#tablaActividades tbody tr');
    filasTabla.forEach(fila => fila.classList.remove('bg-cyan-50'));
    
    // Marcar nueva selección
    fila.classList.add('bg-cyan-50');
    
    // Guardar actividad seleccionada
    auditoriaSeleccionada = actividad;
    console.log('Auditoría seleccionada:', auditoriaSeleccionada);
}

async function enviarFormularioReporte(e) {
    e.preventDefault();
    
    const btnSubmit = e.target.querySelector('button[type="submit"]');
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Guardando...';
    
    try {
        const formData = new FormData();
        formData.append('id_auditoria', auditoriaSeleccionada.id_auditoria);
        formData.append('nombre', document.getElementById('nombreReporte').value);
        formData.append('descripcion', document.getElementById('descripcionReporte').value);
        formData.append('tipo', document.getElementById('tipoReporte').value);
        
        const archivo = document.getElementById('archivoReporte').files[0];
        if (archivo) {
            formData.append('archivo', archivo);
        }
        
        console.log('Enviando reporte para auditoría:', auditoriaSeleccionada.id_auditoria);
        
        const response = await fetch('/seguridad/api/reportes/crear', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.exito) {
            alert('✓ Reporte registrado exitosamente');
            cerrarModalRegistrarReporte();
            auditoriaSeleccionada = null;
            
            // Remover resaltado de la fila
            const filasTabla = document.querySelectorAll('#tablaActividades tbody tr');
            filasTabla.forEach(fila => fila.classList.remove('bg-cyan-50'));
        } else {
            alert('✗ Error al registrar el reporte: ' + (data.mensaje || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error al enviar reporte:', error);
        alert('✗ Error al registrar el reporte: ' + error.message);
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="fas fa-save mr-2"></i>Guardar Reporte';
    }
}

function manejarCambioArchivo(input) {
    const archivoDiv = document.getElementById('archivoReporteSeleccionado');
    const nombreArchivo = document.getElementById('nombreArchivoReporte');
    
    if (input.files && input.files[0]) {
        const archivo = input.files[0];
        nombreArchivo.textContent = archivo.name;
        archivoDiv.classList.remove('hidden');
    } else {
        archivoDiv.classList.add('hidden');
    }
}

function quitarArchivo() {
    document.getElementById('archivoReporte').value = '';
    document.getElementById('archivoReporteSeleccionado').classList.add('hidden');
}

// Inicialización
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Iniciando carga de página de consultar actividad...');
    
    // Cargar datos iniciales
    await cargarEmpleados();
    
    // Cargar actividades sin filtros
    await cargarActividades();
    
    // Setup modales y event listeners
    setupModales();
    setupEventListeners();
    
    // Event listeners para Registrar Reporte
    const btnRegistrarReporte = document.getElementById('btnRegistrarReporte');
    if (btnRegistrarReporte) {
        btnRegistrarReporte.addEventListener('click', abrirModalRegistrarReporte);
    }
    
    const btnCancelarReporte = document.getElementById('btnCancelarReporte');
    if (btnCancelarReporte) {
        btnCancelarReporte.addEventListener('click', cerrarModalRegistrarReporte);
    }
    
    const formRegistrarReporte = document.getElementById('formRegistrarReporte');
    if (formRegistrarReporte) {
        formRegistrarReporte.addEventListener('submit', enviarFormularioReporte);
    }
    
    const archivoReporte = document.getElementById('archivoReporte');
    if (archivoReporte) {
        archivoReporte.addEventListener('change', function() {
            manejarCambioArchivo(this);
        });
    }
    
    const btnQuitarArchivo = document.getElementById('btnQuitarArchivo');
    if (btnQuitarArchivo) {
        btnQuitarArchivo.addEventListener('click', quitarArchivo);
    }
    
    console.log('Página de consultar actividad cargada completamente');
});
