"""
Genera un reporte Excel "self-service": alguien de otro equipo
(comercial, marketing) lo puede abrir sin saber SQL.

Uso:
    python3 etl/generar_reporte.py
(Requiere haber corrido antes etl/load_and_refresh.py)
"""
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "ventas.db"
OUT_PATH = BASE_DIR / "output" / "reporte_ventas.xlsx"


def main():
    conn = sqlite3.connect(DB_PATH)

    ventas_por_mes = pd.read_sql_query("""
        SELECT strftime('%Y-%m', p.fecha) AS mes,
               SUM(dp.precio_unitario * dp.cantidad) AS ventas_totales
        FROM pedidos p
        JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
        GROUP BY mes ORDER BY mes
    """, conn)

    top_productos = pd.read_sql_query("""
        SELECT pr.nombre AS producto, pr.categoria,
               SUM(dp.cantidad) AS unidades_vendidas,
               SUM(dp.precio_unitario * dp.cantidad) AS ingresos
        FROM detalle_pedido dp
        JOIN productos pr ON pr.producto_id = dp.producto_id
        GROUP BY pr.producto_id
        ORDER BY ingresos DESC
    """, conn)

    clientes_recurrentes = pd.read_sql_query("""
        SELECT c.nombre, c.email, c.ciudad,
               COUNT(DISTINCT p.pedido_id) AS cantidad_pedidos,
               SUM(dp.precio_unitario * dp.cantidad) AS gasto_total
        FROM clientes c
        JOIN pedidos p ON p.cliente_id = c.cliente_id
        JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
        GROUP BY c.cliente_id
        HAVING cantidad_pedidos > 1
        ORDER BY gasto_total DESC
    """, conn)

    ventas_por_ciudad = pd.read_sql_query("""
        SELECT c.ciudad, pr.categoria,
               SUM(dp.precio_unitario * dp.cantidad) AS ventas
        FROM clientes c
        JOIN pedidos p ON p.cliente_id = c.cliente_id
        JOIN detalle_pedido dp ON dp.pedido_id = p.pedido_id
        JOIN productos pr ON pr.producto_id = dp.producto_id
        GROUP BY c.ciudad, pr.categoria
        ORDER BY c.ciudad, ventas DESC
    """, conn)

    conn.close()

    OUT_PATH.parent.mkdir(exist_ok=True)
    with pd.ExcelWriter(OUT_PATH, engine="openpyxl") as writer:
        ventas_por_mes.to_excel(writer, sheet_name="Ventas por mes", index=False)
        top_productos.to_excel(writer, sheet_name="Top productos", index=False)
        clientes_recurrentes.to_excel(writer, sheet_name="Clientes recurrentes", index=False)
        ventas_por_ciudad.to_excel(writer, sheet_name="Ventas por ciudad", index=False)

    print(f"Reporte generado en: {OUT_PATH}")


if __name__ == "__main__":
    main()
