# Student Feedback Management System 🎓

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/Tests-15%2F15%20Passing-brightgreen.svg)](docs/TESTING.md)

A secure, institutional-grade web platform for structured peer and faculty evaluations. Built using **Python, Streamlit, and Relational Database Systems (SQLite / PostgreSQL)**, the platform guarantees complete student confidentiality by isolating evaluations strictly for administrative oversight while enforcing self-review prevention and automatic review updating.

---

## 📌 Overview

Traditional academic feedback systems rely on manual paper slips or generic online forms that fail to protect reviewer confidentiality, permit duplicate entries, and lack master directory validation. 

The **Student Feedback Management System (SFMS)** solves these challenges through a unified public web link with strict **Role-Based Access Control (RBAC)**:
- **Authenticated Students / Users:** Submit structured 1–5 star ratings and qualitative comments for peers and faculty members without fear of social retaliation.
- **Academic Administrators:** Gain real-time executive visibility through dynamic KPI cards, distribution charts, person detail dossiers, moderation tools, and one-click CSV export options.
- **Privacy Core:** Standard users can **never** view evaluations submitted by others, overall averages, individual commentary, or evaluator identities.

---

## ✨ Key Features

### 👤 Student / User Features
- **Secure Authentication:** Self-registration and login using either username or institutional email, secured with PBKDF2 SHA-256 salted password hashing.
- **Dual Review Surface:** Seamless toggle between evaluating a peer **Student** or a faculty **Teacher**.
- **Searchable Master Directory:** Pre-loaded with official students formatted strictly as `STUDENT NAME — REGISTRATION NUMBER` (e.g. `AMIT AGARWAL — 23BCON0028`).
- **Standardized Evaluation:** Visual 1 to 5 star rating scale paired with descriptive academic labels (`Poor`, `Fair`, `Good`, `Very Good`, `Excellent`) and rich qualitative text area.
- **Seamless Review Updates:** Submitting an evaluation for the same person automatically updates the existing record instead of cluttering the system with duplicate rows.
- **Triple-Vector Self-Review Prevention:** Prevents users from reviewing themselves by checking user ID, student registration number, and full name.
- **Strict Privacy Guarantee:** Immediate post-submission confirmation (`✓ Review submitted successfully`) with zero leakage of reviews or analytics.
- **Profile & Credential Management:** Personal account details card and password change module.

### 🛡️ Administrator Features
- **Executive KPI Dashboard:** Real-time metrics for Total Reviews, Registered Users, Total Students, Total Teachers, and Average Institutional Rating.
- **Visual Analytics:** Interactive charts for Reviews by Type (Student vs Teacher) and Rating Distribution (1–5 Stars).
- **Live Activity Feed:** Chronological monitoring feed showing recent submissions and top-reviewed individuals.
- **Multi-Dimensional Reviews Management:** Filter reviews by Type, Person Name, Rating, and Date horizon with keyword search and a one-click `🔄 Reset Filters` button.
- **Complete Review Dossier:** Inspect full review text, reviewer identity, registration numbers, and exact timestamps.
- **Review Moderation:** Permanently delete policy-violating comments with mandatory confirmation.
- **Student & Faculty Management:**
  - Searchable student directory with individual average ratings and total review counts.
  - **Person Detail Dossier:** 5-star down to 1-star breakdown bars and individual review cards received by any student or teacher.
  - Active/Inactive status toggles and detail editing.
  - Add new students or faculty members.
- **Users Directory:** Audit registered accounts without exposing password hashes.
- **CSV Data Export:** One-click download of All Reviews, Student Reviews, Teacher Reviews, and Master Directory in CSV format.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | [Streamlit](https://streamlit.io/) (v1.32+) | Reactive, modern SaaS user interface |
| **Backend Language** | Python 3.10+ | Business logic, authentication, and routing |
| **Local Database** | SQLite3 | Embedded, zero-configuration local persistence |
| **Cloud Database** | PostgreSQL 15+ ([Supabase](https://supabase.com/)) | Persistent, cloud-hosted relational storage |
| **Authentication** | PBKDF2 with SHA-256 (260,000 rounds) | Salted, non-reversible password hashing |
| **Data Analytics** | [Pandas](https://pandas.pydata.org/) | Dataframe manipulation, aggregation, and CSV serialization |
| **Styling** | Vanilla CSS3 + Google Fonts (`Plus Jakarta Sans`, `Inter`) | Modern, responsive institutional design system |

---

## 🏛️ System Architecture

```mermaid
graph TD
    Client[Web Browser - Desktop / Mobile] -->|HTTP / WebSocket| App[Streamlit Web App - app.py]
    
    subgraph Core Application Architecture
        App --> Auth[Authentication Layer - auth.py]
        App --> UserShell[User Dashboard: Give Feedback & Profile]
        App --> AdminShell[Admin Portal: KPIs, Reviews, Manage People, Export]
        
        Auth --> Security[PBKDF2 SHA-256 Hashing]
        UserShell --> Validation[Self-Review & Duplicate Check]
        AdminShell --> Moderation[Review Moderation & Dossier Engine]
    end
    
    subgraph Persistence Layer
        Validation --> DBAdapter[Database Layer - database.py]
        Moderation --> DBAdapter
        DBAdapter --> EngineCheck{DATABASE_URL Set?}
        EngineCheck -->|Yes| PostgreSQL[(Cloud PostgreSQL / Supabase)]
        EngineCheck -->|No| SQLite[(Local SQLite - feedback.db)]
    end
```

---

## 🔄 Application Flow

### Normal User Workflow:
1. **Register / Login:** User creates an account with Name, Email, Username, Password, and Registration Number, then signs in.
2. **Select Category:** Chooses to review a **Student** or a **Teacher**.
3. **Select Person:** Picks an individual from the verified directory (`NAME — REGISTRATION NUMBER`).
4. **Rate & Comment:** Selects 1–5 stars and provides constructive written feedback.
5. **Submit / Update:** Submits new feedback or updates an existing evaluation.
6. **Privacy Confirmation:** System confirms submission (`✓ Review submitted successfully`) without exposing other reviews.

### Administrator Workflow:
1. **Admin Login:** Authenticates using master administrator credentials.
2. **Dashboard Overview:** Monitors institutional KPIs and visual distribution charts.
3. **Reviews Inspection:** Filters, searches, reads full review text, or deletes inappropriate entries.
4. **Manage People:** Inspects individual student/teacher dossiers (average score, 5★ to 1★ breakdown, and review cards) and toggles active status.
5. **Export Data:** Generates and downloads structured CSV reports for offline analysis.

---

## 🗄️ Database Schema Summary

The database uses three normalized relational tables:
- **`users`:** User accounts, credentials, salted PBKDF2 password hashes, roles (`user`, `admin`), and registration numbers.
- **`people`:** Verified evaluation targets (students and teachers), departments, and active status flags. Includes 62 verified pre-seeded students.
- **`reviews`:** Review records linking reviewer to target person, with star rating (1–5), comment, and timestamps. Enforces `UNIQUE(reviewer_id, person_id)`.

*For complete table schemas, foreign key cascade behaviors, and indexes, refer to [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md).*

---

## 💻 Local Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/khushi-jain-daga/student-feedback-system.git
cd student-feedback-system
```

### 2. Create Virtual Environment
```bash
# Windows:
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example configuration:
```bash
# Windows:
copy .env.example .env

# macOS / Linux:
cp .env.example .env
```
Edit `.env` and set your master administrator password:
```env
DATABASE_URL=
ADMIN_PASSWORD=YourLocalAdminPassword123
ADMIN_USERNAME=admin
ADMIN_NAME=System Administrator
ADMIN_EMAIL=admin@example.com
```
*(Leave `DATABASE_URL` empty to run on local SQLite).*

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at **http://localhost:8501**.

---

## ⚙️ Environment Variables & Secrets Reference

| Variable Name | Required? | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Cloud Only | `postgresql://user:pass@host:5432/postgres` | PostgreSQL connection URI for Supabase cloud hosting. If empty, local SQLite is used. |
| `ADMIN_PASSWORD`| **Yes** | `AdminPass@123` | Master password for administrator portal login (minimum 8 characters). |
| `ADMIN_USERNAME`| Optional | `admin` | Administrator login username (defaults to `admin`). |
| `ADMIN_NAME` | Optional | `System Administrator` | Full display name for administrator account. |
| `ADMIN_EMAIL` | Optional | `admin@example.com` | Institutional administrator contact email. |

---

## 🌐 Cloud Production Deployment

The project is pre-configured for free, instant deployment on **Streamlit Community Cloud** backed by a **Supabase PostgreSQL** database:

1. **Push to GitHub:** Push your repository to [GitHub](https://github.com/khushi-jain-daga/student-feedback-system).
2. **Create Supabase Database:** Provision a free PostgreSQL project on [Supabase](https://supabase.com/) and copy the connection URI.
3. **Deploy on Streamlit Cloud:** Link your GitHub repository at [share.streamlit.io](https://share.streamlit.io/), configure Secrets (`DATABASE_URL`, `ADMIN_PASSWORD`), and deploy.

*For complete, step-by-step production setup and troubleshooting instructions, see [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md).*

---

## 🧪 Automated Testing

The repository includes a comprehensive automated test suite verifying core business logic, cryptography, database constraints, and Streamlit UI state machines:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Verified Test Suite Results:
```text
Ran 15 tests in 27.771s

OK
```
All **15 automated tests** pass cleanly with 100% compliance across registration, self-review blocking, upsert duplicate updates, role authorization, and AppTest UI renders.

*For detailed test breakdowns and testing methodology, see [docs/TESTING.md](docs/TESTING.md).*

---

## 🛡️ Security & Privacy Guarantees

- **Cryptographic Hashing:** Passwords hashed with PBKDF2 SHA-256 over 260,000 iterations with unique 16-byte random salts.
- **Reviewer Confidentiality:** Standard users have zero access to reviews submitted by peers or aggregate metrics.
- **Self-Review Prevention:** Triple-vector check enforces that students cannot review themselves via ID, registration number, or name.
- **Duplicate Prevention:** Database-level `UNIQUE(reviewer_id, person_id)` constraint ensures users can only update existing reviews.
- **Zero Exposed Secrets:** No passwords, database URLs, or API keys are committed to version control.

---

## 📸 Screenshots Overview

| Screen | Description | Reference |
| :--- | :--- | :--- |
| **Login & Register** | Modern two-column hero and tabbed authentication card | [docs/screenshots/login.png](docs/USER_GUIDE.md) |
| **Give Feedback** | 4-step card with review type toggle, searchable directory, and rating slider | [docs/screenshots/give_feedback.png](docs/USER_GUIDE.md) |
| **Admin Dashboard** | 5-KPI header row, distribution charts, and live feedback activity feed | [docs/screenshots/admin_dashboard.png](docs/ADMIN_GUIDE.md) |
| **Reviews Management** | Multi-dimensional filter bar, visual stars table, and deletion module | [docs/screenshots/reviews.png](docs/ADMIN_GUIDE.md) |
| **Student Dossier** | Comprehensive person detail view with 5★–1★ breakdown and review cards | [docs/screenshots/student_dossier.png](docs/ADMIN_GUIDE.md) |

---

## 📚 Complete Project Documentation

For detailed technical and academic documentation, refer to the guides in the `docs/` folder:

- 📄 [Academic Project Report (`docs/PROJECT_REPORT.md`)](docs/PROJECT_REPORT.md)
- 🗄️ [Database Schema & ER Diagram (`docs/DATABASE_SCHEMA.md`)](docs/DATABASE_SCHEMA.md)
- 👤 [Student Reviewer User Guide (`docs/USER_GUIDE.md`)](docs/USER_GUIDE.md)
- 🛡️ [Administrator Operational Guide (`docs/ADMIN_GUIDE.md`)](docs/ADMIN_GUIDE.md)
- 🚀 [Cloud Production Deployment Guide (`docs/DEPLOYMENT_GUIDE.md`)](docs/DEPLOYMENT_GUIDE.md)
- 🧪 [Automated Testing Strategy (`docs/TESTING.md`)](docs/TESTING.md)
- 🎓 [College Viva Voce Q&A Guide (`docs/VIVA_GUIDE.md`)](docs/VIVA_GUIDE.md)

---

## 📋 Project Status & Author

- **Status:** College Mini Project — Fully Completed & Production Ready
- **Author:** Khushi Jain Daga
- **License:** [MIT License](LICENSE)
