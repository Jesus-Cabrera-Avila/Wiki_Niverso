from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
from pymongo import MongoClient

app = Flask(__name__)

app.secret_key = "clave_secreta_super_segura"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'jchuy.avigoku.8z@gmail.com'

app.config['MAIL_PASSWORD'] = 'cjlj nimo qmna budf'

app.config['MAIL_DEFAULT_SENDER'] = 'jchuy.avigoku.8z@gmail.com'

mail = Mail(app)

uri = "mongodb+srv://24308060610607_db_user:J260909c@dmc5.af41dor.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client["mi_app"]

usuarios = db["usuarios"]

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/perfil")
def perfil():

    if "usuario" not in session:
        return redirect("/login")

    user = usuarios.find_one({"usuario": session["usuario"]})

    return render_template("perfil.html", user=user)


@app.route("/login")
def login():
    return render_template("inicio_sesion.html")


@app.route("/cuenta")
def cuenta():
    return render_template("crear_cuenta.html")

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":

        correo = request.form["correo"].strip().lower()

        user = usuarios.find_one({"usuario": correo})

        if user:

            msg = Message(
                "Recuperar contraseña",
                recipients=[correo]
            )

            msg.body = f"""
Hola.

Solicitaste recuperar tu contraseña.

Tu contraseña es:

{user['password']}
"""

            mail.send(msg)

            return render_template(
                "recuperar_contraseña.html",
                mensaje="Correo enviado correctamente"
            )

        else:

            return render_template(
                "recuperar_contraseña.html",
                error="Ese correo no está registrado"
            )

    return render_template("recuperar_contraseña.html")

@app.route("/registrar", methods=["POST"])
def registrar():

    usuario = request.form["usuario"].strip().lower()

    password = request.form["password"]

    dia = request.form["dia"]
    mes = request.form["mes"]
    anio = request.form["anio"]

    genero = request.form.get("genero")

    user_existente = usuarios.find_one({"usuario": usuario})

    if user_existente:

        return render_template(
            "crear_cuenta.html",
            error="Este correo ya está registrado"
        )

    usuarios.insert_one({
        "usuario": usuario,
        "password": password,
        "fecha_nacimiento": f"{dia}/{mes}/{anio}",
        "genero": genero
    })

    return redirect("/login")

@app.route("/iniciar", methods=["POST"])
def iniciar():

    usuario = request.form["usuario"].strip().lower()

    password = request.form["password"]

    user = usuarios.find_one({"usuario": usuario})

    if user and user["password"] == password:

        session["usuario"] = usuario

        return redirect("/perfil")

    else:

        return render_template(
            "inicio_sesion.html",
            error="Usuario o contraseña incorrectos"
        )

@app.route("/logout")
def logout():

    session.pop("usuario", None)

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)