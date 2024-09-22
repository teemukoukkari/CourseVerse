from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from app import app

db = None
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI")
db = SQLAlchemy(app)

def db_execute(sql, args={}):
    global db
    try:
        return db.session.execute(text(sql), args)
    except Exception as err:
        db.session.rollback()
        print(err)
        return None

def db_commit(sql, args={}):
    global db
    try:
        db.session.execute(text(sql), args)
        db.session.commit()
        return True
    except Exception as err:
        db.session.rollback()
        print(err)
        return False