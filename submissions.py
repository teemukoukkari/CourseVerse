import re
from db import db_execute, db_commit

def get_content_info(content_id):
    sql = """
        SELECT
            course_id,
            type,
            CASE
                WHEN type='material' THEN course_material_id
                WHEN type='multiple_choice' THEN multiple_choice_id
                WHEN type='free_response' THEN free_response_id
            END AS target_id
        FROM course_contents
        WHERE id=:content_id
    """
    result = db_execute(sql, {"content_id": content_id}).fetchone()
    if not result:
        return None

    return {
        "id": content_id,
        "course_id": result.course_id,
        "type": result.type,
        "target_id": result.target_id
    }

def create_raw(student_id, content_id, answer, correct):
    sql = """
        INSERT INTO submissions (
            student_id, content_id, answer, correct, submit_time
        ) VALUES (
            :student_id, :content_id, :answer, :correct, NOW()
        )
    """
    params = {
        "student_id": student_id,
        "content_id": content_id,
        "answer": answer,
        "correct": correct
    }
    return db_commit(sql, params)


def create_course_material(student_id, content_info, status):
    return create_raw(student_id, content_info["id"], "", status)

def create_multiple_choice(student_id, content_info, choices):
    sql = """
        SELECT correct_choices
        FROM multiple_choices
        WHERE id=:id
    """
    result = db_execute(sql, {"id": content_info["target_id"]}).fetchone()
    if not result:
        return False

    correct_choices = result.correct_choices.split(chr(31))
    correct = set(choices) == set(correct_choices)
    return create_raw(student_id, content_info["id"], ";".join(choices), correct)

def create_free_response(student_id, content_info, answer):
    sql = """
        SELECT solution_regex, case_insensitive
        FROM free_responses
        WHERE id=:id
    """
    result = db_execute(sql, { "id": content_info["target_id"]}).fetchone()
    if not result:
        return False

    expr = "^(" + result.solution_regex + ")$"
    flags = re.IGNORECASE if result.case_insensitive else re.NOFLAG
    correct = bool(re.match(expr, answer, flags))
    return create_raw(student_id, content_info["id"], answer, correct)

def get_user_overview(student_id, course_id):
    sql = """
        SELECT ARRAY_AGG(status) AS statuses
        FROM (
            SELECT BOOL_OR(S.correct) AS status
            FROM course_contents CC
            LEFT JOIN submissions S
                ON S.content_id=CC.id AND S.student_id=:student_id
            WHERE CC.course_id=:course_id
            GROUP BY CC.position
        ) AS subquery;
    """
    params = {
        "student_id": student_id,
        "course_id": course_id
    }
    result = db_execute(sql, params).fetchone()
    return result.statuses

def get_teacher_overview(course_id):
    sql = """
        SELECT 
            U.username AS student,
            (
                SELECT ARRAY_AGG(status)
                FROM (
                    SELECT BOOL_OR(S.correct) AS status
                    FROM course_contents CC
                    LEFT JOIN submissions S
                        ON S.content_id=CC.id AND S.student_id=E.student_id
                    WHERE CC.course_id=E.course_id
                    GROUP BY CC.position
                ) AS subquery
            ) AS statuses
        FROM enrollments E
        LEFT JOIN users U ON U.id=E.student_id
        WHERE E.course_id=:course_id;
    """
    params = {
        "course_id": course_id
    }
    result = db_execute(sql, params).fetchall()

    return list(map(lambda x: {
        "name": x.student,
        "statuses": x.statuses
    }, result))
