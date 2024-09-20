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
    return {
        "id": content_id,
        "course_id": result.course_id,
        "type": result.type,
        "target_id": result.target_id
    }

def create_raw(student_id, content_id, answer, correct):
    try:
        sql = """
            INSERT INTO submissions (
                student_id, content_id, answer, correct, submit_time
            ) VALUES (
                :student_id, :content_id, :answer, :correct, NOW()
            )
        """
        db_execute(sql, {
            "student_id": student_id,
            "content_id": content_id,
            "answer": answer,
            "correct": correct
        })
        db_commit()
    except Exception as err:
        print(err)
        return False
    return True


def create_course_material(student_id, content_info, status):
    return create_raw(student_id, content_info["id"], "", status)

def create_multiple_choice(student_id, content_info, choices):
    sql = """
        SELECT correct_choices
        FROM multiple_choices
        WHERE id=:id
    """
    correct_choices = db_execute(sql, {
        "id": content_info["target_id"]
    }).fetchone().correct_choices.split(";")

    correct = set(choices) == set(correct_choices)
    return create_raw(student_id, content_info["id"], ";".join(choices), correct)

def create_free_response(student_id, content_info, answer):
    sql = """
        SELECT solution_regex, case_insensitive
        FROM free_responses
        WHERE id=:id
    """
    result = db_execute(sql, {
        "id": content_info["target_id"]
    }).fetchone()

    expr = "^(" + result.solution_regex + ")$"
    flags = re.IGNORECASE if result.case_insensitive else None
    correct = bool(re.match(expr, answer, flags))
    return create_raw(student_id, content_info["id"], answer, correct)