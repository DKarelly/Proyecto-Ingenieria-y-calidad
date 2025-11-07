from models.reserva import Reserva
import json

# Probar con el paciente 10 que vimos en la BD
reservas = Reserva.obtener_por_paciente(10)
print(f'\nEncontradas {len(reservas)} reservas para paciente 10')

if reservas:
    print('\n=== Estructura de datos ===')
    for r in reservas[:3]:
        print(f"\nReserva {r.get('id_reserva')}:")
        print(f"  - estado: {r.get('estado')} (tipo: {type(r.get('estado')).__name__})")
        print(f"  - fecha_cita: {r.get('fecha_cita')}")
        print(f"  - hora_inicio: {r.get('hora_inicio')}")
        print(f"  - hora_fin: {r.get('hora_fin')}")
        print(f"  - servicio: {r.get('servicio')}")
        print(f"  - nombre_empleado: {r.get('nombre_empleado')}")
        print(f"  - id_servicio: {r.get('id_servicio')}")
else:
    print("Sin reservas para este paciente")
