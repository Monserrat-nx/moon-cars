import os
import base64
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb
import MySQLdb.cursors
from config_server import Config
from seguridad import login_requerido, rol_requerido, ROL_ADMINISTRADOR, ROL_CLIENTE
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

    # Si ya inició sesión, no tiene caso volver a entrar
    if "usuario_id" in session:
        return redirect(url_for("perfil"))

    mensaje = ""

    if request.method == "POST":

        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "")

        try:
            cursor = database.connection.cursor()

            cursor.execute(
                """
                SELECT u.id, u.nombre, u.correo, u.contraseña, r.nombre
                FROM usuarios u
                INNER JOIN roles r ON r.id = u.rol_id
                WHERE u.correo = %s
                """,
                (correo,)
            )

            usuario = cursor.fetchone()

            cursor.close()

        except MySQLdb.Error as error:
            print("Error al iniciar sesión:", error)

            return render_template(
                "login.html",
                mensaje="No se pudo conectar con la base de datos. Intenta más tarde."
            )

        if usuario and check_password_hash(usuario[3], password):

            # Guardar los datos del usuario en la sesión
            session["usuario_id"] = usuario[0]
            session["nombre"] = usuario[1]
            session["rol"] = usuario[4]

            flash(f"Bienvenido(a), {usuario[1]}.", "exito")

            return redirect(url_for("perfil"))

        mensaje = "Correo o contraseña incorrectos"

    return render_template(
        "login.html",
        mensaje=mensaje
    )


# =========================
# CERRAR SESIÓN
# =========================

@app.route("/logout")
def logout():

    # Se borran solo los datos del usuario; el carrito se conserva
    session.pop("usuario_id", None)
    session.pop("nombre", None)
    session.pop("rol", None)

    flash("Cerraste sesión correctamente.", "exito")

    return redirect(url_for("inicio"))

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

        try:
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

            # Guardar usuario en MariaDB (todos los registros nuevos son Clientes)
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, correo, contraseña, rol_id)
                VALUES (%s, %s, %s, (SELECT id FROM roles WHERE nombre = %s))
                """,
                (nombre, correo, password_hash, ROL_CLIENTE)
            )

            database.connection.commit()

            cursor.close()

        except MySQLdb.Error as error:
            database.connection.rollback()

            print("Error al registrar usuario:", error)

            return render_template(
                "formulario.html",
                mensaje="No se pudo crear la cuenta. Intenta más tarde."
            )

        flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "exito")

        return redirect(url_for("login"))

    return render_template(
        "formulario.html",
        mensaje=mensaje
    )

# =========================
# PERFIL
# =========================

@app.route("/perfil")
@login_requerido
def perfil():

    try:
        cursor = database.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(
            """
            SELECT u.nombre, u.correo, u.fecha_registro, r.nombre AS rol
            FROM usuarios u
            INNER JOIN roles r ON r.id = u.rol_id
            WHERE u.id = %s
            """,
            (session["usuario_id"],)
        )

        usuario = cursor.fetchone()

        cursor.close()

    except MySQLdb.Error as error:
        print("Error al cargar el perfil:", error)

        flash("No se pudo cargar tu perfil.", "error")

        return redirect(url_for("inicio"))

    # Si el usuario ya no existe en la BD, se cierra la sesión
    if not usuario:
        return redirect(url_for("logout"))

    return render_template(
        "perfil.html",
        usuario=usuario
    )


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
# FUNCIONES DE APOYO (CATÁLOGO Y CARRITO)
# =========================

def imagen_a_base64(imagen, tipo):
    """Convierte los bytes de la imagen guardada en la BD
    a un texto data:URI en base64 para usarlo en <img src="...">."""

    if not imagen:
        return None

    texto_base64 = base64.b64encode(imagen).decode("utf-8")

    return f"data:{tipo or 'image/jpeg'};base64,{texto_base64}"


def obtener_carrito():
    """Regresa el carrito guardado en la sesión.
    Formato: { "id_producto": cantidad }"""

    return session.get("carrito", {})


def guardar_carrito(carrito):

    session["carrito"] = carrito
    session.modified = True


def contar_carrito():

    return sum(obtener_carrito().values())


# Filtro de Jinja2: {{ producto.precio | moneda }} -> $950,000.00
@app.template_filter("moneda")
def moneda(valor):

    return "${:,.2f}".format(valor or 0)


# Hace que la cantidad del carrito esté disponible en todas las plantillas
@app.context_processor
def datos_globales():

    return {
        "cantidad_carrito": contar_carrito(),
        "es_admin": session.get("rol") == ROL_ADMINISTRADOR
    }


# =========================
# CATÁLOGO
# =========================

@app.route("/catalogo")
def catalogo():

    categoria_id = request.args.get("categoria", type=int)

    productos = []
    categorias = []

    try:
        cursor = database.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")

        categorias = cursor.fetchall()

        # Consulta parametrizada; el filtro de categoría es opcional
        consulta = """
            SELECT p.id, p.nombre, p.marca, p.precio, p.stock,
                   p.imagen, p.imagen_tipo, c.nombre AS categoria
            FROM productos p
            INNER JOIN categorias c ON c.id = p.categoria_id
        """

        parametros = ()

        if categoria_id:
            consulta += " WHERE p.categoria_id = %s"
            parametros = (categoria_id,)

        consulta += " ORDER BY c.nombre, p.nombre"

        cursor.execute(consulta, parametros)

        productos = cursor.fetchall()

        cursor.close()

    except MySQLdb.Error as error:
        print("Error al cargar el catálogo:", error)

        flash("No se pudo cargar el catálogo. Intenta más tarde.", "error")

    # Convertir cada imagen a base64 para la plantilla
    for producto in productos:
        producto["imagen_base64"] = imagen_a_base64(
            producto["imagen"],
            producto["imagen_tipo"]
        )

    return render_template(
        "catalogo.html",
        productos=productos,
        categorias=categorias,
        categoria_actual=categoria_id
    )


# =========================
# DETALLE DE PRODUCTO
# =========================

@app.route("/producto/<int:producto_id>")
def producto(producto_id):

    try:
        cursor = database.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(
            """
            SELECT p.id, p.nombre, p.marca, p.descripcion, p.precio, p.stock,
                   p.imagen, p.imagen_tipo, c.nombre AS categoria
            FROM productos p
            INNER JOIN categorias c ON c.id = p.categoria_id
            WHERE p.id = %s
            """,
            (producto_id,)
        )

        producto_encontrado = cursor.fetchone()

        cursor.close()

    except MySQLdb.Error as error:
        print("Error al cargar el producto:", error)

        flash("No se pudo cargar el producto.", "error")

        return redirect(url_for("catalogo"))

    if not producto_encontrado:
        flash("El producto que buscas no existe.", "error")

        return redirect(url_for("catalogo"))

    producto_encontrado["imagen_base64"] = imagen_a_base64(
        producto_encontrado["imagen"],
        producto_encontrado["imagen_tipo"]
    )

    # Cuántas piezas de este producto ya están en el carrito
    en_carrito = obtener_carrito().get(str(producto_id), 0)

    return render_template(
        "producto.html",
        producto=producto_encontrado,
        en_carrito=en_carrito
    )


# =========================
# CARRITO
# =========================

@app.route("/carrito")
def carrito():

    carrito_sesion = obtener_carrito()

    articulos = []
    total = 0

    if carrito_sesion:

        try:
            cursor = database.connection.cursor(MySQLdb.cursors.DictCursor)

            # Un %s por cada producto del carrito (sigue siendo parametrizada)
            ids = list(carrito_sesion.keys())
            marcadores = ", ".join(["%s"] * len(ids))

            cursor.execute(
                f"""
                SELECT id, nombre, marca, precio, stock, imagen, imagen_tipo
                FROM productos
                WHERE id IN ({marcadores})
                """,
                tuple(ids)
            )

            productos = cursor.fetchall()

            cursor.close()

            carga_correcta = True

        except MySQLdb.Error as error:
            print("Error al cargar el carrito:", error)

            flash("No se pudo cargar el carrito.", "error")

            productos = []
            carga_correcta = False

        for producto_bd in productos:

            cantidad = carrito_sesion[str(producto_bd["id"])]
            subtotal = producto_bd["precio"] * cantidad

            articulos.append({
                "id": producto_bd["id"],
                "nombre": producto_bd["nombre"],
                "marca": producto_bd["marca"],
                "precio": producto_bd["precio"],
                "stock": producto_bd["stock"],
                "cantidad": cantidad,
                "subtotal": subtotal,
                "imagen_base64": imagen_a_base64(
                    producto_bd["imagen"],
                    producto_bd["imagen_tipo"]
                )
            })

            total += subtotal

        # Quitar del carrito productos que ya no existen en la BD
        ids_validos = {str(articulo["id"]) for articulo in articulos}

        if carga_correcta and set(carrito_sesion) != ids_validos:
            guardar_carrito({
                id_producto: cantidad
                for id_producto, cantidad in carrito_sesion.items()
                if id_producto in ids_validos
            })

    return render_template(
        "carrito.html",
        articulos=articulos,
        total=total
    )


def leer_cantidad():
    """Lee la cantidad del formulario; regresa None si no es un entero válido."""

    try:
        cantidad = int(request.form.get("cantidad", 1))

    except ValueError:
        return None

    if cantidad < 1:
        return None

    return cantidad


def obtener_stock(producto_id):
    """Regresa (nombre, stock) del producto o None si no existe."""

    cursor = database.connection.cursor()

    cursor.execute(
        "SELECT nombre, stock FROM productos WHERE id = %s",
        (producto_id,)
    )

    resultado = cursor.fetchone()

    cursor.close()

    return resultado


@app.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
def agregar_carrito(producto_id):

    cantidad = leer_cantidad()

    if cantidad is None:
        flash("La cantidad debe ser un número mayor a 0.", "error")

        return redirect(url_for("producto", producto_id=producto_id))

    try:
        datos_producto = obtener_stock(producto_id)

    except MySQLdb.Error as error:
        print("Error al agregar al carrito:", error)

        flash("No se pudo agregar el producto. Intenta más tarde.", "error")

        return redirect(url_for("catalogo"))

    if not datos_producto:
        flash("El producto no existe.", "error")

        return redirect(url_for("catalogo"))

    nombre, stock = datos_producto

    carrito_sesion = obtener_carrito()
    clave = str(producto_id)

    nueva_cantidad = carrito_sesion.get(clave, 0) + cantidad

    # Validar que no se pida más de lo que hay en stock
    if nueva_cantidad > stock:
        flash(f"Solo hay {stock} pieza(s) de {nombre} disponibles.", "error")

        return redirect(url_for("producto", producto_id=producto_id))

    carrito_sesion[clave] = nueva_cantidad

    guardar_carrito(carrito_sesion)

    flash(f"Agregaste {cantidad} × {nombre} al carrito.", "exito")

    return redirect(url_for("carrito"))


@app.route("/carrito/actualizar/<int:producto_id>", methods=["POST"])
def actualizar_carrito(producto_id):

    carrito_sesion = obtener_carrito()
    clave = str(producto_id)

    if clave not in carrito_sesion:
        return redirect(url_for("carrito"))

    cantidad = leer_cantidad()

    if cantidad is None:
        flash("La cantidad debe ser un número mayor a 0.", "error")

        return redirect(url_for("carrito"))

    try:
        datos_producto = obtener_stock(producto_id)

    except MySQLdb.Error as error:
        print("Error al actualizar el carrito:", error)

        flash("No se pudo actualizar el carrito.", "error")

        return redirect(url_for("carrito"))

    if datos_producto and cantidad > datos_producto[1]:
        flash(f"Solo hay {datos_producto[1]} pieza(s) disponibles.", "error")

        return redirect(url_for("carrito"))

    carrito_sesion[clave] = cantidad

    guardar_carrito(carrito_sesion)

    flash("Carrito actualizado.", "exito")

    return redirect(url_for("carrito"))


@app.route("/carrito/eliminar/<int:producto_id>", methods=["POST"])
def eliminar_carrito(producto_id):

    carrito_sesion = obtener_carrito()

    if carrito_sesion.pop(str(producto_id), None) is not None:
        guardar_carrito(carrito_sesion)

        flash("Producto eliminado del carrito.", "exito")

    return redirect(url_for("carrito"))


@app.route("/carrito/vaciar", methods=["POST"])
def vaciar_carrito():

    guardar_carrito({})

    flash("Vaciaste el carrito.", "exito")

    return redirect(url_for("carrito"))


# =========================
# AGREGAR PRODUCTO
# =========================

# Firmas (primeros bytes) de los formatos de imagen permitidos.
# Así se revisa el contenido real del archivo y no solo su extensión.
FIRMAS_IMAGEN = [
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
]


def detectar_tipo_imagen(datos):
    """Regresa el tipo MIME de la imagen o None si no es una imagen permitida."""

    for firma, tipo in FIRMAS_IMAGEN:
        if datos.startswith(firma):
            return tipo

    # WEBP: empieza con RIFF y en el byte 8 dice WEBP
    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "image/webp"

    return None


def obtener_categorias():

    cursor = database.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")

    categorias = cursor.fetchall()

    cursor.close()

    return categorias


@app.route("/productos/agregar", methods=["GET", "POST"])
@rol_requerido(ROL_ADMINISTRADOR)
def agregar_producto():

    try:
        categorias = obtener_categorias()

    except MySQLdb.Error as error:
        print("Error al cargar categorías:", error)

        flash("No se pudo conectar con la base de datos.", "error")

        return redirect(url_for("catalogo"))

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        marca = request.form.get("marca", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio_texto = request.form.get("precio", "").strip()
        stock_texto = request.form.get("stock", "").strip()
        categoria_texto = request.form.get("categoria_id", "").strip()
        archivo = request.files.get("imagen")

        errores = []

        # Validar textos
        if not nombre or len(nombre) > 100:
            errores.append("El nombre es obligatorio (máximo 100 caracteres).")

        if not marca or len(marca) > 60:
            errores.append("La marca es obligatoria (máximo 60 caracteres).")

        # Validar precio
        try:
            precio = round(float(precio_texto), 2)

            if precio < 0 or precio > 99999999.99:
                raise ValueError

        except ValueError:
            errores.append("El precio debe ser un número mayor o igual a 0.")

        # Validar stock
        try:
            stock = int(stock_texto)

            if stock < 0:
                raise ValueError

        except ValueError:
            errores.append("El stock debe ser un número entero mayor o igual a 0.")

        # Validar categoría (que exista en la BD)
        ids_categorias = {str(categoria["id"]) for categoria in categorias}

        if categoria_texto not in ids_categorias:
            errores.append("Selecciona una categoría válida.")

        # Validar imagen (opcional)
        imagen = None
        imagen_tipo = None

        if archivo and archivo.filename:

            imagen = archivo.read()
            imagen_tipo = detectar_tipo_imagen(imagen)

            if not imagen_tipo:
                errores.append("La imagen debe ser JPG, PNG, GIF o WEBP.")

        if errores:

            for error in errores:
                flash(error, "error")

            return render_template(
                "agregar_producto.html",
                categorias=categorias,
                datos=request.form
            )

        # Guardar producto en MariaDB
        try:
            cursor = database.connection.cursor()

            cursor.execute(
                """
                INSERT INTO productos
                    (nombre, marca, descripcion, precio, stock,
                     imagen, imagen_tipo, categoria_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    nombre,
                    marca,
                    descripcion or None,
                    precio,
                    stock,
                    imagen,
                    imagen_tipo,
                    int(categoria_texto)
                )
            )

            nuevo_id = cursor.lastrowid

            database.connection.commit()

            cursor.close()

        except MySQLdb.Error as error:
            database.connection.rollback()

            print("Error al guardar el producto:", error)

            flash("No se pudo guardar el producto. Intenta de nuevo.", "error")

            return render_template(
                "agregar_producto.html",
                categorias=categorias,
                datos=request.form
            )

        flash(f"Producto \"{nombre}\" agregado correctamente.", "exito")

        return redirect(url_for("producto", producto_id=nuevo_id))

    return render_template(
        "agregar_producto.html",
        categorias=categorias,
        datos={}
    )


# Si suben un archivo más grande que MAX_CONTENT_LENGTH
@app.errorhandler(413)
def archivo_muy_grande(error):

    flash("La imagen es muy grande. El máximo es 2 MB.", "error")

    return redirect(url_for("agregar_producto"))


# =========================
# SERVIDOR
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)