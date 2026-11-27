import os
from flask import Flask, render_template, request, redirect, url_for 
from flask_mysqldb import MySQL
from config_server import Config
from werkzeug.security import generate_password_hash, check_password_hash
import re

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')



app = Flask(__name__, template_folder=template_dir)
app.config.from_object(Config)
database=MySQL(app)

# =========================
# INICIO
# =========================

@app.route("/")
def inicio():

    return render_template("Proyecto.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    mensaje = ""

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        cursor = database.connection.cursor()

        cursor.execute(
            "SELECT id, nombre, correo, contraseña FROM usuarios WHERE correo = %s",
            (correo,)
        )

        usuario = cursor.fetchone()

        cursor.close()

        if usuario and check_password_hash(usuario[3], password):

            usuario_data = {
                "id": usuario[0],
                "nombre": usuario[1],
                "correo": usuario[2]
            }

            return render_template(
                "perfil.html",
                usuario=usuario_data
            )

        mensaje = "Correo o contraseña incorrectos"

    return render_template(
        "login.html",
        mensaje=mensaje
    )

# =========================
# REGISTRO
# =========================

@app.route("/formulario", methods=["GET", "POST"])
def formulario():

    mensaje = ""

    if request.method == "POST":

        nombre = request.form["nombre"].strip()
        correo = request.form["correo"].strip()
        password = request.form["password"]

        # Validar nombre
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$", nombre):
            mensaje = "El nombre solo puede contener letras y espacios."

            return render_template(
                "formulario.html",
                mensaje=mensaje
            )

        # Validar correo
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
            mensaje = "Ingresa un correo electrónico válido."

            return render_template(
                "formulario.html",
                mensaje=mensaje
            )

        # Validar contraseña
        if (
            len(password) < 8
            or not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
            or not re.search(r"[0-9]", password)
            or not re.search(r"[^A-Za-z0-9]", password)
        ):
            mensaje = "La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial."

            return render_template(
                "formulario.html",
                mensaje=mensaje
            )

        # Buscar si el correo ya existe
        cursor = database.connection.cursor()

        cursor.execute(
            "SELECT id FROM usuarios WHERE correo = %s",
            (correo,)
        )

        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()

            mensaje = "Este correo ya está registrado"

            return render_template(
                "formulario.html",
                mensaje=mensaje
            )

        # Encriptar la contraseña
        password_hash = generate_password_hash(password)

        # Guardar usuario en MariaDB
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, correo, contraseña)
            VALUES (%s, %s, %s)
            """,
            (nombre, correo, password_hash)
        )

        database.connection.commit()

        cursor.close()

        return redirect(url_for("login"))

    return render_template(
        "formulario.html",
        mensaje=mensaje
    )

# =========================
# PERFIL
# =========================

@app.route("/perfil")
def perfil():

    return render_template("perfil.html")


# =========================
# CONTACTO
# =========================

@app.route("/contacto")
def contacto():

    return render_template("contacto.html")


# =========================
# ACERCA DE
# =========================

@app.route("/acercade")
def acercade():

    return render_template("acercade.html")


# =========================
# SERVIDOR
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)