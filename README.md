# Moon-cars 🚗

Sistema web de venta de **automóviles y refacciones** con punto de venta para la pyme **Moon-cars** (Querétaro, México).

Proyecto final de la materia **Lenguajes de Programación (ISC0423)**.

---

## Funcionalidades

- **Catálogo** de carros y refacciones con imágenes guardadas en la base de datos, filtro por categoría y detalle de cada producto.
- **Carrito de compras** guardado en la sesión: agregar, cambiar cantidad, quitar y vaciar.
- **Compra** con transacción ACID (`commit` / `rollback`): se descuenta el stock y se genera un **ticket**.
- **Inicio de sesión y registro** con contraseñas cifradas (hash) y opción "Recordarme".
- **Roles (RBAC)**: Administrador, Empleado y Cliente; también se puede entrar como invitado.
- **CRUD de productos** (solo Administrador): agregar, editar y eliminar, con subida de imagen.
- **Historial de ventas** (Administrador y Empleado) y **Mis compras** (Cliente).
- Páginas de error **404** y **500** con el diseño del sitio.
- Diseño **responsivo** (320 px a 1920 px) con validación visual de formularios.
- Protección contra **SQL Injection** con consultas parametrizadas y pruebas automáticas.

---

## Tecnologías

| Parte | Tecnología |
|---|---|
| Backend | Python 3 + **Flask** |
| Plantillas | **Jinja2** (herencia con `extends`, `for`, `if`) |
| Base de datos | **MariaDB / MySQL** (XAMPP) con `Flask-MySQLdb` |
| Interfaz | **Bootstrap 5.3**, **FontAwesome 6.5**, CSS3 (Flexbox y Grid) |
| Seguridad | `werkzeug.security` (hash de contraseñas), sesiones firmadas |

---

## Estructura del proyecto

```
moon-cars/
├── python.py                  # Aplicación Flask (todas las rutas)
├── seguridad.py               # Decoradores de acceso: login_requerido, rol_requerido
├── config_server.py           # Configuración de la BD y de la sesión
├── requirements.txt           # Librerías de Python
├── database/carros.sql        # Estructura de la BD + datos de prueba
├── pruebas/
│   └── prueba_sql_injection.py  # Pruebas de ataques de SQL Injection
├── static/
│   ├── style.css              # Estilos de la marca (sobre Bootstrap)
│   └── img/                   # Imágenes del sitio
└── templates/                 # Páginas HTML (Jinja2)
```

### Base de datos (6 tablas)

| Tabla | Para qué sirve |
|---|---|
| `roles` | Administrador, Empleado, Cliente |
| `usuarios` | Cuentas (con rol) |
| `categorias` | Carros, Refacciones |
| `productos` | Productos con precio, stock e imagen |
| `ventas` | Encabezado de cada venta (cliente, vendedor, total, fecha) |
| `detalle_venta` | Productos de cada venta |

---

## Instalación en Windows (XAMPP)

### 1. Requisitos

- [Python 3](https://www.python.org/downloads/) (marcar *Add Python to PATH* al instalar)
- [XAMPP](https://www.apachefriends.org/) (MariaDB / MySQL)
- [Git](https://git-scm.com/)

### 2. Descargar el proyecto

```powershell
git clone https://github.com/Monserrat-nx/moon-cars.git
cd moon-cars
```

### 3. Crear el entorno virtual e instalar librerías

```powershell
python -m venv .carros
.carros\Scripts\activate
pip install -r requirements.txt
```

### 4. Crear la base de datos

1. Abrir el **Panel de control de XAMPP** e iniciar **MySQL**.
2. Importar el script (crea la BD `carros` con sus tablas y datos de prueba):

```powershell
C:\xampp\mysql\bin\mysql.exe -u root --default-character-set=utf8mb4 < database\carros.sql
```

> También se puede importar desde **phpMyAdmin** (http://localhost/phpmyadmin) → *Importar* → `database/carros.sql`.

Si tu MySQL tiene contraseña o usa otro puerto, cámbialo en `config_server.py`.

### 5. Correr la aplicación

```powershell
python python.py
```

Abrir en el navegador: **http://localhost:8080**

> La app escucha en `0.0.0.0:8080`, así que también se puede abrir desde otro equipo de la misma red con la IP de la computadora.

---

## Usuarios de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@mooncars.com | Admin123! |
| Empleado | empleado@mooncars.com | Empleado123! |
| Cliente | cliente@mooncars.com | Cliente123! |

### Qué puede hacer cada rol

| Acción | Invitado | Cliente | Empleado | Administrador |
|---|:-:|:-:|:-:|:-:|
| Ver catálogo y carrito | ✅ | ✅ | ✅ | ✅ |
| Comprar | — | ✅ | ✅ | ✅ |
| Ver sus compras | — | ✅ | ✅ | ✅ |
| Ver historial de ventas | — | — | ✅ | ✅ |
| Agregar, editar y eliminar productos | — | — | — | ✅ |

---

## Pruebas de SQL Injection

Con el servidor de MySQL encendido:

```powershell
python pruebas\prueba_sql_injection.py
```

Lanza 73 ataques contra las rutas de la aplicación; todos deben salir como **PASA**.

---

## Integrante

| Nombre | GitHub |
|---|---|
| Neylan Monserrat Márquez Urzúa | [@Monserrat-nx](https://github.com/Monserrat-nx) |
