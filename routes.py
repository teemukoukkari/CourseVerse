from flask import request, render_template, session, redirect
from app import app
import users

def get_user():
    if "user" in session:
        return session['user']
    return None

@app.route("/")
def index():
    return render_template("index.html", user=get_user())

@app.route("/login", methods=["GET", "POST"])
def login():
    if get_user():
        return redirect('/')
    
    if request.method == "GET":
        return render_template("login.html", user=None)
    
    username = request.form["username"]
    password = request.form["password"]

    user = users.login(username, password)
    if not user:
        return "Failed to login.", 400
    session["user"] = user

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if get_user():
        return redirect('/')

    if request.method == "GET":
        return render_template("register.html", user=None)
    
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    user = users.register(username, password, role)
    if not user:
        return "Failed to register.", 400
    session["user"] = user

    return redirect("/")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if get_user():
        del session["user"]
    return redirect("/")