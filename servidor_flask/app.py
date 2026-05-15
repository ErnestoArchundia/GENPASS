from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import secrets
import string
from servidor_flask.modelos import guardar_historial, obtener_historial, borrar_historial, validar_usuario, obtener_usuarios, eliminar_usuario, obtener_estadisticas
from servidor_flask.conexion import conectar_db
from servidor_flask.main import run_scan
from servidor_flask.reportpdf import generate_pdf


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

progress = 0
results_data = []

from threading import  Lock
import threading

scan_lock = Lock()
scan_finished = False


def scan_thread(target):
    global progress, results_data

    def update(p):
        global progress
        progress = p

    results_data = run_scan(target, update)
    progress = 100

@app.route("/scan", methods=["POST"])
def scan():
    global progress
    progress = 0

    target = request.form["target"]

    thread = threading.Thread(target=scan_thread, args=(target,))
    thread.start()

    return jsonify({"status": "scanning"})

@app.route("/progress")
def get_progress():
    global progress
    return jsonify({"progress": progress})

@app.route("/results")
def results():
    global results_data
    return jsonify(results_data)

@app.route("/download")
def download():
    global results_data
    generate_pdf(results_data)

    return jsonify({"status": "pdf generado"})

def shuffle(lista):
    for i in range(len(lista) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        lista[i], lista[j] = lista[j], lista[i]
    return lista

def generar_contraseña(longitud):
    if longitud < 8:
        raise ValueError("La longitud mínima es 8")

    mayus = string.ascii_uppercase
    minus = string.ascii_lowercase
    nums = string.digits
    esp = string.punctuation

    pwd = [
        secrets.choice(mayus),
        secrets.choice(minus),
        secrets.choice(nums),
        secrets.choice(esp)
    ]

    todos = mayus + minus + nums + esp

    for _ in range(longitud - 4):
        pwd.append(secrets.choice(todos))

    return ''.join(shuffle(pwd))

def medir_fuerza(pwd):
    score = 0
    if any(c.islower() for c in pwd): score += 1
    if any(c.isupper() for c in pwd): score += 1
    if any(c.isdigit() for c in pwd): score += 1
    if any(c in string.punctuation for c in pwd): score += 1
    if len(pwd) >= 12: score += 1

    niveles = ["Muy débil", "Débil", "Media", "Segura", "Muy Segura"]
    return niveles[min(score, 4)], score

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        pwd = request.form.get("password")

        data = validar_usuario(user, pwd)

        if data:
            session["user"] = data["usuario"]
            session["rol"] = data["rol"]

            if data["rol"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/")

        else:
            return "Login incorrecto"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", user=session["user"])

@app.route("/generar", methods=["POST"])
def generar_api():
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        cantidad = int(data.get("cantidad", 1))
        longitud = int(data.get("longitud", 10))

        if longitud < 8:
            return jsonify({"error": "La longitud mínima es 8"}), 400

        resultado = []
        user = session["user"]

        for _ in range(cantidad):
            pwd = generar_contraseña(longitud)
            fuerza, score = medir_fuerza(pwd)

            resultado.append({
                "password": pwd,
                "fuerza": fuerza,
                "score": score
            })

            guardar_historial(user, pwd, fuerza, score)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/historial")
def ver_historial():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    data = obtener_historial(user)

    return render_template("historial.html", data=data, user=user)

@app.route("/borrar_historial", methods=["POST"])
def eliminar_historial():
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 403

    user = session["user"]
    borrar_historial(user)

    return jsonify({"mensaje": "Historial eliminado"})

@app.context_processor
def inject_user():
    return dict(
        user=session.get("user"),
        rol=session.get("rol")
    )

@app.route("/admin")
def admin_panel():
    if "user" not in session:
        return redirect("/login")

    if session.get("rol") != "Aministrador":
        return "Acceso restringido", 403

    usuarios = obtener_usuarios()
    stats = obtener_estadisticas()

    return render_template("admin.html", usuarios=usuarios, stats=stats)

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/generator')
def generator():
    return render_template('generator.html')

@app.route('/keylogger')
def keylogger():
    return render_template('keylogger.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':

        user = request.form['user']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Las contraseñas no coinciden")
            return redirect(url_for('registro'))

        conexion = conectar_db()

        if conexion:

            cursor = conexion.cursor()

            try:
                sql = "INSERT INTO usuarios (usuario, password) VALUES (%s, %s)"
                valores = (user, password)

                cursor.execute(sql, valores)
                conexion.commit()

                flash("Usuario registrado correctamente")
                return redirect('/login')

            except Exception as e:
                flash(f"Error: {e}")

            finally:
                cursor.close()
                conexion.close()

    return render_template('registro.html')

@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "user" not in session or session.get("rol") != "Aministrador":
        return jsonify({"error": "No autorizado"}), 403

    eliminar_usuario(user_id)
    return jsonify({"success": True})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)  
