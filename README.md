# Ventas Analytics — mini plataforma de análisis de ventas

Proyecto personal para practicar modelado de datos, SQL y un flujo de
datos end-to-end: desde un CSV crudo hasta un reporte que cualquier
persona no técnica puede consumir.

## ¿Qué hace?

1. **Genera/recibe data cruda** (`data/raw_sales.csv`): un dataset simulado
   de ventas de e-commerce, desnormalizado, tal como suele llegar desde
   un sistema operativo real.
2. **Modela y refactoriza** esa data en un esquema relacional normalizado
   (`clientes`, `productos`, `pedidos`, `detalle_pedido`) — ver
   [`sql/01_schema_raw.sql`](sql/01_schema_raw.sql) y
   [`sql/02_schema_normalizado.sql`](sql/02_schema_normalizado.sql).
3. **Corre un ETL en Python** (`etl/load_and_refresh.py`) que carga el CSV,
   lo transforma y puebla el esquema normalizado. Es idempotente: se puede
   correr varias veces sin duplicar datos.
4. **Analiza los datos con SQL** (`sql/03_queries_analisis.sql`): ventas
   por mes, top productos, clientes recurrentes, ranking de pedidos con
   funciones de ventana, cruce ciudad x categoría.
5. **Documenta un caso real de tuning** (`sql/04_optimizacion.sql`): antes
   y después de agregar índices, con la salida real de `EXPLAIN QUERY PLAN`.
6. **Genera un producto de datos self-service** (`etl/generar_reporte.py`):
   un Excel con hojas separadas para que cualquier persona de otro equipo
   (comercial, marketing) lo abra sin tocar SQL.

## Por qué estas decisiones

- **SQLite** en vez de un servidor MySQL/PostgreSQL: cero instalación,
  el archivo `ventas.db` se genera solo. El SQL usado es prácticamente
  portable 1:1 a MySQL o PostgreSQL (la única diferencia real es
  `AUTOINCREMENT` vs `AUTO_INCREMENT` / `IDENTITY`).
- **Normalización explícita en dos pasos** (crudo → modelado): para dejar
  documentado el razonamiento de diseño, no solo el resultado final.
- **Evidencia real de optimización**, no solo la teoría: se corrió la
  query antes y después de crear los índices y se citó la salida real
  del plan de ejecución.

## Cómo correrlo

```bash
# 1. (Opcional) Regenerar el dataset crudo
python3 data/generate_data.py

# 2. Cargar y normalizar en la base de datos
python3 etl/load_and_refresh.py

# 3. Generar el reporte Excel
python3 etl/generar_reporte.py
```

Requiere Python 3 con `pandas` y `openpyxl` (`pip install pandas openpyxl`).

## Posibles próximos pasos

- Migrar el esquema a PostgreSQL con Docker para practicar el motor real.
- Agregar tests automáticos que validen la integridad referencial después del ETL.
- Programar el ETL con un scheduler simple (cron / Airflow) para simular
  un refresh periódico real.

## Stack

Python 3 · SQLite · SQL (DDL, joins, agregaciones, funciones de ventana,
`EXPLAIN QUERY PLAN`) · pandas · openpyxl
