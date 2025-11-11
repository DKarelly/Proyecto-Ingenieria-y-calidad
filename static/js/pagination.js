/**
 * Módulo de Paginación Reutilizable
 * Proporciona funciones para implementar paginación en cualquier tabla
 * Patrón: Dividir datos en páginas y mostrar controles de navegación
 */

/**
 * Configuración de paginación por tabla
 * @type {Object}
 */
const paginationConfig = {
    registrosPorPagina: 20,
    maxBotonesVisibles: 6
};

/**
 * Estado de paginación por tabla (clave = tableId)
 * @type {Object}
 */
const paginationState = {};

/**
 * Inicializa el estado de paginación para una tabla específica
 * @param {string} tableId - ID de la tabla
 */
function initPaginacion(tableId) {
    if (!paginationState[tableId]) {
        paginationState[tableId] = {
            paginaActual: 1,
            datosGlobal: [],
            registrosPorPagina: paginationConfig.registrosPorPagina
        };
    }
}

/**
 * Puebla una tabla con datos paginados
 * @param {string} tableId - ID del tbody de la tabla
 * @param {Array} datos - Array de datos a mostrar
 * @param {Function} renderFn - Función que retorna HTML de una fila (recibe un dato)
 * @param {string} paginationContainerId - ID del contenedor de paginación
 * @param {Object} options - Opciones adicionales (mensajeVacio, registrosPorPagina)
 */
function poblarTablaPaginada(tableId, datos, renderFn, paginationContainerId, options = {}) {
    const tbody = document.getElementById(tableId);
    if (!tbody) {
        console.error(`No se encontró el elemento con ID: ${tableId}`);
        return;
    }

    const {
        mensajeVacio = 'No se encontraron registros',
        registrosPorPagina = paginationConfig.registrosPorPagina
    } = options;

    // Inicializar estado
    initPaginacion(tableId);
    const estado = paginationState[tableId];
    estado.registrosPorPagina = registrosPorPagina;
    estado.datosGlobal = datos || [];

    // Resetear a primera página si hay nuevos datos (ej. después de filtrar)
    estado.paginaActual = 1;

    // Limpiar tbody
    tbody.innerHTML = '';

    // Validar datos
    if (!datos || datos.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="10" class="px-6 py-4 text-center text-gray-500">${mensajeVacio}</td>`;
        tbody.appendChild(tr);
        actualizarPaginacionUI(paginationContainerId, 0, tableId);
        return;
    }

    // Calcular paginación
    const totalRegistros = datos.length;
    const inicio = (estado.paginaActual - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, totalRegistros);
    const datosPagina = datos.slice(inicio, fin);

    // Renderizar filas
    datosPagina.forEach(dato => {
        const html = renderFn(dato);
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition-colors';
        tr.innerHTML = html;
        tbody.appendChild(tr);
    });

    // Actualizar controles de paginación
    actualizarPaginacionUI(paginationContainerId, totalRegistros, tableId);

    // Reasignar eventos de botones si existe la función
    if (typeof asignarEventosBotones === 'function') {
        asignarEventosBotones();
    }
}

/**
 * Actualiza la UI de paginación
 * @param {string} paginationContainerId - ID del contenedor de paginación
 * @param {number} totalRegistros - Total de registros
 * @param {string} tableId - ID de la tabla asociada
 */
function actualizarPaginacionUI(paginationContainerId, totalRegistros, tableId) {
    const container = document.getElementById(paginationContainerId);
    if (!container) {
        console.warn(`Contenedor de paginación no encontrado: ${paginationContainerId}`);
        return;
    }

    initPaginacion(tableId);
    const estado = paginationState[tableId];
    const registrosPorPagina = estado.registrosPorPagina;
    const paginaActual = estado.paginaActual;

    // Actualizar rango si existen elementos de información
    const inicioRango = document.getElementById(`inicio-rango-${tableId}`);
    const finRango = document.getElementById(`fin-rango-${tableId}`);
    const totalSpan = document.getElementById(`total-registros-${tableId}`);

    if (inicioRango && finRango && totalSpan) {
        const inicio = totalRegistros === 0 ? 0 : (paginaActual - 1) * registrosPorPagina + 1;
        const fin = Math.min(paginaActual * registrosPorPagina, totalRegistros);
        inicioRango.textContent = inicio;
        finRango.textContent = fin;
        totalSpan.textContent = totalRegistros;
    }

    // Si solo hay 1 página, no mostrar botones
    const totalPaginas = Math.ceil(totalRegistros / registrosPorPagina);
    container.innerHTML = '';

    if (totalPaginas <= 1) {
        return;
    }

    // Generar botones de página con límite visible
    const maxVisible = paginationConfig.maxBotonesVisibles;
    let inicioPagina = Math.max(1, paginaActual - 2);
    let finPagina = Math.min(totalPaginas, inicioPagina + maxVisible - 1);

    if (finPagina - inicioPagina < maxVisible - 1) {
        inicioPagina = Math.max(1, finPagina - maxVisible + 1);
    }

    // Crear botones
    for (let i = inicioPagina; i <= finPagina; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.type = 'button';
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === paginaActual
                ? 'bg-cyan-600 text-white border-cyan-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            cambiarPagina(tableId, i, paginationContainerId);
        });
        container.appendChild(btn);
    }

    // Agregar "..." si hay más páginas
    if (finPagina < totalPaginas) {
        const span = document.createElement('span');
        span.className = 'px-2 text-gray-500';
        span.textContent = '...';
        container.appendChild(span);

        const ultimoBtn = document.createElement('button');
        ultimoBtn.textContent = totalPaginas;
        ultimoBtn.type = 'button';
        ultimoBtn.className = 'px-3 py-2 text-sm font-medium border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-100 transition-colors';
        ultimoBtn.addEventListener('click', (e) => {
            e.preventDefault();
            cambiarPagina(tableId, totalPaginas, paginationContainerId);
        });
        container.appendChild(ultimoBtn);
    }
}

/**
 * Cambia a una página específica y re-renderiza
 * @param {string} tableId - ID de la tabla
 * @param {number} numeroPagina - Número de página
 * @param {string} paginationContainerId - ID del contenedor de paginación
 */
function cambiarPagina(tableId, numeroPagina, paginationContainerId) {
    initPaginacion(tableId);
    const estado = paginationState[tableId];
    estado.paginaActual = numeroPagina;

    // Re-renderizar tabla
    const tbody = document.getElementById(tableId);
    if (tbody && typeof poblarTablaPaginada === 'function') {
        // Necesitamos que se llame a poblarTablaPaginada desde el código específico
        // Por eso aquí solo actualizamos la UI
        const totalRegistros = estado.datosGlobal.length;
        const registrosPorPagina = estado.registrosPorPagina;
        const inicio = (numeroPagina - 1) * registrosPorPagina;
        const fin = Math.min(inicio + registrosPorPagina, totalRegistros);
        const datosPagina = estado.datosGlobal.slice(inicio, fin);

        // Limpiar y re-renderizar (el código específico debe hacerlo)
        // Por simplicidad, aquí usamos una referencia almacenada
        if (window.tableRenderFunctions && window.tableRenderFunctions[tableId]) {
            const renderFn = window.tableRenderFunctions[tableId];
            tbody.innerHTML = '';
            datosPagina.forEach(dato => {
                const html = renderFn(dato);
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-gray-50 transition-colors';
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });

            // Reasignar eventos
            if (typeof asignarEventosBotones === 'function') {
                asignarEventosBotones();
            }
        }

        // Actualizar UI de paginación
        actualizarPaginacionUI(paginationContainerId, totalRegistros, tableId);
    }
}

/**
 * Obtiene el estado actual de paginación de una tabla
 * @param {string} tableId - ID de la tabla
 * @returns {Object} Estado de paginación
 */
function obtenerEstadoPaginacion(tableId) {
    initPaginacion(tableId);
    return paginationState[tableId];
}

/**
 * Resetea la paginación de una tabla a la primera página
 * @param {string} tableId - ID de la tabla
 */
function resetearPaginacion(tableId) {
    initPaginacion(tableId);
    paginationState[tableId].paginaActual = 1;
}
