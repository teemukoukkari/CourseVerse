from flask_bcrypt import Bcrypt
from flask import session
from app import app
from db import db_execute, db_commit

bcrypt = Bcrypt(app)

def get():
    if "user" in session:
        return session["user"]
    return None

def login(username, password):
    sql = """
        SELECT id, username, password, role
        FROM users
        WHERE username=:username
    """
    user = db_execute(sql, {"username": username}).fetchone()

    if user:
        id, username, password_hash, role = user
        if bcrypt.check_password_hash(password_hash, password):
            session["user"] = { "id": id, "username": username, "role": role }
            load_enrollments()
            return True
    
    return False

def register(username, password, role):
    sql = """
        INSERT INTO users (
            username, password, role
        ) VALUES(
            :username,:password,:role
        )
    """
    params = {
        "username": username,
        "password": bcrypt.generate_password_hash(password).decode('utf-8'),
        "role": role
    }
    if not db_commit(sql, params):
        return False
    return login(username, password)

def logout():
    if "user" in session:
        del session["user"]

def load_enrollments():
    if "user" in session and session["user"]["role"] == "student":
        sql = """
            SELECT course_id
            FROM enrollments
            WHERE student_id=:student_id
        """
        session["user"]["enrollments"] = list(map(
            lambda x: x.course_id,
            db_execute(sql, {"student_id": session["user"]["id"]}).fetchall()
        ))
        return True
    else:
        return False