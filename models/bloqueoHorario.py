from bd import obtener_conexion
from datetime import date, time

class BloqueoHorario:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los bloqueos de horario"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, p.fecha as fecha_programacion, p.hora_inicio as hora_inicio_programacion, p.hora_fin as hora_fin_programacion
            FROM BLOQUEO_PROGRAMACION b
            LEFT JOIN PROGRAMACION p ON b.id_programacion = p.id_programacion
            ORDER BY b.fecha DESC, b.hora_inicio ASC
        """)
        bloqueos = cursor.fetchall()
        cursor.close()
        conn.close()
        return bloqueos

    @staticmethod
    def obtener_por_id(id_bloqueo):
        """Obtiene un bloqueo específico por ID"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, p.fecha as fecha_programacion, p.hora_inicio as hora_inicio_programacion, p.hora_fin as hora_fin_programacion
            FROM BLOQUEO_PROGRAMACION b
            LEFT JOIN PROGRAMACION p ON b.id_programacion = p.id_programacion
            WHERE b.id_bloqueo = %s
        """, (id_bloqueo,))
        bloqueo = cursor.fetchone()
        cursor.close()
        conn.close()
        return bloqueo

    @staticmethod
    def obtener_por_fecha(fecha):
        """Obtiene bloqueos por fecha"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, p.fecha as fecha_programacion, p.hora_inicio as hora_inicio_programacion, p.hora_fin as hora_fin_programacion
            FROM BLOQUEO_PROGRAMACION b
            LEFT JOIN PROGRAMACION p ON b.id_programacion = p.id_programacion
            WHERE b.fecha = %s
            ORDER BY b.hora_inicio ASC
        """, (fecha,))
        bloqueos = cursor.fetchall()
        cursor.close()
        conn.close()
        return bloqueos

    @staticmethod
    def obtener_por_programacion(id_programacion):
        """Obtiene bloqueos por ID de programación"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, p.fecha as fecha_programacion, p.hora_inicio as hora_inicio_programacion, p.hora_fin as hora_fin_programacion
            FROM BLOQUEO_PROGRAMACION b
            LEFT JOIN PROGRAMACION p ON b.id_programacion = p.id_programacion
            WHERE b.id_programacion = %s
            ORDER BY b.fecha DESC, b.hora_inicio ASC
        """, (id_programacion,))
        bloqueos = cursor.fetchall()
        cursor.close()
        conn.close()
        return bloqueos

    @staticmethod
    def buscar_por_filtros(fecha=None, id_programacion=None, estado=None):
        """Busca bloqueos con filtros opcionales"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT b.*, p.fecha as fecha_programacion, p.hora_inicio as hora_inicio_programacion, p.hora_fin as hora_fin_programacion
            FROM BLOQUEO_PROGRAMACION b
            LEFT JOIN PROGRAMACION p ON b.id_programacion = p.id_programacion
            WHERE 1=1
        """
        params = []

        if fecha:
            query += " AND b.fecha = %s"
            params.append(fecha)
        if id_programacion:
            query += " AND b.id_programacion = %s"
            params.append(id_programacion)
        if estado:
            query += " AND b.estado = %s"
            params.append(estado)

        query += " ORDER BY b.fecha DESC, b.hora_inicio ASC"
        cursor.execute(query, params)
        bloqueos = cursor.fetchall()
        cursor.close()
        conn.close()
        return bloqueos

    @staticmethod
    def crear(fecha, hora_inicio, hora_fin, motivo, estado, id_programacion):
        """Crea un nuevo bloqueo de horario"""
        print("Creating bloqueo with data:", fecha, hora_inicio, hora_fin, motivo, estado, id_programacion)
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO BLOQUEO_PROGRAMACION (fecha, hora_inicio, hora_fin, motivo, estado, id_programacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha, hora_inicio, hora_fin, motivo, estado, id_programacion))
            print("Execute successful, rowcount:", cursor.rowcount)
            conn.commit()
            bloqueo_id = cursor.lastrowid
            print("Committed, lastrowid:", bloqueo_id)
            return {'success': True, 'id_bloqueo': bloqueo_id}
        except Exception as e:
            print("Exception during insert:", str(e))
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar(id_bloqueo, fecha=None, hora_inicio=None, hora_fin=None, motivo=None, estado=None, id_programacion=None):
        """Actualiza un bloqueo de horario"""
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            fields = []
            params = []
            if fecha is not None:
                fields.append("fecha = %s")
                params.append(fecha)
            if hora_inicio is not None:
                fields.append("hora_inicio = %s")
                params.append(hora_inicio)
            if hora_fin is not None:
                fields.append("hora_fin = %s")
                params.append(hora_fin)
            if motivo is not None:
                fields.append("motivo = %s")
                params.append(motivo)
            if estado is not None:
                fields.append("estado = %s")
                params.append(estado)
            if id_programacion is not None:
                fields.append("id_programacion = %s")
                params.append(id_programacion)

            if not fields:
                return {'success': False, 'error': 'No fields to update'}

            query = f"UPDATE BLOQUEO_PROGRAMACION SET {', '.join(fields)} WHERE id_bloqueo = %s"
            params.append(id_bloqueo)
            cursor.execute(query, params)
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar(id_bloqueo):
        """Elimina un bloqueo de horario"""
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM BLOQUEO_PROGRAMACION WHERE id_bloqueo = %s", (id_bloqueo,))
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
