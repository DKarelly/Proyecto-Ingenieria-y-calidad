#!/usr/bin/env python3
"""
scripts/generar_horarios.py

Genera e inserta horarios de atención (tabla HORARIO) para todos los médicos.

Características:
- Obtiene la lista de médicos activos con especialidad (usa models.empleado.obtener_medicos()).
- Genera horarios por rango de fechas y días de la semana (por defecto lunes-viernes).
- Permite dry-run (por defecto) para revisar SQL/filas generadas.
- Opción --apply para ejecutar los INSERT en la base de datos.
- Evita duplicados comprobando combinaciones (id_empleado, fecha, hora_inicio) ya existentes.

Uso:
  python scripts/generar_horarios.py --start 2025-11-10 --end 2025-11-30
  python scripts/generar_horarios.py --start 2025-11-10 --end 2025-11-30 --apply
  python scripts/generar_horarios.py --start 2025-11-10 --end 2025-11-30 --medicos 1,2 --apply

Nota: ejecuta primero en modo dry-run (sin --apply) para revisar la salida.
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bd import obtener_conexion
from models.empleado import Empleado


def daterange(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += timedelta(days=1)


def fetch_medicos_by_ids(ids):
    """Devuelve lista de diccionarios de empleados por sus IDs"""
    if not ids:
        return []
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            q_marks = ','.join(['%s'] * len(ids))
            sql = f"SELECT * FROM EMPLEADO WHERE id_empleado IN ({q_marks}) AND estado = 'activo'"
            cursor.execute(sql, tuple(ids))
            return cursor.fetchall()
    finally:
        conexion.close()


def generate_and_insert(start, end, shifts, weekdays=(0,1,2,3,4), apply=False, medicos_ids=None):
    # Obtener médicos
    if medicos_ids:
        medicos = fetch_medicos_by_ids(medicos_ids)
    else:
        medicos = Empleado.obtener_medicos()

    if not medicos:
        print("No se encontraron médicos activos con especialidad.")
        return

    rows = []
    for m in medicos:
        id_empleado = m['id_empleado']
        for single in daterange(start, end):
            if single.weekday() in weekdays:
                for shift in shifts:
                    rows.append((id_empleado, single.strftime('%Y-%m-%d'), shift[0], shift[1], '1'))

    print(f"Generadas {len(rows)} filas para insertar (medicos={len(medicos)}, fechas={ (end-start).days + 1 }).")

    if not apply:
        print("--- Modo dry-run (usar --apply para ejecutar) ---")
        # Mostrar las primeras 12 declaraciones como ejemplo
        for r in rows[:12]:
            print("INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES (%s, '%s', '%s', '%s', %s);" % r)
        return

    # Ejecutar inserción evitando duplicados
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Obtener existentes en el rango para evitar duplicados
            cursor.execute("SELECT id_empleado, fecha, hora_inicio FROM HORARIO WHERE fecha BETWEEN %s AND %s", (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
            existente = set()
            for row in cursor.fetchall():
                fecha_val = row['fecha'] if isinstance(row['fecha'], str) else row['fecha'].strftime('%Y-%m-%d')
                hora_val = row['hora_inicio'] if isinstance(row['hora_inicio'], str) else row['hora_inicio'].strftime('%H:%M:%S')
                existente.add((row['id_empleado'], fecha_val, hora_val))

            insert_sql = "INSERT INTO HORARIO (id_empleado, fecha, hora_inicio, hora_fin, activo) VALUES (%s,%s,%s,%s,%s)"
            to_insert = [r for r in rows if (r[0], r[1], r[2]) not in existente]

            if not to_insert:
                print("No hay filas nuevas para insertar (todos los horarios ya existen en el rango).")
                return

            print(f"Insertando {len(to_insert)} filas en la tabla HORARIO...")
            # Insertar por lotes
            batch = 500
            for i in range(0, len(to_insert), batch):
                chunk = to_insert[i:i+batch]
                cursor.executemany(insert_sql, chunk)
            conexion.commit()
            print("Inserción completada.")
    except Exception as e:
        conexion.rollback()
        print("Error durante la inserción:", e)
    finally:
        conexion.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Generador masivo de horarios para médicos')
    parser.add_argument('--start', required=True, help='Fecha inicio YYYY-MM-DD')
    parser.add_argument('--end', required=True, help='Fecha fin YYYY-MM-DD')
    parser.add_argument('--apply', action='store_true', help='Ejecutar inserts en la BD (si no, dry-run)')
    parser.add_argument('--medicos', help='IDs de médicos separados por comas (ej: 1,2,3)')
    parser.add_argument('--weekdays', help='Días de la semana (0=Lun .. 6=Dom) separados por comas, por defecto 0-4', default='0,1,2,3,4')
    parser.add_argument('--shifts', help="Turnos en formato inicio-fin separados por ; (ej: '07:00:00-13:00:00;14:00:00-22:00:00')", default='07:00:00-13:00:00;14:00:00-22:00:00')
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        start = datetime.strptime(args.start, '%Y-%m-%d').date()
        end = datetime.strptime(args.end, '%Y-%m-%d').date()
    except ValueError:
        print('Formato de fecha inválido. Usa YYYY-MM-DD')
        return

    if end < start:
        print('La fecha fin debe ser igual o posterior a la fecha inicio')
        return

    weekdays = [int(x) for x in args.weekdays.split(',') if x.strip() != '']
    shifts = []
    for s in args.shifts.split(';'):
        if '-' in s:
            inicio, fin = s.split('-', 1)
            shifts.append((inicio.strip(), fin.strip()))

    medicos_ids = None
    if args.medicos:
        medicos_ids = [int(x) for x in args.medicos.split(',') if x.strip()]

    generate_and_insert(start, end, shifts, weekdays=weekdays, apply=args.apply, medicos_ids=medicos_ids)


if __name__ == '__main__':
    main()
