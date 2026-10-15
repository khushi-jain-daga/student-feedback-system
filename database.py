"""SQLite persistence layer for the Student Feedback Management System."""
import sqlite3
from pathlib import Path
import os

def _resolve_db_path():
    env_path = os.getenv('FEEDBACK_DB_PATH')
    if env_path:
        return Path(env_path)
    try:
        import streamlit as st
        if 'FEEDBACK_DB_PATH' in st.secrets:
            return Path(st.secrets['FEEDBACK_DB_PATH'])
    except Exception:
        pass
    return Path(__file__).with_name('feedback.db')


DB_PATH = _resolve_db_path()


def connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connection() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student','admin')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            department TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES users(id),
            faculty_id INTEGER NOT NULL REFERENCES faculty(id),
            course TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comments TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_feedback_student ON feedback(student_id);
        CREATE INDEX IF NOT EXISTS idx_feedback_faculty ON feedback(faculty_id);
        ''')
        for name, dept in [('Dr. Sharma', 'Computer Science'), ('Prof. Gupta', 'Mathematics'), ('Dr. Singh', 'Physics')]:
            db.execute('INSERT OR IGNORE INTO faculty(name, department) VALUES (?,?)', (name, dept))


def create_user(username, full_name, email, password_hash, role='student'):
    if role not in ('student','admin'):
        raise ValueError('Invalid role')
    with connection() as db:
        result = db.execute('INSERT INTO users(username,full_name,email,password_hash,role) VALUES (?,?,?,?,?)',
                            (username, full_name, email, password_hash, role))
        return result.lastrowid


def get_user(username):
    with connection() as db:
        row = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        return dict(row) if row else None


def update_user_password(username, new_password_hash):
    with connection() as db:
        db.execute('UPDATE users SET password_hash=? WHERE username=? COLLATE NOCASE',
                   (new_password_hash, username))


def list_faculty(active_only=True):
    with connection() as db:
        rows = db.execute('SELECT * FROM faculty WHERE active=1 ORDER BY name' if active_only else 'SELECT * FROM faculty ORDER BY name').fetchall()
        return [dict(r) for r in rows]


def add_faculty(name, department):
    with connection() as db:
        db.execute('INSERT INTO faculty(name,department) VALUES (?,?)', (name,department))


def set_faculty_active(faculty_id, active):
    with connection() as db:
        db.execute('UPDATE faculty SET active=? WHERE id=?', (int(active),faculty_id))


def submit_feedback(student_id, faculty_id, course, rating, comments):
    with connection() as db:
        faculty = db.execute('SELECT id FROM faculty WHERE id=? AND active=1', (faculty_id,)).fetchone()
        if not faculty:
            raise ValueError('Faculty unavailable')
        result = db.execute('INSERT INTO feedback(student_id,faculty_id,course,rating,comments) VALUES (?,?,?,?,?)',
                            (student_id,faculty_id,course,rating,comments))
        return result.lastrowid


def fetch_feedback(student_id=None, faculty_id=None):
    query = '''SELECT f.id, u.username AS student, u.full_name AS student_name, t.name AS faculty,
                      t.department, f.course, f.rating, f.comments, f.created_at
               FROM feedback f JOIN users u ON f.student_id=u.id
               JOIN faculty t ON f.faculty_id=t.id WHERE 1=1'''
    params = []
    if student_id is not None:
        query += ' AND f.student_id=?'; params.append(student_id)
    if faculty_id is not None:
        query += ' AND f.faculty_id=?'; params.append(faculty_id)
    query += ' ORDER BY f.id DESC'
    with connection() as db:
        return [dict(r) for r in db.execute(query, params).fetchall()]


def dashboard_stats():
    with connection() as db:
        students = db.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]
        stats = db.execute('SELECT COUNT(*), ROUND(AVG(rating),2) FROM feedback').fetchone()
        by_faculty = [dict(r) for r in db.execute('''SELECT t.name AS faculty, COUNT(f.id) AS responses,
                  ROUND(AVG(f.rating),2) AS avg_rating FROM faculty t
                  LEFT JOIN feedback f ON f.faculty_id=t.id GROUP BY t.id ORDER BY t.name''')]
        return {'students':students,'feedback_count':stats[0],'average_rating':stats[1] or 0,'faculty_stats':by_faculty}
