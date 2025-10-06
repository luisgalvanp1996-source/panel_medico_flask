import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("hospital.db")
cur = conn.cursor()

# Obtener columnas de Rondas
cur.execute("PRAGMA table_info(Rondas)")
columnas = [col[1] for col in cur.fetchall()]

# Lista de nuevas columnas a agregar: (nombre, tipo, valor_por_defecto)
nuevas_columnas = [
    ("ritmo_cardiaco", "INTEGER", 0),
    ("presion_arterial", "TEXT", ""),
    ("oxigeno", "INTEGER", 0),
    ("temperatura", "REAL", 0.0),
    ("respiraciones", "INTEGER", 0)
]

for col, tipo, valor_def in nuevas_columnas:
    if col not in columnas:
        cur.execute(f"ALTER TABLE Rondas ADD COLUMN {col} {tipo} DEFAULT {repr(valor_def)}")
        print(f"Columna '{col}' agregada.")
    else:
        print(f"Columna '{col}' ya existe.")

conn.commit()
conn.close()
