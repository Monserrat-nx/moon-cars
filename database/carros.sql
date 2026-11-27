-- =========================================================
-- MOON-CARS - BASE DE DATOS
-- Motor: MariaDB 10.4 (XAMPP) / MySQL
--
-- Cómo importarlo:
--   phpMyAdmin -> Importar -> seleccionar este archivo
--   o en PowerShell:
--   C:\xamppp\mysql\bin\mysql.exe -u root < database\carros.sql
--
-- OJO: borra y vuelve a crear las tablas de "carros".
--
-- Usuarios de prueba (contraseña en texto solo para pruebas,
-- en la BD se guardan con hash de werkzeug):
--   admin@mooncars.com     ->  Admin123!     (Administrador)
--   empleado@mooncars.com  ->  Empleado123!  (Empleado)
--   cliente@mooncars.com   ->  Cliente123!   (Cliente)
-- =========================================================

CREATE DATABASE IF NOT EXISTS carros
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE carros;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS detalle_venta;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS roles;

SET FOREIGN_KEY_CHECKS = 1;


-- =========================
-- ROLES
-- =========================

CREATE TABLE roles (
    id      INT          NOT NULL AUTO_INCREMENT,
    nombre  VARCHAR(30)  NOT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =========================
-- USUARIOS
-- =========================

CREATE TABLE usuarios (
    id              INT           NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(100)  NOT NULL,
    correo          VARCHAR(150)  NOT NULL,
    contraseña      VARCHAR(255)  NOT NULL,
    rol_id          INT           NOT NULL DEFAULT 3,
    fecha_registro  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_correo (correo),

    CONSTRAINT fk_usuarios_rol
        FOREIGN KEY (rol_id) REFERENCES roles (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =========================
-- CATEGORÍAS
-- =========================

CREATE TABLE categorias (
    id      INT          NOT NULL AUTO_INCREMENT,
    nombre  VARCHAR(50)  NOT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_categorias_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =========================
-- PRODUCTOS
-- =========================

CREATE TABLE productos (
    id            INT            NOT NULL AUTO_INCREMENT,
    nombre        VARCHAR(100)   NOT NULL,
    marca         VARCHAR(60)    NOT NULL,
    descripcion   TEXT           NULL,
    precio        DECIMAL(10,2)  NOT NULL,
    stock         INT            NOT NULL DEFAULT 0,
    imagen        VARCHAR(150)   NULL,
    categoria_id  INT            NOT NULL,

    PRIMARY KEY (id),

    CONSTRAINT chk_productos_precio CHECK (precio >= 0),
    CONSTRAINT chk_productos_stock  CHECK (stock >= 0),

    CONSTRAINT fk_productos_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =========================
-- VENTAS
-- =========================

CREATE TABLE ventas (
    id           INT            NOT NULL AUTO_INCREMENT,
    vendedor_id  INT            NOT NULL,
    cliente_id   INT            NULL,
    fecha        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total        DECIMAL(12,2)  NOT NULL DEFAULT 0,

    PRIMARY KEY (id),

    CONSTRAINT fk_ventas_vendedor
        FOREIGN KEY (vendedor_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_ventas_cliente
        FOREIGN KEY (cliente_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =========================
-- DETALLE DE VENTA
-- =========================

CREATE TABLE detalle_venta (
    id               INT            NOT NULL AUTO_INCREMENT,
    venta_id         INT            NOT NULL,
    producto_id      INT            NOT NULL,
    cantidad         INT            NOT NULL,
    precio_unitario  DECIMAL(10,2)  NOT NULL,
    subtotal         DECIMAL(12,2)  AS (cantidad * precio_unitario) STORED,

    PRIMARY KEY (id),

    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),

    CONSTRAINT fk_detalle_venta
        FOREIGN KEY (venta_id) REFERENCES ventas (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (producto_id) REFERENCES productos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =========================
-- DATOS DE PRUEBA
-- =========================

INSERT INTO roles (id, nombre) VALUES
    (1, 'Administrador'),
    (2, 'Empleado'),
    (3, 'Cliente');


INSERT INTO usuarios (nombre, correo, contraseña, rol_id) VALUES
    (
        'Administrador Moon-cars',
        'admin@mooncars.com',
        'scrypt:32768:8:1$Q0n68kMz6Ct80Jdj$de42015d9a2509d6fe40de8b1a715553b01042079a123eba3dbc458c43db81867a952d39935f415fae8a393fb5a7b04fc8f90fa39977cbd81b84dcf34c5642eb',
        1
    ),
    (
        'Empleado de Prueba',
        'empleado@mooncars.com',
        'scrypt:32768:8:1$1AxtnMa5MBPEI01W$ebe5ba5a3b0a8a08fc4b32681060152cc2abf7605842d5f86140c4c2b95be6643959131799b659be137b6f52f23da87b99f2edd07599a7629dae0268712c12d4',
        2
    ),
    (
        'Cliente de Prueba',
        'cliente@mooncars.com',
        'scrypt:32768:8:1$a7PAqncaqi8dihdt$00c5b09e372ee1108dadf6cfe28b875bf969e8a1b98cd7e7f82672c68e1bcc56d81bf64a6887bc59b1f5e9c413efa258ef4d83c2c0d734b5400047c3fb978c30',
        3
    );


INSERT INTO categorias (id, nombre) VALUES
    (1, 'Carros'),
    (2, 'Refacciones');


INSERT INTO productos (nombre, marca, descripcion, precio, stock, imagen, categoria_id) VALUES
    ('Mustang GT',       'Ford',       'Motor V8 5.0 L, transmisión manual de 6 velocidades.', 950000.00, 2,  'mustang.jpg', 1),
    ('Jetta GLI',        'Volkswagen', 'Motor 2.0 L turbo, transmisión DSG.',                   620000.00, 3,  'jetta.jpg',   1),
    ('Aceite Sintético', 'Mobil',      'Aceite 5W-30 sintético, 5 litros.',                       550.00, 40, 'aceite.jpg',  2),
    ('Llanta Michelin',  'Michelin',   'Llanta 205/55 R16 Primacy 4.',                           3200.00, 16, NULL,          2),
    ('Batería LTH',      'LTH',        'Batería 12V, 600 CCA.',                                  2100.00, 10, NULL,          2);


-- Venta de ejemplo: el empleado le vende al cliente 2 aceites y 1 batería

INSERT INTO ventas (id, vendedor_id, cliente_id, total) VALUES
    (1, 2, 3, 3200.00);

INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario) VALUES
    (1, 3, 2, 550.00),
    (1, 5, 1, 2100.00);
