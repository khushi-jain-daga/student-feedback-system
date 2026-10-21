"""Database persistence layer for the Student Feedback Management System.
Supports both SQLite (local development) and PostgreSQL / Supabase (production deployment).
Includes master student directory management with registration numbers and evaluation analytics.
"""
import os
import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def _resolve_sqlite_path() -> Path:
    env_path = os.getenv('FEEDBACK_DB_PATH')
    if env_path:
        return Path(env_path)
    try:
        import streamlit as st
        if 'FEEDBACK_DB_PATH' in st.secrets:
            return Path(st.secrets['FEEDBACK_DB_PATH'])
    except Exception:
        pass
    return Path(__file__).resolve().parent / 'feedback.db'


DB_PATH = _resolve_sqlite_path()


def get_database_url() -> Optional[str]:
    """Retrieve DATABASE_URL from environment or Streamlit secrets."""
    url = os.getenv('DATABASE_URL')
    if url and url.strip():
        return url.strip()
    try:
        import streamlit as st
        if 'DATABASE_URL' in st.secrets and str(st.secrets['DATABASE_URL']).strip():
            return str(st.secrets['DATABASE_URL']).strip()
        if 'database' in st.secrets and isinstance(st.secrets['database'], dict):
            if 'url' in st.secrets['database'] and str(st.secrets['database']['url']).strip():
                return str(st.secrets['database']['url']).strip()
    except Exception:
        pass
    return None


def get_engine() -> str:
    """Return 'postgres' if DATABASE_URL is configured and psycopg2 is available, else 'sqlite'."""
    url = get_database_url()
    if url and PSYCOPG2_AVAILABLE:
        return 'postgres'
    return 'sqlite'


@contextmanager
def get_connection():
    """Context manager for obtaining a database connection with dictionary rows."""
    engine = get_engine()
    if engine == 'postgres':
        url = get_database_url()
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(
            url,
            cursor_factory=psycopg2.extras.RealDictCursor,
            connect_timeout=10
        )
        try:
            yield conn
        finally:
            conn.close()
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        try:
            yield conn
        finally:
            conn.close()


def _adapt_query(query: str, engine: str) -> str:
    """Convert ? placeholders to %s for PostgreSQL."""
    if engine == 'postgres':
        return query.replace('?', '%s')
    return query


def execute_query(query: str, params: tuple = ()) -> int:
    """Execute a write query and commit. Returns affected rowcount."""
    engine = get_engine()
    sql = _adapt_query(query, engine)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount


def insert_and_get_id(query: str, params: tuple = ()) -> int:
    """Insert a row and return its generated primary key ID."""
    engine = get_engine()
    if engine == 'postgres':
        sql = _adapt_query(query, engine)
        if 'RETURNING id' not in sql.upper():
            sql = sql.rstrip(';') + ' RETURNING id'
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            conn.commit()
            return row['id'] if row else 0
    else:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid


def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a query and return all matching rows as dictionaries."""
    engine = get_engine()
    sql = _adapt_query(query, engine)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Execute a query and return the first matching row as a dictionary."""
    engine = get_engine()
    sql = _adapt_query(query, engine)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


# ------------------------------------------------------------------------------
# Database Initialization & Schema Migrations
# ------------------------------------------------------------------------------

def init_db():
    """Create schema tables and indexes. Migrate legacy schema if needed."""
    engine = get_engine()
    print("[INIT] Starting database initialization...")
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            if engine == 'postgres':
                cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    registration_no VARCHAR(100),
                    password_hash TEXT NOT NULL,
                    role VARCHAR(50) NOT NULL CHECK(role IN ('user', 'admin')),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS people (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    registration_no VARCHAR(100),
                    type VARCHAR(50) NOT NULL CHECK(type IN ('student', 'teacher')),
                    department TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
                    linked_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS reviews (
                    id SERIAL PRIMARY KEY,
                    reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
                    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                    review_text TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(reviewer_id, person_id)
                );

                CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON reviews(reviewer_id);
                CREATE INDEX IF NOT EXISTS idx_reviews_person ON reviews(person_id);
                CREATE INDEX IF NOT EXISTS idx_people_type ON people(type);
                CREATE INDEX IF NOT EXISTS idx_people_active ON people(active);
                CREATE INDEX IF NOT EXISTS idx_people_regno ON people(registration_no);
                ''')
                conn.commit()
            else:
                # SQLite DDL
                conn.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    registration_no TEXT,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'admin', 'student')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    registration_no TEXT,
                    type TEXT NOT NULL CHECK(type IN ('student', 'teacher')),
                    department TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
                    linked_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
                    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                    review_text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(reviewer_id, person_id)
                );

                CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON reviews(reviewer_id);
                CREATE INDEX IF NOT EXISTS idx_reviews_person ON reviews(person_id);
                CREATE INDEX IF NOT EXISTS idx_people_type ON people(type);
                CREATE INDEX IF NOT EXISTS idx_people_active ON people(active);
                ''')

                # SQLite backward-compatibility migrations
                try:
                    users_sql_row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
                    if users_sql_row and users_sql_row[0]:
                        users_sql = users_sql_row[0]
                        if "role IN ('student','admin')" in users_sql or "full_name" in users_sql:
                            conn.execute("PRAGMA foreign_keys = OFF")
                            conn.executescript('''
                                CREATE TABLE IF NOT EXISTS users_v2 (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                                    registration_no TEXT,
                                    password_hash TEXT NOT NULL,
                                    role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
                                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                                );

                                INSERT OR IGNORE INTO users_v2 (id, name, username, email, password_hash, role, created_at)
                                SELECT id,
                                       COALESCE(name, full_name, username),
                                       username,
                                       email,
                                       password_hash,
                                       CASE WHEN role = 'student' THEN 'user' ELSE role END,
                                       created_at
                                FROM users;

                                DROP TABLE users;
                                ALTER TABLE users_v2 RENAME TO users;
                                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                            ''')
                            conn.execute("PRAGMA foreign_keys = ON")
                except Exception:
                    pass

                # Migration: Ensure registration_no column exists in people table
                try:
                    p_cols = [r[1] for r in conn.execute('PRAGMA table_info(people)').fetchall()]
                    if 'registration_no' not in p_cols:
                        conn.execute('ALTER TABLE people ADD COLUMN registration_no TEXT')
                        conn.commit()
                    conn.execute('CREATE INDEX IF NOT EXISTS idx_people_regno ON people(registration_no)')
                    conn.commit()
                except Exception:
                    pass

                # Migration: Ensure registration_no column exists in users table
                try:
                    u_cols = [r[1] for r in conn.execute('PRAGMA table_info(users)').fetchall()]
                    if 'registration_no' not in u_cols:
                        conn.execute('ALTER TABLE users ADD COLUMN registration_no TEXT')
                        conn.commit()
                except Exception:
                    pass

            conn.commit()
            print("[INIT] Database schema ready.")

            # Ensure baseline sample teachers exist using the SAME connection
            seed_initial_teachers(conn)

            # Import Master Student List from students_master.json using the SAME connection
            import_master_students(conn)
            print("[INIT] Master students synchronized.")
    except Exception as e:
        print(f"[INIT ERROR] Database initialization encountered {type(e).__name__}")
        raise


def seed_initial_teachers(conn=None):
    """Ensure baseline active faculty / teachers exist for demonstration using ONE connection."""
    engine = get_engine()

    def _do_seed(c):
        cur = c.cursor()
        sql_count = "SELECT COUNT(*) AS cnt FROM people WHERE LOWER(type) = 'teacher'"
        cur.execute(sql_count)
        row = cur.fetchone()
        cnt = row['cnt'] if isinstance(row, dict) or hasattr(row, '__getitem__') else (row[0] if row else 0)
        if cnt == 0:
            sample_teachers = [
                ('Dr. Sharma', 'teacher', 'Computer Science & Engineering'),
                ('Prof. Gupta', 'teacher', 'Mathematics & Data Science'),
                ('Dr. Anita Roy', 'teacher', 'Electronics & Communication'),
                ('Prof. Ramesh Verma', 'teacher', 'Mechanical Engineering')
            ]
            sql_ins = (
                "INSERT INTO people (name, type, department, active) VALUES (%s, %s, %s, 1)"
                if engine == 'postgres'
                else "INSERT INTO people (name, type, department, active) VALUES (?, ?, ?, 1)"
            )
            for name, p_type, dept in sample_teachers:
                cur.execute(sql_ins, (name, p_type, dept))
            c.commit()

    if conn is not None:
        _do_seed(conn)
    else:
        with get_connection() as c:
            _do_seed(c)


def import_master_students(conn=None) -> int:
    """
    Import master students list from students_master.json into the people table.
    Sets:
      - name = STUDNAME
      - registration_no = REGNO
      - type = 'student'
      - active = 1 (true)
    Uses ONE connection and ONE cursor for the entire 62-student import.
    Commits once after completing the loop.
    Does not import attendance-related columns.
    """
    json_path = Path(__file__).resolve().parent / 'students_master.json'
    if not json_path.exists():
        return 0

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            students = json.load(f)
    except Exception as e:
        print(f"[INIT] Notice: Could not read students_master.json: {type(e).__name__}")
        return 0

    engine = get_engine()

    def _do_import(c) -> int:
        cur = c.cursor()
        count = 0
        sel_sql = (
            'SELECT id FROM people WHERE type = %s AND UPPER(registration_no) = %s'
            if engine == 'postgres'
            else 'SELECT id FROM people WHERE type = ? AND UPPER(registration_no) = ?'
        )
        upd_sql = (
            'UPDATE people SET name = %s, department = %s, active = 1 WHERE id = %s'
            if engine == 'postgres'
            else 'UPDATE people SET name = ?, department = ?, active = 1 WHERE id = ?'
        )
        ins_sql = (
            'INSERT INTO people (name, registration_no, type, department, active) VALUES (%s, %s, %s, %s, 1)'
            if engine == 'postgres'
            else 'INSERT INTO people (name, registration_no, type, department, active) VALUES (?, ?, ?, ?, 1)'
        )

        for s in students:
            reg = str(s.get('registration_no', '')).strip().upper()
            name = str(s.get('name', '')).strip()
            dept = str(s.get('department', 'Computer Science & Engineering')).strip()
            if not reg or not name:
                continue

            cur.execute(sel_sql, ('student', reg))
            row = cur.fetchone()
            if row:
                pid = row['id'] if isinstance(row, dict) or hasattr(row, '__getitem__') else row[0]
                cur.execute(upd_sql, (name, dept, pid))
            else:
                cur.execute(ins_sql, (name, reg, 'student', dept))
                count += 1

        c.commit()
        return count

    if conn is not None:
        return _do_import(conn)
    else:
        with get_connection() as c:
            return _do_import(c)


# ------------------------------------------------------------------------------
# Users CRUD
# ------------------------------------------------------------------------------

def create_user(
    name: str,
    username: str,
    email: str,
    password_hash: str,
    role: str = 'user',
    registration_no: Optional[str] = None
) -> int:
    """Create a new user. Role must be 'user' or 'admin'."""
    role = role.lower()
    if role not in ('user', 'admin', 'student'):
        raise ValueError("Role must be 'user' or 'admin'")
    if role == 'student':
        role = 'user'
    name = name.strip()
    username = username.strip()
    email = email.strip().lower()
    reg_clean = registration_no.strip().upper() if registration_no and registration_no.strip() else None

    sql = 'INSERT INTO users(name, username, email, password_hash, role, registration_no) VALUES (?, ?, ?, ?, ?, ?)'
    return insert_and_get_id(sql, (name, username, email, password_hash, role, reg_clean))


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a user by numeric primary key ID."""
    return fetch_one('SELECT * FROM users WHERE id = ?', (user_id,))


def get_user_by_identifier(identifier: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user by username, email, or registration number (case-insensitive)."""
    if not identifier or not str(identifier).strip():
        return None
    raw = str(identifier).strip()
    clean_lower = raw.lower()
    clean_upper = raw.upper()
    return fetch_one(
        'SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ? OR UPPER(registration_no) = ?',
        (clean_lower, clean_lower, clean_upper)
    )


def get_user_by_username_or_email(identifier: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user by username, email, or registration number (case-insensitive)."""
    return get_user_by_identifier(identifier)


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Backward-compatible lookup by username."""
    return get_user_by_identifier(username)


def update_user_password(user_id_or_username, new_password_hash: str):
    """Update password hash for a user by id or username."""
    if isinstance(user_id_or_username, int):
        execute_query('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id_or_username))
    else:
        execute_query('UPDATE users SET password_hash = ? WHERE LOWER(username) = ?', (new_password_hash, str(user_id_or_username).strip().lower()))


def list_users(role: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all registered users, optionally filtered by role."""
    if role:
        return fetch_all('SELECT id, name, username, email, registration_no, role, created_at FROM users WHERE role = ? ORDER BY id DESC', (role.lower(),))
    return fetch_all('SELECT id, name, username, email, registration_no, role, created_at FROM users ORDER BY id DESC')


def count_users() -> int:
    """Return total count of registered users."""
    row = fetch_one('SELECT COUNT(*) AS cnt FROM users')
    return row['cnt'] if row else 0


# ------------------------------------------------------------------------------
# People CRUD (Students & Teachers)
# ------------------------------------------------------------------------------

def list_people(
    person_type: Optional[str] = None,
    active_only: bool = True,
    exclude_user_id: Optional[int] = None,
    exclude_name: Optional[str] = None,
    exclude_regno: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List people with optional filters.
    Supports excluding the currently logged-in user by ID, Name, or Registration Number to prevent self-review.
    Supports searching by name or registration number.
    """
    query = '''
    SELECT p.*, u.username AS linked_username, u.email AS linked_email
    FROM people p
    LEFT JOIN users u ON p.linked_user_id = u.id
    WHERE 1=1
    '''
    params = []

    if person_type:
        query += ' AND LOWER(p.type) = ?'
        params.append(person_type.strip().lower())

    if active_only:
        query += ' AND p.active = 1'

    if exclude_user_id is not None:
        query += ' AND (p.linked_user_id IS NULL OR p.linked_user_id != ?)'
        params.append(exclude_user_id)

    if exclude_name:
        query += ' AND LOWER(p.name) != ?'
        params.append(exclude_name.strip().lower())

    if exclude_regno and str(exclude_regno).strip():
        query += ' AND (p.registration_no IS NULL OR UPPER(p.registration_no) != ?)'
        params.append(str(exclude_regno).strip().upper())

    if search_query and search_query.strip():
        term = f"%{search_query.strip().lower()}%"
        query += ' AND (LOWER(p.name) LIKE ? OR LOWER(COALESCE(p.registration_no, "")) LIKE ? OR LOWER(p.department) LIKE ?)'
        params.extend([term, term, term])

    query += ' ORDER BY p.name ASC'
    return fetch_all(query, tuple(params))


def get_person(person_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve person by primary key ID."""
    return fetch_one('SELECT * FROM people WHERE id = ?', (person_id,))


def get_person_by_regno(registration_no: str) -> Optional[Dict[str, Any]]:
    """Retrieve person by registration number."""
    if not registration_no or not str(registration_no).strip():
        return None
    return fetch_one(
        'SELECT * FROM people WHERE UPPER(registration_no) = ?',
        (str(registration_no).strip().upper(),)
    )


def add_person(
    name: str,
    person_type: str,
    department: str,
    registration_no: Optional[str] = None,
    linked_user_id: Optional[int] = None
) -> int:
    """Add a student or teacher to people table."""
    p_type = person_type.strip().lower()
    if p_type not in ('student', 'teacher'):
        raise ValueError("Person type must be 'student' or 'teacher'")
    name = name.strip()
    dept = department.strip()
    reg = registration_no.strip().upper() if registration_no and registration_no.strip() else None

    if not name or not dept:
        raise ValueError("Name and department/course are required")

    sql = 'INSERT INTO people (name, registration_no, type, department, active, linked_user_id) VALUES (?, ?, ?, ?, 1, ?)'
    return insert_and_get_id(sql, (name, reg, p_type, dept, linked_user_id))


def update_person(
    person_id: int,
    name: str,
    department: str,
    person_type: Optional[str] = None,
    registration_no: Optional[str] = None,
    linked_user_id: Optional[int] = None
):
    """Update person details."""
    name = name.strip()
    dept = department.strip()
    reg = registration_no.strip().upper() if registration_no and registration_no.strip() else None

    if not name or not dept:
        raise ValueError("Name and department/course are required")

    if person_type:
        p_type = person_type.strip().lower()
        if p_type not in ('student', 'teacher'):
            raise ValueError("Person type must be 'student' or 'teacher'")
        execute_query(
            'UPDATE people SET name = ?, registration_no = ?, department = ?, type = ?, linked_user_id = ? WHERE id = ?',
            (name, reg, dept, p_type, linked_user_id, person_id)
        )
    else:
        execute_query(
            'UPDATE people SET name = ?, registration_no = ?, department = ?, linked_user_id = ? WHERE id = ?',
            (name, reg, dept, linked_user_id, person_id)
        )


def set_person_active(person_id: int, active: bool):
    """Activate or deactivate a person."""
    execute_query('UPDATE people SET active = ? WHERE id = ?', (1 if active else 0, person_id))


def count_people(person_type: Optional[str] = None, active_only: bool = False) -> int:
    """Count students or teachers."""
    query = 'SELECT COUNT(*) AS cnt FROM people WHERE 1=1'
    params = []
    if person_type:
        query += ' AND LOWER(type) = ?'
        params.append(person_type.strip().lower())
    if active_only:
        query += ' AND active = 1'
    row = fetch_one(query, tuple(params))
    return row['cnt'] if row else 0


# ------------------------------------------------------------------------------
# Student Directory Analytics & Summary
# ------------------------------------------------------------------------------

def get_students_summary(search_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve master student directory with evaluation metrics:
    - ID, Name, Registration No, Department, Status
    - Total reviews received
    - Average rating
    Supports searching by student name or registration number.
    """
    query = '''
    SELECT
        p.id AS student_id,
        p.name AS student_name,
        p.registration_no,
        p.department,
        p.active,
        p.linked_user_id,
        u.username AS linked_username,
        COUNT(r.id) AS total_reviews,
        ROUND(AVG(r.rating), 2) AS average_rating
    FROM people p
    LEFT JOIN users u ON p.linked_user_id = u.id
    LEFT JOIN reviews r ON p.id = r.person_id
    WHERE LOWER(p.type) = 'student'
    '''
    params = []

    if search_query and search_query.strip():
        term = f"%{search_query.strip().lower()}%"
        query += ' AND (LOWER(p.name) LIKE ? OR LOWER(COALESCE(p.registration_no, "")) LIKE ? OR LOWER(p.department) LIKE ?)'
        params.extend([term, term, term])

    query += ' GROUP BY p.id, p.name, p.registration_no, p.department, p.active, p.linked_user_id, u.username ORDER BY p.name ASC'
    return fetch_all(query, tuple(params))


def get_student_reviews(student_id: int) -> List[Dict[str, Any]]:
    """Retrieve all reviews received by a specific student."""
    query = '''
    SELECT
        r.id AS review_id,
        r.rating,
        r.review_text,
        r.created_at,
        r.updated_at,
        u.name AS reviewer_name,
        u.username AS reviewer_username,
        u.email AS reviewer_email,
        p.name AS student_name,
        p.registration_no AS student_regno
    FROM reviews r
    JOIN users u ON r.reviewer_id = u.id
    JOIN people p ON r.person_id = p.id
    WHERE r.person_id = ?
    ORDER BY r.updated_at DESC, r.id DESC
    '''
    return fetch_all(query, (student_id,))


def get_teachers_summary(search_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve faculty directory with evaluation metrics:
    - ID, Name, Department, Status
    - Total reviews received
    - Average rating
    """
    query = '''
    SELECT
        p.id AS teacher_id,
        p.name AS teacher_name,
        p.department,
        p.active,
        p.linked_user_id,
        u.username AS linked_username,
        COUNT(r.id) AS total_reviews,
        ROUND(AVG(r.rating), 2) AS average_rating
    FROM people p
    LEFT JOIN users u ON p.linked_user_id = u.id
    LEFT JOIN reviews r ON p.id = r.person_id
    WHERE LOWER(p.type) = 'teacher'
    '''
    params = []

    if search_query and search_query.strip():
        term = f"%{search_query.strip().lower()}%"
        query += ' AND (LOWER(p.name) LIKE ? OR LOWER(p.department) LIKE ?)'
        params.extend([term, term])

    query += ' GROUP BY p.id, p.name, p.department, p.active, p.linked_user_id, u.username ORDER BY p.name ASC'
    return fetch_all(query, tuple(params))


def get_person_detail(person_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve comprehensive evaluation dossier for a specific person (Student or Teacher)
    for the Admin Person Detail View. Includes average rating, total reviews,
    5-star breakdown, and all received reviews with reviewer details.
    """
    person = get_person(person_id)
    if not person:
        return None

    reviews = fetch_all('''
    SELECT
        r.id AS review_id,
        r.rating,
        r.review_text,
        r.created_at,
        r.updated_at,
        u.name AS reviewer_name,
        u.username AS reviewer_username,
        u.email AS reviewer_email
    FROM reviews r
    JOIN users u ON r.reviewer_id = u.id
    WHERE r.person_id = ?
    ORDER BY r.updated_at DESC, r.id DESC
    ''', (person_id,))

    total_reviews = len(reviews)
    avg_rating = round(sum(r['rating'] for r in reviews) / total_reviews, 2) if total_reviews > 0 else 0.0

    breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        rt = int(r['rating'])
        if rt in breakdown:
            breakdown[rt] += 1

    return {
        'id': person['id'],
        'name': person['name'],
        'registration_no': person.get('registration_no'),
        'type': person['type'],
        'department': person['department'],
        'active': bool(person['active']),
        'linked_user_id': person.get('linked_user_id'),
        'total_reviews': total_reviews,
        'average_rating': avg_rating,
        'breakdown': breakdown,
        'reviews': reviews
    }


def get_top_reviewed_people(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve top reviewed students and faculty members based on review counts."""
    query = '''
    SELECT
        p.id,
        p.name,
        p.type,
        p.registration_no,
        p.department,
        COUNT(r.id) AS review_count,
        ROUND(AVG(r.rating), 2) AS average_rating
    FROM people p
    JOIN reviews r ON p.id = r.person_id
    GROUP BY p.id, p.name, p.type, p.registration_no, p.department
    ORDER BY review_count DESC, average_rating DESC
    LIMIT ?
    '''
    return fetch_all(query, (limit,))


def get_recent_feedback_activity(limit: int = 6) -> List[Dict[str, Any]]:
    """Retrieve recent feedback activity feed for the Admin Analytics dashboard."""
    query = '''
    SELECT
        r.id,
        r.rating,
        r.review_text,
        r.updated_at,
        u.name AS reviewer_name,
        p.name AS target_name,
        p.type AS target_type,
        p.registration_no AS target_regno
    FROM reviews r
    JOIN users u ON r.reviewer_id = u.id
    JOIN people p ON r.person_id = p.id
    ORDER BY r.updated_at DESC, r.id DESC
    LIMIT ?
    '''
    return fetch_all(query, (limit,))


# Backward-compatible faculty helpers
def list_faculty(active_only: bool = True) -> List[Dict[str, Any]]:
    return list_people(person_type='teacher', active_only=active_only)

def add_faculty(name: str, department: str) -> int:
    return add_person(name=name, person_type='teacher', department=department)

def set_faculty_active(faculty_id: int, active: bool):
    set_person_active(faculty_id, active)


# ------------------------------------------------------------------------------
# Reviews CRUD & Business Logic
# ------------------------------------------------------------------------------

def submit_or_update_review(reviewer_id: int, person_id: int, rating: int, review_text: str) -> int:
    """
    Submit or update a review.
    - Prevents self-review:
      - If person is linked to reviewer account
      - If person has the same registration number as reviewer
      - If person has the same name as reviewer
    - If user reviews the same person again, updates existing review (duplicate prevention).
    - Ensures rating is between 1 and 5.
    """
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5 stars.")
    review_text = review_text.strip()
    if not review_text:
        raise ValueError("Written review comment cannot be empty.")

    # Validate person
    person = get_person(person_id)
    if not person:
        raise ValueError("Selected person does not exist.")
    if not person.get('active', 1):
        raise ValueError("This person is currently inactive and cannot receive reviews.")

    # Validate reviewer & check self-review
    reviewer = get_user_by_id(reviewer_id)
    if not reviewer:
        raise ValueError("Invalid reviewer session.")

    # Self-review checks
    if person.get('linked_user_id') == reviewer_id:
        raise ValueError("Self-review is not permitted. You cannot review your own profile.")

    # Registration number match check
    p_reg = str(person.get('registration_no') or '').strip().upper()
    r_reg = str(reviewer.get('registration_no') or '').strip().upper()
    if p_reg and r_reg and p_reg == r_reg:
        raise ValueError("Self-review is not permitted. You cannot review yourself using the same registration number.")

    # Name match check
    if person.get('name', '').strip().lower() == reviewer.get('name', '').strip().lower():
        raise ValueError("Self-review is not permitted. You cannot review yourself.")

    # Upsert query compatible with both SQLite (3.24+) and PostgreSQL
    sql = '''
    INSERT INTO reviews (reviewer_id, person_id, rating, review_text, created_at, updated_at)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT(reviewer_id, person_id)
    DO UPDATE SET
        rating = excluded.rating,
        review_text = excluded.review_text,
        updated_at = CURRENT_TIMESTAMP
    '''
    execute_query(sql, (reviewer_id, person_id, rating, review_text))
    return 1


def submit_feedback(student_id: int, faculty_id: int, course: str, rating: int, comments: str) -> int:
    """Backward-compatible helper for legacy tests/endpoints."""
    text = f"[{course}] {comments}" if course else comments
    return submit_or_update_review(student_id, faculty_id, rating, text)


def get_user_review_for_person(reviewer_id: int, person_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve existing review submitted by a specific user for a specific person."""
    return fetch_one(
        'SELECT * FROM reviews WHERE reviewer_id = ? AND person_id = ?',
        (reviewer_id, person_id)
    )


def count_user_reviews(reviewer_id: int) -> int:
    """Count how many reviews a user has submitted."""
    row = fetch_one('SELECT COUNT(*) AS cnt FROM reviews WHERE reviewer_id = ?', (reviewer_id,))
    return row['cnt'] if row else 0


def fetch_admin_reviews(
    person_type: Optional[str] = None,
    person_name: Optional[str] = None,
    person_id: Optional[int] = None,
    rating: Optional[int] = None,
    date_filter: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch reviews with full join details for the Admin Reviews Table and Filters.
    Includes registration numbers for students.
    """
    query = '''
    SELECT
        r.id AS review_id,
        r.reviewer_id,
        u.name AS reviewer_name,
        u.username AS reviewer_username,
        u.email AS reviewer_email,
        u.registration_no AS reviewer_regno,
        p.id AS person_id,
        p.name AS reviewed_person,
        p.registration_no AS reviewed_person_regno,
        p.type AS reviewed_person_type,
        p.department AS reviewed_person_department,
        r.rating,
        r.review_text,
        r.created_at,
        r.updated_at
    FROM reviews r
    JOIN users u ON r.reviewer_id = u.id
    JOIN people p ON r.person_id = p.id
    WHERE 1=1
    '''
    params = []

    # Type filter: All / Students / Teachers
    if person_type and person_type.lower() in ('student', 'teacher'):
        query += ' AND LOWER(p.type) = ?'
        params.append(person_type.lower())

    # Specific person ID filter
    if person_id is not None:
        query += ' AND p.id = ?'
        params.append(person_id)

    # Person name filter
    if person_name and person_name.strip() and person_name != 'All':
        query += ' AND p.name = ?'
        params.append(person_name.strip())

    # Rating filter
    if rating is not None and rating in (1, 2, 3, 4, 5):
        query += ' AND r.rating = ?'
        params.append(rating)

    # Date filter
    if date_filter and date_filter != 'All':
        engine = get_engine()
        if date_filter == 'Today':
            if engine == 'postgres':
                query += " AND r.created_at >= CURRENT_DATE"
            else:
                query += " AND DATE(r.created_at) = DATE('now')"
        elif date_filter == 'Last 7 Days':
            if engine == 'postgres':
                query += " AND r.created_at >= CURRENT_DATE - INTERVAL '7 days'"
            else:
                query += " AND DATE(r.created_at) >= DATE('now', '-7 days')"
        elif date_filter == 'Last 30 Days':
            if engine == 'postgres':
                query += " AND r.created_at >= CURRENT_DATE - INTERVAL '30 days'"
            else:
                query += " AND DATE(r.created_at) >= DATE('now', '-30 days')"
        elif len(date_filter) == 10 and '-' in date_filter:
            if engine == 'postgres':
                query += " AND DATE(r.created_at) = ?::date"
            else:
                query += " AND DATE(r.created_at) = ?"
            params.append(date_filter)

    # Search keyword filter (searches reviewer, target person, registration number, comment)
    if search_query and search_query.strip():
        term = f"%{search_query.strip().lower()}%"
        query += ''' AND (
            LOWER(u.name) LIKE ? OR
            LOWER(u.username) LIKE ? OR
            LOWER(u.email) LIKE ? OR
            LOWER(COALESCE(u.registration_no, "")) LIKE ? OR
            LOWER(p.name) LIKE ? OR
            LOWER(COALESCE(p.registration_no, "")) LIKE ? OR
            LOWER(p.department) LIKE ? OR
            LOWER(r.review_text) LIKE ?
        )'''
        params.extend([term, term, term, term, term, term, term, term])

    query += ' ORDER BY r.updated_at DESC, r.id DESC'
    return fetch_all(query, tuple(params))


def fetch_feedback(student_id=None, faculty_id=None) -> List[Dict[str, Any]]:
    """Backward-compatible helper returning list of feedback dicts."""
    reviews = fetch_admin_reviews()
    res = []
    for r in reviews:
        if student_id is not None and r['reviewer_id'] != student_id:
            continue
        if faculty_id is not None and r['person_id'] != faculty_id:
            continue
        res.append({
            'id': r['review_id'],
            'student': r['reviewer_username'],
            'student_name': r['reviewer_name'],
            'faculty': r['reviewed_person'],
            'department': r['reviewed_person_department'],
            'course': 'General',
            'rating': r['rating'],
            'comments': r['review_text'],
            'created_at': str(r['created_at'])
        })
    return res


def delete_review(review_id: int) -> bool:
    """Delete a review by ID (Admin feature)."""
    rowcount = execute_query('DELETE FROM reviews WHERE id = ?', (review_id,))
    return rowcount > 0


def get_kpis() -> Dict[str, Any]:
    """Calculate real-time KPIs for Admin Dashboard."""
    total_reviews_row = fetch_one('SELECT COUNT(*) AS cnt, AVG(rating) AS avg_rating FROM reviews')
    total_reviews = total_reviews_row['cnt'] if total_reviews_row else 0
    raw_avg = total_reviews_row['avg_rating'] if total_reviews_row and total_reviews_row['avg_rating'] is not None else 0.0
    avg_rating = round(float(raw_avg), 2)

    total_users = count_users()
    total_students = count_people(person_type='student')
    total_teachers = count_people(person_type='teacher')

    # Rating distribution breakdown (1 to 5 stars)
    dist_rows = fetch_all('SELECT rating, COUNT(*) AS cnt FROM reviews GROUP BY rating')
    dist_map = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for dr in dist_rows:
        dist_map[dr['rating']] = dr['cnt']

    # Type distribution
    type_rows = fetch_all('''
        SELECT p.type, COUNT(r.id) AS cnt
        FROM reviews r
        JOIN people p ON r.person_id = p.id
        GROUP BY p.type
    ''')
    type_map = {'student': 0, 'teacher': 0}
    for tr in type_rows:
        if tr['type']:
            type_map[tr['type'].lower()] = tr['cnt']

    return {
        'total_reviews': total_reviews,
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'average_rating': avg_rating,
        'rating_distribution': dist_map,
        'reviews_by_type': type_map
    }


def dashboard_stats() -> Dict[str, Any]:
    """Backward-compatible dashboard stats."""
    kpi = get_kpis()
    teachers = fetch_all('''
        SELECT p.name AS faculty, COUNT(r.id) AS responses, ROUND(AVG(r.rating), 2) AS avg_rating
        FROM people p
        LEFT JOIN reviews r ON r.person_id = p.id
        WHERE p.type = 'teacher'
        GROUP BY p.id, p.name
        ORDER BY p.name
    ''')
    return {
        'students': kpi['total_users'],
        'feedback_count': kpi['total_reviews'],
        'average_rating': kpi['average_rating'],
        'faculty_stats': teachers
    }
