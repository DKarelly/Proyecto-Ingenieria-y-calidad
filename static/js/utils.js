/**
 * Utilidades JavaScript para mejorar rendimiento y UX
 * Incluye: debounce, loading indicators, búsquedas dinámicas, paginación
 */

// ==================== DEBOUNCE ====================
/**
 * Implementa debounce para reducir llamadas a funciones
 * Útil para búsquedas en tiempo real y filtros dinámicos
 * 
 * @param {Function} func - Función a ejecutar
 * @param {number} delay - Retraso en milisegundos (recomendado: 300-500ms)
 * @returns {Function} Función con debounce aplicado
 * 
 * Ejemplo de uso:
 * const buscarPacientes = debounce(async (termino) => {
 *     const resultados = await fetch(`/api/pacientes?q=${termino}`);
 *     mostrarResultados(resultados);
 * }, 400);
 */
function debounce(func, delay = 400) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

// ==================== INDICADORES DE CARGA ====================
/**
 * Muestra un indicador de carga visual
 * 
 * @param {string} contenedorId - ID del contenedor donde mostrar el loading
 * @param {string} mensaje - Mensaje a mostrar (opcional)
 * @param {string} tipo - Tipo de indicador: 'spinner', 'skeleton', 'dots'
 */
function mostrarLoading(contenedorId, mensaje = 'Cargando...', tipo = 'spinner') {
    const contenedor = document.getElementById(contenedorId);
    if (!contenedor) return;
    
    let loadingHTML = '';
    
    switch(tipo) {
        case 'spinner':
            loadingHTML = `
                <div class="loading-container text-center py-8">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <div class="loading-message text-gray-600">${mensaje}</div>
                </div>
            `;
            break;
        
        case 'skeleton':
            loadingHTML = `
                <div class="skeleton-loader">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                </div>
            `;
            break;
        
        case 'dots':
            loadingHTML = `
                <div class="loading-dots text-center py-8">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <p class="mt-3 text-gray-600">${mensaje}</p>
                </div>
            `;
            break;
    }
    
    contenedor.innerHTML = loadingHTML;
}

/**
 * Oculta el indicador de carga
 * 
 * @param {string} contenedorId - ID del contenedor
 */
function ocultarLoading(contenedorId) {
    const contenedor = document.getElementById(contenedorId);
    if (!contenedor) return;
    
    const loadingElement = contenedor.querySelector('.loading-container, .skeleton-loader, .loading-dots');
    if (loadingElement) {
        loadingElement.remove();
    }
}

/**
 * Muestra un overlay de carga en toda la pantalla
 * 
 * @param {string} mensaje - Mensaje a mostrar
 */
function mostrarLoadingGlobal(mensaje = 'Procesando...') {
    // Eliminar overlay previo si existe
    ocultarLoadingGlobal();
    
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay-global';
    overlay.className = 'loading-overlay-global';
    overlay.innerHTML = `
        <div class="loading-overlay-content">
            <div class="spinner-large"></div>
            <div class="loading-message-large">${mensaje}</div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Prevenir scroll del body
    document.body.style.overflow = 'hidden';
}

/**
 * Oculta el overlay de carga global
 */
function ocultarLoadingGlobal() {
    const overlay = document.getElementById('loading-overlay-global');
    if (overlay) {
        overlay.remove();
        document.body.style.overflow = '';
    }
}

// ==================== MENSAJES Y NOTIFICACIONES ====================
/**
 * Muestra un mensaje de notificación (toast)
 * 
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo: 'success', 'error', 'warning', 'info'
 * @param {number} duracion - Duración en ms (0 = permanente)
 */
function mostrarNotificacion(mensaje, tipo = 'info', duracion = 5000) {
    // Crear contenedor de notificaciones si no existe
    let contenedorToasts = document.getElementById('toast-container');
    if (!contenedorToasts) {
        contenedorToasts = document.createElement('div');
        contenedorToasts.id = 'toast-container';
        contenedorToasts.className = 'toast-container';
        document.body.appendChild(contenedorToasts);
    }
    
    // Configuración de iconos y colores por tipo
    const config = {
        'success': { icono: 'fa-check-circle', color: 'success' },
        'error': { icono: 'fa-exclamation-circle', color: 'danger' },
        'warning': { icono: 'fa-exclamation-triangle', color: 'warning' },
        'info': { icono: 'fa-info-circle', color: 'info' }
    };
    
    const conf = config[tipo] || config['info'];
    
    // Crear toast
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${conf.color} fade-in`;
    toast.innerHTML = `
        <i class="fas ${conf.icono} toast-icon"></i>
        <span class="toast-message">${mensaje}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    contenedorToasts.appendChild(toast);
    
    // Auto-ocultar si se especifica duración
    if (duracion > 0) {
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, duracion);
    }
}

/**
 * Muestra mensaje de error estructurado
 * Sigue el formato: "Qué pasó + Por qué + Cómo solucionarlo"
 * 
 * @param {Object} error - Objeto de error del ErrorManager
 * @param {string} contenedorId - ID donde mostrar el error
 */
function mostrarMensajeError(error, contenedorId) {
    const contenedor = document.getElementById(contenedorId);
    if (!contenedor) return;
    
    const errorHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <div class="alert-header">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <strong>${error.que_paso}</strong>
            </div>
            <div class="alert-body mt-2">
                <p class="mb-1"><strong>Causa:</strong> ${error.por_que}</p>
                <p class="mb-1"><strong>Solución:</strong> ${error.solucion}</p>
                ${error.codigo ? `<p class="text-sm text-muted mt-2">Código de error: ${error.codigo}</p>` : ''}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    contenedor.innerHTML = errorHTML;
}

/**
 * Limpia todos los mensajes de error de un contenedor
 * 
 * @param {string} contenedorId - ID del contenedor
 */
function limpiarMensajesError(contenedorId) {
    const contenedor = document.getElementById(contenedorId);
    if (contenedor) {
        contenedor.innerHTML = '';
    }
}

// ==================== VALIDACIÓN EN TIEMPO REAL ====================
/**
 * Configura validación en tiempo real para un campo de email
 * 
 * @param {string} inputId - ID del campo de email
 * @param {string} errorContainerId - ID del contenedor de error
 */
function configurarValidacionEmail(inputId, errorContainerId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const validarEmail = debounce(() => {
        const email = input.value.trim();
        const errorContainer = document.getElementById(errorContainerId);
        
        if (!email) {
            errorContainer.innerHTML = '';
            input.classList.remove('is-invalid', 'is-valid');
            return;
        }
        
        const patronEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        
        if (!patronEmail.test(email)) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            errorContainer.innerHTML = `
                <small class="text-danger">
                    <i class="fas fa-exclamation-circle"></i>
                    El correo debe incluir un @ y un dominio válido (ejemplo: usuario@dominio.com)
                </small>
            `;
        } else {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
            errorContainer.innerHTML = `
                <small class="text-success">
                    <i class="fas fa-check-circle"></i>
                    Formato de correo válido
                </small>
            `;
        }
    }, 500);
    
    input.addEventListener('input', validarEmail);
}

/**
 * Configura validación en tiempo real para un campo de contraseña
 * 
 * @param {string} inputId - ID del campo de contraseña
 * @param {string} feedbackContainerId - ID del contenedor de feedback
 */
function configurarValidacionContrasena(inputId, feedbackContainerId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('input', () => {
        const password = input.value;
        const feedback = document.getElementById(feedbackContainerId);
        
        if (!password) {
            feedback.innerHTML = '';
            return;
        }
        
        const requisitos = [
            { cumple: password.length >= 8, texto: 'Mínimo 8 caracteres' },
            { cumple: /[A-Z]/.test(password), texto: 'Una mayúscula' },
            { cumple: /[a-z]/.test(password), texto: 'Una minúscula' },
            { cumple: /[0-9]/.test(password), texto: 'Un número' }
        ];
        
        const todosOk = requisitos.every(r => r.cumple);
        
        let feedbackHTML = '<div class="password-requirements mt-2">';
        requisitos.forEach(req => {
            const icono = req.cumple ? 'fa-check text-success' : 'fa-times text-danger';
            feedbackHTML += `
                <div class="requirement-item">
                    <i class="fas ${icono}"></i> ${req.texto}
                </div>
            `;
        });
        feedbackHTML += '</div>';
        
        feedback.innerHTML = feedbackHTML;
        
        if (todosOk) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        }
    });
}

// ==================== BÚSQUEDAS DINÁMICAS ====================
/**
 * Configura búsqueda dinámica sin botón
 * 
 * @param {string} inputId - ID del campo de búsqueda
 * @param {Function} funcionBusqueda - Función que realiza la búsqueda
 * @param {string} contadorId - ID del contador de resultados (opcional)
 */
function configurarBusquedaDinamica(inputId, funcionBusqueda, contadorId = null) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // Agregar indicador de búsqueda
    const wrapper = input.parentElement;
    let indicator = wrapper.querySelector('.search-indicator');
    if (!indicator) {
        indicator = document.createElement('span');
        indicator.className = 'search-indicator';
        wrapper.style.position = 'relative';
        wrapper.appendChild(indicator);
    }
    
    const buscarConDebounce = debounce(async () => {
        const termino = input.value.trim();
        
        // Mostrar indicador de búsqueda
        indicator.innerHTML = '<i class="fas fa-spinner fa-spin text-primary"></i>';
        indicator.style.display = 'block';
        
        try {
            const resultados = await funcionBusqueda(termino);
            
            // Actualizar contador si existe
            if (contadorId) {
                const contador = document.getElementById(contadorId);
                if (contador) {
                    const cantidad = Array.isArray(resultados) ? resultados.length : resultados.total || 0;
                    contador.textContent = `${cantidad} resultado${cantidad !== 1 ? 's' : ''} encontrado${cantidad !== 1 ? 's' : ''}`;
                }
            }
            
            // Ocultar indicador
            indicator.style.display = 'none';
            
        } catch (error) {
            console.error('Error en búsqueda:', error);
            indicator.innerHTML = '<i class="fas fa-exclamation-triangle text-danger"></i>';
            setTimeout(() => indicator.style.display = 'none', 2000);
        }
    }, 400);
    
    input.addEventListener('input', buscarConDebounce);
    
    // Agregar botón de limpiar
    const btnLimpiar = document.createElement('button');
    btnLimpiar.type = 'button';
    btnLimpiar.className = 'btn-limpiar-busqueda';
    btnLimpiar.innerHTML = '<i class="fas fa-times"></i>';
    btnLimpiar.style.display = 'none';
    btnLimpiar.onclick = () => {
        input.value = '';
        btnLimpiar.style.display = 'none';
        buscarConDebounce();
    };
    wrapper.appendChild(btnLimpiar);
    
    input.addEventListener('input', () => {
        btnLimpiar.style.display = input.value ? 'block' : 'none';
    });
}

// ==================== PAGINACIÓN ====================
/**
 * Clase para manejar paginación eficiente
 */
class PaginacionManager {
    constructor(elementosPorPagina = 20) {
        this.elementosPorPagina = elementosPorPagina;
        this.paginaActual = 1;
        this.totalElementos = 0;
        this.totalPaginas = 0;
    }
    
    /**
     * Actualiza los totales y calcula páginas
     */
    actualizarTotales(totalElementos) {
        this.totalElementos = totalElementos;
        this.totalPaginas = Math.ceil(totalElementos / this.elementosPorPagina);
    }
    
    /**
     * Obtiene parámetros para query SQL con LIMIT y OFFSET
     */
    obtenerParametrosSQL() {
        const offset = (this.paginaActual - 1) * this.elementosPorPagina;
        return {
            limit: this.elementosPorPagina,
            offset: offset
        };
    }
    
    /**
     * Genera HTML para controles de paginación
     */
    generarControlesHTML(contenedorId) {
        if (this.totalPaginas <= 1) return '';
        
        const inicio = ((this.paginaActual - 1) * this.elementosPorPagina) + 1;
        const fin = Math.min(this.paginaActual * this.elementosPorPagina, this.totalElementos);
        
        return `
            <div class="paginacion-controles" id="${contenedorId}">
                <button 
                    class="btn btn-sm btn-outline-primary"
                    onclick="paginacion.irAPagina(${this.paginaActual - 1})"
                    ${this.paginaActual === 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i> Anterior
                </button>
                
                <span class="paginacion-info">
                    Mostrando ${inicio}-${fin} de ${this.totalElementos}
                </span>
                
                <button 
                    class="btn btn-sm btn-outline-primary"
                    onclick="paginacion.irAPagina(${this.paginaActual + 1})"
                    ${this.paginaActual === this.totalPaginas ? 'disabled' : ''}>
                    Siguiente <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        `;
    }
    
    irAPagina(numeroPagina) {
        if (numeroPagina < 1 || numeroPagina > this.totalPaginas) return;
        this.paginaActual = numeroPagina;
    }
}

// ==================== UTILIDADES GENERALES ====================
/**
 * Formatea un número con separadores de miles
 */
function formatearNumero(numero) {
    return new Intl.NumberFormat('es-PE').format(numero);
}

/**
 * Formatea una fecha en formato local
 */
function formatearFecha(fecha, formato = 'corto') {
    const date = new Date(fecha);
    
    if (formato === 'corto') {
        return date.toLocaleDateString('es-PE');
    } else if (formato === 'largo') {
        return date.toLocaleDateString('es-PE', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    } else if (formato === 'completo') {
        return date.toLocaleString('es-PE');
    }
}

/**
 * Obtiene el IP del cliente (aproximado)
 */
async function obtenerIPCliente() {
    try {
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return data.ip;
    } catch (error) {
        console.error('Error al obtener IP:', error);
        return 'Desconocida';
    }
}

// Exportar funciones globalmente
window.debounce = debounce;
window.mostrarLoading = mostrarLoading;
window.ocultarLoading = ocultarLoading;
window.mostrarLoadingGlobal = mostrarLoadingGlobal;
window.ocultarLoadingGlobal = ocultarLoadingGlobal;
window.mostrarNotificacion = mostrarNotificacion;
window.mostrarMensajeError = mostrarMensajeError;
window.limpiarMensajesError = limpiarMensajesError;
window.configurarValidacionEmail = configurarValidacionEmail;
window.configurarValidacionContrasena = configurarValidacionContrasena;
window.configurarBusquedaDinamica = configurarBusquedaDinamica;
window.PaginacionManager = PaginacionManager;
window.formatearNumero = formatearNumero;
window.formatearFecha = formatearFecha;
window.obtenerIPCliente = obtenerIPCliente;

console.log('✓ Utilidades de rendimiento y UX cargadas');
