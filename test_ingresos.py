import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.farmacia import Medicamento

# Test obtener_ingresos_recientes
print("Testing obtener_ingresos_recientes...")
ingresos = Medicamento.obtener_ingresos_recientes()
print(f"Number of recent entries: {len(ingresos)}")
for ingreso in ingresos:
    print(f"ID: {ingreso['id_medicamento']}, Nombre: {ingreso['nombre']}, Fecha: {ingreso['fecha_ingreso']}")

# Test all medications to check dates
print("\nTesting all medications...")
todos = Medicamento.listar()
print(f"Total medications: {len(todos)}")
for med in todos:
    print(f"ID: {med['id_medicamento']}, Nombre: {med['nombre']}, Fecha Registro: {med['fecha_registro']}")
