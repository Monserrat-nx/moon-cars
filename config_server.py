import os


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
