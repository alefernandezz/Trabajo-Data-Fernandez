-- ============================================================
-- 04_optimizacion.sql
-- Documentación real de tuning de una query pesada.
-- ============================================================

SELECT c.nombre, SUM(dp.precio_unitario * dp.cantidad) AS gasto
FROM clientes c
JOIN pedidos p ON p.cliente_id = c.cliente_id
JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
WHERE p.fecha BETWEEN '2025-03-01' AND '2025-06-30'
GROUP BY c.cliente_id
ORDER BY gasto DESC
LIMIT 10;

-- ------------------------------------------------------------
-- ANTES (sin índices en pedidos.fecha ni detalle_pedido.pedido_id):
--
--   SCAN dp                                    <- recorre TODA la tabla
--   SEARCH p USING INTEGER PRIMARY KEY (rowid=?)
--   SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
--   USE TEMP B-TREE FOR GROUP BY
--   USE TEMP B-TREE FOR ORDER BY
--
-- Diagnóstico: "SCAN dp" es un full table scan de detalle_pedido.
-- En una tabla de millones de filas sería el cuello de botella.
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_pedidos_fecha       ON pedidos(fecha);
CREATE INDEX IF NOT EXISTS idx_detalle_pedido_id   ON detalle_pedido(pedido_id);

-- ------------------------------------------------------------
-- DESPUÉS (con los índices creados arriba):
--
--   SEARCH p USING INDEX idx_pedidos_fecha (fecha>? AND fecha<?)
--   SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
--   SEARCH dp USING INDEX idx_detalle_pedido_id (pedido_id=?)
--   USE TEMP B-TREE FOR GROUP BY
--   USE TEMP B-TREE FOR ORDER BY
--
-- El "SCAN dp" desapareció: ahora busca por índice en vez de escanear todo.
-- ------------------------------------------------------------
