#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que las notificaciones de operación funcionan correctamente
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bd import obtener_conexion
# Importar solo la función que necesitamos, evitando problemas de codificación
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def buscar_medico_por_nombre(nombre_completo):
    """Busca un médico por su nombre completo"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Buscar médico por nombre
            nombre_parts = nombre_completo.split()
            if len(nombre_parts) >= 3:
                nombre = nombre_parts[0]
                apellido1 = nombre_parts[1]
                apellido2 = nombre_parts[2] if len(nombre_parts) > 2 else ""
                
                sql = """
                    SELECT e.id_empleado, 
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_completo,
                           e.id_usuario,
                           u.id_usuario,
                           u.correo
                    FROM EMPLEADO e
                    LEFT JOIN USUARIO u ON e.id_usuario = u.id_usuario
                    WHERE e.nombres LIKE %s 
                    AND (e.apellidos LIKE %s OR e.apellidos LIKE %s)
                """
                
                cursor.execute(sql, (
                    f"%{nombre}%",
                    f"%{apellido1}%",
                    f"%{apellido1} {apellido2}%"
                ))
                
                resultados = cursor.fetchall()
                return resultados
    except Exception as e:
        print(f"ERROR al buscar médico: {e}")
        return []
    finally:
        conexion.close()

def crear_notificacion_prueba_operacion(id_usuario, nombre_medico):
    """Crea una notificación de prueba para una operación derivada"""
    from datetime import datetime
    
    print(f"\n{'='*60}")
    print(f"CREANDO NOTIFICACION DE PRUEBA PARA OPERACION")
    print(f"{'='*60}\n")
    
    # Crear mensaje de notificación de prueba
    titulo = "Nueva Operación Derivada - PRUEBA"
    mensaje = f"""
    <div style="margin: 15px 0;">
        <p style="margin: 10px 0; font-size: 15px; color: #374151;">
            El Dr./Dra. <strong>Médico de Prueba</strong> le ha derivado una operación.
        </p>
        <div style="background-color: #f9fafb; border-left: 4px solid #ef4444; padding: 15px; margin: 15px 0; border-radius: 4px;">
            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>Operación:</strong> Cirugía de Prueba</p>
            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>Paciente:</strong> Paciente de Prueba</p>
            <p style="margin: 5px 0; color: #111827; font-size: 14px;"><strong>ID Autorización:</strong> 999 (PRUEBA)</p>
        </div>
        <p style="margin: 10px 0; font-size: 14px; color: #6b7280;">
            El paciente programará la operación cuando esté listo. Esté preparado para cuando reciba la solicitud de reserva.
        </p>
        <p style="margin: 10px 0; font-size: 12px; color: #9ca3af; font-style: italic;">
            Esta es una notificación de prueba generada automáticamente.
        </p>
    </div>
    """
    
    print(f"Informacion de la notificacion:")
    print(f"  - Titulo: {titulo}")
    print(f"  - Tipo: derivacion_operacion")
    print(f"  - ID Usuario destino: {id_usuario}")
    print(f"  - ID Reserva: None (sin reserva)")
    print(f"\nCreando notificacion...\n")
    
    # Crear la notificación directamente usando SQL para evitar problemas de importación
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            ahora = datetime.now()
            fecha_envio = ahora.date()
            hora_envio = ahora.time()
            
            # Insertar sin id_reserva (será NULL)
            sql = """INSERT INTO NOTIFICACION (titulo, mensaje, tipo, fecha_envio, 
                     hora_envio, id_paciente, id_usuario) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(sql, (titulo, mensaje, 'derivacion_operacion', fecha_envio, hora_envio, None, id_usuario))
            conexion.commit()
            id_notificacion = cursor.lastrowid
            
            resultado = {
                'success': True,
                'id_notificacion': id_notificacion
            }
    
    except Exception as e:
        conexion.rollback()
        print(f"ERROR al crear notificacion: {e}")
        import traceback
        traceback.print_exc()
        resultado = {'success': False, 'error': str(e)}
    finally:
        conexion.close()
    
    if resultado.get('success'):
        id_notificacion = resultado.get('id_notificacion')
        print(f"{'='*60}")
        print(f"OK - NOTIFICACION CREADA EXITOSAMENTE!")
        print(f"{'='*60}")
        print(f"\nDetalles:")
        print(f"  - ID Notificacion: {id_notificacion}")
        print(f"  - Medico destinatario: {nombre_medico}")
        print(f"  - ID Usuario: {id_usuario}")
        print(f"\nLa notificacion deberia aparecer en el panel del medico.")
        print(f"Puedes verificar en la base de datos con:")
        print(f"  SELECT * FROM NOTIFICACION WHERE id_notificacion = {id_notificacion};\n")
        
        # Verificar que se creó correctamente
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT id_notificacion, titulo, tipo, fecha_envio, hora_envio, 
                           id_reserva, id_usuario, leida
                    FROM NOTIFICACION
                    WHERE id_notificacion = %s
                """, (id_notificacion,))
                notif_db = cursor.fetchone()
                
                if notif_db:
                    print(f"Verificacion en base de datos:")
                    print(f"  - ID: {notif_db['id_notificacion']}")
                    print(f"  - Titulo: {notif_db['titulo']}")
                    print(f"  - Tipo: {notif_db['tipo']}")
                    print(f"  - Fecha: {notif_db['fecha_envio']} {notif_db['hora_envio']}")
                    print(f"  - ID Reserva: {notif_db['id_reserva']} (debe ser NULL)")
                    print(f"  - ID Usuario: {notif_db['id_usuario']}")
                    print(f"  - Leida: {notif_db['leida']}")
                    
                    if notif_db['id_reserva'] is None:
                        print(f"\nOK - id_reserva es NULL como se esperaba")
                    else:
                        print(f"\nADVERTENCIA - id_reserva no es NULL: {notif_db['id_reserva']}")
        finally:
            conexion.close()
        
        return True
    else:
        error = resultado.get('error', 'Error desconocido')
        print(f"\n{'='*60}")
        print(f"ERROR - NO SE PUDO CREAR LA NOTIFICACION")
        print(f"{'='*60}")
        print(f"\nError: {error}\n")
        return False

def main():
    """Función principal"""
    nombre_medico = "Carlos García Ramírez"
    
    print(f"\n{'='*60}")
    print(f"PRUEBA DE NOTIFICACION - ASIGNACION DE OPERACION")
    print(f"{'='*60}")
    print(f"\nBuscando medico: {nombre_medico}\n")
    
    # Buscar el médico
    medicos = buscar_medico_por_nombre(nombre_medico)
    
    if not medicos:
        print(f"ERROR - No se encontro el medico '{nombre_medico}'")
        print(f"\nMedicos encontrados con nombres similares:")
        # Intentar búsqueda más amplia
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT e.id_empleado, 
                           CONCAT(e.nombres, ' ', e.apellidos) as nombre_completo,
                           e.id_usuario
                    FROM EMPLEADO e
                    WHERE e.nombres LIKE '%Carlos%' OR e.apellidos LIKE '%García%'
                    LIMIT 10
                """)
                similares = cursor.fetchall()
                for med in similares:
                    print(f"  - {med['nombre_completo']} (ID: {med['id_empleado']}, Usuario: {med['id_usuario']})")
        finally:
            conexion.close()
        return False
    
    if len(medicos) > 1:
        print(f"ADVERTENCIA - Se encontraron {len(medicos)} medicos:")
        for i, med in enumerate(medicos, 1):
            print(f"  {i}. {med['nombre_completo']} (ID: {med['id_empleado']}, Usuario: {med['id_usuario']})")
        print(f"\nUsando el primer resultado...\n")
    
    medico = medicos[0]
    nombre_completo = medico['nombre_completo']
    id_usuario = medico.get('id_usuario')
    
    if not id_usuario:
        print(f"ERROR - El medico '{nombre_completo}' no tiene un id_usuario asociado")
        print(f"  ID Empleado: {medico['id_empleado']}")
        return False
    
    print(f"Medico encontrado:")
    print(f"  - Nombre: {nombre_completo}")
    print(f"  - ID Empleado: {medico['id_empleado']}")
    print(f"  - ID Usuario: {id_usuario}")
    if medico.get('correo'):
        print(f"  - Correo: {medico['correo']}")
    
    # Crear la notificación de prueba
    exito = crear_notificacion_prueba_operacion(id_usuario, nombre_completo)
    
    return exito

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nERROR CRITICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

