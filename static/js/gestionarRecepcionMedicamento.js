document.addEventListener('DOMContentLoaded', () => {
    const modalRegistrar = document.getElementById('modalRegistrarRecepcion');
    const modalModificar = document.getElementById('modalModificarRecepcion');
    const modalEliminar = document.getElementById('modalEliminar');
    const modalVerDetalles = document.getElementById('modalVerDetalles');
    const btnRegistrar = document.getElementById('btnRegistrarRecepcion');
    const tablaBody = document.getElementById('tabla-recepciones-body');
    const formRegistrar = document.getElementById('formRegistrarRecepcion');
    const formModificar = document.getElementById('formModificarRecepcion');

    // Abrir modal registrar
    if (btnRegistrar) {
        btnRegistrar.addEventListener('click', () => modalRegistrar.classList.add('show'));
    }

    // Cerrar modales (botones .close)
    document.addEventListener('click', (e) => {
        if (e.target.matches('.close')) {
            [modalRegistrar, modalModificar, modalEliminar, modalVerDetalles].forEach(m => m && m.classList.remove('show'));
        }
    });

    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', (e) => {
        [modalRegistrar, modalModificar, modalEliminar, modalVerDetalles].forEach(m => {
            if (m && e.target === m) m.classList.remove('show');
        });
    });

    // Cargar medicamentos y poblar tabla
    async function cargarMedicamentos() {
        try {
            const resp = await fetch('/farmacia/api/medicamentos', { credentials: 'same-origin' });
            if (!resp.ok) throw new Error('Error al obtener medicamentos');
            const medicamentos = await resp.json();
            renderTabla(medicamentos);
        } catch (err) {
            console.error(err);
        }
    }

    function renderTabla(medicamentos) {
        if (!tablaBody) return;
        tablaBody.innerHTML = '';
        if (!medicamentos || medicamentos.length === 0) {
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">No se encontraron recepciones</td>
                </tr>`;
            return;
        }

        medicamentos.forEach(m => {
            const idDisplay = `REC-${String(m.id_medicamento).padStart(3, '0')}`;
            const tr = document.createElement('tr');
            tr.dataset.id = idDisplay;
            tr.dataset.idMedicamento = m.id_medicamento;
            tr.dataset.medicamento = m.nombre || '';
            tr.dataset.descripcion = m.descripcion || '';
            tr.dataset.cantidad = m.stock != null ? String(m.stock) : '';
            tr.dataset.fechaRegistro = m.fecha_registro || '';
            tr.dataset.fechaVencimiento = m.fecha_vencimiento || '';

            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${idDisplay}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${escapeHtml(m.nombre)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${escapeHtml(m.descripcion || '')}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${m.stock ?? ''}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${m.fecha_registro || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${m.fecha_vencimiento || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                    <button class="ver-detalle text-cyan-600 hover:text-cyan-900 mr-3" title="Ver detalles"> <i class="fas fa-eye"></i> </button>
                    <button class="btn-editar text-blue-600 hover:text-blue-900 mr-3" title="Editar"> <i class="fas fa-edit"></i> </button>
                </td>
            `;
            tablaBody.appendChild(tr);
        });
    }

    // Delegación de eventos en tabla
    if (tablaBody) {
        tablaBody.addEventListener('click', (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            const tr = btn.closest('tr');
            if (!tr) return;
            if (btn.classList.contains('ver-detalle')) {
                abrirDetalle(tr);
            } else if (btn.classList.contains('btn-editar')) {
                abrirEditar(tr);
            } 
        });
    }

    function abrirDetalle(tr) {
        if (!modalVerDetalles) return;
        setText('detalleId', tr.dataset.id);
        setText('detalleNombre', tr.dataset.medicamento);
        setText('detalleDescripcion', tr.dataset.descripcion);
        setText('detalleStock', tr.dataset.cantidad);
        setText('detalleFechaRegistro', tr.dataset.fechaRegistro);
        setText('detalleFechaVencimiento', tr.dataset.fechaVencimiento);
        modalVerDetalles.classList.add('show');
    }

    function abrirEditar(tr) {
        if (!modalModificar) return;
        document.getElementById('idMedicamento').value = tr.dataset.idMedicamento || '';
        document.getElementById('nombreMedicamentoEdit').value = tr.dataset.medicamento || '';
        document.getElementById('stockEdit').value = tr.dataset.cantidad || '';
        document.getElementById('fechaRegistroEdit').value = tr.dataset.fechaRegistro || '';
        document.getElementById('fechaVencimientoEdit').value = tr.dataset.fechaVencimiento || '';
        document.getElementById('descripcionEdit').value = tr.dataset.descripcion || '';
        modalModificar.classList.add('show');

        // Asegurar validación y configuración del input stock en el modal de modificar
        const stockEditInput = document.getElementById('stockEdit');
        if (stockEditInput) {
            stockEditInput.setAttribute('min', '1');
            stockEditInput.setAttribute('step', '1');
            // eliminar decimales pegados por el usuario al escribir
            stockEditInput.addEventListener('input', () => {
                const v = stockEditInput.value;
                if (v.includes('.')) {
                    stockEditInput.value = Math.trunc(Number(v)) || '';
                }
                // evitar valores negativos o cero en edición
                if (stockEditInput.value !== '' && Number(stockEditInput.value) < 1) {
                    stockEditInput.value = '1';
                }
            }, { once: false });
        }
    }

    function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text || '';
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/[&<>"'`=\/]/g, s => ({
            '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','`':'&#96;','=':'&#61;','/':'&#47;'
        })[s]);
    }

    // Registrar medicamento (POST) - validar entero >=1
    if (formRegistrar) {
        // configurar input stock del modal registrar para mejor UX
        const stockInput = document.getElementById('stock');
        if (stockInput) {
            stockInput.setAttribute('min', '1');
            stockInput.setAttribute('step', '1');
            stockInput.addEventListener('input', () => {
                const v = stockInput.value;
                if (v.includes('.')) {
                    stockInput.value = Math.trunc(Number(v)) || '';
                }
                if (stockInput.value !== '' && Number(stockInput.value) < 1) {
                    stockInput.value = '1';
                }
            }, { once: false });
        }

        formRegistrar.addEventListener('submit', async (e) => {
            e.preventDefault();
            const nombre = document.getElementById('nombreMedicamento').value.trim();
            const descripcion = document.getElementById('descripcion').value.trim();
            const stockVal = document.getElementById('stock').value;
            const fechaVencimiento = document.getElementById('fecha_vencimiento').value;

            if (!nombre || stockVal === '' || !fechaVencimiento) {
                alert('Complete los campos obligatorios: nombre, stock, fecha de vencimiento.');
                return;
            }

            const stockNum = Number(stockVal);
            if (!Number.isInteger(stockNum) || stockNum < 1) {
                alert('Stock debe ser un número entero mayor o igual a 1.');
                return;
            }

            try {
                const resp = await fetch('/farmacia/api/medicamentos/crear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ nombre, descripcion, stock: stockNum, fecha_vencimiento: fechaVencimiento })
                });
                const data = await resp.json();
                if (resp.ok) {
                    alert('Recepción registrada correctamente');
                    formRegistrar.reset();
                    modalRegistrar.classList.remove('show');
                    await cargarMedicamentos();
                } else {
                    console.error(data);
                    alert(data.error || 'Error al registrar medicamento');
                }
            } catch (err) {
                console.error(err);
                alert('Error de conexión al servidor');
            }
        });
    }

    // Modificar medicamento (PUT) - validar entero >=1
    if (formModificar) {
        formModificar.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('idMedicamento').value;
            const nombre = document.getElementById('nombreMedicamentoEdit').value.trim();
            const stockVal = document.getElementById('stockEdit').value;
            const fechaVencimiento = document.getElementById('fechaVencimientoEdit').value;
            const descripcion = document.getElementById('descripcionEdit').value.trim();

            if (!id || !nombre || stockVal === '' || !fechaVencimiento) {
                alert('Complete los campos obligatorios para modificar.');
                return;
            }

            const stockNum = Number(stockVal);
            if (!Number.isInteger(stockNum) || stockNum < 1) {
                alert('Stock debe ser un número entero mayor o igual a 1.');
                return;
            }

            try {
                const resp = await fetch(`/farmacia/api/medicamentos/${encodeURIComponent(id)}/actualizar`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ nombre, descripcion, stock: stockNum, fecha_vencimiento: fechaVencimiento })
                });
                const data = await resp.json();
                if (resp.ok) {
                    alert('Recepción modificada exitosamente');
                    modalModificar.classList.remove('show');
                    await cargarMedicamentos();
                } else {
                    console.error(data);
                    alert(data.error || 'Error al modificar medicamento');
                }
            } catch (err) {
                console.error(err);
                alert('Error de conexión al servidor');
            }
        });
    }

    // Limpiar filtros
    const btnLimpiar = document.getElementById('btnLimpiar');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', (ev) => {
            ev.preventDefault();
            const formFiltros = document.getElementById('formFiltros');
            if (formFiltros) formFiltros.reset();
            cargarMedicamentos();
        });
    }

    // Inicializar
    cargarMedicamentos();
});