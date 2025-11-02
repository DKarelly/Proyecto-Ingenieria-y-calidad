// Cargar fecha actual
document.addEventListener('DOMContentLoaded', function() {
    // Establecer fecha actual
    const fechaInput = document.getElementById('fechaReporte');
    const ahora = new Date();
    const opciones = {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };
    fechaInput.value = ahora.toLocaleDateString('es-ES', opciones);

    // Cargar pacientes
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

// Manejar envío del formulario
const form = document.getElementById('formIncidencia');
if (form) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // Mostrar modal de éxito
                document.getElementById('modalExito').classList.remove('hidden');
                document.getElementById('modalExito').classList.add('flex');

                // Limpiar formulario
                form.reset();
            } else {
                alert('Error al crear la incidencia. Por favor intente nuevamente.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al crear la incidencia. Por favor intente nuevamente.');
        }
    });
}
