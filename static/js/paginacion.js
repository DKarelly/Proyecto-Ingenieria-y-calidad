function inicializarPaginacion({ datos, registrosPorPagina = 10, renderFuncion }) {
    let paginaActual = 1;
    const totalRegistros = datos.length;
    const totalPaginas = Math.ceil(totalRegistros / registrosPorPagina);

    const inicioRango = document.getElementById("inicio-rango");
    const finRango = document.getElementById("fin-rango");
    const totalSpan = document.getElementById("total-registros");
    const contenedorPaginas = document.getElementById("paginacionNumeros");

    if (!inicioRango || !finRango || !totalSpan || !contenedorPaginas) {
        console.error("❌ Error: los elementos de paginación no existen en el HTML.");
        return;
    }

    totalSpan.textContent = totalRegistros;

    function mostrarPagina(pagina) {
        paginaActual = pagina;
        const inicio = (pagina - 1) * registrosPorPagina;
        const fin = inicio + registrosPorPagina;
        const datosPagina = datos.slice(inicio, fin);

        renderFuncion(datosPagina);
        inicioRango.textContent = totalRegistros === 0 ? 0 : inicio + 1;
        finRango.textContent = Math.min(fin, totalRegistros);

        renderizarBotones();
    }

    function renderizarBotones() {
        contenedorPaginas.innerHTML = "";
        const maxVisible = 6;
        let inicio = Math.max(1, paginaActual - 2);
        let fin = Math.min(totalPaginas, inicio + maxVisible - 1);

        if (fin - inicio < maxVisible - 1) inicio = Math.max(1, fin - maxVisible + 1);

        for (let i = inicio; i <= fin; i++) {
            const boton = document.createElement("button");
            boton.textContent = i;
            boton.className = `
                px-3 py-2 text-sm font-medium border border-gray-300 rounded-lg
                ${i === paginaActual ? "bg-cyan-600 text-white" : "bg-white text-gray-700 hover:bg-gray-100"}
                transition-colors
            `;
            boton.addEventListener("click", () => mostrarPagina(i));
            contenedorPaginas.appendChild(boton);
        }

        if (fin < totalPaginas) {
            const puntos = document.createElement("span");
            puntos.textContent = "...";
            puntos.className = "px-2 text-gray-500";
            contenedorPaginas.appendChild(puntos);

            const ultimo = document.createElement("button");
            ultimo.textContent = totalPaginas;
            ultimo.className =
                "px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors";
            ultimo.addEventListener("click", () => mostrarPagina(totalPaginas));
            contenedorPaginas.appendChild(ultimo);
        }
    }

    mostrarPagina(1);
}

// 🔹 Exportar globalmente para usarlo en cualquier HTML
window.inicializarPaginacion = inicializarPaginacion;