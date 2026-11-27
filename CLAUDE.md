# Moon-cars — Guía del proyecto

Proyecto final de **Lenguajes de Programación (ISC0423)**: sistema web de gestión / punto de venta para una pyme de **venta de automóviles y refacciones** ("Moon-cars", Querétaro).
Stack: Flask + Jinja2 + MariaDB/MySQL (`flask_mysqldb`) + werkzeug.security.

Este archivo es la referencia para trabajar en el repo: estilo de código que hay que respetar, estado actual frente a la rúbrica y plan de trabajo con Git.

---

## 1. Estructura actual

```
Proyecto lenguajes/
├── python.py           # App Flask (todas las rutas)
├── config_server.py    # class Config con credenciales MySQL (BD "carros")
├── static/
│   ├── style.css       # CSS propio (tema oscuro + rojo)
│   └── img/            # Aceite.jpg, jetta.jpg, mustang.jpg
├── templates/
│   ├── plantilla.html  # Layout base con {% block contenido %} (nadie la usa todavía)
│   ├── Proyecto.html   # Inicio (catálogo estático de carros y refacciones)
│   ├── login.html
│   ├── formulario.html # Registro de usuarios (validación JS + servidor)
│   ├── perfil.html
│   ├── contacto.html
│   └── acercade.html   # Fragmento suelto (sin <html> ni extends)
├── .carros/            # venv de Python 3.14 (NO se sube a git)
└── .gitignore          # vacío por ahora
```

Base de datos usada en el código: tabla `usuarios (id, nombre, correo, contraseña)`.

Paquetes instalados en el venv: Flask 3.1.3, Flask-MySQLdb 2.0.0, mysqlclient 2.3.0, mysql-connector-python 26.7.0, Werkzeug 3.1.8, Jinja2 3.1.6.

---

## 2. Estilo de código (seguirlo siempre)

### General
- **Todo en español**: nombres de variables, funciones, rutas, plantillas, comentarios y mensajes al usuario (`correo`, `usuario_existente`, `mensaje`, `password_hash`).
- `snake_case` en Python; las rutas usan el mismo nombre que la función (`/acercade` → `def acercade()`).
- Mucho espacio en blanco vertical: línea vacía después de cada `def`, entre bloques lógicos y antes de cada `return`.

### Python (`python.py`)
- Cada ruta va precedida de un banner de sección en mayúsculas:
  ```python
  # =========================
  # NOMBRE DE LA SECCIÓN
  # =========================
  ```
- Comentarios cortos de una línea que describen el paso: `# Validar correo`, `# Encriptar la contraseña`.
- Llamadas largas partidas en varias líneas, un argumento por línea:
  ```python
  return render_template(
      "formulario.html",
      mensaje=mensaje
  )
  ```
- SQL siempre parametrizado con `%s` y tupla (`(correo,)`); los `INSERT` largos en triple comilla.
- Patrón de cursor: `cursor = database.connection.cursor()` → `execute` → `fetchone()` → `cursor.close()`; `database.connection.commit()` después de escribir.
- Los resultados se leen por índice (`usuario[0]`) y se pasan a la plantilla como diccionario (`usuario_data = {...}`).
- Errores de validación: se guarda el texto en `mensaje` y se re-renderiza la plantilla con `mensaje=mensaje`.
- La instancia de MySQL se llama `database`.

### HTML / Jinja2
- `<html lang="es">`, `<meta charset="UTF-8">`, sangría de 4 espacios.
- Línea vacía entre casi cada elemento; atributos largos de `<input>`/`<img>` uno por línea.
- Comentarios de sección en mayúsculas: `<!-- ENCABEZADO -->`, `<!-- MENÚ -->`, `<!-- CONTENIDO PRINCIPAL -->`.
- Estructura semántica: `header` → `nav > ul > li > a` → `main > section` → `footer`.
- Mensajes de servidor: `{% if mensaje %}<p class="mensaje">{{ mensaje }}</p>{% endif %}`.
- Cada página tiene una clase contenedora con su nombre: `.login`, `.formulario`, `.perfil`, `.contacto`.
- JS en línea al final del `<body>`, con `const`, regex y `event.preventDefault()` + `alert()`.

### CSS (`static/style.css`)
- Bloques separados por banners:
  ```css
  /* ================================
     NOMBRE DE LA SECCIÓN
  ================================ */
  ```
- Una línea vacía entre propiedades dentro de una regla.
- Colores en hexadecimal; media query única `@media (max-width: 700px)` al final.

### Branding (paleta actual)
| Uso | Color |
|---|---|
| Fondo | `#101010` |
| Nav / tarjetas | `#181818`, `#1b1b1b`, `#252525` |
| Rojo principal (botones, bordes, th) | `#e00000` |
| Rojo títulos `h2` | `#ff1a1a` |
| Texto secundario | `#cccccc` |
| Error | fondo `#3a1111`, texto `#ff5555` |

Tipografía actual: Arial/Helvetica. Tema: oscuro con acento rojo, estilo "automotriz".

---

## 3. Estado frente a la rúbrica

| Requisito | Estado |
|---|---|
| Flask con rutas GET/POST | ✅ parcial (login y registro) |
| Hashing de contraseñas (werkzeug) | ✅ |
| Consultas parametrizadas | ✅ en lo que existe |
| HTML5 semántico | ✅ parcial |
| Jinja2 `{% extends %}` | ❌ `plantilla.html` existe pero ninguna página la extiende |
| Jinja2 `for` / `if` | ⚠️ solo `if`; catálogo está escrito a mano en el HTML |
| Bootstrap 5 + FontAwesome | ❌ no se usan |
| Responsive | ⚠️ solo una media query y falta `viewport` en varias páginas |
| Sesiones (`session`) / logout | ❌ el login solo renderiza `perfil.html`, no guarda sesión |
| RBAC (Admin / Empleado / Cliente) | ❌ no hay roles |
| CRUD completo | ❌ solo Create de usuarios |
| ≥3 tablas relacionadas (usuarios, productos, ventas…) | ❌ solo `usuarios` |
| try-except | ❌ ninguno |
| Mensajes flash de éxito/error | ⚠️ solo `mensaje` de error |
| `.gitignore` | ❌ vacío |
| `requirements.txt` | ❌ |
| Dump `.sql` (estructura + datos de prueba) | ❌ |
| Repo GitHub, ramas, `main` protegida, Kanban | ❌ pendiente |

### Bugs detectados
1. **`login.html`**: `<form action="login.html">` sin `method="POST"` → el login nunca llega al backend. Debe ser `<form method="POST" action="/login">` y mostrar `{{ mensaje }}`.
2. **`contacto.html`** empieza con `<<!DOCTYPE html>` (un `<` de más).
3. **`acercade.html`** es un fragmento sin `<html>`/`<head>`: se ve sin estilos.
4. **Clase de mensaje**: el HTML usa `class="mensaje"` pero el CSS define `.MENSAJE` (CSS distingue mayúsculas en clases).
5. **Imágenes en Linux**: el archivo es `Aceite.jpg` y el HTML pide `img/aceite.jpg` → en Ubuntu da 404.
6. **Fondo del header**: `url("../img/fondo.jpg")` apunta fuera de `static/` y el archivo no existe (debería ser `img/fondo.jpg` dentro de `static/`).
7. `/perfil` es accesible sin sesión; `debug=True` y credenciales en `config_server.py` versionadas.
8. Falta `SECRET_KEY` (necesaria para `session` y `flash`).

---

## 4. Plan de Git

1. `git init` en la raíz, rama por defecto `main`.
2. `.gitignore` con: `.carros/`, `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `.vscode/`, `.idea/`.
3. Sacar credenciales a `.env` (o `config_server.py` fuera del repo + `config_server.example.py` versionado).
4. `pip freeze > requirements.txt` (solo lo necesario: Flask, Flask-MySQLdb, mysqlclient, Werkzeug).
5. Commit inicial → conectar remoto → push a `main`.
6. Proteger `main` en GitHub (PR obligatorio) y crear el tablero Kanban en GitHub Projects.
7. Trabajar con ramas por funcionalidad: `feature/sesiones-roles`, `feature/crud-productos`, `feature/ventas`, `feature/bootstrap`, `fix/login-form`, `docs/sql-dump`.
8. Commits en español, en imperativo y cortos: `Agrega CRUD de productos`, `Corrige formulario de login`.
9. Cada integrante hace commits con su propia cuenta para que el historial sea equilibrado.

---

## 5. Siguientes pasos sugeridos (orden)

1. Arreglar bugs de la sección 3.
2. Convertir todas las páginas a `{% extends "plantilla.html" %}` y meter Bootstrap 5 + FontAwesome en la plantilla base.
3. Diseñar BD: `roles`, `usuarios` (FK rol), `productos` (carros y refacciones con `categoria`), `ventas`, `detalle_venta`; exportar `database/carros.sql`.
4. `session` + decorador `login_requerido` / `rol_requerido("admin")`; logout.
5. CRUD de productos (admin) y registro de ventas con transacción (`commit` / `rollback`) para ACID.
6. Envolver cada acceso a BD en `try-except` con `rollback` y mensaje `flash`.
7. Catálogo dinámico con `{% for %}` desde la BD.
8. README con instrucciones de instalación en Ubuntu.
