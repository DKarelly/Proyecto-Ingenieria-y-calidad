document.addEventListener('DOMContentLoaded', () => {
    // Elementos del DOM
    const modalRegistrar = document.getElementById('modalRegistrarEntrega');
    const modalModificar = document.getElementById('modalModificarEntrega');
    const modalDetalles = document.getElementById('modalVerDetalles');
    const formRegistrar = document.getElementById('formRegistrarEntrega');
    const formModificar = document.getElementById('formModificarEntrega');
    const tablaEntregas = document.getElementById('tabla-entregas-body');
    
    // Variables para autocompletado
    let timeoutBusqueda = null;
    let elementoSeleccionado = {
        paciente: null,
        empleado: null,
        medicamento: null
    };

    // Inicialización
    inicializarAutocompletado();
    cargarEntregas();

    // Configuración de autocompletado
    function inicializarAutocompletado() {
        const campos = {
            paciente: {
                input: document.getElementById('filtroPaciente'),
                formInput: document.getElementById('paciente'),
                formInputEdit: document.getElementById('pacienteEdit')
            },
            empleado: {
                input: document.getElementById('filtroEmpleado'),
                formInput: document.getElementById('empleado'),
                formInputEdit: document.getElementById('empleadoEdit')
            },
            medicamento: {
                input: document.getElementById('filtroMedicamento'),
                formInput: document.getElementById('medicamento'),
                formInputEdit: document.getElementById('medicamentoEdit')
            }
        };

        Object.entries(campos).forEach(([tipo, config]) => {
            [config.input, config.formInput, config.formInputEdit].filter(Boolean).forEach(input => {
                if (!input) return;

                // Agregar evento input para búsqueda
                input.addEventListener('input', function() {
                    clearTimeout(timeoutBusqueda);
                    const termino = this.value.trim();

                    if (termino.length < 2) {
                        ocultarSugerencias();
                        elementoSeleccionado[tipo] = null; // Limpiar selección si se borra
                        // Limpiar ID correspondiente
                        const idInput = input.id.replace(tipo, 'id_' + tipo);
                        const idElement = document.getElementById(idInput);
                        if (idElement) idElement.value = '';
                        return;
                    }

                    timeoutBusqueda = setTimeout(() => {
                        buscarElementos(tipo, termino, input);
                    }, 300);
                });

                // Prevenir envío de formulario al presionar enter en el input
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                    }
                });

                // Limpiar selección al borrar todo el contenido
                input.addEventListener('change', function() {
                    if (!this.value) {
                        elementoSeleccionado[tipo] = null;
                        // Limpiar ID correspondiente
                        const idInput = input.id.replace(tipo, 'id_' + tipo);
                        const idElement = document.getElementById(idInput);
                        if (idElement) idElement.value = '';
                    }
                });
            });
        });
    }
    async function buscarElementos(tipo, termino, input) {
        try {
            const response = await fetch(`/farmacia/api/${tipo}s/buscar?termino=${encodeURIComponent(termino)}`);
            if (!response.ok) throw new Error(`Error en búsqueda de ${tipo}`);
            const datos = await response.json();
            mostrarSugerencias(datos, tipo, input);
        } catch (error) {
            console.error('Error:', error);
            mostrarError(`Error al buscar ${tipo}s`);
        }
    }

    function mostrarSugerencias(datos, tipo, input) {
        ocultarSugerencias();
        if (!datos.length) return;

        const contenedor = document.createElement('div');
        contenedor.className = 'sugerencias absolute z-[1001] w-full bg-white border border-gray-300 rounded-lg shadow-lg mt-1 max-h-48 overflow-y-auto';

        datos.forEach(item => {
            const div = document.createElement('div');
            div.className = 'p-2 hover:bg-gray-100 cursor-pointer';

            let displayText = '';
            let idField = '';
            
            switch (tipo) {
                case 'paciente':
                    displayText = `${item.nombres} ${item.apellidos}`;
                    idField = 'id_paciente';
                    break;
                case 'empleado':
                    displayText = `${item.nombres} ${item.apellidos}${item.especialidad ? ` - ${item.especialidad}` : ''}`;
                    idField = 'id_empleado';
                    break;
                case 'medicamento':
                    displayText = `${item.nombre}${item.stock !== undefined ? ` (Stock: ${item.stock})` : ''}`;
                    idField = 'id_medicamento';
                    break;
            }

            div.textContent = displayText;
            div.addEventListener('click', () => {
                const valorMostrado = displayText.split('(')[0].trim();
                input.value = valorMostrado;
                elementoSeleccionado[tipo] = {
                    ...item,
                    [idField]: item[idField],
                    displayText: valorMostrado
                };

                // Actualizar campo relacionado en el formulario si existe
                const otroInput = input.id.includes('filtro') ?
                    document.getElementById(tipo) :
                    document.getElementById(`filtro${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`);

                if (otroInput && otroInput !== input) {
                    otroInput.value = valorMostrado;
                }

                // Actualizar campo ID correspondiente
                const idInput = input.id.replace(tipo, 'id_' + tipo);
                const idElement = document.getElementById(idInput);
                if (idElement) {
                    idElement.value = item[idField];
                }

                ocultarSugerencias();
            });

            contenedor.appendChild(div);
        });

        // Asegurar posicionamiento correcto
        const parent = input.parentNode;
        if (window.getComputedStyle(parent).position === 'static') {
            parent.style.position = 'relative';
        }
        parent.appendChild(contenedor);
    }

    // Gestión de entregas
    async function cargarEntregas() {
        try {
            const response = await fetch('/farmacia/api/entregas');
            if (!response.ok) throw new Error('Error al cargar entregas');
            const entregas = await response.json();
            renderizarEntregas(entregas);
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error al cargar las entregas');
        }
    }

    function renderizarEntregas(entregas) {
        if (!tablaEntregas) return;

        tablaEntregas.innerHTML = '';
        if (!entregas.length) {
            tablaEntregas.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                        No hay entregas registradas
                    </td>
                </tr>
            `;
            return;
        }

        entregas.forEach(entrega => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50';
            tr.innerHTML = `
                <td class="px-6 py-4">${entrega.id}</td>
                <td class="px-6 py-4">${escapeHtml(entrega.paciente)}</td>
                <td class="px-6 py-4">${escapeHtml(entrega.empleado)}</td>
                <td class="px-6 py-4">${escapeHtml(entrega.medicamento)}</td>
                <td class="px-6 py-4 text-center">${entrega.cantidad}</td>
                <td class="px-6 py-4">${formatearFecha(entrega.fecha_entrega)}</td>
                <td class="px-6 py-4 text-center">
                    <button class="btn-editar text-yellow-600 hover:text-yellow-800 mx-1" data-id="${entrega.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-ver text-blue-600 hover:text-blue-800 mx-1" data-id="${entrega.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            tablaEntregas.appendChild(tr);
        });
    }

    // Registro de nueva entrega
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!validarFormulario()) return;

            try {
                const response = await fetch('/farmacia/api/entregas', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        id_paciente: elementoSeleccionado.paciente.id_paciente,
                        id_medicamento: elementoSeleccionado.medicamento.id_medicamento,
                        id_empleado: elementoSeleccionado.empleado.id_empleado,
                        cantidad: parseInt(document.getElementById('cantidad').value)
                    })
                });

                if (!response.ok) throw new Error('Error al registrar entrega');
                
                await cargarEntregas();
                cerrarModal(modalRegistrar);
                mostrarExito('Entrega registrada exitosamente');
                formRegistrar.reset();
                elementoSeleccionado = { paciente: null, empleado: null, medicamento: null };
            } catch (error) {
                console.error('Error:', error);
                mostrarError('Error al registrar la entrega');
            }
        });
    }

    // Funciones auxiliares
    function validarFormulario() {
        if (!elementoSeleccionado.paciente) {
            mostrarError('Seleccione un paciente');
            return false;
        }
        if (!elementoSeleccionado.medicamento) {
            mostrarError('Seleccione un medicamento');
            return false;
        }
        if (!elementoSeleccionado.empleado) {
            mostrarError('Seleccione un empleado');
            return false;
        }
        const cantidad = parseInt(document.getElementById('cantidad').value);
        if (isNaN(cantidad) || cantidad <= 0) {
            mostrarError('Ingrese una cantidad válida');
            return false;
        }
        return true;
    }

    function ocultarSugerencias() {
        document.querySelectorAll('.sugerencias').forEach(el => el.remove());
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function formatearFecha(fecha) {
        if (!fecha) return '-';
        return new Date(fecha).toLocaleDateString('es-ES');
    }

    function cerrarModal(modal) {
        if (modal) modal.classList.remove('show');
    }

    function mostrarError(mensaje) {
        // Implementar según tu sistema de notificaciones
        alert(mensaje);
    }

    function mostrarExito(mensaje) {
        // Implementar según tu sistema de notificaciones
        alert(mensaje);
    }

    // Eventos globales
    document.addEventListener('click', (e) => {
        if (!e.target.matches('input') && !e.target.closest('.sugerencias')) {
            ocultarSugerencias();
        }
    });

    const btnLimpiar = document.getElementById('btnLimpiar');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', () => {
            document.querySelectorAll('#formFiltros input').forEach(input => {
                input.value = '';
            });
            elementoSeleccionado = {
                paciente: null,
                empleado: null,
                medicamento: null
            };
            cargarEntregas();
        });
    }

    const btnRegistrar = document.getElementById('btnRegistrarEntrega');
    if (btnRegistrar) {
        btnRegistrar.addEventListener('click', () => {
            modalRegistrar.classList.add('show');
            // Limpiar formulario
            formRegistrar.reset();
            elementoSeleccionado = {
                paciente: null,
                empleado: null,
                medicamento: null
            };
        });
    }

    // Cerrar modales con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            [modalRegistrar, modalModificar, modalDetalles].forEach(modal => {
                if (modal) cerrarModal(modal);
            });
        }
    });

    // Eventos para botones de editar y ver
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-editar') || e.target.closest('.btn-editar')) {
            const id = e.target.closest('.btn-editar').dataset.id;
            editarEntrega(id);
        }
        if (e.target.classList.contains('btn-ver') || e.target.closest('.btn-ver')) {
            const id = e.target.closest('.btn-ver').dataset.id;
            verDetallesEntrega(id);
        }
        if (e.target.classList.contains('close') || e.target.closest('.close')) {
            [modalRegistrar, modalModificar, modalDetalles].forEach(modal => {
                if (modal) cerrarModal(modal);
            });
        }
    });

    // Función para editar entrega
    async function editarEntrega(id) {
        try {
            const response = await fetch(`/farmacia/api/entregas/${id}`);
            if (!response.ok) throw new Error('Error al cargar entrega');
            const entrega = await response.json();

            // Llenar formulario de edición
            document.getElementById('idEntrega').value = entrega.id;
            document.getElementById('pacienteEdit').value = entrega.paciente;
            document.getElementById('id_paciente_edit').value = entrega.id_paciente;
            document.getElementById('empleadoEdit').value = entrega.empleado;
            document.getElementById('id_empleado_edit').value = entrega.id_empleado;
            document.getElementById('medicamentoEdit').value = entrega.medicamento;
            document.getElementById('id_medicamento_edit').value = entrega.id_medicamento;
            document.getElementById('cantidadEdit').value = entrega.cantidad;

            // Establecer selección inicial para validación
            elementoSeleccionado.paciente = {
                id_paciente: entrega.id_paciente,
                displayText: entrega.paciente
            };
            elementoSeleccionado.empleado = {
                id_empleado: entrega.id_empleado,
                displayText: entrega.empleado
            };
            elementoSeleccionado.medicamento = {
                id_medicamento: entrega.id_medicamento,
                displayText: entrega.medicamento
            };

            modalModificar.classList.add('show');
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error al cargar la entrega para editar');
        }
    }

    // Función para ver detalles de entrega
    async function verDetallesEntrega(id) {
        try {
            const response = await fetch(`/farmacia/api/entregas/${id}`);
            if (!response.ok) throw new Error('Error al cargar entrega');
            const entrega = await response.json();

            // Llenar modal de detalles
            document.getElementById('detalleId').textContent = entrega.id;
            document.getElementById('detallePaciente').textContent = entrega.paciente;
            document.getElementById('detalleMedicamento').textContent = entrega.medicamento;
            document.getElementById('detalleCantidad').textContent = entrega.cantidad;
            document.getElementById('detalleFecha').textContent = formatearFecha(entrega.fecha_entrega);
            document.getElementById('detalleEmpleado').textContent = entrega.empleado;

            modalDetalles.classList.add('show');
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error al cargar los detalles de la entrega');
        }
    }

    // Modificación de entrega
    if (formModificar) {
        formModificar.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!validarFormularioEdit()) return;

            const id = document.getElementById('idEntrega').value;

            try {
                const response = await fetch(`/farmacia/api/entregas/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        id_empleado: parseInt(document.getElementById('id_empleado_edit').value),
                        id_paciente: parseInt(document.getElementById('id_paciente_edit').value),
                        id_medicamento: parseInt(document.getElementById('id_medicamento_edit').value),
                        cantidad: parseInt(document.getElementById('cantidadEdit').value)
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al modificar entrega');
                }

                await cargarEntregas();
                cerrarModal(modalModificar);
                mostrarExito('Entrega modificada exitosamente');
            } catch (error) {
                console.error('Error:', error);
                mostrarError(error.message);
            }
        });
    }

    // Función para validar formulario de edición
    function validarFormularioEdit() {
        const idPaciente = document.getElementById('id_paciente_edit').value;
        const idMedicamento = document.getElementById('id_medicamento_edit').value;
        const idEmpleado = document.getElementById('id_empleado_edit').value;
        const cantidad = parseInt(document.getElementById('cantidadEdit').value);

        if (!idPaciente) {
            mostrarError('Seleccione un paciente');
            return false;
        }
        if (!idMedicamento) {
            mostrarError('Seleccione un medicamento');
            return false;
        }
        if (!idEmpleado) {
            mostrarError('Seleccione un empleado');
            return false;
        }
        if (isNaN(cantidad) || cantidad <= 0) {
            mostrarError('Ingrese una cantidad válida');
            return false;
        }
        return true;
    }
});
