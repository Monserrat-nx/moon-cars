import os
from datetime import timedelta


class Config:
    MYSQL_HOST = "127.0.0.1"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DB = "carros"
    MYSQL_CHARSET = "utf8mb4"

    # Llave para firmar la sesión (carrito, login).
    # En producción se cambia con la variable de entorno SECRET_KEY.
    SECRET_KEY = os.environ.get("SECRET_KEY", "moon-cars-clave-de-desarrollo")

    # "Recordarme": cuánto dura la sesión si el usuario marca la casilla
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

    # La cookie de sesión no se puede leer desde JavaScript
    # y no se manda desde otros sitios
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Tamaño máximo de lo que se puede subir (imágenes): 2 MB
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
