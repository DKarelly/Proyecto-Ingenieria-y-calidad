/**
 * Paginación para Gestión de Cuentas Internas
 * Maneja la paginación de tablas de empleados y pacientes
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar paginación para tabla de empleados
    const tableEmpleados = document.getElementById('tabla-empleados');
    const tableEmpleadosBody = tableEmpleados ? tableEmpleados.querySelector('tbody') : null;
    
    if (tableEmpleadosBody) {
        // Contar filas en la tabla de empleados (excluyendo el mensaje vacío)
        const filasEmpleados = Array.from(tableEmpleadosBody.querySelectorAll('tr')).filter(tr => {
            return !tr.querySelector('td[colspan]'); // Excluir mensaje "No hay empleados"
        });

        // Calcular paginación
        const totalEmpleados = filasEmpleados.length;
        const registrosPorPagina = 20;
        const totalPaginasEmpleados = Math.ceil(totalEmpleados / registrosPorPagina);

        // Actualizar información de paginación
        document.getElementById('total-registros-tabla-empleados').textContent = totalEmpleados;
        
        // Mostrar controles de paginación si hay múltiples páginas
        if (totalPaginasEmpleados > 1) {
            mostrarPaginacionEmpleados(filasEmpleados, registrosPorPagina, totalEmpleados);
        } else {
            // Una sola página - mostrar todos
            document.getElementById('inicio-rango-tabla-empleados').textContent = totalEmpleados > 0 ? 1 : 0;
            document.getElementById('fin-rango-tabla-empleados').textContent = totalEmpleados;
        }
    }

    // Inicializar paginación para tabla de pacientes
    const tablePacientes = document.querySelectorAll('table')[1]; // Segunda tabla
    const tablePacientesBody = tablePacientes ? tablePacientes.querySelector('tbody') : null;
    
    if (tablePacientesBody) {
        const filasPacientes = Array.from(tablePacientesBody.querySelectorAll('tr')).filter(tr => {
            return !tr.querySelector('td[colspan]'); // Excluir mensaje "No hay pacientes"
        });

        const totalPacientes = filasPacientes.length;
        const registrosPorPagina = 20;
        const totalPaginasPacientes = Math.ceil(totalPacientes / registrosPorPagina);

        // Actualizar información de paginación
        document.getElementById('total-registros-tabla-pacientes').textContent = totalPacientes;
        
        // Mostrar controles de paginación si hay múltiples páginas
        if (totalPaginasPacientes > 1) {
            mostrarPaginacionPacientes(filasPacientes, registrosPorPagina, totalPacientes);
        } else {
            // Una sola página - mostrar todos
            document.getElementById('inicio-rango-tabla-pacientes').textContent = totalPacientes > 0 ? 1 : 0;
            document.getElementById('fin-rango-tabla-pacientes').textContent = totalPacientes;
        }
    }
});

function mostrarPaginacionEmpleados(filas, registrosPorPagina, total) {
    const totalPaginas = Math.ceil(total / registrosPorPagina);
    const container = document.getElementById('paginacion-tabla-empleados');
    
    // Mostrar primera página por defecto
    mostrarPaginaEmpleados(1, filas, registrosPorPagina, total);
    
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
            mostrarPaginaEmpleados(i, filas, registrosPorPagina, total);
            
            // Actualizar estilos de botones
            document.querySelectorAll('#paginacion-tabla-empleados button').forEach(b => {
                b.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
                    b === btn
                        ? 'bg-cyan-600 text-white border-cyan-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
                }`;
            });
        });
        container.appendChild(btn);
    }
}

function mostrarPaginaEmpleados(pagina, filas, registrosPorPagina, total) {
    const inicio = (pagina - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, total);
    
    // Ocultar todas las filas
    filas.forEach((fila, index) => {
        fila.style.display = index >= inicio && index < fin ? 'table-row' : 'none';
    });
    
    // Actualizar información de rango
    document.getElementById('inicio-rango-tabla-empleados').textContent = total > 0 ? inicio + 1 : 0;
    document.getElementById('fin-rango-tabla-empleados').textContent = fin;
}

function mostrarPaginacionPacientes(filas, registrosPorPagina, total) {
    const totalPaginas = Math.ceil(total / registrosPorPagina);
    const container = document.getElementById('paginacion-tabla-pacientes');
    
    // Mostrar primera página por defecto
    mostrarPaginaPacientes(1, filas, registrosPorPagina, total);
    
    // Generar botones de página
    for (let i = 1; i <= totalPaginas; i++) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = i;
        btn.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
            i === 1
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        }`;
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            mostrarPaginaPacientes(i, filas, registrosPorPagina, total);
            
            // Actualizar estilos de botones
            document.querySelectorAll('#paginacion-tabla-pacientes button').forEach(b => {
                b.className = `px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
                    b === btn
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
                }`;
            });
        });
        container.appendChild(btn);
    }
}

function mostrarPaginaPacientes(pagina, filas, registrosPorPagina, total) {
    const inicio = (pagina - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, total);
    
    // Ocultar todas las filas
    filas.forEach((fila, index) => {
        fila.style.display = index >= inicio && index < fin ? 'table-row' : 'none';
    });
    
    // Actualizar información de rango
    document.getElementById('inicio-rango-tabla-pacientes').textContent = total > 0 ? inicio + 1 : 0;
    document.getElementById('fin-rango-tabla-pacientes').textContent = fin;
}
