# Production Deployment Guide

This guide provides end-to-end instructions for deploying the **Student Feedback Management System** into public production using **GitHub**, **Supabase (Cloud PostgreSQL)**, and **Streamlit Community Cloud**.

---

## Architecture Overview

```mermaid
graph LR
    Dev[Developer / Local] -->|git push| GitHub[GitHub Repository<br>khushi-jain-daga/student-feedback-system]
    GitHub -->|Auto Deploy CI/CD| Streamlit[Streamlit Community Cloud<br>Public Web URL]
    Streamlit -->|SSL Connection / DATABASE_URL| Supabase[(Supabase Cloud PostgreSQL<br>Persistent ACID Database)]
```

---

## SECTION 1: GitHub Repository Setup

The official repository for this project is hosted at:
[https://github.com/khushi-jain-daga/student-feedback-system](https://github.com/khushi-jain-daga/student-feedback-system)

### Step 1.1: Verify Clean Local Git Status
In your terminal inside the project directory:
```bash
git status --short
```
Verify that no `.env`, `feedback.db`, `test.db`, or temporary files are untracked or staged for commit.

### Step 1.2: Configure Remote and Branch
```bash
git branch -M main
git remote add origin https://github.com/khushi-jain-daga/student-feedback-system.git
```
*(If `origin` already exists, verify with `git remote -v` or update with `git remote set-url origin https://github.com/khushi-jain-daga/student-feedback-system.git`)*

### Step 1.3: Commit and Push
```bash
git add .
git commit -m "feat: complete student feedback management system"
git push -u origin main
```

---

## SECTION 2: Cloud PostgreSQL Database Setup on Supabase

Using Supabase ensures persistent, ACID-compliant cloud storage so that feedback data is preserved even when Streamlit server instances restart.

### Step 2.1: Create Project on Supabase
1. Go to [supabase.com](https://supabase.com/) and click **Sign in** (authenticate with GitHub).
2. Click **New project** and select your organization.
3. Configure your project:
   - **Name:** `student-feedback-db`
   - **Database Password:** Enter a strong password and **record it securely**.
   - **Region:** Choose the region nearest to your target users (e.g., *South Asia (Mumbai)* or *US East*).
   - **Pricing Plan:** Free Tier.
4. Click **Create new project** and allow 1 to 2 minutes for the database instance to initialize.

### Step 2.2: Obtain Connection String (`DATABASE_URL`)
1. In your Supabase dashboard, click **Project Settings** (gear icon) in the left sidebar.
2. Under Settings, select **Database**.
3. Scroll down to the **Connection string** panel.
4. Click the **URI** tab.
5. Select Mode: **Session** (or Transaction pooler on port 6543 / direct 5432).
6. Copy the connection string:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
7. Replace `[YOUR-PASSWORD]` with the password you set in Step 2.1.
   *(Note: If your password contains special characters such as `@`, `#`, or `$`, URL-encode them, e.g., `@` becomes `%40`).*

---

## SECTION 3: Streamlit Community Cloud Setup

Streamlit Community Cloud provides free, high-performance hosting with automated Continuous Deployment (CD).

### Step 3.1: Sign In
1. Visit [share.streamlit.io](https://share.streamlit.io/).
2. Click **Sign in with GitHub** and authorize Streamlit.

### Step 3.2: Create New App
1. Click the **Create app** (or **Deploy an app**) button.
2. Select **I have an app already**.
3. Fill in the repository coordinates:
   - **Repository:** `khushi-jain-daga/student-feedback-system`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Customize your public subdomain:
     ```
     student-feedback-system.streamlit.app
     ```

---

## SECTION 4: Configuring Secrets on Streamlit Cloud

> [!IMPORTANT]
> Never hardcode passwords or database URLs in `app.py`. Streamlit Cloud provides a secure secret manager.

1. Before launching, click **Advanced settings...** (or navigate to App Settings → **Secrets**).
2. Paste the following configuration in TOML format:

```toml
# ==============================================================================
# Streamlit Cloud Production Secrets (DO NOT COMMIT REAL VALUES TO GIT)
# ==============================================================================

# 1. Supabase Cloud PostgreSQL Connection:
DATABASE_URL = "postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres"

# 2. Administrator Master Login Password (minimum 8 characters):
ADMIN_PASSWORD = "YourSecureProductionAdminPassword123"

# 3. Optional Admin Account Metadata:
ADMIN_USERNAME = "admin"
ADMIN_NAME = "System Administrator"
ADMIN_EMAIL = "admin@example.com"
```

3. Replace the placeholder values with your actual Supabase URL and chosen administrator password.
4. Click **Save**.

---

## SECTION 5: Deploy Application

1. Click **Deploy!**.
2. Streamlit Cloud will automatically:
   - Clone the `main` branch from your GitHub repository.
   - Install all dependencies listed in `requirements.txt` (`streamlit`, `pandas`, `python-dotenv`, `psycopg2-binary`).
   - Run `app.py`, which detects `DATABASE_URL` and connects to Supabase PostgreSQL.
   - Execute table creation migrations (`users`, `people`, `reviews`).
   - Import the 62 verified student records from `students_master.json`.
   - Seed the administrator account.
3. Once the build completes, the app will display:
   ```
   https://student-feedback-system.streamlit.app
   ```

---

## SECTION 6: Post-Deployment Smoke Testing

Perform the following smoke tests on your public URL to verify production readiness:

1. **Unauthenticated Landing Page:**
   - Open `https://<your-subdomain>.streamlit.app` in an incognito/private browser window.
   - Verify that the hero banner, privacy guidelines, and Sign In / Create Account tabs render cleanly.
2. **User Registration:**
   - Under **Create Account**, register a student account (e.g., Name: `TEST STUDENT`, Username: `teststudent`, Email: `test@univ.edu`, RegNo: `23BCON1740`, Password: `Password@123`).
   - Verify the success alert displays.
3. **User Authentication & Evaluation:**
   - Sign in with the registered credentials.
   - Verify sidebar displays `Logged in as: TEST STUDENT`.
   - Select **Student**, pick `AMIT AGARWAL — 23BCON0028`, select 5 stars, enter a comment, and click **Submit Review**.
   - Verify the confirmation banner appears: `✓ Review submitted successfully`.
   - Verify self-review prevention: Confirm `TEST STUDENT — 23BCON1740` does NOT appear in the dropdown.
4. **Duplicate Review Updating:**
   - Select `AMIT AGARWAL` again.
   - Verify the update notice appears: `You have already reviewed this person. Your existing review can be updated.`
   - Change rating to 4 stars and click **Update Review**.
5. **Normal User Privacy Check:**
   - Open **My Profile**.
   - Confirm only account details are visible. Confirm NO reviews by others, average scores, or admin tools appear.
   - Click **Logout**.
6. **Administrator Control Center:**
   - Log in using `admin` and your configured `ADMIN_PASSWORD`.
   - Confirm the 5 KPI cards load on the Dashboard.
   - Confirm the review submitted in Step 3 appears in the Recent Feedback Activity feed.
   - Go to **Reviews**: test the filters and search.
   - Go to **Manage People**: select `AMIT AGARWAL` and verify the detailed dossier with 5★–1★ breakdown and review cards.
   - Go to **Export**: download CSV files to ensure data streams successfully.
   - Click **Logout**.
7. **Cloud Persistence Check:**
   - Open your Supabase dashboard → **Table Editor**.
   - Confirm that the `users`, `people`, and `reviews` tables contain the records created above.

---

## SECTION 7: Troubleshooting Common Deployment Issues

| Problem | Root Cause | Solution |
| :--- | :--- | :--- |
| **`psycopg2.OperationalError: could not translate host name`** | Incorrect `DATABASE_URL` or missing pooler subdomain. | Double-check URI from Supabase Project Settings → Database. Ensure format starts with `postgresql://`. |
| **`psycopg2.OperationalError: password authentication failed`** | Incorrect password or unescaped special characters. | Re-enter password. If it contains symbols like `@` or `:`, URL-encode them (`%40`, `%3A`). |
| **`ModuleNotFoundError: No module named 'psycopg2'`** | Missing driver in `requirements.txt`. | Ensure `psycopg2-binary>=2.9.9` is present in `requirements.txt` and pushed to GitHub. |
| **Admin login fails with "Invalid credentials"** | `ADMIN_PASSWORD` not configured in Streamlit Secrets. | Open App Settings → Secrets, ensure `ADMIN_PASSWORD` has at least 8 characters, and restart app. |
| **App runs on SQLite instead of Supabase** | `DATABASE_URL` is empty, commented out, or misspelled in Secrets. | Verify key name is exactly `DATABASE_URL` under Streamlit Cloud Secrets. |
| **Streamlit timeout during App deployment** | Cloud resource throttling. | Check Streamlit Cloud manage logs panel. Clear cache and reboot app. |
