import pyodbc


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


def conectar():
 conn = pyodbc.connect(
     f"DRIVER={{ODBC Driver 17 for SQL Server}};"
     f"SERVER={SERVER};"
     f"DATABASE={DATABASE};"
     f"UID={USER};"
     f"PWD={PASSWORD};"
     "TrustServerCertificate=yes;",
     autocommit=True
 )
 return conn