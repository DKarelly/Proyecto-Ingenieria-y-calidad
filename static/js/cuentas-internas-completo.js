/**
 * GESTIÓN COMPLETA DE CUENTAS INTERNAS
 * Incluye: Paginación, Validaciones
 * Versión limpia sin conflictos
 */

console.log('🔄 Iniciando sistema de gestión de cuentas internas...');

// ==================== VARIABLES GLOBALES ====================
let paginaActual = 1;
const registrosPorPagina = 10;
let empleadosGlobal = [];

let paginaActualPacientes = 1;
const registrosPorPaginaPacientes = 10;
let pacientesGlobal = [];



// ==================== PAGINACIÓN EMPLEADOS ====================
function poblarTablaEmpleados(empleados) {
    console.log(`📊 Poblando tabla empleados: ${empleados ? empleados.length : 0} registros`);
    
    const tbody = document.getElementById('tabla-empleados-body');
    if (!tbody) {
        console.error('❌ No se encontró tbody con ID: tabla-empleados-body');
        return;
    }
    
    tbody.innerHTML = '';
    empleadosGlobal = empleados || [];
    
    if (empleadosGlobal.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-12 text-center">
                    <div class="flex flex-col items-center justify-center text-gray-500">
                        <i class="fa-solid fa-users text-4xl mb-3 text-gray-300"></i>
                        <p class="text-lg font-medium">No se encontraron empleados</p>
                    </div>
                </td>
            </tr>
        `;
        actualizarPaginacionEmpleados(0);
        return;
    }

    // Calcular registros para la página actual
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, empleadosGlobal.length);
    const empleadosPagina = empleadosGlobal.slice(inicio, fin);

    console.log(`📄 Página ${paginaActual}: Mostrando empleados ${inicio + 1} a ${fin} de ${empleadosGlobal.length}`);
    console.log(`🔎 DEBUG: Iniciando debug detallado...`);
    console.log(`🔎 empleadosGlobal:`, empleadosGlobal);
    console.log(`🔎 paginaActual:`, paginaActual);
    console.log(`🔎 registrosPorPagina:`, registrosPorPagina);
    console.log(`🔎 inicio:`, inicio, 'fin:', fin);
    console.log(`🔎 Intentando slice...`);
    console.log(`🎯 Empleados a renderizar:`, empleadosPagina.length);
    console.log(`🔍 Primer empleado:`, empleadosPagina[0]);
    console.log(`🔍 Tbody encontrado:`, tbody);

    // Renderizar filas con try-catch
    try {
        console.log(`🚀 Iniciando forEach con ${empleadosPagina.length} empleados...`);
        empleadosPagina.forEach((empleado, index) => {
            console.log(`🔨 Creando fila ${index + 1} para empleado: ${empleado.nombres} ${empleado.apellidos} (ID: ${empleado.id_empleado})`);
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-slate-50 transition-colors';
            
            // HTML COMPLETO restaurado
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                        <div class="h-10 w-10 rounded-full bg-cyan-100 flex items-center justify-center">
                            <span class="text-cyan-600 font-bold">${empleado.nombres[0]}${empleado.apellidos[0]}</span>
                        </div>
                        <span class="text-sm font-semibold text-slate-900">${empleado.nombres} ${empleado.apellidos}</span>
                    </div>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600">
                    <div class="flex items-center gap-2">
                        <span class="text-slate-400">✉️</span>
                        ${empleado.correo}
                    </div>
                </td>
                <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ${empleado.rol || 'Sin rol'}
                    </span>
                </td>
                <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Activo
                    </span>
                </td>
                <td class="px-6 py-4 text-center">
                    <div class="flex items-center justify-center gap-2">
                        <a href="/cuentas/editar-empleado/${empleado.id_empleado}" 
                           class="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-100 text-blue-600 hover:bg-blue-600 hover:text-white transition-all text-xs font-semibold"
                           title="Editar empleado">
                            <span class="material-symbols-outlined text-base">edit</span>
                            Editar
                        </a>
                        <button onclick="eliminarEmpleado(${empleado.id_empleado}, '${empleado.nombres} ${empleado.apellidos}')" 
                                class="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-100 text-red-600 hover:bg-red-600 hover:text-white transition-all text-xs font-semibold"
                                title="Eliminar empleado">
                            <span class="material-symbols-outlined text-base">delete</span>
                            Eliminar
                        </button>
                    </div>
                </td>
            `;
            
            console.log(`✅ HTML generado para empleado ${empleado.id_empleado}:`, tr.innerHTML.length, 'caracteres');
            tbody.appendChild(tr);
        });
        console.log(`🎉 forEach completado exitosamente`);
    } catch (error) {
        console.error(`❌ ERROR en forEach:`, error);
    }

    console.log(`🏁 Llamando a actualizarPaginacionEmpleados...`);
    actualizarPaginacionEmpleados(empleadosGlobal.length);
    console.log(`✅ poblarTablaEmpleados terminó exitosamente`);
}

function actualizarPaginacionEmpleados(totalRegistros) {
    console.log(`🔢 Actualizando paginación empleados: ${totalRegistros} registros`);
    
    const paginacionContainer = document.getElementById('paginacionNumeros');
    const inicioRango = document.getElementById('inicio-rango');
    const finRango = document.getElementById('fin-rango');
    const totalRegistrosSpan = document.getElementById('total-registros');

    if (!paginacionContainer || !inicioRango || !finRango || !totalRegistrosSpan) {
        console.error('❌ No se encontraron elementos de paginación para empleados');
        return;
    }

    const totalPaginas = Math.ceil(totalRegistros / registrosPorPagina);
    paginacionContainer.innerHTML = '';

    // Actualizar texto de rango
    const inicio = totalRegistros === 0 ? 0 : (paginaActual - 1) * registrosPorPagina + 1;
    const fin = Math.min(paginaActual * registrosPorPagina, totalRegistros);
    inicioRango.textContent = inicio;
    finRango.textContent = fin;
    totalRegistrosSpan.textContent = totalRegistros;

    console.log(`📊 Rango: ${inicio}-${fin} de ${totalRegistros} | Páginas: ${totalPaginas}`);

    if (totalPaginas <= 1) return;

    // Crear botones de página (máximo 6 visibles)
    const maxVisible = 6;
    let inicioPagina = Math.max(1, paginaActual - 2);
    let finPagina = Math.min(totalPaginas, inicioPagina + maxVisible - 1);

    if (finPagina - inicioPagina < maxVisible - 1) {
        inicioPagina = Math.max(1, finPagina - maxVisible + 1);
    }

    for (let i = inicioPagina; i <= finPagina; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === paginaActual
                ? 'bg-cyan-600 text-white border-cyan-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', () => {
            console.log(`🔄 Cambiando a página ${i}`);
            paginaActual = i;
            poblarTablaEmpleados(empleadosGlobal);
        });
        paginacionContainer.appendChild(btn);
    }

    // Agregar "..." si hay más páginas
    if (finPagina < totalPaginas) {
        const span = document.createElement('span');
        span.className = 'px-2 text-gray-500';
        span.textContent = '...';
        paginacionContainer.appendChild(span);

        const ultimoBtn = document.createElement('button');
        ultimoBtn.textContent = totalPaginas;
        ultimoBtn.className = 'px-3 py-2 text-sm font-medium border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-100';
        ultimoBtn.addEventListener('click', () => {
            console.log(`🔄 Saltando a última página ${totalPaginas}`);
            paginaActual = totalPaginas;
            poblarTablaEmpleados(empleadosGlobal);
        });
        paginacionContainer.appendChild(ultimoBtn);
    }
}

// ==================== PAGINACIÓN PACIENTES ====================
function poblarTablaPacientes(pacientes) {
    console.log(`🏥 Poblando tabla pacientes: ${pacientes ? pacientes.length : 0} registros`);
    
    const tbody = document.getElementById('tabla-pacientes-body');
    if (!tbody) {
        console.log('ℹ️ No se encontró tabla de pacientes, omitiendo...');
        return;
    }
    
    tbody.innerHTML = '';
    pacientesGlobal = pacientes || [];
    
    if (pacientesGlobal.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-12 text-center">
                    <div class="flex flex-col items-center justify-center text-gray-500">
                        <i class="fa-solid fa-user-injured text-4xl mb-3 text-gray-300"></i>
                        <p class="text-lg font-medium">No se encontraron pacientes</p>
                    </div>
                </td>
            </tr>
        `;
        actualizarPaginacionPacientes(0);
        return;
    }

    // Calcular registros para la página actual
    const inicio = (paginaActualPacientes - 1) * registrosPorPaginaPacientes;
    const fin = Math.min(inicio + registrosPorPaginaPacientes, pacientesGlobal.length);
    const pacientesPagina = pacientesGlobal.slice(inicio, fin);

    console.log(`📄 Página ${paginaActualPacientes}: Mostrando pacientes ${inicio + 1} a ${fin} de ${pacientesGlobal.length}`);

    // Renderizar filas
    pacientesPagina.forEach(paciente => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 transition-colors';
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                    <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <i class="fa-solid fa-user-injured text-blue-600"></i>
                    </div>
                    <span class="text-sm font-semibold text-slate-900">${paciente.nombres} ${paciente.apellidos}</span>
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
                <i class="fa-solid fa-envelope text-slate-400 mr-2"></i>
                ${paciente.correo || 'N/A'}
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
                <i class="fa-solid fa-phone text-slate-400 mr-2"></i>
                ${paciente.telefono || 'N/A'}
            </td>
            <td class="px-6 py-4">
                <span class="admin-badge success inline-flex items-center">
                    <i class="fa-solid fa-circle-check mr-1.5"></i>
                    Activo
                </span>
            </td>
            <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center gap-2">
                    <button onclick="verPerfilPaciente(${paciente.id_paciente}, '${paciente.nombres}', '${paciente.apellidos}', '${paciente.documento_identidad}', '${paciente.correo}', '${paciente.telefono}', '${paciente.fecha_nacimiento}', 'Activo')" 
                       class="inline-flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-lg bg-purple-100 text-purple-600 hover:bg-purple-600 hover:text-white transition-all text-xs font-semibold"
                       title="Ver perfil del paciente">
                        <span class="material-symbols-outlined text-base">visibility</span>
                        Perfil
                    </button>
                    <a href="/cuentas/editar-paciente/${paciente.id_paciente}" 
                       class="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-100 text-blue-600 hover:bg-blue-600 hover:text-white transition-all text-xs font-semibold"
                       title="Editar paciente">
                        <span class="material-symbols-outlined text-base">edit</span>
                        Editar
                    </a>
                    <button onclick="eliminarPaciente(${paciente.id_paciente}, '${paciente.nombres} ${paciente.apellidos}')" 
                            class="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-100 text-red-600 hover:bg-red-600 hover:text-white transition-all text-xs font-semibold"
                            title="Eliminar paciente">
                        <span class="material-symbols-outlined text-base">delete</span>
                        Eliminar
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });

    actualizarPaginacionPacientes(pacientesGlobal.length);
}

function actualizarPaginacionPacientes(totalRegistros) {
    console.log(`🔢 Actualizando paginación pacientes: ${totalRegistros} registros`);
    
    const paginacionContainer = document.getElementById('paginacionNumeros-pacientes');
    const inicioRango = document.getElementById('inicio-rango-pacientes');
    const finRango = document.getElementById('fin-rango-pacientes');
    const totalRegistrosSpan = document.getElementById('total-registros-pacientes');

    if (!paginacionContainer || !inicioRango || !finRango || !totalRegistrosSpan) {
        console.error('❌ No se encontraron elementos de paginación para pacientes');
        return;
    }

    const totalPaginas = Math.ceil(totalRegistros / registrosPorPaginaPacientes);
    paginacionContainer.innerHTML = '';

    // Actualizar texto de rango
    const inicio = totalRegistros === 0 ? 0 : (paginaActualPacientes - 1) * registrosPorPaginaPacientes + 1;
    const fin = Math.min(paginaActualPacientes * registrosPorPaginaPacientes, totalRegistros);
    inicioRango.textContent = inicio;
    finRango.textContent = fin;
    totalRegistrosSpan.textContent = totalRegistros;

    console.log(`📊 Rango: ${inicio}-${fin} de ${totalRegistros} | Páginas: ${totalPaginas}`);

    if (totalPaginas <= 1) return;

    // Crear botones de página (máximo 6 visibles)
    const maxVisible = 6;
    let inicioPagina = Math.max(1, paginaActualPacientes - 2);
    let finPagina = Math.min(totalPaginas, inicioPagina + maxVisible - 1);

    if (finPagina - inicioPagina < maxVisible - 1) {
        inicioPagina = Math.max(1, finPagina - maxVisible + 1);
    }

    // Botón "Primera página" (si no estamos en la primera)
    if (paginaActualPacientes > 1) {
        paginacionContainer.appendChild(crearBotonPaginacionPacientes('primera', '«', () => {
            paginaActualPacientes = 1;
            poblarTablaPacientes(pacientesGlobal);
        }));
    }

    // Botones numéricos
    for (let i = inicioPagina; i <= finPagina; i++) {
        const esActual = i === paginaActualPacientes;
        paginacionContainer.appendChild(crearBotonPaginacionPacientes(
            esActual ? 'activo' : 'normal',
            i,
            () => {
                paginaActualPacientes = i;
                poblarTablaPacientes(pacientesGlobal);
            }
        ));
    }

    // Botón "Última página" (si no estamos en la última)
    if (paginaActualPacientes < totalPaginas) {
        paginacionContainer.appendChild(crearBotonPaginacionPacientes('ultima', '»', () => {
            paginaActualPacientes = totalPaginas;
            poblarTablaPacientes(pacientesGlobal);
        }));
    }
}

// Función auxiliar para crear botones de paginación de pacientes
function crearBotonPaginacionPacientes(tipo, texto, onClick) {
    const btn = document.createElement('button');
    btn.textContent = texto;

    const baseClasses = 'px-3 py-2 text-sm font-medium border rounded-lg transition-colors';
    const tipoClasses = {
        'activo': 'bg-cyan-600 text-white border-cyan-600 cursor-default',
        'normal': 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100',
        'primera': 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100',
        'ultima': 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
    };

    btn.className = `${baseClasses} ${tipoClasses[tipo] || tipoClasses['normal']}`;

    if (tipo !== 'activo') {
        btn.addEventListener('click', onClick);
    }

    return btn;
}

// ==================== CARGA DE DATOS ====================
async function cargarEmpleados() {
    try {
        console.log('🔄 Cargando empleados desde API...');
        const response = await fetch('/cuentas/api/empleados');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const empleados = await response.json();
        console.log(`✅ Empleados cargados exitosamente: ${empleados.length} registros`);
        
        poblarTablaEmpleados(empleados);
    } catch (error) {
        console.error('❌ Error al cargar empleados:', error);
        
        // Mostrar mensaje de error en la tabla
        const tbody = document.getElementById('tabla-empleados-body');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-12 text-center">
                        <div class="flex flex-col items-center justify-center text-red-500">
                            <i class="fa-solid fa-exclamation-triangle text-4xl mb-3"></i>
                            <p class="text-lg font-medium">Error al cargar empleados</p>
                            <p class="text-sm mt-1">${error.message}</p>
                        </div>
                    </td>
                </tr>
            `;
        }
    }
}

async function cargarPacientes() {
    try {
        console.log('🔄 Cargando pacientes desde API...');
        const response = await fetch('/cuentas/api/pacientes');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const pacientes = await response.json();
        console.log(`✅ Pacientes cargados exitosamente: ${pacientes.length} registros`);
        
        poblarTablaPacientes(pacientes);
    } catch (error) {
        console.error('❌ Error al cargar pacientes:', error);
    }
}

// ==================== FUNCIONES AUXILIARES ====================
function eliminarEmpleado(idEmpleado, nombreCompleto) {
    if (!confirm(`¿Está seguro de eliminar al empleado ${nombreCompleto}?\n\nEsta acción desactivará la cuenta del empleado.`)) {
        return;
    }
    window.location.href = `/cuentas/eliminar-empleado/${idEmpleado}?tab=empleados`;
}

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM cargado - Inicializando sistema de gestión de cuentas internas...');

    // Leer datos desde las variables globales en el HTML
    console.log('📊 Leyendo datos de empleados y pacientes...');
    
    if (typeof datosEmpleados !== 'undefined' && datosEmpleados) {
        console.log(`✅ Empleados encontrados: ${datosEmpleados.length} registros`);
        poblarTablaEmpleados(datosEmpleados);
    } else {
        console.log('🔄 Intentando cargar desde data-container...');
        const dataContainer = document.getElementById('data-container');
        if (dataContainer) {
            try {
                const empleadosData = JSON.parse(dataContainer.getAttribute('data-empleados') || '[]');
                const pacientesData = JSON.parse(dataContainer.getAttribute('data-pacientes') || '[]');
                console.log(`✅ Datos parseados - Empleados: ${empleadosData.length}, Pacientes: ${pacientesData.length}`);
                poblarTablaEmpleados(empleadosData);
                poblarTablaPacientes(pacientesData);
            } catch (error) {
                console.error('❌ Error al parsear datos del data-container:', error);
                cargarEmpleados();
                cargarPacientes();
            }
        } else {
            console.log('⚠️ No se encontró data-container, usando API...');
            cargarEmpleados();
            cargarPacientes();
        }
    }
    
    if (typeof datosPacientes !== 'undefined' && datosPacientes) {
        console.log(`✅ Pacientes encontrados: ${datosPacientes.length} registros`);
        poblarTablaPacientes(datosPacientes);
    }

    console.log('✅ Sistema inicializado correctamente');
});

console.log('📝 Script de gestión de cuentas internas cargado exitosamente');