#!/usr/bin/env python3
"""
Script para verificar las incidencias en la base de datos
"""

from bd import obtener_conexion

def obtener_incidencias():
    """
    Obtiene todas las incidencias con información del paciente
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                i.id_incidencia,
                i.descripcion,
                i.categoria,
                i.prioridad,
                i.estado,
                i.fecha_registro,
                i.id_paciente,
                p.nombres,
                p.apellidos,
                p.documento_identidad as dni
            FROM INCIDENCIA i
            LEFT JOIN PACIENTE p ON i.id_paciente = p.id_paciente
            ORDER BY i.fecha_registro DESC
        """)

        incidencias = cursor.fetchall()

        # Formatear los datos para incluir nombre completo del paciente
        for incidencia in incidencias:
            if incidencia['nombres'] and incidencia['apellidos']:
                incidencia['paciente'] = f"{incidencia['nombres']} {incidencia['apellidos']}"
            else:
                incidencia['paciente'] = 'No asignado'

        return incidencias

    except Exception as e:
        print(f"Error al obtener incidencias: {e}")
        return []
    finally:
        if conexion:
            conexion.close()

if __name__ == "__main__":
    print("Verificando incidencias en la base de datos...")
    incidencias = obtener_incidencias()

    print(f"Total de incidencias encontradas: {len(incidencias)}")

    if incidencias:
        print("\nPrimeras 5 incidencias:")
        for i, inc in enumerate(incidencias[:5]):
            print(f"{i+1}. ID: {inc['id_incidencia']}, Paciente: {inc['paciente']}, Estado: {inc['estado']}")
    else:
        print("No se encontraron incidencias.")
