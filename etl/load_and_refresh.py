"""

Flujo:
  1. Lee data/raw_sales.csv (data cruda tal como llegaría de un sistema operativo).
  2. La carga tal cual en la tabla raw_sales (sql/01_schema_raw.sql).
  3. Refactoriza esa data en el esquema normalizado (sql/02_schema_normalizado.sql):
     - deduplica clientes por email
     - deduplica productos por nombre
     - arma pedidos y detalle_pedido
  4. Es idempotente: se puede correr muchas veces sin duplicar datos.

Uso:
    python3 etl/load_and_refresh.py
"""
import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "ventas.db"
CSV_PATH = BASE_DIR / "data" / "raw_sales.csv"
SQL_DIR = BASE_DIR / "sql"


def run_sql_file(conn, path):
    with open(path, encoding="utf-8") as f:
        conn.executescript(f.read())


def cargar_raw(conn):
    """Paso 1: crea y puebla la tabla cruda desde el CSV, sin transformar nada."""
    run_sql_file(conn, SQL_DIR / "01_schema_raw.sql")
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["order_id"]), r["order_date"], r["customer_name"],
                r["customer_email"], r["customer_city"], r["product_name"],
                r["category"], int(r["unit_price"]), int(r["quantity"]),
            )
            for r in reader
        ]
    conn.executemany(
        "INSERT INTO raw_sales VALUES (?,?,?,?,?,?,?,?,?)", rows
    )
    conn.commit()
    print(f"[raw] {len(rows)} filas cargadas en raw_sales")


def normalizar(conn):
    """Paso 2: recrea el esquema modelado y lo puebla a partir de raw_sales."""
    run_sql_file(conn, SQL_DIR / "02_schema_normalizado.sql")
    cur = conn.cursor()

    # --- clientes (dedupe por email) ---
    cur.execute("""
        SELECT DISTINCT customer_email, customer_name, customer_city
        FROM raw_sales
    """)
    clientes_map = {}
    for email, nombre, ciudad in cur.fetchall():
        cur.execute(
            "INSERT INTO clientes (nombre, email, ciudad) VALUES (?,?,?)",
            (nombre, email, ciudad),
        )
        clientes_map[email] = cur.lastrowid

    # --- productos (dedupe por nombre) ---
    cur.execute("SELECT DISTINCT product_name, category FROM raw_sales")
    productos_map = {}
    for nombre, categoria in cur.fetchall():
        cur.execute(
            "INSERT INTO productos (nombre, categoria) VALUES (?,?)",
            (nombre, categoria),
        )
        productos_map[nombre] = cur.lastrowid

    # --- pedidos ---
    cur.execute("""
        SELECT order_id, MIN(order_date), customer_email
        FROM raw_sales
        GROUP BY order_id
    """)
    for order_id, fecha, email in cur.fetchall():
        cur.execute(
            "INSERT INTO pedidos (pedido_id, cliente_id, fecha) VALUES (?,?,?)",
            (order_id, clientes_map[email], fecha),
        )

    # --- detalle_pedido ---
    cur.execute("""
        SELECT order_id, product_name, unit_price, quantity FROM raw_sales
    """)
    for order_id, prod_name, precio, cantidad in cur.fetchall():
        cur.execute(
            """INSERT INTO detalle_pedido (pedido_id, producto_id, precio_unitario, cantidad)
               VALUES (?,?,?,?)""",
            (order_id, productos_map[prod_name], precio, cantidad),
        )

    conn.commit()
    print(f"[normalizado] {len(clientes_map)} clientes, {len(productos_map)} productos")


def crear_indices(conn):
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha);
        CREATE INDEX IF NOT EXISTS idx_detalle_pedido_id ON detalle_pedido(pedido_id);
        CREATE INDEX IF NOT EXISTS idx_detalle_producto_id ON detalle_pedido(producto_id);
        CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_id ON pedidos(cliente_id);
    """)
    conn.commit()
    print("[indices] creados")


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    cargar_raw(conn)
    normalizar(conn)
    crear_indices(conn)
    conn.close()
    print(f"\nListo. Base de datos generada en: {DB_PATH}")


if __name__ == "__main__":
    main() 
