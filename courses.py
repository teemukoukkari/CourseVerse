import users
from db import db_execute, db_commit

def get_list():
    sql = "SELECT C.id, C.name, U.id, U.username FROM courses C, users U WHERE C.teacher_id=U.id"
    courses = db_execute(sql).fetchall()
    return list(map(lambda course: {
        "id": course[0],
        "name": course[1],
        "teacher": { 
            "id": course[2],
            "name": course[3]
        }
    }, courses))

def create(name, description):
    user = users.get()
    if not user or user["role"] != "teacher":
        return False
    
    try:
        sql = "INSERT INTO courses (name, description, teacher_id) VALUES(:name, :description, :teacher_id)"
        db_execute(sql, {"name": name, "description": description, "teacher_id": user["id"]})
        db_commit()
    except Exception as error:
        print(error)
        return False
    
    return True