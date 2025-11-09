// Gestionar Programación JavaScript

// Variables de paginación para la tabla de horarios de empleados
let currentPage = 1;
const itemsPerPage = 3;

document.addEventListener('DOMContentLoaded', function() {
    // Elementos de modal
    const modalRegistrar = document.getElementById('modalRegistrarProgramacion');
    const modalModificar = document.getElementById('modalModificarProgramacion');
    const modalEliminar = document.getElementById('modalEliminar');

    // Elementos de botones
    const btnRegistrar = document.getElementById('btnRegistrarProgramacion');
    const btnLimpiar = document.getElementById('btnLimpiar');
    const btnBuscar = document.getElementById('btnBuscar');

    // Elementos de formularios
    const formRegistrar = document.getElementById('formRegistrarProgramacion');
    const formModificar = document.getElementById('formModificarProgramacion');

    // Botones de cerrar
    const closeButtons = document.querySelectorAll('.close');

    // Cuerpo de la tabla
    const tablaBody = document.getElementById('tabla-programacion-body');

    // Abrir modal de registrar
    if (btnRegistrar) {
        btnRegistrar.addEventListener('click', function() {
            modalRegistrar.classList.add('show');
            // Limpiar campos de empleado inicialmente
            document.getElementById('idEmpleado').value = '';
            document.getElementById('nombreEmpleado').value = '';
            document.getElementById('idHorario').value = '';
            // Cargar tipos de servicio y servicios
            loadTiposServicio('tipoServicioProgramacion');
            loadServicios('servicioProgramacion');
            // Cargar horarios activos de empleados
            populateHorarioEmpleado('tablaHorarioEmpleado');
        });
    }

    // Función para limpiar el formulario de registrar
    function clearRegistrarForm() {
        document.getElementById('fechaProgramacion').value = '';
        document.getElementById('horaInicio').value = '';
        document.getElementById('horaFin').value = '';
        document.getElementById('estadoProgramacion').selectedIndex = 0;
        document.getElementById('tipoServicioProgramacion').selectedIndex = 0;
        document.getElementById('servicioProgramacion').selectedIndex = 0;
        document.getElementById('idEmpleado').value = '';
        document.getElementById('nombreEmpleado').value = '';
        document.getElementById('idHorario').value = '';
        document.getElementById('tablaHorarioEmpleado').innerHTML = '';
        document.getElementById('suggestions-empleado').classList.add('hidden');
        // Remover paginación si existe
        const existingPagination = document.getElementById('pagination-controls-tablaHorarioEmpleado');
        if (existingPagination) {
            existingPagination.remove();
        }
        currentPage = 1;
    }

    // Función para limpiar el formulario de editar
    function clearEditarForm() {
        document.getElementById('idProgramacionEdit').value = '';
        document.getElementById('fechaProgramacionEdit').value = '';
        document.getElementById('horaInicioEdit').value = '';
        document.getElementById('horaFinEdit').value = '';
        document.getElementById('estadoProgramacionEdit').selectedIndex = 0;
        document.getElementById('tipoServicioProgramacionEdit').selectedIndex = 0;
        document.getElementById('servicioProgramacionEdit').selectedIndex = 0;
        document.getElementById('idEmpleadoEdit').value = '';
        document.getElementById('nombreEmpleadoEdit').value = '';
        document.getElementById('idHorarioEdit').value = '';
        document.getElementById('tablaHorarioEmpleadoEdit').innerHTML = '';
        document.getElementById('suggestions-empleado-edit').classList.add('hidden');
        // Remover paginación si existe
        const existingPagination = document.getElementById('pagination-controls-tablaHorarioEmpleadoEdit');
        if (existingPagination) {
            existingPagination.remove();
        }
        currentPage = 1;
    }

    // Cerrar modales
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.closest('#modalRegistrarProgramacion')) {
                clearRegistrarForm();
            }
            if (this.closest('#modalModificarProgramacion')) {
                clearEditarForm();
            }
            modalRegistrar.classList.remove('show');
            modalModificar.classList.remove('show');
            modalEliminar.classList.remove('show');
        });
    });

    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', function(event) {
        if (event.target === modalRegistrar) {
            clearRegistrarForm();
            modalRegistrar.classList.remove('show');
        }
        if (event.target === modalModificar) {
            clearEditarForm();
            modalModificar.classList.remove('show');
        }
        if (event.target === modalEliminar) {
            modalEliminar.classList.remove('show');
        }
    }); 

    // Event listener para el botón btnLimpiarRegistrar
    const btnLimpiarRegistrar = document.getElementById('btnLimpiarRegistrar');
    if (btnLimpiarRegistrar) {
        btnLimpiarRegistrar.addEventListener('click', function() {
            if (confirm('¿Está seguro que desea limpiar todos los campos?')) {
                clearRegistrarForm();
            }
        });
    }

    // Event listener para el botón btnLimpiarEditar
    const btnLimpiarEditar = document.getElementById('btnLimpiarEditar');
    if (btnLimpiarEditar) {
        btnLimpiarEditar.addEventListener('click', function() {
            if (confirm('¿Está seguro que desea limpiar todos los campos?')) {
                clearEditarForm();
            }
        });
    }

    // Event listener para el botón btnCancelarRegistrar
    const btnCancelarRegistrar = document.getElementById('btnCancelarRegistrar');
    if (btnCancelarRegistrar) {
        btnCancelarRegistrar.addEventListener('click', function() {
            clearRegistrarForm();
            modalRegistrar.classList.remove('show');
        });
    }

    // Event listener para el botón btnCancelarEditar
    const btnCancelarEditar = document.getElementById('btnCancelarEditar');
    if (btnCancelarEditar) {
        btnCancelarEditar.addEventListener('click', function() {
            clearEditarForm();
            modalModificar.classList.remove('show');
        });
    }

    // Envíos de formularios
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(formRegistrar);
            const data = {
                fecha: formData.get('fechaProgramacion'),
                hora_inicio: formData.get('horaInicio'),
                hora_fin: formData.get('horaFin'),
                id_servicio: formData.get('servicioProgramacion'),
                id_horario: formData.get('idHorario')
            };

            fetch('/admin/api/programaciones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('Programación registrada exitosamente');
                    clearRegistrarForm();
                    modalRegistrar.classList.remove('show');
                    loadProgramaciones(); // Recargar la tabla
                } else {
                    alert('Error: ' + result.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al registrar la programación');
            });
        });
    }

    if (formModificar) {
        formModificar.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(formModificar);
            const id = formData.get('idProgramacionEdit');
            const data = {
                fecha: formData.get('fechaProgramacionEdit'),
                hora_inicio: formData.get('horaInicioEdit'),
                hora_fin: formData.get('horaFinEdit'),
                id_servicio: formData.get('servicioProgramacionEdit'),
                estado: formData.get('estadoProgramacionEdit')
            };

            fetch(`/admin/api/programaciones/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('Programación modificada exitosamente');
                    modalModificar.classList.remove('show');
                    loadProgramaciones(); // Recargar la tabla
                } else {
                    alert('Error: ' + result.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al modificar la programación');
            });
        });
    }

    // Limpiar filtros
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', function() {
            document.getElementById('formFiltros').reset();
        });
    }

    // Event listeners para filtros dinámicos
    const filtroFechaInput = document.getElementById('filtroFecha');
    if (filtroFechaInput) {
        filtroFechaInput.addEventListener('change', function() {
            loadProgramaciones();
        });
    }

    const filtroTipoServicioSelect = document.getElementById('filtroTipoServicio');
    if (filtroTipoServicioSelect) {
        filtroTipoServicioSelect.addEventListener('change', function() {
            const selectedTipo = this.value;
            loadServicios('filtroServicio', selectedTipo || null);
            loadProgramaciones();
        });
    }

    const filtroServicioSelect = document.getElementById('filtroServicio');
    if (filtroServicioSelect) {
        filtroServicioSelect.addEventListener('change', function() {
            loadProgramaciones();
        });
    }

    const filtroEstadoSelect = document.getElementById('filtroEstado');
    if (filtroEstadoSelect) {
        filtroEstadoSelect.addEventListener('change', function() {
            loadProgramaciones();
        });
    }

    // Función para cargar sugerencias de empleados en filtros
    function loadEmployeeSuggestionsFiltro(inputValue) {
        const suggestionsDiv = document.getElementById('suggestions-empleado-filtro');
        suggestionsDiv.innerHTML = '';

        if (inputValue.length < 2) {
            suggestionsDiv.classList.add('hidden');
            return;
        }

        fetch('/admin/api/empleados')
            .then(response => response.json())
            .then(data => {
                const filteredEmployees = data.filter(employee => {
                    const fullName = `${employee.nombres || ''} ${employee.apellidos || ''}`.trim();
                    return fullName.toLowerCase().includes(inputValue.toLowerCase());
                });

                if (filteredEmployees.length > 0) {
                    filteredEmployees.forEach(employee => {
                        const fullName = `${employee.nombres || ''} ${employee.apellidos || ''}`.trim();
                        const suggestionItem = document.createElement('div');
                        suggestionItem.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
                        suggestionItem.textContent = fullName;
                        suggestionItem.addEventListener('click', function() {
                            document.getElementById('filtroNombreEmpleado').value = fullName;
                            document.getElementById('filtroIdEmpleado').value = employee.id_empleado;
                            suggestionsDiv.classList.add('hidden');
                            loadProgramaciones(); // Recargar programaciones al seleccionar empleado
                        });
                        suggestionsDiv.appendChild(suggestionItem);
                    });
                    suggestionsDiv.classList.remove('hidden');
                } else {
                    suggestionsDiv.classList.add('hidden');
                }
            })
            .catch(error => console.error('Error cargando empleados:', error));
    }

    // Event listener para el input filtroNombreEmpleado
    const filtroNombreEmpleadoInput = document.getElementById('filtroNombreEmpleado');
    if (filtroNombreEmpleadoInput) {
        // Usamos un timeout para debounce en input y recargar programaciones
        let debounceTimer;
        filtroNombreEmpleadoInput.addEventListener('input', function() {
            const nombre = this.value.trim();
            loadEmployeeSuggestionsFiltro(nombre);
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                loadProgramaciones();
            }, 500); // Espera 500ms después de que el usuario deje de escribir
            if (nombre.length < 2) {
                document.getElementById('filtroIdEmpleado').value = '';
                document.getElementById('suggestions-empleado-filtro').classList.add('hidden');
            }
        });

        // Ocultar sugerencias al hacer clic fuera
        document.addEventListener('click', function(event) {
            const suggestionsDiv = document.getElementById('suggestions-empleado-filtro');
            if (!filtroNombreEmpleadoInput.contains(event.target) && !suggestionsDiv.contains(event.target)) {
                suggestionsDiv.classList.add('hidden');
            }
        });
    }

    // Función para cargar tipos de servicio en el select
    function loadTiposServicio(selectId) {
        return fetch('/admin/api/tipos-servicio')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById(selectId);
                select.innerHTML = '<option value="" selected>Todos los tipos</option>';
                data.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo.id_tipo_servicio;
                    option.textContent = tipo.nombre;
                    select.appendChild(option);
                });
            })
            .catch(error => console.error('Error cargando tipos de servicio:', error));
    }

    // Función para cargar servicios en el select, filtrados por tipo si se especifica
    function loadServicios(selectId, tipoServicioId = null) {
        let url = '/admin/api/servicios';
        if (tipoServicioId) {
            url += `?tipo_servicio=${tipoServicioId}`;
        }
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById(selectId);
                select.innerHTML = '<option value="" disabled selected>Seleccione un servicio</option>';
                data.forEach(servicio => {
                    const option = document.createElement('option');
                    option.value = servicio.id_servicio;
                    option.textContent = servicio.nombre;
                    select.appendChild(option);
                });
            })
            .catch(error => console.error('Error cargando servicios:', error));
    }

    // Event listener para el select tipoServicioProgramacion para filtrar servicios
    const tipoServicioSelect = document.getElementById('tipoServicioProgramacion');
    if (tipoServicioSelect) {
        tipoServicioSelect.addEventListener('change', function() {
            const selectedTipo = this.value;
            loadServicios('servicioProgramacion', selectedTipo || null);
        });
    }

    // Event listener para el select tipoServicioProgramacionEdit para filtrar servicios en edición
    const tipoServicioSelectEdit = document.getElementById('tipoServicioProgramacionEdit');
    if (tipoServicioSelectEdit) {
        tipoServicioSelectEdit.addEventListener('change', function() {
            const selectedTipo = this.value;
            loadServicios('servicioProgramacionEdit', selectedTipo || null);
        });
    }

    // Función para poblar la tabla de horarios de empleados con paginación
    function populateHorarioEmpleado(tableId, nombreFilter = '', employeeIdFilter = '', dateFilter = '') {
        const tbody = document.getElementById(tableId);
        tbody.innerHTML = ''; // Limpiar filas existentes

        // Remover controles de paginación existentes
        const existingPagination = document.getElementById('pagination-controls-' + tableId);
        if (existingPagination) {
            existingPagination.remove();
        }

        fetch('/admin/api/horarios')
            .then(response => response.json())
            .then(data => {
                // Filtrar por estado 'Activo'
                let filteredData = data.filter(schedule => schedule.estado && schedule.estado.toLowerCase() === 'activo');

                if (employeeIdFilter) {
                    // Filtrar por ID de empleado específico
                    filteredData = filteredData.filter(schedule => schedule.id_empleado == employeeIdFilter);
                } else if (nombreFilter) {
                    // Filtrar por nombre de empleado
                    filteredData = filteredData.filter(schedule =>
                        schedule.empleado &&
                        schedule.empleado.toLowerCase().includes(nombreFilter.toLowerCase())
                    );
                }

                if (dateFilter) {
                    // Filtrar por fecha específica
                    filteredData = filteredData.filter(schedule => schedule.fecha === dateFilter);
                }

                // Calcular paginación
                const totalItems = filteredData.length;
                const totalPages = Math.ceil(totalItems / itemsPerPage);
                const startIndex = (currentPage - 1) * itemsPerPage;
                const endIndex = startIndex + itemsPerPage;
                const paginatedData = filteredData.slice(startIndex, endIndex);

                // Determinar el prefijo para los IDs de los campos
                const isEdit = tableId === 'tablaHorarioEmpleadoEdit';
                const idEmpleadoField = isEdit ? 'idEmpleadoEdit' : 'idEmpleado';
                const nombreEmpleadoField = isEdit ? 'nombreEmpleadoEdit' : 'nombreEmpleado';
                const idHorarioField = isEdit ? 'idHorarioEdit' : 'idHorario';

                // Poblar filas de la tabla
                paginatedData.forEach(schedule => {
                    const row = document.createElement('tr');
                    row.style.cursor = 'pointer';
                    row.addEventListener('click', function() {
                        document.getElementById(idEmpleadoField).value = schedule.id_empleado;
                        document.getElementById(nombreEmpleadoField).value = schedule.empleado || 'Nombre no disponible';
                        document.getElementById(idHorarioField).value = schedule.id_horario;
                    });
                    row.innerHTML = `
                        <td class="px-4 py-2 text-sm text-gray-700">${schedule.id_empleado}</td>
                        <td class="px-4 py-2 text-sm text-gray-700">${schedule.empleado || 'Nombre no disponible'}</td>
                        <td class="px-4 py-2 text-sm text-gray-700">${schedule.fecha}</td>
                        <td class="px-4 py-2 text-sm text-gray-700 text-center">${schedule.hora_inicio}</td>
                        <td class="px-4 py-2 text-sm text-gray-700 text-center">${schedule.hora_fin}</td>
                    `;
                    tbody.appendChild(row);
                });

                // Agregar controles de paginación después de la tabla
                if (totalPages > 1) {
                    const tableContainer = tbody.closest('.overflow-x-auto');
                    const paginationDiv = document.createElement('div');
                    paginationDiv.id = 'pagination-controls-' + tableId;
                    paginationDiv.className = 'flex justify-between items-center mt-4 px-4';
                    paginationDiv.innerHTML = `
                        <button id="prev-page-${tableId}" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded-lg transition-colors ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}" ${currentPage === 1 ? 'disabled' : ''}>
                            <i class="fas fa-chevron-left mr-2"></i>
                            Anterior
                        </button>
                        <span class="text-sm text-gray-700">Página ${currentPage} de ${totalPages}</span>
                        <button id="next-page-${tableId}" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded-lg transition-colors ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}" ${currentPage === totalPages ? 'disabled' : ''}>
                            Siguiente
                            <i class="fas fa-chevron-right ml-2"></i>
                        </button>
                    `;
                    tableContainer.appendChild(paginationDiv);

                    // Agregar event listeners para botones de paginación
                    document.getElementById('prev-page-' + tableId).addEventListener('click', function() {
                        if (currentPage > 1) {
                            currentPage--;
                            populateHorarioEmpleado(tableId, nombreFilter, employeeIdFilter, dateFilter);
                        }
                    });

                    document.getElementById('next-page-' + tableId).addEventListener('click', function() {
                        if (currentPage < totalPages) {
                            currentPage++;
                            populateHorarioEmpleado(tableId, nombreFilter, employeeIdFilter, dateFilter);
                        }
                    });
                }
            })
            .catch(error => console.error('Error cargando horarios:', error));
    }

    // Función para cargar sugerencias de empleados
    function loadEmployeeSuggestions(inputValue) {
        const suggestionsDiv = document.getElementById('suggestions-empleado');
        suggestionsDiv.innerHTML = '';

        if (inputValue.length < 2) {
            suggestionsDiv.classList.add('hidden');
            return;
        }

        fetch('/admin/api/empleados')
            .then(response => response.json())
            .then(data => {
                const filteredEmployees = data.filter(employee => {
                    const fullName = `${employee.nombres || ''} ${employee.apellidos || ''}`.trim();
                    return fullName.toLowerCase().includes(inputValue.toLowerCase());
                });

                if (filteredEmployees.length > 0) {
                    filteredEmployees.forEach(employee => {
                        const fullName = `${employee.nombres || ''} ${employee.apellidos || ''}`.trim();
                        const suggestionItem = document.createElement('div');
                        suggestionItem.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
                        suggestionItem.textContent = fullName;
                        suggestionItem.addEventListener('click', function() {
                            document.getElementById('nombreEmpleado').value = fullName;
                            document.getElementById('idEmpleado').value = employee.id_empleado;
                            suggestionsDiv.classList.add('hidden');
                            // Cargar horarios específicos del empleado
                            currentPage = 1;
                            populateHorarioEmpleado('tablaHorarioEmpleado', '', employee.id_empleado);
                        });
                        suggestionsDiv.appendChild(suggestionItem);
                    });
                    suggestionsDiv.classList.remove('hidden');
                } else {
                    suggestionsDiv.classList.add('hidden');
                }
            })
            .catch(error => console.error('Error cargando empleados:', error));
    }

    // Función para cargar sugerencias de empleados en edición
    function loadEmployeeSuggestionsEdit(inputValue) {
        const suggestionsDiv = document.getElementById('suggestions-empleado-edit');
        suggestionsDiv.innerHTML = '';

        if (inputValue.length < 2) {
            suggestionsDiv.classList.add('hidden');
            return;
        }

        fetch('/admin/api/empleados')
            .then(response => response.json())
            .then(data => {
                const filteredEmployees = data.filter(employee => {
                    const fullName = `${employee.nombres || ''} ${employee.apellidos || ''}`.trim();
                    return fullName.toLowerCase().includes(inputValue.toLowerCase());
                });

                if (filteredEmployees.length > 0) {
                    filteredEmployees.forEach(employee => {
                        const fullName = `${employee.nombres || ''} ${employee.apellidos || ''}`.trim();
                        const suggestionItem = document.createElement('div');
                        suggestionItem.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
                        suggestionItem.textContent = fullName;
                        suggestionItem.addEventListener('click', function() {
                            document.getElementById('nombreEmpleadoEdit').value = fullName;
                            document.getElementById('idEmpleadoEdit').value = employee.id_empleado;
                            suggestionsDiv.classList.add('hidden');
                            // Cargar horarios específicos del empleado
                            currentPage = 1;
                            const selectedDate = document.getElementById('fechaProgramacionEdit').value;
                            populateHorarioEmpleado('tablaHorarioEmpleadoEdit', '', employee.id_empleado, selectedDate);
                        });
                        suggestionsDiv.appendChild(suggestionItem);
                    });
                    suggestionsDiv.classList.remove('hidden');
                } else {
                    suggestionsDiv.classList.add('hidden');
                }
            })
            .catch(error => console.error('Error cargando empleados:', error));
    }

    // Event listener para el input nombreEmpleado
    const nombreEmpleadoInput = document.getElementById('nombreEmpleado');
    if (nombreEmpleadoInput) {
        nombreEmpleadoInput.addEventListener('input', function() {
            const nombre = this.value.trim();
            loadEmployeeSuggestions(nombre);
            if (nombre.length < 2) {
                document.getElementById('idEmpleado').value = '';
                document.getElementById('tablaHorarioEmpleado').innerHTML = '';
                // Remover paginación si existe
                const existingPagination = document.getElementById('pagination-controls-tablaHorarioEmpleado');
                if (existingPagination) {
                    existingPagination.remove();
                }
            }
        });

        // Ocultar sugerencias al hacer clic fuera
        document.addEventListener('click', function(event) {
            const suggestionsDiv = document.getElementById('suggestions-empleado');
            if (!nombreEmpleadoInput.contains(event.target) && !suggestionsDiv.contains(event.target)) {
                suggestionsDiv.classList.add('hidden');
            }
        });
    }

    // Event listener para el input nombreEmpleadoEdit
    const nombreEmpleadoEditInput = document.getElementById('nombreEmpleadoEdit');
    if (nombreEmpleadoEditInput) {
        nombreEmpleadoEditInput.addEventListener('input', function() {
            const nombre = this.value.trim();
            loadEmployeeSuggestionsEdit(nombre);
            if (nombre.length < 2) {
                document.getElementById('idEmpleadoEdit').value = '';
                document.getElementById('idHorarioEdit').value = '';
                document.getElementById('tablaHorarioEmpleadoEdit').innerHTML = '';
                // Remover paginación si existe
                const existingPagination = document.getElementById('pagination-controls-tablaHorarioEmpleadoEdit');
                if (existingPagination) {
                    existingPagination.remove();
                }
                // Recargar tabla con filtro solo por fecha
                currentPage = 1;
                const selectedDate = document.getElementById('fechaProgramacionEdit').value;
                populateHorarioEmpleado('tablaHorarioEmpleadoEdit', '', '', selectedDate);
            }
        });

        // Ocultar sugerencias al hacer clic fuera
        document.addEventListener('click', function(event) {
            const suggestionsDiv = document.getElementById('suggestions-empleado-edit');
            if (!nombreEmpleadoEditInput.contains(event.target) && !suggestionsDiv.contains(event.target)) {
                suggestionsDiv.classList.add('hidden');
            }
        });
    }

    // Event listener para el input fechaProgramacion para actualizar la tabla de horarios de empleados
    const fechaProgramacionInput = document.getElementById('fechaProgramacion');
    if (fechaProgramacionInput) {
        fechaProgramacionInput.addEventListener('change', function() {
            const selectedDate = this.value;
            const employeeId = document.getElementById('idEmpleado').value;
            if (selectedDate) {
                currentPage = 1;
                if (employeeId) {
                    populateHorarioEmpleado('tablaHorarioEmpleado', '', employeeId, selectedDate);
                } else {
                    populateHorarioEmpleado('tablaHorarioEmpleado', '', '', selectedDate);
                }
            }
        });
    }

    // Event listener para el input fechaProgramacionEdit para actualizar la tabla de horarios de empleados en edición
    const fechaProgramacionEditInput = document.getElementById('fechaProgramacionEdit');
    if (fechaProgramacionEditInput) {
        fechaProgramacionEditInput.addEventListener('change', function() {
            const selectedDate = this.value;
            const employeeId = document.getElementById('idEmpleadoEdit').value;
            if (selectedDate) {
                currentPage = 1;
                if (employeeId) {
                    populateHorarioEmpleado('tablaHorarioEmpleadoEdit', '', employeeId, selectedDate);
                } else {
                    populateHorarioEmpleado('tablaHorarioEmpleadoEdit', '', '', selectedDate);
                }
            }
        });
    }

    // Función para cargar y mostrar programaciones con filtros
    function loadProgramaciones() {
        // Obtener valores de filtros
        const filtroFecha = document.getElementById('filtroFecha').value;
        const filtroTipoServicio = document.getElementById('filtroTipoServicio').value;
        const filtroServicio = document.getElementById('filtroServicio').value;
        const filtroEstado = document.getElementById('filtroEstado').value;
        const filtroIdEmpleado = document.getElementById('filtroIdEmpleado').value;

        // Construir URL con parámetros de consulta
        let url = '/admin/api/programaciones';
        const params = new URLSearchParams();
        if (filtroFecha) params.append('fecha', filtroFecha);
        if (filtroTipoServicio) params.append('tipo_servicio', filtroTipoServicio);
        if (filtroServicio) params.append('servicio', filtroServicio);
        if (filtroEstado) params.append('estado', filtroEstado);
        if (filtroIdEmpleado) params.append('id_empleado', filtroIdEmpleado);
        if (params.toString()) url += '?' + params.toString();

        fetch(url)
            .then(response => response.json())
            .then(data => {
                tablaBody.innerHTML = ''; // Limpiar tabla
                data.forEach(prog => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="px-6 py-4 text-sm text-gray-700">${prog.id_programacion}</td>
                        <td class="px-6 py-4 text-sm text-gray-700">${prog.fecha}</td>
                        <td class="px-6 py-4 text-sm text-gray-700 text-center">${prog.hora_inicio}</td>
                        <td class="px-6 py-4 text-sm text-gray-700 text-center">${prog.hora_fin}</td>
                        <td class="px-6 py-4 text-sm text-gray-700">${prog.servicio || 'N/A'}</td>
                        <td class="px-6 py-4 text-sm text-gray-700">${prog.tipo_servicio || 'N/A'}</td>
                        <td class="px-6 py-4 text-sm text-gray-700">${prog.empleado || 'N/A'}</td>
                        <td class="px-6 py-4 text-center">
                            <span class="badge-${prog.estado.toLowerCase()} text-xs font-semibold px-2 py-1 rounded-full">${prog.estado}</span>
                        </td>
                        <td class="px-6 py-4 text-center text-sm font-medium">
                            <button class="text-blue-600 hover:text-blue-900 mr-2" onclick="editarProgramacion('${prog.id_programacion}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="text-red-600 hover:text-red-900" onclick="eliminarProgramacion('${prog.id_programacion}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tablaBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error cargando programaciones:', error));
    }

    // Cargar filtros iniciales
    loadTiposServicio('filtroTipoServicio');
    loadServicios('filtroServicio');

    // Cargar programaciones al iniciar
    loadProgramaciones();

    // Funciones globales para editar y eliminar
    window.editarProgramacion = function(id) {
        modalModificar.classList.add('show');
        fetch(`/admin/api/programaciones/${id}`)
            .then(response => response.json())
            .then(prog => {
                document.getElementById('idProgramacionEdit').value = prog.id_programacion;
                document.getElementById('fechaProgramacionEdit').value = prog.fecha;
                document.getElementById('horaInicioEdit').value = prog.hora_inicio;
                document.getElementById('horaFinEdit').value = prog.hora_fin;
                document.getElementById('estadoProgramacionEdit').value = prog.estado;
                // Cargar tipos de servicio primero, establecer valor, luego cargar servicios filtrados
                loadTiposServicio('tipoServicioProgramacionEdit').then(() => {
                    document.getElementById('tipoServicioProgramacionEdit').value = prog.id_tipo_servicio;
                    // Cargar servicios filtrados por el tipo seleccionado
                    loadServicios('servicioProgramacionEdit', prog.id_tipo_servicio).then(() => {
                        document.getElementById('servicioProgramacionEdit').value = prog.id_servicio;
                        document.getElementById('idEmpleadoEdit').value = prog.id_empleado;
                        document.getElementById('nombreEmpleadoEdit').value = prog.empleado;
                        document.getElementById('idHorarioEdit').value = prog.id_horario;
                        // Poblar tabla de horarios filtrada por empleado y fecha
                        populateHorarioEmpleado('tablaHorarioEmpleadoEdit', '', prog.id_empleado, prog.fecha);
                    }).catch(error => console.error('Error cargando servicios:', error));
                }).catch(error => console.error('Error cargando tipos de servicio:', error));
            })
            .catch(error => console.error('Error cargando programación:', error));
    };

    // Variable para almacenar el ID de la programación a eliminar
    let idProgramacionEliminar = null;

    window.eliminarProgramacion = function(id) {
        idProgramacionEliminar = id;
        modalEliminar.classList.add('show');
    };

    // Event listeners para los botones del modal de eliminación
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    if (btnCancelarEliminar) {
        btnCancelarEliminar.addEventListener('click', function() {
            modalEliminar.classList.remove('show');
            idProgramacionEliminar = null;
        });
    }

    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', function() {
            if (idProgramacionEliminar) {
                fetch(`/admin/api/programaciones/${idProgramacionEliminar}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ estado: 'Inactiva' })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('Programación desactivada exitosamente');
                        modalEliminar.classList.remove('show');
                        loadProgramaciones(); // Recargar la tabla
                        idProgramacionEliminar = null;
                    } else {
                        alert('Error: ' + result.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al desactivar la programación');
                });
            }
        });
    }
});
