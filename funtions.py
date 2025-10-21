import pyodbc
import platform
import os
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')


SINCROTABLES = {
    "Rondas"
}

MESES_ES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

def crear_tablas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            edad INTEGER,
            sexo TEXT,
            diagnostico TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            especialidad TEXT,
            telefono TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Rondas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER,
            id_medico INTEGER,
            fecha TEXT,
            observaciones TEXT,
            FOREIGN KEY(id_paciente) REFERENCES Pacientes(id),
            FOREIGN KEY(id_medico) REFERENCES Medicos(id)
        )
    ''')
    conn.commit()
    conn.close()



SERVER = "SERVER404\\SERVERHOME"
DATABASE = "hospital"
USER = "sa"
PASSWORD = "Luis1996@@"
SQLITE_PATH = "hospital.db"


# --- 1️⃣ Verificar si el servidor SQL responde ---
def ping_sqlserver(server):
    """
    Hace ping al host (nivel de red).
    Retorna True si responde, False si no.
    """
    host = server.split("\\")[0]  # elimina la instancia si existe (por ejemplo, SERVER404)
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]

    print(f" Haciendo ping a {host} ...")
    respuesta = os.system(" ".join(command)) == 0
    if respuesta:
        print(" El servidor responde al ping.")
    else:
        print(" No se pudo hacer ping al servidor.")
    return respuesta


# --- 2️⃣ Intentar conexión a SQL Server ---
def conectar_sqlserver():
    """
    Intenta conectarse al SQL Server principal.
    Retorna la conexión si tiene éxito, None si falla.
    """
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={USER};"
            f"PWD={PASSWORD};"
            "TrustServerCertificate=yes;",
            autocommit=True,
            timeout=3
        )
        print(" Conectado a SQL Server correctamente.")
        return conn
    except Exception as e:
        print(f" Error al conectar a SQL Server: {e}")
        return None


# --- 3️⃣ Conectar (o crear) base SQLite local ---
def conectar_sqlite():
    """
    Conecta a la base SQLite local.
    Crea el archivo si no existe.
    """
    try:
        conn = sqlite3.connect(SQLITE_PATH)
        print(f" Conectado a la base SQLite local ({SQLITE_PATH}).")
        return conn
    except Exception as e:
        print(f" Error al conectar a SQLite: {e}")
        return None


# --- 4️⃣ Función principal que elige automáticamente ---
def conectar():
    """
    Verifica si el servidor SQL responde y permite conectar.
    Si no responde o la conexión falla, usa SQLite local.
    Retorna la conexión activa (SQL Server o SQLite).
    """
    print(" Verificando conexión al servidor SQL...")

    if ping_sqlserver(SERVER):
        conn = conectar_sqlserver()
        if conn:
            print(" Usando conexión a SQL Server.")
            return conn

    print(" Usando base de datos local SQLite como respaldo...")
    return conectar_sqlite()



def sincronizar_tablas():
    """
    Si hay conexión al servidor SQL, copia los registros
    de las tablas en SINCROTABLES desde SQLite hacia SQL Server
    y luego limpia las tablas locales.
    """
    print("🔍 Verificando conexión con SQL Server...")
    if not ping_sqlserver(SERVER):
        print(" No hay conexión de red con el servidor SQL.")
        return

    sql_conn = conectar_sqlserver()
    if not sql_conn:
        print(" No se pudo conectar al SQL Server.")
        return

    sqlite_conn = conectar_sqlite()
    if not sqlite_conn:
        print(" No se pudo conectar a la base SQLite local.")
        return

    sql_cursor = sql_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()

    for table in SINCROTABLES:
        print(f"\n Sincronizando tabla '{table}' ...")

        try:
            # Obtener todas las filas de la tabla local
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()

            if not rows:
                print(f" No hay registros nuevos en {table}.")
                continue

            # Obtener los nombres de las columnas desde SQLite
            columnas = [desc[0] for desc in sqlite_cursor.description]
            placeholders = ", ".join(["?"] * len(columnas))
            columnas_sql = ", ".join(columnas)

            # Insertar los registros en SQL Server
            insert_query = f"INSERT INTO {table} ({columnas_sql}) VALUES ({placeholders})"
            sql_cursor.fast_executemany = True
            sql_cursor.executemany(insert_query, rows)
            sql_conn.commit()

            print(f" {len(rows)} registros insertados en SQL Server para '{table}'.")

            # Eliminar datos locales ya sincronizados
            sqlite_cursor.execute(f"DELETE FROM {table}")
            sqlite_conn.commit()
            print(f"🧹 Datos locales de '{table}' eliminados en SQLite.")

        except Exception as e:
            print(f" Error sincronizando la tabla {table}: {e}")

    sqlite_conn.close()
    sql_conn.close()
    print("\n Sincronización completada correctamente.")