-- ============================================================
-- 01_schema_raw.sql
-- Tabla "cruda": así suele llegar la data desde un sistema
-- operativo (un CSV plano, todo repetido y desnormalizado).
-- Un pedido con 3 productos genera 3 filas que repiten
-- nombre/email/ciudad del cliente y categoría del producto.
-- ============================================================

DROP TABLE IF EXISTS raw_sales;

CREATE TABLE raw_sales (
    order_id        INTEGER,
    order_date      TEXT,
    customer_name   TEXT,
    customer_email  TEXT,
    customer_city   TEXT,
    product_name    TEXT,
    category        TEXT,
    unit_price      INTEGER,
    quantity        INTEGER
);

-- Problemas de este diseño (para documentar en el README):
--   1. El email/nombre/ciudad del cliente se repite en cada fila -> redundancia
--      y riesgo de inconsistencia (typos en distintas filas del mismo cliente).
--   2. La categoría depende del producto pero está repetida por fila.
--   3. No hay integridad referencial: nada impide un unit_price negativo
--      o un product_name mal escrito que "invente" un producto nuevo.
--   4. Cualquier agregación (ventas por cliente, por producto) implica
--      escanear y agrupar texto libre en vez de IDs -> más lento e impreciso.
