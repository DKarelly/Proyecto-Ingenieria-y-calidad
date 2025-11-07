// Variables globales para los gráficos
let chartTopServicios, chartTipoServicio, chartExamenes, chartTendencia;
let timeoutBusqueda;

document.addEventListener('DOMContentLoaded', function() {
    // Configurar fechas por defecto (último mes)
    const hoy = new Date();
    const haceUnMes = new Date();
    haceUnMes.setMonth(haceUnMes.getMonth() - 1);
    
    document.getElementById('fechaFin').valueAsDate = hoy;
    document.getElementById('fechaInicio').valueAsDate = haceUnMes;
    
    // Cargar especialidades
    cargarEspecialidades();
    
    // Cargar reporte inicial
    cargarReporte();
    
    // Event listeners para búsqueda dinámica
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

// Cargar especialidades
async function cargarEspecialidades() {
    try {
        const response = await fetch('/reportes/api/demanda-preferencias/especialidades');
        const especialidades = await response.json();
        
        const select = document.getElementById('especialidadFiltro');
        especialidades.forEach(esp => {
            const option = document.createElement('option');
            option.value = esp.id_especialidad;
            option.textContent = esp.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar especialidades:', error);
    }
}

// Cargar reporte
async function cargarReporte() {
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    const idEspecialidad = document.getElementById('especialidadFiltro').value;
    
    if (!fechaInicio || !fechaFin) {
        return;
    }
    
    try {
        const response = await fetch('/reportes/api/demanda-preferencias', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fecha_inicio: fechaInicio,
                fecha_fin: fechaFin,
                id_especialidad: idEspecialidad || null
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
        actualizarGraficoTopServicios(data.top_servicios);
        actualizarGraficoTipoServicio(data.tipo_servicio);
        actualizarGraficoExamenes(data.examenes);
        actualizarGraficoTendencia(data.tendencia);
        
        // Actualizar tablas
        actualizarTablaTopMedicos(data.top_medicos);
        actualizarTablaDetalleServicios(data.top_servicios);

    } catch (error) {
        console.error('Error al cargar reporte:', error);
    }
}

// Actualizar KPIs
function actualizarKPIs(kpis) {
    document.getElementById('kpi-total-reservas').textContent = kpis.total_reservas.toLocaleString();
    document.getElementById('kpi-pacientes-unicos').textContent = kpis.pacientes_unicos.toLocaleString();
    document.getElementById('kpi-servicios-diferentes').textContent = kpis.servicios_diferentes.toLocaleString();
    document.getElementById('kpi-dias-anticipacion').textContent = kpis.dias_anticipacion.toFixed(1);
}

// Actualizar gráfico de Top Servicios
function actualizarGraficoTopServicios(servicios) {
    const ctx = document.getElementById('chartTopServicios').getContext('2d');
    
    if (chartTopServicios) chartTopServicios.destroy();
    
    const labels = servicios.map(s => s.servicio.length > 30 ? s.servicio.substring(0, 30) + '...' : s.servicio);
    const data = servicios.map(s => s.total_reservas);
    
    chartTopServicios = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Reservas',
                data: data,
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const servicio = servicios[index];
                            return [
                                `Reservas: ${servicio.total_reservas}`,
                                `Completadas: ${servicio.completadas}`,
                                `Éxito: ${servicio.tasa_exito}%`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// Actualizar gráfico de Tipo de Servicio
function actualizarGraficoTipoServicio(tipos) {
    const ctx = document.getElementById('chartTipoServicio').getContext('2d');
    
    if (chartTipoServicio) chartTipoServicio.destroy();
    
    const labels = tipos.map(t => t.tipo);
    const data = tipos.map(t => t.cantidad);
    
    chartTipoServicio = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(168, 85, 247, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 15, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = data.reduce((a, b) => a + b, 0);
                            const porcentaje = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${porcentaje}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Actualizar gráfico de Exámenes
function actualizarGraficoExamenes(examenes) {
    const ctx = document.getElementById('chartExamenes').getContext('2d');
    
    if (chartExamenes) chartExamenes.destroy();
    
    const labels = examenes.map(e => e.examen.length > 25 ? e.examen.substring(0, 25) + '...' : e.examen);
    const data = examenes.map(e => e.frecuencia);
    
    chartExamenes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Frecuencia',
                data: data,
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// Actualizar gráfico de Tendencia
function actualizarGraficoTendencia(tendencia) {
    const ctx = document.getElementById('chartTendencia').getContext('2d');
    
    if (chartTendencia) chartTendencia.destroy();
    
    const labels = tendencia.map(t => {
        const [year, month] = t.mes.split('-');
        const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
        return `${months[parseInt(month) - 1]} ${year}`;
    });
    const data = tendencia.map(t => t.total_reservas);
    
    chartTendencia = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Reservas',
                data: data,
                backgroundColor: 'rgba(168, 85, 247, 0.2)',
                borderColor: 'rgba(168, 85, 247, 1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(168, 85, 247, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// Actualizar tabla de Top Médicos
function actualizarTablaTopMedicos(medicos) {
    const tbody = document.getElementById('tablaTopMedicos');
    
    if (!medicos || medicos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-4 py-4 text-center text-gray-500">No hay datos disponibles</td></tr>';
        return;
    }
    
    tbody.innerHTML = medicos.map((med, index) => {
        let badge = '';
        if (index === 0) badge = '<span class="badge badge-gold">🥇 1°</span>';
        else if (index === 1) badge = '<span class="badge badge-silver">🥈 2°</span>';
        else if (index === 2) badge = '<span class="badge badge-bronze">🥉 3°</span>';
        else badge = `<span class="text-gray-600 font-semibold">${index + 1}°</span>`;
        
        const tasaExitoClass = med.tasa_exito >= 80 ? 'text-green-600' : med.tasa_exito >= 60 ? 'text-yellow-600' : 'text-red-600';
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-4 py-3 text-center">${badge}</td>
                <td class="px-4 py-3 font-medium text-gray-800">${med.medico}</td>
                <td class="px-4 py-3 text-gray-600">${med.especialidad}</td>
                <td class="px-4 py-3 text-center font-bold text-blue-600">${med.total_reservas}</td>
                <td class="px-4 py-3 text-center text-green-600">${med.completadas}</td>
                <td class="px-4 py-3 text-center ${tasaExitoClass} font-semibold">${med.tasa_exito}%</td>
                <td class="px-4 py-3 text-center text-gray-600">${med.demanda_anticipada} días</td>
            </tr>
        `;
    }).join('');
}

// Actualizar tabla de Detalle de Servicios
function actualizarTablaDetalleServicios(servicios) {
    const tbody = document.getElementById('tablaDetalleServicios');
    
    if (!servicios || servicios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="px-3 py-3 text-center text-gray-500">No hay datos disponibles</td></tr>';
        return;
    }
    
    tbody.innerHTML = servicios.map(srv => {
        const tasaExitoClass = srv.tasa_exito >= 80 ? 'text-green-600' : srv.tasa_exito >= 60 ? 'text-yellow-600' : 'text-red-600';
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-3 py-2 text-gray-800">${srv.servicio}</td>
                <td class="px-3 py-2 text-gray-600">${srv.especialidad}</td>
                <td class="px-3 py-2 text-center font-semibold text-blue-600">${srv.total_reservas}</td>
                <td class="px-3 py-2 text-center text-green-600">${srv.completadas}</td>
                <td class="px-3 py-2 text-center ${tasaExitoClass} font-semibold">${srv.tasa_exito}%</td>
            </tr>
        `;
    }).join('');
}

// Exportar a PDF mejorado
function exportarPDF() {
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    
    // Actualizar fecha en el encabezado del PDF
    const fechaReportePDF = document.getElementById('fecha-reporte-pdf');
    fechaReportePDF.textContent = `Período: ${formatearFecha(fechaInicio)} - ${formatearFecha(fechaFin)}`;
    
    const element = document.getElementById('reportContent');
    
    if (!element) {
        console.error('No se encontró el elemento #reportContent');
        return;
    }

    const filename = `reporte-demanda-preferencias_${fechaInicio}_${fechaFin}.pdf`;

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

// Función auxiliar para formatear fechas
function formatearFecha(fecha) {
    if (!fecha) return '';
    const [year, month, day] = fecha.split('-');
    return `${day}/${month}/${year}`;
}
