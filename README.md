# Student Feedback Management System — Complete Mini Project

A working local web application with **Python, Streamlit, SQLite, and password-based authentication**. No MySQL server is required.

## Features
- Student account registration and sign-in
- Salted PBKDF2 password hashing; student/admin roles
- Faculty rating (1–5), comments, and subject/course submission
- Personal feedback history
- Admin summary, average rating, faculty-wise graph
- Filterable feedback, CSV export, faculty add/enable/disable
- SQLite relational database with foreign keys

## Requirements
- Python 3.10 or newer
- Windows, macOS, or Linux

## Installation
1. Extract this folder and open the terminal inside it.
2. Create a virtual environment (optional): `python -m venv .venv`
3. Activate on Windows PowerShell: `.venv\Scripts\Activate.ps1` (if PowerShell blocks this, skip activation and use your system Python). On macOS/Linux: `source .venv/bin/activate`
4. Run `python -m pip install -r requirements.txt`
5. Set an admin password **before the first launch**:
   - Windows PowerShell: `$env:ADMIN_PASSWORD="YourStrongAdminPass123"`
   - Windows CMD: `set ADMIN_PASSWORD=YourStrongAdminPass123`
   - macOS/Linux: `export ADMIN_PASSWORD='YourStrongAdminPass123'`
6. Run `python -m streamlit run app.py`
7. Open `http://localhost:8501` (or the URL displayed in the terminal).

## Demo walkthrough
1. Click **Student Registration**. Create a student account.
2. Log in as that student; select a faculty, course, rating, and comment, then submit.
3. Open **My History** to confirm data was saved.
4. Log out. Sign in with username `admin` and the password set in the environment.
5. View analytics, filter entries, export CSV, and add another faculty.

## Database schema
- `users(id, username, full_name, email, password_hash, role, created_at)`
- `faculty(id, name, department, active)`
- `feedback(id, student_id, faculty_id, course, rating, comments, created_at)`

Relations: `feedback.student_id -> users.id`, `feedback.faculty_id -> faculty.id`.

SQLite creates `feedback.db` on first launch. Three sample faculty entries are initialized (example names can be edited from the Admin dashboard).

## Test
`python -m unittest discover -s tests -v`

## Viva explanation
- **Frontend/UI:** Streamlit widgets render HTML in a browser.
- **Backend:** Python handles form validation and inserts/queries.
- **Connectivity:** Built-in `sqlite3` opens the database file and parameterized SQL is used.
- **Auth:** PBKDF2-SHA256 with random salt; `hmac.compare_digest` verifies passwords.
- **Authorization:** UI routes users to student or admin screens based on their database role.
- **Queries:** INSERT creates a response, SELECT+JOIN displays it, GROUP BY provides faculty statistics.

## Limitations
For a classroom/local demonstration. Not production-hardened: no password recovery, email verification, session expiry policy, audit logging, or rate limiting. Use unique admin credentials. Changing `ADMIN_PASSWORD` after creation does **not** reset the existing admin password. To start from scratch during development, stop the app and delete `feedback.db` (this deletes all data).
