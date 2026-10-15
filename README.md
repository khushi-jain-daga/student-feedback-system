# Student Feedback Management System 🎓

A complete web application built with **Python, Streamlit, SQLite, and PBKDF2 salted password authentication**. Ready for both local development and deployment on **Streamlit Community Cloud**.

---

## 🌟 Key Features

- **Role-Based Authentication:** Dedicated portals for students and administrators.
- **Security:** Salted PBKDF2 password hashing (260,000 SHA-256 iterations) with timing-safe comparison (`hmac.compare_digest`).
- **Student Portal:**
  - Self-registration with input validation.
  - Submit ratings (1–5 stars) and qualitative feedback per faculty & course.
  - Personal feedback submission history table.
- **Admin Dashboard:**
  - Real-time statistics (total students, feedback count, aggregate rating).
  - Faculty rating comparison bar chart.
  - Filterable feedback table with instant CSV export.
  - Faculty directory management (add new faculty, enable/disable status).
- **Relational Persistence:** SQLite with foreign keys and index optimization. Zero external database server needed.
- **Cloud Ready:** Works seamlessly with Streamlit Community Cloud Secrets and environment variables.

---

## 🚀 Streamlit Community Cloud Deployment Guide

Deploy this project on Streamlit Community Cloud in 3 steps:

### Step 1: Push Code to GitHub

1. Create a new repository on [GitHub](https://github.com/new) (e.g. `student-feedback-system`). Keep it **Public** (required for free Streamlit Cloud) or Private (if your Streamlit Cloud account allows it).
2. Open your terminal in this project folder and run:
   ```bash
   git add .
   git commit -m "Prepare repository for Streamlit Community Cloud deployment"
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2. Click **Create app** (or **New app**).
3. Fill in the repository details:
   - **Repository:** `<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Customize if desired (e.g. `student-feedback-portal.streamlit.app`).

### Step 3: Configure Admin Secrets (Critical)

Before or immediately after deploying, configure your administrator credentials:

1. In the deployment modal (or in **Settings** → **Secrets** from the deployed app's kebab menu `...`), open the **Secrets** editor.
2. Paste the following TOML snippet and customize your password:
   ```toml
   ADMIN_PASSWORD = "YourSecureAdminPassword123"

   # Optional customizations:
   ADMIN_USERNAME = "admin"
   ADMIN_NAME = "System Administrator"
   ADMIN_EMAIL = "admin@feedback.local"
   ```
3. Click **Save**. Streamlit Cloud will automatically reboot the app with your admin credentials active!
4. Sign in at your public URL with:
   - **Username:** `admin`
   - **Password:** The password you defined in `ADMIN_PASSWORD`

---

## 💻 Local Development Setup

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
cd <YOUR_REPOSITORY_NAME>

# (Optional) Create and activate a virtual environment
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Configure Local Credentials
You can provide the administrator password using any of these methods:

- **Option A (Local `.env` file):**
  Create a `.env` file in the project root:
  ```env
  ADMIN_PASSWORD=YourLocalAdminPass123
  ```
  *(Note: `.env` is ignored by git and will never be committed).*

- **Option B (Local Streamlit secret):**
  Create `.streamlit/secrets.toml`:
  ```toml
  ADMIN_PASSWORD = "YourLocalAdminPass123"
  ```
  *(Note: `.streamlit/secrets.toml` is ignored by git and will never be committed).*

- **Option C (Terminal Environment Variable):**
  - **Windows PowerShell:** `$env:ADMIN_PASSWORD="YourLocalAdminPass123"`
  - **Windows CMD:** `set ADMIN_PASSWORD=YourLocalAdminPass123`
  - **macOS / Linux:** `export ADMIN_PASSWORD="YourLocalAdminPass123"`

### 4. Run the Application
```bash
python -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🗄️ Database Architecture

The application uses SQLite with foreign keys enabled (`PRAGMA foreign_keys = ON`). The database file `feedback.db` is created automatically on startup.

```text
+------------------------------------+       +------------------------------------+
|               users                |       |              faculty               |
+------------------------------------+       +------------------------------------+
| id (PK, AUTOINCREMENT)             |       | id (PK, AUTOINCREMENT)             |
| username (TEXT, UNIQUE, NOCASE)    |       | name (TEXT, UNIQUE, NOCASE)        |
| full_name (TEXT)                   |       | department (TEXT)                  |
| email (TEXT, UNIQUE, NOCASE)       |       | active (INTEGER, 0/1)              |
| password_hash (TEXT)               |       +-----------------+------------------+
| role ('student' | 'admin')         |                         |
| created_at (TIMESTAMP)             |                         | 1:N
+-----------------+------------------+                         |
                  |                                            |
                  | 1:N                                        |
                  |          +-------------------------+       |
                  +--------> |        feedback         | <-----+
                             +-------------------------+
                             | id (PK, AUTOINCREMENT)  |
                             | student_id (FK -> users)|
                             | faculty_id (FK -> facult|
                             | course (TEXT)           |
                             | rating (INT, 1-5)       |
                             | comments (TEXT)         |
                             | created_at (TIMESTAMP)  |
                             +-------------------------+
```

### Note on Streamlit Cloud Persistence
Streamlit Community Cloud provides an ephemeral container filesystem. While SQLite persists data during active user sessions, rebooting or waking up the app from long inactivity may recreate the database cleanly. This makes the project ideal for demonstrations, academic submissions, and portfolio showcases.

---

## 🧪 Running Unit Tests

Run the comprehensive test suite locally:
```bash
python -m unittest discover -s tests -v
```

Tests cover:
- Student registration, validation, and collision prevention.
- PBKDF2 password hashing uniqueness and salt randomization.
- Feedback submission, filtering, and aggregate metric calculation.
- Admin credential synchronization and password rotation.

---

## 🛡️ Security & Git Hygiene

- **`.gitignore`:** Configured to strictly block `feedback.db`, `*.db`, `.env`, `.streamlit/secrets.toml`, local caches, and OS files.
- **Admin Password Rotation:** If you change `ADMIN_PASSWORD` in Streamlit Cloud Secrets, the system automatically synchronizes the stored admin hash on next boot.
- **Timing Attacks Defense:** Password verification uses `hmac.compare_digest` to prevent side-channel timing attacks.

---

## 🎓 Academic / Viva Highlights

- **Framework:** Streamlit for reactive frontend rendering in pure Python.
- **Relational Data Integrity:** SQLite schema enforces table constraints (`CHECK(rating BETWEEN 1 AND 5)`, `CHECK(role IN ('student','admin'))`, foreign keys).
- **Authentication Pattern:** Industry-standard PBKDF2 HMAC-SHA256 with 16-byte cryptographically secure random salts.
- **12-Factor App Compatibility:** Secrets and configurations decoupled from code using environment variables and Streamlit Cloud Secrets.
