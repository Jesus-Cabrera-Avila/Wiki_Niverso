from flask import (
    Flask,
    request,
    url_for,
    redirect,
    render_template,
    session
)

from flask_mail import Mail, Message
from itsdangerous import (
    URLSafeTimedSerializer,
    SignatureExpired,
    BadSignature
)

import bcrypt

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

serializer = URLSafeTimedSerializer(app.secret_key)

uri = "mongodb+srv://24308060610607_db_user:J260909c@dmc5.af41dor.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client["mi_app"]

usuarios = db["usuarios"]

@app.route("/")
def index():
    return redirect("/login")

@app.route("/perfil")
def perfil():

    if "usuario" not in session:
        return redirect("/login")

    user = usuarios.find_one({
        "usuario": session["usuario"]
    })

    return render_template(
        "perfil.html",
        user=user
    )

@app.route("/login")
def login():
    return render_template("inicio_sesion.html")

@app.route("/cuenta")
def cuenta():
    return render_template("crear_cuenta.html")

@app.route("/cambiar_password", methods=["GET", "POST"])
def cambiar_password():

    if request.method == "POST":

        correo = request.form["correo"].strip().lower()

        user = usuarios.find_one({
            "usuario": correo
        })

        if user:

            token = serializer.dumps(
                correo,
                salt="cambiar-password"
            )

            link = url_for(
                "reset_password",
                token=token,
                _external=True
            )

            msg = Message(
                "Cambiar contraseña",
                recipients=[correo]
            )

            msg.body = f"""
Hola.

Haz clic en el siguiente enlace para cambiar tu contraseña:

{link}

Este enlace expira en 15 minutos.
"""

            mail.send(msg)

            return render_template(
                "cambiar_password.html",
                mensaje="Correo enviado correctamente"
            )

        else:

            return render_template(
                "cambiar_password.html",
                error="Ese correo no está registrado"
            )

    return render_template("cambiar_password.html")

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):

    try:

        correo = serializer.loads(
            token,
            salt="cambiar-password",
            max_age=900
        )

    except SignatureExpired:
        return "El enlace expiró"

    except BadSignature:
        return "Token inválido"

    if request.method == "POST":

        nueva_password = request.form["password"]

        password_encriptada = bcrypt.hashpw(
            nueva_password.encode("utf-8"),
            bcrypt.gensalt()
        )

        usuarios.update_one(
            {"usuario": correo},
            {
                "$set": {
                    "password": password_encriptada
                }
            }
        )

        return redirect("/login")

    return render_template("nueva_password.html")

@app.route("/registrar", methods=["POST"])
def registrar():

    usuario = request.form["usuario"].strip().lower()

    password = request.form["password"]

    dia = request.form["dia"]
    mes = request.form["mes"]
    anio = request.form["anio"]

    genero = request.form.get("genero")

    user_existente = usuarios.find_one({
        "usuario": usuario
    })

    if user_existente:

        return render_template(
            "crear_cuenta.html",
            error="Este correo ya está registrado"
        )

    password_encriptada = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    usuarios.insert_one({

        "usuario": usuario,

        "password": password_encriptada,

        "fecha_nacimiento": f"{dia}/{mes}/{anio}",

        "genero": genero
    })

    return redirect("/login")

@app.route("/iniciar", methods=["POST"])
def iniciar():

    usuario = request.form["usuario"].strip().lower()

    password = request.form["password"]

    user = usuarios.find_one({
        "usuario": usuario
    })

    if user and bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"]
    ):

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