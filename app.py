"""Student Feedback Management System
A professional, institutional-grade feedback platform with secure authentication,
strict normal-user privacy guarantees, master student directory with registration numbers,
comprehensive analytics, and an advanced administrator control center.
"""
import datetime
from typing import Optional
import pandas as pd
import streamlit as st

import database
import auth

# ------------------------------------------------------------------------------
# Page Configuration & Design System
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Feedback Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cached application initialization (executes ONCE per Streamlit server process)
@st.cache_resource
def initialize_application():
    try:
        database.init_db()
        auth.seed_admin()
        print("[INIT] Application initialization complete.")
        return True
    except Exception as e:
        print(f"[INIT ERROR] Application initialization failed: {type(e).__name__}")
        raise

initialize_application()

# Custom SaaS Design System CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0f172a;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Landing Hero Section */
.landing-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0369a1 100%);
    padding: 2.8rem 2.4rem;
    border-radius: 16px;
    color: #ffffff;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.12);
    margin-bottom: 2rem;
}

.landing-badge {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 1rem;
}

.landing-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.8rem;
    color: #ffffff;
}

.landing-subtitle {
    font-size: 1.1rem;
    color: #cbd5e1;
    font-weight: 400;
    line-height: 1.6;
    max-width: 620px;
}

/* Institutional Card Container */
.ui-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
}

.ui-card-header {
    font-size: 1.2rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.5rem;
    letter-spacing: -0.01em;
}

.ui-card-sub {
    font-size: 0.88rem;
    color: #64748b;
    margin-bottom: 1.2rem;
    line-height: 1.5;
}

/* KPI Cards */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 1.2rem;
    margin-bottom: 2rem;
}

.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.4rem 1.3rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px -2px rgba(15, 23, 42, 0.06);
}

.kpi-label {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748b;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.kpi-sub {
    font-size: 0.8rem;
    color: #0284c7;
    font-weight: 500;
    margin-top: 0.4rem;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-student { background-color: #e0f2fe; color: #0369a1; }
.badge-teacher { background-color: #f1f5f9; color: #334155; }
.badge-admin   { background-color: #fef3c7; color: #92400e; }
.badge-user    { background-color: #f1f5f9; color: #475569; }
.badge-active  { background-color: #dcfce7; color: #15803d; }
.badge-inactive{ background-color: #fee2e2; color: #b91c1c; }

/* Review Card in Feed/Detail */
.review-item {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.review-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.review-reviewer {
    font-weight: 700;
    font-size: 0.95rem;
    color: #0f172a;
}

.review-date {
    font-size: 0.78rem;
    color: #94a3b8;
}

.review-stars {
    color: #f59e0b;
    font-size: 1rem;
    letter-spacing: 1px;
}

.review-text-box {
    font-size: 0.92rem;
    color: #334155;
    line-height: 1.6;
    background: #f8fafc;
    border-left: 3px solid #0284c7;
    padding: 0.85rem 1rem;
    border-radius: 6px;
    margin-top: 0.6rem;
}

/* Empty State Box */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: #f8fafc;
    border: 1.5px dashed #cbd5e1;
    border-radius: 14px;
    margin: 1.5rem 0;
}

.empty-state-icon {
    font-size: 2.2rem;
    color: #94a3b8;
    margin-bottom: 0.7rem;
}

.empty-state-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #334155;
    margin-bottom: 0.3rem;
}

.empty-state-text {
    font-size: 0.88rem;
    color: #64748b;
    max-width: 420px;
    margin: 0 auto;
}

/* Success Banner */
.success-banner {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 12px;
    padding: 1.8rem;
    text-align: center;
    margin: 1.5rem 0;
}
.success-banner-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #065f46;
    margin-bottom: 0.4rem;
}
.success-banner-sub {
    font-size: 0.95rem;
    color: #047857;
}

/* Buttons */
div.stButton > button {
    border-radius: 9px;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
    transition: all 0.2s ease;
}

div.stButton > button[kind="primary"] {
    background-color: #0f172a;
    border-color: #0f172a;
    color: #ffffff;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #1e293b;
    border-color: #1e293b;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# State Initialization
# ------------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "review_submitted" not in st.session_state:
    st.session_state.review_submitted = False

if "admin_active_tab" not in st.session_state:
    st.session_state.admin_active_tab = "Dashboard"

if "user_active_tab" not in st.session_state:
    st.session_state.user_active_tab = "Give Review"

# Review filter states for Reset button
if "rf_type" not in st.session_state:
    st.session_state.rf_type = "All"
if "rf_rating" not in st.session_state:
    st.session_state.rf_rating = "All"
if "rf_person" not in st.session_state:
    st.session_state.rf_person = "All"
if "rf_date" not in st.session_state:
    st.session_state.rf_date = "All"
if "rf_search" not in st.session_state:
    st.session_state.rf_search = ""


# ------------------------------------------------------------------------------
# Formatting Helpers
# ------------------------------------------------------------------------------
def format_datetime(val) -> str:
    """Safely format database timestamp for clean display."""
    if val is None:
        return "—"
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.strftime("%Y-%m-%d %H:%M")
    val_str = str(val)
    if len(val_str) >= 16:
        return val_str[:16].replace("T", " ")
    return val_str


def rating_stars(rating: int) -> str:
    """Render numeric rating as visual star symbols (e.g. ★★★★☆)."""
    r = int(rating or 0)
    return "★" * r + "☆" * (5 - r)


def rating_stars_label(rating: int) -> str:
    """Render star rating with textual academic descriptor."""
    labels = {
        1: "Poor",
        2: "Fair",
        3: "Good",
        4: "Very Good",
        5: "Excellent"
    }
    r = int(rating or 0)
    stars = "★" * r + "☆" * (5 - r)
    return f"{stars} ({r} — {labels.get(r, 'N/A')})"


# ==============================================================================
# VIEW 1: LANDING & AUTHENTICATION PAGE
# ==============================================================================
def render_landing_page():
    # Left / Right Responsive Layout
    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        st.markdown("""
        <div class="landing-hero">
            <div class="landing-badge">Institutional Evaluation Portal</div>
            <div class="landing-title">Student Feedback<br>Management System</div>
            <div class="landing-subtitle">
                A secure platform for structured peer and faculty feedback.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ui-card">
            <div class="ui-card-header">System Principles & Privacy</div>
            <div class="ui-card-sub">Engineered to foster transparent, constructive, and fair academic growth.</div>
            <div style="font-size:0.9rem; color:#475569; line-height:1.7;">
                <p style="margin-bottom:0.7rem;">
                    🔒 <strong>Strict Privacy:</strong> Individual reviews, ratings, and evaluator identities are accessible exclusively to authorized academic administrators.
                </p>
                <p style="margin-bottom:0.7rem;">
                    👥 <strong>Master Student Directory:</strong> Integrated official student directory identified by validated registration numbers.
                </p>
                <p style="margin-bottom:0.7rem;">
                    🛡️ <strong>Fairness Safeguards:</strong> Self-evaluations are strictly prohibited, and subsequent submissions automatically update your existing review without duplicates.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        auth_tab_login, auth_tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        # TAB 1: SIGN IN
        with auth_tab_login:
            st.markdown("#### Welcome Back")
            st.caption("Sign in with your registered username or institutional email address.")

            with st.form("login_form", clear_on_submit=False):
                login_id = st.text_input(
                    "Username or Email",
                    placeholder="e.g. user@university.edu or username"
                )
                login_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your account password"
                )
                submit_login = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)

            if submit_login:
                if not login_id.strip() or not login_password:
                    st.error("Please enter both your username/email and password.")
                else:
                    user_data = auth.authenticate(login_id.strip(), login_password)
                    if user_data:
                        st.session_state.user = user_data
                        st.session_state.review_submitted = False
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        # TAB 2: CREATE ACCOUNT
        with auth_tab_register:
            st.markdown("#### Create Account")
            st.caption("Register a new account to participate in academic reviews.")

            with st.form("register_form", clear_on_submit=True):
                reg_name = st.text_input("Full Name", placeholder="e.g. AMIT AGARWAL")
                reg_user = st.text_input("Username", placeholder="e.g. amitag (minimum 3 characters)")
                reg_email = st.text_input("Email Address", placeholder="e.g. amit.agarwal@university.edu")
                reg_no = st.text_input(
                    "Registration Number (Students only — e.g. 23BCON0028)",
                    placeholder="e.g. 23BCON0028"
                )
                reg_pass = st.text_input("Password (min 8 characters)", type="password")
                reg_confirm = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if submit_reg:
                if reg_pass != reg_confirm:
                    st.error("Passwords do not match. Please verify both password entries.")
                else:
                    try:
                        auth.register_user(
                            name=reg_name,
                            username=reg_user,
                            email=reg_email,
                            password=reg_pass,
                            role='user',
                            registration_no=reg_no.strip() if reg_no else None
                        )
                        st.success("Account created successfully! You can now log in using the 'Sign In' tab.")
                    except ValueError as err:
                        st.error(str(err))
                    except Exception as err:
                        st.error(f"Registration failed: {err}")


# ==============================================================================
# VIEW 2: NORMAL USER PORTAL
# ==============================================================================
def render_user_dashboard(user):
    # Sidebar App-Shell
    with st.sidebar:
        st.markdown("### 🎓 SFMS Portal")
        st.caption("Student Feedback System")
        st.divider()

        user_nav = st.radio(
            "Navigation",
            ["✍️ Give Review", "👤 My Profile", "🚪 Logout"],
            index=0 if st.session_state.user_active_tab in ("Give Review", "Give Feedback") else 1
        )

        if user_nav == "🚪 Logout":
            st.session_state.user = None
            st.session_state.review_submitted = False
            st.rerun()

        st.session_state.user_active_tab = "Give Review" if "Give" in user_nav else "My Profile"

        st.divider()
        st.markdown("**Logged in as:**")
        st.markdown(f"**{user['name']}**")
        st.caption(f"@{user['username']}")
        if user.get('registration_no'):
            st.markdown(f"<span class='badge badge-student'>{user['registration_no']}</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='badge badge-user'>Standard Account</span>", unsafe_allow_html=True)

    # PAGE: GIVE FEEDBACK
    if st.session_state.user_active_tab in ("Give Review", "Give Feedback"):
        st.markdown("## Give Feedback")
        st.caption("Share constructive feedback for a student or teacher.")

        # Post-submission Clean Success State
        if st.session_state.review_submitted:
            st.markdown("""
            <div class="success-banner">
                <div class="success-banner-title">✓ Review submitted successfully</div>
                <div class="success-banner-sub">Thank you for sharing your feedback.</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("➕ Submit Another Review", type="primary"):
                st.session_state.review_submitted = False
                st.rerun()
            return

        # Main Feedback Form Container
        col_center, _ = st.columns([1, 0.05])
        with col_center:
            st.markdown("""
            <div class="ui-card" style="max-width:850px;">
                <div class="ui-card-header">Step 1: Choose Review Type</div>
                <div class="ui-card-sub">Select whether you would like to evaluate a student peer or a faculty teacher.</div>
            """, unsafe_allow_html=True)

            # STEP 1: Review Type Toggle
            review_type_choice = st.radio(
                "Review Type",
                ["Student", "Teacher"],
                horizontal=True,
                help="Select whether you are submitting peer feedback for a student or teacher evaluation."
            )
            person_type = review_type_choice.lower()

            st.markdown("<hr style='border:none; border-top:1px solid #f1f5f9; margin:1.2rem 0;'>", unsafe_allow_html=True)

            # STEP 2: Select Person (Self-review prevention included)
            eligible_people = database.list_people(
                person_type=person_type,
                active_only=True,
                exclude_user_id=user['id'],
                exclude_name=user['name'],
                exclude_regno=user.get('registration_no')
            )

            if not eligible_people:
                st.markdown(f"""
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <div class="empty-state-title">No Active {review_type_choice}s Available</div>
                    <div class="empty-state-text">There are currently no other active {person_type}s available to evaluate.</div>
                </div>
                </div>
                """, unsafe_allow_html=True)
                return

            st.markdown("""
                <div class="ui-card-header">Step 2: Select Person</div>
                <div class="ui-card-sub">Search by name or registration number from the verified directory.</div>
            """, unsafe_allow_html=True)

            if person_type == "student":
                people_options = {
                    f"{p['name']} — {p.get('registration_no') or 'N/A'}": p
                    for p in eligible_people
                }
                dropdown_label = "Student Directory (Name — Registration Number)"
            else:
                people_options = {
                    f"{p['name']} — {p['department']}": p
                    for p in eligible_people
                }
                dropdown_label = "Teacher Directory (Name — Department)"

            selected_label = st.selectbox(dropdown_label, options=list(people_options.keys()))
            selected_person = people_options[selected_label]

            # Duplicate review check: seamless update policy
            existing_review = database.get_user_review_for_person(user['id'], selected_person['id'])
            if existing_review:
                st.info(
                    "You have already reviewed this person. Your existing review can be updated."
                )
                initial_rating = int(existing_review['rating'])
                initial_comment = str(existing_review['review_text'])
                submit_label = "Update Review"
            else:
                initial_rating = 5
                initial_comment = ""
                submit_label = "Submit Review"

            st.markdown("<hr style='border:none; border-top:1px solid #f1f5f9; margin:1.2rem 0;'>", unsafe_allow_html=True)

            with st.form("give_review_form"):
                # STEP 3: Rating (1 to 5 Stars with clear labels)
                st.markdown("""
                    <div class="ui-card-header">Step 3: Rating</div>
                    <div class="ui-card-sub">Select an objective rating reflecting your evaluation.</div>
                """, unsafe_allow_html=True)

                rating = st.select_slider(
                    "Rating Scale",
                    options=[1, 2, 3, 4, 5],
                    value=initial_rating,
                    format_func=rating_stars_label
                )

                st.markdown("<hr style='border:none; border-top:1px solid #f1f5f9; margin:1.2rem 0;'>", unsafe_allow_html=True)

                # STEP 4: Review text area
                st.markdown("""
                    <div class="ui-card-header">Step 4: Written Feedback</div>
                    <div class="ui-card-sub">Provide detailed, constructive, and respectful observations.</div>
                """, unsafe_allow_html=True)

                comment = st.text_area(
                    "Review / Comments",
                    value=initial_comment,
                    placeholder="Share constructive and respectful feedback...",
                    height=140
                )

                submit_btn = st.form_submit_button(submit_label, type="primary", use_container_width=True)

            if submit_btn:
                if not comment.strip():
                    st.error("Please provide written feedback before submitting.")
                else:
                    try:
                        database.submit_or_update_review(
                            reviewer_id=user['id'],
                            person_id=selected_person['id'],
                            rating=int(rating),
                            review_text=comment.strip()
                        )
                        st.session_state.review_submitted = True
                        st.rerun()
                    except ValueError as val_err:
                        st.error(str(val_err))
                    except Exception as err:
                        st.error(f"Failed to submit review: {err}")

            st.markdown("</div>", unsafe_allow_html=True)

    # PAGE: MY PROFILE
    elif st.session_state.user_active_tab == "My Profile":
        st.markdown("## My Profile")
        st.caption("Manage your verified identity and security credentials.")

        col_p1, col_p2 = st.columns([1.2, 1], gap="large")

        with col_p1:
            reg_display = user.get('registration_no') or 'Not Linked'
            created_str = format_datetime(user.get('created_at'))

            st.markdown(f"""
            <div class="ui-card">
                <div class="ui-card-header">Account Profile</div>
                <div class="ui-card-sub">Your registered credentials in the institutional feedback directory.</div>
                <div style="font-size:0.92rem; color:#334155; line-height:2;">
                    <div><strong>Full Name:</strong> {user['name']}</div>
                    <div><strong>Username:</strong> @{user['username']}</div>
                    <div><strong>Email:</strong> {user['email']}</div>
                    <div><strong>Registration Number:</strong> <code>{reg_display}</code></div>
                    <div><strong>Account Role:</strong> <span class="badge badge-user">{user['role'].title()}</span></div>
                    <div><strong>Account Created Date:</strong> {created_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_p2:
            st.markdown("""
            <div class="ui-card">
                <div class="ui-card-header">Security & Password</div>
                <div class="ui-card-sub">Update your account login password.</div>
            """, unsafe_allow_html=True)

            with st.form("change_password_form"):
                current_pw = st.text_input("Current Password", type="password")
                new_pw = st.text_input("New Password (min 8 chars)", type="password")
                confirm_pw = st.text_input("Confirm New Password", type="password")
                change_btn = st.form_submit_button("Update Password", type="primary", use_container_width=True)

            if change_btn:
                if new_pw != confirm_pw:
                    st.error("New passwords do not match.")
                elif len(new_pw) < 8:
                    st.error("New password must be at least 8 characters long.")
                else:
                    try:
                        auth.change_user_password(user['id'], current_pw, new_pw)
                        st.success("Your password has been updated successfully!")
                    except ValueError as err:
                        st.error(str(err))

            st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# VIEW 3: ADMINISTRATOR DASHBOARD
# ==============================================================================
def render_admin_dashboard(user):
    with st.sidebar:
        st.markdown("### 🛡️ Admin Portal")
        st.caption("Institutional Review Administration")
        st.divider()

        nav_choice = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 Reviews", "👥 Manage People", "👤 Users", "📥 Export", "🚪 Logout"],
            index=["Dashboard", "Reviews", "Manage People", "Users", "Export", "Logout"].index(st.session_state.admin_active_tab)
            if st.session_state.admin_active_tab in ["Dashboard", "Reviews", "Manage People", "Users", "Export"] else 0
        )

        clean_nav = nav_choice.split(" ", 1)[-1]
        if clean_nav == "Logout":
            st.session_state.user = None
            st.rerun()

        st.session_state.admin_active_tab = clean_nav

        st.divider()
        st.markdown("**Administrator:**")
        st.markdown(f"**{user['name']}**")
        st.caption(f"@{user['username']} • System Administrator")

    current_page = st.session_state.admin_active_tab

    # --------------------------------------------------------------------------
    # 1. ADMIN DASHBOARD (Home & KPI Overview)
    # --------------------------------------------------------------------------
    if current_page == "Dashboard":
        st.markdown("## Admin Dashboard")
        st.caption("Monitor feedback activity and manage the review system.")
        st.subheader("Administrative Dashboard", divider=False)

        kpis = database.get_kpis()

        # Responsive KPI Row
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-label">📊 Total Reviews</div>
                <div class="kpi-value">{kpis['total_reviews']}</div>
                <div class="kpi-sub">All submissions</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">👥 Registered Users</div>
                <div class="kpi-value">{kpis['total_users']}</div>
                <div class="kpi-sub">Active accounts</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🎓 Total Students</div>
                <div class="kpi-value">{kpis['total_students']}</div>
                <div class="kpi-sub">Directory master</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">👨‍🏫 Total Teachers</div>
                <div class="kpi-value">{kpis['total_teachers']}</div>
                <div class="kpi-sub">Faculty members</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">⭐ Average Rating</div>
                <div class="kpi-value">{'%.2f' % kpis['average_rating']}</div>
                <div class="kpi-sub">Out of 5.00</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Visual Analytics
        col_c1, col_c2 = st.columns(2, gap="large")

        with col_c1:
            st.markdown("##### 👥 Reviews by Type (Student vs Teacher)")
            type_df = pd.DataFrame([
                {"Target": "Student", "Submissions": kpis['reviews_by_type']['student']},
                {"Target": "Teacher", "Submissions": kpis['reviews_by_type']['teacher']}
            ])
            st.bar_chart(type_df.set_index("Target"), color="#0284c7")

        with col_c2:
            st.markdown("##### ⭐ Rating Distribution (1–5 Stars)")
            dist_df = pd.DataFrame([
                {"Rating": f"{k} Star{'s' if k > 1 else ''}", "Reviews": v}
                for k, v in kpis['rating_distribution'].items()
            ])
            st.bar_chart(dist_df.set_index("Rating"), color="#0f172a")

        st.divider()

        # Recent Feedback Activity & Top Reviewed People
        col_act1, col_act2 = st.columns([1.2, 1], gap="large")

        with col_act1:
            st.markdown("##### 🕒 Recent Feedback Activity")
            recent_activity = database.get_recent_feedback_activity(limit=5)
            if recent_activity:
                for act in recent_activity:
                    t_badge = "badge-student" if act['target_type'] == 'student' else "badge-teacher"
                    reg_text = f" ({act['target_regno']})" if act.get('target_regno') else ""
                    st.markdown(f"""
                    <div class="review-item">
                        <div class="review-item-header">
                            <div>
                                <span class="review-reviewer">{act['reviewer_name']}</span>
                                <span style="color:#64748b; font-size:0.85rem;"> evaluated </span>
                                <strong>{act['target_name']}{reg_text}</strong>
                                <span class="badge {t_badge}">{act['target_type'].title()}</span>
                            </div>
                            <span class="review-stars">{rating_stars(act['rating'])}</span>
                        </div>
                        <div class="review-text-box">{act['review_text']}</div>
                        <div class="review-date" style="margin-top:0.4rem;">{format_datetime(act['updated_at'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <div class="empty-state-title">No Reviews Submitted Yet</div>
                    <div class="empty-state-text">Recent feedback activities will display here once users submit evaluations.</div>
                </div>
                """, unsafe_allow_html=True)

        with col_act2:
            st.markdown("##### 🏆 Top Reviewed People")
            top_people = database.get_top_reviewed_people(limit=5)
            if top_people:
                top_df = pd.DataFrame([{
                    "Name": p['name'],
                    "Type": p['type'].title(),
                    "Identifier": p['registration_no'] or p['department'],
                    "Reviews": p['review_count'],
                    "Avg Rating": f"{p['average_rating']:.2f} ★"
                } for p in top_people])
                st.dataframe(top_df, hide_index=True, use_container_width=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <div class="empty-state-title">No Rankings Available</div>
                    <div class="empty-state-text">Top reviewed individuals will appear after evaluations are recorded.</div>
                </div>
                """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 2. ADMIN REVIEWS MANAGEMENT
    # --------------------------------------------------------------------------
    elif current_page == "Reviews":
        st.markdown("## Reviews Management")
        st.caption("Inspect, filter, search, read in full, or moderate inappropriate reviews.")

        # Top Filter Bar
        with st.container():
            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([1.2, 1.2, 1, 1.1, 0.9])

            with f_col1:
                filter_type = st.selectbox(
                    "Review Type",
                    options=["All", "Student", "Teacher"],
                    index=["All", "Student", "Teacher"].index(st.session_state.rf_type) if st.session_state.rf_type in ["All", "Student", "Teacher"] else 0
                )
                st.session_state.rf_type = filter_type

            with f_col2:
                all_people_names = sorted(list(set([p['name'] for p in database.list_people(active_only=False)])))
                person_opts = ["All"] + all_people_names
                selected_p_name = st.selectbox(
                    "Person Name",
                    options=person_opts,
                    index=person_opts.index(st.session_state.rf_person) if st.session_state.rf_person in person_opts else 0
                )
                st.session_state.rf_person = selected_p_name

            with f_col3:
                rating_opts = ["All", "5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"]
                selected_rating_label = st.selectbox(
                    "Rating",
                    options=rating_opts,
                    index=rating_opts.index(st.session_state.rf_rating) if st.session_state.rf_rating in rating_opts else 0
                )
                st.session_state.rf_rating = selected_rating_label
                filter_rating = int(selected_rating_label.split()[0]) if selected_rating_label != "All" else None

            with f_col4:
                date_opts = ["All", "Today", "Last 7 Days", "Last 30 Days", "Custom Date"]
                selected_date = st.selectbox(
                    "Date Filter",
                    options=date_opts,
                    index=date_opts.index(st.session_state.rf_date) if st.session_state.rf_date in date_opts else 0
                )
                st.session_state.rf_date = selected_date

            with f_col5:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Reset Filters", use_container_width=True):
                    st.session_state.rf_type = "All"
                    st.session_state.rf_person = "All"
                    st.session_state.rf_rating = "All"
                    st.session_state.rf_date = "All"
                    st.session_state.rf_search = ""
                    st.rerun()

            custom_date_str = None
            if selected_date == "Custom Date":
                picked = st.date_input("Select Date", value=datetime.date.today())
                custom_date_str = picked.strftime("%Y-%m-%d")

            search_text = st.text_input(
                "Search Reviews",
                value=st.session_state.rf_search,
                placeholder="Search name, registration number or reviewer..."
            )
            st.session_state.rf_search = search_text

        # Execute filtered query
        type_arg = filter_type.lower() if filter_type != "All" else None
        date_arg = custom_date_str if selected_date == "Custom Date" else selected_date

        reviews = database.fetch_admin_reviews(
            person_type=type_arg,
            person_name=selected_p_name if selected_p_name != "All" else None,
            rating=filter_rating,
            date_filter=date_arg,
            search_query=search_text
        )

        st.markdown(f"**Found {len(reviews)} review{'s' if len(reviews) != 1 else ''}**")

        if not reviews:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-title">No Reviews Found</div>
                <div class="empty-state-text">No reviews match your current search and filter criteria.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            table_records = []
            for r in reviews:
                target_desc = r['reviewed_person']
                if r['reviewed_person_type'] == 'student' and r.get('reviewed_person_regno'):
                    target_desc += f" ({r['reviewed_person_regno']})"

                # Truncate long reviews in table
                raw_text = r['review_text'] or ""
                trunc_text = (raw_text[:75] + "...") if len(raw_text) > 75 else raw_text

                table_records.append({
                    "Review ID": r['review_id'],
                    "Reviewer": f"{r['reviewer_name']} (@{r['reviewer_username']})",
                    "Reviewed Person": target_desc,
                    "Type": r['reviewed_person_type'].title(),
                    "Rating": rating_stars(r['rating']),
                    "Review": trunc_text,
                    "Date": format_datetime(r['updated_at'])
                })

            df_reviews = pd.DataFrame(table_records)
            st.dataframe(
                df_reviews.drop(columns=["Review ID"]),
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            # View Complete Review & Delete Inappropriate Review
            col_v1, col_v2 = st.columns([1.3, 1], gap="large")

            review_map = {
                f"#{r['review_id']} — {r['reviewer_name']} on {r['reviewed_person']} ({rating_stars(r['rating'])})": r
                for r in reviews
            }

            with col_v1:
                st.markdown("#### 🔍 View Complete Review")
                sel_rev_key = st.selectbox("Select Review to Inspect:", options=list(review_map.keys()))
                chosen_rev = review_map[sel_rev_key]

                reg_markup = f" • Reg: <code>{chosen_rev['reviewed_person_regno']}</code>" if chosen_rev.get('reviewed_person_regno') else ""
                t_badge = "badge-student" if chosen_rev['reviewed_person_type'] == 'student' else "badge-teacher"

                st.markdown(f"""
                <div class="ui-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                        <span style="font-size:1.15rem; font-weight:700;">{chosen_rev['reviewed_person']}</span>
                        <span class="badge {t_badge}">{chosen_rev['reviewed_person_type'].title()}</span>
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin-bottom:0.4rem;">
                        <strong>Department / Program:</strong> {chosen_rev['reviewed_person_department']}{reg_markup}
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin-bottom:0.4rem;">
                        <strong>Reviewer:</strong> {chosen_rev['reviewer_name']} (<code>@{chosen_rev['reviewer_username']}</code> • {chosen_rev['reviewer_email']})
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin-bottom:0.4rem;">
                        <strong>Rating:</strong> <span style="color:#f59e0b; font-weight:700;">{rating_stars_label(chosen_rev['rating'])}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.8rem;">
                        Submitted: {format_datetime(chosen_rev['created_at'])} | Updated: {format_datetime(chosen_rev['updated_at'])}
                    </div>
                    <div class="review-text-box">
                        {chosen_rev['review_text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_v2:
                st.markdown("#### 🗑️ Delete Review")
                st.warning("Admins can permanently remove inappropriate or policy-violating reviews.")
                confirm_del = st.checkbox("I confirm I want to permanently delete this review.", key="del_box")

                if st.button("Delete Inappropriate Review", type="primary", use_container_width=True):
                    if not confirm_del:
                        st.error("Please check the confirmation box above before deleting.")
                    else:
                        ok = database.delete_review(chosen_rev['review_id'])
                        if ok:
                            st.success(f"Review #{chosen_rev['review_id']} was deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete review. Please try again.")

    # --------------------------------------------------------------------------
    # 3. ADMIN MANAGE PEOPLE & PERSON DETAIL VIEW
    # --------------------------------------------------------------------------
    elif current_page == "Manage People":
        st.markdown("## Manage People")
        st.caption("Manage students and faculty, inspect detailed reviews dossier, and toggle active status.")

        tab_students, tab_teachers, tab_add_student, tab_add_teacher = st.tabs([
            "🎓 Student Directory & Analytics",
            "👨‍🏫 Faculty Directory",
            "➕ Add Student",
            "➕ Add Teacher"
        ])

        # TAB 1: STUDENTS
        with tab_students:
            st.markdown("##### Search Student Directory")
            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                st_search = st.text_input(
                    "Search student by Name or Registration Number",
                    placeholder="e.g. AMIT or 23BCON0028"
                )
            with col_s2:
                st_filter = st.selectbox("Status Filter", ["All", "Active Only", "Inactive Only"])

            students_data = database.get_students_summary(search_query=st_search)
            if st_filter == "Active Only":
                students_data = [s for s in students_data if s['active']]
            elif st_filter == "Inactive Only":
                students_data = [s for s in students_data if not s['active']]

            if not students_data:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">🎓</div>
                    <div class="empty-state-title">No Students Match Your Search</div>
                    <div class="empty-state-text">Check your search query or add a new student using the Add Student tab.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st_table = pd.DataFrame([{
                    "Name": s['student_name'],
                    "Registration No.": s['registration_no'] or "—",
                    "Department": s['department'],
                    "Reviews": s['total_reviews'],
                    "Average Rating": f"{s['average_rating']:.2f} ★" if s['average_rating'] else "No reviews",
                    "Status": "Active" if s['active'] else "Inactive"
                } for s in students_data])
                st.dataframe(st_table, hide_index=True, use_container_width=True)

                st.divider()

                # PERSON DETAIL VIEW: STUDENT
                st.markdown("### 📋 Student Dossier & Reviews Received")
                st_picker_map = {
                    f"{s['student_name']} — {s['registration_no'] or 'N/A'} ({s['total_reviews']} reviews)": s['student_id']
                    for s in students_data
                }
                chosen_st_label = st.selectbox("Select Student to Inspect:", options=list(st_picker_map.keys()), key="st_dossier_pick")
                chosen_st_id = st_picker_map[chosen_st_label]

                dossier = database.get_person_detail(chosen_st_id)
                if dossier:
                    # Header metrics
                    col_d1, col_d2, col_d3 = st.columns([1.5, 1, 1])
                    with col_d1:
                        st.markdown(f"**Name:** {dossier['name']}")
                        st.markdown(f"**Registration Number:** `{dossier['registration_no'] or 'N/A'}`")
                        st.markdown(f"**Department:** {dossier['department']}")
                        status_badge = "badge-active" if dossier['active'] else "badge-inactive"
                        st.markdown(f"**Status:** <span class='badge {status_badge}'>{'Active' if dossier['active'] else 'Inactive'}</span>", unsafe_allow_html=True)

                    with col_d2:
                        st.metric("Average Rating", f"{dossier['average_rating']:.2f} ★" if dossier['average_rating'] else "No reviews")
                        st.metric("Total Reviews", dossier['total_reviews'])

                    with col_d3:
                        st.markdown("**Rating Breakdown:**")
                        for star_num in [5, 4, 3, 2, 1]:
                            count = dossier['breakdown'].get(star_num, 0)
                            st.write(f"{star_num} ★ : **{count}**")

                    # Status toggle & edit
                    col_btn, col_edit = st.columns([1, 1])
                    with col_btn:
                        btn_txt = "Deactivate Student" if dossier['active'] else "Activate Student"
                        if st.button(btn_txt, key="btn_toggle_st", use_container_width=True):
                            database.set_person_active(dossier['id'], not dossier['active'])
                            st.success(f"{dossier['name']} status updated.")
                            st.rerun()

                    with col_edit:
                        with st.expander("✏️ Edit Student Details"):
                            with st.form("edit_st_form"):
                                new_name = st.text_input("Name", value=dossier['name'])
                                new_reg = st.text_input("Registration No", value=dossier['registration_no'] or "")
                                new_dept = st.text_input("Department", value=dossier['department'])
                                save_st = st.form_submit_button("Save Changes", use_container_width=True)

                            if save_st:
                                try:
                                    database.update_person(
                                        person_id=dossier['id'],
                                        name=new_name,
                                        department=new_dept,
                                        person_type="student",
                                        registration_no=new_reg.strip() if new_reg else None
                                    )
                                    st.success("Student details updated.")
                                    st.rerun()
                                except ValueError as err:
                                    st.error(str(err))

                    # Reviews Received List
                    st.markdown("##### Reviews Received")
                    if dossier['reviews']:
                        for rev in dossier['reviews']:
                            st.markdown(f"""
                            <div class="review-item">
                                <div class="review-item-header">
                                    <span class="review-reviewer">{rev['reviewer_name']} (@{rev['reviewer_username']})</span>
                                    <span class="review-stars">{rating_stars(rev['rating'])}</span>
                                </div>
                                <div class="review-text-box">{rev['review_text']}</div>
                                <div class="review-date" style="margin-top:0.4rem;">{format_datetime(rev['updated_at'])}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No reviews have been submitted for this student yet.")

        # TAB 2: TEACHERS
        with tab_teachers:
            st.markdown("##### Search Faculty Directory")
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                t_search = st.text_input("Search faculty by Name or Department", placeholder="e.g. Computer Science")
            with col_t2:
                t_filter = st.selectbox("Status Filter", ["All", "Active Only", "Inactive Only"], key="t_stat_filter")

            teachers_data = database.get_teachers_summary(search_query=t_search)
            if t_filter == "Active Only":
                teachers_data = [t for t in teachers_data if t['active']]
            elif t_filter == "Inactive Only":
                teachers_data = [t for t in teachers_data if not t['active']]

            if not teachers_data:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">👨‍🏫</div>
                    <div class="empty-state-title">No Teacher Reviews Found</div>
                    <div class="empty-state-text">No faculty members match your criteria. Add teachers using the Add Teacher tab.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                t_table = pd.DataFrame([{
                    "Name": t['teacher_name'],
                    "Department": t['department'],
                    "Reviews": t['total_reviews'],
                    "Average Rating": f"{t['average_rating']:.2f} ★" if t['average_rating'] else "No reviews",
                    "Status": "Active" if t['active'] else "Inactive"
                } for t in teachers_data])
                st.dataframe(t_table, hide_index=True, use_container_width=True)

                st.divider()

                # PERSON DETAIL VIEW: TEACHER
                st.markdown("### 📋 Faculty Dossier & Reviews Received")
                t_picker_map = {
                    f"{t['teacher_name']} — {t['department']} ({t['total_reviews']} reviews)": t['teacher_id']
                    for t in teachers_data
                }
                chosen_t_label = st.selectbox("Select Faculty Member to Inspect:", options=list(t_picker_map.keys()), key="t_dossier_pick")
                chosen_t_id = t_picker_map[chosen_t_label]

                t_dossier = database.get_person_detail(chosen_t_id)
                if t_dossier:
                    col_td1, col_td2, col_td3 = st.columns([1.5, 1, 1])
                    with col_td1:
                        st.markdown(f"**Name:** {t_dossier['name']}")
                        st.markdown(f"**Department:** {t_dossier['department']}")
                        t_status_badge = "badge-active" if t_dossier['active'] else "badge-inactive"
                        st.markdown(f"**Status:** <span class='badge {t_status_badge}'>{'Active' if t_dossier['active'] else 'Inactive'}</span>", unsafe_allow_html=True)

                    with col_td2:
                        st.metric("Average Rating", f"{t_dossier['average_rating']:.2f} ★" if t_dossier['average_rating'] else "No reviews")
                        st.metric("Total Reviews", t_dossier['total_reviews'])

                    with col_td3:
                        st.markdown("**Rating Breakdown:**")
                        for star_num in [5, 4, 3, 2, 1]:
                            count = t_dossier['breakdown'].get(star_num, 0)
                            st.write(f"{star_num} ★ : **{count}**")

                    col_t_btn, col_t_edit = st.columns([1, 1])
                    with col_t_btn:
                        btn_txt = "Deactivate Teacher" if t_dossier['active'] else "Activate Teacher"
                        if st.button(btn_txt, key="btn_toggle_teacher", use_container_width=True):
                            database.set_person_active(t_dossier['id'], not t_dossier['active'])
                            st.success(f"{t_dossier['name']} status updated.")
                            st.rerun()

                    with col_t_edit:
                        with st.expander("✏️ Edit Teacher Details"):
                            with st.form("edit_t_form"):
                                new_t_name = st.text_input("Name", value=t_dossier['name'])
                                new_t_dept = st.text_input("Department", value=t_dossier['department'])
                                save_t = st.form_submit_button("Save Changes", use_container_width=True)

                            if save_t:
                                try:
                                    database.update_person(
                                        person_id=t_dossier['id'],
                                        name=new_t_name,
                                        department=new_t_dept,
                                        person_type="teacher"
                                    )
                                    st.success("Faculty details updated.")
                                    st.rerun()
                                except ValueError as err:
                                    st.error(str(err))

                    st.markdown("##### Reviews Received")
                    if t_dossier['reviews']:
                        for rev in t_dossier['reviews']:
                            st.markdown(f"""
                            <div class="review-item">
                                <div class="review-item-header">
                                    <span class="review-reviewer">{rev['reviewer_name']} (@{rev['reviewer_username']})</span>
                                    <span class="review-stars">{rating_stars(rev['rating'])}</span>
                                </div>
                                <div class="review-text-box">{rev['review_text']}</div>
                                <div class="review-date" style="margin-top:0.4rem;">{format_datetime(rev['updated_at'])}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No reviews have been submitted for this teacher yet.")

        # TAB 3: ADD STUDENT
        with tab_add_student:
            st.markdown("##### Add Student to Directory")
            with st.form("add_student_form", clear_on_submit=True):
                new_s_name = st.text_input("Student Name", placeholder="e.g. PRIYANKA SANGWA")
                new_s_reg = st.text_input("Registration Number", placeholder="e.g. 23BCON1710")
                new_s_dept = st.text_input("Department / Program", value="Computer Science & Engineering")
                submit_add_s = st.form_submit_button("Add Student", type="primary", use_container_width=True)

            if submit_add_s:
                try:
                    database.add_person(
                        name=new_s_name,
                        person_type='student',
                        department=new_s_dept,
                        registration_no=new_s_reg.strip() if new_s_reg else None
                    )
                    st.success(f"Student '{new_s_name}' ({new_s_reg}) added successfully!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

        # TAB 4: ADD TEACHER
        with tab_add_teacher:
            st.markdown("##### Add Faculty / Teacher")
            with st.form("add_teacher_form", clear_on_submit=True):
                new_t_name = st.text_input("Teacher Name", placeholder="e.g. Dr. Robert Miller")
                new_t_dept = st.text_input("Department", placeholder="e.g. Computer Science")
                submit_add_t = st.form_submit_button("Add Teacher", type="primary", use_container_width=True)

            if submit_add_t:
                try:
                    database.add_person(
                        name=new_t_name,
                        person_type='teacher',
                        department=new_t_dept
                    )
                    st.success(f"Teacher '{new_t_name}' added successfully!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

    # --------------------------------------------------------------------------
    # 4. ADMIN USERS DIRECTORY
    # --------------------------------------------------------------------------
    elif current_page == "Users":
        st.markdown("## Registered Accounts")
        st.caption("Inspect verified user accounts and linked registration credentials.")

        all_users = database.list_users()
        user_search = st.text_input("Search user accounts by name, username, email, or registration number...")
        if user_search.strip():
            kw = user_search.strip().lower()
            all_users = [
                u for u in all_users
                if kw in u['name'].lower() or kw in u['username'].lower() or kw in u['email'].lower() or (u.get('registration_no') and kw in u['registration_no'].lower())
            ]

        if not all_users:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">👤</div>
                <div class="empty-state-title">No User Accounts Found</div>
                <div class="empty-state-text">No user accounts match your search query.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            user_rows = []
            for u in all_users:
                user_rows.append({
                    "Name": u['name'],
                    "Username / Email": f"@{u['username']} • {u['email']}",
                    "Registration Number": u.get('registration_no') or "—",
                    "Role": u['role'].title(),
                    "Created Date": format_datetime(u['created_at']),
                    "Status": "Active"
                })

            st.dataframe(pd.DataFrame(user_rows), hide_index=True, use_container_width=True)

    # --------------------------------------------------------------------------
    # 5. ADMIN EXPORT DATA
    # --------------------------------------------------------------------------
    elif current_page == "Export":
        st.markdown("## Export Data to CSV")
        st.caption("Generate and download structured CSV reports for compliance, archiving, and analysis.")

        col_e1, col_e2 = st.columns(2, gap="large")

        # EXPORT REVIEWS
        with col_e1:
            st.markdown("""
            <div class="ui-card">
                <div class="ui-card-header">Export Reviews</div>
                <div class="ui-card-sub">Download complete submissions including evaluator details, ratings, and written comments.</div>
            """, unsafe_allow_html=True)

            export_choice = st.radio(
                "Select Export Dataset:",
                ["All Reviews", "Student Reviews", "Teacher Reviews"],
                key="exp_rev_choice"
            )

            filter_type = None
            if export_choice == "Student Reviews":
                filter_type = "student"
            elif export_choice == "Teacher Reviews":
                filter_type = "teacher"

            reviews_to_export = database.fetch_admin_reviews(person_type=filter_type)
            st.write(f"Total matching records: **{len(reviews_to_export)}**")

            if reviews_to_export:
                df_exp_rev = pd.DataFrame([{
                    "Review ID": r['review_id'],
                    "Reviewer Name": r['reviewer_name'],
                    "Reviewer Username": r['reviewer_username'],
                    "Reviewer Email": r['reviewer_email'],
                    "Reviewed Person": r['reviewed_person'],
                    "Registration Number": r['reviewed_person_regno'] or "—",
                    "Reviewed Person Type": r['reviewed_person_type'].title(),
                    "Department": r['reviewed_person_department'],
                    "Rating": r['rating'],
                    "Review Comment": r['review_text'],
                    "Date Submitted": format_datetime(r['created_at']),
                    "Date Updated": format_datetime(r['updated_at'])
                } for r in reviews_to_export])

                csv_rev = df_exp_rev.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"⬇️ Download {export_choice} CSV",
                    data=csv_rev,
                    file_name=f"{export_choice.lower().replace(' ', '_')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("No reviews available to export.")

            st.markdown("</div>", unsafe_allow_html=True)

        # EXPORT PEOPLE DIRECTORY
        with col_e2:
            st.markdown("""
            <div class="ui-card">
                <div class="ui-card-header">Export Master Directory</div>
                <div class="ui-card-sub">Download master student directory with registration numbers and faculty listings.</div>
            """, unsafe_allow_html=True)

            people_to_export = database.list_people(active_only=False)
            st.write(f"Total directory records: **{len(people_to_export)}**")

            if people_to_export:
                df_exp_people = pd.DataFrame([{
                    "Person ID": p['id'],
                    "Name": p['name'],
                    "Registration Number": p.get('registration_no') or "—",
                    "Type": p['type'].title(),
                    "Department": p['department'],
                    "Status": "Active" if p['active'] else "Inactive"
                } for p in people_to_export])

                csv_people = df_exp_people.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download People Directory CSV",
                    data=csv_people,
                    file_name="master_people_directory.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("No people records available.")

            st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# MAIN ROUTING CONTROLLER
# ==============================================================================
def main():
    if st.session_state.user is None:
        render_landing_page()
    else:
        role = st.session_state.user.get('role', 'user')
        if role == 'admin':
            render_admin_dashboard(st.session_state.user)
        else:
            render_user_dashboard(st.session_state.user)


if __name__ == "__main__":
    main()
