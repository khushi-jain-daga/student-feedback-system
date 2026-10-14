"""Streamlit UI: student portal and administrator dashboard."""
import sqlite3
import pandas as pd
import streamlit as st
from database import (init_db, list_faculty, add_faculty, set_faculty_active,
                      submit_feedback, fetch_feedback, dashboard_stats)
from auth import register_student, authenticate, seed_admin

st.set_page_config(page_title='Student Feedback Portal', page_icon='🎓', layout='wide')
init_db()
seed_admin()
st.markdown('''<style>
.block-container {padding-top:2rem;max-width:1150px}
h1,h2,h3 {letter-spacing:-.02em}
div[data-testid="stMetric"] {background:#f0f5fa;border-radius:12px;padding:16px}
</style>''', unsafe_allow_html=True)
st.title('🎓 Student Feedback Management System')
st.caption('Secure student portal • Faculty evaluation • Administration dashboard')

if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    left, right = st.columns([2,1])
    with left:
        login_tab, signup_tab = st.tabs(['🔐 Login', '📝 Student Registration'])
        with login_tab:
            with st.form('login'):
                username = st.text_input('Username')
                password = st.text_input('Password', type='password')
                clicked = st.form_submit_button('Sign in', use_container_width=True)
            if clicked:
                user = authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error('Invalid credentials.')
        with signup_tab:
            with st.form('registration'):
                full_name = st.text_input('Full name')
                new_user = st.text_input('Choose username')
                email = st.text_input('Email')
                new_password = st.text_input('Password (at least 8 characters)', type='password')
                confirm = st.text_input('Confirm password', type='password')
                create = st.form_submit_button('Create account', use_container_width=True)
            if create:
                if new_password != confirm:
                    st.error('Passwords do not match.')
                else:
                    try:
                        register_student(new_user, full_name, email, new_password)
                        st.success('Account created! Sign in from the Login tab.')
                    except ValueError as exc:
                        st.error(str(exc))
    with right:
        st.info('**How it works**\n\n1. Students create an account.\n\n2. Submit feedback for faculty.\n\n3. Admin reviews ratings and feedback.')
else:
    user = st.session_state.user
    with st.sidebar:
        st.header('My account')
        st.write(f"**{user['full_name']}**")
        st.caption(f"@{user['username']} • {user['role'].title()}")
        if st.button('🚪 Log out', use_container_width=True):
            st.session_state.user = None
            st.rerun()
    if user['role'] == 'student':
        tab1, tab2 = st.tabs(['✍️ Submit Feedback','📜 My History'])
        with tab1:
            faculty = list_faculty()
            if not faculty:
                st.warning('No faculty available yet.')
            else:
                options = {f"{f['name']} — {f['department']}":f['id'] for f in faculty}
                with st.form('submit_feedback', clear_on_submit=True):
                    chosen = st.selectbox('Select faculty', list(options))
                    course = st.text_input('Course / Subject', placeholder='e.g. Database Management Systems')
                    rating = st.slider('Rating', min_value=1, max_value=5, value=4)
                    comments = st.text_area('Your feedback', max_chars=1500)
                    submit = st.form_submit_button('Submit feedback', use_container_width=True)
                if submit:
                    if not course.strip() or not comments.strip():
                        st.error('Course and comments are required.')
                    else:
                        try:
                            submit_feedback(user['id'], options[chosen], course.strip(), rating, comments.strip())
                            st.success('Feedback saved in the database!')
                        except (ValueError, sqlite3.IntegrityError) as exc:
                            st.error(str(exc))
        with tab2:
            rows = fetch_feedback(student_id=user['id'])
            if rows:
                st.dataframe(pd.DataFrame(rows).drop(columns=['student','student_name']), hide_index=True, use_container_width=True)
            else:
                st.info('You have not submitted any feedback yet.')
    elif user['role'] == 'admin':
        tab1, tab2, tab3 = st.tabs(['📊 Overview','💬 All Feedback','👩‍🏫 Faculty Management'])
        with tab1:
            stats = dashboard_stats()
            c1,c2,c3 = st.columns(3)
            c1.metric('Registered Students', stats['students'])
            c2.metric('Feedback Entries', stats['feedback_count'])
            c3.metric('Average Rating', f"{stats['average_rating']:.2f} / 5")
            st.subheader('Faculty rating summary')
            st.dataframe(pd.DataFrame(stats['faculty_stats']), hide_index=True, use_container_width=True)
            chart_data = [x for x in stats['faculty_stats'] if x['responses']]
            if chart_data:
                st.bar_chart(pd.DataFrame(chart_data).set_index('faculty')['avg_rating'])
        with tab2:
            all_rows = fetch_feedback()
            faculty_options = {'All faculty':None}
            faculty_options.update({f['name']:f['id'] for f in list_faculty(False)})
            selected = st.selectbox('Filter by faculty', list(faculty_options))
            rows = fetch_feedback(faculty_id=faculty_options[selected]) if faculty_options[selected] else all_rows
            if rows:
                frame = pd.DataFrame(rows)
                st.dataframe(frame, hide_index=True, use_container_width=True)
                st.download_button('⬇️ Export CSV', frame.to_csv(index=False).encode('utf-8'), 'student_feedback.csv', 'text/csv')
            else:
                st.info('No feedback matches this filter.')
        with tab3:
            st.subheader('Add faculty')
            with st.form('add_faculty'):
                faculty_name = st.text_input('Faculty name')
                department = st.text_input('Department')
                save = st.form_submit_button('Add faculty')
            if save:
                if not faculty_name.strip() or not department.strip():
                    st.error('Both fields are required.')
                else:
                    try:
                        add_faculty(faculty_name.strip(), department.strip())
                        st.success('Faculty added.')
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error('Faculty already exists.')
            st.subheader('Faculty directory')
            for f in list_faculty(False):
                c1,c2 = st.columns([5,1])
                c1.write(f"**{f['name']}** — {f['department']} ({'Active' if f['active'] else 'Inactive'})")
                if c2.button('Disable' if f['active'] else 'Enable', key=f"faculty_{f['id']}"):
                    set_faculty_active(f['id'], not f['active'])
                    st.rerun()
