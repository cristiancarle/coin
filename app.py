from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB = "schoolcoin.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# --- Ruta de inicio ---
@app.route('/')
def index():
    return render_template("base.html")


# --- Docente: asignar coins ---
@app.route('/asignar_coins', methods=['GET','POST'])
def asignar_coins():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        id_estudiante = request.form['id_estudiante']
        trabajo = request.form['trabajo']
        coins = float(request.form['coins'])
        # Registrar entrega y asignar coins
        cur.execute("INSERT INTO entregas (id_estudiante, trabajo, coins_asignados) VALUES (?,?,?)",
                    (id_estudiante, trabajo, coins))
        # Actualizar coins del estudiante
        cur.execute("UPDATE estudiantes SET coins = coins + ? WHERE id=?", (coins, id_estudiante))
        conn.commit()
    cur.execute("SELECT * FROM estudiantes")
    estudiantes = cur.fetchall()
    conn.close()
    return render_template("asignar_coins.html", estudiantes=estudiantes)


# --- Estudiante: consultar saldo ---
@app.route('/saldo/<int:id_estudiante>')
def saldo(id_estudiante):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, coins FROM estudiantes WHERE id=?", (id_estudiante,))
    estudiante = cur.fetchone()
    conn.close()
    return render_template("saldo.html", estudiante=estudiante)


# --- Estudiante: formulario para canjear ---
@app.route('/canjear/<int:id_estudiante>', methods=['GET'])
def canjear_form(id_estudiante):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM estudiantes WHERE id=?", (id_estudiante,))
    estudiante = cur.fetchone()
    conn.close()
    return render_template("canjear.html", estudiante=estudiante)


# --- Estudiante: procesar canje ---
@app.route('/canjear', methods=['POST'])
def canjear():
    id_estudiante = request.form['id_estudiante']
    examen = request.form['examen']
    coins_a_usar = float(request.form['coins'])
    
    conn = get_db()
    cur = conn.cursor()
    # Obtener coins actuales
    cur.execute("SELECT coins FROM estudiantes WHERE id=?", (id_estudiante,))
    coins_actuales = cur.fetchone()['coins']
    
    if coins_a_usar > coins_actuales:
        conn.close()
        return "No tienes suficientes coins"
    
    # Equivalencia: 10 coins = +3 puntos
    puntos = coins_a_usar * 3 / 10
    
    # Actualizar nota del examen
    cur.execute("SELECT * FROM examenes WHERE id_estudiante=? AND examen=?", (id_estudiante, examen))
    examen_existente = cur.fetchone()
    if examen_existente:
        cur.execute("UPDATE examenes SET nota = nota + ? WHERE id_estudiante=? AND examen=?", 
                    (puntos, id_estudiante, examen))
    else:
        cur.execute("INSERT INTO examenes (id_estudiante, examen, nota) VALUES (?,?,?)",
                    (id_estudiante, examen, puntos))
    
    # Restar coins
    cur.execute("UPDATE estudiantes SET coins = coins - ? WHERE id=?", (coins_a_usar, id_estudiante))
    conn.commit()
    conn.close()
    
    return f"Canje realizado: {coins_a_usar} coins usados para aumentar {puntos} puntos en {examen}"


# --- Listar alumnos ---
@app.route('/alumnos')
def listar_alumnos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM estudiantes")
    estudiantes = cur.fetchall()
    conn.close()
    return render_template("listar_alumnos.html", estudiantes=estudiantes)


# --- Cargar nuevo alumno ---
@app.route('/cargar_alumnos', methods=['GET','POST'])
def cargar_alumnos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO estudiantes (nombre, coins) VALUES (?, ?)", (nombre, 0))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_alumnos'))
    return render_template("cargar_alumnos.html")


if __name__ == '__main__':
    app.run(debug=True)
