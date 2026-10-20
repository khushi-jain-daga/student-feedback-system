# User Guide — Student Feedback Management System

Welcome to the **Student Feedback Management System (SFMS)**. This guide outlines how student reviewers and standard users can create an account, submit constructive feedback, edit past evaluations, and manage their profile.

---

## 🔒 Important Privacy Notice

> [!NOTE]
> **Strict Evaluation Confidentiality:**
> - Regular users **CANNOT** see reviews submitted by other users.
> - Regular users **CANNOT** view average ratings, individual comments, admin analytics, or who reviewed whom.
> - Submitted evaluations are encrypted in transit and accessible solely to authorized academic administrators.

---

## Step-by-Step Instructions

### 1. Access the Application
Open the application link in any modern web browser (Google Chrome, Firefox, Safari, Edge) on your computer, laptop, tablet, or smartphone:
```
http://localhost:8501/
```
*(or your institution's public Streamlit URL)*

---

### 2. Create an Account (First-Time Users)
1. On the landing page, click the **📝 Create Account** tab.
2. Fill in your details:
   - **Full Name:** Enter your full legal name (e.g. `PRIYANKA SANGWA`).
   - **Username:** Choose a unique username (minimum 3 characters, e.g. `priyankas`).
   - **Email Address:** Your institutional or personal email (e.g. `priyanka@student.univ.edu`).
   - **Registration Number:** Enter your official student registration number (e.g. `23BCON1710`).
   - **Password:** Create a secure password (minimum 8 characters).
   - **Confirm Password:** Re-enter the identical password.
3. Click the **Create Account** button.
4. You will see a success confirmation: `Account created successfully! You can now log in using the 'Sign In' tab.`

---

### 3. Log In
1. Switch to the **🔐 Sign In** tab on the landing page.
2. Enter your **Username or Email** in the first field.
3. Enter your **Password** in the second field (click the eye icon to toggle visibility).
4. Click **Sign In to Portal**.
5. Once authenticated, your personalized **User Dashboard** will load.

---

### 4. Submit Feedback (Give Review)

Your sidebar will display:
- **SFMS Portal**
- Navigation: `✍️ Give Review`, `👤 My Profile`, `🚪 Logout`
- Logged-in credentials: Your Full Name, `@username`, and your linked Registration Number badge.

#### Step 1: Choose Review Type
Select whether you wish to evaluate a peer student or a faculty member:
- `[ Student ]`
- `[ Teacher ]`

#### Step 2: Select Person
Open the searchable dropdown to select the target:
- **For Students:** The dropdown formats every student as:
  ```
  STUDENT NAME — REGISTRATION NUMBER
  Example: AMIT AGARWAL — 23BCON0028
  ```
  You can type either the student's name or their registration number to find them instantly.
- **For Teachers:** Formatted as `TEACHER NAME — DEPARTMENT`.

> [!IMPORTANT]
> **Self-Review Prevention:** You cannot review yourself. If your account is linked to a registration number or matches an entry in the directory, your own name is automatically hidden from the dropdown and blocked on the server.

#### Step 3: Choose Rating
Use the visual star rating slider to assign a score from 1 to 5 stars:
- `★☆☆☆☆ (1 — Poor)`
- `★★☆☆☆ (2 — Fair)`
- `★★★☆☆ (3 — Good)`
- `★★★★☆ (4 — Very Good)`
- `★★★★★ (5 — Excellent)`

#### Step 4: Write Constructive Feedback
In the text box provided, type your observations and suggestions:
- Provide specific, objective, and respectful commentary.
- Highlight academic strengths and areas for continued development.

#### Step 5: Submit
Click the primary **Submit Review** button.

---

### 5. Submission Confirmation
Upon successful submission, you will see a clean confirmation banner:
```
✓ Review submitted successfully
Thank you for sharing your feedback.
```
Your review is securely recorded. Click **➕ Submit Another Review** to return to the form and evaluate another individual.

---

### 6. Updating an Existing Review (Duplicate Prevention)
The system prevents duplicate review clutter:
- If you select someone you previously evaluated, an alert will inform you:
  ```
  You have already reviewed this person. Your existing review can be updated.
  ```
- The form will automatically load your previous rating and comments.
- Modify your rating or text as desired and click **Update Review**.
- Your record is updated cleanly in the database without creating duplicate entries.

---

### 7. View Your Profile & Change Password
1. Click **👤 My Profile** in the left sidebar.
2. The **Account Profile** card displays:
   - Full Name
   - Username
   - Email
   - Registration Number
   - Account Role (`User`)
   - Account Created Date
3. To update your password:
   - Enter your **Current Password**.
   - Enter your **New Password** (minimum 8 characters).
   - Re-enter to **Confirm New Password**.
   - Click **Update Password**.

---

### 8. Log Out
When finished, click **🚪 Logout** in the sidebar to securely terminate your session.
