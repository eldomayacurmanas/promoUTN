import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import webbrowser

from helpers import login_required, promo_required, admin_required, checkwellnes, chequearvotos, restarles


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///promoutn.db")


@app.route("/")
def index():

    if session.get("user_id") is None:
        userdata = {"tipo": "invitado", "id": "invitado"}
    else:
        userdata = db.execute(
            "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]
    promos = db.execute('''SELECT usuarios.id AS id, usuarios.nombre AS nombre, usuarios.tipo AS tipo, promos.instagram AS instagram, promos.foto AS foto, promos.seguidores AS seguidores
                                FROM usuarios INNER JOIN promos
                                ON usuarios.id=promos.userid
                                WHERE tipo in ('PROMO','SOLICITANTE')
                                ORDER BY seguidores DESC''')
    mensajes = db.execute('''SELECT annmsj.msjid AS msjid, usuarios.nombre AS emisor, usuarios.tipo AS tipo, annmsj.mensaje AS mensaje, annmsj.hora AS hora
                                    FROM usuarios INNER JOIN annmsj
                                    ON usuarios.id=annmsj.userid
                                    ORDER BY hora ''')
    jodas = db.execute(
        '''SELECT jodaid, nombre, descripcion, ubicacion, fecha, estado FROM jodas''')
    userdata["estaEn"] = []
    for li in db.execute("SELECT jodaid FROM listas WHERE userid=?", userdata["id"]):
        userdata["estaEn"].append(li["jodaid"])

    return render_template("index.html", userdata=userdata, anonyms=mensajes, promos=promos, jodas=jodas)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("provea nombre de usuario")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("provea contraseña")
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM usuarios WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("nombre de usuaruio o contraseña incorrectos")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# /logout
# logs the user out
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# /register


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checking
        if not request.form.get("nombre"):
            flash("provea nombre completo")
            return redirect("/register")

        elif not request.form.get("username"):
            flash("provea nombre de usuario")
            return redirect("/register")

        elif not request.form.get("password"):
            flash("provea contraseña")
            return redirect("/register")

        elif not request.form.get("confirmation"):
            flash("confirmar contraseña!")
            return redirect("/register")

        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("confirmacion invalida, no concuerdan las contraseñas")
            return redirect("/register")

        userswiththatname = db.execute(
            "SELECT * FROM usuarios WHERE username = ?", request.form.get("username"))
        try:
            userswiththatname = userswiththatname[0]["username"]
        except:
            userswiththatname = None
        if userswiththatname != None:
            flash("nombre de usuario ya esta en uso")
            return redirect("/register")

        message = checkwellnes(request.form.get("password"))
        if message != "ok":
            flash(message)
            return redirect("/register")

        db.execute("INSERT INTO usuarios (nombre, username, password) VALUES ( ? , ? , ? )", request.form.get(
            "username"), request.form.get("username"), generate_password_hash(request.form.get("password")))

        return redirect("/")

    else:

        return render_template("register.html")


# /solicitar
    # solicitar promo
        # cargarle a b.d. promos los datos: userid, link instagram, link foto
        # updatearle a bd usuarios columna tipo: normal->solicitante
@app.route("/solicitar", methods=["GET", "POST"])
@login_required
def solicitarpromo():
    if request.method == "POST":
        userid = session.get("user_id")
        if not request.form.get("instagram"):
            flash("completar todas las casillas")
            return redirect("/solicitar", 403)
        insta = request.form.get("instagram")
        if not request.form.get("foto"):
            flash("completar todas las casillas")
            return redirect("/solicitar", 403)
        foto = request.form.get("foto")

        db.execute(
            "INSERT INTO promos (userid, instagram, foto, seguidores) VALUES (?, ?, ?, ?)", userid, insta, foto, 0)
        db.execute("UPDATE usuarios SET tipo='SOLICITANTE' WHERE id=?", userid)

        flash("solicitud enviada!")
        return redirect("/")
    else:
        userdata = db.execute(
            "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]
        return render_template("solicitar.html", userdata=userdata)


# /confirmar
# adminrequired
    # confirmar promo
        # updatearle a b.d. promos el dato seguidores: 0 -> request.form.get("seguidores")
        # updatearle a b.d. usuarios el dato tipo: solicitante -> promo
@app.route("/confirmar", methods=["POST"])
@admin_required
def confirmar():
    promoid = request.form.get("promoid")
    if not request.form.get("seguidores"):
        flash("completar todas las casillas")
        return redirect("/index", 403)
    seguidores = request.form.get("seguidores")

    db.execute("UPDATE promos SET seguidores = ? WHERE userid= ?",
               seguidores, promoid)
    db.execute("UPDATE usuarios SET tipo = 'PROMO' WHERE id = ?", promoid)

    flash("promo confirmado")
    return redirect("/")


# /eliminarpromo
# adminrequired
    # dropear en b.d. promos la row con el userid = promo["id"]
    # updatear en b.d. usuarios el dato tipo: promo -> normal
@app.route("/eliminarpromo", methods=["POST"])
@admin_required
def eliminarpromo():
    if not request.form.get("promoid"):
        flash("falta id de promo")
        return redirect("/")
    promoid = request.form.get("promoid")

    db.execute("DELETE FROM promos WHERE userid = ?", promoid)
    db.execute("UPDATE usuarios SET tipo = 'normal' WHERE id = ?", promoid)

    return redirect("/")


@app.route("/anonnyms", methods=["POST"])
@login_required
def sendmsj():
    if request.method == "POST":
        # submit msj
        if not request.form.get("mensaje"):
            flash("ingrese mensaje para enviar")
            return redirect("/")

        userid = session.get("user_id")
        mensaje = request.form.get("mensaje")
        hora = datetime.datetime.now()

        db.execute(
            "INSERT INTO annmsj (userid, mensaje, hora) VALUES (?, ?, ?)", userid, mensaje, hora)

        return redirect("/")

# /eliminarmsj


@app.route("/eliminarmsj", methods=["POST"])
@admin_required
def eliminarmsj():
    if not request.form.get("msjid"):
        flash("missing msj id")
        return redirect("/")
    msjid = request.form.get("msjid")

    db.execute("DELETE FROM annmsj WHERE msjid=?", msjid)

    flash("mensaje eliminado correctamente")
    return redirect("/")


# /jodas__alistarse
    # ponerse en lista de una joda
@app.route("/jodas__alistarse", methods=["GET", "POST"])
@login_required
def alistarse():
    if request.method == "POST":

        jodaid = request.form.get("jodaid")

        # si la lista esta llena se rechaza el intento
        joda = db.execute(
            "SELECT capacidad , precio FROM jodas WHERE jodaid = ?", jodaid)[0]
        confirmados = len(db.execute(
            "SELECT * FROM listas WHERE jodaid = ?", jodaid))
        if confirmados >= joda["capacidad"]:
            flash("lista llena!")
            return redirect("/")

        userid = session.get("user_id")
        userdata = db.execute(
            "SELECT cash , tipo FROM usuarios WHERE id = ?", userid)[0]

        # si no le alcanza la entrada y es cuenta normal se rechaza el intento
        if userdata["cash"] < joda["precio"] and not userdata["tipo"] in ["PROMO", "ADMIN"]:
            flash("no tenés saldo suficiente!")
            return redirect("/")

        # si ya esta en lista se rechaza el intento
        try:
            listaid = db.execute(
                "SELECT listaid FROM listas WHERE userid = ? AND jodaid = ?", userid, jodaid)[0]["listaid"]
        except:
            listaid = None
        if listaid != None:
            flash("ya esta en la lista")
            return redirect("/")

        # si es una cuenta normal se le cobra entrada
        if not userdata["tipo"] in ["PROMO", "ADMIN"]:
            userdata["cash"] -= joda["precio"]
            db.execute("UPDATE usuarios SET cash = ? WHERE id = ?",
                       userdata["cash"], userid)
        # se lo agrega a lista
        db.execute(
            "INSERT INTO listas (jodaid , userid ) VALUES ( ? , ? )", jodaid, userid)

        flash("confirmaste correctamente!")
        return redirect("/")
    else:
        if not request.args.get("jodaid"):
            flash("faltante: id de joda")
            return redirect("/")
        userdata = db.execute(
            "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]
        jodaid = request.args.get("jodaid")

        # checks if the user isn't already in the list
        try:
            confirmado = db.execute("SELECT userid FROM listas WHERE jodaid=? AND userid=? ", jodaid, userdata["id"])[0]["userid"]
            confirmado = "si"
        except:
            confirmado = "no"

        jodadata = db.execute(
            "SELECT jodaid, nombre, descripcion, ubicacion, fecha, precio, sevende FROM jodas WHERE jodaid = ?", jodaid)[0]
        return render_template("confirmarlista.html", userdata=userdata, jodadata=jodadata, confirmado = confirmado)


# /jodas__lista
# promo_required
    # ver lista de joda
@app.route("/listajodas", methods=["GET"])
@promo_required
def listajodas():
    userdata = db.execute(
        "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]
    if request.args.get("jodaid") == None:
        flash("id de joda es necesario")
        return redirect("/")
    jodaid = request.args.get("jodaid")
    confirmados = db.execute(''' SELECT usuarios.username AS username, usuarios.nombre AS nombre, usuarios.id AS userid, listas.listaid AS listaid, listas.yaentro AS yaentro
                                FROM usuarios INNER JOIN listas
                                ON usuarios.id = listas.userid
                                WHERE listas.jodaid = ?
                                ORDER BY nombre''', jodaid)
    jodadata = db.execute(
        "SELECT jodaid, nombre FROM jodas WHERE jodaid=?", jodaid)[0]
    return render_template("lista.html", userdata=userdata, confirmados=confirmados, jodadata=jodadata)


@app.route("/listajodas/buscar")
@promo_required
def buscarconfirmados():
    confirmados = db.execute(''' SELECT usuarios.username AS username, usuarios.nombre AS nombre, usuarios.id AS userid, listas.listaid AS listaid, listas.yaentro AS yaentro
                                FROM usuarios INNER JOIN listas
                                ON usuarios.id = listas.userid
                                WHERE listas.jodaid = ? AND userid LIKE ?''', request.args.get("jodaid"), request.args.get("userid")+'%')
    return jsonify(confirmados)

# yaentro
# promorequired


@app.route("/yaentro", methods=["POST"])
@promo_required
def ya_entro():
    if not request.form.get("listaid"):
        flash("listaid faltante")
        return redirect("/")
    listaid = request.form.get("listaid")
    db.execute("UPDATE listas SET yaentro = 'Si' WHERE listaid=?", listaid)

    jodaid = db.execute("SELECT jodaid FROM listas WHERE listaid = ?", listaid)[
        0]["jodaid"]
    return redirect("/listajodas?jodaid=" + jodaid)


# /eliminarconfirmado
# admin_required
@app.route("/eliminarconfirmado", methods=["POST"])
@admin_required
def eliminarconfirmado():
    if not request.form.get("listaid"):
        flash("faltante: lista id")
        return redirect("/")
    listaid = request.form.get("listaid")

    jodaid = db.execute("SELECT jodaid FROM listas WHERE listaid = ?", listaid)[
        0]["jodaid"]

    db.execute("DELETE FROM listas WHERE listaid=?", listaid)

    flash("eliminado correctamente. ojala no reclame dinero")
    return redirect("/listajodas?jodaid={}".format(jodaid))

# /proponerjoda
# promo_required
    # proponer joda
@app.route("/proponerjoda", methods=["GET", "POST"])
@login_required
def proponerjoda():
    solicitudes=[
        {"request": "nombre", "tipo":"text"},
        {"request": "descripcion", "tipo":"text"},
        {"request": "ubicacion", "tipo":"text"},
        {"request": "fecha", "tipo":"date"},
        {"request": "presupuesto", "tipo":"number"},
        {"request": "capacidad", "tipo":"number"},
        {"request": "precio", "tipo":"number"},
        {"request": "sevende", "tipo":"text"}
    ]


    if request.method == "POST":
        # cargar propuesta en b.d. jodas

        autorid = session.get("user_id")

        for solicitud in solicitudes:
            if not request.form.get(solicitud["request"]):
                flash("faltante:{}".format(solicitud["request"]))
                return redirect("/proponerjoda")
            solicitud["value"]= request.form.get(solicitud["request"])

        db.execute("INSERT INTO jodas (autorid , nombre , descripcion , ubicacion , fecha , presupuesto , capacidad , precio , sevende) VALUES(? , ? , ? , ? , ? , ? , ? , ? , ?)",
                   autorid, solicitudes[0]["value"], solicitudes[1]["value"], solicitudes[2]["value"], solicitudes[3]["value"], solicitudes[4]["value"], solicitudes[5]["value"], solicitudes[6]["value"], solicitudes[7]["value"])

        flash("joda propuesta correctamente")
        return redirect("/")
    else:
        # mostrar formulario
        userdata = db.execute(
            "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]

        return render_template("proponer.html", userdata=userdata, solicitudes=solicitudes)

# /votarjodas
@app.route("/votarjodas", methods=["GET", "POST"])
@promo_required
def votarjodas():
    if request.method == "POST":
        # cargar voto en b.d. jodavotos
        jodaid = request.form.get("jodaid")
        if not request.form.get("voto"):
            flash("voto faltante")
            return redirect("/votarjodas/{0}".format(jodaid))
        voto = request.form.get("voto")
        db.execute("INSERT INTO jodavotos(jodaid, userid, voto) VALUES(?,?,?)",
                   jodaid, session.get("user_id"), voto)

        # se chequea si la joda en votacion se tiene que confirmar o rechazar
        if chequearvotos(jodaid):
            restarles(jodaid)  # se le resta a cada promo lo que debe poner

        flash("voto cargado correctamente")
        return redirect("/")
    else:
        userdata = db.execute(
            "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]
        # mostrar formulario de votacion
        if not request.args.get("jodaid"):
            flash("faltante: id de joda")
            return redirect("/")
        jodaid = request.args.get("jodaid")

        try:
            votoanterior = db.execute(
                "SELECT voto FROM jodavotos WHERE userid= ? AND jodaid = ?", userdata["id"], jodaid)[0]["voto"]
        except:
            votoanterior = None
        if votoanterior != None:
            flash("usted ya voto que " + votoanterior)
            return redirect("/")

        jodadata = db.execute("SELECT * FROM jodas WHERE jodaid= ?", jodaid)[0]
        promos = db.execute("SELECT userid FROM promos")

        CUpone = jodadata["presupuesto"] / len(promos)
        SeGana = jodadata["precio"] * jodadata["capacidad"] * 0.80

        bdvotos = db.execute(
            "SELECT * FROM jodavotos WHERE jodaid = ?", jodaid)
        votos = {'si': 0,
                 'no': 0,
                 'cantpromos': len(promos)}
        for voto in bdvotos:
            if voto["voto"] == "si":
                votos["si"] += 1
            else:
                votos["no"] += 1

        return render_template("votacion.html", userdata=userdata, jodadata=jodadata, CUpone=CUpone, SeGana=SeGana, votos=votos)

# /eliminarjodas
@app.route("/eliminarjoda", methods=["POST"])
@admin_required
def eliminarjoda():
    if not request.form.get("jodaid"):
        flash("faltante: jodaid")
        return redirect("/")
    jodaid = request.form.get("jodaid")

    db.execute("DELETE FROM jodas WHERE jodaid=?", jodaid)

    flash("joda eliminada correctamente")
    return redirect("/")

# /pedircarga
    # pedir carga de dinero, a arreglar con administrador
@app.route("/pedircarga", methods=["GET", "POST"])
@login_required
def pedircarga():
    if request.method == "POST":
        if request.form.get("monto") == None:
            flash("ingrese monto a cargar")
            return redirect("/pedircarga")
        monto = request.form.get("monto")

        phone = "543804594410"
        text = "id de usuario: {}. monto a cargar: {}$".format(
            session.get("user_id"), monto)
        text = '%20'.join(text.split(" "))
        webbrowser.open_new_tab(
            "https://api.whatsapp.com/send?phone={}&text={}".format(phone, text))
        flash("redirigido correctamente")
        return redirect("/")
    else:
        userdata = db.execute(
            "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]
        return render_template("pedircarga.html", userdata=userdata)


# /cargarplata
    # cargar plata
@app.route("/cargarplata", methods=["GET", "POST"])
@admin_required
def cargarplata():
    if request.method == "POST":
        userid = request.form.get("userid")
        deposito = float(request.form.get("deposito"))
        monto = float(db.execute(
            "SELECT cash FROM usuarios WHERE id = ?", userid)[0]["cash"])
        db.execute("UPDATE usuarios SET cash = ? WHERE id = ?", monto + deposito, userid)
        flash("dinero cargado correctamente")
        return redirect("/")
    else:
        userdata = db.execute(
            "SELECT * FROM usuarios WHERE id = ?", session.get("user_id"))[0]
        return render_template("cargarplata.html", userdata=userdata)


