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
            "username": course[3]
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

def get(course_id):
    sql = "SELECT C.id, C.name, C.description, U.id, U.username FROM courses C, users U WHERE C.id=:id AND C.teacher_id=U.id"
    course = db_execute(sql, {"id": course_id}).fetchone()

    sql = "SELECT content FROM course_materials WHERE course_id=:course_id"
    materials = db_execute(sql, {"course_id": course_id}).fetchall()

    return {
        "id": course[0],
        "name": course[1],
        "description": course[2],
        "teacher": {
            "id": course[3],
            "username": course[4]
        },
        "contents": list(map(lambda x: {
            "type": "material",
            "text": x[0]
        }, materials))
    }

def add_material(course_id, content):
    try:
        sql = "INSERT INTO course_materials (course_id, content) VALUES (:course_id, :content)"
        db_execute(sql, {"course_id": course_id, "content": content})
        db_commit()
    except Exception as err:
        print(err)
        return False
    
    return True
