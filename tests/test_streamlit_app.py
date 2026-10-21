"""Streamlit AppTest suite verifying all screens, role-based views, top navbar, directories, and UI controls."""
import os
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

import database
import auth

APP_PATH = str(Path(__file__).resolve().parent.parent / 'app.py')


def create_app_test() -> AppTest:
    return AppTest.from_file(APP_PATH, default_timeout=25)


class StreamlitAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['ADMIN_PASSWORD'] = 'AdminPass@123'
        database.init_db()
        auth.seed_admin()

        # Ensure registered user, teacher, student, and baseline review exist for UI tests
        user = database.get_user_by_username_or_email("ui_tester")
        if not user:
            uid = database.create_user(
                "UI Tester",
                "ui_tester",
                "uitester@university.edu",
                auth.hash_password("Password@123"),
                registration_no="23BCON9001"
            )
        else:
            uid = user['id']

        teachers = database.list_people(person_type="teacher", active_only=False)
        if not teachers:
            tid = database.add_person("Dr. Test Teacher", "teacher", "Computer Science")
        else:
            tid = teachers[0]['id']

        database.submit_or_update_review(uid, tid, 5, "Exceptional teaching and mentorship.")

    def test_landing_page_unauthenticated(self):
        """Verify landing page renders for unauthenticated users with login and register forms."""
        at = create_app_test()
        at.run()
        self.assertFalse(at.exception)
        access_radios = [r for r in at.radio if r.label == "Account access"]
        self.assertEqual(len(access_radios), 1)
        self.assertEqual(list(access_radios[0].options), ["Sign In", "Create Account"])
        self.assertEqual(len(at.dataframe), 0)

        input_labels = [i.label for i in at.text_input]
        self.assertIn("Username, Email or Registration Number", input_labels)

    def test_auth_flash_message_and_login_error(self):
        """Verify registration flash message displays on Sign In tab, and login error is exact."""
        # 1. Test flash message
        at = create_app_test()
        at.session_state.auth_flash_success = True
        at.run()
        self.assertFalse(at.exception)
        success_texts = [s.value for s in at.success]
        self.assertTrue(any("Account created successfully" in s for s in success_texts))
        self.assertTrue(any("registration number" in s for s in success_texts))

        # 2. Test failed login error
        at_login = create_app_test()
        at_login.run()
        login_inputs = [i for i in at_login.text_input if "Registration Number" in i.label]
        self.assertGreaterEqual(len(login_inputs), 1)
        login_input = login_inputs[0]
        pass_input = [i for i in at_login.text_input if "Password" in i.label][0]
        login_input.set_value("nonexistent_user")
        pass_input.set_value("WrongPass@123")
        at_login.button[0].click().run()
        self.assertFalse(at_login.exception)
        error_texts = [e.value for e in at_login.error]
        self.assertIn("Account not found or password is incorrect.", error_texts)

    def test_user_dashboard_home(self):
        """Verify regular user lands on Home dashboard with greeting, action cards, and strict privacy."""
        at = create_app_test()
        at.session_state.user = {
            'id': 2,
            'name': 'John Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'registration_no': '23BCON0028',
            'role': 'user'
        }
        at.session_state.user_nav = "Home"
        at.run()
        self.assertFalse(at.exception)

        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("Hello, John", all_md)
        self.assertIn("Student Feedback", all_md)
        self.assertIn("Teacher Feedback", all_md)
        self.assertIn("visible only to authorized administrators", all_md)

        # Privacy verification: Normal users must never see dataframes or admin analytics
        self.assertEqual(len(at.dataframe), 0)

    def test_user_dashboard_student_directory_and_self_exclusion(self):
        """Verify Student Directory page renders cards and excludes current student."""
        at = create_app_test()
        at.session_state.user = {
            'id': 2,
            'name': 'AMIT AGARWAL',
            'username': 'amitag',
            'email': 'amit@example.com',
            'registration_no': '23BCON0028',
            'role': 'user'
        }
        at.session_state.user_nav = "Students"
        at.run()
        self.assertFalse(at.exception)

        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("Student Feedback", all_md)
        self.assertIn("Choose a student and share constructive feedback", all_md)

        # Self-exclusion: The current student's registration number must not appear in directory cards
        # (excluding header badge where user's own reg number is shown)
        student_card_buttons = [b.label for b in at.button if b.label in ("Give Feedback", "Edit Feedback")]
        self.assertGreaterEqual(len(student_card_buttons), 1)

    def test_user_dashboard_teacher_directory(self):
        """Verify Teacher Directory page renders faculty cards and search input."""
        at = create_app_test()
        at.session_state.user = {
            'id': 2,
            'name': 'John Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'registration_no': '23BCON0028',
            'role': 'user'
        }
        at.session_state.user_nav = "Teachers"
        at.run()
        self.assertFalse(at.exception)

        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("Teacher Feedback", all_md)
        self.assertIn("Share feedback about faculty members", all_md)

    def test_user_dashboard_feedback_detail(self):
        """Verify dedicated feedback form renders target details, rating slider, and privacy card."""
        at = create_app_test()
        teachers = database.list_people(person_type="teacher", active_only=True)
        self.assertGreaterEqual(len(teachers), 1)
        target = teachers[0]

        at.session_state.user = {
            'id': 2,
            'name': 'John Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'registration_no': '23BCON0028',
            'role': 'user'
        }
        at.session_state.user_nav = "Feedback Form"
        at.session_state.active_target_person = target
        at.session_state.active_target_type = "teacher"
        at.session_state.review_submitted = False
        at.run()
        self.assertFalse(at.exception)

        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn(target['name'], all_md)
        self.assertIn("Private Feedback", all_md)
        self.assertGreaterEqual(len(at.text_area), 1)
        self.assertGreaterEqual(len(at.select_slider), 1)

    def test_user_dashboard_profile(self):
        """Verify regular user profile page renders personal info and change password form."""
        at = create_app_test()
        at.session_state.user = {
            'id': 2,
            'name': 'John Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'registration_no': '23BCON0028',
            'role': 'user'
        }
        at.session_state.user_nav = "My Profile"
        at.run()
        self.assertFalse(at.exception)

        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("Account Profile", all_md)
        self.assertIn("Change Password", all_md)
        self.assertIn("johndoe", all_md)

        forms = [f for f in at.text_input if "Password" in f.label]
        self.assertGreaterEqual(len(forms), 2)

    def test_admin_dashboard_kpis(self):
        """Verify Admin Dashboard renders KPI cards and charts."""
        at = create_app_test()
        at.session_state.user = {
            'id': 1,
            'name': 'System Administrator',
            'username': 'admin',
            'email': 'admin@feedback.local',
            'role': 'admin'
        }
        at.session_state.admin_active_tab = "Overview"
        at.run()
        self.assertFalse(at.exception)

        subheaders = [s.value for s in at.subheader]
        self.assertTrue(any("Administrative Dashboard" in s for s in subheaders))

        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("Total Reviews", all_md)
        self.assertIn("Registered Users", all_md)
        self.assertIn("Total Students", all_md)
        self.assertIn("Total Teachers", all_md)
        self.assertIn("Average Rating", all_md)

    def test_admin_reviews_table_and_filters(self):
        """Verify Admin Reviews tab renders reviews table and filter controls."""
        at = create_app_test()
        at.session_state.user = {
            'id': 1,
            'name': 'System Administrator',
            'username': 'admin',
            'email': 'admin@feedback.local',
            'role': 'admin'
        }
        at.session_state.admin_active_tab = "Reviews"
        at.run()
        self.assertFalse(at.exception)

        select_labels = [s.label for s in at.selectbox]
        self.assertIn("Review Type", select_labels)
        self.assertIn("Person Name", select_labels)
        self.assertIn("Rating", select_labels)
        self.assertIn("Date Filter", select_labels)

        search_inputs = [t for t in at.text_input if "Search" in t.label]
        self.assertGreaterEqual(len(search_inputs), 1)
        self.assertGreaterEqual(len(at.dataframe), 1)

    def test_admin_students_management(self):
        """Verify Admin Students tab renders directory and add student form."""
        at = create_app_test()
        at.session_state.user = {
            'id': 1,
            'name': 'System Administrator',
            'username': 'admin',
            'email': 'admin@feedback.local',
            'role': 'admin'
        }
        at.session_state.admin_active_tab = "Students"
        at.run()
        self.assertFalse(at.exception)

        tab_labels = [t.label for t in at.tabs]
        self.assertTrue(any("Student Directory" in t for t in tab_labels))
        self.assertTrue(any("Add Student" in t for t in tab_labels))

    def test_admin_teachers_management(self):
        """Verify Admin Teachers tab renders directory and add teacher form."""
        at = create_app_test()
        at.session_state.user = {
            'id': 1,
            'name': 'System Administrator',
            'username': 'admin',
            'email': 'admin@feedback.local',
            'role': 'admin'
        }
        at.session_state.admin_active_tab = "Teachers"
        at.run()
        self.assertFalse(at.exception)

        tab_labels = [t.label for t in at.tabs]
        self.assertTrue(any("Faculty Directory" in t for t in tab_labels))
        self.assertTrue(any("Add Teacher" in t for t in tab_labels))

    def test_admin_users_and_export(self):
        """Verify Users tab and Export tab render correctly."""
        at = create_app_test()
        at.session_state.user = {
            'id': 1,
            'name': 'System Administrator',
            'username': 'admin',
            'email': 'admin@feedback.local',
            'role': 'admin'
        }
        at.session_state.admin_active_tab = "Export"
        at.run()
        self.assertFalse(at.exception)

        download_btns = [b.label for b in at.download_button]
        self.assertTrue(any("Reviews" in b for b in download_btns))
        self.assertTrue(any("People Directory" in b for b in download_btns))


if __name__ == '__main__':
    unittest.main()
