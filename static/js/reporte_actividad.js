// reporte_actividad.js - Script para consultar actividad (auditoría) con soporte de archivos

// Cargar empleados al inicio
async function cargarEmpleados() {
    try {
        const response = await fetch('/reportes/api/empleados');
        const empleados = await response.json();
        
        const filtroEmpleado = document.getElementById('filtroEmpleado');
        filtroEmpleado.innerHTML = '<option value="">Todos los empleados</option>';
        
        empleados.forEach(empleado => {
            const option = document.createElement('option');
            option.value = empleado.id_empleado;
            option.textContent = `${empleado.nombres} ${empleado.apellidos}${empleado.especialidad ? ' - ' + empleado.especialidad : ''}`;
            filtroEmpleado.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar empleados:', error);
    }
}

// Cargar actividades de auditoría desde la BD
async function cargarActividadesAuditoria(filtros = {}) {
    try {
        console.log('Cargando actividades con filtros:', filtros);
        
        const response = await fetch('/reportes/api/auditoria', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_empleado: filtros.id_empleado || null,
                fecha_inicio: filtros.fecha_inicio || null,
                fecha_fin: filtros.fecha_fin || null,
                tipo_evento: filtros.tipo_evento || null,
                limite: 100
            })
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const actividades = await response.json();
        console.log('Actividades recibidas:', actividades);
        
        const tbody = document.getElementById('tablaReportes');
        
        if (actividades && actividades.length > 0) {
            tbody.innerHTML = '';
            actividades.forEach(actividad => {
                const estadoClass = {
                    'Login': 'badge-activo',
                    'Logout': 'badge-inactivo',
                    'Creación': 'badge-completado',
                    'Modificación': 'badge-pendiente',
                    'Eliminación': 'badge-inactivo',
                    'Consulta': 'badge-revisado',
                    'Registro Manual': 'badge-activo'
                }[actividad.tipo_evento] || 'badge-pendiente';

                const row = `
                    <tr class="hover:bg-gray-50 transition-colors">
                        <td class="px-6 py-4 text-sm text-gray-900 font-medium">${actividad.fecha_formateada || 'N/A'}</td>
                        <td class="px-6 py-4 text-sm text-gray-900">${actividad.empleado || 'Sistema'}</td>
                        <td class="px-6 py-4 text-sm text-gray-600">${actividad.accion || 'N/A'}</td>
                        <td class="px-6 py-4">
                            <span class="${estadoClass} text-white text-xs font-semibold px-3 py-1 rounded-full">
                                ${actividad.tipo_evento || 'N/A'}
                            </span>
                        </td>
                        <td class="px-6 py-4 text-center space-x-2">
                            <button onclick="verDetalleActividad(${actividad.id_auditoria})" 
                                    class="text-cyan-600 hover:text-cyan-800 transition-colors" 
                                    title="Ver detalle">
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
                    <td colspan="5" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-2 block"></i>
                        <p>No se encontraron registros de actividad</p>
                        <p class="text-sm mt-2">Intente ajustar los filtros o generar nuevos registros</p>
                    </td>
                </tr>
            `;
            document.getElementById('btnExportar').disabled = true;
        }
    } catch (error) {
        console.error('Error al cargar actividades:', error);
        const tbody = document.getElementById('tablaReportes');
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-8 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-2 block"></i>
                    <p>Error al cargar las actividades</p>
                    <p class="text-sm mt-2">${error.message}</p>
                </td>
            </tr>
        `;
    }
}

// Variable global para almacenar el reporte actual
let reporteActualActividad = null;

// Función para ver detalle de actividad
async function verDetalleActividad(idAuditoria) {
    try {
        // Obtener detalle completo de la actividad
        const response = await fetch(`/reportes/api/auditoria/${idAuditoria}`);
        const actividad = await response.json();
        
        reporteActualActividad = actividad;
        
        // Llenar modal con datos
        document.getElementById('detalleId').textContent = `#${actividad.id_auditoria}`;
        document.getElementById('detalleEmpleado').textContent = actividad.empleado || 'Sistema';
        document.getElementById('detalleAccion').textContent = actividad.accion || 'N/A';
        document.getElementById('detalleTipo').textContent = actividad.tipo_evento || 'N/A';
        document.getElementById('detalleDescripcion').textContent = actividad.descripcion || 'Sin descripción';
        document.getElementById('detalleFecha').textContent = actividad.fecha_formateada || 'N/A';
        document.getElementById('detalleIP').textContent = actividad.ip_address || 'N/A';
        
        // Cargar archivos adjuntos
        cargarArchivosActividad(idAuditoria);
        
        document.getElementById('modalDetalle').classList.add('show');
    } catch (error) {
        console.error('Error al cargar detalle:', error);
        alert('Error al cargar el detalle de la actividad');
    }
}

// Función para eliminar actividad
async function eliminarActividad() {
    if (!reporteActualActividad) {
        alert('No hay actividad seleccionada');
        return;
    }
    
    if (!confirm(`¿Está seguro de eliminar el registro #${reporteActualActividad.id_auditoria}?\n\nAcción: ${reporteActualActividad.accion}\nEmpleado: ${reporteActualActividad.empleado}\n\nEsta acción no se puede deshacer.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/reportes/api/auditoria/${reporteActualActividad.id_auditoria}`, {
            method: 'DELETE'
        });
        
        const resultado = await response.json();
        
        if (resultado.exito) {
            alert('✓ Registro eliminado exitosamente');
            document.getElementById('modalDetalle').classList.remove('show');
            reporteActualActividad = null;
            // Recargar tabla
            aplicarFiltros();
        } else {
            alert('✗ Error al eliminar: ' + (resultado.mensaje || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error al eliminar:', error);
        alert('✗ Error al eliminar el registro');
    }
}

// Cargar archivos adjuntos de la actividad
async function cargarArchivosActividad(idAuditoria) {
    try {
        const response = await fetch(`/reportes/api/auditoria/${idAuditoria}/archivos`);
        const archivos = await response.json();
        
        const listaArchivos = document.getElementById('listaArchivosActividad');
        
        if (archivos && archivos.length > 0) {
            listaArchivos.innerHTML = archivos.map(archivo => {
                const extension = archivo.nombre_archivo.split('.').pop().toLowerCase();
                let iconClass = 'fa-file';
                let iconColor = 'text-gray-600';
                
                if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
                    iconClass = 'fa-file-image';
                    iconColor = 'text-blue-600';
                } else if (extension === 'pdf') {
                    iconClass = 'fa-file-pdf';
                    iconColor = 'text-red-600';
                } else if (['doc', 'docx'].includes(extension)) {
                    iconClass = 'fa-file-word';
                    iconColor = 'text-blue-700';
                } else if (['xls', 'xlsx'].includes(extension)) {
                    iconClass = 'fa-file-excel';
                    iconColor = 'text-green-600';
                }
                
                return `
                    <div class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-cyan-300 transition-all">
                        <div class="flex items-center gap-3 flex-1">
                            <i class="fas ${iconClass} ${iconColor} text-2xl"></i>
                            <div class="flex-1">
                                <p class="font-medium text-gray-900 text-sm">${archivo.nombre_archivo}</p>
                                <p class="text-xs text-gray-500">${formatearTamano(archivo.tamano_bytes)} • ${archivo.fecha_subida}</p>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <button onclick="descargarArchivoActividad(${archivo.id_archivo})" 
                                    class="p-2 text-green-600 hover:bg-green-50 rounded transition-colors" title="Descargar">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            listaArchivos.innerHTML = `
                <div class="text-center py-8 text-gray-400">
                    <i class="fas fa-inbox text-3xl mb-2 block"></i>
                    <p>No hay archivos adjuntos</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error al cargar archivos:', error);
        document.getElementById('listaArchivosActividad').innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-2"></i>
                <p>Error al cargar archivos</p>
            </div>
        `;
    }
}

// Descargar archivo de actividad
function descargarArchivoActividad(idArchivo) {
    window.open(`/reportes/api/auditoria/descargar-archivo/${idArchivo}`, '_blank');
}

// Obtener icono según tipo de archivo
function obtenerIconoArchivo(tipoArchivo) {
    if (!tipoArchivo) return 'fa-file';
    
    if (tipoArchivo.includes('pdf')) return 'fa-file-pdf';
    if (tipoArchivo.includes('image')) return 'fa-file-image';
    if (tipoArchivo.includes('word') || tipoArchivo.includes('document')) return 'fa-file-word';
    if (tipoArchivo.includes('excel') || tipoArchivo.includes('spreadsheet')) return 'fa-file-excel';
    if (tipoArchivo.includes('zip') || tipoArchivo.includes('compressed')) return 'fa-file-archive';
    return 'fa-file';
}

// Formatear tamaño de archivo
function formatearTamano(bytes) {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Exportar a PDF
function exportarActividadPDF() {
    const empleado = document.getElementById('filtroEmpleado').value;
    const fechaInicio = document.getElementById('filtroFechaInicio').value;
    const fechaFin = document.getElementById('filtroFechaFin').value;
    const tipoEvento = document.getElementById('filtroTipoEvento').value;
    
    let url = '/reportes/api/auditoria/exportar?formato=pdf';
    
    if (empleado) url += `&id_empleado=${empleado}`;
    if (fechaInicio) url += `&fecha_inicio=${fechaInicio}`;
    if (fechaFin) url += `&fecha_fin=${fechaFin}`;
    if (tipoEvento) url += `&tipo_evento=${tipoEvento}`;
    
    window.open(url, '_blank');
    document.getElementById('modalExportar').classList.remove('show');
}

// Aplicar filtros
function aplicarFiltros() {
    const filtros = {
        id_empleado: document.getElementById('filtroEmpleado')?.value || null,
        fecha_inicio: document.getElementById('filtroFechaInicio')?.value || null,
        fecha_fin: document.getElementById('filtroFechaFin')?.value || null,
        tipo_evento: document.getElementById('filtroTipoEvento')?.value || null
    };
    
    cargarActividadesAuditoria(filtros);
}

// Funcionalidad de modales
function setupModales() {
    const modales = ['modalDetalle', 'modalEliminar', 'modalExito', 'modalExportar', 'modalGenerarReporteActividad'];
    
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
function abrirModalGenerarActividad() {
    // Cargar empleados en el selector del modal
    cargarEmpleadosModal();
    
    // Limpiar formulario
    document.getElementById('formGenerarActividad').reset();
    document.getElementById('archivoSeleccionadoActividad').classList.add('hidden');
    document.getElementById('progresoSubidaActividad').classList.add('hidden');
    
    document.getElementById('modalGenerarReporteActividad').classList.add('show');
}

// Cerrar modal
function cerrarModalGenerarActividad() {
    document.getElementById('modalGenerarReporteActividad').classList.remove('show');
}

// Cargar empleados en selector del modal
let empleadosGlobal = [];

async function cargarEmpleadosModal() {
    try {
        const response = await fetch('/reportes/api/empleados?formato=object');
        const data = await response.json();
        
        if (data.success && data.empleados) {
            empleadosGlobal = data.empleados;
            configurarBusquedaEmpleados();
        } else if (Array.isArray(data)) {
            // Fallback si devuelve array directo
            empleadosGlobal = data;
            configurarBusquedaEmpleados();
        }
    } catch (error) {
        console.error('Error al cargar empleados:', error);
    }
}

// Configurar búsqueda dinámica de empleados
function configurarBusquedaEmpleados() {
    const inputBusqueda = document.getElementById('buscarEmpleadoReporte');
    const inputHidden = document.getElementById('empleadoReporte');
    const listaEmpleados = document.getElementById('listaEmpleadosReporte');
    
    if (!inputBusqueda || !listaEmpleados) return;
    
    // Mostrar todos los empleados al hacer clic
    inputBusqueda.addEventListener('focus', () => {
        mostrarEmpleados('');
    });
    
    // Búsqueda en tiempo real
    inputBusqueda.addEventListener('input', function() {
        const termino = this.value.toLowerCase();
        mostrarEmpleados(termino);
    });
    
    // Cerrar al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!inputBusqueda.contains(e.target) && !listaEmpleados.contains(e.target)) {
            listaEmpleados.classList.add('hidden');
        }
    });
    
    function mostrarEmpleados(termino) {
        const empleadosFiltrados = empleadosGlobal.filter(emp => {
            const nombreCompleto = `${emp.nombres} ${emp.apellidos}`.toLowerCase();
            const cargo = (emp.cargo || '').toLowerCase();
            return nombreCompleto.includes(termino) || cargo.includes(termino);
        });
        
        if (empleadosFiltrados.length === 0) {
            listaEmpleados.innerHTML = '<div class="px-4 py-3 text-gray-500 text-center">No se encontraron empleados</div>';
            listaEmpleados.classList.remove('hidden');
            return;
        }
        
        listaEmpleados.innerHTML = empleadosFiltrados.map(emp => `
            <div class="px-4 py-3 hover:bg-purple-50 cursor-pointer transition-colors border-b last:border-b-0 empleado-option" 
                 data-id="${emp.id_empleado}"
                 data-nombre="${emp.nombres} ${emp.apellidos}">
                <div class="font-medium text-gray-900">${emp.nombres} ${emp.apellidos}</div>
                <div class="text-sm text-gray-500">${emp.cargo || 'Sin cargo'}</div>
            </div>
        `).join('');
        
        listaEmpleados.classList.remove('hidden');
        
        // Agregar eventos de clic a las opciones
        document.querySelectorAll('.empleado-option').forEach(opcion => {
            opcion.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const nombre = this.getAttribute('data-nombre');
                
                inputHidden.value = id;
                inputBusqueda.value = nombre;
                listaEmpleados.classList.add('hidden');
            });
        });
    }
}

// Manejar selección de archivo
function setupFileHandlerActividad() {
    const fileInput = document.getElementById('archivoActividad');
    const dropZone = document.getElementById('dropZoneActividad');
    const archivoSeleccionado = document.getElementById('archivoSeleccionadoActividad');
    const nombreArchivo = document.getElementById('nombreArchivoActividad');
    const btnEliminar = document.getElementById('btnEliminarArchivoActividad');
    
    // Click en zona de drop
    dropZone.addEventListener('click', () => fileInput.click());
    
    // Cambio de archivo
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            nombreArchivo.textContent = this.files[0].name;
            archivoSeleccionado.classList.remove('hidden');
        }
    });
    
    // Eliminar archivo
    btnEliminar.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.value = '';
        archivoSeleccionado.classList.add('hidden');
    });
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-purple-500');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-purple-500');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-purple-500');
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            fileInput.files = e.dataTransfer.files;
            nombreArchivo.textContent = e.dataTransfer.files[0].name;
            archivoSeleccionado.classList.remove('hidden');
        }
    });
}

// Enviar formulario de generación
async function enviarFormularioActividad(e) {
    e.preventDefault();
    
    const empleadoId = document.getElementById('empleadoReporte').value;
    const accion = document.getElementById('accionActividad').value;
    const descripcion = document.getElementById('descripcionActividad').value;
    const archivo = document.getElementById('archivoActividad').files[0];
    
    if (!empleadoId || !accion || !descripcion) {
        alert('Por favor complete todos los campos obligatorios');
        return;
    }
    
    const formData = new FormData();
    formData.append('id_empleado', empleadoId);
    formData.append('accion', accion);
    formData.append('descripcion', descripcion);
    
    if (archivo) {
        formData.append('archivo', archivo);
    }
    
    try {
        // Mostrar progreso
        const progresoDiv = document.getElementById('progresoSubidaActividad');
        const barraProgreso = document.getElementById('barraProgresoActividad');
        const porcentaje = document.getElementById('porcentajeActividad');
        const btnSubmit = document.getElementById('btnSubmitActividad');
        
        progresoDiv.classList.remove('hidden');
        btnSubmit.disabled = true;
        
        // Usar XMLHttpRequest para tracking de progreso
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                barraProgreso.style.width = percent + '%';
                porcentaje.textContent = percent + '%';
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const resultado = JSON.parse(xhr.responseText);
                cerrarModalGenerarActividad();
                
                // Mostrar modal de éxito
                document.getElementById('exitoEmpleado').textContent = document.getElementById('empleadoReporte').selectedOptions[0].text;
                document.getElementById('exitoFecha').textContent = new Date().toLocaleDateString('es-PE');
                document.getElementById('exitoTotal').textContent = '1 registro';
                document.getElementById('modalExito').classList.add('show');
                
                // Recargar tabla
                aplicarFiltros();
            } else {
                alert('Error al generar el registro de auditoría');
            }
            
            progresoDiv.classList.add('hidden');
            btnSubmit.disabled = false;
        });
        
        xhr.addEventListener('error', () => {
            alert('Error de conexión al generar el registro');
            progresoDiv.classList.add('hidden');
            btnSubmit.disabled = false;
        });
        
        xhr.open('POST', '/reportes/api/auditoria/generar');
        xhr.send(formData);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar el registro');
        document.getElementById('progresoSubidaActividad').classList.add('hidden');
        document.getElementById('btnSubmitActividad').disabled = false;
    }
}

// Event listeners
function setupEventListeners() {
    const btnExportar = document.getElementById('btnExportar');
    if (btnExportar) {
        btnExportar.addEventListener('click', () => {
            exportarActividadPDF();
        });
    }
    
    // Botón generar reporte
    const btnGenerarReporte = document.getElementById('btnGenerarReporte');
    if (btnGenerarReporte) {
        btnGenerarReporte.addEventListener('click', abrirModalGenerarActividad);
    }
    
    // Botón eliminar actividad (en modal detalle)
    const btnEliminarActividad = document.getElementById('btnEliminarActividad');
    if (btnEliminarActividad) {
        btnEliminarActividad.addEventListener('click', eliminarActividad);
    }
    
    // Formulario de generación
    const formGenerar = document.getElementById('formGenerarActividad');
    if (formGenerar) {
        formGenerar.addEventListener('submit', enviarFormularioActividad);
    }
    
    // Búsqueda en tiempo real - auto-buscar al cambiar filtros
    const filtroEmpleado = document.getElementById('filtroEmpleado');
    const filtroFechaInicio = document.getElementById('filtroFechaInicio');
    const filtroFechaFin = document.getElementById('filtroFechaFin');
    
    if (filtroEmpleado) {
        filtroEmpleado.addEventListener('change', aplicarFiltros);
    }
    
    if (filtroFechaInicio) {
        filtroFechaInicio.addEventListener('change', aplicarFiltros);
    }
    if (filtroFechaFin) {
        filtroFechaFin.addEventListener('change', aplicarFiltros);
    }
    
    // Setup file handler
    setupFileHandlerActividad();
}

// Inicialización
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Iniciando carga de página de actividades...');
    
    // Cargar datos iniciales
    await cargarEmpleados();
    
    // Cargar actividades sin filtros inicialmente
    await cargarActividadesAuditoria();
    
    // Setup modales y event listeners
    setupModales();
    setupEventListeners();
    
    console.log('Página de actividades cargada completamente');
});
