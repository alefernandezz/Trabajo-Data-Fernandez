"""
Genera un dataset crudo y desnormalizado de ventas de e-commerce,
simulando cómo suele llegar la data "cruda" desde un sistema operativo
(todo en una sola tabla plana, con repeticiones).
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

nombres = ["Lucía", "Martín", "Sofía", "Juan", "Camila", "Nicolás", "Valentina",
           "Tomás", "Agustina", "Mateo", "Julieta", "Franco", "Micaela", "Bruno",
           "Florencia", "Ignacio", "Rocío", "Santiago", "Milagros", "Emilio"]
apellidos = ["Gómez", "Rodríguez", "Fernández", "López", "Díaz", "Martínez",
             "Pérez", "Sánchez", "Romero", "Torres", "Flores", "Acosta"]
ciudades = ["Mendoza", "Buenos Aires", "Córdoba", "Rosario", "La Plata", "San Juan"]

productos = [
    ("Mouse inalámbrico", "Periféricos", 8500),
    ("Teclado mecánico", "Periféricos", 32000),
    ("Monitor 24\"", "Monitores", 145000),
    ("Auriculares Bluetooth", "Audio", 21000),
    ("Webcam HD", "Periféricos", 18500),
    ("SSD 1TB", "Almacenamiento", 65000),
    ("Notebook 15\"", "Computadoras", 850000),
    ("Mochila para notebook", "Accesorios", 24000),
    ("Silla ergonómica", "Muebles", 210000),
    ("Hub USB-C", "Periféricos", 12500),
    ("Router WiFi", "Redes", 38000),
    ("Cargador rápido", "Accesorios", 9500),
]

# 60 clientes únicos (para que se repitan pedidos -> clientes recurrentes)
clientes = []
for i in range(60):
    nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
    email = nombre.lower().replace(" ", ".").replace("í", "i").replace("ó", "o") + f"{i}@mail.com"
    clientes.append((nombre, email, random.choice(ciudades)))

rows = []
order_id = 1000
start = date(2025, 1, 1)

for _ in range(650):
    order_id += 1
    cliente = random.choice(clientes)
    order_date = start + timedelta(days=random.randint(0, 269))  # hasta ~sept 2025
    n_items = random.randint(1, 3)
    items = random.sample(productos, n_items)
    for prod_name, categoria, precio in items:
        cantidad = random.randint(1, 4)
        # pequeña variación de precio (descuentos/promos)
        precio_final = round(precio * random.choice([1, 1, 1, 0.9, 0.85]))
        rows.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_name": cliente[0],
            "customer_email": cliente[1],
            "customer_city": cliente[2],
            "product_name": prod_name,
            "category": categoria,
            "unit_price": precio_final,
            "quantity": cantidad,
        })

rows.sort(key=lambda r: (r["order_date"], r["order_id"]))

with open("/home/claude/ventas-analytics/data/raw_sales.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Generadas {len(rows)} filas crudas de {order_id - 1000} pedidos y {len(clientes)} clientes.")
