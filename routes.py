from flask import request, render_template, session, redirect
from app import app
import users, courses, submissions

@app.route("/")
def index():
    course_list = courses.get_list()
    return render_template("index.html", user=users.get(), courses=course_list)

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

@app.route("/courses", methods=["POST"])
def create_course():
    name = request.form["name"]
    description = request.form["description"]
    teacher_id = users.get()["id"]

    if not courses.create(name, description, teacher_id):
        return "Failed to create course.", 400
    return redirect("/")

@app.route("/courses/<id>/")
def get_course(id):
    course = courses.get(id)
    user = users.get()
    return render_template("course.html", user=user, course=course)

@app.route("/courses/<id>/add_material", methods=["POST"])
def add_material(id):
    title = request.form["title"]
    content = request.form["content"]
    courses.add_material(id, title, content)
    return redirect("/courses/" + id)

@app.route("/courses/<id>/add_multiple_choice", methods=["POST"])
def add_multiple_choice(id):
    question = request.form["question"]
    choices = []
    correct_choices = []
    for i in range(0,100):
        if "answer_" + str(i) in request.form:
            if "correct_" + str(i) in request.form:
                choices.append(request.form["answer_" + str(i)])
                correct_choices.append(request.form["answer_" + str(i)])
            else:
                choices.append(request.form["answer_" + str(i)])
        else:
            break

    courses.add_multiple_choice(id, question, choices, correct_choices)

    return redirect("/courses/" + id)

@app.route("/courses/<id>/add_free_response", methods=["POST"])
def add_free_response(id):
    question = request.form["question"]
    solution_regex = request.form["solution_regex"]
    case_insensitive = "case_insensitive" in request.form

    courses.add_free_response(id, question, solution_regex, case_insensitive)
    return redirect("/courses/" + id)

@app.route("/courses/<id>/enroll")
def enroll(id):
    user = users.get()
    if (user["role"] != "student"):
        return "Only students can enroll to courses", 400
    
    if not courses.enroll(id, user["id"]):
        return "Failed to enroll to course", 400

    users.load_enrollments()

    return redirect("/courses/" + id)    

@app.route("/courses/<id>/move_content", methods=["POST"])
def move_content(id):
    old_position = int(request.form["position"])
    action = request.form["action"]
    if not courses.move_content(id, old_position, action):
        return "Failed to move content", 400
    return redirect("/courses/" + id) 

@app.route("/submit", methods=["POST"])
def submit():
    user = users.get()
    content_id = int(request.form["content_id"])
    info = submissions.get_content_info(content_id)
    
    if info["type"] == "material":
        status = request.form["status"]
        if not submissions.create_course_material(user["id"], info, status):
            return "Failed to create submission", 400
    elif info["type"] == "multiple_choice":
        choices = []
        for field in request.form:
            if field.startswith("choice_"):
                choices.append(field[7:])
        if not submissions.create_multiple_choice(user["id"], info, choices):
            return "Failed to create submission", 400
    elif info["type"] == "free_response":
        answer = request.form["answer"]
        if not submissions.create_free_response(user["id"], info, answer):
            return "Failed to create submission", 400

    return redirect("/courses/" + str(info["course_id"]))