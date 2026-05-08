import mysql.connector
import os

def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user=os.getenv("DB_USER", "Administrador"),
            password=os.getenv("DB_PASSWORD", "12345"),
            database=os.getenv("DB_NAME", "GENPASS")
        )
        return conexion
    except mysql.connector.Error as e:
        print("Error al conectar a la BD:", e)
        return None