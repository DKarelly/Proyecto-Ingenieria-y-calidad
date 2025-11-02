// reportes.js - Funcionalidad completa para el módulo de reportes
// Búsqueda en tiempo real, modales dinámicos, subida de archivos

class ReportesManager {
    constructor() {
        this.reportes = [];
        this.categorias = [];
        this.paginaActual = 1;
        this.reportesPorPagina = 10;
        this.filtros = {
            busqueda: '',
            id_categoria: null,
            tipo: null,
            fecha_inicio: null,
            fecha_fin: null
        };
        this.init();
    }

    init() {
        this.cargarCategorias();
        this.cargarReportes();
        this.setupEventListeners();
        this.setupSearchRealTime();
    }

    async cargarCategorias() {
        try {
            const response = await fetch('/reportes/api/reportes/categorias');
            const data = await response.json();
            this.categorias = data;
            this.renderizarSelectCategorias();
        } catch (error) {
            console.error('Error cargando categorías:', error);
        }
    }

    renderizarSelectCategorias() {
        const selects = document.querySelectorAll('[data-select-categorias]');
        const html = `
            <option value="">Todas las categorías</option>
            ${this.categorias.map(cat => `
                <option value="${cat.id_categoria}">${cat.nombre}</option>
            `).join('')}
        `;
        selects.forEach(select => select.innerHTML = html);
    }

    async cargarReportes() {
        try {
            const response = await fetch('/reportes/api/reportes/buscar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(this.filtros)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            // Verificar si data es un array
            if (Array.isArray(data)) {
                this.reportes = data;
            } else if (data.error) {
                throw new Error(data.error);
            } else {
                this.reportes = [];
                console.warn('Respuesta inesperada del servidor:', data);
            }
            
            this.renderizarReportes();
        } catch (error) {
            console.error('Error cargando reportes:', error);
            this.mostrarError(`Error al cargar los reportes: ${error.message}`);
            this.reportes = [];
            this.renderizarReportes();
        }
    }

    renderizarReportes() {
        const tbody = document.getElementById('tablaReportes');
        if (!tbody) return;

        if (this.reportes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-8 text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-2"></i>
                        <p>No se encontraron reportes</p>
                    </td>
                </tr>
            `;
            return;
        }

        const inicio = (this.paginaActual - 1) * this.reportesPorPagina;
        const fin = inicio + this.reportesPorPagina;
        const reportesPaginados = this.reportes.slice(inicio, fin);

        tbody.innerHTML = reportesPaginados.map(reporte => `
            <tr class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 text-sm text-gray-900">
                    <div class="font-medium">${reporte.codigo || 'N/A'}</div>
                    <div class="text-gray-500 text-xs">${reporte.fecha_formateada || ''}</div>
                </td>
                <td class="px-6 py-4 text-sm">
                    <span class="font-semibold text-cyan-600">${reporte.categoria || 'Sin categoría'}</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900">${reporte.tipo || 'N/A'}</td>
                <td class="px-6 py-4 text-sm text-gray-900">${reporte.empleado || 'N/A'}</td>
                <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">${reporte.nombre || reporte.descripcion || 'Sin descripción'}</td>
                <td class="px-6 py-4 text-sm">
                    <span class="inline-flex items-center gap-1">
                        <i class="fas fa-paperclip text-gray-400"></i>
                        <span class="text-gray-600">${reporte.num_archivos || 0}</span>
                    </span>
                </td>
                <td class="px-6 py-4 text-center">
                    <button onclick="reportesManager.verDetalle(${reporte.id_reporte})" 
                            class="btn btn-outline text-cyan-600 hover:text-white hover:bg-cyan-500 mx-1" 
                            title="Ver detalle">
                        <i class="fas fa-eye text-lg"></i>
                    </button>
                    <button onclick="reportesManager.descargarReporte(${reporte.id_reporte})" 
                            class="btn btn-outline text-emerald-600 hover:text-white hover:bg-emerald-500 mx-1" 
                            title="Descargar">
                        <i class="fas fa-download text-lg"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        this.actualizarPaginacion();
    }

    actualizarPaginacion() {
        const totalPaginas = Math.ceil(this.reportes.length / this.reportesPorPagina);
        document.getElementById('paginaActual').textContent = this.paginaActual;
        document.getElementById('totalPaginas').textContent = totalPaginas;

        const btnAnterior = document.getElementById('btnAnterior');
        const btnSiguiente = document.getElementById('btnSiguiente');

        if (btnAnterior) btnAnterior.disabled = this.paginaActual === 1;
        if (btnSiguiente) btnSiguiente.disabled = this.paginaActual >= totalPaginas;
    }

    async verDetalle(idReporte) {
        try {
            const response = await fetch(`/reportes/api/reportes/${idReporte}`);
            const reporte = await response.json();

            if (!reporte || reporte.error) {
                this.mostrarError('No se pudo cargar el reporte');
                return;
            }

            this.mostrarModalDetalle(reporte);
        } catch (error) {
            console.error('Error cargando detalle:', error);
            this.mostrarError('Error al cargar el detalle del reporte');
        }
    }

    mostrarModalDetalle(reporte) {
        const modal = document.getElementById('modalDetalle');

        // Log para depuración
        console.log('Datos del reporte:', reporte);

        // Formatear fecha y hora desde fecha_creacion (MySQL datetime)
        const fechaCompleta = reporte.fecha_creacion || '';
        let fecha = 'N/A';
        let hora = 'N/A';

        if (fechaCompleta) {
            try {
                // Si viene en formato MySQL: "2025-10-31 14:30:00"
                const fechaStr = String(fechaCompleta);
                if (fechaStr.includes('-') && fechaStr.includes(':')) {
                    const [fechaParte, horaParte] = fechaStr.split(' ');
                    const [anio, mes, dia] = fechaParte.split('-');
                    fecha = `${dia}/${mes}/${anio}`;
                    hora = horaParte ? horaParte.substring(0, 8) : 'N/A'; // HH:MM:SS
                } else if (fechaStr.includes('/')) {
                    // Si ya viene formateada
                    fecha = fechaStr.split(' ')[0] || fechaStr;
                    hora = fechaStr.split(' ')[1] || 'N/A';
                }
            } catch (e) {
                console.error('Error formateando fecha:', e, fechaCompleta);
                fecha = String(fechaCompleta).substring(0, 10);
            }
        }

        // Rellenar datos básicos
        const elementos = {
            'detalleCodigo': reporte.codigo,
            'detalleCategoria': reporte.categoria,
            'detalleTipo': reporte.tipo,
            'detalleFecha': fecha,
            'detalleHora': hora,
            'detalleEmpleado': reporte.empleado,
            'detalleDescripcion': reporte.descripcion
        };

        // Actualizar cada elemento con validación
        for (const [id, valor] of Object.entries(elementos)) {
            const elemento = document.getElementById(id);
            if (elemento) {
                elemento.textContent = valor || 'No especificado';
            } else {
                console.warn(`Elemento ${id} no encontrado en el DOM`);
            }
        }

        // Renderizar archivos adjuntos con vista previa
        const listaArchivos = document.getElementById('listaArchivos');
        if (reporte.archivos && reporte.archivos.length > 0) {
            listaArchivos.innerHTML = reporte.archivos.map(archivo => {
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
                    <div class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-cyan-300 transition-all cursor-pointer" 
                         onclick="reportesManager.previsualizarArchivo(${archivo.id_archivo}, '${archivo.nombre_archivo}', '${archivo.ruta_archivo}')">
                        <div class="flex items-center gap-3 flex-1">
                            <i class="fas ${iconClass} ${iconColor} text-2xl"></i>
                            <div class="flex-1">
                                <p class="font-medium text-gray-900 text-sm">${archivo.nombre_archivo}</p>
                                <p class="text-xs text-gray-500">${this.formatearTamano(archivo.tamano_bytes)} • ${archivo.fecha_subida}</p>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <button onclick="event.stopPropagation(); reportesManager.descargarArchivo(${archivo.id_archivo})" 
                                    class="p-2 text-green-600 hover:bg-green-50 rounded transition-colors" title="Descargar">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            listaArchivos.innerHTML = '<p class="text-gray-500 text-center py-8"><i class="fas fa-inbox text-3xl mb-2 block"></i>No hay archivos adjuntos</p>';
        }

        // Limpiar vista previa
        document.getElementById('vistaPrevia').innerHTML = `
            <div class="text-center text-gray-400">
                <i class="fas fa-image text-6xl mb-3"></i>
                <p>Selecciona un archivo para previsualizar</p>
            </div>
        `;

        // Guardar ID del reporte actual
        modal.dataset.idReporte = reporte.id_reporte;
        modal.dataset.codigoReporte = reporte.codigo || '';

        modal.classList.add('show');
    }

    formatearTamano(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / 1048576).toFixed(2) + ' MB';
    }

    async subirArchivo(idReporte, archivo) {
        await this.subirArchivoConProgreso(idReporte, archivo, false);
    }

    async subirArchivoConProgreso(idReporte, archivo, desdeModal = false) {
        const formData = new FormData();
        formData.append('archivo', archivo);

        // Mostrar progreso si es desde modal de generación
        let progresoDiv, barraProgreso, porcentaje;
        if (desdeModal) {
            progresoDiv = document.getElementById('progresoSubida');
            barraProgreso = document.getElementById('barraProgreso');
            porcentaje = document.getElementById('porcentajeProgreso');
            progresoDiv?.classList.remove('hidden');
        }

        try {
            // Usar XMLHttpRequest para tener progreso
            const resultado = await new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();

                // Evento de progreso
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = Math.round((e.loaded / e.total) * 100);
                        if (barraProgreso && porcentaje) {
                            barraProgreso.style.width = `${percentComplete}%`;
                            porcentaje.textContent = `${percentComplete}%`;
                        }
                    }
                });

                // Evento de carga completa
                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            resolve(JSON.parse(xhr.responseText));
                        } catch (e) {
                            reject(new Error('Respuesta inválida del servidor'));
                        }
                    } else {
                        reject(new Error(`Error ${xhr.status}: ${xhr.statusText}`));
                    }
                });

                // Evento de error
                xhr.addEventListener('error', () => {
                    reject(new Error('Error de red al subir el archivo'));
                });

                // Enviar petición
                xhr.open('POST', `/reportes/api/reportes/${idReporte}/subir-archivo`);
                xhr.send(formData);
            });

            if (resultado.success) {
                this.mostrarExito('Archivo subido exitosamente');
                
                // Recargar detalle automáticamente si el modal está abierto
                const modalDetalle = document.getElementById('modalDetalle');
                if (modalDetalle && modalDetalle.classList.contains('show')) {
                    await this.verDetalle(idReporte);
                }
                
                return resultado;
            } else {
                this.mostrarError(resultado.error || 'Error al subir archivo');
                return null;
            }
        } catch (error) {
            console.error('Error subiendo archivo:', error);
            this.mostrarError('Error al subir el archivo: ' + error.message);
            return null;
        } finally {
            // Ocultar progreso
            if (progresoDiv) {
                setTimeout(() => {
                    progresoDiv.classList.add('hidden');
                    if (barraProgreso) barraProgreso.style.width = '0%';
                    if (porcentaje) porcentaje.textContent = '0%';
                }, 1000);
            }
        }
    }

    async descargarArchivo(idArchivo) {
        // Mostrar indicador de descarga
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-blue-500 text-white px-6 py-4 rounded-lg shadow-2xl z-50';
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fas fa-download fa-bounce text-2xl"></i>
                <div>
                    <p class="font-bold">Descargando archivo...</p>
                    <div class="w-48 bg-blue-300 rounded-full h-2 mt-2">
                        <div class="descarga-progreso bg-white h-2 rounded-full animate-pulse"></div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(toast);

        // Simular progreso de descarga
        setTimeout(() => {
            toast.remove();
        }, 2000);

        // Abrir archivo en nueva ventana
        window.open(`/reportes/api/reportes/descargar-archivo/${idArchivo}`, '_blank');
    }

    async eliminarArchivo(idArchivo, idReporte) {
        if (!confirm('¿Está seguro de eliminar este archivo?')) return;

        try {
            const response = await fetch(`/reportes/api/reportes/eliminar-archivo/${idArchivo}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.mostrarExito('Archivo eliminado exitosamente');
                this.verDetalle(idReporte); // Recargar detalle
            } else {
                this.mostrarError(result.error || 'Error al eliminar archivo');
            }
        } catch (error) {
            console.error('Error eliminando archivo:', error);
            this.mostrarError('Error al eliminar el archivo');
        }
    }

    async descargarReporte(idReporte) {
        const formato = prompt('Formato de descarga (pdf/excel):', 'pdf');
        if (!formato) return;

        window.open(`/reportes/api/reportes/${idReporte}/descargar?formato=${formato}`, '_blank');
    }

    async crearReporte(datos) {
        try {
            const response = await fetch('/reportes/api/reportes/crear', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(datos)
            });

            const result = await response.json();

            if (result.success) {
                this.mostrarExito('Reporte creado exitosamente');
                this.cargarReportes(); // Recargar lista
                return result;
            } else {
                this.mostrarError(result.error || 'Error al crear reporte');
                return null;
            }
        } catch (error) {
            console.error('Error creando reporte:', error);
            this.mostrarError('Error al crear el reporte');
            return null;
        }
    }

    setupEventListeners() {
        // Botón Generar Reporte
        document.getElementById('btnGenerarReporte')?.addEventListener('click', () => {
            this.mostrarModalGenerar();
        });

        // Botón Exportar
        document.getElementById('btnExportar')?.addEventListener('click', () => {
            this.mostrarModalExportar();
        });

        // Formulario de generar reporte
        document.getElementById('formGenerarReporte')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generarNuevoReporte();
        });

        // Botón cancelar generar
        document.getElementById('btnCancelarGenerar')?.addEventListener('click', () => {
            document.getElementById('modalGenerar').classList.remove('show');
        });

        // Botones de exportación (PDF y Excel)
        document.querySelectorAll('.btn-export-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const formato = btn.dataset.formato;
                this.exportarReportes(formato);
            });
        });

        // Paginación
        document.getElementById('btnAnterior')?.addEventListener('click', () => {
            if (this.paginaActual > 1) {
                this.paginaActual--;
                this.renderizarReportes();
            }
        });

        document.getElementById('btnSiguiente')?.addEventListener('click', () => {
            const totalPaginas = Math.ceil(this.reportes.length / this.reportesPorPagina);
            if (this.paginaActual < totalPaginas) {
                this.paginaActual++;
                this.renderizarReportes();
            }
        });

        // Cerrar modales
        document.querySelectorAll('.modal .close, .modal .btn-cancelar').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.remove('show');
            });
        });

        // Cerrar modales con botón × o clic fuera
        document.querySelectorAll('.modal').forEach(modal => {
            // Botón de cerrar (×)
            modal.querySelector('.close')?.addEventListener('click', () => {
                modal.classList.remove('show');
            });

            // Clic fuera del modal
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('show');
                }
            });
        });

        // Cerrar con tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.show').forEach(modal => {
                    modal.classList.remove('show');
                });
            }
        });

        // ============================================
        // EVENT LISTENERS PARA DETALLE DE REPORTE
        // ============================================

        // Botón Eliminar Reporte
        document.getElementById('btnEliminarReporte')?.addEventListener('click', () => {
            this.mostrarModalEliminar();
        });

        // Confirmar eliminación
        document.getElementById('btnConfirmarEliminar')?.addEventListener('click', () => {
            this.eliminarReporte();
        });

        // Cancelar eliminación
        document.getElementById('btnCancelarEliminar')?.addEventListener('click', () => {
            document.getElementById('modalConfirmarEliminar').classList.remove('show');
        });

        // Exportar detalle a PDF
        document.getElementById('btnExportarPdfDetalle')?.addEventListener('click', () => {
            this.exportarDetalleAPDF();
        });

        // Exportar detalle a Excel
        document.getElementById('btnExportarExcelDetalle')?.addEventListener('click', () => {
            this.exportarDetalleAExcel();
        });
    }

    setupSearchRealTime() {
        const inputBusqueda = document.getElementById('inputBusqueda');
        const selectCategoria = document.getElementById('filtroCategoria');
        const selectTipo = document.getElementById('filtroTipo');
        const inputFechaInicio = document.getElementById('filtroFechaInicio');
        const inputFechaFin = document.getElementById('filtroFechaFin');

        let timeoutId;

        const buscar = () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                this.filtros.busqueda = inputBusqueda?.value || '';
                // Asegurar que id_categoria sea null o un valor válido (no string vacío)
                const categoriaValue = selectCategoria?.value;
                this.filtros.id_categoria = categoriaValue && categoriaValue !== '' ? parseInt(categoriaValue) : null;
                this.filtros.tipo = selectTipo?.value || null;
                this.filtros.fecha_inicio = inputFechaInicio?.value || null;
                this.filtros.fecha_fin = inputFechaFin?.value || null;
                this.paginaActual = 1;
                this.cargarReportes();
            }, 300); // Debounce de 300ms
        };

        inputBusqueda?.addEventListener('input', buscar);
        selectCategoria?.addEventListener('change', buscar);
        selectTipo?.addEventListener('change', buscar);
        inputFechaInicio?.addEventListener('change', buscar);
        inputFechaFin?.addEventListener('change', buscar);
    }

    mostrarExito(mensaje) {
        // Toast de éxito con estilo mejorado
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-2xl z-50 animate-fade-in';
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fas fa-check-circle text-2xl"></i>
                <span class="font-medium">${mensaje}</span>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    mostrarError(mensaje) {
        // Toast de error con estilo mejorado
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-lg shadow-2xl z-50 animate-fade-in';
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fas fa-exclamation-circle text-2xl"></i>
                <div>
                    <p class="font-bold">Error</p>
                    <p class="text-sm">${mensaje}</p>
                </div>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    mostrarModalGenerar() {
        // Cargar categorías en el select del modal
        const selectCategoria = document.getElementById('categoriaReporte');
        if (selectCategoria && this.categorias.length > 0) {
            selectCategoria.innerHTML = '<option value="">Seleccione una categoría</option>';
            this.categorias.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id_categoria;
                option.textContent = cat.nombre;
                selectCategoria.appendChild(option);
            });
        }
        
        // Limpiar formulario y archivo
        document.getElementById('formGenerarReporte')?.reset();
        document.getElementById('archivoSeleccionado')?.classList.add('hidden');
        document.getElementById('progresoSubida')?.classList.add('hidden');
        
        // Configurar eventos de archivo
        this.configurarSubidaArchivo();
        
        // Mostrar modal
        document.getElementById('modalGenerar').classList.add('show');
    }

    configurarSubidaArchivo() {
        const inputArchivo = document.getElementById('archivoNuevoReporte');
        const divSeleccionado = document.getElementById('archivoSeleccionado');
        const nombreArchivo = document.getElementById('nombreArchivoSeleccionado');
        const tamanoArchivo = document.getElementById('tamanoArchivoSeleccionado');
        const btnRemover = document.getElementById('btnRemoverArchivo');

        // Evento change del input
        inputArchivo.onchange = (e) => {
            const archivo = e.target.files[0];
            if (archivo) {
                // Validar tamaño (10MB máximo)
                if (archivo.size > 10 * 1024 * 1024) {
                    this.mostrarError('El archivo no debe superar los 10MB');
                    inputArchivo.value = '';
                    return;
                }

                nombreArchivo.textContent = archivo.name;
                tamanoArchivo.textContent = this.formatearTamano(archivo.size);
                divSeleccionado.classList.remove('hidden');
            }
        };

        // Botón remover archivo
        btnRemover.onclick = () => {
            inputArchivo.value = '';
            divSeleccionado.classList.add('hidden');
        };
    }

    mostrarModalExportar() {
        document.getElementById('modalExportacion').classList.add('show');
    }

    async generarNuevoReporte() {
        const categoriaId = document.getElementById('categoriaReporte').value;
        const descripcion = document.getElementById('descripcionReporte').value;
        const inputArchivo = document.getElementById('archivoNuevoReporte');
        const archivo = inputArchivo.files[0];

        if (!categoriaId) {
            this.mostrarError('Por favor seleccione una categoría');
            return;
        }

        // Mostrar spinner
        const spinner = document.getElementById('spinnerGenerar');
        const texto = document.getElementById('textoGenerar');
        spinner.style.display = 'inline-block';
        texto.textContent = 'Generando...';

        try {
            // Obtener nombre de categoría
            const categoria = this.categorias.find(c => c.id_categoria == categoriaId);
            const categoriaNombre = categoria ? categoria.nombre : 'Sin categoría';

            // Generar código único con timestamp
            const ahora = new Date();
            const timestamp = ahora.getFullYear() + 
                            String(ahora.getMonth() + 1).padStart(2, '0') + 
                            String(ahora.getDate()).padStart(2, '0') +
                            String(ahora.getHours()).padStart(2, '0') +
                            String(ahora.getMinutes()).padStart(2, '0') +
                            String(ahora.getSeconds()).padStart(2, '0');
            const codigo = `REP-${timestamp}-${Math.floor(Math.random() * 10000)}`;
            
            // El nombre se genera automáticamente en el backend
            const nombreReporte = `Reporte ${categoriaNombre} - ${ahora.toLocaleDateString('es-PE')}`;
            
            // Crear reporte (la fecha se genera automáticamente en el backend)
            const response = await fetch('/reportes/api/reportes/crear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    codigo: codigo,
                    nombre: nombreReporte,
                    tipo: categoriaNombre,
                    descripcion: descripcion || `Reporte de ${categoriaNombre}`,
                    id_categoria: categoriaId,
                    estado: 'Completado'
                })
            });

            const result = await response.json();

            if (response.ok && result.id_reporte) {
                // Si hay archivo, subirlo con barra de progreso
                if (archivo) {
                    await this.subirArchivoConProgreso(result.id_reporte, archivo, true);
                }

                this.mostrarExito('Reporte generado exitosamente');
                document.getElementById('modalGenerar').classList.remove('show');
                
                // Recargar reportes
                await this.cargarReportes();
            } else {
                this.mostrarError(result.error || 'Error al generar el reporte');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error al generar el reporte');
        } finally {
            // Ocultar spinner
            spinner.style.display = 'none';
            texto.textContent = 'Generar';
        }
    }

    async exportarReportes(formato) {
        try {
            // Obtener reportes actuales con filtros aplicados
            const filtrosQuery = new URLSearchParams();
            
            if (this.filtros.id_categoria) {
                filtrosQuery.append('id_categoria', this.filtros.id_categoria);
            }
            if (this.filtros.tipo) {
                filtrosQuery.append('tipo', this.filtros.tipo);
            }
            if (this.filtros.fecha_inicio) {
                filtrosQuery.append('fecha_inicio', this.filtros.fecha_inicio);
            }
            if (this.filtros.fecha_fin) {
                filtrosQuery.append('fecha_fin', this.filtros.fecha_fin);
            }
            
            // Construir URL de exportación
            let url = `/reportes/api/reportes/exportar?formato=${formato}`;
            if (filtrosQuery.toString()) {
                url += '&' + filtrosQuery.toString();
            }

            // Crear mensaje de exportación
            const categoriaNombre = this.filtros.id_categoria 
                ? (this.categorias.find(c => c.id_categoria == this.filtros.id_categoria)?.nombre || 'Todos')
                : 'Todos';
            
            const mensaje = `
                <div class="text-center">
                    <i class="fas fa-file-${formato === 'pdf' ? 'pdf' : 'excel'} text-${formato === 'pdf' ? 'red' : 'green'}-600 text-6xl mb-4"></i>
                    <h3 class="text-xl font-bold mb-2">Exportando ${this.reportes.length} reportes</h3>
                    <p class="text-gray-600 mb-4">Categoría: ${categoriaNombre}</p>
                    <p class="text-sm text-gray-500">Formato: ${formato.toUpperCase()}</p>
                </div>
            `;

            // Por ahora, simular exportación
            this.mostrarExito(`Exportando ${this.reportes.length} reportes a ${formato.toUpperCase()}`);
            
            // Cerrar modal
            document.getElementById('modalExportacion').classList.remove('show');

            // Nota: Implementación real requeriría endpoints backend para generar PDF/Excel
            console.log('URL de exportación:', url);
            console.log('Reportes a exportar:', this.reportes);
            
            // Crear tabla temporal para simular exportación
            this.simularExportacion(formato);

        } catch (error) {
            console.error('Error al exportar:', error);
            this.mostrarError('Error al exportar los reportes');
        }
    }

    simularExportacion(formato) {
        // Crear datos para exportar
        const datos = this.reportes.map(r => ({
            'Código': r.codigo || 'N/A',
            'Nombre': r.nombre || 'Sin nombre',
            'Categoría': r.categoria || 'Sin categoría',
            'Tipo': r.tipo || 'N/A',
            'Empleado': r.empleado || 'No asignado',
            'Fecha': r.fecha_formateada || 'N/A',
            'Estado': r.estado || 'Pendiente',
            'Archivos': r.num_archivos || 0
        }));

        if (formato === 'excel') {
            // Convertir a CSV
            const csv = this.convertirACSV(datos);
            this.descargarArchivo(csv, 'reportes.csv', 'text/csv');
        } else if (formato === 'pdf') {
            // Por ahora mostrar mensaje
            alert('La exportación a PDF requiere implementación backend. Los datos están listos para exportar.');
            console.table(datos);
        }
    }

    convertirACSV(datos) {
        if (!datos || datos.length === 0) return '';
        
        const headers = Object.keys(datos[0]);
        const csvHeaders = headers.join(',');
        
        const csvRows = datos.map(row => {
            return headers.map(header => {
                const value = row[header];
                // Escapar comillas y valores con comas
                return `"${String(value).replace(/"/g, '""')}"`;
            }).join(',');
        });
        
        return [csvHeaders, ...csvRows].join('\n');
    }

    descargarArchivo(contenido, nombreArchivo, tipoMime) {
        const blob = new Blob([contenido], { type: tipoMime });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = nombreArchivo;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    // ============================================
    // NUEVAS FUNCIONALIDADES PARA DETALLE
    // ============================================

    previsualizarArchivo(idArchivo, nombreArchivo, rutaArchivo) {
        const vistaPrevia = document.getElementById('vistaPrevia');
        const extension = nombreArchivo.split('.').pop().toLowerCase();
        
        // Construir URL del archivo
        const urlArchivo = `/reportes/api/reportes/descargar-archivo/${idArchivo}`;
        
        // Mostrar indicador de carga
        vistaPrevia.innerHTML = `
            <div class="text-center">
                <i class="fas fa-spinner fa-spin text-cyan-600 text-6xl mb-4"></i>
                <p class="text-gray-600">Cargando vista previa...</p>
                <div class="w-48 mx-auto mt-4 bg-gray-200 rounded-full h-2">
                    <div class="carga-previa bg-cyan-500 h-2 rounded-full animate-pulse" style="width: 60%"></div>
                </div>
            </div>
        `;
        
        // Simular carga y luego mostrar contenido
        setTimeout(() => {
            if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(extension)) {
                // Previsualizar imagen con lazy load
                vistaPrevia.innerHTML = `
                    <div class="w-full h-full flex flex-col items-center justify-center gap-3">
                        <div class="relative max-w-full max-h-full">
                            <img src="${urlArchivo}" 
                                 alt="${nombreArchivo}" 
                                 class="max-w-full max-h-96 object-contain rounded-lg shadow-2xl border-4 border-white"
                                 onload="this.classList.add('animate-fade-in')"
                                 onerror="this.parentElement.innerHTML='<div class=\\'text-red-600\\'><i class=\\'fas fa-exclamation-circle text-4xl mb-2 block\\'></i><p>Error al cargar imagen</p></div>'">
                        </div>
                        <div class="flex gap-2 mt-2">
                            <a href="${urlArchivo}" download class="btn btn-sm bg-green-500 hover:bg-green-600 text-white">
                                <i class="fas fa-download mr-1"></i> Descargar
                            </a>
                            <a href="${urlArchivo}" target="_blank" class="btn btn-sm bg-blue-500 hover:bg-blue-600 text-white">
                                <i class="fas fa-external-link-alt mr-1"></i> Abrir
                            </a>
                        </div>
                    </div>
                `;
            } else if (extension === 'pdf') {
                // Previsualizar PDF con embed
                vistaPrevia.innerHTML = `
                    <div class="w-full h-full flex flex-col">
                        <div class="bg-gray-900 text-white px-4 py-2 rounded-t-lg flex items-center justify-between">
                            <span class="text-sm">
                                <i class="fas fa-file-pdf mr-2"></i>${nombreArchivo}
                            </span>
                            <a href="${urlArchivo}" target="_blank" class="text-xs bg-white text-gray-900 px-2 py-1 rounded hover:bg-gray-200">
                                <i class="fas fa-expand mr-1"></i> Pantalla completa
                            </a>
                        </div>
                        <iframe src="${urlArchivo}#toolbar=1&navpanes=1&scrollbar=1" 
                                class="w-full flex-1 rounded-b-lg border-2 border-gray-300"
                                style="min-height: 500px;"
                                frameborder="0">
                        </iframe>
                        <p class="text-center text-xs text-gray-500 mt-2">
                            <i class="fas fa-info-circle mr-1"></i>
                            Si no se visualiza correctamente, 
                            <a href="${urlArchivo}" target="_blank" class="text-cyan-600 hover:underline font-medium">haz clic aquí</a>
                        </p>
                    </div>
                `;
            } else {
                // Otros archivos - mostrar información
                const iconMap = {
                    'doc': 'fa-file-word',
                    'docx': 'fa-file-word',
                    'xls': 'fa-file-excel',
                    'xlsx': 'fa-file-excel',
                    'ppt': 'fa-file-powerpoint',
                    'pptx': 'fa-file-powerpoint',
                    'txt': 'fa-file-alt',
                    'zip': 'fa-file-archive',
                    'rar': 'fa-file-archive'
                };
                const icon = iconMap[extension] || 'fa-file';
                
                vistaPrevia.innerHTML = `
                    <div class="text-center">
                        <div class="inline-block p-8 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full mb-4">
                            <i class="fas ${icon} text-gray-600 text-6xl"></i>
                        </div>
                        <h3 class="font-bold text-lg text-gray-900 mb-2">${nombreArchivo}</h3>
                        <p class="text-gray-600 mb-6">Vista previa no disponible para archivos .${extension.toUpperCase()}</p>
                        <div class="flex gap-3 justify-center">
                            <a href="${urlArchivo}" download 
                               class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold rounded-lg transition-all shadow-md hover:shadow-lg">
                                <i class="fas fa-download mr-2"></i>
                                Descargar Archivo
                            </a>
                            <a href="${urlArchivo}" target="_blank" 
                               class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold rounded-lg transition-all shadow-md hover:shadow-lg">
                                <i class="fas fa-external-link-alt mr-2"></i>
                                Abrir en nueva ventana
                            </a>
                        </div>
                    </div>
                `;
            }
        }, 500); // Pequeño delay para mostrar el loading
    }

    mostrarModalEliminar() {
        const modal = document.getElementById('modalDetalle');
        const codigo = modal.dataset.codigoReporte || 'este reporte';
        
        document.getElementById('codigoEliminar').textContent = codigo;
        document.getElementById('modalConfirmarEliminar').classList.add('show');
    }

    async eliminarReporte() {
        const modalDetalle = document.getElementById('modalDetalle');
        const idReporte = modalDetalle.dataset.idReporte;
        
        if (!idReporte) {
            this.mostrarError('No se pudo identificar el reporte');
            return;
        }

        try {
            const response = await fetch(`/reportes/api/reportes/${idReporte}/eliminar`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.mostrarExito('Reporte eliminado exitosamente');
                
                // Cerrar modales
                document.getElementById('modalConfirmarEliminar').classList.remove('show');
                document.getElementById('modalDetalle').classList.remove('show');
                
                // Recargar lista de reportes
                await this.cargarReportes();
            } else {
                this.mostrarError(result.error || 'Error al eliminar el reporte');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error al eliminar el reporte');
        }
    }

    exportarDetalleAPDF() {
        const modalDetalle = document.getElementById('modalDetalle');
        const idReporte = modalDetalle.dataset.idReporte;
        
        if (!idReporte) {
            this.mostrarError('No se pudo identificar el reporte');
            return;
        }

        // Abrir en nueva ventana para descargar
        window.open(`/reportes/api/reportes/${idReporte}/descargar?formato=pdf`, '_blank');
        this.mostrarExito('Generando PDF...');
    }

    exportarDetalleAExcel() {
        const modalDetalle = document.getElementById('modalDetalle');
        const idReporte = modalDetalle.dataset.idReporte;
        const codigo = modalDetalle.dataset.codigoReporte || 'reporte';
        
        if (!idReporte) {
            this.mostrarError('No se pudo identificar el reporte');
            return;
        }

        // Obtener datos del reporte del DOM (sin Estado, sin Nombre)
        const datos = {
            'Código': document.getElementById('detalleCodigo').textContent,
            'Categoría': document.getElementById('detalleCategoria').textContent,
            'Tipo': document.getElementById('detalleTipo').textContent,
            'Fecha de Generación': document.getElementById('detalleFecha').textContent,
            'Hora de Generación': document.getElementById('detalleHora').textContent,
            'Empleado Responsable': document.getElementById('detalleEmpleado').textContent,
            'Descripción': document.getElementById('detalleDescripcion').textContent
        };

        // Convertir a CSV
        const csv = this.convertirObjetoACSV(datos);
        this.descargarArchivo(csv, `${codigo}.csv`, 'text/csv;charset=utf-8;');
        this.mostrarExito('Reporte exportado a Excel (CSV)');
    }

    convertirObjetoACSV(objeto) {
        const lineas = [];
        for (const [clave, valor] of Object.entries(objeto)) {
            lineas.push(`"${clave}","${String(valor).replace(/"/g, '""')}"`);
        }
        return lineas.join('\n');
    }
}

// Inicializar cuando el DOM esté listo
let reportesManager;
document.addEventListener('DOMContentLoaded', () => {
    reportesManager = new ReportesManager();
});
