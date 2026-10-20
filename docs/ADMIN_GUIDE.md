# Administrator Guide — Student Feedback Management System

This comprehensive guide details all administrative controls, analytics capabilities, directory management workflows, and moderation features available in the **Student Feedback Management System**.

---

## 🛡️ Security Warnings & Operational Guidelines

> [!WARNING]
> **Master Credential Security:**
> - The administrator master account has total oversight over evaluations, reviewer identities, and directory statuses.
> - **Never share the admin password.**
> - Never commit `.env` or Streamlit Secrets containing `ADMIN_PASSWORD` to any public repository.
> - Always terminate administrator sessions by clicking **Logout** when finished.

---

## 1. Accessing the Admin Portal

1. Open the application landing page.
2. Under the **🔐 Sign In** tab:
   - **Username or Email:** Enter `admin` (or the configured `ADMIN_USERNAME`).
   - **Password:** Enter the master password defined in your `.env` or Streamlit Cloud Secrets.
3. Click **Sign In to Portal**.
4. The system recognizes the `admin` role and loads the **Admin Portal** shell with a specialized dark-navy sidebar navigation:
   - `📊 Dashboard`
   - `📝 Reviews`
   - `👥 Manage People`
   - `👤 Users`
   - `📥 Export`
   - `🚪 Logout`

---

## 2. Executive Dashboard (KPIs & Analytics)

Upon login, the **Admin Dashboard** provides high-level institutional visibility:

### 2.1 Responsive 5-KPI Header
- **TOTAL REVIEWS:** Real-time count of all active evaluation submissions.
- **REGISTERED USERS:** Total user accounts registered in the portal.
- **TOTAL STUDENTS:** Total verified student records in the master directory.
- **TOTAL TEACHERS:** Total faculty members registered in the directory.
- **AVERAGE RATING:** Aggregate institutional feedback score (calculated out of 5.00).

### 2.2 Visual Analytics
- **Reviews by Type (Student vs Teacher):** Interactive bar chart comparing student peer evaluations against faculty reviews.
- **Rating Distribution (1–5 Stars):** Frequency chart displaying the count of 1-star, 2-star, 3-star, 4-star, and 5-star submissions.

### 2.3 Activity Monitoring & Rankings
- **Recent Feedback Activity Feed:** Real-time chronological timeline displaying the latest reviews, showing evaluator name, target person, target category badge, star rating, feedback excerpt, and submission timestamp.
- **Top Reviewed People:** Dynamic table ranking individuals receiving the highest review volume along with their individual average scores.

---

## 3. Reviews Management Page

Navigate to **📝 Reviews** in the sidebar to inspect, filter, or moderate evaluations.

### 3.1 Multi-Dimensional Filter Bar
The top control panel includes:
1. **Review Type:** Filter by `All`, `Student`, or `Teacher`.
2. **Person Name:** Select an individual from a sorted dropdown of all directory entries.
3. **Rating:** Filter by star rating (`All`, `5 Stars`, `4 Stars`, `3 Stars`, `2 Stars`, `1 Star`).
4. **Date Filter:** Filter by time horizon (`All`, `Today`, `Last 7 Days`, `Last 30 Days`, or pick a `Custom Date`).
5. **Search Input:** Real-time text search across student names, registration numbers (e.g. `23BCON0028`), reviewer names, email addresses, departments, or review comments.
6. **🔄 Reset Filters Button:** Restores all search and filter dropdowns to their default states in a single click.

### 3.2 Reviews Table
The table presents clean, structured columns:
- **Reviewer:** Reviewer full name and `@username`.
- **Reviewed Person:** Full name and registration number (if student).
- **Type:** Category badge (`Student` or `Teacher`).
- **Rating:** Visual star symbols (`★★★★★`).
- **Review:** Truncated preview of comments.
- **Date:** Formatted timestamp (`YYYY-MM-DD HH:MM`).

### 3.3 Full Review Inspection (Dossier View)
Under **🔍 View Complete Review**:
- Select any review from the dropdown list.
- A card displays:
  - Target individual's name and department.
  - Reviewer's full name, username, and verified email address.
  - Numeric and academic rating label (e.g. `★★★★☆ (4 — Very Good)`).
  - Exact submission and last update timestamps.
  - Complete, un-truncated written commentary.

### 3.4 Moderating Inappropriate Reviews
Under **🗑️ Delete Review**:
- Admins can permanently remove inappropriate, offensive, or policy-violating reviews.
- Check the safety confirmation: `I confirm I want to permanently delete this review.`
- Click **Delete Inappropriate Review**. The submission is permanently purged, and all KPIs/average ratings are automatically re-calculated.

---

## 4. Manage People & Directory Management

Navigate to **👥 Manage People** to maintain student and teacher records and inspect comprehensive individual dossiers.

### 4.1 Tab 1: Student Directory & Analytics
- **Search:** Search master students by name or registration number.
- **Status Filter:** Filter by `All`, `Active Only`, or `Inactive Only`.
- **Directory Table:** Displays Name, Registration Number, Department, Total Reviews received, Average Rating, and Active Status.

#### Student Dossier & Reviews Received (Person Detail View)
1. Select any student in the **Select Student to Inspect** dropdown.
2. The detailed dossier card renders:
   - **Student Identity:** Name, Registration Number, Department, and Status Badge.
   - **Metrics:** Average Rating (e.g. `4.50 ★`) and Total Reviews count.
   - **5-Star to 1-Star Breakdown:** Detailed counts for 5★, 4★, 3★, 2★, and 1★.
   - **Status Controls:** Click **Activate Student** or **Deactivate Student** (deactivated students are hidden from review dropdowns).
   - **Edit Details:** Expand the edit panel to update student name, registration number, or department.
   - **Reviews Received:** Displays individual review cards with reviewer names, star ratings, full comments, and submission dates.

### 4.2 Tab 2: Faculty Directory
- Displays all teachers, departments, total reviews, and average ratings.
- **Faculty Dossier:** Select any teacher to view their average rating, total reviews, 5★ to 1★ breakdown, and review cards.
- Status toggle (**Activate/Deactivate**) and edit forms for faculty details.

### 4.3 Tab 3 & 4: Add Student & Add Teacher
- **Add Student:** Register a student with Full Name, Registration Number, and Department.
- **Add Teacher:** Register a new faculty member with Full Name and Department.

---

## 5. Users Management Page

Navigate to **👤 Users** in the sidebar:
- Search registered user accounts by name, username, email, or registration number.
- Table columns: `Name`, `Username / Email`, `Registration Number`, `Role`, `Created Date`, `Status`.
- **Security Guarantee:** Password hashes are strictly omitted and never sent to the client.

---

## 6. Export Data to CSV

Navigate to **📥 Export** in the sidebar to download compliance and archiving reports:
- **Export Reviews:**
  - Choose dataset: `All Reviews`, `Student Reviews`, or `Teacher Reviews`.
  - Displays total matching records count.
  - Click **⬇️ Download [Dataset] CSV**.
  - Generated CSV includes Review ID, Reviewer Name, Username, Email, Target Person, Registration Number, Type, Department, Rating, Review Comment, and Submission Dates.
- **Export Master Directory:**
  - Displays total directory records.
  - Click **⬇️ Download People Directory CSV**.
  - Generated CSV includes Person ID, Name, Registration Number, Type, Department, and Active Status.

---

## 7. Logging Out

Click **🚪 Logout** at the bottom of the sidebar to clear administrator session tokens and return to the public landing page.
