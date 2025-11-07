from models.reserva import Reserva
import json

# Probar con el paciente 2
reservas = Reserva.obtener_por_paciente(2)
print(f'Encontradas {len(reservas)} reservas para paciente 2')

if reservas:
    print('\n=== Datos crudos de la primera reserva ===')
    r = reservas[0]
    print(f"Tipo: {type(r)}")
    print(f"Contenido: {dict(r) if hasattr(r, 'items') else r}")
    print(f"\nClaves disponibles: {list(r.keys()) if hasattr(r, 'keys') else 'N/A'}")
else:
    print("Sin reservas")
