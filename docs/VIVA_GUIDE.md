# College Viva Voce Preparation Guide

A curated question-and-answer guide for the **Student Feedback Management System**, designed to help you confidently answer technical questions during your project viva examination.

---

### Q1. What is the objective of your project?
**Answer:** The objective is to build a secure, web-based platform that allows authenticated students to submit structured feedback for peers and faculty members, while guaranteeing complete confidentiality by ensuring submitted reviews and reviewer identities are accessible exclusively to administrators.

---

### Q2. Why did you use Streamlit for this project?
**Answer:** Streamlit is an open-source Python framework that allows rapid development of reactive, data-driven web applications. It seamlessly binds Python backend logic, authentication states, and database queries to a modern web interface without requiring complex frontend JavaScript build pipelines.

---

### Q3. What is SQLite and why is it used?
**Answer:** SQLite is a lightweight, zero-configuration, serverless relational database engine stored as a single disk file (`feedback.db`). It is ideal for local development, prototyping, and automated unit testing because it requires no separate database server setup.

---

### Q4. Why do you need PostgreSQL / Supabase in production?
**Answer:** Cloud platforms like Streamlit Community Cloud use ephemeral container instances that reset their local filesystems on restart, which would wipe an SQLite file. PostgreSQL hosted on Supabase provides persistent, cloud-hosted, ACID-compliant storage that supports concurrent connections and permanent data retention.

---

### Q5. What is database connectivity in your application?
**Answer:** Database connectivity refers to how the Python backend connects to and executes queries against a database. In our app, `database.py` detects the presence of the `DATABASE_URL` environment variable. If present, it establishes a connection to PostgreSQL using `psycopg2`; otherwise, it connects to local SQLite via Python's built-in `sqlite3` driver.

---

### Q6. What is the difference between Authentication and Authorization?
**Answer:**
- **Authentication:** Verifying *who* the user is (e.g., verifying username/email and password during login).
- **Authorization:** Determining *what* the authenticated user is allowed to do (e.g., normal users can only give feedback and view their own profile, while admins can view all reviews, manage directory records, and export data).

---

### Q7. How are passwords stored in your database?
**Answer:** Passwords are never stored as plaintext. They are stored as salted cryptographic hashes generated using the **PBKDF2** algorithm with **SHA-256** and **260,000 iterations**, prefixed by a cryptographically secure 16-byte random salt.

---

### Q8. Why shouldn't passwords be stored as plain text?
**Answer:** If the database is compromised, leaked, or inspected by unauthorized personnel, plaintext passwords would immediately expose all user accounts and enable credential-stuffing attacks across other platforms. Hashing protects credentials because it is computationally infeasible to reverse a cryptographic hash.

---

### Q9. What is password hashing?
**Answer:** Hashing is a one-way mathematical function that transforms an input string (password) into a fixed-length string of bytes (digest). It cannot be decrypted back into the original password; instead, during login, the entered password is hashed with the stored salt and compared to the stored hash.

---

### Q10. What is PBKDF2 and why is it preferred over simple MD5 or SHA-256?
**Answer:** PBKDF2 (Password-Based Key Derivation Function 2) applies a pseudorandom function (SHA-256) repeatedly over thousands of iterations (we use 260,000). This intentional computational cost makes brute-force dictionary attacks and GPU-accelerated rainbow table cracking infeasible, unlike simple MD5 or single-round SHA-256 which can be cracked in microseconds.

---

### Q11. What are Primary Keys and Foreign Keys?
**Answer:**
- **Primary Key:** A column (or set of columns) that uniquely identifies each row in a table (e.g., `users.id`, `people.id`, `reviews.id`).
- **Foreign Key:** A column that establishes a link between data in two tables by referencing the primary key of another table (e.g., `reviews.reviewer_id` references `users.id`, and `reviews.person_id` references `people.id`).

---

### Q12. Explain your `users` table.
**Answer:** The `users` table stores account credentials: `id` (Primary Key), `name`, `username` (Unique), `email` (Unique), `password_hash`, `registration_no` (Unique, optional for staff), `role` (`'user'` or `'admin'`), and `created_at`.

---

### Q13. Explain your `reviews` table.
**Answer:** The `reviews` table stores feedback submissions: `id` (Primary Key), `reviewer_id` (Foreign Key referencing `users.id`), `person_id` (Foreign Key referencing `people.id`), `rating` (1 to 5), `review_text` (comments), `created_at`, and `updated_at`. It has a composite unique constraint `UNIQUE(reviewer_id, person_id)`.

---

### Q14. How do you prevent self-review in your application?
**Answer:** Self-review is prevented at both the UI and database levels across three vectors:
1. By User ID: Verifying `person.linked_user_id != user.id`.
2. By Registration Number: Verifying `person.registration_no != user.registration_no`.
3. By Full Name: Verifying `person.name != user.name`.
The UI dropdown excludes the logged-in student, and the backend raises a `ValueError` if an attempted self-review is submitted.

---

### Q15. How do you prevent duplicate reviews for the same person?
**Answer:** The database enforces a `UNIQUE(reviewer_id, person_id)` constraint on the `reviews` table. When a user reviews someone they have already reviewed, the backend executes an `UPSERT` (`INSERT ... ON CONFLICT(reviewer_id, person_id) DO UPDATE SET rating = excluded.rating, review_text = excluded.review_text`), updating the existing review instead of creating a duplicate row.

---

### Q16. Who can see submitted reviews?
**Answer:** Only authorized users with the `admin` role can see submitted reviews, average scores, and individual comments. Normal users receive only a success confirmation (`✓ Review submitted successfully`) and have zero visibility into any reviews.

---

### Q17. What is Role-Based Access Control (RBAC)?
**Answer:** RBAC is a security model where access rights are assigned based on defined roles. In our system, the router checks `st.session_state.user['role']`. If it is `'admin'`, the user is granted access to the executive dashboard, review moderation, and directory management; otherwise, they are restricted to the student feedback and profile views.

---

### Q18. What is Supabase?
**Answer:** Supabase is an open-source cloud backend-as-a-service built around PostgreSQL. It provides managed PostgreSQL database hosting, automated connection pooling, and web-based database inspection tools.

---

### Q19. Why do we use environment variables and secrets?
**Answer:** Storing sensitive values (such as `DATABASE_URL` and `ADMIN_PASSWORD`) in environment variables or `.streamlit/secrets.toml` separates configuration from code. This ensures sensitive credentials are never committed to public version control repositories like GitHub.

---

### Q20. What happens when `DATABASE_URL` exists vs. when it does not?
**Answer:** When `DATABASE_URL` exists, the application initializes the PostgreSQL engine using `psycopg2` and targets the cloud database. When `DATABASE_URL` is omitted, the app falls back to local SQLite (`feedback.db`). The business logic and queries remain identical.

---

### Q21. How does the CSV export feature work?
**Answer:** The administrator triggers an export from the **Export** tab. The database queries matching review or directory records, converts them into a Pandas DataFrame, serializes them to CSV format via `.to_csv(index=False).encode('utf-8')`, and streams the file to the browser via Streamlit's `st.download_button`.

---

### Q22. How is the average rating calculated?
**Answer:** The average rating is calculated using the SQL aggregate function `AVG(rating)` grouped by target person ID: `SELECT ROUND(AVG(rating), 2) AS average_rating FROM reviews WHERE person_id = ?`. In the admin dashboard, overall average is computed across all reviews in the table.

---

### Q23. What are the limitations of your system?
**Answer:** Realistic limitations include:
1. No university Single Sign-On (SSO) integration (uses self-contained PBKDF2 accounts).
2. No automated email OTP verification during registration.
3. Faculty members are entered manually by administrators rather than synchronized with an automated university HR database.
4. Streamlit is designed for dashboard workflows and is best suited for departmental or college-level scale rather than massive concurrent enterprise applications.

---

### Q24. What future enhancements can be added?
**Answer:**
1. College SSO / LDAP integration with Google Workspace or Microsoft Azure AD.
2. Email verification using one-time passwords (OTP).
3. NLP-based AI sentiment analysis to categorize constructive suggestions and flag abusive language.
4. Cross-departmental comparative performance benchmarking.
5. Native mobile application built in Flutter or React Native.

---

### Q25. Why did you use a Relational Database instead of NoSQL?
**Answer:** Student feedback requires strong referential integrity, rigid relational constraints (`UNIQUE(reviewer_id, person_id)`, foreign key cascades on user deletion), and complex aggregation queries (`AVG`, `COUNT`, `GROUP BY`). Relational databases (SQLite/PostgreSQL) provide ACID guarantees and structured joins that prevent data inconsistency.

---

### Q26. What happens after a student clicks "Submit Review"?
**Answer:**
1. The app validates that the comment is non-empty and rating is 1–5.
2. The backend performs self-review verification.
3. An atomic SQL `UPSERT` is executed against the database.
4. Session state updates `review_submitted = True`.
5. The UI displays the success banner (`✓ Review submitted successfully`).
6. No database contents or other reviews are revealed to the student.

---

### Q27. How does the Admin Dashboard calculate ratings breakdown (5★ to 1★)?
**Answer:** In `database.py`, the `get_person_detail(person_id)` function fetches all reviews for that person, iterates through the ratings, and tallies frequency counts into a dictionary `{5: count, 4: count, 3: count, 2: count, 1: count}`. This is rendered on the Person Detail Dossier so administrators see exact distributions.

---

### Q28. Explain the complete system architecture in brief.
**Answer:** The user interacts with the application via a web browser. The presentation layer (`app.py`) manages UI components and session state. It delegates user authentication to `auth.py` and data operations to `database.py`. The database layer connects to either SQLite or PostgreSQL, enforcing relational constraints and returning data structured with Pandas for display.
