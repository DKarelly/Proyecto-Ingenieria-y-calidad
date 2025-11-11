#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bd import obtener_conexion

conn = obtener_conexion()
c = conn.cursor()

c.execute('SELECT COUNT(*) as total FROM HORARIO WHERE fecha BETWEEN "2025-11-10" AND "2025-12-31"')
result = c.fetchone()
print(f'Total horarios insertados: {result["total"]}')

c.execute('SELECT COUNT(DISTINCT id_empleado) as medicos FROM HORARIO WHERE fecha BETWEEN "2025-11-10" AND "2025-12-31"')
result = c.fetchone()
print(f'Médicos con horarios: {result["medicos"]}')

c.execute('SELECT MIN(fecha) as fecha_min, MAX(fecha) as fecha_max FROM HORARIO WHERE fecha BETWEEN "2025-11-10" AND "2025-12-31"')
result = c.fetchone()
print(f'Rango de fechas: {result["fecha_min"]} a {result["fecha_max"]}')

c.execute('SELECT id_empleado, COUNT(*) as total FROM HORARIO WHERE fecha BETWEEN "2025-11-10" AND "2025-12-31" GROUP BY id_empleado LIMIT 5')
results = c.fetchall()
print(f'\nPrimeros 5 médicos (horarios por médico):')
for r in results:
    print(f'  Médico {r["id_empleado"]}: {r["total"]} horarios')

conn.close()
