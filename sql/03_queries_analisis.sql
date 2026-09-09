-- ============================================================
-- 03_queries_analisis.sql
-- ============================================================

-- 1) Ventas totales por mes
SELECT
    strftime('%Y-%m', fecha) AS mes,
    SUM(dp.precio_unitario * dp.cantidad) AS ventas_totales
FROM pedidos p
JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
GROUP BY mes
ORDER BY mes;

-- 2) Top 5 productos más vendidos (por ingresos)
SELECT
    pr.nombre,
    pr.categoria,
    SUM(dp.cantidad) AS unidades_vendidas,
    SUM(dp.precio_unitario * dp.cantidad) AS ingresos
FROM detalle_pedido dp
JOIN productos pr ON pr.producto_id = dp.producto_id
GROUP BY pr.producto_id
ORDER BY ingresos DESC
LIMIT 5;

-- 3) Clientes recurrentes
SELECT
    c.nombre,
    c.email,
    COUNT(DISTINCT p.pedido_id) AS cantidad_pedidos,
    SUM(dp.precio_unitario * dp.cantidad) AS gasto_total
FROM clientes c
JOIN pedidos p ON p.cliente_id = c.cliente_id
JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
GROUP BY c.cliente_id
HAVING cantidad_pedidos > 1
ORDER BY gasto_total DESC;

-- 4) Ticket promedio y ranking de pedidos por mes (función de ventana)
WITH totales_pedido AS (
    SELECT
        p.pedido_id,
        strftime('%Y-%m', p.fecha) AS mes,
        SUM(dp.precio_unitario * dp.cantidad) AS total_pedido
    FROM pedidos p
    JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
    GROUP BY p.pedido_id
)
SELECT
    mes,
    pedido_id,
    total_pedido,
    RANK() OVER (PARTITION BY mes ORDER BY total_pedido DESC) AS ranking_en_el_mes
FROM totales_pedido
ORDER BY mes, ranking_en_el_mes;

-- 5) Ventas por ciudad y categoría
SELECT
    c.ciudad,
    pr.categoria,
    SUM(dp.precio_unitario * dp.cantidad) AS ventas
FROM clientes c
JOIN pedidos p ON p.cliente_id = c.cliente_id
JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
JOIN productos pr ON pr.producto_id = dp.producto_id
GROUP BY c.ciudad, pr.categoria
ORDER BY c.ciudad, ventas DESC;
