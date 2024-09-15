from flask import request, render_template, session, redirect
from app import app
import users

@app.route("/")
def index():
    return render_template("index.html", user=users.get())

@app.route("/login", methods=["GET", "POST"])
def login():
    if users.get():
        return redirect('/')
    
    if request.method == "GET":
        return render_template("login.html", user=None)
    
    username = request.form["username"]
    password = request.form["password"]

    if not users.login(username, password):
        return "Failed to login.", 400

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if users.get():
        return redirect('/')

    if request.method == "GET":
        return render_template("register.html", user=None)
    
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    if not users.register(username, password, role):
        return "Failed to register.", 400
    return redirect("/")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    users.logout()
    return redirect("/")