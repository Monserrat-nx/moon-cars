# =========================
# CONTROL DE ACCESO (RBAC)
# =========================
#
# Decoradores para proteger rutas de Flask según la sesión
# y el rol del usuario (Administrador, Empleado, Cliente).
#
# Uso:
#     @app.route("/perfil")
#     @login_requerido
#     def perfil(): ...
#
#     @app.route("/productos/agregar")
#     @rol_requerido("Administrador")
#     def agregar_producto(): ...

from functools import wraps
from flask import session, flash, redirect, url_for


ROL_ADMINISTRADOR = "Administrador"
ROL_EMPLEADO = "Empleado"
ROL_CLIENTE = "Cliente"


def login_requerido(funcion):
    """Solo deja pasar si hay un usuario con sesión iniciada."""

    @wraps(funcion)
    def envoltura(*args, **kwargs):

        if "usuario_id" not in session:
            flash("Debes iniciar sesión para entrar a esa página.", "error")

            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return envoltura


def rol_requerido(*roles_permitidos):
    """Solo deja pasar si el rol del usuario está en roles_permitidos."""

    def decorador(funcion):

        @wraps(funcion)
        def envoltura(*args, **kwargs):

            if "usuario_id" not in session:
                flash("Debes iniciar sesión para entrar a esa página.", "error")

                return redirect(url_for("login"))

            if session.get("rol") not in roles_permitidos:
                flash("No tienes permiso para entrar a esa página.", "error")

                return redirect(url_for("inicio"))

            return funcion(*args, **kwargs)

        return envoltura

    return decorador
