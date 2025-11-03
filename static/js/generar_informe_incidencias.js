// Cargar pacientes al iniciar
document.addEventListener('DOMContentLoaded', function() {
    cargarPacientes();
});

// Cargar lista de pacientes
async function cargarPacientes() {
    try {
        const response = await fetch('/seguridad/api/pacientes');
        if (response.ok) {
            const pacientes = await response.json();
            const selectPaciente = document.getElementById('paciente');

            pacientes.forEach(paciente => {
                const option = document.createElement('option');
                option.value = paciente.id_paciente;
                option.textContent = paciente.nombre_completo;
                selectPaciente.appendChild(option);
            });
        } else {
            console.error('Error al cargar pacientes');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Generar reporte
document.getElementById('btnGenerarReporte').addEventListener('click', async function() {
    const filtros = {
        paciente: document.getElementById('paciente').value,
        fecha: document.getElementById('fecha').value,
        categoria: document.getElementById('categoria').value,
        estado: document.getElementById('estado').value
    };

    try {
        const response = await fetch('/seguridad/api/incidencias/informe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filtros)
        });

        if (response.ok) {
            const incidencias = await response.json();
            mostrarResultados(incidencias);

            // Mostrar sección de resultados
            const resultsSection = document.getElementById('resultsSection');
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });

            // Actualizar contador
            document.getElementById('totalIncidencias').textContent = `${incidencias.length} incidencias`;
            document.getElementById('totalResultados').textContent = incidencias.length;
        } else {
            alert('Error al generar el informe');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar el informe');
    }
});

// Mostrar resultados en la tabla
function mostrarResultados(incidencias) {
    const tbody = document.getElementById('tablaIncidencias');
    tbody.innerHTML = '';

    if (incidencias.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-4 text-center text-gray-500">
                    No se encontraron incidencias con los filtros especificados
                </td>
            </tr>
        `;
        return;
    }

    incidencias.forEach(incidencia => {
        const estadoClass = incidencia.estado ? incidencia.estado.toLowerCase().replace(' ', '-') : 'pendiente';
        const categoria = incidencia.categoria || 'Sin categoría';
        const prioridad = incidencia.prioridad || 'Media';

        let estadoBadge = '';
        switch(incidencia.estado) {
            case 'Abierta':
                estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Abierta</span>';
                break;
            case 'En Progreso':
            case 'En proceso':
                estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">En Progreso</span>';
                break;
            case 'Resuelta':
                estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Resuelta</span>';
                break;
            case 'Cerrada':
                estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">Cerrada</span>';
                break;
            default:
                estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Pendiente</span>';
        }

        let prioridadBadge = '';
        switch(prioridad) {
            case 'Alta':
                prioridadBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">🔴 Alta</span>';
                break;
            case 'Media':
                prioridadBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-orange-100 text-orange-800">🟡 Media</span>';
                break;
            case 'Baja':
                prioridadBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">🟢 Baja</span>';
                break;
            default:
                prioridadBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-orange-100 text-orange-800">Media</span>';
        }

        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-all duration-200';
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-cyan-600">#${incidencia.id_incidencia}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${incidencia.fecha_registro}</td>
            <td class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title="${incidencia.descripcion}">${incidencia.descripcion}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${incidencia.paciente}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">${categoria}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">${prioridadBadge}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">${estadoBadge}</td>
            <td class="px-6 py-4 whitespace-nowrap text-center">
                <button onclick="verDetalle(${incidencia.id_incidencia})" class="text-cyan-600 hover:text-cyan-800 font-semibold">
                    <i class="fas fa-eye mr-1"></i>
                    Ver
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Ver detalle de incidencia
function verDetalle(id) {
    // Buscar la incidencia en los resultados actuales
    const tbody = document.getElementById('tablaIncidencias');
    const rows = tbody.querySelectorAll('tr');

    // Como no tenemos un array global, extraeremos la info del DOM
    fetch(`/seguridad/api/incidencias`)
        .then(response => response.json())
        .then(incidencias => {
            const incidencia = incidencias.find(inc => inc.id_incidencia == id);
            if (incidencia) {
                document.getElementById('detalle-id').textContent = `#${incidencia.id_incidencia}`;
                document.getElementById('detalle-fecha').textContent = incidencia.fecha_registro;
                document.getElementById('detalle-paciente').textContent = incidencia.paciente;
                document.getElementById('detalle-categoria').textContent = incidencia.categoria || 'Sin categoría';
                document.getElementById('detalle-descripcion').textContent = incidencia.descripcion;

                let estadoBadge = '';
                switch(incidencia.estado) {
                    case 'Abierta':
                        estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Abierta</span>';
                        break;
                    case 'En Progreso':
                        estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">En Progreso</span>';
                        break;
                    case 'Resuelta':
                        estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Resuelta</span>';
                        break;
                    default:
                        estadoBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Pendiente</span>';
                }
                document.getElementById('detalle-estado').innerHTML = estadoBadge;

                let prioridadBadge = '';
                const prioridad = incidencia.prioridad || 'Media';
                switch(prioridad) {
                    case 'Alta':
                        prioridadBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">🔴 Alta</span>';
                        break;
                    case 'Media':
                        prioridadBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-orange-100 text-orange-800">🟡 Media</span>';
                        break;
                    case 'Baja':
                        prioridadBadge = '<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">🟢 Baja</span>';
                        break;
                }
                document.getElementById('detalle-prioridad').innerHTML = prioridadBadge;

                document.getElementById('detalle-resolucion').textContent = incidencia.fecha_resolucion || 'Pendiente';
                document.getElementById('detalle-observaciones').textContent = incidencia.observaciones || 'Sin observaciones';

                // Mostrar modal
                document.getElementById('modalDetalle').classList.remove('hidden');
                document.getElementById('modalDetalle').classList.add('flex');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al obtener detalles de la incidencia');
        });
}

function cerrarModal() {
    document.getElementById('modalDetalle').classList.add('hidden');
    document.getElementById('modalDetalle').classList.remove('flex');
}
