import users
from db import db_execute, db_commit, db_execute_commit

def get_list():
    sql = """
        SELECT C.id, C.name, U.id, U.username
        FROM courses C, users U
        WHERE C.teacher_id=U.id
    """
    courses = db_execute(sql).fetchall()
    return list(map(lambda course: {
        "id": course[0],
        "name": course[1],
        "teacher": { 
            "id": course[2],
            "username": course[3]
        }
    }, courses))

def create(name, description, teacher_id):
    sql = """
        INSERT INTO courses (
            name, description, teacher_id
        ) VALUES(
            :name, :description, :teacher_id
        )
    """
    params = {
        "name": name,
        "description": description,
        "teacher_id": teacher_id
    }
    return db_commit(sql, params)

def get(course_id):
    sql = """
        SELECT C.id, C.name, C.description, U.id, U.username
        FROM courses C, users U
        WHERE C.id=:id AND C.teacher_id=U.id
    """
    course = db_execute(sql, {"id": course_id}).fetchone()

    sql = """
        SELECT
            CC.id as id,
            CC.type as type,
            CM.content AS m_content,
            MC.question AS mcq_question,
            MC.choices AS mcq_choices,
            MC.correct_choices AS mcq_correct_choices,
            FR.question AS frq_question,
            FR.solution_regex AS frq_solution_regex,
            FR.case_insensitive AS frq_case_insensitive
        FROM course_contents CC
            LEFT JOIN course_materials CM ON CC.course_material_id=CM.id
            LEFT JOIN multiple_choices MC ON CC.multiple_choice_id=MC.id
            LEFT JOIN free_responses FR ON CC.free_response_id=FR.id
    """
    contents = db_execute(sql, {"id": course_id}).fetchall()

    def map_content(x):
        if x.type == "material": return {
            "id": x.id,
            "type": x.type,
            "text": x.m_content
        }
        elif x.type == "multiple_choice": return {
            "id": x.id,
            "type": x.type,
            "question": x.mcq_question,
            "choices": x.mcq_choices.split(";"),
            "correct_choices": x.mcq_choices.split(";")
        }
        elif x.type == "free_response": return {
            "id": x.id,
            "type": x.type,
            "question": x.frq_question,
            "solution_regex": x.frq_solution_regex,
            "case_insensitive": x.frq_case_insensitive
        }
        
    return {
        "id": course[0],
        "name": course[1],
        "description": course[2],
        "teacher": {
            "id": course[3],
            "username": course[4]
        },
        "contents": list(map(map_content, contents))
    }

def add_content(course_id, content_type, content_id):
    sql = """
        INSERT INTO course_contents (
            course_id, type, course_material_id, multiple_choice_id, free_response_id
        ) VALUES (
            :course_id, :type, :course_material_id, :multiple_choice_id, :free_response_id
        )
    """
    params = {
        "course_id": course_id,
        "type": content_type,
        "course_material_id": content_id if content_type == "material" else None,
        "multiple_choice_id": content_id if content_type == "multiple_choice" else None,
        "free_response_id": content_id if content_type == "free_response" else None
    }

    return db_commit(sql, params)

def add_material(course_id, content):
    sql = """
        INSERT INTO course_materials (
            content
        ) VALUES (
            :content
        ) RETURNING id
    """
    res = db_execute(sql, {"content": content})

    if res == None:
        return False
    return db_commit(course_id, "material", res.fetchone().id)

def add_multiple_choice(course_id, question, choices, correct_choices):
    sql = """
        INSERT INTO multiple_choices (
            question, choices, correct_choices
        ) VALUES (
            :question, :choices, :correct_choices
        ) RETURNING id
    """
    params = {
        "question": question,
        "choices": ";".join(choices),
        "correct_choices": ";".join(correct_choices)
    }
    res = db_execute(sql, params)

    if res == None:
        return False
    return add_content(course_id, "multiple_choice", res.fetchone().id)

def add_free_response(course_id, question, solution_regex, case_insensitive):
    sql = """
        INSERT INTO free_responses (
            question, solution_regex, case_insensitive
        ) VALUES (
            :question, :solution_regex, :case_insensitive
        ) RETURNING id
    """
    params = {
        "question": question,
        "solution_regex": solution_regex,
        "case_insensitive": case_insensitive
    }
    res = db_execute(sql, params)

    if res == None:
        return False
    return add_content(course_id, "free_response", res.fetchone().id):

def enroll(course_id, student_id):
    sql = """
        INSERT INTO enrollments (
            student_id, course_id
        ) VALUES (
            :student_id, :course_id
        )
    """
    params = {
        "student_id": student_id,
        "course_id": course_id
    }
    return db_commit(sql, params)