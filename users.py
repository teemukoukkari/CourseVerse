from db import db_execute, db_commit
from flask_bcrypt import Bcrypt
from app import app

bcrypt = Bcrypt(app)

def login(username, password):
    sql = "SELECT id, username, password, role FROM users WHERE username=:username"
    user = db_execute(sql, {"username": username}).fetchone()

    if user:
        id, username, password_hash, role = user
        if bcrypt.check_password_hash(password_hash, password):
            return { "id": id, "username": username, "role": role }
    
    return None


def register(username, password, role):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        sql = "INSERT INTO users (username, password, role) VALUES(:username,:password,:role)"
        db_execute(sql, {"username": username, "password": password_hash, "role": role})
        db_commit()
    except Exception as error:
        return None
    
    return login(username, password)