// reporte-eficiencia.js - Reporte de Eficiencia Operativa

let chartDiaSemana, chartHorarios, chartFlujo, heatmapDemanda;
let timeoutBusqueda;

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Establecer fechas por defecto (último mes)
    const hoy = new Date();
    const hace30Dias = new Date();
    hace30Dias.setDate(hace30Dias.getDate() - 30);
    
    document.getElementById('fechaFin').valueAsDate = hoy;
    document.getElementById('fechaInicio').valueAsDate = hace30Dias;
    
    cargarEspecialidades();
    cargarReporte();
    
    // Agregar listeners para búsqueda dinámica
    document.getElementById('fechaInicio').addEventListener('change', busquedaDinamica);
    document.getElementById('fechaFin').addEventListener('change', busquedaDinamica);
    document.getElementById('especialidadFiltro').addEventListener('change', busquedaDinamica);
});

// Búsqueda dinámica con debounce
function busquedaDinamica() {
    clearTimeout(timeoutBusqueda);
    timeoutBusqueda = setTimeout(() => {
        cargarReporte();
    }, 500);
}

// Cargar especialidades para el filtro
async function cargarEspecialidades() {
    try {
        const response = await fetch('/reportes/api/especialidades');
        const data = await response.json();
        
        const select = document.getElementById('especialidadFiltro');
        data.especialidades.forEach(esp => {
            const option = document.createElement('option');
            option.value = esp.id_especialidad;
            option.textContent = esp.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar especialidades:', error);
    }
}

// Cargar datos del reporte
async function cargarReporte() {
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    const especialidad = document.getElementById('especialidadFiltro').value;

    if (!fechaInicio || !fechaFin) {
        return;
    }

    try {
        const response = await fetch('/reportes/api/eficiencia-operativa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fecha_inicio: fechaInicio,
                fecha_fin: fechaFin,
                id_especialidad: especialidad || null
            })
        });

        const data = await response.json();
        
        if (data.error) {
            console.error('Error en respuesta:', data.error);
            return;
        }

        // Actualizar KPIs
        actualizarKPIs(data.kpis);
        
        // Actualizar gráficos
        actualizarGraficosDemanda(data.demanda);
        actualizarGraficoFlujo(data.flujo);
        
        // Actualizar tabla de especialidades
        actualizarTablaEspecialidades(data.especialidades);

    } catch (error) {
        console.error('Error al cargar reporte:', error);
    }
}

// Actualizar KPIs
function actualizarKPIs(kpis) {
    document.getElementById('kpi-tiempo-espera').textContent = kpis.tiempo_promedio_espera.toFixed(1) + ' días';
    document.getElementById('kpi-reprogramacion').textContent = kpis.tasa_reprogramacion.toFixed(1) + '%';
    document.getElementById('kpi-cancelacion').textContent = kpis.tasa_cancelacion.toFixed(1) + '%';
    document.getElementById('kpi-resolucion').textContent = kpis.resolucion_primera_cita.toFixed(1) + '%';
}
// Actualizar gráficos de demanda
function actualizarGraficosDemanda(demanda) {
    // Gráfico por día de semana
    const diasSemana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    const ctx1 = document.getElementById('chartDiaSemana').getContext('2d');
    
    if (chartDiaSemana) chartDiaSemana.destroy();
    
    chartDiaSemana = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: diasSemana,
            datasets: [{
                label: 'Número de Reservas',
                data: demanda.por_dia,
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });

    // Gráfico por horario
    const ctx2 = document.getElementById('chartHorarios').getContext('2d');
    
    if (chartHorarios) chartHorarios.destroy();
    
    chartHorarios = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['08:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00'],
            datasets: [{
                data: demanda.por_horario,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(249, 115, 22, 0.7)',
                    'rgba(234, 179, 8, 0.7)',
                    'rgba(34, 197, 94, 0.7)',
                    'rgba(59, 130, 246, 0.7)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Heatmap simplificado (usando barras horizontales)
    const ctx3 = document.getElementById('heatmapDemanda').getContext('2d');
    
    if (heatmapDemanda) heatmapDemanda.destroy();
    
    heatmapDemanda = new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: diasSemana,
            datasets: [
                {
                    label: '08:00-10:00',
                    data: demanda.heatmap[0],
                    backgroundColor: 'rgba(239, 68, 68, 0.6)'
                },
                {
                    label: '10:00-12:00',
                    data: demanda.heatmap[1],
                    backgroundColor: 'rgba(249, 115, 22, 0.6)'
                },
                {
                    label: '12:00-14:00',
                    data: demanda.heatmap[2],
                    backgroundColor: 'rgba(234, 179, 8, 0.6)'
                },
                {
                    label: '14:00-16:00',
                    data: demanda.heatmap[3],
                    backgroundColor: 'rgba(34, 197, 94, 0.6)'
                },
                {
                    label: '16:00-18:00',
                    data: demanda.heatmap[4],
                    backgroundColor: 'rgba(59, 130, 246, 0.6)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Actualizar gráfico de flujo
function actualizarGraficoFlujo(flujo) {
    const ctx = document.getElementById('chartFlujo').getContext('2d');
    
    if (chartFlujo) chartFlujo.destroy();
    
    chartFlujo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Total Citas', 'Sin Procedimientos', 'Con Exámenes', 'Con Operaciones', 'Con Ambos'],
            datasets: [{
                label: 'Cantidad',
                data: [
                    flujo.total_citas,
                    flujo.sin_procedimientos,
                    flujo.con_examenes,
                    flujo.con_operaciones,
                    flujo.con_ambos
                ],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(34, 197, 94, 0.7)',
                    'rgba(168, 85, 247, 0.7)',
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(249, 115, 22, 0.7)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });

    // Actualizar estadísticas
    document.getElementById('stat-citas-completadas').textContent = flujo.total_citas;
    document.getElementById('stat-con-examenes').textContent = flujo.con_examenes + flujo.con_ambos;
    document.getElementById('stat-con-operaciones').textContent = flujo.con_operaciones + flujo.con_ambos;
}

// Actualizar tabla de especialidades
function actualizarTablaEspecialidades(especialidades) {
    const tbody = document.getElementById('tablaEspecialidades');
    
    if (!especialidades || especialidades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No hay datos disponibles</td></tr>';
        return;
    }

    tbody.innerHTML = especialidades.map(esp => {
        const exito = esp.total > 0 ? ((esp.completadas / esp.total) * 100).toFixed(1) : 0;
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 text-sm font-medium text-gray-800">${esp.nombre}</td>
                <td class="px-6 py-4 text-sm text-center text-gray-600">${esp.total}</td>
                <td class="px-6 py-4 text-sm text-center">
                    <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">${esp.completadas}</span>
                </td>
                <td class="px-6 py-4 text-sm text-center">
                    <span class="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">${esp.canceladas}</span>
                </td>
                <td class="px-6 py-4 text-sm text-center">
                    <div class="flex items-center justify-center gap-2">
                        <div class="w-16 bg-gray-200 rounded-full h-2">
                            <div class="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full" style="width: ${exito}%"></div>
                        </div>
                        <span class="font-semibold text-gray-700">${exito}%</span>
                    </div>
                </td>
                <td class="px-6 py-4 text-sm text-center font-semibold text-blue-600">${esp.tiempo_espera.toFixed(1)} días</td>
            </tr>
        `;
    }).join('');
}

// Exportar a PDF mejorado usando html2pdf.js
function exportarPDF() {
    const element = document.getElementById('reportContent');
    
    if (!element) {
        console.error('No se encontró el elemento #reportContent');
        return;
    }

    const fechaInicio = document.getElementById('fechaInicio').value || 'N/A';
    const fechaFin = document.getElementById('fechaFin').value || 'N/A';
    const filename = `reporte-eficiencia-operativa_${fechaInicio}_${fechaFin}.pdf`;

    const opt = {
        margin: [15, 10, 15, 10],
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
            scale: 2,
            useCORS: true,
            logging: false,
            letterRendering: true,
            allowTaint: true
        },
        jsPDF: { 
            unit: 'mm', 
            format: 'a4', 
            orientation: 'portrait',
            compress: true
        },
        pagebreak: { 
            mode: ['avoid-all', 'css', 'legacy'],
            before: '.page-break-before',
            after: '.page-break-after',
            avoid: ['img', 'tr', 'canvas']
        }
    };

    // Mostrar mensaje de carga
    const btnExportar = event.target || document.querySelector('button[onclick="exportarPDF()"]');
    const textoOriginal = btnExportar ? btnExportar.innerHTML : '';
    if (btnExportar) {
        btnExportar.disabled = true;
        btnExportar.innerHTML = '⏳ Generando PDF...';
    }

    html2pdf().set(opt).from(element).save().then(() => {
        if (btnExportar) {
            btnExportar.disabled = false;
            btnExportar.innerHTML = textoOriginal;
        }
    }).catch(error => {
        console.error('Error al generar PDF:', error);
        if (btnExportar) {
            btnExportar.disabled = false;
            btnExportar.innerHTML = textoOriginal;
        }
        alert('Error al generar el PDF. Por favor, intenta nuevamente.');
    });
}
