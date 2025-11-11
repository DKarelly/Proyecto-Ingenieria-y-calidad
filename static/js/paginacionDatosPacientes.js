/**
 * Paginación para Gestión de Datos de Pacientes
 * Maneja la paginación de la tabla de pacientes
 */

document.addEventListener('DOMContentLoaded', function() {
    inicializarPaginacionPacientes();

    // Reinicializar paginación cuando se busca
    const searchInput = document.getElementById('search-paciente');
    if (searchInput) {
        const originalEventListener = searchInput.oninput;
        searchInput.addEventListener('input', function() {
            // Esperar a que se actualice el filtrado de búsqueda
            setTimeout(() => {
                inicializarPaginacionPacientes();
            }, 100);
        });
    }
});

function inicializarPaginacionPacientes() {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    // Obtener todas las filas visibles (no filtradas y no el mensaje vacío)
    const todasLasFilas = Array.from(tbody.querySelectorAll('tr'));
    const filasVisibles = todasLasFilas.filter(fila => {
        // Excluir fila de "No hay pacientes"
        return !fila.querySelector('td[colspan]') && fila.style.display !== 'none';
    });

    const registrosPorPagina = 20;
    const totalPacientes = filasVisibles.length;
    const totalPaginas = Math.ceil(totalPacientes / registrosPorPagina);

    // Actualizar total de registros
    document.getElementById('total-registros-tabla-pacientes-datos').textContent = totalPacientes;

    // Limpiar controles de paginación
    const paginacionContainer = document.getElementById('paginacion-tabla-pacientes-datos');
    paginacionContainer.innerHTML = '';

    if (totalPaginas <= 1) {
        // Una sola página o sin registros
        const inicio = totalPacientes > 0 ? 1 : 0;
        const fin = totalPacientes;
        document.getElementById('inicio-rango-tabla-pacientes-datos').textContent = inicio;
        document.getElementById('fin-rango-tabla-pacientes-datos').textContent = fin;
        return;
    }

    // Mostrar primera página por defecto
    mostrarPaginaPacientes(1, filasVisibles, registrosPorPagina);

    // Generar botones de página
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
            mostrarPaginaPacientes(i, filasVisibles, registrosPorPagina);

            // Actualizar estilos de botones
            document.querySelectorAll('#paginacion-tabla-pacientes-datos button').forEach(b => {
                b.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
                    b === btn
                        ? 'bg-cyan-600 text-white border-cyan-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
                }`;
            });

            // Scroll a la tabla
            const tabla = document.querySelector('table');
            if (tabla) {
                tabla.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
        paginacionContainer.appendChild(btn);
    }
}

function mostrarPaginaPacientes(pagina, filasVisibles, registrosPorPagina) {
    const inicio = (pagina - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, filasVisibles.length);

    // Mostrar solo las filas de la página actual
    filasVisibles.forEach((fila, index) => {
        fila.style.display = index >= inicio && index < fin ? 'table-row' : 'none';
    });

    // Actualizar información de rango
    document.getElementById('inicio-rango-tabla-pacientes-datos').textContent = filasVisibles.length > 0 ? inicio + 1 : 0;
    document.getElementById('fin-rango-tabla-pacientes-datos').textContent = fin;
}
