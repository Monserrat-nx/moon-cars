# =========================================================
# PRUEBA DE SQL INJECTION - MOON-CARS
#
# Ataca la aplicación con entradas maliciosas típicas de
# SQL Injection y revisa que NINGUNA funcione.
#
# Cómo correrla (con XAMPP encendido y la BD "carros" importada):
#     .carros\Scripts\python.exe pruebas\prueba_sql_injection.py
#
# Resultado esperado: todas las pruebas en PASA.
# =========================================================

import os
import sys

# Para poder importar python.py desde la carpeta raíz del proyecto
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import MySQLdb
from python import app
from config_server import Config


# =========================
# ATAQUES TÍPICOS
# =========================

ATAQUES = [
    "' OR '1'='1",
    "' OR '1'='1' -- ",
    "admin@mooncars.com' -- ",
    "admin@mooncars.com' #",
    "' OR 1=1 #",
    "\" OR \"\"=\"",
    "'; DROP TABLE usuarios; -- ",
    "' UNION SELECT 1, 2, 3, 4, 5 -- ",
    "1 OR 1=1",
    "1; DELETE FROM productos",
]


resultados = []


def registrar(nombre, paso):

    resultados.append((nombre, paso))

    print(("PASA   " if paso else "FALLA  ") + nombre)


def consultar_bd(sql, valores=()):
    """Consulta directa a MariaDB para revisar que los datos sigan intactos."""

    conexion = MySQLdb.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        passwd=Config.MYSQL_PASSWORD,
        db=Config.MYSQL_DB,
        charset="utf8mb4"
    )

    cursor = conexion.cursor()

    cursor.execute(sql, valores)

    filas = cursor.fetchall()

    conexion.commit()

    conexion.close()

    return filas


def contar(tabla):

    # El nombre de la tabla viene de esta lista fija, no del usuario
    assert tabla in ("usuarios", "productos", "ventas", "detalle_venta")

    return consultar_bd(f"SELECT COUNT(*) FROM {tabla}")[0][0]


# =========================
# ESTADO INICIAL
# =========================

antes = {tabla: contar(tabla) for tabla in ("usuarios", "productos", "ventas", "detalle_venta")}

print("Registros antes de los ataques:", antes)
print()


# =========================
# 1. LOGIN: no se puede entrar sin la contraseña
# =========================

print("--- Login ---")

for ataque in ATAQUES:

    for correo, password in [(ataque, ataque), ("admin@mooncars.com", ataque), (ataque, "x")]:

        cliente = app.test_client()

        cliente.post("/login", data={"correo": correo, "password": password})

        with cliente.session_transaction() as sesion:
            entro = "usuario_id" in sesion

        registrar(f"login correo={correo!r} password={password!r} no inicia sesión", not entro)


# =========================
# 2. REGISTRO: el ataque no se guarda ni rompe nada
# =========================

print()
print("--- Registro ---")

for ataque in ATAQUES:

    cliente = app.test_client()

    respuesta = cliente.post("/formulario", data={
        "nombre": ataque,
        "correo": ataque,
        "password": "Prueba123!"
    })

    registrar(f"registro con {ataque!r} se rechaza sin error 500", respuesta.status_code == 200)


# =========================
# 3. CATÁLOGO Y PRODUCTO: los parámetros de la URL no se inyectan
# =========================

print()
print("--- Catálogo y producto ---")

cliente = app.test_client()

for ataque in ATAQUES:

    respuesta = cliente.get("/catalogo", query_string={"categoria": ataque})

    registrar(f"/catalogo?categoria={ataque!r} responde sin error", respuesta.status_code == 200)

    respuesta = cliente.get(f"/producto/{ataque}")

    registrar(f"/producto/{ataque!r} no existe (404)", respuesta.status_code == 404)


# =========================
# 4. CARRITO: ids o cantidades maliciosas
# =========================

print()
print("--- Carrito ---")

cliente = app.test_client()

for ataque in ATAQUES:

    respuesta = cliente.post("/carrito/agregar/3", data={"cantidad": ataque})

    with cliente.session_transaction() as sesion:
        carrito = sesion.get("carrito", {})

    registrar(f"cantidad {ataque!r} no entra al carrito", carrito.get("3") is None and respuesta.status_code == 302)

# Carrito alterado a mano en la sesión (ids que no son números)
with cliente.session_transaction() as sesion:
    sesion["carrito"] = {"1) OR (1=1": 1, "3; DROP TABLE productos": 2, "2": 1}

respuesta = cliente.get("/carrito")

registrar("carrito con ids maliciosos en la sesión no rompe la página", respuesta.status_code == 200)


# =========================
# 5. AGREGAR PRODUCTO: el texto se guarda tal cual, como dato
# =========================

print()
print("--- Agregar producto (administrador) ---")

admin = app.test_client()

admin.post("/login", data={"correo": "admin@mooncars.com", "password": "Admin123!"})

nombre_malicioso = "Prueba'); DROP TABLE productos; -- "

admin.post("/productos/agregar", data={
    "nombre": nombre_malicioso,
    "marca": "' OR '1'='1",
    "precio": "100",
    "stock": "1",
    "categoria_id": "2",
    "descripcion": "1; DELETE FROM ventas"
})

guardado = consultar_bd(
    "SELECT id, marca, descripcion FROM productos WHERE nombre = %s",
    (nombre_malicioso,)
)

registrar(
    "el nombre malicioso se guardó como texto normal",
    len(guardado) == 1 and guardado[0][1] == "' OR '1'='1"
)

# Limpiar el producto de prueba
consultar_bd("DELETE FROM productos WHERE nombre = %s", (nombre_malicioso,))


# =========================
# 6. LA BASE DE DATOS SIGUE INTACTA
# =========================

print()
print("--- Integridad de la base de datos ---")

despues = {tabla: contar(tabla) for tabla in antes}

print("Registros después de los ataques:", despues)

registrar("no se borró ni se agregó ningún registro", antes == despues)


# =========================
# RESUMEN
# =========================

total = len(resultados)
fallas = [nombre for nombre, paso in resultados if not paso]

print()
print("=" * 55)
print(f"RESULTADO: {total - len(fallas)} de {total} pruebas pasaron")

if fallas:
    print("Fallaron:")

    for nombre in fallas:
        print("  -", nombre)

    sys.exit(1)

print("La aplicación resiste los ataques de SQL Injection.")
