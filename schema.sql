CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    teacher_id INTEGER REFERENCES users
);

CREATE TABLE course_materials (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT
);

CREATE TABLE multiple_choices (
    id SERIAL PRIMARY KEY,
    question TEXT,
    choices TEXT,
    correct_choices TEXT
);

CREATE TABLE free_responses (
    id SERIAL PRIMARY KEY,
    question TEXT,
    solution_regex TEXT,
    case_insensitive BOOLEAN
);

CREATE TABLE course_contents (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    position INTEGER,
    type TEXT,
    course_material_id INTEGER REFERENCES course_materials ON DELETE CASCADE,
    multiple_choice_id INTEGER REFERENCES multiple_choices ON DELETE CASCADE,
    free_response_id INTEGER REFERENCES free_responses ON DELETE CASCADE
);

CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users NOT NULL,
    course_id INTEGER REFERENCES courses NOT NULL
);

CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users NOT NULL,
    content_id INTEGER REFERENCES course_contents NOT NULL,
    answer TEXT,
    correct BOOLEAN,
    submit_time TIMESTAMP
);