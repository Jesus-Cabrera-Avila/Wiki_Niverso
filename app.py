from flask import Flask, render_template, request, redirect, url_for, session
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import bcrypt
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

app.secret_key = "clave_secreta_super_segura"

app.config["SERVER_NAME"] = "sevenfold-dormitory-emptier.ngrok-free.dev"

uri = "mongodb+srv://24308060610607_db_user:J260909c@dmc5.af41dor.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client["mi_app"]

usuarios = db["usuarios"]

comics = db["comics"]

serializer = URLSafeTimedSerializer(app.secret_key)

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login")
def login():
    return render_template("inicio_sesion.html")

@app.route("/iniciar", methods=["POST"])
def iniciar():

    usuario = request.form["usuario"].strip().lower()
    password = request.form["password"]

    user = usuarios.find_one({"usuario": usuario})

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):

        session["usuario"] = usuario

        return redirect(url_for("tarjetas"))

    return render_template("inicio_sesion.html", error="Usuario o contraseña incorrectos")

@app.route("/Principal")
def tarjetas():

    if "usuario" not in session:
        return redirect("/login")

    lista_comics = list(comics.find())

    return render_template("necxo.html", comics=lista_comics)

@app.route("/agregar_comic")
def agregar_comic():

    if "usuario" not in session:
        return redirect("/login")

    return render_template("agregar_comic.html")

@app.route("/guardar_comic", methods=["POST"])
def guardar_comic():

    if "usuario" not in session:
        return redirect("/login")

    nuevo_comic = {
        "titulo": request.form["titulo"],
        "autor": request.form["autor"],
        "descripcion": request.form["descripcion"]
    }

    comics.insert_one(nuevo_comic)

    return redirect(url_for("tarjetas"))

@app.route("/editar_comic/<id>", methods=["GET", "POST"])
def editar_comic(id):

    if "usuario" not in session:
        return redirect("/login")

    comic = comics.find_one({"_id": ObjectId(id)})

    if request.method == "POST":

        titulo = request.form["titulo"]
        autor = request.form["autor"]
        descripcion = request.form["descripcion"]

        comics.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "titulo": titulo,
                "autor": autor,
                "descripcion": descripcion
            }}
        )

        return redirect(url_for("tarjetas"))

    return render_template("editar_comic.html", comic=comic)

@app.route("/logout")
def logout():

    session.pop("usuario", None)

    return redirect("/login")

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)