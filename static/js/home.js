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
    const userAuthButton = document.getElementById('user-auth-button');
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');
    const closeLoginModal = document.getElementById('close-login-modal');
    const closeRegisterModal = document.getElementById('close-register-modal');
    const goToRegister = document.getElementById('go-to-register');
    const goToLogin = document.getElementById('go-to-login');

    const openModal = (modal) => {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    };
    
    const closeModal = (modal) => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };

    userAuthButton.addEventListener('click', () => openModal(loginModal));
    closeLoginModal.addEventListener('click', () => closeModal(loginModal));
    closeRegisterModal.addEventListener('click', () => closeModal(registerModal));

    goToRegister.addEventListener('click', () => {
        closeModal(loginModal);
        openModal(registerModal);
    });
    
    goToLogin.addEventListener('click', () => {
        closeModal(registerModal);
        openModal(loginModal);
    });

    // Cierra el modal si se hace clic fuera del contenido
    window.addEventListener('click', (event) => {
        if (event.target === loginModal) closeModal(loginModal);
        if (event.target === registerModal) closeModal(registerModal);
    });
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
});
