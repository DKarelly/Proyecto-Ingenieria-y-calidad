// Inicializar Swiper Carousels
function initializeSwipers() {
    // Hero Swiper
    new Swiper('.hero-swiper', {
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
    });

    // Specialties Swiper
    new Swiper('.specialties-swiper', {
        loop: false,
        slidesPerView: 1,
        spaceBetween: 30,
        navigation: {
            nextEl: '.specialties-next',
            prevEl: '.specialties-prev',
        },
        breakpoints: {
            640: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
        }
    });

    // Testimonials Swiper
    new Swiper('.testimonials-swiper', {
        loop: false,
        slidesPerView: 1,
        spaceBetween: 30,
        pagination: {
            el: '.testimonials-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.testimonials-next',
            prevEl: '.testimonials-prev',
        },
        breakpoints: {
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
        }
    });
}

// Header con sombra al hacer scroll
function initializeHeader() {
    const header = document.getElementById('main-header');
    window.addEventListener('scroll', () => {
        header.classList.toggle('shadow-md', window.scrollY > 10);
    });
}

// Menú Móvil
function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');
    
    const openMenu = () => mobileMenu.classList.remove('translate-x-full');
    const closeMenu = () => mobileMenu.classList.add('translate-x-full');

    mobileMenuButton.addEventListener('click', openMenu);
    mobileMenuClose.addEventListener('click', closeMenu);
    mobileLinks.forEach(link => link.addEventListener('click', closeMenu));
}

// Animaciones al hacer scroll
function initializeScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.style.animationDelay) * 1000 || 0;
                setTimeout(() => entry.target.classList.add('fade-in-up'), delay);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
}

// Modals de Autenticación
function initializeAuthModals() {
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');
    const forgotPasswordModal = document.getElementById('forgot-password-modal');
    const closeLoginModal = document.getElementById('close-login-modal');
    const closeRegisterModal = document.getElementById('close-register-modal');
    const closeForgotPasswordModal = document.getElementById('close-forgot-password-modal');
    const goToRegister = document.getElementById('go-to-register');
    const goToLogin = document.getElementById('go-to-login');
    const forgotPasswordLink = document.getElementById('forgot-password-link');
    const backToLogin = document.getElementById('back-to-login');

    const openModal = (modal) => {
        // Guardar posición del scroll antes de bloquear
        const scrollY = window.scrollY;
        document.body.dataset.scrollY = scrollY.toString();
        
        // Bloquear scroll del body y html
        document.body.classList.add('modal-open');
        document.documentElement.classList.add('modal-open');
        document.body.style.top = `-${scrollY}px`;
        document.body.style.position = 'fixed';
        document.body.style.width = '100%';
        
        // Mostrar modal
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        
        // Focus first input
        const firstInput = modal.querySelector('input:not([type="hidden"]), select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    };

    // --- Password strength meter helpers ---
    function scorePassword(pw) {
        if (!pw) return { score: 0, label: 'Muy débil', color: '#ef4444' };
        let score = 0;

        // longitud
        if (pw.length >= 6) score += 10;
        if (pw.length >= 8) score += 15;
        if (pw.length >= 12) score += 20;

        // variedad
        if (/[a-z]/.test(pw)) score += 15;
        if (/[A-Z]/.test(pw)) score += 15;
        if (/\d/.test(pw)) score += 15;
        if (/[^A-Za-z0-9]/.test(pw)) score += 15;

        if (score > 100) score = 100;

        let label = 'Muy débil';
        let color = '#ef4444'; // rojo
        if (score >= 90) { label = 'Muy fuerte'; color = '#0ea5a4'; } // teal
        else if (score >= 75) { label = 'Fuerte'; color = '#06b6d4'; } // cyan
        else if (score >= 50) { label = 'Media'; color = '#f59e0b'; } // amarillo
        else if (score >= 30) { label = 'Débil'; color = '#f97316'; } // naranja

        return { score, label, color };
    }

    function updatePasswordStrength(pw) {
        const bar = document.getElementById('password-strength-bar');
        const text = document.getElementById('password-strength-text');
        if (!bar || !text) return;

        const { score, label, color } = scorePassword(pw);
        bar.style.width = score + '%';
        bar.style.background = color;
        bar.style.transition = 'width 200ms ease, background 200ms ease';
        text.textContent = label;
        text.style.color = color;
    }
    const closeModal = (modal) => {
        // Ocultar modal
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        
        // Restaurar scroll del body y html
        const scrollY = document.body.dataset.scrollY || '0';
        document.body.classList.remove('modal-open');
        document.documentElement.classList.remove('modal-open');
        document.body.style.top = '';
        document.body.style.position = '';
        document.body.style.width = '';
        delete document.body.dataset.scrollY;
        
        // Restaurar posición del scroll
        window.scrollTo(0, parseInt(scrollY));
    };

    // Función global para abrir modal
    window.openModal = openModal;

    // Cerrar modales
    closeLoginModal.addEventListener('click', () => closeModal(loginModal));
    closeRegisterModal.addEventListener('click', () => closeModal(registerModal));
    closeForgotPasswordModal.addEventListener('click', () => closeModal(forgotPasswordModal));

    goToRegister.addEventListener('click', () => {
        // No cerrar completamente el modal, solo cambiar la visibilidad para mantener el scroll bloqueado
        loginModal.classList.add('hidden');
        loginModal.classList.remove('flex');
        openModal(registerModal);
    });

    goToLogin.addEventListener('click', () => {
        // No cerrar completamente el modal, solo cambiar la visibilidad para mantener el scroll bloqueado
        registerModal.classList.add('hidden');
        registerModal.classList.remove('flex');
        openModal(loginModal);
    });

    forgotPasswordLink.addEventListener('click', () => {
        closeModal(loginModal);
        openModal(forgotPasswordModal);
    });

    backToLogin.addEventListener('click', () => {
        closeModal(forgotPasswordModal);
        openModal(loginModal);
    });

    // Cierra el modal si se hace clic fuera del contenido
    window.addEventListener('click', (event) => {
        if (event.target === loginModal) closeModal(loginModal);
        if (event.target === registerModal) closeModal(registerModal);
        if (event.target === forgotPasswordModal) closeModal(forgotPasswordModal);
    });

    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' || event.keyCode === 27) {
            if (!loginModal.classList.contains('hidden')) closeModal(loginModal);
            if (!registerModal.classList.contains('hidden')) closeModal(registerModal);
            if (!forgotPasswordModal.classList.contains('hidden')) closeModal(forgotPasswordModal);
        }
    });

    // Toggle mostrar/ocultar contraseña en login
    const toggleLoginPassword = document.getElementById('toggle-login-password');
    const loginPasswordInput = document.getElementById('login-password');
    const loginPasswordEyeIcon = document.getElementById('login-password-eye-icon');
    
    if (toggleLoginPassword && loginPasswordInput && loginPasswordEyeIcon) {
        toggleLoginPassword.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (loginPasswordInput.type === 'password') {
                loginPasswordInput.type = 'text';
                loginPasswordEyeIcon.classList.remove('fa-eye');
                loginPasswordEyeIcon.classList.add('fa-eye-slash');
            } else {
                loginPasswordInput.type = 'password';
                loginPasswordEyeIcon.classList.remove('fa-eye-slash');
                loginPasswordEyeIcon.classList.add('fa-eye');
            }
        });
    }

    // Manejo del formulario de login
    const loginForm = document.querySelector('#login-modal form');
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/usuarios/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    correo: email,
                    contrasena: password
                })
            });

            const data = await response.json();

            if (data.success) {
                // Verificar si es empleado y redirigir al panel
                if (data.usuario.tipo_usuario === 'empleado') {
                    // Redirigir al panel de administración
                    window.location.href = '/admin/';
                    return;
                }
                
                // Para pacientes: verificar si hay una URL de redirección guardada
                const redirectUrl = sessionStorage.getItem('redirect_after_login');
                if (redirectUrl) {
                    sessionStorage.removeItem('redirect_after_login');
                    window.location.href = redirectUrl;
                } else {
                    // Recargar página para actualizar UI desde sesión
                    window.location.reload();
                }
            } else {
                alert(data.error || 'Error al iniciar sesión');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        }
    });

    // Configuración de tipos de documento
    const tiposDocumento = {
        'DNI': { min: 8, max: 8, pattern: /^[0-9]{8}$/, placeholder: '12345678', hint: 'Ingrese 8 dígitos', inputmode: 'numeric' },
        'CE': { min: 9, max: 12, pattern: /^[0-9]{9,12}$/, placeholder: '123456789', hint: 'Ingrese entre 9 y 12 dígitos', inputmode: 'numeric' },
        'PASAPORTE': { min: 6, max: 15, pattern: /^[A-Z0-9]{6,15}$/, placeholder: 'ABC123456', hint: 'Ingrese entre 6 y 15 caracteres (letras y números)', inputmode: 'text' }
    };

    // Configurar fecha máxima de nacimiento (18 años atrás)
    const fechaNacimiento = document.getElementById('register-nacimiento');
    if (fechaNacimiento) {
        const today = new Date();
        const maxDate = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
        fechaNacimiento.max = maxDate.toISOString().split('T')[0];
    }

    // Manejar tipo de documento
    const tipoDocumentoSelect = document.getElementById('register-tipo-documento');
    const documentoInput = document.getElementById('register-documento');
    const documentoHint = document.getElementById('register-documento-hint');
    
    if (tipoDocumentoSelect && documentoInput) {
        tipoDocumentoSelect.addEventListener('change', function() {
            const tipo = this.value;
            documentoInput.value = '';
            
            if (tipo && tiposDocumento[tipo]) {
                const config = tiposDocumento[tipo];
                documentoInput.maxLength = config.max;
                documentoInput.placeholder = config.placeholder;
                if (documentoHint) documentoHint.textContent = config.hint;
                documentoInput.disabled = false;
                documentoInput.setAttribute('inputmode', config.inputmode);
                documentoInput.classList.remove('border-red-500');
                clearFieldError(documentoInput);
            } else {
                documentoInput.disabled = true;
                documentoInput.placeholder = 'Seleccione tipo primero';
                if (documentoHint) documentoHint.textContent = 'Seleccione el tipo de documento primero';
            }
        });
    }

    // Validación de documento según tipo
    if (documentoInput) {
        documentoInput.addEventListener('input', function(e) {
            const tipo = tipoDocumentoSelect ? tipoDocumentoSelect.value : 'DNI';
            if (tipo === 'PASAPORTE') {
                // Solo mayúsculas y números para pasaporte
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            } else {
                // Solo números para DNI y CE
                this.value = this.value.replace(/[^0-9]/g, '');
            }
        });
    }
    
    // Validación de teléfono (solo números)
    const telefonoInput = document.getElementById('register-telefono');
    if (telefonoInput) {
        telefonoInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }

    // Toggle visibilidad de contraseña en registro
    const toggleRegisterPassword = document.getElementById('toggle-register-password');
    const registerPasswordInput = document.getElementById('register-password');
    const registerPasswordEyeIcon = document.getElementById('register-password-eye-icon');
    
    if (toggleRegisterPassword && registerPasswordInput && registerPasswordEyeIcon) {
        toggleRegisterPassword.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (registerPasswordInput.type === 'password') {
                registerPasswordInput.type = 'text';
                registerPasswordEyeIcon.classList.remove('fa-eye');
                registerPasswordEyeIcon.classList.add('fa-eye-slash');
            } else {
                registerPasswordInput.type = 'password';
                registerPasswordEyeIcon.classList.remove('fa-eye-slash');
                registerPasswordEyeIcon.classList.add('fa-eye');
            }
        });
    }

    // Mejorar función updatePasswordStrength para mostrar indicador
    const originalUpdatePasswordStrength = updatePasswordStrength;
    updatePasswordStrength = function(pw) {
        originalUpdatePasswordStrength(pw);
        const strengthDiv = document.getElementById('password-strength');
        const requirements = {
            length: document.getElementById('req-length'),
            letter: document.getElementById('req-letter'),
            number: document.getElementById('req-number')
        };
        
        if (!strengthDiv) return;
        
        if (!pw || pw.length === 0) {
            strengthDiv.classList.add('hidden');
            return;
        }
        
        strengthDiv.classList.remove('hidden');
        
        // Validar requisitos
        const hasLength = pw.length >= 6;
        const hasLetter = /[A-Za-z]/.test(pw);
        const hasNumber = /\d/.test(pw);
        
        // Actualizar indicadores
        if (requirements.length) {
            requirements.length.querySelector('span').textContent = hasLength ? '✓' : '✗';
            requirements.length.querySelector('span').className = hasLength ? 'text-green-500' : 'text-red-500';
        }
        if (requirements.letter) {
            requirements.letter.querySelector('span').textContent = hasLetter ? '✓' : '✗';
            requirements.letter.querySelector('span').className = hasLetter ? 'text-green-500' : 'text-red-500';
        }
        if (requirements.number) {
            requirements.number.querySelector('span').textContent = hasNumber ? '✓' : '✗';
            requirements.number.querySelector('span').className = hasNumber ? 'text-green-500' : 'text-red-500';
        }
    };

    // Manejo del formulario de registro con validaciones cliente
    const registerForm = document.querySelector('#register-modal form');
    const showFieldError = (field, message) => {
        clearFieldError(field);
        field.classList.add('border-red-500');
        
        // Buscar elemento de error específico por ID
        const errorId = field.id + '-error';
        const errorElement = document.getElementById(errorId);
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        } else {
            // Fallback: crear elemento de error si no existe
            const msg = document.createElement('p');
            msg.id = errorId;
            msg.className = 'input-error text-xs text-red-600 mt-1';
            msg.textContent = message;
            field.parentNode.appendChild(msg);
        }
    };

    const clearFieldError = (field) => {
        field.classList.remove('border-red-500');
        
        // Limpiar elemento de error específico
        const errorId = field.id + '-error';
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.classList.add('hidden');
            errorElement.textContent = '';
        }
        
        // Limpiar elementos de error antiguos
        const oldError = field.parentNode.querySelector('.input-error');
        if (oldError) oldError.remove();
    };

    const clearAllErrors = (form) => {
        form.querySelectorAll('.input-error').forEach(el => el.remove());
        form.querySelectorAll('.border-red-500').forEach(f => f.classList.remove('border-red-500'));
    };

    const validateRegister = () => {
        clearAllErrors(registerForm);
        const nombres = document.getElementById('register-nombres');
        const apellidos = document.getElementById('register-apellidos');
        const tipoDocumento = document.getElementById('register-tipo-documento');
        const documento = document.getElementById('register-documento');
        const sexo = document.getElementById('register-sexo');
        const telefono = document.getElementById('register-telefono');
        const correo = document.getElementById('register-email');
        const nacimiento = document.getElementById('register-nacimiento');
        const departamento = document.getElementById('register-departamento');
        const provincia = document.getElementById('register-provincia');
        const distrito = document.getElementById('register-distrito');
        const password = document.getElementById('register-password');

        // Validar nombres
        if (!nombres.value || nombres.value.trim().length < 2) {
            showFieldError(nombres, 'Ingrese al menos 2 caracteres en nombres');
            nombres.focus();
            return false;
        }
        if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(nombres.value.trim())) {
            showFieldError(nombres, 'Los nombres solo pueden contener letras y espacios');
            nombres.focus();
            return false;
        }

        // Validar apellidos
        if (!apellidos.value || apellidos.value.trim().length < 2) {
            showFieldError(apellidos, 'Ingrese al menos 2 caracteres en apellidos');
            apellidos.focus();
            return false;
        }
        if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(apellidos.value.trim())) {
            showFieldError(apellidos, 'Los apellidos solo pueden contener letras y espacios');
            apellidos.focus();
            return false;
        }

        // Validar tipo de documento
        if (!tipoDocumento || !tipoDocumento.value) {
            showFieldError(tipoDocumento, 'Seleccione un tipo de documento');
            if (tipoDocumento) tipoDocumento.focus();
            return false;
        }

        // Validar documento según tipo
        if (!documento.value || documento.disabled) {
            showFieldError(documento, 'Ingrese el número de documento');
            documento.focus();
            return false;
        }
        
        const tipoDoc = tipoDocumento.value;
        if (tiposDocumento[tipoDoc]) {
            const config = tiposDocumento[tipoDoc];
            if (!config.pattern.test(documento.value)) {
                showFieldError(documento, config.hint);
                documento.focus();
                return false;
            }
        }

        if (!sexo.value) {
            showFieldError(sexo, 'Seleccione un sexo');
            sexo.focus();
            return false;
        }

        if (!/^\d{9}$/.test(telefono.value)) {
            showFieldError(telefono, 'El teléfono debe tener 9 dígitos');
            telefono.focus();
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(correo.value)) {
            showFieldError(correo, 'Correo electrónico inválido');
            correo.focus();
            return false;
        }

        if (!nacimiento.value) {
            showFieldError(nacimiento, 'Ingrese la fecha de nacimiento');
            nacimiento.focus();
            return false;
        } else {
            const today = new Date();
            const dob = new Date(nacimiento.value);
            const age = today.getFullYear() - dob.getFullYear() - (today.getMonth() < dob.getMonth() || (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate()) ? 1 : 0);
            if (isNaN(age) || age < 18) {
                showFieldError(nacimiento, 'Debes ser mayor de 18 años');
                nacimiento.focus();
                return false;
            }
        }

        if (!departamento.value) {
            showFieldError(departamento, 'Seleccione un departamento');
            departamento.focus();
            return false;
        }

        if (!provincia.value) {
            showFieldError(provincia, 'Seleccione una provincia');
            provincia.focus();
            return false;
        }

        if (!distrito.value) {
            showFieldError(distrito, 'Seleccione un distrito');
            distrito.focus();
            return false;
        }

        // Validar contraseña
        if (!password.value || password.value.length < 6) {
            showFieldError(password, 'La contraseña debe tener al menos 6 caracteres');
            password.focus();
            return false;
        }
        
        // Validar complejidad de contraseña
        const hasLetter = /[A-Za-z]/.test(password.value);
        const hasNumber = /\d/.test(password.value);
        if (!hasLetter || !hasNumber) {
            showFieldError(password, 'La contraseña debe incluir letras y números');
            password.focus();
            return false;
        }

        return true;
    };

    // Validación en tiempo real por campo
    // touched tracking: no mostrar errores hasta que el usuario toque el campo
    const touched = {};

    const validateField = (field) => {
        const id = field.id;
        const val = field.value.trim();

        // evitar validar selects vacíos con input event
        if (field.tagName.toLowerCase() === 'select') {
            // solo validar cuando haya un value
        }

        // reglas por campo
        try {
            if (id === 'register-nombres') {
                if (!val || val.length < 2) {
                    if (touched[id]) showFieldError(field, 'Mínimo 2 caracteres');
                } else clearFieldError(field);
            } else if (id === 'register-apellidos') {
                if (!val || val.length < 2) {
                    if (touched[id]) showFieldError(field, 'Mínimo 2 caracteres');
                } else clearFieldError(field);
            } else if (id === 'register-tipo-documento') {
                if (!val) {
                    if (touched[id]) showFieldError(field, 'Seleccione un tipo de documento');
                } else {
                    clearFieldError(field);
                    // Habilitar campo de documento
                    if (documentoInput && tiposDocumento[val]) {
                        documentoInput.disabled = false;
                        const config = tiposDocumento[val];
                        documentoInput.maxLength = config.max;
                        documentoInput.placeholder = config.placeholder;
                        if (documentoHint) documentoHint.textContent = config.hint;
                        documentoInput.setAttribute('inputmode', config.inputmode);
                    }
                }
            } else if (id === 'register-documento') {
                const tipoDoc = tipoDocumentoSelect ? tipoDocumentoSelect.value : '';
                if (!tipoDoc) {
                    if (touched[id]) showFieldError(field, 'Seleccione tipo de documento primero');
                } else if (tiposDocumento[tipoDoc]) {
                    const config = tiposDocumento[tipoDoc];
                    if (!config.pattern.test(val)) {
                        if (touched[id]) showFieldError(field, config.hint);
                    } else {
                        clearFieldError(field);
                    }
                }
            } else if (id === 'register-sexo') {
                if (!val) {
                    if (touched[id]) showFieldError(field, 'Seleccione una opción');
                } else clearFieldError(field);
            } else if (id === 'register-telefono') {
                if (!/^\d*$/.test(val)) {
                    if (touched[id]) showFieldError(field, 'Solo dígitos');
                } else if (val.length > 0 && val.length < 9) {
                    if (touched[id]) showFieldError(field, 'Número incompleto');
                } else if (val.length === 9) clearFieldError(field);
                else clearFieldError(field);
            } else if (id === 'register-email') {
                const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!val) {
                    if (touched[id]) showFieldError(field, 'Ingrese un correo');
                } else if (!re.test(val)) {
                    if (touched[id]) showFieldError(field, 'Correo inválido');
                } else clearFieldError(field);
            } else if (id === 'register-nacimiento') {
                if (!val) {
                    if (touched[id]) showFieldError(field, 'Ingrese fecha');
                } else {
                    const today = new Date();
                    const dob = new Date(val);
                    const age = today.getFullYear() - dob.getFullYear() - (today.getMonth() < dob.getMonth() || (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate()) ? 1 : 0);
                    if (isNaN(age)) {
                        if (touched[id]) showFieldError(field, 'Fecha inválida');
                    } else if (age < 18) {
                        if (touched[id]) showFieldError(field, 'Debes ser mayor de 18 años');
                    } else clearFieldError(field);
                }
            } else if (id === 'register-departamento' || id === 'register-provincia' || id === 'register-distrito') {
                if (!val) {
                    if (touched[id]) showFieldError(field, 'Seleccione una opción');
                } else clearFieldError(field);
            } else if (id === 'register-password') {
                if (!val || val.length < 6) {
                    if (touched[id]) showFieldError(field, 'Mínimo 6 caracteres');
                } else {
                    // chequeo básico de complejidad (letra + número)
                    const ok = /[A-Za-z]/.test(val) && /\d/.test(val);
                    if (!ok) {
                        if (touched[id]) showFieldError(field, 'Incluye letras y números');
                    } else clearFieldError(field);
                }
            }
        } catch (err) {
            // si algo falla, no romper la UX
            // console.warn('validateField error', err);
        }
    };

    // Asignar listeners: input para campos de texto, change para selects y date
    const realtimeFields = [
        'register-nombres','register-apellidos','register-documento','register-telefono','register-email','register-password'
    ];
    
    // Agregar validación en tiempo real para tipo de documento
    if (tipoDocumentoSelect) {
        tipoDocumentoSelect.addEventListener('change', () => {
            touched['register-tipo-documento'] = true;
            validateField(tipoDocumentoSelect);
            if (documentoInput && !documentoInput.disabled) {
                touched['register-documento'] = true;
                validateField(documentoInput);
            }
        });
    }
    realtimeFields.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', () => { validateField(el); if (id === 'register-password') updatePasswordStrength(el.value); });
            el.addEventListener('focus', () => { touched[id] = true; });
            el.addEventListener('blur', () => { touched[id] = true; validateField(el); if (id === 'register-password') updatePasswordStrength(el.value); });
            // inicializar indicador si ya hay valor (p. ej. retorno al formulario)
            if (id === 'register-password' && el.value) updatePasswordStrength(el.value);
        }
    });

    const changeFields = ['register-tipo-documento','register-sexo','register-nacimiento','register-departamento','register-provincia','register-distrito'];
    changeFields.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => validateField(el));
            el.addEventListener('focus', () => { touched[id] = true; });
            el.addEventListener('blur', () => { touched[id] = true; validateField(el); });
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!validateRegister()) return;

        const submitBtn = registerForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Registrando...';

        const formData = {
            nombres: document.getElementById('register-nombres').value.trim(),
            apellidos: document.getElementById('register-apellidos').value.trim(),
            tipo_documento: document.getElementById('register-tipo-documento').value,
            documento_identidad: document.getElementById('register-documento').value.trim(),
            sexo: document.getElementById('register-sexo').value,
            telefono: document.getElementById('register-telefono').value.trim(),
            correo: document.getElementById('register-email').value.trim(),
            fecha_nacimiento: document.getElementById('register-nacimiento').value,
            id_departamento: document.getElementById('register-departamento').value,
            id_provincia: document.getElementById('register-provincia').value,
            id_distrito: document.getElementById('register-distrito').value,
            contrasena: document.getElementById('register-password').value
        };

        try {
            const response = await fetch('/usuarios/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                // feedback más profesional
                const successMsg = document.createElement('div');
                successMsg.className = 'text-sm text-green-600 text-center my-4';
                successMsg.textContent = 'Registro exitoso. Ahora puedes iniciar sesión.';
                registerForm.parentNode.insertBefore(successMsg, registerForm.nextSibling);

                setTimeout(() => {
                    closeModal(registerModal);
                    openModal(loginModal);
                    registerForm.reset();
                    document.getElementById('register-provincia').disabled = true;
                    document.getElementById('register-distrito').disabled = true;
                    successMsg.remove();
                }, 1200);
            } else {
                // Mostrar errores del servidor junto al campo correspondiente si es posible
                const serverMsg = data && data.error ? data.error.toString() : null;
                if (serverMsg) {
                    // elegir campo por palabras clave
                    const lower = serverMsg.toLowerCase();
                    const emailField = document.getElementById('register-email');
                    const docField = document.getElementById('register-documento');
                    const departamentoField = document.getElementById('register-departamento');
                    const provinciaField = document.getElementById('register-provincia');
                    const distritoField = document.getElementById('register-distrito');

                    const mapAndShow = (field) => {
                        if (!field) return false;
                        showFieldError(field, serverMsg);
                        field.focus();
                        return true;
                    };

                    if (/correo|email/.test(lower)) {
                        mapAndShow(emailField);
                    } else if (/documento|dni/.test(lower)) {
                        mapAndShow(docField);
                    } else if (/departamento/.test(lower)) {
                        mapAndShow(departamentoField);
                    } else if (/provincia/.test(lower)) {
                        mapAndShow(provinciaField);
                    } else if (/distrito/.test(lower)) {
                        mapAndShow(distritoField);
                    } else {
                        // si no podemos mapear, mostrar error global arriba del formulario
                        clearAllErrors(registerForm);
                        const globalErr = document.createElement('div');
                        globalErr.className = 'text-sm text-red-600 text-center my-4 server-error';
                        globalErr.textContent = serverMsg;
                        // eliminar errores globales previos
                        const prev = registerForm.parentNode.querySelector('.server-error');
                        if (prev) prev.remove();
                        registerForm.parentNode.insertBefore(globalErr, registerForm);
                    }
                } else {
                    alert('Error al registrarse');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // Manejo del formulario de recuperación de contraseña
    const sendCodeBtn = document.getElementById('send-code-btn');
    const emailMessage = document.getElementById('email-message');
    const formMessage = document.getElementById('form-message');
    const codeField = document.getElementById('code-field');
    const passwordField = document.getElementById('password-field');
    const confirmPasswordField = document.getElementById('confirm-password-field');
    const resetPasswordBtn = document.getElementById('reset-password-btn');

    // Enviar código de verificación
    sendCodeBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const email = document.getElementById('forgot-email').value.trim();

        emailMessage.className = 'text-sm mt-2 hidden';
        emailMessage.textContent = '';

        if (!email) {
            emailMessage.textContent = 'Por favor ingrese su correo electrónico';
            emailMessage.className = 'text-sm mt-2 text-red-600';
            return;
        }

        sendCodeBtn.disabled = true;
        sendCodeBtn.textContent = 'Enviando...';

        try {
            const response = await fetch('/usuarios/api/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ correo: email })
            });

            if (response.ok) {
                emailMessage.textContent = 'Código enviado. Revisa tu correo electrónico';
                emailMessage.className = 'text-sm mt-2 text-green-600';
                sendCodeBtn.textContent = 'Reenviar';
                
                // Mostrar campos adicionales
                codeField.style.display = 'block';
                passwordField.style.display = 'block';
                confirmPasswordField.style.display = 'block';
                resetPasswordBtn.style.display = 'block';
            } else {
                const data = await response.json().catch(() => ({}));
                emailMessage.textContent = data.error || 'No se pudo enviar el código. Intente nuevamente.';
                emailMessage.className = 'text-sm mt-2 text-red-600';
                sendCodeBtn.textContent = 'Enviar';
            }
        } catch (error) {
            emailMessage.textContent = 'Error de red. Intente nuevamente.';
            emailMessage.className = 'text-sm mt-2 text-red-600';
            sendCodeBtn.textContent = 'Enviar';
        } finally {
            sendCodeBtn.disabled = false;
        }
    });

    // Enviar formulario completo para cambiar contraseña
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    forgotPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('forgot-email').value.trim();
        const code = document.getElementById('forgot-code').value.trim();
        const newPassword = document.getElementById('forgot-new-password').value;
        const confirmPassword = document.getElementById('forgot-confirm-password').value;

        formMessage.className = 'text-sm mt-3 text-center hidden';
        formMessage.textContent = '';

        // Validaciones
        if (!email || !code || !newPassword || !confirmPassword) {
            formMessage.textContent = 'Complete todos los campos';
            formMessage.className = 'text-sm mt-3 text-center text-red-600';
            return;
        }

        if (code.length !== 6 || !/^\d{6}$/.test(code)) {
            formMessage.textContent = 'El código debe ser de 6 dígitos';
            formMessage.className = 'text-sm mt-3 text-center text-red-600';
            return;
        }

        if (newPassword !== confirmPassword) {
            formMessage.textContent = 'Las contraseñas no coinciden';
            formMessage.className = 'text-sm mt-3 text-center text-red-600';
            return;
        }

        if (newPassword.length < 6) {
            formMessage.textContent = 'La contraseña debe tener al menos 6 caracteres';
            formMessage.className = 'text-sm mt-3 text-center text-red-600';
            return;
        }

        resetPasswordBtn.disabled = true;
        resetPasswordBtn.textContent = 'Procesando...';

        try {
            const response = await fetch('/usuarios/api/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    correo: email,
                    codigo: code,
                    nueva_contrasena: newPassword
                })
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok && data.success) {
                formMessage.textContent = '✓ Contraseña actualizada. Redirigiendo...';
                formMessage.className = 'text-sm mt-3 text-center text-green-600';
                
                setTimeout(() => {
                    closeModal(forgotPasswordModal);
                    openModal(loginModal);
                    forgotPasswordForm.reset();
                    // Ocultar campos adicionales
                    codeField.style.display = 'none';
                    passwordField.style.display = 'none';
                    confirmPasswordField.style.display = 'none';
                    resetPasswordBtn.style.display = 'none';
                    sendCodeBtn.textContent = 'Enviar';
                }, 1500);
            } else {
                formMessage.textContent = data.error || 'No se pudo actualizar la contraseña';
                formMessage.className = 'text-sm mt-3 text-center text-red-600';
                resetPasswordBtn.disabled = false;
                resetPasswordBtn.textContent = 'Cambiar Contraseña';
            }
        } catch (error) {
            formMessage.textContent = 'Error de red. Intente nuevamente';
            formMessage.className = 'text-sm mt-3 text-center text-red-600';
            resetPasswordBtn.disabled = false;
            resetPasswordBtn.textContent = 'Cambiar Contraseña';
        }
    });
    
    // Cargar selectores en cascada para ubicación
    loadUbicacionSelectors();
}

// Cargar departamentos, provincias y distritos en cascada
function loadUbicacionSelectors() {
    const departamentoSelect = document.getElementById('register-departamento');
    const provinciaSelect = document.getElementById('register-provincia');
    const distritoSelect = document.getElementById('register-distrito');
    
    // Cargar departamentos al abrir el modal de registro
    const goToRegister = document.getElementById('go-to-register');
    goToRegister.addEventListener('click', loadDepartamentos);
    
    // También cargar al inicio si el modal está presente
    loadDepartamentos();
    
    // Cargar departamentos
    async function loadDepartamentos() {
        try {
            const response = await fetch('/usuarios/api/departamentos');
            const departamentos = await response.json();
            
            departamentoSelect.innerHTML = '<option value="">Seleccione...</option>';
            departamentos.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.id_departamento;
                option.textContent = dept.nombre;
                departamentoSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error cargando departamentos:', error);
        }
    }
    
    // Cuando cambia el departamento, cargar provincias
    departamentoSelect.addEventListener('change', async (e) => {
        const idDepartamento = e.target.value;
        
        // Resetear provincia y distrito
        provinciaSelect.innerHTML = '<option value="">Seleccione...</option>';
        distritoSelect.innerHTML = '<option value="">Seleccione provincia primero</option>';
        distritoSelect.disabled = true;
        
        if (!idDepartamento) {
            provinciaSelect.disabled = true;
            return;
        }
        
        try {
            const response = await fetch(`/usuarios/api/provincias/${idDepartamento}`);
            const provincias = await response.json();
            
            provincias.forEach(prov => {
                const option = document.createElement('option');
                option.value = prov.id_provincia;
                option.textContent = prov.nombre;
                provinciaSelect.appendChild(option);
            });
            
            provinciaSelect.disabled = false;
        } catch (error) {
            console.error('Error cargando provincias:', error);
        }
    });
    
    // Cuando cambia la provincia, cargar distritos
    provinciaSelect.addEventListener('change', async (e) => {
        const idProvincia = e.target.value;
        
        // Resetear distrito
        distritoSelect.innerHTML = '<option value="">Seleccione...</option>';
        
        if (!idProvincia) {
            distritoSelect.disabled = true;
            return;
        }
        
        try {
            const response = await fetch(`/usuarios/api/distritos/${idProvincia}`);
            const distritos = await response.json();
            
            distritos.forEach(dist => {
                const option = document.createElement('option');
                option.value = dist.id_distrito;
                option.textContent = dist.nombre;
                distritoSelect.appendChild(option);
            });
            
            distritoSelect.disabled = false;
        } catch (error) {
            console.error('Error cargando distritos:', error);
        }
    });
}

// Actualizar el botón de usuario cuando está logueado
function updateUserButton(usuario) {
    const userAuthButton = document.getElementById('user-auth-button');
    
    // Verificar que el elemento existe antes de modificarlo
    if (!userAuthButton) {
        console.warn('Elemento user-auth-button no encontrado');
        return;
    }

    if (usuario) {
        // Usuario logueado - mostrar menú desplegable
        const inicial = usuario.nombre ? usuario.nombre.charAt(0).toUpperCase() : 'U';

        userAuthButton.innerHTML = `
            <div class="user-button-wrapper">
                <div class="w-10 h-10 bg-cyan-500 rounded-full flex items-center justify-center hover:bg-cyan-600 transition-colors duration-300 cursor-pointer">
                    <span class="text-white font-bold text-lg">${inicial}</span>
                </div>
                <div class="user-menu">
                    <div class="px-4 py-3 border-b border-gray-200">
                        <p class="font-semibold text-gray-800 text-sm">${usuario.nombre}</p>
                        <p class="text-xs text-gray-500 mt-1">${usuario.correo}</p>
                    </div>
                    <div class="py-1">
                        <a href="/usuarios/perfil" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">Mi Perfil</a>
                        ${usuario.tipo_usuario === 'empleado' ? '<a href="/usuarios/listar" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">Gestionar Usuarios</a>' : ''}
                        <button onclick="logout()" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">Cerrar Sesión</button>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Usuario no logueado - mostrar botón de login
        userAuthButton.innerHTML = `
            <div class="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center hover:bg-gray-300 transition-colors duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user text-gray-600"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
        `;

        // Agregar event listener SOLO cuando no está logueado
        userAuthButton.addEventListener('click', () => {
            const loginModal = document.getElementById('login-modal');
            openModal(loginModal);
        });
    }
}

// Cerrar sesión
function logout() {
    if (confirm('¿Estás seguro que deseas cerrar sesión?')) {
        // Redirigir a la página de logout que limpiará la sesión
        window.location.href = '/logout';
    }
}

// Función para mostrar/ocultar contraseñas
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('svg');

    if (input.type === 'password') {
        input.type = 'text';
        icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-10-7-10-7a15.18 15.18 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 10 7 10 7a15.18 15.18 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
    } else {
        input.type = 'password';
        icon.innerHTML = '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>';
    }
}

// Hacer la función global para que pueda ser llamada desde HTML
window.togglePasswordVisibility = togglePasswordVisibility;

// Verificar si hay usuario logueado al cargar la página
async function checkUserSession() {
    try {
        // Preferir usuario ya inyectado por el servidor (window.usuario)
        if (window.usuario) {
            updateUserButton(window.usuario);
            return;
        }

        // Fallback: consultar la API si no se inyectó el usuario (p.ej. páginas sin header)
        const response = await fetch('/usuarios/api/session');
        if (response.ok) {
            const data = await response.json();
            if (data.logged_in) {
                updateUserButton(data.usuario);
            } else {
                updateUserButton(null);
            }
        } else {
            updateUserButton(null);
        }
    } catch (error) {
        console.error('Error al verificar sesión:', error);
        updateUserButton(null);
    }
}

// Inicializar todo cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Esperar a que Swiper esté disponible
    if (typeof Swiper !== 'undefined') {
        initializeSwipers();
    } else {
        // Si Swiper aún no está cargado, esperar un poco
        setTimeout(() => {
            if (typeof Swiper !== 'undefined') {
                initializeSwipers();
            }
        }, 100);
    }
    
    initializeHeader();
    initializeMobileMenu();
    initializeScrollAnimations();
    initializeAuthModals();
    checkUserSession(); // Verificar sesión al cargar
});
