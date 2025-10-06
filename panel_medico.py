import sqlite3
from datetime import datetime

DB = "hospital.db"

def conectar():
    conn = sqlite3.connect(DB)
    return conn

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

# === CRUD Pacientes ===
def agregar_paciente():
    nombre = input("Nombre del paciente: ")
    edad = int(input("Edad: "))
    sexo = input("Sexo (M/F): ")
    diagnostico = input("Diagnóstico: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO Pacientes (nombre, edad, sexo, diagnostico) VALUES (?, ?, ?, ?)",
                (nombre, edad, sexo, diagnostico))
    conn.commit()
    conn.close()
    print("✅ Paciente agregado correctamente.\n")

def listar_pacientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pacientes")
    pacientes = cur.fetchall()
    conn.close()
    print("\n📋 Lista de Pacientes:")
    for p in pacientes:
        print(f"ID: {p[0]} | Nombre: {p[1]} | Edad: {p[2]} | Sexo: {p[3]} | Diagnóstico: {p[4]}")
    print()

def modificar_paciente():
    listar_pacientes()
    idp = int(input("ID del paciente a modificar: "))
    campo = input("Campo a modificar (nombre/edad/sexo/diagnostico): ")
    valor = input("Nuevo valor: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"UPDATE Pacientes SET {campo} = ? WHERE id = ?", (valor, idp))
    conn.commit()
    conn.close()
    print("✅ Paciente modificado.\n")

# === CRUD Médicos ===
def agregar_medico():
    nombre = input("Nombre del médico: ")
    especialidad = input("Especialidad: ")
    telefono = input("Teléfono: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO Medicos (nombre, especialidad, telefono) VALUES (?, ?, ?)",
                (nombre, especialidad, telefono))
    conn.commit()
    conn.close()
    print("✅ Médico agregado.\n")

def listar_medicos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Medicos")
    medicos = cur.fetchall()
    conn.close()
    print("\n👨‍⚕️ Lista de Médicos:")
    for m in medicos:
        print(f"ID: {m[0]} | Nombre: {m[1]} | Especialidad: {m[2]} | Tel: {m[3]}")
    print()

# === Rondas ===
def agregar_ronda():
    listar_pacientes()
    id_paciente = int(input("ID del paciente: "))
    listar_medicos()
    id_medico = int(input("ID del médico: "))
    observaciones = input("Observaciones: ")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO Rondas (id_paciente, id_medico, fecha, observaciones) VALUES (?, ?, ?, ?)",
                (id_paciente, id_medico, fecha, observaciones))
    conn.commit()
    conn.close()
    print("✅ Ronda registrada.\n")

def listar_rondas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute('''
        SELECT R.id, P.nombre, M.nombre, R.fecha, R.observaciones
        FROM Rondas R
        JOIN Pacientes P ON R.id_paciente = P.id
        JOIN Medicos M ON R.id_medico = M.id
    ''')
    rondas = cur.fetchall()
    conn.close()
    print("\n🩺 Rondas Médicas:")
    for r in rondas:
        print(f"ID: {r[0]} | Paciente: {r[1]} | Médico: {r[2]} | Fecha: {r[3]} | Obs: {r[4]}")
    print()

# === Menú principal ===
def menu():
    crear_tablas()
    while True:
        print("=== PANEL MÉDICO ===")
        print("1. Agregar paciente")
        print("2. Listar pacientes")
        print("3. Modificar paciente")
        print("4. Agregar médico")
        print("5. Listar médicos")
        print("6. Registrar ronda")
        print("7. Listar rondas")
        print("0. Salir")
        op = input("Seleccione una opción: ")
        if op == "1": agregar_paciente()
        elif op == "2": listar_pacientes()
        elif op == "3": modificar_paciente()
        elif op == "4": agregar_medico()
        elif op == "5": listar_medicos()
        elif op == "6": agregar_ronda()
        elif op == "7": listar_rondas()
        elif op == "0": break
        else: print("Opción inválida.\n")

if __name__ == "__main__":
    menu()
