from conexion import conectar_db

# ------------------ HISTORIAL ------------------

def guardar_historial(usuario, password, fuerza, score):
    conn = conectar_db()
    if conn is None:
        return

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO historial (usuario, password, fuerza, score)
        VALUES (%s, %s, %s, %s)
    """, (usuario, password, fuerza, score))

    conn.commit()
    cursor.close()
    conn.close()


def obtener_historial(usuario):
    conn = conectar_db()
    if conn is None:
        return []

    cursor = conn.cursor()

    cursor.execute("""
        SELECT password, fuerza, score, fecha
        FROM historial
        WHERE usuario = %s
        ORDER BY id DESC
    """, (usuario,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


# ------------------ OPCIONAL (PRO) ------------------

def borrar_historial(usuario):
    conn = conectar_db()
    if conn is None:
        return

    cursor = conn.cursor()

    cursor.execute("DELETE FROM historial WHERE usuario = %s", (usuario,))

    conn.commit()
    cursor.close()
    conn.close()

def validar_usuario(usuario, password):
    conn = conectar_db()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT usuario, rol
        FROM usuarios
        WHERE usuario = %s AND password = %s
    """, (usuario, password))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user  # ahora devuelve info completa

from conexion import conectar_db

# ------------------ USUARIOS ------------------

def obtener_usuarios():
    conn = conectar_db()
    if conn is None:
        return []

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, usuario, rol
        FROM usuarios
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def eliminar_usuario(user_id):
    conn = conectar_db()
    if conn is None:
        return False

    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return True


# ------------------ ESTADISTICAS ------------------

def obtener_estadisticas():
    conn = conectar_db()
    if conn is None:
        return {}

    cursor = conn.cursor()

    # total usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_users = cursor.fetchone()[0]

    # total passwords
    cursor.execute("SELECT COUNT(*) FROM historial")
    total_passwords = cursor.fetchone()[0]

    # promedio score
    cursor.execute("SELECT AVG(score) FROM historial")
    avg_score = cursor.fetchone()[0] or 0

    # conteo por fuerza
    cursor.execute("""
    SELECT fuerza, COUNT(*)
    FROM historial
    GROUP BY fuerza
    """)
    fuerza_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "usuarios": total_users,
        "passwords": total_passwords,
        "avg_score": round(avg_score, 2),
        "fuerza": fuerza_data
    }