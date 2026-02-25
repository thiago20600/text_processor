import mysql.connector
import os

# Configuración de la conexión (ajusta estos valores a tu entorno)
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "text_processor_db")
    )
