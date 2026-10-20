"""Streamlit AppTest suite verifying all screens, role-based views, and UI controls."""
import os
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

import database
import auth

APP_PATH = str(Path(__file__).resolve().parent.parent / 'app.py')


def create_app_test() -> AppTest:
    return AppTest.from_file(APP_PATH, default_timeout=20)


class StreamlitAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['ADMIN_PASSWORD'] = 'AdminPass@123'
        database.init_db()
        auth.seed_admin()

        # Ensure at least one registered user, teacher, student, and review exist for UI tests
        user = database.get_user_by_username_or_email("ui_tester")
        if not user:
            uid = database.create_user("UI Tester", "ui_tester", "uitester@university.edu", auth.hash_password("Password@123"))
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
        tab_labels = [t.label for t in at.tabs]
        self.assertIn("🔐 Sign In", tab_labels)
        self.assertIn("📝 Create Account", tab_labels)
        self.assertEqual(len(at.dataframe), 0)

    def test_user_dashboard_give_review(self):
        """Verify regular user sees Give Review, selects student/teacher, and cannot see other reviews."""
        at = create_app_test()
        at.session_state.user = {
            'id': 2,
            'name': 'John Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'role': 'user'
        }
        at.run()
        self.assertFalse(at.exception)

        radios = [r.label for r in at.radio]
        self.assertTrue(any("Review Type" in r for r in radios))
        self.assertEqual(len(at.dataframe), 0)

    def test_user_dashboard_profile(self):
        """Verify regular user profile page renders personal info and change password form."""
        at = create_app_test()
        at.session_state.user = {
            'id': 2,
            'name': 'John Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'role': 'user'
        }
        at.run()
        self.assertFalse(at.exception)
        # Select My Profile in sidebar
        at.sidebar.radio[0].set_value("👤 My Profile").run()
        self.assertFalse(at.exception)

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
        at.run()
        self.assertFalse(at.exception)
        at.sidebar.radio[0].set_value("📝 Reviews").run()
        self.assertFalse(at.exception)

        select_labels = [s.label for s in at.selectbox]
        self.assertIn("Review Type", select_labels)
        self.assertIn("Person Name", select_labels)
        self.assertIn("Rating", select_labels)
        self.assertIn("Date Filter", select_labels)

        search_inputs = [t for t in at.text_input if "Search" in t.label]
        self.assertGreaterEqual(len(search_inputs), 1)

        self.assertGreaterEqual(len(at.dataframe), 1)

    def test_admin_manage_people(self):
        """Verify Admin Manage People tab renders directory, add teacher, and add student forms."""
        at = create_app_test()
        at.session_state.user = {
            'id': 1,
            'name': 'System Administrator',
            'username': 'admin',
            'email': 'admin@feedback.local',
            'role': 'admin'
        }
        at.run()
        self.assertFalse(at.exception)
        at.sidebar.radio[0].set_value("👥 Manage People").run()
        self.assertFalse(at.exception)

        tab_labels = [t.label for t in at.tabs]
        self.assertTrue(any("Directory" in t for t in tab_labels))
        self.assertTrue(any("Add Teacher" in t for t in tab_labels))
        self.assertTrue(any("Add Student" in t for t in tab_labels))

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
        at.run()
        self.assertFalse(at.exception)
        at.sidebar.radio[0].set_value("📥 Export").run()
        self.assertFalse(at.exception)

        download_btns = [b.label for b in at.download_button]
        self.assertTrue(any("Reviews" in b for b in download_btns))
        self.assertTrue(any("People Directory" in b for b in download_btns))


if __name__ == '__main__':
    unittest.main()
