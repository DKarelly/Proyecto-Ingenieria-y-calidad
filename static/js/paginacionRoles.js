/**
 * Paginación para Gestión de Roles y Permisos
 * Maneja la paginación de la tabla de roles cargada dinámicamente
 */

document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que se carguen los roles
    const tablaRoles = document.getElementById('tabla-roles');
    if (tablaRoles) {
        // Observar cambios en la tabla para reinicializar paginación
        const observer = new MutationObserver(() => {
            inicializarPaginacionRoles();
        });

        observer.observe(tablaRoles, {
            childList: true,
            subtree: true,
            characterData: false
        });

        // Inicializar cuando la página carga
        setTimeout(() => {
            inicializarPaginacionRoles();
        }, 500);
    }
});

function inicializarPaginacionRoles() {
    const tbody = document.getElementById('tabla-roles');
    if (!tbody) return;

    // Obtener todas las filas excepto la de carga
    const todasLasFilas = Array.from(tbody.querySelectorAll('tr'));
    const filasVisibles = todasLasFilas.filter(fila => {
        const loadingRow = fila.querySelector('#loading-row');
        return !loadingRow && fila.id !== 'loading-row';
    });

    const registrosPorPagina = 20;
    const totalRoles = filasVisibles.length;
    const totalPaginas = Math.ceil(totalRoles / registrosPorPagina);

    // Actualizar total de registros
    document.getElementById('total-registros-tabla-roles').textContent = totalRoles;

    // Limpiar controles de paginación
    const paginacionContainer = document.getElementById('paginacion-tabla-roles');
    if (!paginacionContainer) return;
    
    paginacionContainer.innerHTML = '';

    if (totalPaginas <= 1) {
        // Una sola página o sin registros
        const inicio = totalRoles > 0 ? 1 : 0;
        const fin = totalRoles;
        document.getElementById('inicio-rango-tabla-roles').textContent = inicio;
        document.getElementById('fin-rango-tabla-roles').textContent = fin;
        return;
    }

    // Mostrar primera página por defecto
    mostrarPaginaRoles(1, filasVisibles, registrosPorPagina);

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
            mostrarPaginaRoles(i, filasVisibles, registrosPorPagina);

            // Actualizar estilos de botones
            document.querySelectorAll('#paginacion-tabla-roles button').forEach(b => {
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

function mostrarPaginaRoles(pagina, filasVisibles, registrosPorPagina) {
    const inicio = (pagina - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, filasVisibles.length);

    // Mostrar solo las filas de la página actual
    filasVisibles.forEach((fila, index) => {
        fila.style.display = index >= inicio && index < fin ? 'table-row' : 'none';
    });

    // Actualizar información de rango
    document.getElementById('inicio-rango-tabla-roles').textContent = filasVisibles.length > 0 ? inicio + 1 : 0;
    document.getElementById('fin-rango-tabla-roles').textContent = fin;
}
