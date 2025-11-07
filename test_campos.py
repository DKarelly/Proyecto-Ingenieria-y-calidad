from models.reserva import Reserva
from datetime import timedelta

reservas = Reserva.obtener_por_paciente(2)
if reservas:
    r_dict = dict(reservas[0])
    print("Campos y tipos:")
    for key, val in r_dict.items():
        tipo = type(val).__name__
        if isinstance(val, timedelta):
            print(f"  {key}: {tipo} ⚠️ TIMEDELTA")
        elif tipo != 'NoneType':
            print(f"  {key}: {tipo}")
