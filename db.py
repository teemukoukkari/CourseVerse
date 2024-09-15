from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from app import app

db = None
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI")
db = SQLAlchemy(app)

def db_execute(sql, args):
    global db
    return db.session.execute(text(sql), args)

def db_commit():
    global db
    db.session.commit()