let todosLosHorariosLab = []; 
// Gestión de Horarios Laborables
document.addEventListener('DOMContentLoaded', function() {
    cargarHorarios();
    inicializarEventos();
});

function inicializarEventos() {
    // Botón registrar horario
    const btnRegistrarHorario = document.getElementById('btnRegistrarHorario');
    if (btnRegistrarHorario) {
        btnRegistrarHorario.onclick = function () {
            cargarEmpleados();
            document.getElementById('modalRegistrarHorario').classList.add('show');
        }
    }

    // Formulario registrar
    const formRegistrar = document.getElementById('formRegistrarHorario');
    if (formRegistrar) {
        formRegistrar.onsubmit = function (e) {
            e.preventDefault();
            registrarHorario();
        }

        // Botón cancelar
        const btnCancelar = formRegistrar.querySelector('button[type="button"]');
        if (btnCancelar) {
            btnCancelar.onclick = function () {
                document.getElementById('modalRegistrarHorario').classList.remove('show');
            }
        }

        // Evento para buscar empleado en tiempo real
        const nombreEmpleadoInput = document.getElementById('nombreEmpleado');
        if (nombreEmpleadoInput) {
            nombreEmpleadoInput.addEventListener('input', function() {
                buscarEmpleado(this.value);
            });
        }
    }

    // Formulario modificar
    const formModificar = document.getElementById('formModificarHorario');
    if (formModificar) {
        formModificar.onsubmit = function (e) {
            e.preventDefault();
            modificarHorario();
        }

        // Botón cancelar
        const btnCancelar = formModificar.querySelector('button[type="button"]');
        if (btnCancelar) {
            btnCancelar.onclick = function () {
                document.getElementById('modalModificarHorario').classList.remove('show');
            }
        }
    }

    // Modal eliminar
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    if (btnCancelarEliminar) {
        btnCancelarEliminar.onclick = function () {
            document.getElementById('modalEliminar').classList.remove('show');
        }
    }

    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.onclick = function () {
            eliminarHorario();
        }
    }

    // Botón limpiar
    const btnLimpiar = document.getElementById('btnLimpiar');
    if (btnLimpiar) {
        btnLimpiar.onclick = function () {
            document.getElementById('filtroEmpleado').value = '';
            document.getElementById('filtroHorario').value = '';
            cargarHorarios(); // Recargar todos los horarios
        }
    }

    // Búsqueda dinámica
    const filtroEmpleado = document.getElementById('filtroEmpleado');
    const filtroHorario = document.getElementById('filtroHorario');

    if (filtroEmpleado) {
        filtroEmpleado.addEventListener('input', function() {
            filtrarHorariosDinamicamente();
        });
    }

    if (filtroHorario) {
        filtroHorario.addEventListener('input', function() {
            filtrarHorariosDinamicamente();
        });
    }

    // Funcionalidad de modales
    const modales = ['modalRegistrarHorario', 'modalModificarHorario', 'modalEliminar'];

    modales.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            const closeBtn = modal.querySelector('.close');
            if (closeBtn) {
                closeBtn.onclick = function () {
                    modal.classList.remove('show');
                }
            }
        }
    });

    window.onclick = function (event) {
        modales.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal && event.target == modal) {
                modal.classList.remove('show');
            }
        });
    }
}

function cargarHorarios() {
    fetch('/admin/api/horarios')
        .then(response => response.json())
        .then(data => {
            todosLosHorariosLab = data; // guarda copia completa
            // Usa la paginación genérica
            inicializarPaginacion({
                datos: todosLosHorariosLab,
                registrosPorPagina: 20,
                renderFuncion: mostrarHorarios
            });
        })
        .catch(error => {
            console.error('Error al cargar horarios:', error);
            mostrarMensaje('Error al cargar los horarios', 'error');
        });
}

function mostrarHorarios(horarios) {
    const tbody = document.getElementById('tabla-horarios-body');
    tbody.innerHTML = '';

    if (horarios.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="px-6 py-8 text-center text-gray-500">
                    <i class="fas fa-calendar-times text-4xl mb-4"></i>
                    <p>No hay horarios registrados</p>
                </td>
            </tr>
        `;
        return;
    }

    horarios.forEach(horario => {
        const row = crearFilaHorario(horario);
        tbody.appendChild(row);
    });
}

function crearFilaHorario(horario) {
    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50 transition-colors';

    // Formatear fecha
    const fecha = new Date(horario.fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });

    // Formatear horas
    const horaInicio = horario.hora_inicio ? horario.hora_inicio.substring(0, 5) : '';
    const horaFin = horario.hora_fin ? horario.hora_fin.substring(0, 5) : '';

    // Determinar estado de disponibilidad
    const disponibilidad = (horario.disponibilidad || horario.estado || '').toLowerCase() === 'disponible' ? 'Disponible' : 'No disponible';
    const claseDisponibilidad = (horario.disponibilidad || horario.estado || '').toLowerCase() === 'disponible' ? 'badge-disponible' : 'badge-no-disponible';

    // Determinar estado
    const estado = (horario.estado || '').toLowerCase() === 'activo' ? 'Activo' : 'Inactivo';
    const claseEstado = (horario.estado || '').toLowerCase() === 'activo' ? 'badge-activo' : 'badge-inactivo';

    row.innerHTML = `
        <td class="px-6 py-4 text-sm text-gray-900 font-medium">${horario.id_empleado}</td>
        <td class="px-6 py-4 text-sm text-gray-900">${horario.empleado || 'N/A'}</td>
        <td class="px-6 py-4 text-sm text-gray-900 font-medium">${horario.id_horario}</td>
        <td class="px-6 py-4 text-sm text-gray-900">${fecha}</td>
        <td class="px-6 py-4 text-sm text-gray-900">${horaInicio}</td>
        <td class="px-6 py-4 text-sm text-gray-900">${horaFin}</td>
        <td class="px-6 py-4 text-center">
            <span class="${claseEstado} text-white text-xs font-semibold px-3 py-1 rounded-full">
                ${estado}
            </span>
        </td>
        <td class="px-6 py-4 text-center">
            <button class="btn-editar text-blue-600 hover:text-blue-800 mx-1 transition-colors"
                    title="Editar" data-id="${horario.id_horario}">
                <i class="fas fa-edit text-lg"></i>
            </button>
            <button class="btn-eliminar text-red-600 hover:text-red-800 mx-1 transition-colors"
                    title="Eliminar" data-id="${horario.id_horario}">
                <i class="fas fa-trash-alt text-lg"></i>
            </button>
        </td>
    `;

    // Agregar eventos a los botones
    const btnEditar = row.querySelector('.btn-editar');
    const btnEliminar = row.querySelector('.btn-eliminar');

    btnEditar.onclick = function() {
        editarHorario(horario.id_horario);
    };

    btnEliminar.onclick = function() {
        confirmarEliminarHorario(horario.id_horario);
    };

    return row;
}

function registrarHorario() {
    const formData = new FormData(document.getElementById('formRegistrarHorario'));
    const data = {
        id_empleado: parseInt(formData.get('idEmpleado')),
        fecha: formData.get('fecha'),
        hora_inicio: formData.get('horaInicio'),
        hora_fin: formData.get('horaFin'),
        estado: formData.get('disponibilidad') === 'Disponible' ? 'disponible' : 'no_disponible'
    };

    fetch('/admin/api/horarios', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById('modalRegistrarHorario').classList.remove('show');
            mostrarMensaje('Horario registrado exitosamente', 'success');
            cargarHorarios();
            document.getElementById('formRegistrarHorario').reset();
        } else {
            mostrarMensaje(result.message || 'Error al registrar horario', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al registrar horario', 'error');
    });
}

function editarHorario(idHorario) {
    fetch(`/admin/api/horarios/${idHorario}`)
        .then(response => response.json())
        .then(horario => {
            if (horario) {
                // Llenar el formulario de modificación
                document.getElementById('codigoHorario').value = horario.id_horario;
                document.getElementById('idEmpleadoMod').value = horario.id_empleado;
                document.getElementById('nombreEmpleadoMod').value = horario.empleado || '';

                // Formatear fecha para input date (YYYY-MM-DD)
                if (horario.fecha) {
                    const fecha = new Date(horario.fecha);
                    document.getElementById('fechaMod').value = fecha.toISOString().split('T')[0];
                }

                // Formatear horas para input time (HH:MM)
                if (horario.hora_inicio) {
                    const horaInicio = horario.hora_inicio.length >= 5 ? horario.hora_inicio.substring(0, 5) : horario.hora_inicio;
                    document.getElementById('horaInicioMod').value = horaInicio;
                }
                if (horario.hora_fin) {
                    const horaFin = horario.hora_fin.length >= 5 ? horario.hora_fin.substring(0, 5) : horario.hora_fin;
                    document.getElementById('horaFinMod').value = horaFin;
                }

                // Mapear estado a disponibilidad (disponible/no disponible)
                const estadoHorario = (horario.estado || '').toLowerCase();
                document.getElementById('disponibilidadMod').value = estadoHorario === 'disponible' ? 'Disponible' : 'No disponible';

                // Estado del horario (activo/inactivo)
                document.getElementById('estadoMod').value = estadoHorario === 'activo' || estadoHorario === 'disponible' ? 'Activo' : 'Inactivo';

                // Guardar el ID del horario para la modificación
                document.getElementById('formModificarHorario').dataset.idHorario = idHorario;

                document.getElementById('modalModificarHorario').classList.add('show');
            } else {
                mostrarMensaje('Horario no encontrado', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al cargar horario', 'error');
        });
}

function modificarHorario() {
    const form = document.getElementById('formModificarHorario');
    const idHorario = form.dataset.idHorario;

    const formData = new FormData(form);
    const data = {
        fecha: formData.get('fechaMod'),
        hora_inicio: formData.get('horaInicioMod'),
        hora_fin: formData.get('horaFinMod'),
        estado: formData.get('disponibilidadMod') === 'Disponible' ? 'disponible' : 'no_disponible'
    };

    fetch(`/admin/api/horarios/${idHorario}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById('modalModificarHorario').classList.remove('show');
            mostrarMensaje('Horario actualizado exitosamente', 'success');
            cargarHorarios();
        } else {
            mostrarMensaje(result.message || 'Error al actualizar horario', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al actualizar horario', 'error');
    });
}

function confirmarEliminarHorario(idHorario) {
    document.getElementById('modalEliminar').dataset.idHorario = idHorario;
    document.getElementById('modalEliminar').classList.add('show');
}

function eliminarHorario() {
    const idHorario = document.getElementById('modalEliminar').dataset.idHorario;

    fetch(`/admin/api/horarios/${idHorario}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById('modalEliminar').classList.remove('show');
            mostrarMensaje('Horario eliminado exitosamente', 'success');
            cargarHorarios();
        } else {
            mostrarMensaje(result.message || 'Error al eliminar horario', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error al eliminar horario', 'error');
    });
}

function filtrarHorariosDinamicamente() {
    const filtroEmpleado = document.getElementById('filtroEmpleado').value.toLowerCase();
    const filtroHorario = document.getElementById('filtroHorario').value;

    const horariosFiltrados = todosLosHorariosLab.filter(horario => {
        const coincideEmpleado = !filtroEmpleado || (horario.empleado && horario.empleado.toLowerCase().includes(filtroEmpleado));
        const coincideFecha = !filtroHorario || (horario.fecha && horario.fecha.startsWith(filtroHorario));

        return coincideEmpleado && coincideFecha;
    });

    // Actualizar la paginación con los datos filtrados
    inicializarPaginacion({
        datos: horariosFiltrados,
        registrosPorPagina: 20,
        renderFuncion: mostrarHorarios
    });
}

function cargarEmpleados() {
    fetch('/admin/api/empleados')
        .then(response => response.json())
        .then(empleados => {
            // Guardar empleados para búsqueda
            window.empleados = empleados;
            console.log('Empleados cargados:', empleados);
        })
        .catch(error => {
            console.error('Error al cargar empleados:', error);
            mostrarMensaje('Error al cargar empleados', 'error');
        });
}

function buscarEmpleado(termino) {
    if (!window.empleados || termino.length < 2) {
        return;
    }

    const empleadosFiltrados = window.empleados.filter(empleado =>
        empleado.nombres.toLowerCase().includes(termino.toLowerCase()) ||
        empleado.apellidos.toLowerCase().includes(termino.toLowerCase())
    );

    mostrarSugerenciasEmpleados(empleadosFiltrados);
}

function mostrarSugerenciasEmpleados(empleados) {
    // Remover sugerencias anteriores
    const sugerenciasAnteriores = document.querySelector('.sugerencias-empleados');
    if (sugerenciasAnteriores) {
        sugerenciasAnteriores.remove();
    }

    if (empleados.length === 0) {
        return;
    }

    const inputNombre = document.getElementById('nombreEmpleado');
    const sugerenciasDiv = document.createElement('div');
    sugerenciasDiv.className = 'sugerencias-empleados absolute z-10 bg-white border border-gray-300 rounded-lg shadow-lg max-h-40 overflow-y-auto mt-1';
    sugerenciasDiv.style.width = inputNombre.offsetWidth + 'px';

    empleados.forEach(empleado => {
        const opcion = document.createElement('div');
        opcion.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
        opcion.textContent = `${empleado.nombres} ${empleado.apellidos}`;
        opcion.onclick = function() {
            seleccionarEmpleado(empleado);
            sugerenciasDiv.remove();
        };
        sugerenciasDiv.appendChild(opcion);
    });

    inputNombre.parentNode.style.position = 'relative';
    inputNombre.parentNode.appendChild(sugerenciasDiv);
}

function seleccionarEmpleado(empleado) {
    document.getElementById('nombreEmpleado').value = `${empleado.nombres} ${empleado.apellidos}`;
    document.getElementById('idEmpleado').value = empleado.id_empleado;
}

function mostrarMensaje(mensaje, tipo) {
    // Crear elemento de mensaje
    const mensajeDiv = document.createElement('div');
    mensajeDiv.className = `fixed top-4 right-4 px-6 py-3 rounded-lg text-white font-semibold z-50 ${
        tipo === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    mensajeDiv.textContent = mensaje;

    document.body.appendChild(mensajeDiv);

    // Remover mensaje después de 3 segundos
    setTimeout(() => {
        mensajeDiv.remove();
    }, 3000);
}
