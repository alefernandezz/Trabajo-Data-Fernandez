-- ============================================================
-- 02_schema_normalizado.sql
-- Refactor de raw_sales en tablas normalizadas (3FN aproximado).
-- Cada entidad (cliente, producto, pedido) vive una sola vez;
-- las relaciones se hacen por ID, no por texto repetido.
-- ============================================================

DROP TABLE IF EXISTS detalle_pedido;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    cliente_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    ciudad          TEXT
);

CREATE TABLE productos (
    producto_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL UNIQUE,
    categoria       TEXT NOT NULL
);

CREATE TABLE pedidos (
    pedido_id       INTEGER PRIMARY KEY,
    cliente_id      INTEGER NOT NULL REFERENCES clientes(cliente_id),
    fecha           TEXT NOT NULL
);

CREATE TABLE detalle_pedido (
    detalle_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id       INTEGER NOT NULL REFERENCES pedidos(pedido_id),
    producto_id     INTEGER NOT NULL REFERENCES productos(producto_id),
    precio_unitario INTEGER NOT NULL CHECK (precio_unitario > 0),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0)
);

-- Nota de portabilidad a MySQL / PostgreSQL:
--   - AUTOINCREMENT (SQLite)  -> AUTO_INCREMENT (MySQL) / GENERATED ALWAYS AS IDENTITY (Postgres)
--   - El resto (PK, FK, CHECK, UNIQUE) es prácticamente idéntico en los 3 motores.
