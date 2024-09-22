import users
from db import db_execute, db_commit

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
        WHERE C.id=:course_id AND C.teacher_id=U.id
    """
    course = db_execute(sql, {"course_id": course_id}).fetchone()

    sql = """
        SELECT
            CC.id as id,
            CC.position as position,
            CC.type as type,
            CM.title AS m_title,
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
        WHERE CC.course_id=:course_id
        ORDER BY CC.position 
    """
    contents = db_execute(sql, {"course_id": course_id}).fetchall()

    def map_content(x):
        common = {
            "id": x.id,
            "position": x.position,
            "type": x.type
        }
        if x.type == "material": return dict(common, **{
            "title": x.m_title,
            "text": x.m_content
        })
        elif x.type == "multiple_choice": return dict(common, **{
            "question": x.mcq_question,
            "choices": x.mcq_choices.split(";"),
            "correct_choices": x.mcq_correct_choices.split(";")
        })
        elif x.type == "free_response": return dict(common, **{
            "question": x.frq_question,
            "solution_regex": x.frq_solution_regex,
            "case_insensitive": x.frq_case_insensitive
        })
        
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
            course_id,
            position,
            type,
            course_material_id,
            multiple_choice_id,
            free_response_id
        ) VALUES(
            :course_id,
            (
                SELECT COALESCE(MAX(position),0) + 1
                FROM course_contents
                WHERE course_id=:course_id
            ),
            :type,
            :course_material_id,
            :multiple_choice_id,
            :free_response_id
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

def add_material(course_id, title, content):
    sql = """
        INSERT INTO course_materials (
            title, content
        ) VALUES (
            :title, :content
        ) RETURNING id
    """
    res = db_execute(sql, {"title": title, "content": content})

    if res == None:
        return False
    return add_content(course_id, "material", res.fetchone().id)

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
    return add_content(course_id, "free_response", res.fetchone().id)

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

def move_content(course_id, old_position, action):
    sql_top = """
        UPDATE course_contents
        SET position = (CASE
            WHEN position=:old_position THEN 1 
            ELSE position + 1
        END)
        WHERE course_id=:course_id AND position<=:old_position
    """

    sql_up = """
        UPDATE course_contents
        SET position = (CASE
            WHEN position=:old_position-1 THEN :old_position
            WHEN position=:old_position AND position!=0 THEN :old_position-1
            ELSE :old_position
        END)
        WHERE course_id=:course_id
            AND position IN(:old_position, :old_position-1)
    """

    sql_down = """
        UPDATE course_contents
        SET position = (CASE
            WHEN position=:old_position+1 THEN :old_position
            WHEN position=:old_position AND position!=(
                SELECT MAX(position)
                FROM course_contents
                WHERE course_id=:course_id
            ) THEN position+1
            ELSE :old_position
        END)
        WHERE course_id=:course_id 
            AND position IN(:old_position, :old_position+1)
    """

    sql_bottom = """
        UPDATE course_contents
        SET position = (CASE
            WHEN position=:old_position
            THEN (
                SELECT MAX(position)
                FROM course_contents
                WHERE course_id=:course_id
            )
            ELSE position - 1
        END)
        WHERE course_id=:course_id AND position>=:old_position
    """
    
    params = {
        "course_id": course_id,
        "old_position": old_position
    }

    if action == "top":
        return db_commit(sql_top, params)
    elif action == "up":
        return db_commit(sql_up, params)
    elif action == "down":
        return db_commit(sql_down, params)
    elif action == "bottom":
        return db_commit(sql_bottom, params)

    return False