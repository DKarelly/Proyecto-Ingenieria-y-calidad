document.addEventListener('DOMContentLoaded', () => {
    // IDs de modales
    const modales = ['modalRegistrarBloqueo', 'modalModificarHorario', 'modalEliminar'];

    // Cerrar modal con la X
    modales.forEach(id => {
        const modal = document.getElementById(id);
        if (!modal) return;
        const closeBtn = modal.querySelector('.close');
        closeBtn?.addEventListener('click', () => modal.classList.remove('show'));
    });

    // Cerrar modal al click fuera del contenido
    window.addEventListener('click', event => {
        modales.forEach(id => {
            const modal = document.getElementById(id);
            if (modal && event.target === modal) modal.classList.remove('show');
        });
    });

    // Abrir modal registrar
    document.getElementById('btnRegistrarBloqueo')?.addEventListener('click', () => {
        document.getElementById('modalRegistrarBloqueo')?.classList.add('show');
    });

    // Abrir modal editar
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('modalModificarHorario')?.classList.add('show');
        });
    });

    // Abrir modal eliminar
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('modalEliminar')?.classList.add('show');
        });
    });

    // Form registrar
    const formRegistrar = document.getElementById('formRegistrarBloqueo');
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', e => {
            e.preventDefault();
            document.getElementById('modalRegistrarBloqueo')?.classList.remove('show');
            alert('Bloqueo registrado exitosamente');
            // Aquí podrías enviar al backend con fetch() y luego refrescar la tabla
        });
        formRegistrar.querySelector('button[type="button"]')?.addEventListener('click', () => {
            document.getElementById('modalRegistrarBloqueo')?.classList.remove('show');
        });
    }

    // Form modificar
    const formModificar = document.getElementById('formModificarHorario');
    if (formModificar) {
        formModificar.addEventListener('submit', e => {
            e.preventDefault();
            document.getElementById('modalModificarHorario')?.classList.remove('show');
            alert('Bloqueo actualizado exitosamente');
            // Enviar al backend y refrescar la tabla
        });
        formModificar.querySelector('button[type="button"]')?.addEventListener('click', () => {
            document.getElementById('modalModificarHorario')?.classList.remove('show');
        });
    }

    // Modal eliminar
    document.getElementById('btnCancelarEliminar')?.addEventListener('click', () => {
        document.getElementById('modalEliminar')?.classList.remove('show');
    });
    document.getElementById('btnConfirmarEliminar')?.addEventListener('click', () => {
        document.getElementById('modalEliminar')?.classList.remove('show');
        alert('Bloqueo eliminado exitosamente');
        // Aquí llamarías al backend para eliminar y luego refrescar la tabla
    });

    // ----------------------------
    // BUSCAR: ahora BUSCAR PROGRAMACION por fecha
    // ----------------------------
    const btnBuscar = document.getElementById('btnBuscar');
    btnBuscar?.addEventListener('click', async () => {
        const fechaProgramacion = document.getElementById('filtroProgramacion')?.value;
        const fechaBloqueo = document.getElementById('filtroBloqueo')?.value;

        // Validación simple
        if (!fechaProgramacion && !fechaBloqueo) {
            console.log('Selecciona al menos una fecha para buscar (programación o bloqueo).');
            return;
        }

        console.log(`Buscando programaciones para la fecha de programación: ${fechaProgramacion || '—'} y fecha de bloqueo: ${fechaBloqueo || '—'}`);

        // ---- Método recomendado: pedir programaciones al backend ----
        // Endpoint de ejemplo que deberías implementar en el backend:
        // GET /api/programaciones?fecha=YYYY-MM-DD
        // El backend devolvería JSON con programaciones (y opcionalmente sus bloqueos).
        if (fechaProgramacion) {
            try {
                // Ejemplo de petición — ajusta la URL según tu backend
                const res = await fetch(`/api/programaciones?fecha=${encodeURIComponent(fechaProgramacion)}`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const programaciones = await res.json();

                // ---- Poblar la tabla de horarios / programaciones ----
                // Aquí asumimos que programaciones es un array de objetos:
                // { id_programacion, fecha, hora_inicio, hora_fin, id_horario, estado, ... }
                poblarTablaProgramaciones(programaciones);

                // Si quieres además filtrar bloqueos por fechaBloqueo, puedes llamar a otro endpoint o filtrar aquí.
                if (fechaBloqueo) {
                    // ejemplo: fetch(`/api/bloqueos?fecha=${fechaBloqueo}`)
                    // y luego poblar tabla de bloqueos
                }
                return;
            } catch (err) {
                console.warn('Fetch /api/programaciones falló: ', err);
                // fallback: continuar con lógica local (si existe)
            }
        }

        // ---- Fallback: filtro local en la tabla de bloqueos (si tienes datos ya cargados) ----
        // Esto filtra las filas de tablaBloqueos comparando la columna "Fecha" del bloqueo.
        if (fechaBloqueo) {
            filtrarTablaBloqueosPorFecha(fechaBloqueo);
        }
    });

    // ----------------------------------------------------------------
    // Helpers: poblar tablas y filtrar (uso: adaptar a la estructura de datos)
    // ----------------------------------------------------------------
    function poblarTablaProgramaciones(programaciones = []) {
        // ejemplo: llenar tbody#tablaHorarios con programaciones
        const tbody = document.getElementById('tablaHorarios');
        if (!tbody) return;
        tbody.innerHTML = ''; // limpiar

        programaciones.forEach(p => {
            // Ajusta campos según la respuesta real de tu API
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 transition-colors';
            tr.innerHTML = `
                <td class="px-6 py-4 text-sm text-gray-900 font-medium">${escapeHtml(p.id_programacion ?? '')}</td>
                <td class="px-6 py-4 text-sm text-gray-900">${escapeHtml(p.dia_texto ?? '')}</td>
                <td class="px-6 py-4 text-sm text-gray-600 font-mono">${escapeHtml(p.hora_inicio ?? '')}</td>
                <td class="px-6 py-4 text-sm text-gray-600 font-mono">${escapeHtml(p.hora_fin ?? '')}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function filtrarTablaBloqueosPorFecha(fecha) {
        const tbody = document.getElementById('tablaBloqueos');
        if (!tbody) return;
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.forEach(row => {
            // Asumimos que la columna Fecha está en la 3ª celda (index 2)
            const celdaFecha = row.cells[2];
            if (!celdaFecha) {
                row.style.display = 'none';
                return;
            }
            // Normalizar: desde "DD/MM/YYYY" a "YYYY-MM-DD" o comparar de forma flexible
            const textoFecha = celdaFecha.textContent.trim();
            // Si la fecha en la tabla está en formato DD/MM/YYYY convertimos:
            const parts = textoFecha.split('/');
            let rowDateIso = '';
            if (parts.length === 3) {
                // parts: [DD, MM, YYYY]
                rowDateIso = `${parts[2]}-${parts[1].padStart(2,'0')}-${parts[0].padStart(2,'0')}`;
            } else {
                // intentar usar directamente
                rowDateIso = textoFecha;
            }
            row.style.display = (rowDateIso === fecha) ? '' : 'none';
        });
    }

    // pequeño helper para evitar XSS si inyectas datos en la tabla
    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        return String(unsafe)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
