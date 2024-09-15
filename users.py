from db import db_execute, db_commit
from flask_bcrypt import Bcrypt
from app import app

bcrypt = Bcrypt(app)

def login(username, password):
    sql = "SELECT id, username, password FROM users WHERE username=:username"
    user = db_execute(sql, {"username": username}).fetchone()

    if user:
        id, username, password_hash = user
        if bcrypt.check_password_hash(password_hash, password):
            return { "id": id, "username": username }
    
    return None


def register(username, password):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        sql = "INSERT INTO users (username, password) VALUES(:username,:password)"
        db_execute(sql, {"username": username, "password": password_hash})
        db_commit()
    except Exception as error:
        return None
    
    return login(username, password)