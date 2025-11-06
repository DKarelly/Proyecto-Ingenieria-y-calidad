"""
Script simplificado para actualizar la base de datos paso por paso
"""
import pymysql
from bd import obtener_conexion

def ejecutar_actualizacion_manual():
    """Ejecuta la actualización paso por paso con manejo de errores"""
    
    print("\n" + "=" * 60)
    print("ACTUALIZACIÓN MANUAL DE BASE DE DATOS")
    print("=" * 60 + "\n")
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    try:
        # PASO 1: Agregar columna descripcion a ROL
        print("PASO 1: Agregando columna 'descripcion' a tabla ROL...")
        try:
            cursor.execute("ALTER TABLE `ROL` ADD COLUMN `descripcion` TEXT AFTER `nombre`")
            print("✅ Columna agregada exitosamente\n")
        except pymysql.Error as e:
            if "Duplicate column name" in str(e):
                print("⚠️  La columna ya existe, continuando...\n")
            else:
                print(f"❌ Error: {e}\n")
                raise
        
        conexion.commit()
        
        # PASO 2: Actualizar descripciones de roles existentes
        print("PASO 2: Actualizando descripciones de roles...")
        descripciones = {
            'Administrador': 'Acceso total al sistema con permisos de administración',
            'Médico': 'Gestión de consultas médicas y atención de pacientes',
            'Recepcionista': 'Gestión de citas y atención en recepción',
            'Farmacéutico': 'Gestión de medicamentos y farmacia',
            'Laboratorista': 'Gestión de exámenes y análisis de laboratorio'
        }
        
        for rol, desc in descripciones.items():
            cursor.execute("UPDATE `ROL` SET `descripcion` = %s WHERE `nombre` = %s", (desc, rol))
            print(f"   ✓ {rol}")
        
        conexion.commit()
        print("✅ Descripciones actualizadas\n")
        
        # PASO 3: Eliminar tabla ROL_PERMISO primero (tiene foreign keys)
        print("PASO 3: Eliminando tablas existentes...")
        try:
            cursor.execute("DROP TABLE IF EXISTS `ROL_PERMISO`")
            print("   ✓ ROL_PERMISO eliminada")
            cursor.execute("DROP TABLE IF EXISTS `PERMISO`")
            print("   ✓ PERMISO eliminada")
            print("✅ Tablas eliminadas\n")
        except pymysql.Error as e:
            print(f"⚠️  Advertencia: {e}\n")
        
        conexion.commit()
        
        # PASO 4: Crear tabla PERMISO
        print("PASO 4: Creando tabla PERMISO...")
        try:
            cursor.execute("""
                CREATE TABLE `PERMISO` (
                  `id_permiso` INT NOT NULL AUTO_INCREMENT,
                  `nombre` VARCHAR(100) NOT NULL,
                  `codigo` VARCHAR(50) NOT NULL,
                  `descripcion` TEXT,
                  `modulo` VARCHAR(50) NOT NULL,
                  `estado` VARCHAR(20) DEFAULT 'Activo',
                  PRIMARY KEY (`id_permiso`),
                  UNIQUE KEY `codigo` (`codigo`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("✅ Tabla PERMISO creada\n")
        except pymysql.Error as e:
            print(f"❌ Error: {e}\n")
            raise
        
        conexion.commit()
        
        # PASO 5: Crear tabla ROL_PERMISO
        print("PASO 5: Creando tabla ROL_PERMISO...")
        try:
            cursor.execute("""
                CREATE TABLE `ROL_PERMISO` (
                  `id_rol` INT NOT NULL,
                  `id_permiso` INT NOT NULL,
                  PRIMARY KEY (`id_rol`, `id_permiso`),
                  KEY `id_permiso` (`id_permiso`),
                  CONSTRAINT `ROL_PERMISO_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `ROL` (`id_rol`) ON DELETE CASCADE,
                  CONSTRAINT `ROL_PERMISO_ibfk_2` FOREIGN KEY (`id_permiso`) REFERENCES `PERMISO` (`id_permiso`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("✅ Tabla ROL_PERMISO creada\n")
        except pymysql.Error as e:
            print(f"❌ Error: {e}\n")
            raise
        
        conexion.commit()
        
        # PASO 6: Insertar permisos
        print("PASO 6: Insertando permisos del sistema...")
        
        permisos = [
            # Módulo: Administración
            ('Ver Panel Administración', 'admin.panel.ver', 'Permite acceder al panel de administración', 'Administración'),
            ('Gestionar Programación', 'admin.programacion.gestionar', 'Permite crear y modificar programaciones', 'Administración'),
            ('Gestionar Recursos Físicos', 'admin.recursos.gestionar', 'Permite administrar recursos físicos', 'Administración'),
            ('Gestionar Horarios', 'admin.horarios.gestionar', 'Permite configurar horarios laborables', 'Administración'),
            ('Gestionar Bloqueos', 'admin.bloqueos.gestionar', 'Permite bloquear y desbloquear horarios', 'Administración'),
            ('Consultar Agenda Médica', 'admin.agenda.consultar', 'Permite consultar la agenda médica', 'Administración'),
            ('Gestionar Catálogo de Servicios', 'admin.catalogo.gestionar', 'Permite administrar el catálogo de servicios', 'Administración'),
            
            # Módulo: Reservas
            ('Ver Panel Reservas', 'reservas.panel.ver', 'Permite acceder al panel de reservas', 'Reservas'),
            ('Generar Reserva', 'reservas.generar', 'Permite crear nuevas reservas', 'Reservas'),
            ('Consultar Disponibilidad', 'reservas.disponibilidad.consultar', 'Permite consultar disponibilidad de servicios', 'Reservas'),
            ('Reprogramar Reserva', 'reservas.reprogramar', 'Permite reprogramar citas existentes', 'Reservas'),
            ('Gestionar Cancelaciones', 'reservas.cancelaciones.gestionar', 'Permite cancelar reservas', 'Reservas'),
            ('Gestionar Confirmaciones', 'reservas.confirmaciones.gestionar', 'Permite confirmar citas', 'Reservas'),
            
            # Módulo: Cuentas
            ('Ver Panel Cuentas', 'cuentas.panel.ver', 'Permite acceder al panel de cuentas', 'Cuentas'),
            ('Gestionar Cuentas Internas', 'cuentas.internas.gestionar', 'Permite administrar cuentas de empleados', 'Cuentas'),
            ('Gestionar Roles y Permisos', 'cuentas.roles.gestionar', 'Permite configurar roles y permisos', 'Cuentas'),
            ('Gestionar Datos Pacientes', 'cuentas.pacientes.gestionar', 'Permite administrar datos de pacientes', 'Cuentas'),
            
            # Módulo: Notificaciones
            ('Ver Panel Notificaciones', 'notificaciones.panel.ver', 'Permite acceder al panel de notificaciones', 'Notificaciones'),
            ('Gestionar Recordatorios', 'notificaciones.recordatorios.gestionar', 'Permite configurar recordatorios automáticos', 'Notificaciones'),
            ('Gestionar Notificaciones de Cambios', 'notificaciones.cambios.gestionar', 'Permite enviar notificaciones de cambios', 'Notificaciones'),
            
            # Módulo: Seguridad
            ('Ver Panel Seguridad', 'seguridad.panel.ver', 'Permite acceder al panel de seguridad', 'Seguridad'),
            ('Consultar Actividad', 'seguridad.actividad.consultar', 'Permite consultar logs de actividad', 'Seguridad'),
            ('Generar Incidencia', 'seguridad.incidencias.generar', 'Permite crear nuevas incidencias', 'Seguridad'),
            ('Consultar Incidencia', 'seguridad.incidencias.consultar', 'Permite ver incidencias registradas', 'Seguridad'),
            ('Asignar Responsable', 'seguridad.incidencias.asignar', 'Permite asignar responsables a incidencias', 'Seguridad'),
            ('Generar Informe', 'seguridad.incidencias.informe', 'Permite generar informes de incidencias', 'Seguridad'),
            
            # Módulo: Reportes
            ('Ver Panel Reportes', 'reportes.panel.ver', 'Permite acceder al panel de reportes', 'Reportes'),
            ('Consultar por Categoría', 'reportes.categoria.consultar', 'Permite generar reportes por categoría', 'Reportes'),
            ('Generar Reporte de Actividad', 'reportes.actividad.generar', 'Permite generar reportes de actividad', 'Reportes'),
            ('Generar Ocupación de Recursos', 'reportes.ocupacion.generar', 'Permite generar reportes de ocupación', 'Reportes'),
            
            # Módulo: Farmacia
            ('Ver Panel Farmacia', 'farmacia.panel.ver', 'Permite acceder al panel de farmacia', 'Farmacia'),
            ('Gestionar Entrega Medicamentos', 'farmacia.entrega.gestionar', 'Permite registrar entregas de medicamentos', 'Farmacia'),
            ('Gestionar Recepción Medicamentos', 'farmacia.recepcion.gestionar', 'Permite registrar recepciones de medicamentos', 'Farmacia'),
            
            # Módulo: Exámenes y Operaciones
            ('Generar Examen', 'examenes.generar', 'Permite registrar nuevos exámenes', 'Exámenes'),
            ('Gestionar Exámenes', 'examenes.gestionar', 'Permite administrar exámenes existentes', 'Exámenes'),
            ('Generar Operación', 'operaciones.generar', 'Permite registrar nuevas operaciones', 'Operaciones'),
            ('Gestionar Operaciones', 'operaciones.gestionar', 'Permite administrar operaciones existentes', 'Operaciones'),
        ]
        
        cursor.executemany("""
            INSERT INTO `PERMISO` (`nombre`, `codigo`, `descripcion`, `modulo`)
            VALUES (%s, %s, %s, %s)
        """, permisos)
        
        print(f"✅ {len(permisos)} permisos insertados\n")
        conexion.commit()
        
        # PASO 7: Asignar permisos a roles
        print("PASO 7: Asignando permisos a roles...")
        
        # Administrador - TODOS los permisos
        cursor.execute("""
            INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
            SELECT 1, `id_permiso` FROM `PERMISO`
        """)
        print("   ✓ Administrador: todos los permisos")
        
        # Médico
        cursor.execute("""
            INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
            SELECT 2, `id_permiso` FROM `PERMISO` 
            WHERE `codigo` IN (
                'admin.agenda.consultar',
                'reservas.panel.ver', 'reservas.generar', 'reservas.disponibilidad.consultar', 'reservas.reprogramar',
                'notificaciones.panel.ver',
                'examenes.generar', 'examenes.gestionar',
                'operaciones.generar', 'operaciones.gestionar',
                'reportes.panel.ver', 'reportes.actividad.generar'
            )
        """)
        print("   ✓ Médico: 12 permisos")
        
        # Recepcionista
        cursor.execute("""
            INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
            SELECT 3, `id_permiso` FROM `PERMISO` 
            WHERE `codigo` IN (
                'reservas.panel.ver', 'reservas.generar', 'reservas.disponibilidad.consultar',
                'reservas.reprogramar', 'reservas.cancelaciones.gestionar', 'reservas.confirmaciones.gestionar',
                'cuentas.panel.ver', 'cuentas.pacientes.gestionar',
                'notificaciones.panel.ver', 'notificaciones.recordatorios.gestionar'
            )
        """)
        print("   ✓ Recepcionista: 10 permisos")
        
        # Farmacéutico
        cursor.execute("""
            INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
            SELECT 4, `id_permiso` FROM `PERMISO` 
            WHERE `codigo` IN (
                'farmacia.panel.ver', 'farmacia.entrega.gestionar', 'farmacia.recepcion.gestionar',
                'notificaciones.panel.ver'
            )
        """)
        print("   ✓ Farmacéutico: 4 permisos")
        
        # Laboratorista
        cursor.execute("""
            INSERT INTO `ROL_PERMISO` (`id_rol`, `id_permiso`)
            SELECT 5, `id_permiso` FROM `PERMISO` 
            WHERE `codigo` IN (
                'examenes.generar', 'examenes.gestionar',
                'notificaciones.panel.ver',
                'reportes.panel.ver'
            )
        """)
        print("   ✓ Laboratorista: 4 permisos")
        
        conexion.commit()
        print("✅ Permisos asignados correctamente\n")
        
        # Verificación final
        print("=" * 60)
        print("VERIFICACIÓN FINAL")
        print("=" * 60 + "\n")
        
        cursor.execute("SELECT COUNT(*) as total FROM PERMISO")
        total = cursor.fetchone()
        print(f"✓ Total permisos: {total['total'] if isinstance(total, dict) else total[0]}")
        
        cursor.execute("SELECT COUNT(*) as total FROM ROL_PERMISO")
        total = cursor.fetchone()
        print(f"✓ Total asignaciones: {total['total'] if isinstance(total, dict) else total[0]}")
        
        cursor.execute("""
            SELECT r.nombre, COUNT(rp.id_permiso) as total
            FROM ROL r
            LEFT JOIN ROL_PERMISO rp ON r.id_rol = rp.id_rol
            GROUP BY r.id_rol
            ORDER BY r.id_rol
        """)
        
        print("\nPermisos por rol:")
        for row in cursor.fetchall():
            if isinstance(row, dict):
                print(f"   • {row['nombre']}: {row['total']} permisos")
            else:
                print(f"   • {row[0]}: {row[1]} permisos")
        
        print("\n" + "=" * 60)
        print("✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        conexion.rollback()
        return False
        
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    print("\n⚠️  Este script actualizará la base de datos CLINICA")
    respuesta = input("¿Continuar? (S/N): ").strip().upper()
    
    if respuesta == 'S':
        if ejecutar_actualizacion_manual():
            print("✅ Puedes iniciar la aplicación ahora.\n")
        else:
            print("❌ La actualización falló.\n")
    else:
        print("\n⚠️  Cancelado.\n")
    
    input("Presiona ENTER para salir...")
