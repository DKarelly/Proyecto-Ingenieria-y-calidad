/**
 * Sistema de Confirmación Modal para Clínica Unión
 * Versión 1.0
 * 
 * Este script proporciona un modal de confirmación reutilizable con diferentes tipos de alertas.
 */

// Crear el HTML del modal una sola vez cuando se carga el script
(function() {
    if (document.getElementById('confirmation-modal')) {
        return; // Ya existe el modal
    }

    const modalHTML = `
        <!-- Modal de Confirmación -->
        <div id="confirmation-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[80] hidden items-center justify-center p-4" style="animation: fadeIn 0.3s ease-out;">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 relative" style="animation: slideUp 0.3s ease-out;">
                <div class="flex flex-col items-center text-center">
                    <div id="confirm-icon-container" class="mb-4">
                        <!-- El icono se cambiará dinámicamente -->
                    </div>
                    <h3 id="confirm-title" class="text-2xl font-bold text-gray-800 mb-3"></h3>
                    <p id="confirm-message" class="text-gray-600 mb-6"></p>
                    
                    <div class="flex gap-3 w-full">
                        <button type="button" id="confirm-cancel" class="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-semibold transition-all hover:border-gray-400">
                            <span class="material-symbols-outlined text-sm align-middle mr-1">close</span>
                            Cancelar
                        </button>
                        <button type="button" id="confirm-accept" class="flex-1 px-6 py-3 rounded-lg text-white font-semibold transition-all shadow-lg hover:shadow-xl inline-flex items-center justify-center">
                            <span class="material-symbols-outlined text-sm mr-2" id="confirm-accept-icon">check_circle</span>
                            <span id="confirm-accept-text">Aceptar</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { 
                    opacity: 0;
                    transform: translateY(30px) scale(0.95);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes fadeOut {
                from {
                    opacity: 1;
                }
                to {
                    opacity: 0;
                }
            }
        </style>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
})();

/**
 * Muestra un modal de confirmación personalizado
 * @param {Object} opciones - Opciones del modal
 * @param {string} opciones.titulo - Título del modal
 * @param {string} opciones.mensaje - Mensaje del modal
 * @param {string} [opciones.tipo='info'] - Tipo de alerta: 'info', 'success', 'warning', 'danger'
 * @param {string} [opciones.textoAceptar='Aceptar'] - Texto del botón de aceptar
 * @param {string} [opciones.textoIconoAceptar='check_circle'] - Icono Material del botón de aceptar
 * @returns {Promise<boolean>} Promise que resuelve true si acepta, false si cancela
 */
function mostrarConfirmacion(opciones) {
    return new Promise((resolve) => {
        const { 
            titulo, 
            mensaje, 
            tipo = 'info', 
            textoAceptar = 'Aceptar', 
            textoIconoAceptar = 'check_circle' 
        } = opciones;
        
        const confirmationModal = document.getElementById('confirmation-modal');
        const iconContainer = document.getElementById('confirm-icon-container');
        const acceptButton = document.getElementById('confirm-accept');
        
        let iconoHTML = '';
        let colorBoton = '';
        
        switch(tipo) {
            case 'danger':
                iconoHTML = '<div class="bg-red-100 p-4 rounded-full"><span class="material-symbols-outlined text-red-600 text-5xl">warning</span></div>';
                colorBoton = 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700';
                break;
            case 'warning':
                iconoHTML = '<div class="bg-yellow-100 p-4 rounded-full"><span class="material-symbols-outlined text-yellow-600 text-5xl">error</span></div>';
                colorBoton = 'bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700';
                break;
            case 'success':
                iconoHTML = '<div class="bg-green-100 p-4 rounded-full"><span class="material-symbols-outlined text-green-600 text-5xl">check_circle</span></div>';
                colorBoton = 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700';
                break;
            case 'info':
            default:
                iconoHTML = '<div class="bg-blue-100 p-4 rounded-full"><span class="material-symbols-outlined text-blue-600 text-5xl">info</span></div>';
                colorBoton = 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700';
                break;
        }
        
        iconContainer.innerHTML = iconoHTML;
        document.getElementById('confirm-title').textContent = titulo;
        document.getElementById('confirm-message').textContent = mensaje;
        document.getElementById('confirm-accept-text').textContent = textoAceptar;
        document.getElementById('confirm-accept-icon').textContent = textoIconoAceptar;
        
        acceptButton.className = `flex-1 px-6 py-3 rounded-lg text-white font-semibold transition-all shadow-lg hover:shadow-xl inline-flex items-center justify-center ${colorBoton}`;
        
        confirmationModal.classList.remove('hidden');
        confirmationModal.classList.add('flex');
        document.body.style.overflow = 'hidden';
        
        const handleAccept = () => {
            confirmationModal.classList.add('hidden');
            confirmationModal.classList.remove('flex');
            document.body.style.overflow = 'auto';
            cleanup();
            resolve(true);
        };
        
        const handleCancel = () => {
            confirmationModal.classList.add('hidden');
            confirmationModal.classList.remove('flex');
            document.body.style.overflow = 'auto';
            cleanup();
            resolve(false);
        };
        
        const cleanup = () => {
            document.getElementById('confirm-accept').removeEventListener('click', handleAccept);
            document.getElementById('confirm-cancel').removeEventListener('click', handleCancel);
        };
        
        document.getElementById('confirm-accept').addEventListener('click', handleAccept);
        document.getElementById('confirm-cancel').addEventListener('click', handleCancel);

        // Cerrar con ESC
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                handleCancel();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    });
}

/**
 * Muestra una notificación toast
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} [tipo='info'] - Tipo: 'success' o 'error'
 */
function mostrarToast(mensaje, tipo = 'info') {
    const toast = document.createElement('div');
    const iconoColor = tipo === 'success' ? 'bg-green-500' : tipo === 'error' ? 'bg-red-500' : 'bg-blue-500';
    const icono = tipo === 'success' ? 'check_circle' : tipo === 'error' ? 'error' : 'info';
    
    toast.className = `fixed top-4 right-4 ${iconoColor} text-white px-6 py-4 rounded-xl shadow-2xl z-[100] flex items-center gap-3`;
    toast.style.animation = 'slideIn 0.3s ease-out';
    toast.innerHTML = `
        <span class="material-symbols-outlined">${icono}</span>
        <span class="font-medium">${mensaje}</span>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, tipo === 'error' ? 4000 : 3000);
}

// Exportar funciones si se usa como módulo
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { mostrarConfirmacion, mostrarToast };
}
