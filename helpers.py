import os
import requests
import urllib.parse
import datetime
from cs50 import SQL
from flask import redirect, render_template, request, session, flash
from functools import wraps


db = SQL("sqlite:///promoutn.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("you need to log in")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def promo_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not db.execute("SELECT tipo FROM usuarios WHERE id = ?", session.get("user_id"))[0]["tipo"] in ["PROMO", "ADMIN"]:
            flash("requerido ser promo")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if db.execute("SELECT tipo FROM usuarios WHERE id = ?", session.get("user_id"))[0]["tipo"] != "ADMIN":
            flash("requerido ser admin")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def checkwellnes(password):
    if len(password) < 6 or len(password) > 16:
        return "password must have 6-16 characters"
    numbers = 0
    letters = 0
    for char in password:
        if char.isdigit():
            numbers+=1
        else:
             letters+=1
    if not numbers >= 3:
        return "password must have at least 3 numbers"
    if not letters >= 3:
        return "password must have at least 3 letters"
    return "ok"


def restarles(jodaid):
    presupuesto = db.execute("SELECT presupuesto FROM jodas WHERE jodaid= ?", jodaid)[0]["presupuesto"]
    promos = db.execute('''SELECT promos.userid AS userid, usuarios.cash AS cash
                                FROM promos INNER JOIN usuarios
                                on promos.userid = usuarios.id''')
    CUpone = presupuesto / len(promos)
    for promo in promos:
        db.execute("UPDATE usuarios SET cash= ? WHERE id = ?", float(promo["cash"]) - CUpone, promo["userid"])
    return True

def confirmarjoda(jodaid):
    #se confirma la joda
    nombrejoda= db.execute("SELECT nombre FROM jodas WHERE jodaid= ?", jodaid)[0]["nombre"]
    db.execute("UPDATE jodas SET estado = 'confirmada' WHERE jodaid = ?", jodaid)
    db.execute("INSERT INTO annmsj (userid, mensaje, hora) VALUES (?, ?, ?)", 0, "la joda {} se confirmó".format(nombrejoda), datetime.datetime.now())
    return
def eliminarjoda(jodaid):
    #se rechaza la joda
    nombrejoda= db.execute("SELECT nombre FROM jodas WHERE jodaid= ?", jodaid)[0]["nombre"]
    db.execute("DELETE FROM jodas WHERE jodaid = ?", jodaid)
    db.execute("DELETE FROM jodavotos WHERE jodaid = ?", jodaid)
    db.execute("INSERT INTO annmsj (userid, mensaje, hora) VALUES (?, ?, ?)", 0, "la joda {} fue eliminada".format(nombrejoda), datetime.datetime.now())
    return

def chequearvotos(jodaid):
    promos = db.execute("SELECT userid FROM promos")
    bdvotos = db.execute("SELECT * FROM jodavotos WHERE jodaid = ?", jodaid)
    votos = { 'si': 0,
              'no': 0,
              'cantpromos': len(promos)}
    for voto in bdvotos:
        if voto["voto"] == "si":
            votos["si"] += 1
        else:
            votos["no"] += 1
    if votos["si"] > 0.80* votos["cantpromos"]:
            confirmarjoda(jodaid)
            return True
    elif votos["no"] > 0.20 * votos["cantpromos"] :
            eliminarjoda(jodaid)
            return False
    return False

def chequearfecha(jodaid):
    fecha= db.execute("SELECT fecha FROM jodas WHERE jodaid = ?", jodaid)[0]["fecha"]
    y1, m1, d1 = [int(x) for x in fecha.split('-')]
    fecha = datetime.date(y1, m1, d1)
    if datetime.date.today() > fecha:
        eliminarjoda(jodaid)
        return True
    return FalseThis