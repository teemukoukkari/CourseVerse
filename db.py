from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI")
db = SQLAlchemy(app)

def db_execute(sql, args={}):
    try:
        return db.session.execute(text(sql), args)
    except SQLAlchemyError as err:
        db.session.rollback()
        print(err)
        return None

def db_commit(sql, args={}):
    try:
        db.session.execute(text(sql), args)
        db.session.commit()
        return True
    except SQLAlchemyError as err:
        db.session.rollback()
        print(err)
        return False
