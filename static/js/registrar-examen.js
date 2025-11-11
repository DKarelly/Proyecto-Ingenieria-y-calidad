// Script para registro de exámenes - Versión simple
let currentStep = 1;
let serviciosDisponibles = [];
let especialidadesDisponibles = [];
let formData = {
    id_servicio: null,
    servicio_nombre: '',
    id_empleado: null,
    empleado_nombre: '',
    id_programacion: null,
    fecha: '',
    hora_inicio: '',
    hora_fin: '',
    dia_semana: ''
};
let medicosDisponibles = [];
let currentPageMedicos = 1;
const medicosPerPage = 6;
let currentPageServicios = 1;
const serviciosPerPage = 6;

document.addEventListener('DOMContentLoaded', async function() {
    console.log('[Init] Cargando...');
    await cargarEspecialidades();
    await cargarServiciosExamen();
    setupEventListeners();
});

function setupEventListeners() {
    const filtro = document.getElementById('filtroEspecialidad');
    if (filtro) filtro.addEventListener('change', filtrarServiciosPorEspecialidad);
    
    const btn1 = document.getElementById('btnStep1Next');
    if (btn1) btn1.addEventListener('click', async function() {
        if (formData.id_servicio) {
            // Actualizar el nombre del servicio en el Paso 2
            const ss = document.getElementById('servicioSeleccionado');
            if (ss) ss.textContent = formData.servicio_nombre;
            
            await cargarMedicos();
            goToStep(2);
        } else alert('Selecciona un examen');
    });
    
    const btn2b = document.getElementById('btnStep2Back');
    if (btn2b) btn2b.addEventListener('click', () => goToStep(1));
    
    const btn2n = document.getElementById('btnStep2Next');
    if (btn2n) btn2n.addEventListener('click', async function() {
        if (formData.id_empleado) {
            const ss = document.getElementById('servicioSeleccionado');
            const ss2 = document.getElementById('servicioSeleccionado2');
            const ms = document.getElementById('medicoSeleccionado');
            if (ss) ss.textContent = formData.servicio_nombre;
            if (ss2) ss2.textContent = formData.servicio_nombre;
            if (ms) ms.textContent = formData.empleado_nombre;
            await cargarHorariosSemanales();
            goToStep(3);
        } else alert('Selecciona un médico');
    });
    
    const btn3b = document.getElementById('btnStep3Back');
    if (btn3b) btn3b.addEventListener('click', () => goToStep(2));
    
    const btn3n = document.getElementById('btnStep3Next');
    if (btn3n) btn3n.addEventListener('click', function() {
        if (formData.id_programacion) {
            mostrarResumen();
            goToStep(4);
        } else alert('Selecciona un horario');
    });
    
    const btn4b = document.getElementById('btnStep4Back');
    if (btn4b) btn4b.addEventListener('click', () => goToStep(3));
    
    const btnConf = document.getElementById('btnConfirmar');
    if (btnConf) btnConf.addEventListener('click', async (e) => {
        e.preventDefault();
        await confirmarExamen();
    });
}

async function cargarEspecialidades() {
    try {
        console.log('[Especialidades] Iniciando carga...');
        const r = await fetch('/reservas/api/especialidades-publicas');
        const d = await r.json();
        console.log('[Especialidades] Respuesta:', d);
        if (r.ok && d.success && d.especialidades) {
            especialidadesDisponibles = d.especialidades;
            const s = document.getElementById('filtroEspecialidad');
            if (s) {
                d.especialidades.forEach(e => {
                    const o = document.createElement('option');
                    o.value = e.id_especialidad;
                    o.textContent = e.nombre;
                    s.appendChild(o);
                });
                console.log('[Especialidades] Cargadas:', d.especialidades.length, 'especialidades');
            }
        }
    } catch (e) { 
        console.error('[Especialidades] Error:', e); 
    }
}

async function cargarServiciosExamen() {
    const l = document.getElementById('loadingServicios');
    const c = document.getElementById('serviciosContainer');
    const e = document.getElementById('errorServicios');
    try {
        console.log('[Servicios] Iniciando carga...');
        const r = await fetch('/reservas/api/servicios-examen');
        const d = await r.json();
        console.log('[Servicios] Respuesta:', d);
        if (r.ok && d.success && d.servicios) {
            serviciosDisponibles = d.servicios;
            console.log('[Servicios] Total cargados:', serviciosDisponibles.length);
            if (serviciosDisponibles.length === 0) {
                if (e) e.classList.remove('hidden');
                if (l) l.classList.add('hidden');
                return;
            }
            renderizarServicios(serviciosDisponibles);
            if (l) l.classList.add('hidden');
            if (c) c.classList.remove('hidden');
        }
    } catch (err) {
        console.error('[Servicios] Error:', err);
        if (e) e.classList.remove('hidden');
        if (l) l.classList.add('hidden');
    }
}

function filtrarServiciosPorEspecialidad() {
    const f = document.getElementById('filtroEspecialidad');
    if (!f) return;
    const id = f.value;
    let lista = serviciosDisponibles;
    if (id) {
        lista = serviciosDisponibles.filter(s => s.id_especialidad == id);
        console.log('[Filtro] Especialidad seleccionada:', id, '- Servicios filtrados:', lista.length);
    } else {
        console.log('[Filtro] Mostrando todos los servicios:', lista.length);
    }
    currentPageServicios = 1; // Resetear paginación al filtrar
    renderizarServicios(lista);
}

function renderizarServicios(lista) {
    const c = document.getElementById('serviciosContainer');
    if (!c) return;
    
    console.log('[Render] Renderizando', lista.length, 'servicios');
    
    if (lista.length === 0) {
        c.innerHTML = '<p class="col-span-2 text-center text-gray-500 py-4">Sin servicios</p>';
        return;
    }
    
    // Calcular paginación
    const totalPages = Math.ceil(lista.length / serviciosPerPage);
    const startIndex = (currentPageServicios - 1) * serviciosPerPage;
    const endIndex = startIndex + serviciosPerPage;
    const serviciosPage = lista.slice(startIndex, endIndex);
    
    // Limpiar contenedor
    c.innerHTML = '';
    
    // Crear grid para servicios
    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 md:grid-cols-2 gap-4 mb-4';
    
    const colores = ['orange','red','blue','purple','indigo','pink','green'];
    serviciosPage.forEach((s, i) => {
        const color = colores[i % colores.length];
        const card = document.createElement('div');
        card.className = 'servicio-card border-2 border-gray-200 rounded-lg p-4 hover:border-orange-500 cursor-pointer transition-all';
        card.innerHTML = '<div class="flex items-center gap-3"><div class="w-12 h-12 bg-'+color+'-100 rounded-lg flex items-center justify-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div><div class="flex-1"><p class="font-semibold text-gray-800">'+s.nombre+'</p><p class="text-sm text-gray-500">'+(s.nombre_especialidad||'General')+'</p></div></div>';
        card.addEventListener('click', function() {
            document.querySelectorAll('.servicio-card').forEach(x => {
                x.classList.remove('border-orange-500','bg-orange-50');
                x.classList.add('border-gray-200');
            });
            this.classList.add('border-orange-500','bg-orange-50');
            formData.id_servicio = s.id_servicio;
            formData.servicio_nombre = s.nombre;
            console.log('[Paso1] Servicio seleccionado:', s.nombre, 'ID:', s.id_servicio);
            const b = document.getElementById('btnStep1Next');
            if (b) b.disabled = false;
        });
        grid.appendChild(card);
    });
    
    c.appendChild(grid);
    
    // Agregar controles de paginación si hay más de una página
    if (totalPages > 1) {
        const pagination = document.createElement('div');
        pagination.className = 'flex items-center justify-center gap-2 mt-4';
        
        // Botón anterior
        const btnPrev = document.createElement('button');
        btnPrev.type = 'button';
        btnPrev.className = 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed';
        btnPrev.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>';
        btnPrev.disabled = currentPageServicios === 1;
        btnPrev.addEventListener('click', () => {
            if (currentPageServicios > 1) {
                currentPageServicios--;
                renderizarServicios(lista);
            }
        });
        pagination.appendChild(btnPrev);
        
        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            const btnPage = document.createElement('button');
            btnPage.type = 'button';
            btnPage.textContent = i;
            btnPage.className = i === currentPageServicios 
                ? 'px-4 py-2 bg-orange-500 text-white rounded-lg font-semibold'
                : 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all';
            btnPage.addEventListener('click', () => {
                currentPageServicios = i;
                renderizarServicios(lista);
            });
            pagination.appendChild(btnPage);
        }
        
        // Botón siguiente
        const btnNext = document.createElement('button');
        btnNext.type = 'button';
        btnNext.className = 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed';
        btnNext.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>';
        btnNext.disabled = currentPageServicios === totalPages;
        btnNext.addEventListener('click', () => {
            if (currentPageServicios < totalPages) {
                currentPageServicios++;
                renderizarServicios(lista);
            }
        });
        pagination.appendChild(btnNext);
        
        c.appendChild(pagination);
        
        // Mostrar info de página
        const info = document.createElement('p');
        info.className = 'text-center text-sm text-gray-600 mt-2';
        info.textContent = `Mostrando ${startIndex + 1}-${Math.min(endIndex, lista.length)} de ${lista.length} servicios`;
        c.appendChild(info);
    }
}

async function cargarMedicos() {
    const l = document.getElementById('loadingMedicos');
    const c = document.getElementById('medicosContainer');
    const e = document.getElementById('errorMedicos');
    
    // Mostrar loading
    if (l) l.classList.remove('hidden');
    if (c) c.classList.add('hidden');
    if (e) e.classList.add('hidden');
    
    try {
        console.log('[Paso2] Cargando médicos para servicio ID:', formData.id_servicio);
        const url = '/reservas/api/medicos-por-servicio/'+formData.id_servicio;
        console.log('[Paso2] URL:', url);
        
        const r = await fetch(url);
        console.log('[Paso2] Response status:', r.status, r.statusText);
        
        if (!r.ok) {
            const errorText = await r.text();
            console.error('[Paso2] Error response:', errorText);
            throw new Error('Error del servidor ('+r.status+'): ' + errorText);
        }
        
        const d = await r.json();
        console.log('[Paso2] Datos recibidos completos:', d);
        
        // Verificar si hay médicos
        if (!d.medicos) {
            console.error('[Paso2] Respuesta sin campo medicos:', d);
            throw new Error('Respuesta inválida del servidor: falta campo medicos');
        }
        
        if (!Array.isArray(d.medicos)) {
            console.error('[Paso2] Campo medicos no es array:', typeof d.medicos);
            throw new Error('Formato de datos inválido: medicos debe ser un array');
        }
        
        medicosDisponibles = d.medicos;
        console.log('[Paso2] Total médicos:', medicosDisponibles.length);
        
        if (medicosDisponibles.length === 0) {
            console.warn('[Paso2] No hay médicos disponibles');
            if (e) {
                e.classList.remove('hidden');
                const errorText = e.querySelector('p');
                if (errorText) errorText.textContent = 'No hay médicos disponibles para este servicio. Por favor, contacta con la clínica.';
            }
            if (l) l.classList.add('hidden');
            return;
        }
        
        // Validar que cada médico tenga los campos necesarios
        const medicoInvalido = medicosDisponibles.find(m => !m.id_empleado || !m.nombre_completo);
        if (medicoInvalido) {
            console.error('[Paso2] Médico con datos incompletos:', medicoInvalido);
            throw new Error('Datos de médico incompletos');
        }
        
        currentPageMedicos = 1; // Resetear paginación
        renderizarMedicos(medicosDisponibles);
        if (l) l.classList.add('hidden');
        if (c) c.classList.remove('hidden');
        console.log('[Paso2] Médicos renderizados exitosamente');
        
    } catch (err) {
        console.error('[Paso2] Error cargando médicos:', err);
        console.error('[Paso2] Error stack:', err.stack);
        if (e) {
            e.classList.remove('hidden');
            const errorText = e.querySelector('p');
            if (errorText) {
                errorText.innerHTML = '<strong>Error al cargar médicos:</strong><br>' + err.message + '<br><small>Revisa la consola del servidor para más detalles.</small>';
            }
        }
        if (l) l.classList.add('hidden');
    }
}

function renderizarMedicos(lista) {
    const c = document.getElementById('medicosContainer');
    if (!c) return;
    
    console.log('[Paso2] Renderizando', lista.length, 'médicos');
    
    if (lista.length === 0) {
        c.innerHTML = '<p class="col-span-2 text-center text-gray-500 py-4">Sin médicos disponibles</p>';
        return;
    }
    
    // Calcular paginación
    const totalPages = Math.ceil(lista.length / medicosPerPage);
    const startIndex = (currentPageMedicos - 1) * medicosPerPage;
    const endIndex = startIndex + medicosPerPage;
    const medicosPage = lista.slice(startIndex, endIndex);
    
    // Limpiar contenedor
    c.innerHTML = '';
    
    // Crear grid para médicos
    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 md:grid-cols-2 gap-4 mb-4';
    
    medicosPage.forEach((m) => {
        const card = document.createElement('div');
        card.className = 'medico-card border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 cursor-pointer transition-all';
        card.innerHTML = '<div class="flex items-center gap-3"><div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div><div class="flex-1"><p class="font-semibold text-gray-800">Dr(a). '+m.nombre_completo+'</p><p class="text-sm text-gray-500">'+(m.especialidad||'Médico General')+'</p></div></div>';
        card.addEventListener('click', function() {
            document.querySelectorAll('.medico-card').forEach(x => {
                x.classList.remove('border-blue-500','bg-blue-50');
                x.classList.add('border-gray-200');
            });
            this.classList.add('border-blue-500','bg-blue-50');
            formData.id_empleado = m.id_empleado;
            formData.empleado_nombre = 'Dr(a). '+m.nombre_completo;
            console.log('[Paso2] Médico seleccionado:', m.nombre_completo, 'ID:', m.id_empleado);
            const b = document.getElementById('btnStep2Next');
            if (b) b.disabled = false;
        });
        grid.appendChild(card);
    });
    
    c.appendChild(grid);
    
    // Agregar controles de paginación si hay más de una página
    if (totalPages > 1) {
        const pagination = document.createElement('div');
        pagination.className = 'flex items-center justify-center gap-2 mt-4';
        
        // Botón anterior
        const btnPrev = document.createElement('button');
        btnPrev.type = 'button';
        btnPrev.className = 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed';
        btnPrev.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>';
        btnPrev.disabled = currentPageMedicos === 1;
        btnPrev.addEventListener('click', () => {
            if (currentPageMedicos > 1) {
                currentPageMedicos--;
                renderizarMedicos(lista);
            }
        });
        pagination.appendChild(btnPrev);
        
        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            const btnPage = document.createElement('button');
            btnPage.type = 'button';
            btnPage.textContent = i;
            btnPage.className = i === currentPageMedicos 
                ? 'px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold'
                : 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all';
            btnPage.addEventListener('click', () => {
                currentPageMedicos = i;
                renderizarMedicos(lista);
            });
            pagination.appendChild(btnPage);
        }
        
        // Botón siguiente
        const btnNext = document.createElement('button');
        btnNext.type = 'button';
        btnNext.className = 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed';
        btnNext.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>';
        btnNext.disabled = currentPageMedicos === totalPages;
        btnNext.addEventListener('click', () => {
            if (currentPageMedicos < totalPages) {
                currentPageMedicos++;
                renderizarMedicos(lista);
            }
        });
        pagination.appendChild(btnNext);
        
        c.appendChild(pagination);
        
        // Mostrar info de página
        const info = document.createElement('p');
        info.className = 'text-center text-sm text-gray-600 mt-2';
        info.textContent = `Mostrando ${startIndex + 1}-${Math.min(endIndex, lista.length)} de ${lista.length} médicos`;
        c.appendChild(info);
    }
}

async function cargarHorariosSemanales() {
    try {
        console.log('[Paso3] Cargando horarios para servicio ID:', formData.id_servicio, 'Médico ID:', formData.id_empleado);
        const hl = document.getElementById('horariosLoading');
        const hs = document.getElementById('horariosSemanales');
        const nh = document.getElementById('noHorarios');
        if (hl) hl.classList.remove('hidden');
        if (hs) hs.classList.add('hidden');
        if (nh) nh.classList.add('hidden');
        
        const url = '/reservas/api/buscar-horarios-disponibles?id_tipo_servicio=4&id_servicio='+formData.id_servicio+'&id_empleado='+formData.id_empleado;
        console.log('[Paso3] URL:', url);
        const r = await fetch(url);
        const d = await r.json();
        console.log('[Paso3] Respuesta horarios:', d);
        
        if (hl) hl.classList.add('hidden');
        if (d.horarios && d.horarios.length > 0) {
            console.log('[Paso3] Total horarios recibidos:', d.horarios.length);
            const porFecha = {};
            d.horarios.forEach(h => {
                if (!porFecha[h.fecha]) porFecha[h.fecha] = [];
                porFecha[h.fecha].push(h);
            });
            if (hs) {
                hs.innerHTML = '';
                Object.keys(porFecha).sort().forEach(f => {
                    const hd = porFecha[f];
                    const fo = new Date(f+'T00:00:00');
                    const ds = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'][fo.getDay()];
                    const ff = fo.toLocaleDateString('es-ES',{day:'2-digit',month:'long',year:'numeric'});
                    const dc = document.createElement('div');
                    dc.className = 'border rounded-lg p-4 bg-gray-50';
                    dc.innerHTML = '<h4 class="font-semibold text-gray-800 mb-3">'+ds+', '+ff+'</h4><div class="grid grid-cols-2 md:grid-cols-4 gap-2" data-fecha="'+f+'"></div>';
                    const grid = dc.querySelector('[data-fecha]');
                    hd.forEach(h => {
                        const disp = h.estado_programacion === 'Disponible';
                        const btn = document.createElement('button');
                        btn.type = 'button';
                        if (disp) {
                            btn.className = 'border-2 border-gray-300 bg-white rounded-lg p-2 text-sm hover:border-orange-500 hover:bg-orange-50 transition-all';
                            btn.onclick = () => seleccionarHorario(h.id_programacion,f,h.hora_inicio,h.hora_fin,ds,btn);
                        } else {
                            btn.className = 'border-2 border-gray-200 bg-gray-100 rounded-lg p-2 text-sm text-gray-400 cursor-not-allowed';
                            btn.disabled = true;
                        }
                        btn.innerHTML = '<div class="font-semibold">'+h.hora_inicio+' - '+h.hora_fin+'</div><div class="text-xs '+(disp?'text-green-600':'text-red-500')+'">'+(disp?'✓ Disponible':'✗ Ocupado')+'</div>';
                        grid.appendChild(btn);
                    });
                    hs.appendChild(dc);
                });
                hs.classList.remove('hidden');
                console.log('[Paso3] Horarios renderizados correctamente');
            }
        } else {
            console.log('[Paso3] No hay horarios disponibles');
            if (nh) nh.classList.remove('hidden');
        }
    } catch (e) {
        console.error('[Paso3] Error:', e);
        const hl = document.getElementById('horariosLoading');
        const nh = document.getElementById('noHorarios');
        if (hl) hl.classList.add('hidden');
        if (nh) nh.classList.remove('hidden');
    }
}

function seleccionarHorario(id,f,hi,hf,ds,el) {
    console.log('[Paso3] Horario seleccionado - ID:', id, 'Fecha:', f, 'Hora:', hi, '-', hf);
    document.querySelectorAll('#horariosSemanales button').forEach(b => {
        if (!b.disabled) {
            b.classList.remove('border-orange-500','bg-orange-50','ring-2','ring-orange-300');
            b.classList.add('border-gray-300','bg-white');
        }
    });
    el.classList.add('border-orange-500','bg-orange-50','ring-2','ring-orange-300');
    formData.id_programacion = id;
    formData.fecha = f;
    formData.hora_inicio = hi;
    formData.hora_fin = hf;
    formData.dia_semana = ds;
    const b = document.getElementById('btnStep3Next');
    if (b) b.disabled = false;
}

function goToStep(n) {
    ['step1','step2','step3','step4'].forEach(s => {
        const e = document.getElementById(s);
        if (e) e.classList.add('hidden');
    });
    const e = document.getElementById('step'+n);
    if (e) e.classList.remove('hidden');
    currentStep = n;
    updateStepIndicators(n);
    // Scroll deshabilitado para evitar reinicio del formulario
    // window.scrollTo({top:0,behavior:'smooth'});
}

function updateStepIndicators(n) {
    const ind = [
        {i:'step1-indicator',t:'step1-text',l:null},
        {i:'step2-indicator',t:'step2-text',l:'line1'},
        {i:'step3-indicator',t:'step3-text',l:'line2'},
        {i:'step4-indicator',t:'step4-text',l:'line3'}
    ];
    ind.forEach((x,idx) => {
        const i = document.getElementById(x.i);
        const t = document.getElementById(x.t);
        const l = x.l ? document.getElementById(x.l) : null;
        if (!i || !t) return;
        if (idx+1 < n) {
            i.className = 'step-indicator step-completed w-12 h-12 rounded-full flex items-center justify-center font-bold mb-2';
            t.className = 'text-sm font-medium text-green-600';
            if (l) l.className = 'flex-1 h-1 bg-green-500 mx-2';
        } else if (idx+1 === n) {
            i.className = 'step-indicator step-active w-12 h-12 rounded-full flex items-center justify-center font-bold mb-2';
            t.className = 'text-sm font-medium text-orange-600';
            if (l) l.className = 'flex-1 h-1 bg-gray-300 mx-2';
        } else {
            i.className = 'step-indicator step-inactive w-12 h-12 rounded-full flex items-center justify-center font-bold mb-2';
            t.className = 'text-sm font-medium text-gray-400';
            if (l) l.className = 'flex-1 h-1 bg-gray-300 mx-2';
        }
    });
}

function mostrarResumen() {
    const fo = new Date(formData.fecha+'T00:00:00');
    const ff = fo.toLocaleDateString('es-ES',{weekday:'long',year:'numeric',month:'long',day:'numeric'});
    const rt = document.getElementById('resumenTipo');
    const rm = document.getElementById('resumenMedico');
    const rf = document.getElementById('resumenFecha');
    const rh = document.getElementById('resumenHora');
    if (rt) rt.textContent = formData.servicio_nombre;
    if (rm) rm.textContent = formData.empleado_nombre;
    if (rf) rf.textContent = ff;
    if (rh) rh.textContent = formData.hora_inicio+' - '+formData.hora_fin;
}

async function confirmarExamen() {
    const b = document.getElementById('btnConfirmar');
    if (!b) return;
    console.log('[Confirmar] Datos a enviar:', formData);
    b.disabled = true;
    b.innerHTML = '<svg class="animate-spin inline mr-2" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="0.75"/></svg>Procesando...';
    try {
        const r = await fetch('/reservas/paciente/crear-reserva',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                id_programacion:formData.id_programacion,
                id_servicio:formData.id_servicio
            })
        });
        const d = await r.json();
        console.log('[Confirmar] Respuesta del servidor:', d);
        if (d.success) {
            alert('¡Examen agendado exitosamente!');
            window.location.href = '/reservas/paciente/historial';
        } else {
            alert('Error: '+(d.error||'Desconocido'));
            b.disabled = false;
            b.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="inline mr-2"><polyline points="20 6 9 17 4 12"/></svg>Confirmar Examen';
        }
    } catch (e) {
        console.error('[Confirmar] Error:', e);
        alert('Error: '+e.message);
        b.disabled = false;
        b.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="inline mr-2"><polyline points="20 6 9 17 4 12"/></svg>Confirmar Examen';
    }
}