from flask import Flask, render_template, request, redirect, url_for, send_from_directory,jsonify,request
import sqlite3
from datetime import datetime
from funtions import *
import locale



app = Flask(__name__)



@app.route('/paciente/<int:id_paciente>/cambiar_estatus', methods=['POST'])
def cambiar_estatus(id_paciente):
    nuevo_estatus = request.form.get('estatus')
    if nuevo_estatus not in ['activo', 'alta', 'por ingresar']:
        return "Estatus inválido", 400

    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE Pacientes SET estatus = ? WHERE id = ?", (nuevo_estatus, id_paciente))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/rondas/paciente/<int:id_paciente>')
def rondas_por_paciente(id_paciente):
    conn = conectar()
    cur = conn.cursor()
    cur.execute('''
        SELECT fecha, observaciones, ritmo_cardiaco, presion_arterial, oxigeno, temperatura, respiraciones
        FROM Rondas
        WHERE id_paciente = ?
        ORDER BY fecha DESC
    ''', (id_paciente,))
    rondas = cur.fetchall()
    conn.close()

    result = []
    for r in rondas:
        fecha = r[0]
        # Convertir a datetime
        if isinstance(fecha, str):
            try:
                fecha_dt = datetime.fromisoformat(fecha)
            except:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        else:
            fecha_dt = fecha

        fecha_formateada = f"{fecha_dt.day:02d} {MESES_ES[fecha_dt.month]} {fecha_dt.hour:02d}:{fecha_dt.minute:02d}"

        result.append({
            "fecha": fecha_formateada,
            "observaciones": r[1],
            "ritmo_cardiaco": r[2],
            "presion_arterial": r[3],
            "oxigeno": r[4],
            "temperatura": r[5],
            "respiraciones": r[6]
        })

    return jsonify(result)

@app.route('/')
def index():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM Pacientes")
    pacientes = cur.fetchall()
    conn.close()
    return render_template('index.html', pacientes=pacientes)


# ==== Pacientes ====
@app.route('/pacientes')
def pacientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pacientes")
    data = cur.fetchall()
    conn.close()
    return render_template('pacientes.html', pacientes=data)

@app.route('/pacientes/agregar', methods=['POST'])
def agregar_paciente():
    nombre = request.form['nombre']
    edad = request.form['edad']
    sexo = request.form['sexo']
    diagnostico = request.form['diagnostico']
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO Pacientes (nombre, edad, sexo, diagnostico) VALUES (?, ?, ?, ?)",
                (nombre, edad, sexo, diagnostico))
    conn.commit()
    conn.close()
    return redirect(url_for('pacientes'))

@app.route('/pacientes/eliminar/<int:id>')
def eliminar_paciente(id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM Pacientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('pacientes'))

# ==== Médicos ====
@app.route('/medicos')
def medicos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Medicos")
    data = cur.fetchall()
    conn.close()
    return render_template('medicos.html', medicos=data)

@app.route('/medicos/agregar', methods=['POST'])
def agregar_medico():
    nombre = request.form['nombre']
    especialidad = request.form['especialidad']
    telefono = request.form['telefono']
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO Medicos (nombre, especialidad, telefono) VALUES (?, ?, ?)",
                (nombre, especialidad, telefono))
    conn.commit()
    conn.close()
    return redirect(url_for('medicos'))

@app.route('/medicos/eliminar/<int:id>')
def eliminar_medico(id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM Medicos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('medicos'))

@app.route('/rondas')
def rondas():
    conn = conectar()
    cur = conn.cursor()
    
    # Traer todas las rondas con los signos vitales
    cur.execute('''
        SELECT R.id, P.nombre, M.nombre, R.fecha, R.observaciones,
               R.ritmo_cardiaco, R.presion_arterial, R.oxigeno,
               R.temperatura, R.respiraciones
        FROM Rondas R
        JOIN Pacientes P ON R.id_paciente = P.id
        JOIN Medicos M ON R.id_medico = M.id
        ORDER BY R.fecha DESC
    ''')
    rondas_raw = cur.fetchall()

    # Formatear la fecha y preparar lista
    rondas_list = []
    for r in rondas_raw:
        fecha_str = r[3]
        try:
            fecha_dt = datetime.fromisoformat(fecha_str)
        except:
            fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
        fecha_formateada = f"{fecha_dt.day:02d} {MESES_ES[fecha_dt.month]} {fecha_dt.hour:02d}:{fecha_dt.minute:02d}"

        rondas_list.append((
            r[0], r[1], r[2], fecha_formateada, r[4], r[5], r[6], r[7], r[8], r[9]
        ))

    # Pacientes y médicos para el formulario
    cur.execute("SELECT id, nombre FROM Pacientes")
    pacientes = cur.fetchall()
    cur.execute("SELECT id, nombre FROM Medicos")
    medicos = cur.fetchall()

    conn.close()
    return render_template('rondas.html', rondas=rondas_list, pacientes=pacientes, medicos=medicos)

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('.', 'service-worker.js')

@app.route('/rondas/agregar', methods=['POST'])
def agregar_ronda():
    id_paciente = request.form['id_paciente']
    id_medico = request.form['id_medico']
    observaciones = request.form.get('observaciones', '')
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Capturar nuevos campos de signos vitales
    try:
        ritmo_cardiaco = int(request.form.get('ritmo_cardiaco', 0))
    except ValueError:
        ritmo_cardiaco = 0

    presion_arterial = request.form.get('presion_arterial', '')

    try:
        oxigeno = int(request.form.get('oxigeno', 0))
    except ValueError:
        oxigeno = 0

    try:
        temperatura = float(request.form.get('temperatura', 0.0))
    except ValueError:
        temperatura = 0.0

    try:
        respiraciones = int(request.form.get('respiraciones', 0))
    except ValueError:
        respiraciones = 0

    # Guardar en la base de datos
    conn = conectar()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO Rondas (
            id_paciente, id_medico, fecha, observaciones,
            ritmo_cardiaco, presion_arterial, oxigeno, temperatura, respiraciones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_paciente, id_medico, fecha, observaciones,
          ritmo_cardiaco, presion_arterial, oxigeno, temperatura, respiraciones))
    conn.commit()
    conn.close()

    return redirect(url_for('rondas'))


@app.route('/rondas/eliminar/<int:id>')
def eliminar_ronda(id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM Rondas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('rondas'))

@app.route('/')
def home():
    user_agent = request.headers.get('User-Agent')
    print(user_agent)  # 👉 imprime en la consola del servidor
    return f"Tu User-Agent es: {user_agent}"

if __name__ == '__main__':
    #crear_tablas()

#    conn = conectar()
#    cur = conn.cursor()
#    cur.execute("SELECT name FROM sys.tables")
#    print("Tablas en la base de datos:")
#    for row in cur.fetchall():
#        print("-", row[0])
#    conn.close()

    app.run(host='0.0.0.0', port=5000, debug=True)

