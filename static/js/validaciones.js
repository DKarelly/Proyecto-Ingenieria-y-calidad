/**
 * Validaciones globales para formularios
 * Este archivo contiene funciones de validación que se usan en toda la aplicación
 */

/**
 * Validar que un campo solo contenga números
 * @param {HTMLInputElement} input - El elemento input a validar
 * @param {number} maxLength - Longitud máxima permitida
 */
function validarSoloNumeros(input, maxLength = null) {
    input.addEventListener('input', function(e) {
        // Eliminar cualquier carácter que no sea número
        this.value = this.value.replace(/[^0-9]/g, '');
        
        // Limitar la longitud si se especifica
        if (maxLength && this.value.length > maxLength) {
            this.value = this.value.slice(0, maxLength);
        }
    });
    
    // Prevenir pegar texto que contenga letras
    input.addEventListener('paste', function(e) {
        e.preventDefault();
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        const numericOnly = pastedText.replace(/[^0-9]/g, '');
        
        if (maxLength && numericOnly.length > maxLength) {
            this.value = numericOnly.slice(0, maxLength);
        } else {
            this.value = numericOnly;
        }
    });
    
    // Prevenir teclas no numéricas
    input.addEventListener('keypress', function(e) {
        // Permitir: backspace, delete, tab, escape, enter
        if ([8, 9, 27, 13, 110].indexOf(e.keyCode) !== -1 ||
            // Permitir: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
            (e.keyCode === 65 && e.ctrlKey === true) ||
            (e.keyCode === 67 && e.ctrlKey === true) ||
            (e.keyCode === 86 && e.ctrlKey === true) ||
            (e.keyCode === 88 && e.ctrlKey === true)) {
            return;
        }
        
        // Asegurar que es un número
        if ((e.keyCode < 48 || e.keyCode > 57) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
}

/**
 * Validar DNI (8 dígitos)
 * @param {HTMLInputElement} input - El elemento input del DNI
 */
function validarDNI(input) {
    validarSoloNumeros(input, 8);
    
    // Validación adicional al perder el foco
    input.addEventListener('blur', function() {
        if (this.value.length > 0 && this.value.length !== 8) {
            this.setCustomValidity('El DNI debe tener exactamente 8 dígitos');
            this.reportValidity();
        } else {
            this.setCustomValidity('');
        }
    });
}

/**
 * Validar teléfono (9 dígitos)
 * @param {HTMLInputElement} input - El elemento input del teléfono
 */
function validarTelefono(input) {
    validarSoloNumeros(input, 9);
    
    // Validación adicional al perder el foco
    input.addEventListener('blur', function() {
        if (this.value.length > 0 && this.value.length !== 9) {
            this.setCustomValidity('El teléfono debe tener exactamente 9 dígitos');
            this.reportValidity();
        } else {
            this.setCustomValidity('');
        }
    });
}

/**
 * Validar documento de identidad (8-12 dígitos)
 * @param {HTMLInputElement} input - El elemento input del documento
 */
function validarDocumentoIdentidad(input) {
    validarSoloNumeros(input, 12);
    
    // Validación adicional al perder el foco
    input.addEventListener('blur', function() {
        if (this.value.length > 0 && (this.value.length < 8 || this.value.length > 12)) {
            this.setCustomValidity('El documento debe tener entre 8 y 12 dígitos');
            this.reportValidity();
        } else {
            this.setCustomValidity('');
        }
    });
}

/**
 * Inicializar validaciones automáticamente en todos los campos
 * Busca campos por sus IDs o clases comunes
 */
function inicializarValidaciones() {
    // Validar DNI (8 dígitos exactos)
    const camposDNI = document.querySelectorAll(
        'input[id*="dni"], input[id*="DNI"], ' +
        'input[name*="dni"], input[name*="DNI"], ' +
        'input[placeholder*="12345678"], ' +
        'input[pattern="[0-9]{8}"]'
    );
    camposDNI.forEach(campo => validarDNI(campo));
    
    // Validar documento de identidad (8-12 dígitos)
    const camposDocumento = document.querySelectorAll(
        'input[id*="documento"], input[id*="document"], ' +
        'input[name*="documento"], input[name*="document"]'
    );
    camposDocumento.forEach(campo => {
        // Si ya tiene pattern="[0-9]{8}", es DNI
        if (campo.getAttribute('pattern') === '[0-9]{8}') {
            validarDNI(campo);
        } else {
            validarDocumentoIdentidad(campo);
        }
    });
    
    // Validar teléfono (9 dígitos)
    const camposTelefono = document.querySelectorAll(
        'input[type="tel"], ' +
        'input[id*="telefono"], input[id*="phone"], input[id*="celular"], ' +
        'input[name*="telefono"], input[name*="phone"], input[name*="celular"], ' +
        'input[placeholder*="987654321"], ' +
        'input[pattern="[0-9]{9}"]'
    );
    camposTelefono.forEach(campo => validarTelefono(campo));
    
    console.log('✅ Validaciones numéricas inicializadas');
}

// Inicializar automáticamente cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarValidaciones);
} else {
    inicializarValidaciones();
}

// También inicializar cuando se cargue dinámicamente contenido
// (útil para modales que se cargan después)
window.addEventListener('load', inicializarValidaciones);
