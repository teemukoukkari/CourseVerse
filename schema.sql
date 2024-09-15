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
    course_id INTEGER REFERENCES courses NOT NULL,
    content TEXT
);