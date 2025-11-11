/**
 * Paginación para Gestión de Usuarios
 * Maneja la paginación de tablas de empleados y pacientes en la página de gestión de usuarios
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar paginación para tabla de empleados
    const tbodyEmpleados = document.getElementById('empleados-tbody');
    if (tbodyEmpleados) {
        const filas = Array.from(tbodyEmpleados.querySelectorAll('tr')).filter(tr => {
            return !tr.querySelector('td[colspan]'); // Excluir mensaje "No hay empleados"
        });

        const totalEmpleados = filas.length;
        document.getElementById('total-registros-tabla-empleados-usuarios').textContent = totalEmpleados;

        if (totalEmpleados > 20) {
            inicializarPaginacion('empleados', filas);
        } else {
            document.getElementById('inicio-rango-tabla-empleados-usuarios').textContent = totalEmpleados > 0 ? 1 : 0;
            document.getElementById('fin-rango-tabla-empleados-usuarios').textContent = totalEmpleados;
        }
    }

    // Inicializar paginación para tabla de pacientes
    const tbodyPacientes = document.getElementById('pacientes-tbody');
    if (tbodyPacientes) {
        const filas = Array.from(tbodyPacientes.querySelectorAll('tr')).filter(tr => {
            return !tr.querySelector('td[colspan]'); // Excluir mensaje "No hay pacientes"
        });

        const totalPacientes = filas.length;
        document.getElementById('total-registros-tabla-pacientes-usuarios').textContent = totalPacientes;

        if (totalPacientes > 20) {
            inicializarPaginacion('pacientes', filas);
        } else {
            document.getElementById('inicio-rango-tabla-pacientes-usuarios').textContent = totalPacientes > 0 ? 1 : 0;
            document.getElementById('fin-rango-tabla-pacientes-usuarios').textContent = totalPacientes;
        }
    }
});

function inicializarPaginacion(tipo, filas) {
    const registrosPorPagina = 20;
    const total = filas.length;
    const totalPaginas = Math.ceil(total / registrosPorPagina);

    if (totalPaginas <= 1) return;

    const sufijo = tipo === 'empleados' ? 'empleados-usuarios' : 'pacientes-usuarios';
    const containerId = `paginacion-tabla-${sufijo}`;
    const container = document.getElementById(containerId);

    if (!container) return;

    // Mostrar primera página
    mostrarPagina(tipo, 1, filas, registrosPorPagina);

    // Generar botones
    for (let i = 1; i <= totalPaginas; i++) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = i;
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === 1
                ? 'bg-cyan-600 text-white border-cyan-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            mostrarPagina(tipo, i, filas, registrosPorPagina);

            // Actualizar estilos
            document.querySelectorAll(`#${containerId} button`).forEach(b => {
                b.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
                    b === btn
                        ? 'bg-cyan-600 text-white border-cyan-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
                }`;
            });
        });
        container.appendChild(btn);
    }
}

function mostrarPagina(tipo, pagina, filas, registrosPorPagina) {
    const inicio = (pagina - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, filas.length);

    // Mostrar/ocultar filas
    filas.forEach((fila, index) => {
        fila.style.display = index >= inicio && index < fin ? 'table-row' : 'none';
    });

    // Actualizar información de rango
    const sufijo = tipo === 'empleados' ? 'empleados-usuarios' : 'pacientes-usuarios';
    const inicioEl = document.getElementById(`inicio-rango-tabla-${sufijo}`);
    const finEl = document.getElementById(`fin-rango-tabla-${sufijo}`);

    if (inicioEl && finEl) {
        inicioEl.textContent = filas.length > 0 ? inicio + 1 : 0;
        finEl.textContent = fin;
    }
}
