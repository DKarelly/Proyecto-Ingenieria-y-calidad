console.log('🔵 Script cargado');

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🟢 DOMContentLoaded disparado');
    
    const tablaBody = document.getElementById('tabla-recepciones-body');
    const modalRegistrar = document.getElementById('modalRegistrarRecepcion');
    const modalModificar = document.getElementById('modalModificarRecepcion');
    const modalVerDetalles = document.getElementById('modalVerDetalles');
    const btnRegistrar = document.getElementById('btnRegistrarRecepcion');
    const formRegistrar = document.getElementById('formRegistrarRecepcion');
    const formModificar = document.getElementById('formModificarRecepcion');

    console.log('📦 Elementos encontrados:', {
        tablaBody: !!tablaBody,
        modalRegistrar: !!modalRegistrar,
        btnRegistrar: !!btnRegistrar
    });

    if (!tablaBody) {
        console.error('❌ tbody NO encontrado');
        return;
    }

    // ==================== FUNCIONES AUXILIARES ====================
    
    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text || '';
    }

    // ==================== CARGAR MEDICAMENTOS ====================
    
    async function cargarMedicamentos() {
        console.log('🔄 Iniciando carga de medicamentos...');
        
        try {
            console.log('📡 Fetch a /farmacia/api/medicamentos');
            const resp = await fetch('/farmacia/api/medicamentos', { 
                credentials: 'same-origin' 
            });
            
            console.log('📊 Status:', resp.status);
            
            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status}`);
            }
            
            const medicamentos = await resp.json();
            console.log('✅ Medicamentos recibidos:', medicamentos.length);

            // Ordenar
            medicamentos.sort((a, b) => a.id_medicamento - b.id_medicamento);

            // Guardar globalmente
            window.medicamentos = medicamentos;

            // Poblar datalist para autocompletar
            const datalist = document.getElementById('medicamentos-list');
            if (datalist) {
                datalist.innerHTML = '';
                medicamentos.forEach(m => {
                    const option = document.createElement('option');
                    option.value = m.nombre;
                    datalist.appendChild(option);
                });
            }

            // Notificaciones
            mostrarNotificaciones(medicamentos);

            // ✅ INICIALIZAR PAGINACIÓN
            if (typeof inicializarPaginacion === 'function') {
                console.log('🔧 Inicializando paginación...');
                inicializarPaginacion({
                    datos: medicamentos,
                    registrosPorPagina: 10,
                    renderFuncion: renderTabla,
                    ids: {
                        inicioRango: 'inicio-rango',
                        finRango: 'fin-rango',
                        totalRegistros: 'total-registros',
                        paginacionNumeros: 'paginacionNumeros'
                    }
                });
            } else {
                console.warn('⚠️ paginacion2.js no cargado, renderizando sin paginación');
                renderTabla(medicamentos);
                actualizarContadores(medicamentos.length, medicamentos.length);
            }

            // Inicializar filtro de búsqueda
            inicializarFiltroBusqueda();

        } catch (err) {
            console.error('❌ Error:', err);
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        Error: ${err.message}
                    </td>
                </tr>
            `;
        }
    }

    function inicializarFiltroBusqueda() {
        const filtroInput = document.getElementById('filtroMedicamento');
        const btnLimpiar = document.getElementById('btnLimpiar');

        if (filtroInput) {
            filtroInput.addEventListener('input', (e) => {
                const termino = e.target.value.toLowerCase().trim();
                let datosFiltrados = window.medicamentos;

                if (termino) {
                    datosFiltrados = window.medicamentos.filter(m =>
                        m.nombre.toLowerCase().includes(termino)
                    );
                }

                // Reinicializar paginación con datos filtrados
                if (typeof inicializarPaginacion === 'function') {
                    inicializarPaginacion({
                        datos: datosFiltrados,
                        registrosPorPagina: 10,
                        renderFuncion: renderTabla,
                        ids: {
                            inicioRango: 'inicio-rango',
                            finRango: 'fin-rango',
                            totalRegistros: 'total-registros',
                            paginacionNumeros: 'paginacionNumeros'
                        }
                    });
                } else {
                    renderTabla(datosFiltrados);
                    actualizarContadores(datosFiltrados.length, datosFiltrados.length);
                }
            });
        }

        if (btnLimpiar) {
            btnLimpiar.addEventListener('click', () => {
                filtroInput.value = '';
                // Reinicializar paginación con todos los datos
                if (typeof inicializarPaginacion === 'function') {
                    inicializarPaginacion({
                        datos: window.medicamentos,
                        registrosPorPagina: 10,
                        renderFuncion: renderTabla,
                        ids: {
                            inicioRango: 'inicio-rango',
                            finRango: 'fin-rango',
                            totalRegistros: 'total-registros',
                            paginacionNumeros: 'paginacionNumeros'
                        }
                    });
                } else {
                    renderTabla(window.medicamentos);
                    actualizarContadores(window.medicamentos.length, window.medicamentos.length);
                }
            });
        }
    }

    function renderTabla(medicamentos) {
        console.log('🎨 Renderizando', medicamentos.length, 'medicamentos');

        tablaBody.innerHTML = '';

        if (!medicamentos || medicamentos.length === 0) {
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                        No hay medicamentos
                    </td>
                </tr>
            `;
            return;
        }

        medicamentos.forEach((m, i) => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 transition-colors';
            
            tr.dataset.idMedicamento = m.id_medicamento;
            tr.dataset.medicamento = m.nombre || '';
            tr.dataset.descripcion = m.descripcion || '';
            tr.dataset.cantidad = m.stock || '0';
            tr.dataset.fechaRegistro = m.fecha_registro || '';
            tr.dataset.fechaVencimiento = m.fecha_vencimiento || '';

            tr.innerHTML = `
                <td class="px-6 py-4 text-sm font-medium text-gray-900">${m.id_medicamento}</td>
                <td class="px-6 py-4 text-sm text-gray-900">${escapeHtml(m.nombre)}</td>
                <td class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title="${escapeHtml(m.descripcion || '')}">${escapeHtml(m.descripcion || 'Sin descripción')}</td>
                <td class="px-6 py-4 text-sm text-gray-900 text-center">
                    <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full font-semibold">${m.stock || 0}</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900">${m.fecha_registro || 'N/A'}</td>
                <td class="px-6 py-4 text-sm text-gray-900">${m.fecha_vencimiento || 'N/A'}</td>
                <td class="px-6 py-4 text-center text-sm">
                    <button class="ver-detalle text-cyan-600 hover:text-cyan-900 mr-3 transition-colors" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-editar text-blue-600 hover:text-blue-900 transition-colors" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            `;

            tablaBody.appendChild(tr);
        });

        console.log('✅ Tabla renderizada con', medicamentos.length, 'filas');
    }

    function actualizarContadores(inicio, fin) {
        const inicioRango = document.getElementById('inicio-rango');
        const finRango = document.getElementById('fin-rango');
        const totalRegistros = document.getElementById('total-registros');
        const total = window.medicamentos ? window.medicamentos.length : 0;

        if (inicioRango) inicioRango.textContent = total > 0 ? inicio : '0';
        if (finRango) finRango.textContent = fin;
        if (totalRegistros) totalRegistros.textContent = total;
    }

    function mostrarNotificaciones(medicamentos) {
        const contenedor = document.getElementById('notificaciones-vencimiento');
        if (!contenedor) return;

        contenedor.innerHTML = '';
        const hoy = new Date();
        const en30Dias = new Date();
        en30Dias.setDate(hoy.getDate() + 30);

        const porVencer = medicamentos.filter(m => {
            if (!m.fecha_vencimiento) return false;
            const fv = new Date(m.fecha_vencimiento);
            return fv >= hoy && fv <= en30Dias;
        });

        porVencer.forEach(m => {
            const fv = new Date(m.fecha_vencimiento);
            const dias = Math.ceil((fv - hoy) / (1000 * 60 * 60 * 24));
            
            const div = document.createElement('div');
            div.className = 'bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-400 p-4 rounded-lg shadow-sm';
            div.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <i class="fas fa-exclamation-triangle text-yellow-400 text-xl"></i>
                    </div>
                    <div class="ml-3 flex-1">
                        <h3 class="text-sm font-medium text-yellow-800">
                            <i class="fas fa-pills mr-1"></i>
                            ${escapeHtml(m.nombre)}
                        </h3>
                        <div class="mt-2 text-sm text-yellow-700">
                            <p><i class="fas fa-clock mr-1"></i> Vence en ${dias} día${dias !== 1 ? 's' : ''}</p>
                            <p><i class="fas fa-boxes mr-1"></i> Stock actual: ${m.stock || 0}</p>
                        </div>
                    </div>
                </div>
            `;
            contenedor.appendChild(div);
        });
    }

    // ==================== VALIDACIÓN DE STOCK ====================

    function validarStockInput(input) {
        input.addEventListener('input', (e) => {
            let value = e.target.value;
            // Remover cualquier carácter que no sea dígito
            value = value.replace(/[^0-9]/g, '');
            // Asegurar que no sea vacío o cero
            if (value === '' || parseInt(value) === 0) {
                value = '';
            }
            e.target.value = value;
        });

        input.addEventListener('keydown', (e) => {
            // Prevenir la tecla de menos (-)
            if (e.key === '-' || e.keyCode === 189) {
                e.preventDefault();
            }
        });
    }

    // ==================== VALIDACIÓN DE FECHAS ====================

    function validarFechaVencimiento(input) {
        input.addEventListener('input', (e) => {
            const hoyActual = new Date();
            const hoyActualStr = hoyActual.getFullYear() + '-' + String(hoyActual.getMonth() + 1).padStart(2, '0') + '-' + String(hoyActual.getDate()).padStart(2, '0');
            if (e.target.value < hoyActualStr) {
                e.target.value = hoyActualStr;
            }
        });
        input.addEventListener('change', (e) => {
            const hoyActual = new Date();
            const hoyActualStr = hoyActual.getFullYear() + '-' + String(hoyActual.getMonth() + 1).padStart(2, '0') + '-' + String(hoyActual.getDate()).padStart(2, '0');
            if (e.target.value < hoyActualStr) {
                e.target.value = hoyActualStr;
                alert('La fecha de vencimiento no puede ser anterior a hoy.');
            }
        });
        input.addEventListener('mousedown', (e) => {
            const hoyActual = new Date();
            const hoyActualStr = hoyActual.getFullYear() + '-' + String(hoyActual.getMonth() + 1).padStart(2, '0') + '-' + String(hoyActual.getDate()).padStart(2, '0');
            e.target.setAttribute('min', hoyActualStr);
        });
        input.addEventListener('focus', (e) => {
            const hoyActual = new Date();
            const hoyActualStr = hoyActual.getFullYear() + '-' + String(hoyActual.getMonth() + 1).padStart(2, '0') + '-' + String(hoyActual.getDate()).padStart(2, '0');
            e.target.setAttribute('min', hoyActualStr);
        });
        input.addEventListener('click', (e) => {
            const hoyActual = new Date();
            const hoyActualStr = hoyActual.getFullYear() + '-' + String(hoyActual.getMonth() + 1).padStart(2, '0') + '-' + String(hoyActual.getDate()).padStart(2, '0');
            e.target.setAttribute('min', hoyActualStr);
        });
    }

    // Aplicar validación a los inputs de stock
    const stockInput = document.getElementById('stock');
    const stockEditInput = document.getElementById('stockEdit');
    if (stockInput) validarStockInput(stockInput);
    if (stockEditInput) validarStockInput(stockEditInput);

    // Aplicar validación a las fechas de vencimiento
    const fechaVencimientoInput = document.getElementById('fecha_vencimiento');
    const fechaVencimientoEditInput = document.getElementById('fechaVencimientoEdit');
    if (fechaVencimientoInput) validarFechaVencimiento(fechaVencimientoInput);
    if (fechaVencimientoEditInput) validarFechaVencimiento(fechaVencimientoEditInput);

    // ==================== EVENTOS MODALES ====================

    if (btnRegistrar) {
        btnRegistrar.addEventListener('click', () => {
            if (modalRegistrar) {
                // Repopular datalist para autocompletar
                const datalist = document.getElementById('medicamentos-list');
                if (datalist && window.medicamentos) {
                    datalist.innerHTML = '';
                    window.medicamentos.forEach(m => {
                        const option = document.createElement('option');
                        option.value = m.nombre;
                        datalist.appendChild(option);
                    });
                }
                modalRegistrar.classList.add('show');
            }
        });
    }

    document.addEventListener('click', (e) => {
        if (e.target.matches('.close') || e.target.id === 'closeDetalles' || e.target.id === 'btnCerrarDetalles') {
            [modalRegistrar, modalModificar, modalVerDetalles].forEach(m => {
                if (m) m.classList.remove('show');
            });
        }
    });

    window.addEventListener('click', (e) => {
        [modalRegistrar, modalModificar, modalVerDetalles].forEach(m => {
            if (m && e.target === m) m.classList.remove('show');
        });
    });

    if (tablaBody) {
        tablaBody.addEventListener('click', (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            
            const tr = btn.closest('tr');
            if (!tr) return;

            if (btn.classList.contains('ver-detalle')) {
                if (!modalVerDetalles) return;
                setText('detalleNombre', tr.dataset.medicamento);
                setText('detalleDescripcion', tr.dataset.descripcion);
                setText('detalleStock', tr.dataset.cantidad);
                setText('detalleFechaRegistro', tr.dataset.fechaRegistro);
                setText('detalleFechaVencimiento', tr.dataset.fechaVencimiento);
                modalVerDetalles.classList.add('show');
            } else if (btn.classList.contains('btn-editar')) {
                if (!modalModificar) return;
                document.getElementById('idMedicamento').value = tr.dataset.idMedicamento;
                document.getElementById('nombreMedicamentoEdit').value = tr.dataset.medicamento;
                document.getElementById('stockEdit').value = tr.dataset.cantidad;
                document.getElementById('fechaRegistroEdit').value = tr.dataset.fechaRegistro;
                const fechaVencimientoEdit = document.getElementById('fechaVencimientoEdit');
                const hoy = new Date();
                const hoyStr = hoy.toISOString().split('T')[0];
                fechaVencimientoEdit.setAttribute('min', hoyStr);
                const originalDate = new Date(tr.dataset.fechaVencimiento);
                const maxDate = originalDate > hoy ? originalDate : hoy;
                fechaVencimientoEdit.value = maxDate.toISOString().split('T')[0];
                document.getElementById('descripcionEdit').value = tr.dataset.descripcion;
                modalModificar.classList.add('show');
            }
        });
    }

    // ==================== FORMULARIOS ====================
    
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', async (e) => {
            e.preventDefault();

            const nombre = document.getElementById('nombreMedicamento').value.trim();
            const descripcion = document.getElementById('descripcion').value.trim();
            const stock = parseInt(document.getElementById('stock').value);
            const fecha_vencimiento = document.getElementById('fecha_vencimiento').value;

            if (!nombre || !stock || !fecha_vencimiento) {
                alert('Complete los campos obligatorios');
                return;
            }

            if (stock <= 0) {
                alert('El stock debe ser mayor a 0');
                return;
            }

            try {
                const resp = await fetch('/farmacia/api/medicamentos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ nombre, descripcion, stock, fecha_vencimiento })
                });
                
                const data = await resp.json();
                
                if (resp.ok) {
                    alert('Medicamento registrado correctamente');
                    formRegistrar.reset();
                    modalRegistrar.classList.remove('show');
                    await cargarMedicamentos();
                } else {
                    alert(data.error || 'Error al registrar');
                }
            } catch (err) {
                console.error(err);
                alert('Error de conexión');
            }
        });
    }

    if (formModificar) {
        formModificar.addEventListener('submit', async (e) => {
            e.preventDefault();

            const id = document.getElementById('idMedicamento').value;
            const nombre = document.getElementById('nombreMedicamentoEdit').value.trim();
            const descripcion = document.getElementById('descripcionEdit').value.trim();
            const stock = parseInt(document.getElementById('stockEdit').value);
            const fecha_vencimiento = document.getElementById('fechaVencimientoEdit').value;

            if (!id || !nombre || !stock || !fecha_vencimiento) {
                alert('Complete los campos obligatorios');
                return;
            }

            if (stock <= 0) {
                alert('El stock debe ser mayor a 0');
                return;
            }

            try {
                const resp = await fetch(`/farmacia/api/medicamentos/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ nombre, descripcion, stock, fecha_vencimiento })
                });
                
                const data = await resp.json();
                
                if (resp.ok) {
                    alert('Medicamento modificado correctamente');
                    modalModificar.classList.remove('show');
                    await cargarMedicamentos();
                } else {
                    alert(data.error || 'Error al modificar');
                }
            } catch (err) {
                console.error(err);
                alert('Error de conexión');
            }
        });
    }

    // ==================== INICIALIZAR ====================
    
    console.log('🚀 Inicializando...');
    await cargarMedicamentos();
});