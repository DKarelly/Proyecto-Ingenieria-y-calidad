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
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        // Focus first input
        const firstInput = modal.querySelector('input:not([type="hidden"])');
        if (firstInput) firstInput.focus();
    };

    const closeModal = (modal) => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };

    // Función global para abrir modal
    window.openModal = openModal;

    // Cerrar modales
    closeLoginModal.addEventListener('click', () => closeModal(loginModal));
    closeRegisterModal.addEventListener('click', () => closeModal(registerModal));
    closeForgotPasswordModal.addEventListener('click', () => closeModal(forgotPasswordModal));

    goToRegister.addEventListener('click', () => {
        closeModal(loginModal);
        openModal(registerModal);
    });

    goToLogin.addEventListener('click', () => {
        closeModal(registerModal);
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
                
                // Para pacientes: recargar página para actualizar UI desde sesión
                window.location.reload();
            } else {
                alert(data.error || 'Error al iniciar sesión');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        }
    });

    // Validación de solo números en documento y teléfono
    document.getElementById('register-documento').addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
    
    document.getElementById('register-telefono').addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    // Manejo del formulario de registro
    const registerForm = document.querySelector('#register-modal form');
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            nombres: document.getElementById('register-nombres').value,
            apellidos: document.getElementById('register-apellidos').value,
            documento_identidad: document.getElementById('register-documento').value,
            sexo: document.getElementById('register-sexo').value,
            telefono: document.getElementById('register-telefono').value,
            correo: document.getElementById('register-email').value,
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
                alert('¡Registro exitoso! Ahora puedes iniciar sesión');
                closeModal(registerModal);
                openModal(loginModal);
                registerForm.reset();
                // Resetear selectores
                document.getElementById('register-provincia').disabled = true;
                document.getElementById('register-distrito').disabled = true;
            } else {
                alert(data.error || 'Error al registrarse');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
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
