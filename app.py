from flask import Flask, render_template, request, redirect, url_for, session
# Se usa para: Recuperación de contraseña. Verificación de correos. Links temporales.
from itsdangerous import URLSafeTimedSerializer
# Permite enviar correos electrónicos. Mail Configura el servicio SMTP. Message Construye correos.
from flask_mail import Mail, Message
import bcrypt
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

app.secret_key = "clave_secreta_super_segura"

# Define el dominio principal. que genera URLs completas como: Puerto TLS. Servidor SMTP de Gmail. Activa cifrado TLS. Correo remitente. Contraseña de aplicación de Gmail. (lo hace una red publica pero segura)
app.config["SERVER_NAME"] = "sevenfold-dormitory-emptier.ngrok-free.dev"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "jchuy.avigoku.8z@gmail.com"
app.config["MAIL_PASSWORD"] = "unyg pydi xjmo ysxx"

# Conecta Flask Mail con tu aplicación.
mail = Mail(app)

# Crea un generador de tokens. Sirve para crear enlaces de recuperación.
serializer = URLSafeTimedSerializer(app.secret_key)

# Cadena de conexión.
uri = "mongodb+srv://24308060610607_db_user:J260909c@dmc5.af41dor.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client["mi_app"]

usuarios = db["usuarios"]

comics = db["comics"]

@app.route("/")
def index():

    if "usuario" in session:
        return redirect(url_for("tarjetas"))

    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("inicio_sesion.html")

@app.route("/iniciar", methods=["POST"])
def iniciar():

    usuario = request.form["usuario"].strip().lower()
    password = request.form["password"]

    user = usuarios.find_one({"usuario": usuario})

    if user and bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"]
    ):

        session["usuario"] = usuario

        return redirect(url_for("tarjetas"))

    return render_template(
        "inicio_sesion.html",
        error="Usuario o contrasena incorrectos"
    )

@app.route("/cuenta")
def cuenta():
    return render_template("crear_cuenta.html")

@app.route("/registrar", methods=["POST"])
def registrar():

    usuario = request.form["usuario"].strip().lower()
    password = request.form["password"]

    existe = usuarios.find_one({"usuario": usuario})

    if existe:

        return render_template(
            "crear_cuenta.html",
            error="Ese correo ya esta registrado"
        )

    # VALIDACIÓN DE CONTRASEÑA: Convierte texto a bytes. Compara hash almacenado.
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    fecha = (
        f'{request.form["dia"]}/'
        f'{request.form["mes"]}/'
        f'{request.form["anio"]}'
    )

    nuevo_usuario = {

        "usuario": usuario,

        "password": password_hash,

        "fecha_nacimiento": fecha,

        "genero": request.form["genero"]

    }

    usuarios.insert_one(nuevo_usuario)

    return redirect(url_for("login"))

@app.route("/perfil")
def perfil():

    if "usuario" not in session:
        return redirect(url_for("login"))
# Busca usuario actual.
    user = usuarios.find_one({
        "usuario": session["usuario"]
    })
# Envía datos al HTML.
    return render_template(
        "perfil.html",
        user=user
    )

@app.route("/logout")
def logout():
# Elimina la sesión.
    session.pop("usuario", None)

    return redirect(url_for("login"))

@app.route("/Principal")
def tarjetas():

    if "usuario" not in session:
        return redirect(url_for("login"))
# find() Devuelve cursor. list() Convierte cursor en lista.
    lista_comics = list(comics.find())

    return render_template(
        "comics.html",
        comics=lista_comics
    )

@app.route("/comics")
def comics_page():

    if "usuario" not in session:
        return redirect(url_for("login"))

    lista_comics = list(comics.find({
        "categoria": "comic"
    }))

    return render_template(
        "comics.html",
        comics=lista_comics
    )

@app.route("/mangas")
def mangas_page():

    if "usuario" not in session:
        return redirect(url_for("login"))

    lista_comics = list(comics.find({
        "categoria": "manga"
    }))

    return render_template(
        "mangas.html",
        comics=lista_comics
    )

@app.route("/libros")
def libros_page():

    if "usuario" not in session:
        return redirect(url_for("login"))

    lista_comics = list(comics.find({
        "categoria": "libro"
    }))

    return render_template(
        "libros.html",
        comics=lista_comics
    )

@app.route("/agregar_comic")
def agregar_comic():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template("agregar_comic.html")

@app.route("/guardar_comic", methods=["POST"])
def guardar_comic():

    if "usuario" not in session:
        return redirect(url_for("login"))

    nuevo_comic = {

        "titulo": request.form["titulo"],

        "autor": request.form["autor"],

        "descripcion": request.form["descripcion"],

        "imagen": request.form["imagen"],

        "categoria": request.form["categoria"]

    }

    comics.insert_one(nuevo_comic)

    return redirect(url_for("tarjetas"))

@app.route("/editar_comic/<id>", methods=["GET", "POST"])
# Obtiene ID:
def editar_comic(id):

    if "usuario" not in session:
        return redirect(url_for("login"))
# Busca documento:
    comic = comics.find_one({
        "_id": ObjectId(id)
    })

    if not comic:
        return "Comic no encontrado"

    if request.method == "POST":

        comics.update_one(

            {"_id": ObjectId(id)},

            {"$set": {

                "titulo": request.form["titulo"],

                "autor": request.form["autor"],

                "descripcion": request.form["descripcion"]

            }}

        )

        return redirect(url_for("tarjetas"))

    return render_template(
        "editar_comic.html",
        comic=comic
    )

@app.route("/eliminar_comic/<id>")
def eliminar_comic(id):

    if "usuario" not in session:
        return redirect(url_for("login"))

    comics.delete_one({
        "_id": ObjectId(id)
    })

    return redirect(url_for("tarjetas"))

@app.route("/cambiar_password", methods=["GET", "POST"])
def cambiar_password():

    if request.method == "POST":

        correo = request.form["correo"].strip().lower()

        user = usuarios.find_one({
            "usuario": correo
        })

        if not user:

            return render_template(
                "cambiar_password.html",
                error="Correo no encontrado"
            )

        token = serializer.dumps(
            correo,
            salt="recuperar-password"
        )

        link = url_for(
            "reset_password",
            token=token,
            _external=True
        )

        mensaje = Message(
            subject="Recuperacion de contrasena",
            sender=app.config["MAIL_USERNAME"],
            recipients=[correo]
        )

        mensaje.body = f"""
Hola.

Da clic en el siguiente enlace para recuperar tu contrasena:

{link}

Si no solicitaste esto, ignora este mensaje.
"""

        mail.send(mensaje)

        return render_template(
            "cambiar_password.html",
            mensaje="Correo enviado exitosamente"
        )

    return render_template("cambiar_password.html")

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):

    try:

        correo = serializer.loads(
            token,
            salt="recuperar-password",
            max_age=3600
        )

    except:
        return "El enlace expiro o es invalido"

    if request.method == "POST":

        nueva_password = request.form["password"]

        password_hash = bcrypt.hashpw(
            nueva_password.encode("utf-8"),
            bcrypt.gensalt()
        )

        usuarios.update_one(
            {"usuario": correo},
            {"$set": {"password": password_hash}}
        )

        return redirect(url_for("login"))

    return render_template(
        "reset_password.html",
        token=token
    )

@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():

    if "usuario" not in session:
        return redirect(url_for("login"))

    user = usuarios.find_one({
        "usuario": session["usuario"]
    })

    if request.method == "POST":

        nueva_fecha = (
            f'{request.form["dia"]}/'
            f'{request.form["mes"]}/'
            f'{request.form["anio"]}'
        )

        usuarios.update_one(

            {"usuario": session["usuario"]},

            {"$set": {

                "fecha_nacimiento": nueva_fecha,

                "genero": request.form["genero"]

            }}

        )

        return redirect(url_for("perfil"))

    return render_template(
        "editar_perfil.html",
        user=user
    )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
