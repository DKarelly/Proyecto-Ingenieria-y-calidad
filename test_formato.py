from models.reserva import Reserva
import json
from datetime import datetime, timedelta, date

# Probar con el paciente 2
reservas = Reserva.obtener_por_paciente(2)

if reservas:
    r = reservas[0]
    print(f"Estado: '{r['estado']}'")
    print(f"Estado lowercase: '{(r['estado'] or '').lower()}'")
    print(f"¿Es Pendiente? {(r['estado'] or '').lower() == 'pendiente'}")
    
    # Convertir tiempos
    hora_inicio = r['hora_inicio']
    hora_fin = r['hora_fin']
    
    if isinstance(hora_inicio, timedelta):
        total_seconds = int(hora_inicio.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        hora_inicio_str = f"{hours:02d}:{minutes:02d}"
    else:
        hora_inicio_str = str(hora_inicio)
    
    print(f"\nHora inicio (raw): {r['hora_inicio']}")
    print(f"Hora inicio (str): {hora_inicio_str}")
