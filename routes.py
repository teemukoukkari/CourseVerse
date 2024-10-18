import re
from flask import request, render_template, session, redirect
from app import app
import users
import courses
import submissions

def form_get(*fields):
    return tuple(request.form.get(field, None) for field in fields)

@app.route("/")
def index():
    return redirect("/courses")

@app.route("/login", methods=["GET", "POST"])
def login():
    if users.get():
        return redirect('/')

    if request.method == "GET":
        return render_template("login.html", user=None)

    error_msg = None
    username, password = form_get("username", "password")
    if not (username and password):
        error_msg = "Required fields are missing"
    elif not users.login(username, password):
        error_msg = "Wrong username or password."

    if error_msg:
        return render_template("login.html", user=None, error_msg=error_msg)
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if users.get():
        return redirect('/')
    if request.method == "GET":
        return render_template("register.html", user=None)

    error_msg = None
    username, password, role = form_get("username", "password", "role")
    if not (username and password and role):
        error_msg = "Required fields are missing."
    elif not 3 <= len(username) <= 32:
        error_msg = "Username must be between 3 and 32 characters long."
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        error_msg = "Username may only contain letters, digits and underscores."
    elif not 5 <= len(password) <= 64:
        error_msg = "Password must be between 5 and 64 characters long."
    elif not re.search(r'(?=.*[a-zA-Z])(?=.*[0-9])', password):
        error_msg = "Password must contain both letters and numbers."
    elif not role in ("student", "teacher"):
        error_msg = "Invalid role."
    elif not users.register(username, password, role):
        error_msg = "Failed to register. Username may be already taken."

    if error_msg:
        return render_template("register.html", user=None, error_msg=error_msg)
    return redirect("/")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    users.logout()
    return redirect("/")

@app.route("/courses", methods=["GET", "POST"])
def create_course():
    user = users.get()
    if request.method == "GET":
        course_list = courses.get_list()
        return render_template("courses.html", user=user, courses=course_list)

    if not (user and user["role"] == "teacher"):
        return "You must be logged in as teacher to do this", 403

    error_msg = None
    name, description = form_get("name", "description")
    if not (name and description):
        error_msg = "Required fields are missing."
    elif not 4 <= len(name) <= 32:
        error_msg = "Course name must be between 4 and 32 characters long."
    elif not 1 <= len(description) <= 256:
        error_msg = "Course description can be at most 256 characters long."
    elif not courses.create(name, description, user["id"]):
        error_msg = "Failed to create course. Course name may be already taken."

    course_list = courses.get_list()
    return render_template(
        "courses.html", user=user, courses=course_list, error_msg=error_msg
    )

@app.route("/courses/<course_id>/delete")
def delete_course(course_id):
    user = users.get()
    if not (user and user["role"] == "teacher"):
        return "You must be logged in as teacher to do this", 403

    courses.delete(course_id)
    return redirect("/")

@app.route("/courses/<course_id>/enroll")
def enroll(course_id):
    user = users.get()
    if not (user and user["role"] == "student"):
        return "You must be logged in as a student to do this", 403

    if not courses.enroll(course_id, user["id"]):
        course_list = courses.get_list()
        error_msg = "Failed to enroll to the course."
        return render_template(
            "courses.html",
            user=user, courses=course_list, error_msg=error_msg
        )

    users.load_enrollments()

    return redirect("/courses/" + course_id)

@app.route("/courses/<course_id>/")
def get_course(course_id):
    user = users.get()
    if not user:
        return "You must be logged in to do this", 403
    if not course_id.isdecimal():
        return "Invalid id", 400
    if user["role"] == "student" and int(course_id) not in user["enrollments"]:
        return "You are not enrolled to this course!", 403

    course = courses.get(course_id)
    if not course:
        return "Course not found", 404

    overview =  None
    if user["role"] == "student":
        overview = submissions.get_user_overview(user["id"], course_id)
        for i in range(0, len(course["contents"])):
            course["contents"][i]["status"] = overview[i]
    elif user["role"] == "teacher":
        overview = submissions.get_teacher_overview(course_id)

    error_msg = None
    if "course_error_msg" in session:
        error_msg = session["course_error_msg"]
        del session["course_error_msg"]

    return render_template(
        "course.html",
        user=user, course=course, overview=overview, error_msg=error_msg
    )

@app.route("/courses/<course_id>/add_material", methods=["POST"])
def add_material(course_id):
    user = users.get()
    if not (user and user["role"] == "teacher"):
        return "You must be logged in as teacher to do this", 403

    error_msg = None
    title, content = form_get("title", "content")
    if not (title and content):
        error_msg = "Required fields are missing."
    elif not courses.add_material(course_id, title, content):
        error_msg = "Failed to create material."

    session["course_error_msg"] = error_msg
    return redirect("/courses/" + course_id)

@app.route("/courses/<course_id>/add_multiple_choice", methods=["POST"])
def add_multiple_choice(course_id):
    user = users.get()
    if not (user and user["role"] == "teacher"):
        return "You must be logged in as teacher to do this", 403

    question, = form_get("question")
    choices = []
    correct_choices = []
    for i in range(0,100):
        if "answer_" + str(i) not in request.form:
            break
        if "correct_" + str(i) in request.form:
            choices.append(request.form["answer_" + str(i)])
            correct_choices.append(request.form["answer_" + str(i)])
        else:
            choices.append(request.form["answer_" + str(i)])

    error_msg = None
    if not (question and choices):
        error_msg = "Question or choices are missing."
    elif not courses.add_multiple_choice(course_id, question, choices, correct_choices):
        error_msg = "Failed to create multiple choice question."

    session["course_error_msg"] = error_msg
    return redirect("/courses/" + course_id)

def check_regex(s):
    try:
        re.compile(s)
    except re.error:
        return False
    return True

@app.route("/courses/<course_id>/add_free_response", methods=["POST"])
def add_free_response(course_id):
    user = users.get()
    if not (user and user["role"] == "teacher"):
        return "You must be logged in as teacher to do this", 403

    error_msg = None
    question, solution_regex = form_get("question", "solution_regex")
    case = "case_insensitive" in request.form
    if not (question and solution_regex):
        error_msg = "Required fields are missing."
    elif not check_regex("^(" + solution_regex + ")$"):
        error_msg = "Invalid solution regex."
    elif not courses.add_free_response(course_id, question, solution_regex, case):
        error_msg = "Failed to create free reponse question."

    session["course_error_msg"] = error_msg
    return redirect("/courses/" + course_id)

@app.route("/courses/<course_id>/delete_content", methods=["POST"])
def delete_content(course_id):
    user = users.get()
    if not (user and user["role"] == "teacher"):
        return "You must be logged in as teacher to do this", 403

    error_msg = None
    content_id, position = form_get("content_id", "position")
    if not (content_id and position):
        error_msg = "Required fields are missing."
    elif not courses.delete_content(course_id, content_id, position):
        error_msg = "Failed to delete content."

    session["course_error_msg"] = error_msg
    return redirect("/courses/" + course_id)

@app.route("/courses/<course_id>/move_content", methods=["POST"])
def move_content(course_id):
    user = users.get()
    if not (user and user["role"] == "teacher"):
        return "You must be logged in as teacher to do this", 403

    error_msg = None
    old_position, action = form_get("position", "action")
    if not (old_position and action in ("top", "up", "down", "bottom")):
        error_msg = "Required fields are missing or invalid."
    if not courses.move_content(course_id, old_position, action):
        error_msg = "Failed to move content."

    session["course_error_msg"] = error_msg
    return redirect("/courses/" + course_id)

@app.route("/submit", methods=["POST"])
def submit():
    user = users.get()
    if not (user and user["role"] == "student"):
        return "You must be logged in as a student to do this", 403

    content_id, = form_get("content_id")
    if not content_id:
        return "Required field is missing", 400

    info = submissions.get_content_info(content_id)
    if info is None:
        return "Failed to find info for given id.", 400

    error_msg = None
    if info["type"] == "material":
        status, = form_get("status")
        if not status in ("0", "1"):
            error_msg = "Required field is missing or invalid."
        elif not submissions.create_course_material(user["id"], info, status):
            error_msg = "Failed to create submission for text material."
    elif info["type"] == "multiple_choice":
        choices = []
        for field in request.form:
            if field.startswith("choice_"):
                choices.append(field[7:])
        if not submissions.create_multiple_choice(user["id"], info, choices):
            error_msg = "Failed to create submission for multiple choice question."
    elif info["type"] == "free_response":
        answer, = form_get("answer")
        if not answer:
            error_msg = "Required field is missing or invalid."
        if not submissions.create_free_response(user["id"], info, answer):
            error_msg = "Failed to create submission for free response question."

    session["course_error_msg"] = error_msg
    return redirect("/courses/" + str(info["course_id"]))
